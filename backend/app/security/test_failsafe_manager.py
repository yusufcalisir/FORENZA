"""
FORENZA Fail-Safe & Emergency Control Test Suite (Dimension 16).

Validates:
- Fail-Open Behavior on Public Content during Dependency Crash
- Fail-Closed Behavior on Sensitive Auth/Crypto Routes during Dependency Crash
- Emergency Administrative Override Master Key Activation & Deactivation
- Unauthorized Override Attempt Rejection
"""

import pytest

from app.security.failsafe_manager import FailSafeManager, OperationSensitivity


class TestFailSafeManager:
    def test_fail_open_on_public_route_crash(self):
        """Kamuya açık adli referans yollarında güvenlik servisi çökerse kullanıcı erişimi kesilmemeli (Fail-Open)."""
        manager = FailSafeManager()

        def crashing_security_check():
            raise RuntimeError("Redis connection timeout / third-party outage")

        is_allowed, err, is_degraded = manager.execute_with_failsafe(
            path="/api/v1/forensic/population/matrices",
            method="GET",
            security_check_fn=crashing_security_check,
        )

        assert is_allowed is True
        assert err is None
        assert is_degraded is True

    def test_fail_closed_on_sensitive_auth_route_crash(self):
        """Kimlik doğrulama veya ZKP gibi hassas yollarda güvenlik servisi çökerse kesinlikle engellenmeli (Fail-Closed)."""
        manager = FailSafeManager()

        def crashing_security_check():
            raise RuntimeError("Crypto backend memory error")

        is_allowed, err, is_degraded = manager.execute_with_failsafe(
            path="/api/v1/auth/login",
            method="POST",
            security_check_fn=crashing_security_check,
        )

        assert is_allowed is False
        assert "temporarily degraded" in err.lower()
        assert is_degraded is True

    def test_emergency_admin_bypass_activation(self):
        """Kriptografik anahtar ile acil durum bypass modu açılıp kapatılabilmeli."""
        manager = FailSafeManager()
        master_key = "EMERGENCY_MASTER_SEC_2026_PROD_OVERRIDE"

        # 1. Activate bypass
        ok, msg = manager.activate_emergency_bypass(master_key, "admin_lead")
        assert ok is True
        assert manager.get_failsafe_status()["emergency_bypass_active"] is True

        # 2. Deactivate bypass
        manager.deactivate_emergency_bypass()
        assert manager.get_failsafe_status()["emergency_bypass_active"] is False

    def test_emergency_bypass_unauthorized_key_rejection(self):
        """Geçersiz anahtar ile acil durum modu açma girişimi reddedilmeli."""
        manager = FailSafeManager()

        ok, msg = manager.activate_emergency_bypass("wrong_key_123", "attacker")
        assert ok is False
        assert "Invalid emergency" in msg
        assert manager.get_failsafe_status()["emergency_bypass_active"] is False
