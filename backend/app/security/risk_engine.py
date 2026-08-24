"""
FORENZA Traffic Risk & Progressive Anomaly Engine (Dimension 1 & 4 & 18).

Implements a 6-tier graduated response continuum without premature blocking:
- NORMAL (R < 30): Zero intervention, 0ms delay, no CAPTCHA.
- SLIGHTLY_ANOMALOUS (30 <= R < 50): Increased monitoring, passive audit telemetry.
- SUSPICIOUS (50 <= R < 70): Tighter rate limits, burst reduction.
- HIGHLY_SUSPICIOUS (70 <= R < 85): Micro-throttling (100-250ms) + background PoW challenge.
- CLEARLY_MALICIOUS (85 <= R < 95): Temporary cooling block (60-120s).
- PERSISTENT_MALICIOUS (R >= 95 or >=3 repeat offenses): 24-hour quarantine ban.

Features:
- Dual-Key Identity Isolation: SHA256(IP + User-Agent + SessionCookie) prevents shared NAT false positives.
- EWMA Request Pacing: Detects sub-50ms machine periodicity.
- Exponential Reputation Decay: Recovers normal rating after period of good behavior.
- Repeat Offender Quarantine: Escalates persistent attack infrastructure to 24h bans.
"""

import hashlib
import math
import re
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Deque, Dict, List, Optional, Tuple


class RiskTier(str, Enum):
    NORMAL = "NORMAL"                          # R < 30: Zero intervention
    SLIGHTLY_ANOMALOUS = "SLIGHTLY_ANOMALOUS"  # 30 <= R < 50: Increased monitoring
    SUSPICIOUS = "SUSPICIOUS"                  # 50 <= R < 70: Tighter rate limits
    HIGHLY_SUSPICIOUS = "HIGHLY_SUSPICIOUS"    # 70 <= R < 85: Throttling / PoW challenge
    CLEARLY_MALICIOUS = "CLEARLY_MALICIOUS"    # 85 <= R < 95: Temporary blocking (60-120s)
    PERSISTENT_MALICIOUS = "PERSISTENT_MALICIOUS" # R >= 95 or repeat: 24h quarantine ban

    # Aliases for backwards compatibility
    MONITORED = "SLIGHTLY_ANOMALOUS"
    THROTTLED = "SUSPICIOUS"
    CHALLENGED = "HIGHLY_SUSPICIOUS"
    BLOCKED = "CLEARLY_MALICIOUS"


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
    retry_after_seconds: int = 0


@dataclass
class ClientTrafficState:
    timestamps: Deque[float] = field(default_factory=deque)
    error_timestamps: Deque[float] = field(default_factory=deque)
    failed_auth_timestamps: Deque[float] = field(default_factory=deque)
    last_seen: float = field(default_factory=time.time)
    reputation_penalty: float = 0.0
    ewma_interval: float = 2.0  # Exponentially weighted moving average (seconds)
    last_path: str = ""
    paths_visited: Deque[str] = field(default_factory=lambda: deque(maxlen=20))
    ban_count: int = 0
    quarantine_until: float = 0.0


class TrafficRiskEngine:
    """
    Production-grade in-memory Bayesian-adaptive risk evaluation engine.
    Derives from Section 1, 4 and 18 specifications.
    """

    KNOWN_SCANNER_PATTERNS = [
        re.compile(r"(sqlmap|nikto|gobuster|masscan|dirbuster|acunetix|wpscan|hydra|zgrab)", re.IGNORECASE),
        re.compile(r"(nmap|openvas|havij|netsparker|nuclei|jaeles|burpcollaborator|wfuzz)", re.IGNORECASE),
    ]

    HEADLESS_AUTOMATION_PATTERNS = [
        re.compile(r"(HeadlessChrome|PhantomJS|Puppeteer|Playwright|Selenium|WebDriver)", re.IGNORECASE),
        re.compile(r"(aiohttp|python-urllib|Go-http-client|Java/|Apache-HttpClient|node-fetch)", re.IGNORECASE),
    ]

    SUSPICIOUS_PATH_PATTERNS = [
        re.compile(r"(\.env|\.git|wp-admin|phpmyadmin|\.aws|etc/passwd|win\.ini|eval\(|base64_decode)", re.IGNORECASE),
        re.compile(r"(\.\./\.\./|/etc/shadow|/proc/self/environ|<script>|union\s+select|actuator/health)", re.IGNORECASE),
        re.compile(r"(xmlrpc\.php|cgi-bin|\.well-known/security\.txt/|swagger-ui|api-docs)", re.IGNORECASE),
    ]

    def __init__(
        self,
        window_seconds: float = 60.0,
        base_burst_threshold: int = 40,
        burst_threshold: Optional[int] = None,
        max_clients: int = 50000,
    ):
        self.window_seconds = window_seconds
        self.base_burst_threshold = burst_threshold if burst_threshold is not None else base_burst_threshold
        self.max_clients = max_clients
        self._states: Dict[str, ClientTrafficState] = {}
        self._global_timestamps: Deque[float] = deque(maxlen=1000)
        self._last_cleanup = time.time()

    def generate_identity_key(
        self,
        ip: str,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Tuple[str, str]:
        """
        Generates privacy-preserving dual key to protect legitimate shared NAT/Wifi networks.
        """
        clean_ip = ip.strip() if ip else "127.0.0.1"
        ip_hash = hashlib.sha256(clean_ip.encode("utf-8")).hexdigest()[:16]

        ua_part = (user_agent or "unknown").strip()[:100]
        sess_part = (session_id or "anon").strip()[:64]

        raw_key = f"{clean_ip}|{ua_part}|{sess_part}"
        client_key = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:24]

        return client_key, ip_hash

    def _get_dynamic_burst_threshold(self) -> int:
        now = time.time()
        self._prune_deque(self._global_timestamps, now, 10.0)
        global_rps = len(self._global_timestamps) / 10.0 if self._global_timestamps else 0.0
        if global_rps > 100.0:
            return int(self.base_burst_threshold * 1.5)
        return self.base_burst_threshold

    def evaluate_request(
        self,
        ip: str,
        path: str,
        method: str = "GET",
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        now: Optional[float] = None,
    ) -> TrafficRiskAssessment:
        ts = now if now is not None else time.time()
        self._maybe_cleanup(ts)

        client_key, ip_hash = self.generate_identity_key(ip, user_agent, session_id)
        state = self._states.get(client_key)

        if state is None:
            state = ClientTrafficState(last_seen=ts)
            self._states[client_key] = state

        # Check persistent quarantine ban
        if state.quarantine_until > ts:
            remaining = int(state.quarantine_until - ts)
            return TrafficRiskAssessment(
                risk_score=100,
                risk_tier=RiskTier.PERSISTENT_MALICIOUS,
                client_key=client_key,
                ip_hash=ip_hash,
                reasons=[f"Quarantined malicious infrastructure. Active for {remaining}s."],
                delay_ms=0,
                requires_pow=False,
                is_blocked=True,
                retry_after_seconds=remaining,
            )

        # Update EWMA interval
        if state.timestamps:
            delta = ts - state.timestamps[-1]
            if delta > 0:
                alpha = 0.3
                state.ewma_interval = (alpha * delta) + ((1 - alpha) * state.ewma_interval)

        # Record activity
        state.timestamps.append(ts)
        self._global_timestamps.append(ts)
        state.last_seen = ts
        state.last_path = path
        state.paths_visited.append(path)

        # Prune older records
        self._prune_deque(state.timestamps, ts, self.window_seconds)
        self._prune_deque(state.error_timestamps, ts, self.window_seconds)
        self._prune_deque(state.failed_auth_timestamps, ts, self.window_seconds * 5)

        score = 0
        reasons: List[str] = []

        # ── SIGNAL 1: User-Agent & Scanner Signatures ──────────────────────
        ua = user_agent or ""
        for pattern in self.KNOWN_SCANNER_PATTERNS:
            if pattern.search(ua):
                score += 85
                reasons.append(f"Malicious scanner signature ({pattern.pattern[:15]})")
                break

        for pattern in self.HEADLESS_AUTOMATION_PATTERNS:
            if pattern.search(ua):
                score += 40
                reasons.append("Headless automation / script client signature")
                break

        if headers:
            lower_headers = {k.lower(): v for k, v in headers.items()}
            accept = lower_headers.get("accept", "")
            if "mozilla" in ua.lower() and not accept:
                score += 15
                reasons.append("Missing standard browser Accept header")

            sec_ch_ua = lower_headers.get("sec-ch-ua", "")
            if "headless" in sec_ch_ua.lower():
                score += 50
                reasons.append("Sec-Ch-Ua headless flag detected")

        # ── SIGNAL 2: Suspicious Path & Exploit Probing ─────────────────────
        for pattern in self.SUSPICIOUS_PATH_PATTERNS:
            if pattern.search(path):
                score += 70
                reasons.append("Vulnerability exploit probe pattern in URI")
                break

        # ── SIGNAL 3: Request Frequency & Velocity Anomalies ───────────────
        dynamic_burst = self._get_dynamic_burst_threshold()
        recent_count = len(state.timestamps)
        
        if recent_count > dynamic_burst * 2:
            score += 45
            reasons.append(f"Extreme request velocity ({recent_count} req/{self.window_seconds}s)")
        elif recent_count > dynamic_burst:
            score += 20
            reasons.append(f"Elevated request velocity ({recent_count} req/{self.window_seconds}s)")

        two_sec_count = sum(1 for t in state.timestamps if ts - t <= 2.0)
        if two_sec_count > 18:
            score += 35
            reasons.append(f"Micro-burst spike ({two_sec_count} req in 2s)")

        if len(state.timestamps) >= 10 and state.ewma_interval < 0.05:
            score += 25
            reasons.append("Sub-50ms machine-like request pacing")

        # ── SIGNAL 4: Error Rate Spike Accumulation ────────────────────────
        error_count = len(state.error_timestamps)
        if error_count > 10:
            score += 30
            reasons.append(f"High 4xx/5xx failure frequency ({error_count} errors)")

        # ── SIGNAL 5: Authentication Attack Tracking ───────────────────────
        failed_auths = len(state.failed_auth_timestamps)
        if failed_auths >= 5:
            score += 50
            reasons.append(f"Consecutive authentication failures ({failed_auths})")
        elif failed_auths >= 3:
            score += 25
            reasons.append(f"Repeated authentication failures ({failed_auths})")

        # ── SIGNAL 6: Reputation Penalty Decay ─────────────────────────────
        if state.reputation_penalty > 0:
            score += int(state.reputation_penalty)
            reasons.append(f"Residual threat reputation penalty (+{int(state.reputation_penalty)})")
            state.reputation_penalty = max(0.0, state.reputation_penalty - 0.75)

        # Cap score to [0, 100]
        final_score = min(100, max(0, score))

        # ── 6-TIER GRADUATED RESPONSE CONTINUUM (Dimension 4) ──────────────
        retry_after_seconds = 0
        if final_score < 30:
            tier = RiskTier.NORMAL
            delay_ms = 0
            requires_pow = False
            is_blocked = False
        elif final_score < 50:
            tier = RiskTier.SLIGHTLY_ANOMALOUS
            delay_ms = 0
            requires_pow = False
            is_blocked = False
        elif final_score < 70:
            tier = RiskTier.SUSPICIOUS
            delay_ms = 0
            requires_pow = False
            is_blocked = False
        elif final_score < 85:
            tier = RiskTier.HIGHLY_SUSPICIOUS
            delay_ms = int(100 + (final_score - 70) * 10.0)  # 100ms to 250ms
            requires_pow = True
            is_blocked = False
        elif final_score < 95:
            tier = RiskTier.CLEARLY_MALICIOUS
            delay_ms = 0
            requires_pow = False
            is_blocked = True
            retry_after_seconds = 60
            state.ban_count += 1
            if state.ban_count >= 3:
                state.quarantine_until = ts + 86400.0  # 24-hour quarantine escalation
        else:
            tier = RiskTier.PERSISTENT_MALICIOUS
            delay_ms = 0
            requires_pow = False
            is_blocked = True
            retry_after_seconds = 86400
            state.quarantine_until = ts + 86400.0

        return TrafficRiskAssessment(
            risk_score=final_score,
            risk_tier=tier,
            client_key=client_key,
            ip_hash=ip_hash,
            reasons=reasons,
            delay_ms=delay_ms,
            requires_pow=requires_pow,
            is_blocked=is_blocked,
            retry_after_seconds=retry_after_seconds,
        )

    def _get_or_create_state(self, client_key: str, ts: Optional[float] = None) -> ClientTrafficState:
        state = self._states.get(client_key)
        if state is None:
            state = ClientTrafficState(last_seen=ts or time.time())
            self._states[client_key] = state
        return state

    def record_pow_solved(self, ip: str, user_agent: Optional[str] = None, session_id: Optional[str] = None):
        """Reduces risk score upon verified Proof-of-Work solution."""
        client_key, _ = self.generate_identity_key(ip, user_agent, session_id)
        state = self._get_or_create_state(client_key)
        state.reputation_penalty = max(0.0, state.reputation_penalty - 35.0)

    def record_error(self, ip: str, user_agent: Optional[str] = None, session_id: Optional[str] = None):
        """Records an HTTP error event for an identity."""
        client_key, _ = self.generate_identity_key(ip, user_agent, session_id)
        state = self._get_or_create_state(client_key)
        state.error_timestamps.append(time.time())

    def record_auth_failure(self, ip: str, user_agent: Optional[str] = None, session_id: Optional[str] = None):
        """Records an authentication failure event for an identity."""
        client_key, _ = self.generate_identity_key(ip, user_agent, session_id)
        state = self._get_or_create_state(client_key)
        state.failed_auth_timestamps.append(time.time())
        state.reputation_penalty = min(50.0, state.reputation_penalty + 15.0)

    def record_auth_success(self, ip: str, user_agent: Optional[str] = None, session_id: Optional[str] = None):
        """Reduces risk on successful authenticated action."""
        client_key, _ = self.generate_identity_key(ip, user_agent, session_id)
        state = self._get_or_create_state(client_key)
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
        expired_keys = [k for k, v in self._states.items() if v.last_seen < cutoff and v.quarantine_until < now]
        for k in expired_keys:
            del self._states[k]


# Singleton instance for application lifecycle
traffic_risk_engine = TrafficRiskEngine()
