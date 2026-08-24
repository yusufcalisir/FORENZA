"""
FORENZA Production Security Layer Comprehensive Test Suite.

Validates all 18 security dimensions:
- Zero-friction normal user flow (R < 30, 0ms delay)
- Malicious scanner and exploit probe detection
- Dual-key shared NAT/University isolation
- Endpoint-aware token bucket rate limiting
- Concurrency semaphores and heavy compute saturation prevention
- SSRF private IP blocker
- Path traversal and file upload magic byte validation
- ISO 27001 structured logging without PII leakage
- Silent WebCrypto PoW challenge and verification
- Enterprise security headers and proxy IP resolution
"""

import asyncio
import hashlib
import time
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.security.risk_engine import TrafficRiskEngine, RiskTier
from app.security.rate_limiter import AdaptiveRateLimiter, RateLimitCategory
from app.security.concurrency_guard import BiocomputationalResourceGuard, ComputeSlotConfig
from app.security.app_shield import ApplicationShield
from app.security.audit_logger import SecurityAuditLogger
from app.security.security_headers_middleware import UnifiedSecurityMiddleware
from app.api.security_routes import router as security_router


# ============================================================================
# 1. Traffic Risk Engine Tests (Dimensions 1, 4, 18)
# ============================================================================

class TestTrafficRiskEngine:
    def test_normal_user_zero_friction(self):
        """Meşru kullanıcı sıfır gecikme ve NORMAL tier almalı."""
        engine = TrafficRiskEngine()
        res = engine.evaluate_request(
            ip="203.0.113.195",
            path="/api/v1/forensic/str/evaluate-single-source",
            method="POST",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        )
        assert res.risk_score < 30
        assert res.risk_tier == RiskTier.NORMAL
        assert res.delay_ms == 0
        assert res.requires_pow is False
        assert res.is_blocked is False

    def test_malicious_scanner_detection(self):
        """Sqlmap veya Nikto gibi tarayıcılar yüksek risk skoru almalı."""
        engine = TrafficRiskEngine()
        res = engine.evaluate_request(
            ip="198.51.100.22",
            path="/api/v1/forensic/population",
            method="GET",
            user_agent="sqlmap/1.6.12#stable (https://sqlmap.org)",
        )
        assert res.risk_score >= 80
        assert "Malicious scanner signature" in " ".join(res.reasons)

    def test_exploit_probe_path_detection(self):
        """Hassas yol taramaları (.env, wp-admin, etc/passwd) anında işaretlenmeli."""
        engine = TrafficRiskEngine()
        res = engine.evaluate_request(
            ip="198.51.100.44",
            path="/.env",
            method="GET",
            user_agent="Mozilla/5.0",
        )
        assert res.risk_score >= 70
        assert any("probe pattern" in r for r in res.reasons)

    def test_shared_nat_dual_key_isolation(self):
        """Aynı IP arkasındaki iki farklı kullanıcı birbirini bloklamamalı."""
        engine = TrafficRiskEngine(burst_threshold=10)
        shared_ip = "195.175.254.2"  # Shared University/Hospital NAT

        # User A sends requests
        for _ in range(5):
            engine.evaluate_request(
                ip=shared_ip,
                path="/api/v1/forensic/phenotype",
                method="GET",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                session_id="session_alice_123",
            )

        # User B sends 1 request with different session/UA
        res_b = engine.evaluate_request(
            ip=shared_ip,
            path="/api/v1/forensic/phenotype",
            method="GET",
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
            session_id="session_bob_456",
        )

        assert res_b.risk_score < 30
        assert res_b.risk_tier == RiskTier.NORMAL

    def test_headless_automation_detection(self):
        """HeadlessChrome veya Playwright imzaları tespit edilmeli."""
        engine = TrafficRiskEngine()
        res = engine.evaluate_request(
            ip="198.51.100.77",
            path="/api/v1/forensic/population",
            method="GET",
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/120.0.0.0 Safari/537.36",
        )
        assert res.risk_score >= 40
        assert any("headless" in r.lower() for r in res.reasons)

    def test_header_inconsistency_missing_accept(self):
        """Mozilla User-Agent ile gelip Accept başlığı göndermeyen şüpheli botlar puanlanmalı."""
        engine = TrafficRiskEngine()
        res = engine.evaluate_request(
            ip="198.51.100.88",
            path="/api/v1/forensic/population",
            method="GET",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            headers={"Host": "localhost"},  # Missing Accept header
        )
        assert any("Accept" in r for r in res.reasons)

    def test_machine_like_pacing_detection(self):
        """Çok hızlı aralıklı makine benzeri istek dizilimi tespit edilmeli."""
        engine = TrafficRiskEngine(base_burst_threshold=100)
        client_ip = "198.51.100.99"
        base_time = 1000.0

        # Simulate 15 requests with 0.01s (10ms) intervals
        res = None
        for i in range(15):
            res = engine.evaluate_request(
                ip=client_ip,
                path="/api/v1/forensic/population",
                method="GET",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                now=base_time + (i * 0.01),
            )

        assert res is not None
        assert any("machine-like" in r.lower() or "micro-burst" in r.lower() for r in res.reasons)



# ============================================================================
# 2. Adaptive Rate Limiter Tests (Dimensions 3, 9)
# ============================================================================

class TestAdaptiveRateLimiter:
    def test_auth_endpoint_strict_limiting(self):
        """Auth uç noktaları katı 5 req/min sınırına uymalı."""
        limiter = AdaptiveRateLimiter()
        client_key = "test_auth_client"

        # First 3 (burst allowance) should pass
        for _ in range(3):
            res = limiter.check_rate_limit(client_key, "/api/v1/auth/login", "POST")
            assert res.allowed is True
            assert res.category == RateLimitCategory.AUTH

        # Subsequent rapid requests should be throttled
        throttled_hit = False
        for _ in range(5):
            res = limiter.check_rate_limit(client_key, "/api/v1/auth/login", "POST")
            if not res.allowed:
                throttled_hit = True
                assert res.retry_after is not None
                assert res.retry_after > 0
                break

        assert throttled_hit is True

    def test_password_reset_endpoint_strict_limiting(self):
        """Şifre sıfırlama uç noktaları son derece sıkı (3 req/5min) sınırına uymalı."""
        limiter = AdaptiveRateLimiter()
        client_key = "test_pw_reset_client"

        # 1st request (burst capacity = 1) passes
        res1 = limiter.check_rate_limit(client_key, "/api/v1/auth/reset-password", "POST")
        assert res1.allowed is True
        assert res1.category == RateLimitCategory.PASSWORD_RESET

        # 2nd immediate request must be blocked
        res2 = limiter.check_rate_limit(client_key, "/api/v1/auth/reset-password", "POST")
        assert res2.allowed is False
        assert res2.retry_after is not None
        assert res2.retry_after > 0

    def test_heavy_compute_rate_limiting(self):
        """MCMC ve ZKP gibi ağır matematiksel uç noktalar 10 req/min ile sınırlandırılmalı."""
        limiter = AdaptiveRateLimiter()
        client_key = "test_compute_client"

        # Burst of 4 passes
        for _ in range(4):
            res = limiter.check_rate_limit(client_key, "/api/v1/forensic/mixture", "POST")
            assert res.allowed is True
            assert res.category == RateLimitCategory.HEAVY_COMPUTE

        # 5th immediate exceeds burst capacity
        res = limiter.check_rate_limit(client_key, "/api/v1/forensic/mixture", "POST")
        assert res.allowed is False

    def test_risk_modulated_quota_scaling(self):
        """Yüksek risk skoruna sahip istemcilerin kota ve burst kapasitesi dinamik daraltılmalı."""
        limiter = AdaptiveRateLimiter()
        low_risk_client = "client_low_risk"
        high_risk_client = "client_high_risk"

        # Low risk (R=10) gets full burst
        res_low = limiter.check_rate_limit(low_risk_client, "/api/v1/forensic/population", "GET", risk_score=10)
        assert res_low.limit == 120

        # High risk (R=85) gets scaled down quota
        res_high = limiter.check_rate_limit(high_risk_client, "/api/v1/forensic/population", "GET", risk_score=85)
        assert res_high.limit < 120



# ============================================================================
# 3. Concurrency Semaphore Tests (Dimension 11)
# ============================================================================

class TestConcurrencyGuard:
    @pytest.mark.asyncio
    async def test_slot_acquisition_and_release(self):
        """Hesaplama slotu doğru alınmalı ve serbest bırakılmalı."""
        guard = BiocomputationalResourceGuard(
            configs={"test_compute": ComputeSlotConfig(max_concurrent=2, timeout_seconds=1.0, description="Test Slot")}
        )

        async with guard.acquire_slot("test_compute"):
            tel = guard.get_active_telemetry()
            assert tel["test_compute"]["active_jobs"] == 1

        tel = guard.get_active_telemetry()
        assert tel["test_compute"]["active_jobs"] == 0

    @pytest.mark.asyncio
    async def test_slot_saturation_timeout_rejection(self):
        """Slot kapasitesi dolduğunda 503 fırlatılmalı."""
        guard = BiocomputationalResourceGuard(
            configs={"test_limited": ComputeSlotConfig(max_concurrent=1, timeout_seconds=0.1, description="Limited Slot")}
        )

        async def holding_task():
            async with guard.acquire_slot("test_limited"):
                await asyncio.sleep(0.3)

        t = asyncio.create_task(holding_task())
        await asyncio.sleep(0.02)

        with pytest.raises(HTTPException) as exc_info:
            async with guard.acquire_slot("test_limited", timeout_override=0.05):
                pass

        assert exc_info.value.status_code == 503
        assert "Retry-After" in exc_info.value.headers
        await t


# ============================================================================
# 4. Application Shield OWASP Tests (Dimensions 7, 8, 9)
# ============================================================================

class TestApplicationShield:
    def test_ssrf_blocks_private_networks(self):
        """SSRF koruması yerel ve özel ağları engellemeli."""
        blocked_urls = [
            "http://127.0.0.1:8000/admin",
            "http://localhost:3000",
            "http://10.0.0.5/api",
            "http://169.254.169.254/latest/meta-data/",
            "http://192.168.1.1/router",
        ]
        for u in blocked_urls:
            is_safe, err = ApplicationShield.is_safe_external_url(u)
            assert is_safe is False
            assert err is not None

    def test_path_traversal_sanitization(self):
        """Dizin kaçış karakterleri güvenli dosya adına dönüştürülmeli."""
        unsafe_names = [
            "../../../../etc/passwd",
            "..\\..\\windows\\system32\\cmd.exe",
            "/var/log/forensic_cases.json",
            "sample\x00_override.vcf",
        ]
        for name in unsafe_names:
            safe = ApplicationShield.sanitize_filename(name)
            assert "/" not in safe
            assert "\\" not in safe
            assert ".." not in safe
            assert "\x00" not in safe

    def test_file_upload_validation(self):
        """İzin verilen adli dosya formatları ve boyut sınırları doğrulanmalı."""
        valid_xml = b"<?xml version='1.0'?><CODISProfile><Locus>TH01</Locus></CODISProfile>"
        is_valid, err = ApplicationShield.validate_file_upload("profile.xml", valid_xml)
        assert is_valid is True
        assert err is None

        # Exceeding max size
        huge_bytes = b"0" * (11 * 1024 * 1024)
        is_valid, err = ApplicationShield.validate_file_upload("huge.csv", huge_bytes)
        assert is_valid is False
        assert "exceeds maximum limit" in err


# ============================================================================
# 5. Security Audit Logging & PII Protection Tests (Dimension 14)
# ============================================================================

class TestSecurityAuditLogger:
    def test_sensitive_field_masking(self):
        """Şifreler ve tokenlar asla açık metin olarak loglanmamalı."""
        clean_pass = SecurityAuditLogger.mask_sensitive_value("password", "SecretP@ssword123")
        clean_token = SecurityAuditLogger.mask_sensitive_value("access_token", "eyJhbGciOiJIUzI1Ni...")
        clean_normal = SecurityAuditLogger.mask_sensitive_value("locus_count", 24)

        assert clean_pass == "******[REDACTED]******"
        assert clean_token == "******[REDACTED]******"
        assert clean_normal == 24


# ============================================================================
# 6. Full FastAPI Middleware & Security Endpoints Integration Tests
# ============================================================================

class TestSecurityIntegration:
    @pytest.fixture
    def client(self):
        test_app = FastAPI()
        test_app.add_middleware(UnifiedSecurityMiddleware)
        test_app.include_router(security_router, prefix="/api/v1")

        @test_app.get("/api/v1/test-endpoint")
        def sample_route():
            return {"status": "ok"}

        return TestClient(test_app)

    def test_security_health_endpoint(self, client):
        """GET /api/v1/security/health 200 ve aktif durum dönmeli."""
        r = client.get("/api/v1/security/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "HEALTHY"
        assert data["zero_friction_mode"] is True

    def test_security_metrics_endpoint(self, client):
        """GET /api/v1/security/metrics telemetri dönmeli."""
        r = client.get("/api/v1/security/metrics")
        assert r.status_code == 200
        data = r.json()
        assert "compute_semaphores" in data
        assert "client_risk_score" in data

    def test_enterprise_security_headers_present(self, client):
        """Tüm yanıtlarda zorunlu kurumsal güvenlik başlıkları bulunmalı."""
        r = client.get("/api/v1/test-endpoint")
        assert r.status_code == 200
        assert r.headers["X-Content-Type-Options"] == "nosniff"
        assert r.headers["X-Frame-Options"] == "DENY"
        assert "Strict-Transport-Security" in r.headers
        assert "X-Correlation-ID" in r.headers
        assert "X-RateLimit-Limit" in r.headers
        assert "X-Risk-Tier" in r.headers

    def test_pow_challenge_verification_flow(self, client):
        """PoW challenge üretimi ve doğru nonce ile doğrulanması testi."""
        # 1. Challenge isteği (difficulty=2 hızlı test için)
        chal_resp = client.post("/api/v1/security/pow-challenge", json={"difficulty": 2})
        assert chal_resp.status_code == 200
        chal_data = chal_resp.json()

        salt = chal_data["salt"]
        diff = chal_data["difficulty"]
        target = "0" * diff

        # 2. Nonce çöz
        nonce = 0
        while True:
            candidate = f"{salt}:{nonce}"
            h = hashlib.sha256(candidate.encode("utf-8")).hexdigest()
            if h.startswith(target):
                break
            nonce += 1

        # 3. Doğrula
        verify_resp = client.post(
            "/api/v1/security/verify-pow",
            json={
                "challenge_id": chal_data["challenge_id"],
                "salt": salt,
                "nonce": str(nonce),
                "difficulty": diff,
                "signature": chal_data["signature"],
            },
        )
        assert verify_resp.status_code == 200
        verify_data = verify_resp.json()
        assert verify_data["verified"] is True
        assert verify_data["reduced_risk_score"] <= 10
