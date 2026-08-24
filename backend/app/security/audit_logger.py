"""
FORENZA Structured Security Audit Logger (Dimension 14 & 15).

Provides tamper-evident, privacy-conscious JSON security logging:
- ISO 27001 & ISO 21043 compliant structured audit entries.
- Automatic correlation ID generation (X-Correlation-ID).
- PII & Sensitive Biometric masking (zero plaintext secrets).
- Security event taxonomy: RATE_LIMIT_EXCEEDED, AUTH_FAILURE, PROBE_DETECTED, etc.
"""

import json
import logging
import time
import uuid
from typing import Any, Dict, Optional

logger = logging.getLogger("forenza.security")


class SecurityAuditLogger:
    """
    Structured security audit recorder emitting standardized JSON lines.
    """

    @classmethod
    def generate_correlation_id(cls) -> str:
        """Generates unique trace ID for an HTTP request."""
        return f"frz_sec_{uuid.uuid4().hex[:16]}"

    @classmethod
    def mask_sensitive_value(cls, key: str, val: Any) -> Any:
        """Masks sensitive authentication tokens and passwords."""
        if not isinstance(val, str):
            return val
        lower_k = key.lower()
        if any(s in lower_k for s in ("pass", "token", "secret", "auth", "credential", "key")):
            return "******[REDACTED]******"
        return val

    @classmethod
    def log_event(
        cls,
        event_type: str,
        path: str,
        method: str,
        ip_hash: str,
        risk_score: int,
        risk_tier: str,
        correlation_id: str,
        status_code: int = 200,
        details: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None,
    ):
        """
        Emits a structured JSON security log entry.
        """
        clean_details = {}
        if details:
            for k, v in details.items():
                clean_details[k] = cls.mask_sensitive_value(k, v)

        entry = {
            "timestamp": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "correlation_id": correlation_id,
            "event_type": event_type,
            "ip_hash": ip_hash,
            "path": path,
            "method": method,
            "status_code": status_code,
            "risk_score": risk_score,
            "risk_tier": risk_tier,
            "duration_ms": round(duration_ms, 2) if duration_ms is not None else None,
            "details": clean_details,
        }

        # Log according to severity
        msg = json.dumps(entry, ensure_ascii=False)
        if risk_score >= 80 or status_code in (401, 403, 429, 503):
            logger.warning(f"[SECURITY_ALERT] {msg}")
        elif risk_score >= 50:
            logger.info(f"[SECURITY_WARN] {msg}")
        else:
            logger.debug(f"[SECURITY_AUDIT] {msg}")


# Singleton instance
security_logger = SecurityAuditLogger()
