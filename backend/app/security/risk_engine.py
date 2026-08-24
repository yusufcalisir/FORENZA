"""
FORENZA Intelligent Traffic Risk Engine (Dimension 1 & 4 & 18).

Provides passive, privacy-preserving risk assessment for all incoming traffic:
- Multi-signal anomaly evaluation (frequency, headers, error rates, bot signatures).
- Zero friction for legitimate users (R < 30 -> 0ms delay, no CAPTCHA).
- Dual-key isolation: Hash(IP + User-Agent + Session) prevents NAT/University false positives.
- Graduated risk tiers: NORMAL -> MONITORED -> THROTTLED -> CHALLENGED -> BLOCKED.
"""

import hashlib
import re
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Deque, Dict, List, Optional, Tuple


class RiskTier(str, Enum):
    NORMAL = "NORMAL"          # R < 30: Zero friction, instant pass-through
    MONITORED = "MONITORED"    # 30 <= R < 60: Passive telemetry enhancement
    THROTTLED = "THROTTLED"    # 60 <= R < 80: Adaptive micro-delay (100-250ms)
    CHALLENGED = "CHALLENGED"  # 80 <= R < 95: Silent background PoW required
    BLOCKED = "BLOCKED"        # R >= 95: Temporary cooling block (429)


@dataclass
class TrafficRiskAssessment:
    risk_score: int
    risk_tier: RiskTier
    client_key: str
    ip_hash: str
    reasons: List[str]
    delay_ms: int = 0
    requires_pow: bool = False
    is_blocked: bool = False


@dataclass
class ClientTrafficState:
    timestamps: Deque[float] = field(default_factory=deque)
    error_timestamps: Deque[float] = field(default_factory=deque)
    failed_auth_timestamps: Deque[float] = field(default_factory=deque)
    last_seen: float = field(default_factory=time.time)
    reputation_penalty: float = 0.0


class TrafficRiskEngine:
    """
    High-performance, in-memory adaptive risk evaluation engine.
    Derives verbatim from Section 1, 4 and 18 specifications.
    """

    KNOWN_SCANNER_PATTERNS = [
        re.compile(r"(sqlmap|nikto|gobuster|masscan|dirbuster|acunetix|wpscan|hydra|zgrab)", re.IGNORECASE),
        re.compile(r"(nmap|openvas|havij|netsparker|nuclei|jaeles|burpcollaborator)", re.IGNORECASE),
    ]

    SUSPICIOUS_PATH_PATTERNS = [
        re.compile(r"(\.env|\.git|wp-admin|phpmyadmin|\.aws|etc/passwd|win\.ini|eval\(|base64_decode)", re.IGNORECASE),
        re.compile(r"(\.\./\.\./|/etc/shadow|/proc/self/environ|<script>|union\s+select)", re.IGNORECASE),
    ]

    def __init__(
        self,
        window_seconds: float = 60.0,
        burst_threshold: int = 40,
        max_clients: int = 50000,
    ):
        self.window_seconds = window_seconds
        self.burst_threshold = burst_threshold
        self.max_clients = max_clients
        self._states: Dict[str, ClientTrafficState] = {}
        self._last_cleanup = time.time()

    def generate_identity_key(
        self,
        ip: str,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Tuple[str, str]:
        """
        Creates privacy-conscious dual-key:
        - client_key: Hash(IP + UA + Session) ensures shared NAT/Wifi IPs are treated individually.
        - ip_hash: Anonymized IP identifier for audit logs (zero plaintext PII storage).
        """
        clean_ip = ip.strip() if ip else "127.0.0.1"
        clean_ua = (user_agent or "unknown").strip()
        clean_sess = (session_id or "").strip()

        ip_hash = hashlib.sha256(clean_ip.encode("utf-8")).hexdigest()[:16]
        composite = f"{clean_ip}|{clean_ua[:80]}|{clean_sess}"
        client_key = hashlib.sha256(composite.encode("utf-8")).hexdigest()[:24]

        return client_key, ip_hash

    def evaluate_request(
        self,
        ip: str,
        path: str,
        method: str,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        now: Optional[float] = None,
    ) -> TrafficRiskAssessment:
        """
        Evaluates real-time risk score for an incoming HTTP request.
        Zero friction for standard user flows (Score < 30).
        """
        ts = now if now is not None else time.time()
        client_key, ip_hash = self.generate_identity_key(ip, user_agent, session_id)

        self._maybe_cleanup(ts)

        state = self._states.get(client_key)
        if state is None:
            state = ClientTrafficState()
            self._states[client_key] = state

        # Slide time window
        state.last_seen = ts
        self._prune_deque(state.timestamps, ts, self.window_seconds)
        self._prune_deque(state.error_timestamps, ts, self.window_seconds)
        self._prune_deque(state.failed_auth_timestamps, ts, self.window_seconds)

        state.timestamps.append(ts)

        score = 0
        reasons: List[str] = []

        # 1. Header & User-Agent Anomaly Checks
        ua = (user_agent or "").strip()
        if not ua:
            score += 25
            reasons.append("Empty User-Agent")
        else:
            for pattern in self.KNOWN_SCANNER_PATTERNS:
                if pattern.search(ua):
                    score += 85
                    reasons.append(f"Malicious scanner signature: {pattern.pattern}")
                    break

        # 2. Suspicious Probe Path Pattern Detection
        for pattern in self.SUSPICIOUS_PATH_PATTERNS:
            if pattern.search(path):
                score += 70
                reasons.append("Vulnerability exploit probe pattern in URI")
                break

        # 3. Traffic Burst / Velocity Evaluation
        recent_count = len(state.timestamps)
        if recent_count > self.burst_threshold * 2:
            score += 45
            reasons.append(f"Extreme request velocity ({recent_count} req/{self.window_seconds}s)")
        elif recent_count > self.burst_threshold:
            score += 20
            reasons.append(f"Elevated request velocity ({recent_count} req/{self.window_seconds}s)")

        # Burst velocity in last 2 seconds
        two_sec_count = sum(1 for t in state.timestamps if ts - t <= 2.0)
        if two_sec_count > 15:
            score += 30
            reasons.append(f"Micro-burst spike ({two_sec_count} req in 2s)")

        # 4. Error Burst History
        error_count = len(state.error_timestamps)
        if error_count > 10:
            score += 25
            reasons.append(f"High 4xx/5xx failure frequency ({error_count} errors)")

        # 5. Failed Authentication Penalty
        failed_auths = len(state.failed_auth_timestamps)
        if failed_auths >= 5:
            score += 50
            reasons.append(f"Consecutive authentication failures ({failed_auths})")
        elif failed_auths >= 3:
            score += 25
            reasons.append(f"Repeated authentication failures ({failed_auths})")

        # 6. Reputation penalty decay
        if state.reputation_penalty > 0:
            score += int(state.reputation_penalty)
            reasons.append(f"Residual threat reputation penalty (+{int(state.reputation_penalty)})")
            state.reputation_penalty = max(0.0, state.reputation_penalty - 0.5)

        # Cap score to [0, 100]
        final_score = min(100, max(0, score))

        # Determine Risk Tier and Progressive Action
        if final_score < 30:
            tier = RiskTier.NORMAL
            delay_ms = 0
            requires_pow = False
            is_blocked = False
        elif final_score < 60:
            tier = RiskTier.MONITORED
            delay_ms = 0
            requires_pow = False
            is_blocked = False
        elif final_score < 80:
            tier = RiskTier.THROTTLED
            delay_ms = int(100 + (final_score - 60) * 7.5) # 100ms to 250ms
            requires_pow = False
            is_blocked = False
        elif final_score < 95:
            tier = RiskTier.CHALLENGED
            delay_ms = 150
            requires_pow = True
            is_blocked = False
        else:
            tier = RiskTier.BLOCKED
            delay_ms = 0
            requires_pow = False
            is_blocked = True

        return TrafficRiskAssessment(
            risk_score=final_score,
            risk_tier=tier,
            client_key=client_key,
            ip_hash=ip_hash,
            reasons=reasons,
            delay_ms=delay_ms,
            requires_pow=requires_pow,
            is_blocked=is_blocked,
        )

    def record_error(self, ip: str, user_agent: Optional[str] = None, session_id: Optional[str] = None):
        """Records an HTTP error event for an identity."""
        client_key, _ = self.generate_identity_key(ip, user_agent, session_id)
        state = self._states.get(client_key)
        if state:
            state.error_timestamps.append(time.time())

    def record_auth_failure(self, ip: str, user_agent: Optional[str] = None, session_id: Optional[str] = None):
        """Records an authentication failure event for an identity."""
        client_key, _ = self.generate_identity_key(ip, user_agent, session_id)
        state = self._states.get(client_key)
        if state:
            state.failed_auth_timestamps.append(time.time())
            state.reputation_penalty = min(50.0, state.reputation_penalty + 15.0)

    def record_auth_success(self, ip: str, user_agent: Optional[str] = None, session_id: Optional[str] = None):
        """Reduces risk on successful authenticated action."""
        client_key, _ = self.generate_identity_key(ip, user_agent, session_id)
        state = self._states.get(client_key)
        if state:
            state.failed_auth_timestamps.clear()
            state.reputation_penalty = max(0.0, state.reputation_penalty - 20.0)

    def _prune_deque(self, q: Deque[float], now: float, window: float):
        cutoff = now - window
        while q and q[0] < cutoff:
            q.popleft()

    def _maybe_cleanup(self, now: float):
        if now - self._last_cleanup < 120.0 and len(self._states) < self.max_clients:
            return
        self._last_cleanup = now
        cutoff = now - (self.window_seconds * 3)
        expired_keys = [k for k, v in self._states.items() if v.last_seen < cutoff]
        for k in expired_keys:
            del self._states[k]


# Singleton instance for application lifecycle
traffic_risk_engine = TrafficRiskEngine()
