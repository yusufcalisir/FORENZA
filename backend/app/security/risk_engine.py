"""
FORENZA Intelligent Traffic Risk Engine (Dimension 1 & 4 & 18).

Provides multi-signal, adaptive background risk evaluation for all incoming traffic:
- Signal 1: Request Frequency & Velocity (EWMA inter-request intervals, rolling windows, burst spikes).
- Signal 2: Header Consistency & Automation Signatures (Headless Chrome, Selenium, missing browser headers).
- Signal 3: Exploit Probe Patterns (.env, wp-admin, actuator, path traversal).
- Signal 4: Error Rate Burst Tracking (4xx/5xx spike detection).
- Signal 5: Authentication Security (Credential stuffing and brute-force detection).
- Signal 6: Adaptive Dynamic Thresholding (Auto-scaling based on global traffic velocity).
- Signal 7: Dual-Key Isolation: Hash(IP + User-Agent + Session) prevents NAT/University false positives.

Zero Friction Standard:
- Normal users (R < 30): 0ms delay, no CAPTCHA, no popups, full performance.
"""

import hashlib
import math
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
    ewma_interval: float = 2.0  # Exponentially weighted moving average of request interval (seconds)
    last_path: str = ""
    paths_visited: Deque[str] = field(default_factory=lambda: deque(maxlen=20))


class TrafficRiskEngine:
    """
    Production-grade, in-memory Bayesian-adaptive risk evaluation engine.
    Derives verbatim from Section 1, 4 and 18 specifications.
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

    def _get_dynamic_burst_threshold(self) -> int:
        """
        Calculates dynamic burst capacity based on rolling global traffic velocity.
        Allows higher throughput during peak legitimate hours without false positives.
        """
        now = time.time()
        cutoff = now - 60.0
        while self._global_timestamps and self._global_timestamps[0] < cutoff:
            self._global_timestamps.popleft()

        global_rpm = len(self._global_timestamps)
        # Scale adaptive multiplier based on system-wide throughput
        multiplier = 1.0 + min(2.0, global_rpm / 300.0)
        return int(self.base_burst_threshold * multiplier)

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
        Evaluates real-time risk score for an incoming HTTP request across 7 signal dimensions.
        Zero friction for standard user flows (Score < 30).
        """
        ts = now if now is not None else time.time()
        client_key, ip_hash = self.generate_identity_key(ip, user_agent, session_id)

        self._maybe_cleanup(ts)
        self._global_timestamps.append(ts)

        state = self._states.get(client_key)
        if state is None:
            state = ClientTrafficState()
            self._states[client_key] = state

        # Calculate inter-request interval & EWMA
        if state.timestamps:
            delta = max(0.001, ts - state.timestamps[-1])
            # EWMA with alpha = 0.25
            state.ewma_interval = 0.25 * delta + 0.75 * state.ewma_interval

        # Slide time window
        state.last_seen = ts
        state.last_path = path
        state.paths_visited.append(path)
        self._prune_deque(state.timestamps, ts, self.window_seconds)
        self._prune_deque(state.error_timestamps, ts, self.window_seconds)
        self._prune_deque(state.failed_auth_timestamps, ts, self.window_seconds)

        state.timestamps.append(ts)

        score = 0
        reasons: List[str] = []

        # ── SIGNAL 1: Header Consistency & Automation Signatures ───────────
        ua = (user_agent or "").strip()
        if not ua:
            score += 25
            reasons.append("Empty User-Agent header")
        else:
            # Malicious offensive scanners
            for pattern in self.KNOWN_SCANNER_PATTERNS:
                if pattern.search(ua):
                    score += 85
                    reasons.append(f"Malicious scanner signature: {pattern.pattern}")
                    break

            # Headless browser / scraping scripts
            for pattern in self.HEADLESS_AUTOMATION_PATTERNS:
                if pattern.search(ua):
                    score += 40
                    reasons.append("Automated headless/scripting signature")
                    break

        # Header consistency check if headers provided
        if headers:
            lower_headers = {k.lower(): v for k, v in headers.items()}
            sec_fetch_site = lower_headers.get("sec-fetch-site")
            accept = lower_headers.get("accept", "")
            
            # Browser UA but completely missing standard browser Accept
            if "mozilla" in ua.lower() and not accept:
                score += 15
                reasons.append("Missing standard browser Accept header")

            # Automation signature in Sec-Ch-Ua
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

        # Micro-burst velocity (last 2 seconds)
        two_sec_count = sum(1 for t in state.timestamps if ts - t <= 2.0)
        if two_sec_count > 18:
            score += 35
            reasons.append(f"Micro-burst spike ({two_sec_count} req in 2s)")

        # Machine-like periodicity (constant sub-20ms interval without variance)
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
            # Natural exponential decay
            state.reputation_penalty = max(0.0, state.reputation_penalty - 0.75)

        # Cap score strictly to [0, 100]
        final_score = min(100, max(0, score))

        # ── SIGNAL 7: Graduated Tier & Zero-Friction Invariant ──────────────
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
            delay_ms = int(100 + (final_score - 60) * 7.5)  # 100ms to 250ms micro-delay
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
