"""
FORENZA Structured Security Logging & Detection Test Suite (Dimension 14).

Validates:
- Structured ISO 27001 / ISO 21043 JSON Log Generation
- Security Event Taxonomy (Rate Limit, WAF, Auth Failure, Spraying, Circuit Breaker)
- Deep Sensitive Data Masking (Zero plaintext passwords, tokens, or session secrets)
- Event Ring Buffer & Telemetry Aggregations
"""

import pytest

from app.security.audit_logger import SecurityAuditLogger, SecurityEventType


class TestStructuredSecurityLogging:
    def test_security_event_taxonomy_logging(self):
        """Güvenlik olay taksonomisi (Rate-Limit, WAF, Auth Failure, Spraying) standartlaştırılmış JSON üretmeli."""
        logger = SecurityAuditLogger()
        corr_id = logger.generate_correlation_id()

        entry = logger.log_event(
            event_type=SecurityEventType.PASSWORD_SPRAYING_DETECTED,
            path="/api/v1/auth/login",
            method="POST",
            ip_hash="abc123456789def0",
            risk_score=90,
            risk_tier="CLEARLY_MALICIOUS",
            correlation_id=corr_id,
            status_code=429,
            details={"attempted_accounts_count": 9, "target_endpoint": "/auth/login"},
            duration_ms=45.2,
        )

        assert entry["event_type"] == "PASSWORD_SPRAYING_DETECTED"
        assert entry["correlation_id"] == corr_id
        assert entry["risk_score"] == 90
        assert "iso_time" in entry
        assert entry["details"]["attempted_accounts_count"] == 9

    def test_deep_masking_of_passwords_tokens_and_session_secrets(self):
        """İç içe geçmiş sözlüklerdeki parola, token ve oturum anahtarları kesinlikle maskelenmeli."""
        logger = SecurityAuditLogger()

        sensitive_details = {
            "user_id": "usr_analyst_1",
            "password": "SuperSecretPassword123!",
            "auth_token": "fat_eyJhbGciOi...",
            "session_data": {
                "session_secret": "raw_hmac_secret_xyz",
                "cookie_value": "forenza_session=abc",
                "public_identifier": "analyst_alice",
            },
            "token_list": ["token_1", "token_2"],
        }

        entry = logger.log_event(
            event_type=SecurityEventType.AUTHENTICATION_FAILURE,
            path="/api/v1/auth/login",
            method="POST",
            ip_hash="1122334455667788",
            risk_score=60,
            risk_tier="SUSPICIOUS",
            correlation_id="corr_test_01",
            status_code=401,
            details=sensitive_details,
        )

        details = entry["details"]
        assert details["password"] == "******[REDACTED]******"
        assert details["auth_token"] == "******[REDACTED]******"
        assert details["session_data"]["session_secret"] == "******[REDACTED]******"
        assert details["session_data"]["cookie_value"] == "******[REDACTED]******"
        assert details["session_data"]["public_identifier"] == "analyst_alice"
        assert details["token_list"] == ["******[REDACTED]******", "******[REDACTED]******"]

    def test_event_ring_buffer_and_telemetry_metrics(self):
        """Olay halka arabelleği (ring buffer) ve metrik toplayıcı doğru sayıları vermeli."""
        logger = SecurityAuditLogger()

        logger.log_event(SecurityEventType.RATE_LIMIT_EXCEEDED, "/api", "GET", "h1", 50, "SUSPICIOUS", "c1")
        logger.log_event(SecurityEventType.WAF_RULE_TRIGGERED, "/probe", "GET", "h2", 90, "MALICIOUS", "c2")
        logger.log_event(SecurityEventType.RATE_LIMIT_EXCEEDED, "/api", "GET", "h3", 50, "SUSPICIOUS", "c3")

        metrics = logger.get_event_metrics()
        assert metrics["RATE_LIMIT_EXCEEDED"] == 2
        assert metrics["WAF_RULE_TRIGGERED"] == 1

        recent = logger.get_recent_events(limit=10)
        assert len(recent) == 3

        filtered = logger.get_recent_events(limit=10, event_type_filter="WAF_RULE_TRIGGERED")
        assert len(filtered) == 1
        assert filtered[0]["path"] == "/probe"
