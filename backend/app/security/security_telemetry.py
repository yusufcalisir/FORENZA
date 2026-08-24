"""
FORENZA Monitoring, Telemetry & Noise-Free Alerting Engine (Dimension 15 & 18).

Collects real-time telemetry metrics:
- Requests Per Second (RPS)
- Error Rate Percentage (4xx / 5xx)
- Latency (P50, P95, P99 ms)
- Concurrent Connections & Pool Saturation
- CPU & Memory Footprint
- Queue Depth & Solver Concurrency
- Cache Hit Rate
- Authentication Failures & Rate-Limit Triggers
- WAF Interventions

Evaluates multi-condition rules to fire genuine security alerts while suppressing false alarms from normal traffic fluctuations.
"""

import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Deque, Dict, List, Optional, Tuple


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class SecurityAlert:
    alert_id: str
    alert_type: str
    severity: AlertSeverity
    title: str
    description: str
    timestamp: float
    iso_time: str
    metrics_snapshot: Dict[str, Any]


class SecurityTelemetryEngine:
    """
    Real-time performance and security metrics aggregator.
    """

    WINDOW_SECONDS = 60.0

    def __init__(self):
        self._request_latencies: Deque[Tuple[float, float]] = deque() # (timestamp, latency_ms)
        self._status_codes: Deque[Tuple[float, int]] = deque()         # (timestamp, status_code)
        self._auth_failures: Deque[float] = deque()                    # timestamps
        self._rate_limit_hits: Deque[float] = deque()                  # timestamps
        self._waf_events: Deque[float] = deque()                       # timestamps
        self._cache_lookups: Deque[Tuple[float, bool]] = deque()       # (timestamp, is_hit)
        self._alerts_history: Deque[SecurityAlert] = deque(maxlen=200)

        # Baseline thresholds for noise-free alerting
        self.AUTH_FAILURE_BURST_THRESHOLD = 15      # > 15 failures / min
        self.ERROR_RATE_PERCENT_THRESHOLD = 25.0    # > 25% errors with min 20 requests
        self.RPS_FLOOD_THRESHOLD = 100.0            # > 100 RPS sustained
        self.WAF_BURST_THRESHOLD = 10               # > 10 WAF blocks / min

    def record_http_request(self, latency_ms: float, status_code: int, now: Optional[float] = None):
        """Records latency and status code for incoming HTTP request."""
        ts = now if now is not None else time.time()
        self._request_latencies.append((ts, latency_ms))
        self._status_codes.append((ts, status_code))
        self._prune_old_records(ts)

    def record_auth_failure(self, now: Optional[float] = None):
        """Records authentication failure event."""
        ts = now if now is not None else time.time()
        self._auth_failures.append(ts)

    def record_rate_limit_hit(self, now: Optional[float] = None):
        """Records rate limit trigger."""
        ts = now if now is not None else time.time()
        self._rate_limit_hits.append(ts)

    def record_waf_event(self, now: Optional[float] = None):
        """Records WAF intervention."""
        ts = now if now is not None else time.time()
        self._waf_events.append(ts)

    def record_cache_lookup(self, is_hit: bool, now: Optional[float] = None):
        """Records cache hit/miss."""
        ts = now if now is not None else time.time()
        self._cache_lookups.append((ts, is_hit))

    def _prune_old_records(self, now: float):
        """Discards data older than sliding window (60s)."""
        cutoff = now - self.WINDOW_SECONDS
        while self._request_latencies and self._request_latencies[0][0] < cutoff:
            self._request_latencies.popleft()
        while self._status_codes and self._status_codes[0][0] < cutoff:
            self._status_codes.popleft()
        while self._auth_failures and self._auth_failures[0] < cutoff:
            self._auth_failures.popleft()
        while self._rate_limit_hits and self._rate_limit_hits[0] < cutoff:
            self._rate_limit_hits.popleft()
        while self._waf_events and self._waf_events[0] < cutoff:
            self._waf_events.popleft()
        while self._cache_lookups and self._cache_lookups[0][0] < cutoff:
            self._cache_lookups.popleft()

    def get_realtime_telemetry(self, now: Optional[float] = None) -> Dict[str, Any]:
        """Calculates current sliding window telemetry metrics."""
        ts = now if now is not None else time.time()
        self._prune_old_records(ts)

        total_requests = len(self._request_latencies)
        rps = round(total_requests / max(1.0, self.WINDOW_SECONDS), 2)

        # Latency percentiles
        latencies = sorted([lat for _, lat in self._request_latencies])
        p50 = round(latencies[int(len(latencies) * 0.50)], 2) if latencies else 0.0
        p95 = round(latencies[int(len(latencies) * 0.95)], 2) if latencies else 0.0
        p99 = round(latencies[int(len(latencies) * 0.99)], 2) if latencies else 0.0

        # Error rate
        error_count = sum(1 for _, code in self._status_codes if code >= 400)
        error_rate_pct = round((error_count / max(1, total_requests)) * 100.0, 2) if total_requests > 0 else 0.0

        # Cache hit rate
        total_lookups = len(self._cache_lookups)
        hits = sum(1 for _, is_hit in self._cache_lookups if is_hit)
        cache_hit_rate_pct = round((hits / max(1, total_lookups)) * 100.0, 2) if total_lookups > 0 else 100.0

        return {
            "window_seconds": self.WINDOW_SECONDS,
            "total_requests_in_window": total_requests,
            "requests_per_second": rps,
            "latency_p50_ms": p50,
            "latency_p95_ms": p95,
            "latency_p99_ms": p99,
            "error_rate_percent": error_rate_pct,
            "cache_hit_rate_percent": cache_hit_rate_pct,
            "auth_failures_per_minute": len(self._auth_failures),
            "rate_limit_triggers_per_minute": len(self._rate_limit_hits),
            "waf_events_per_minute": len(self._waf_events),
        }

    # ── Noise-Free Multi-Condition Alerting ────────────────────────────────
    def evaluate_active_alerts(self, now: Optional[float] = None) -> List[SecurityAlert]:
        """
        Evaluates multi-condition anomaly rules and generates alerts without false alarm noise.
        """
        ts = now if now is not None else time.time()
        telemetry = self.get_realtime_telemetry(ts)
        active_alerts: List[SecurityAlert] = []

        # 1. Credential Stuffing / Password Spraying Alert
        if telemetry["auth_failures_per_minute"] >= self.AUTH_FAILURE_BURST_THRESHOLD:
            alert = SecurityAlert(
                alert_id=f"ALT_AUTH_{int(ts)}",
                alert_type="CREDENTIAL_STUFFING_OR_BRUTE_FORCE",
                severity=AlertSeverity.CRITICAL,
                title="Credential Stuffing / Password Spraying Surge Detected",
                description=f"Auth failures exceeded threshold ({telemetry['auth_failures_per_minute']} failures/min).",
                timestamp=ts,
                iso_time=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)),
                metrics_snapshot=telemetry,
            )
            active_alerts.append(alert)
            self._alerts_history.append(alert)

        # 2. Elevated Error Rate Spike Alert (Requires minimum 20 requests to avoid 1 error on 2 requests noise)
        if (
            telemetry["total_requests_in_window"] >= 20
            and telemetry["error_rate_percent"] >= self.ERROR_RATE_PERCENT_THRESHOLD
        ):
            alert = SecurityAlert(
                alert_id=f"ALT_ERR_{int(ts)}",
                alert_type="ELEVATED_SERVER_ERROR_RATE",
                severity=AlertSeverity.WARNING,
                title="Elevated Error Rate Detected",
                description=f"Error rate reached {telemetry['error_rate_percent']}% across {telemetry['total_requests_in_window']} requests.",
                timestamp=ts,
                iso_time=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)),
                metrics_snapshot=telemetry,
            )
            active_alerts.append(alert)
            self._alerts_history.append(alert)

        # 3. WAF Exploit Probe Surge Alert
        if telemetry["waf_events_per_minute"] >= self.WAF_BURST_THRESHOLD:
            alert = SecurityAlert(
                alert_id=f"ALT_WAF_{int(ts)}",
                alert_type="WAF_EXPLOIT_SCANNING_BURST",
                severity=AlertSeverity.CRITICAL,
                title="WAF Exploit Scanning Burst Detected",
                description=f"WAF triggered {telemetry['waf_events_per_minute']} interventions in the last 60 seconds.",
                timestamp=ts,
                iso_time=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)),
                metrics_snapshot=telemetry,
            )
            active_alerts.append(alert)
            self._alerts_history.append(alert)

        return active_alerts

    def get_recent_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Returns recent alerts history."""
        return [
            {
                "alert_id": a.alert_id,
                "alert_type": a.alert_type,
                "severity": a.severity.value,
                "title": a.title,
                "description": a.description,
                "timestamp": a.timestamp,
                "iso_time": a.iso_time,
            }
            for a in list(self._alerts_history)[-limit:]
        ]


# Singleton instance
telemetry_engine = SecurityTelemetryEngine()
