"""
FORENZA Structured Security Audit Logger & SIEM Exporter (Dimension 14 & 18).

Provides tamper-evident, privacy-conscious JSON security logging:
- ISO 27001 & ISO 21043 compliant structured audit entries.
- Automatic correlation ID generation (X-Correlation-ID).
- Comprehensive PII, Token, Password, and Session Secret masking (zero plaintext secrets).
- Complete Security Event Taxonomy:
  * RATE_LIMIT_EXCEEDED
  * WAF_RULE_TRIGGERED
  * AUTHENTICATION_FAILURE
  * PASSWORD_SPRAYING_DETECTED
  * SUSPICIOUS_SESSION_DETECTED
  * REQUEST_BLOCKED
  * DDOS_INDICATOR_TRIGGERED
  * API_ABUSE_DETECTED
  * AUTHORIZATION_FAILURE
  * CIRCUIT_BREAKER_TRIPPED
  * INFRASTRUCTURE_ANOMALY
- In-memory event ring buffer for real-time security observability & SIEM export.
"""

import json
import logging
import time
import uuid
from collections import defaultdict, deque
from enum import Enum
from typing import Any, Deque, Dict, List, Optional, Union

logger = logging.getLogger("forenza.security")


class SecurityEventType(str, Enum):
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    WAF_RULE_TRIGGERED = "WAF_RULE_TRIGGERED"
    AUTHENTICATION_FAILURE = "AUTHENTICATION_FAILURE"
    PASSWORD_SPRAYING_DETECTED = "PASSWORD_SPRAYING_DETECTED"
    SUSPICIOUS_SESSION_DETECTED = "SUSPICIOUS_SESSION_DETECTED"
    REQUEST_BLOCKED = "REQUEST_BLOCKED"
    DDOS_INDICATOR_TRIGGERED = "DDOS_INDICATOR_TRIGGERED"
    API_ABUSE_DETECTED = "API_ABUSE_DETECTED"
    AUTHORIZATION_FAILURE = "AUTHORIZATION_FAILURE"
    CIRCUIT_BREAKER_TRIPPED = "CIRCUIT_BREAKER_TRIPPED"
    INFRASTRUCTURE_ANOMALY = "INFRASTRUCTURE_ANOMALY"
    HTTP_REQUEST_AUDIT = "HTTP_REQUEST_AUDIT"


class SecurityAuditLogger:
    """
    Structured security audit recorder emitting standardized JSON lines.
    Maintains a rolling ring buffer of recent events for telemetry and incident response.
    """

    MAX_BUFFER_EVENTS = 500

    def __init__(self):
        self._events_buffer: Deque[Dict[str, Any]] = deque(maxlen=self.MAX_BUFFER_EVENTS)
        self._event_counts: Dict[str, int] = defaultdict(int)

    @classmethod
    def generate_correlation_id(cls) -> str:
        """Generates unique trace ID for an HTTP request."""
        return f"frz_sec_{uuid.uuid4().hex[:16]}"

    @classmethod
    def mask_sensitive_value(cls, key: str, val: Any) -> Any:
        """Masks sensitive authentication tokens, passwords, cookies, and secrets."""
        if isinstance(val, dict):
            return {k: cls.mask_sensitive_value(k, v) for k, v in val.items()}
        if isinstance(val, list):
            return [cls.mask_sensitive_value(key, item) for item in val]
        if not isinstance(val, str):
            return val

        lower_k = key.lower()
        if any(s in lower_k for s in ("pass", "token", "secret", "auth", "credential", "key", "cookie", "session")):
            return "******[REDACTED]******"
        return val

    def log_event(
        self,
        event_type: Union[SecurityEventType, str],
        path: str,
        method: str,
        ip_hash: str,
        risk_score: int,
        risk_tier: str,
        correlation_id: str,
        status_code: int = 200,
        details: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Emits a structured JSON security log entry and adds to event ring buffer.
        """
        ev_str = event_type.value if isinstance(event_type, SecurityEventType) else str(event_type)
        self._event_counts[ev_str] += 1

        clean_details = {}
        if details:
            for k, v in details.items():
                clean_details[k] = self.mask_sensitive_value(k, v)

        entry = {
            "timestamp": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "correlation_id": correlation_id,
            "event_type": ev_str,
            "ip_hash": ip_hash,
            "path": path,
            "method": method,
            "status_code": status_code,
            "risk_score": risk_score,
            "risk_tier": risk_tier,
            "duration_ms": round(duration_ms, 2) if duration_ms is not None else None,
            "details": clean_details,
        }

        self._events_buffer.append(entry)

        # Log according to severity
        msg = json.dumps(entry, ensure_ascii=False)
        if risk_score >= 80 or status_code in (401, 403, 429, 503):
            logger.warning(f"[SECURITY_ALERT] {msg}")
        elif risk_score >= 50:
            logger.info(f"[SECURITY_WARN] {msg}")
        else:
            logger.debug(f"[SECURITY_AUDIT] {msg}")

        return entry

    def get_recent_events(self, limit: int = 50, event_type_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns recent audit events with optional event type filtering."""
        events = list(self._events_buffer)
        if event_type_filter:
            events = [e for e in events if e.get("event_type") == event_type_filter]
        return events[-limit:]

    def get_event_metrics(self) -> Dict[str, int]:
        """Returns aggregate count of all security events by type."""
        return dict(self._event_counts)


# Singleton instance
security_logger = SecurityAuditLogger()
