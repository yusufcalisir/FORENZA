"""
FORENZA Session & Device Intelligence Test Suite (Dimension 5).

Validates:
- Privacy-Conscious Device Consistency (Non-invasive hashing)
- Refresh Token Rotation (RTR) Flow
- Automatic Token Family Reuse Detection & Family Revocation
- Inactivity Timeout & Session Hijacking Detection
"""

import time
import pytest

from app.security.session_guard import SessionAuthLevel, SessionSecurityManager


class TestSessionSecurityManager:
    def test_create_and_validate_session_consistency(self):
        """Aynı cihaz ve ağdan gelen meşru oturum doğrulaması sıfır anomaliyle geçmeli."""
        mgr = SessionSecurityManager()
        ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        ip = "195.175.254.10"
        lang = "en-US,en;q=0.9"

        session_id, access_token, refresh_token = mgr.create_session(
            user_id="usr_scientist_42",
            auth_level=SessionAuthLevel.AUTHENTICATED_BASIC,
            user_agent=ua,
            accept_language=lang,
            client_ip=ip,
        )

        assert session_id.startswith("fsess_")
        assert access_token.startswith("fat_")
        assert refresh_token.startswith("frt_")

        # Validate with same context
        valid, risk, anomalies = mgr.validate_session_consistency(
            session_id=session_id,
            user_agent=ua,
            accept_language=lang,
            client_ip=ip,
        )

        assert valid is True
        assert risk == 0
        assert len(anomalies) == 0

    def test_device_context_mismatch_detection(self):
        """Farklı bir User-Agent / Subnet üzerinden oturum çalma girişimi tespit edilmeli."""
        mgr = SessionSecurityManager()
        original_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        original_ip = "203.0.113.50"

        session_id, _, _ = mgr.create_session(
            user_id="usr_analyst_99",
            user_agent=original_ua,
            client_ip=original_ip,
        )

        # Attacker uses stolen session token from Linux / different IP
        attacker_ua = "curl/7.68.0"
        attacker_ip = "198.51.100.22"

        valid, risk, anomalies = mgr.validate_session_consistency(
            session_id=session_id,
            user_agent=attacker_ua,
            client_ip=attacker_ip,
        )

        assert valid is True
        assert risk >= 40
        assert "DEVICE_CONTEXT_MISMATCH" in anomalies

    def test_refresh_token_rotation_flow(self):
        """Her refresh token kullanımında yeni tek kullanımlık token çifti üretilmeli."""
        mgr = SessionSecurityManager()
        _, _, initial_rt = mgr.create_session(user_id="usr_123")

        ok, new_at, new_rt, err = mgr.rotate_refresh_token(initial_rt)
        assert ok is True
        assert new_at is not None
        assert new_rt is not None
        assert new_rt != initial_rt
        assert err is None

        # Rotate again with new token
        ok2, new_at2, new_rt2, err2 = mgr.rotate_refresh_token(new_rt)
        assert ok2 is True
        assert new_rt2 != new_rt
        assert err2 is None

    def test_refresh_token_reuse_attack_revocation(self):
        """Daha önce kullanılmış bir refresh token tekrar sunulursa tüm oturum ailesi derhal feshedilmeli."""
        mgr = SessionSecurityManager()
        sess_id, _, initial_rt = mgr.create_session(user_id="usr_victim_77")

        # Legitimate rotation
        ok, _, new_rt, _ = mgr.rotate_refresh_token(initial_rt)
        assert ok is True

        # Attacker tries to use old initial_rt that was already consumed!
        attack_ok, _, _, err = mgr.rotate_refresh_token(initial_rt)
        assert attack_ok is False
        assert "Token reuse detected" in err

        # Even the new legitimate token must now be invalid because family was revoked
        victim_ok, _, _, err_v = mgr.rotate_refresh_token(new_rt)
        assert victim_ok is False

        # Session should also be terminated
        sess_valid, _, _ = mgr.validate_session_consistency(sess_id, "Mozilla/5.0")
        assert sess_valid is False

    def test_non_invasive_context_hashing(self):
        """Kalıcı cihaz izi (fingerprinting) olmadan yalnız kaba subnet ve UA ailesi kullanılmalı."""
        mgr = SessionSecurityManager()
        ua1 = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0"
        ua2 = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.1"

        # Within same /24 subnet and same UA prefix
        hash1 = mgr.generate_device_context_hash(ua1, "en", "192.168.1.10")
        hash2 = mgr.generate_device_context_hash(ua2, "en", "192.168.1.25")
        assert hash1 == hash2

    def test_session_inactivity_expiration(self):
        """Süresi dolmuş oturumlar temizlenmeli."""
        mgr = SessionSecurityManager()
        sess_id, _, _ = mgr.create_session()

        # Check with timestamp past 24h
        future = time.time() + 90000.0
        valid, _, anomalies = mgr.validate_session_consistency(sess_id, "Mozilla/5.0", now=future)
        assert valid is False
        assert any(a in ("SESSION_EXPIRED_INACTIVITY", "SESSION_NOT_FOUND") for a in anomalies)

