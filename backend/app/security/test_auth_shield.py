"""
FORENZA Authentication Security Test Suite (Dimension 6).

Validates:
- Secure PBKDF2-HMAC-SHA256 Password Hashing & Timing-Safe Verification
- Constant-Time Dummy Hash Execution (Anti-Account Enumeration)
- Per-Account Lockout Thresholds
- Per-IP Password Spraying Attack Detection
- Progressive Micro-Delays on Suspicious Failures
- Double Submit Cookie CSRF Validation
"""

import time
import pytest

from app.security.auth_shield import AuthenticationShield


class TestAuthenticationShield:
    def test_password_hashing_and_verification(self):
        """Parola güvenli hashlenmeli, doğru parola onaylanmalı, yanlış parola reddedilmeli."""
        shield = AuthenticationShield()
        pwd = "UltraSecurePassword#2026!"
        h = shield.hash_password(pwd)

        assert h.startswith("pbkdf2_sha256$600000$")
        assert shield.verify_password(pwd, h) is True
        assert shield.verify_password("WrongPassword123", h) is False

    def test_constant_time_dummy_verification_on_nonexistent_user(self):
        """Kullanıcı veritabanında bulunamadığında timing saldırısını önleyen dummy hash çalışmalı."""
        shield = AuthenticationShield()
        # Stored hash is None (user does not exist)
        res = shield.verify_password("AnyPassword123!", None)
        assert res is False

    def test_per_account_lockout_after_max_failures(self):
        """Bir hesaba art arda 5 başarısız deneme yapıldığında hesap 15 dakika kilitlenmeli."""
        shield = AuthenticationShield()
        email = "investigator.doe@forenza.org"
        client_ip = "203.0.113.15"

        # 4 failed attempts: Allowed with progressive delay
        for _ in range(4):
            allowed, _, _ = shield.pre_login_check(email, client_ip)
            assert allowed is True
            shield.record_login_attempt(email, client_ip, success=False)

        # 5th failed attempt triggers lockout
        locked, msg = shield.record_login_attempt(email, client_ip, success=False)
        assert locked is True
        assert "locked" in msg.lower()

        # Next pre-flight check must reject
        allowed, err, _ = shield.pre_login_check(email, client_ip)
        assert allowed is False
        assert "locked" in err.lower()

    def test_password_spraying_detection_across_multiple_accounts(self):
        """Bir IP'den çok sayıda farklı hesaba tek tek şifre denendiğinde (Spraying) IP banlanmalı."""
        shield = AuthenticationShield()
        sprayer_ip = "198.51.100.80"

        # Attempt 9 distinct accounts from the same IP
        for i in range(9):
            acc_email = f"user_{i}@forenza.org"
            shield.record_login_attempt(acc_email, sprayer_ip, success=False)

        # Pre-flight for next login from this IP should be blocked for spraying
        allowed, err, _ = shield.pre_login_check("target_user@forenza.org", sprayer_ip)
        assert allowed is False
        assert "too many" in err.lower() or "network" in err.lower()

    def test_progressive_delay_on_consecutive_failures(self):
        """İlk 2 başarısız denemede 0ms gecikme, 3. ve 4. denemede kademeli mikro gecikme olmalı."""
        shield = AuthenticationShield()
        email = "analyst.smith@forenza.org"
        ip = "203.0.113.40"

        # 0 and 1 failures -> 0ms delay
        _, _, d0 = shield.pre_login_check(email, ip)
        assert d0 == 0
        shield.record_login_attempt(email, ip, success=False)

        _, _, d1 = shield.pre_login_check(email, ip)
        assert d1 == 0
        shield.record_login_attempt(email, ip, success=False)

        # 2 failures -> 0ms delay
        _, _, d2 = shield.pre_login_check(email, ip)
        assert d2 == 0
        shield.record_login_attempt(email, ip, success=False)

        # 3 failures -> micro-delay >= 100ms
        _, _, d3 = shield.pre_login_check(email, ip)
        assert d3 >= 100

    def test_double_submit_cookie_csrf_token_validation(self):
        """Double submit CSRF token eşleşmesi doğrulanmalı."""
        shield = AuthenticationShield()
        session_id = "fsess_test_123"
        token = shield.generate_csrf_token(session_id)

        # Matching tokens pass
        assert shield.validate_csrf_token(token, token) is True

        # Mismatched tokens fail
        assert shield.validate_csrf_token(token, "invalid_csrf_token") is False

        # Missing token fails
        assert shield.validate_csrf_token(None, token) is False
