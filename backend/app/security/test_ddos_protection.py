"""
FORENZA DDoS Protection Engine Test Suite (Dimension 2).

Validates:
- Volumetric & L7 HTTP Flood Detection
- Concurrent Connection Exhaustion Defense
- Slowloris & Slow HTTP Flagging
- Origin Cloaking & Secret Header Verification
- Active Ban Expiration & Telemetry Metrics
"""

import time
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.security.ddos_shield import DDoSShield
from app.security.security_headers_middleware import UnifiedSecurityMiddleware


class TestDDoSShieldUnit:
    def test_normal_connection_flow(self):
        """Meşru bağlantı kotası aşılmadan sorunsuz açılıp kapanmalı."""
        shield = DDoSShield(max_concurrent=10, max_burst_rps=20)
        ip = "203.0.113.10"

        ok, err = shield.acquire_connection(ip)
        assert ok is True
        assert err is None

        telemetry = shield.get_telemetry()
        assert telemetry["total_active_connections"] == 1

        shield.release_connection(ip)
        telemetry_after = shield.get_telemetry()
        assert telemetry_after["total_active_connections"] == 0

    def test_concurrent_connection_exhaustion_defense(self):
        """Maksimum eşzamanlı bağlantı aşıldığında DDoS savunma banı tetiklenmeli."""
        max_conn = 5
        shield = DDoSShield(max_concurrent=max_conn, max_burst_rps=50)
        attacker_ip = "198.51.100.100"

        # Open max_conn connections
        for _ in range(max_conn):
            ok, err = shield.acquire_connection(attacker_ip)
            assert ok is True

        # Next connection should be blocked and trigger ban
        ok, err = shield.acquire_connection(attacker_ip)
        assert ok is False
        assert "exceeded" in err.lower() or "blocked" in err.lower()
        assert shield.is_ip_banned(attacker_ip) is True

    def test_instantaneous_http_flood_detection(self):
        """1 saniyede aşırı sayıda istek (L7 HTTP Flood) anında banlanmalı."""
        max_burst = 15
        shield = DDoSShield(max_concurrent=50, max_burst_rps=max_burst)
        flood_ip = "198.51.100.200"
        base_time = 1000.0

        for i in range(max_burst):
            ok, err = shield.acquire_connection(flood_ip, now=base_time + (i * 0.02))
            assert ok is True
            shield.release_connection(flood_ip)

        # 16th request within 1s should trigger flood ban
        ok, err = shield.acquire_connection(flood_ip, now=base_time + 0.5)
        assert ok is False
        assert "flood" in err.lower()
        assert shield.is_ip_banned(flood_ip, now=base_time + 0.5) is True

    def test_origin_cloaking_header_verification(self):
        """Doğrudan sunucuya yapılan ve origin secret içermeyen istekler engellenmeli."""
        shield = DDoSShield(origin_secret="top_secret_origin_key_123", enforce_origin_secret=True)

        # Missing secret
        ok, err = shield.verify_origin_headers({})
        assert ok is False
        assert "prohibited" in err.lower()


        # Invalid secret
        ok, err = shield.verify_origin_headers({"x-origin-verify-secret": "wrong_key"})
        assert ok is False

        # Valid secret
        ok, err = shield.verify_origin_headers({"x-origin-verify-secret": "top_secret_origin_key_123"})
        assert ok is True
        assert err is None

    def test_slowloris_slow_drip_flagging(self):
        """Tekrarlayan yavaş okuma (Slowloris) bayrakları biriktiğinde ban uygulanmalı."""
        shield = DDoSShield()
        slow_ip = "198.51.100.250"
        base_time = 1000.0

        shield.record_slow_request_flag(slow_ip, now=base_time)
        shield.record_slow_request_flag(slow_ip, now=base_time + 1.0)
        assert shield.is_ip_banned(slow_ip, now=base_time + 1.0) is False

        # 3rd slow flag triggers ban
        shield.record_slow_request_flag(slow_ip, now=base_time + 2.0)
        assert shield.is_ip_banned(slow_ip, now=base_time + 2.0) is True


class TestDDoSIntegration:
    @pytest.fixture
    def client(self):
        test_app = FastAPI()
        test_app.add_middleware(UnifiedSecurityMiddleware)

        @test_app.get("/api/v1/ping")
        def ping():
            return {"message": "pong"}

        return TestClient(test_app)

    def test_ddos_integration_normal_traffic_passes(self, client):
        """Normal trafik sorunsuz geçmeli."""
        r = client.get("/api/v1/ping")
        assert r.status_code == 200
        assert r.json() == {"message": "pong"}
