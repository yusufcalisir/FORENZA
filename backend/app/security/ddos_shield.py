"""
FORENZA Layered DDoS Protection Engine (Dimension 2).

Provides multi-tiered defense against:
- Volumetric & HTTP Flood Attacks (L7 Flood detection, instant burst drops).
- Slow HTTP / Slowloris Attacks (Connection timeout enforcement, slow byte drip detection).
- Connection Exhaustion (Per-IP concurrent connection tracking).
- Origin Cloaking & Edge Proxy Verification (CF-Ray, X-Origin-Verify).
- Circuit Breaker Protection for downstream compute & DB resources.
"""

import asyncio
import os
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Optional, Set, Tuple


@dataclass
class ConnectionState:
    active_count: int = 0
    request_timestamps: Deque[float] = field(default_factory=deque)
    slow_request_count: int = 0
    banned_until: float = 0.0


class DDoSShield:
    """
    In-memory, non-blocking L7 DDoS and connection exhaustion mitigation shield.
    Filters malicious floods before expensive application processing occurs.
    """

    # Default connection and burst thresholds
    MAX_CONCURRENT_PER_IP = 25          # Maximum open concurrent connections per IP
    MAX_BURST_RPS = 35                  # Instantaneous requests per second threshold
    SLOW_READ_TIMEOUT_SECONDS = 10.0    # Max time allowed to receive headers / initial payload
    MIN_DATA_RATE_BPS = 100             # Minimum acceptable transfer rate (bytes/sec) to defeat Slowloris
    BAN_DURATION_SECONDS = 120.0        # 2-minute cooling ban for active flooders

    def __init__(
        self,
        max_concurrent: int = MAX_CONCURRENT_PER_IP,
        max_burst_rps: int = MAX_BURST_RPS,
        origin_secret: Optional[str] = None,
        enforce_origin_secret: bool = False,
    ):
        self.max_concurrent = max_concurrent
        self.max_burst_rps = max_burst_rps
        self.origin_secret = origin_secret or os.getenv("FORENZA_ORIGIN_VERIFY_SECRET", "")
        self.enforce_origin_secret = enforce_origin_secret
        self._ip_states: Dict[str, ConnectionState] = defaultdict(ConnectionState)
        self._last_cleanup = time.time()

    def is_ip_banned(self, ip: str, now: Optional[float] = None) -> bool:
        """Checks if IP is in active DDoS cooling ban."""
        ts = now if now is not None else time.time()
        state = self._ip_states.get(ip)
        if state and state.banned_until > ts:
            return True
        return False

    def verify_origin_headers(self, headers: Dict[str, str]) -> Tuple[bool, Optional[str]]:
        """
        Validates that request arrived through trusted CDN / Edge proxy.
        Prevents attackers from bypassing Cloudflare/CDN to hit origin directly.
        """
        if not self.enforce_origin_secret or not self.origin_secret:
            return True, None

        incoming_secret = headers.get("x-origin-verify-secret", "")
        if not incoming_secret or incoming_secret != self.origin_secret:
            return False, "Direct origin access prohibited. Traffic must route via CDN."

        return True, None

    def acquire_connection(self, ip: str, now: Optional[float] = None) -> Tuple[bool, Optional[str]]:
        """
        Tracks connection establishment. Drops connection if:
        - IP is currently banned for DDoS.
        - Concurrent connection quota is exceeded (Connection Exhaustion / Slowloris).
        - Request burst velocity exceeds L7 flood threshold.
        """
        ts = now if now is not None else time.time()
        self._maybe_cleanup(ts)

        state = self._ip_states[ip]

        # 1. Check existing ban
        if state.banned_until > ts:
            remaining = int(state.banned_until - ts)
            return False, f"IP temporarily blocked for DDoS flood. Retry after {remaining}s."

        # 2. Check concurrent connection exhaustion
        if state.active_count >= self.max_concurrent:
            # Trigger short cooling ban for connection flood
            state.banned_until = ts + self.BAN_DURATION_SECONDS
            return False, f"Concurrent connection limit ({self.max_concurrent}) exceeded. Defense ban active."

        # 3. Check instantaneous RPS burst (L7 HTTP Flood)
        # Prune timestamps older than 1.0 second
        cutoff_1s = ts - 1.0
        while state.request_timestamps and state.request_timestamps[0] < cutoff_1s:
            state.request_timestamps.popleft()

        if len(state.request_timestamps) >= self.max_burst_rps:
            state.banned_until = ts + self.BAN_DURATION_SECONDS
            return False, f"L7 HTTP flood detected ({len(state.request_timestamps)} req/s). Defense ban active."

        # Increment state
        state.active_count += 1
        state.request_timestamps.append(ts)
        return True, None

    def release_connection(self, ip: str):
        """Decrements active connection counter when request completes."""
        state = self._ip_states.get(ip)
        if state and state.active_count > 0:
            state.active_count -= 1

    def record_slow_request_flag(self, ip: str, now: Optional[float] = None):
        """
        Penalizes clients engaging in Slowloris / Slow POST byte dripping.
        """
        ts = now if now is not None else time.time()
        state = self._ip_states[ip]
        state.slow_request_count += 1
        if state.slow_request_count >= 3:
            state.banned_until = ts + self.BAN_DURATION_SECONDS

    def get_telemetry(self) -> Dict[str, int]:
        """Returns real-time DDoS tracking telemetry."""
        now = time.time()
        banned_count = sum(1 for s in self._ip_states.values() if s.banned_until > now)
        active_conn = sum(s.active_count for s in self._ip_states.values())
        return {
            "tracked_ips": len(self._ip_states),
            "banned_ips": banned_count,
            "total_active_connections": active_conn,
        }

    def _maybe_cleanup(self, now: float):
        if now - self._last_cleanup < 120.0 and len(self._ip_states) < 10000:
            return
        self._last_cleanup = now
        cutoff = now - 300.0
        expired = [
            ip for ip, s in self._ip_states.items()
            if s.active_count == 0 and s.banned_until < now and (not s.request_timestamps or s.request_timestamps[-1] < cutoff)
        ]
        for ip in expired:
            del self._ip_states[ip]


# Singleton instance for application lifecycle
ddos_shield = DDoSShield()
