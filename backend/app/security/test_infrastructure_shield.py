"""
FORENZA Infrastructure Protection Test Suite (Dimension 10).

Validates:
- Circuit Breaker State Transitions (CLOSED -> OPEN -> HALF_OPEN -> CLOSED)
- Circuit Breaker Fail-Fast & Retry-After Timing
- Secrets Hygiene Auditor (Rejection of insecure defaults)
- Restricted Port & Database Isolation Validation
- TLS 1.3 & HSTS Invariant Enforcement
"""

import time
import pytest

from app.security.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitState
from app.security.infra_guard import InfrastructureGuard


class TestInfrastructureProtection:
    def test_circuit_breaker_closed_to_open_transition(self):
        """Ardışık 5 başarısızlıktan sonra devre kesici OPEN durumuna geçmeli ve istekleri durdurmalı."""
        config = CircuitBreakerConfig(failure_threshold=5, recovery_timeout_seconds=20.0)
        cb = CircuitBreaker("database_primary", config)

        assert cb.state == CircuitState.CLOSED
        assert cb.can_execute()[0] is True

        # Record 4 failures -> still CLOSED
        for _ in range(4):
            cb.record_failure()
            assert cb.state == CircuitState.CLOSED

        # 5th failure -> trips to OPEN
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

        # Subsequent requests fail fast with retry_after
        allowed, err, retry_after = cb.can_execute()
        assert allowed is False
        assert "unavailable" in err.lower()
        assert retry_after > 0

    def test_circuit_breaker_recovery_to_half_open_and_closed(self):
        """Soğuma süresi bittiğinde HALF_OPEN ile test edilmeli ve 3 başarıda tamamen CLOSED'a dönmeli."""
        config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout_seconds=10.0, half_open_success_threshold=3)
        cb = CircuitBreaker("biocompute_worker", config)
        base_time = 1000.0

        # Trip to OPEN
        cb.record_failure(now=base_time)
        cb.record_failure(now=base_time)
        assert cb.state == CircuitState.OPEN

        # Before timeout (t = 1005s) -> still OPEN
        assert cb.can_execute(now=base_time + 5.0)[0] is False

        # After timeout (t = 1011s) -> transitions to HALF_OPEN
        allowed_half, _, _ = cb.can_execute(now=base_time + 11.0)
        assert allowed_half is True
        assert cb.state == CircuitState.HALF_OPEN

        # 3 consecutive successes recover circuit to CLOSED
        cb.record_success(now=base_time + 11.1)
        assert cb.state == CircuitState.HALF_OPEN
        cb.record_success(now=base_time + 11.2)
        assert cb.state == CircuitState.HALF_OPEN
        cb.record_success(now=base_time + 11.3)
        assert cb.state == CircuitState.CLOSED

    def test_secrets_hygiene_auditor_flags_insecure_defaults(self):
        """Güvensiz varsayılan parolalar ve yetersiz üretim gizli anahtarları tespit edilmeli."""
        guard = InfrastructureGuard()

        # Insecure default secret
        bad_env = {
            "FORENZA_ENVIRONMENT": "production",
            "FORENZA_SESSION_HMAC_SECRET": "secret",  # Insecure default!
            "DATABASE_PASSWORD": "password",          # Insecure default!
        }
        is_safe, violations = guard.audit_secrets_hygiene(bad_env)
        assert is_safe is False
        assert len(violations) >= 2
        assert any("insecure default" in v.lower() for v in violations)

        # Cryptographically strong production secret
        good_env = {
            "FORENZA_ENVIRONMENT": "production",
            "FORENZA_SESSION_HMAC_SECRET": "c7a8e2b1f4d9a6c3e0b8d5a2f1c4e7b9",
            "FORENZA_ORIGIN_VERIFY_SECRET": "9a3f2d1e8c7b6a5f4e3d2c1b0a9f8e7d",
            "DATABASE_PASSWORD": "P#9xK$2vL@8mQ&1zW%4nJ*7tY",
        }
        is_safe_good, violations_good = guard.audit_secrets_hygiene(good_env)
        assert is_safe_good is True
        assert len(violations_good) == 0

    def test_port_exposure_validator_blocks_admin_ports(self):
        """Veritabanı ve yönetim portlarının (5432, 6379, 22) kamuya açılması engellenmeli."""
        guard = InfrastructureGuard()

        # Dangerous exposure of Postgres (5432) and SSH (22) to public
        dangerous_ports = [80, 443, 5432, 22]
        is_safe, violations = guard.validate_port_exposure(dangerous_ports, is_public_facing=True)
        assert is_safe is False
        assert len(violations) >= 2

        # Safe public exposure (only 80 and 443)
        safe_ports = [80, 443]
        is_safe_clean, violations_clean = guard.validate_port_exposure(safe_ports, is_public_facing=True)
        assert is_safe_clean is True
        assert len(violations_clean) == 0

    def test_tls_configuration_validator(self):
        """TLS 1.3 ve HSTS zorunluluğu doğrulanmalı."""
        guard = InfrastructureGuard()

        # Insecure TLS 1.0 -> rejected
        assert guard.validate_tls_configuration("TLSv1.0", hsts_enabled=True)[0] is False

        # Missing HSTS -> rejected
        assert guard.validate_tls_configuration("TLSv1.3", hsts_enabled=False)[0] is False

        # Modern TLS 1.3 + HSTS -> accepted
        assert guard.validate_tls_configuration("TLSv1.3", hsts_enabled=True)[0] is True
