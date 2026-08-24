"""
FORENZA Zero-Friction User Experience Test Suite (Dimension 18).

Validates that legitimate users experience the web application exactly as they would without security friction:
1. Zero CAPTCHA on regular visits ($R < 30$).
2. Zero verification on page refreshes.
3. Zero shared IP / NAT collateral damage (Dual-Key Isolation).
4. Zero added artificial delays for normal traffic ($0.0ms$).
5. Zero forced re-authentication for active sessions.
6. Non-invasive privacy-conscious telemetry.
7. High-throughput power-user tolerance for legitimate forensic workflows.
"""

import pytest

from app.security.rate_limiter import AdaptiveRateLimiter, RateLimitCategory
from app.security.risk_engine import RiskTier, TrafficRiskEngine
from app.security.session_guard import SessionAuthLevel, SessionSecurityManager
from app.security.zero_friction_auditor import ZeroFrictionAuditor


class TestZeroFrictionUserExperience:
    def test_normal_user_friction_free_browsing(self):
        """Meşru bir adli analist 25 vaka sayfasını gezerken 0ms yapay gecikme ve %100 sürtünmesiz deneyim yaşamalı."""
        auditor = ZeroFrictionAuditor()
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        report = auditor.audit_normal_user_browsing_session(
            client_ip="198.51.100.75",
            user_agent=ua,
            page_views=25,
            average_interval_seconds=2.0,
        )

        assert report.total_requests == 25
        assert report.friction_events_count == 0
        assert report.added_artificial_delay_ms == 0.0
        assert report.challenges_triggered_count == 0
        assert report.blocked_requests_count == 0
        assert report.friction_free_percentage == 100.0
        assert len(report.violations) == 0

    def test_page_refresh_zero_verification(self):
        """Kullanıcı sayfayı art arda yenilediğinde (F5 / Refresh) gereksiz CAPTCHA veya doğrulama çıkmamalı."""
        engine = TrafficRiskEngine()
        client_ip = "198.51.100.80"
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        base_time = 1000.0

        # Simulate 5 rapid page refreshes with human variation (300ms to 900ms)
        refresh_intervals = [0.35, 0.45, 0.60, 0.80, 0.50]
        cur_time = base_time

        for interval in refresh_intervals:
            cur_time += interval
            assessment = engine.evaluate_request(
                ip=client_ip,
                path="/cases/active-view",
                method="GET",
                user_agent=ua,
                headers={"accept": "text/html,application/xhtml+xml"},
                now=cur_time,
            )
            # Legitimate refresh must NOT trigger PoW or Block
            assert assessment.requires_pow is False
            assert assessment.is_blocked is False
            assert assessment.delay_ms == 0

    def test_shared_nat_coexistence_no_collateral_damage(self):
        """Aynı üniversite/laboratuvar NAT'ındaki bir bot yüzünden 10 meşru araştırmacı asla engellenmemeli."""
        auditor = ZeroFrictionAuditor()
        report = auditor.audit_shared_nat_coexistence(
            shared_ip="198.51.100.99",
            normal_users_count=10,
            malicious_users_count=1,
        )

        assert report.shared_ip_isolation_intact is True
        assert report.friction_free_percentage == 100.0
        assert report.blocked_requests_count == 0
        assert len(report.violations) == 0

    def test_power_user_forensic_workflow_tolerance(self):
        """Yoğun STR analizi yapan adli uzman (Power-User) makul yüksek trafikte orantısız hız kısıtlamasına uğramamalı."""
        limiter = AdaptiveRateLimiter()
        client_key = "analyst_power_user_key"
        base_time = 1000.0

        # Normal risk power user (risk score 10) performing 40 public search lookups in 1 minute
        allowed_count = 0
        for i in range(40):
            res = limiter.check_rate_limit(
                client_key=client_key,
                path="/api/v1/forensic/alleles",
                method="GET",
                risk_score=10,
                now=base_time + (i * 1.2),
            )
            if res.allowed:
                allowed_count += 1

        # Public read allows 120 req/min for normal risk, so all 40 must be allowed
        assert allowed_count == 40

    def test_active_session_zero_forced_reauthentication(self):
        """Geçerli oturuma sahip analist çalışma esnasında gereksiz yere oturumdan atılmamalı (RTR Güvencesi)."""
        manager = SessionSecurityManager()
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        base_time = 1000.0

        # 1. Login and get initial session and tokens
        sess_id, access_token, refresh_token = manager.create_session(
            user_id="usr_lead_analyst",
            auth_level=SessionAuthLevel.AUTHENTICATED_BASIC,
            user_agent=ua,
            client_ip="198.51.100.50",
        )
        assert access_token.startswith("fat_")
        assert refresh_token.startswith("frt_")

        # 2. Seamlessly rotate refresh token without forcing user to re-authenticate with password
        rot_ok, new_at, new_rt, rot_err = manager.rotate_refresh_token(
            presented_refresh_token=refresh_token,
            user_agent=ua,
            client_ip="198.51.100.50",
            now=base_time + 600.0,
        )
        assert rot_ok is True
        assert new_at is not None
        assert new_rt is not None
        assert new_at != access_token
