"""
FORENZA Monitoring & Noise-Free Alerting Test Suite (Dimension 15).

Validates:
- Real-Time Sliding Window Metrics (RPS, Latency Percentiles, Error %, Cache Hit Rate)
- Noise-Free Credential Stuffing Surge Alerting
- Low-Volume False Alarm Suppression (Anti-Noise Multi-Condition Guard)
- WAF Exploit Scanning Burst Alerting
"""

import pytest

from app.security.security_telemetry import AlertSeverity, SecurityTelemetryEngine


class TestSecurityTelemetry:
    def test_telemetry_rps_latency_error_metrics(self):
        """Kayan pencere (sliding window) metrikleri (RPS, gecikme yüzdelikleri, hata oranı) doğru hesaplanmalı."""
        engine = SecurityTelemetryEngine()
        base_time = 1000.0

        # Simulate 20 requests with various latencies and status codes
        for i in range(20):
            status = 500 if i < 4 else 200  # 4 errors (20%)
            latency = 10.0 + (i * 5.0)       # 10ms to 105ms
            engine.record_http_request(latency_ms=latency, status_code=status, now=base_time + (i * 0.5))

        telemetry = engine.get_realtime_telemetry(now=base_time + 15.0)

        assert telemetry["total_requests_in_window"] == 20
        assert telemetry["requests_per_second"] > 0
        assert telemetry["error_rate_percent"] == 20.0
        assert telemetry["latency_p50_ms"] > 0
        assert telemetry["latency_p95_ms"] > telemetry["latency_p50_ms"]

    def test_noise_free_credential_stuffing_alert(self):
        """Kimlik doğrulama hataları eşiği (>=15/dk) aştığında KRİTİK alarm üretilmeli, 2 münferit hatada sessiz kalınmalı."""
        engine = SecurityTelemetryEngine()
        base_time = 1000.0

        # 1. Normal minor mistake (2 failures) -> No alert fired (zero noise)
        engine.record_auth_failure(now=base_time)
        engine.record_auth_failure(now=base_time + 1.0)
        alerts_minor = engine.evaluate_active_alerts(now=base_time + 2.0)
        assert len(alerts_minor) == 0

        # 2. Credential stuffing attack (16 failures in 30s) -> Alert fired!
        for i in range(16):
            engine.record_auth_failure(now=base_time + 5.0 + (i * 0.5))

        alerts_attack = engine.evaluate_active_alerts(now=base_time + 20.0)
        assert len(alerts_attack) >= 1
        auth_alert = [a for a in alerts_attack if a.alert_type == "CREDENTIAL_STUFFING_OR_BRUTE_FORCE"][0]
        assert auth_alert.severity == AlertSeverity.CRITICAL
        assert "Surge Detected" in auth_alert.title

    def test_noise_free_error_rate_alert_suppression(self):
        """Toplam istek sayısı düşükken (<20) tek bir 404 hatasında yanlış alarm üretilmemeli (Anti-Noise Guard)."""
        engine = SecurityTelemetryEngine()
        base_time = 1000.0

        # Only 2 requests total, 1 is an error (50% error rate, but too few requests)
        engine.record_http_request(latency_ms=20.0, status_code=200, now=base_time)
        engine.record_http_request(latency_ms=25.0, status_code=404, now=base_time + 1.0)

        alerts = engine.evaluate_active_alerts(now=base_time + 2.0)
        # Suppressed because total_requests < 20
        err_alerts = [a for a in alerts if a.alert_type == "ELEVATED_SERVER_ERROR_RATE"]
        assert len(err_alerts) == 0

        # Now simulate 30 requests with 10 errors (33% error rate >= 25% threshold)
        for i in range(30):
            code = 500 if i < 10 else 200
            engine.record_http_request(latency_ms=30.0, status_code=code, now=base_time + 5.0 + (i * 0.2))

        alerts_elevated = engine.evaluate_active_alerts(now=base_time + 15.0)
        err_alerts_active = [a for a in alerts_elevated if a.alert_type == "ELEVATED_SERVER_ERROR_RATE"]
        assert len(err_alerts_active) >= 1
        assert err_alerts_active[0].severity == AlertSeverity.WARNING

    def test_waf_burst_alert_firing(self):
        """WAF kural tetiklenmeleri eşiği (>=10/dk) aştığında KRİTİK exploit tarama alarmı üretilmeli."""
        engine = SecurityTelemetryEngine()
        base_time = 1000.0

        for i in range(12):
            engine.record_waf_event(now=base_time + (i * 0.5))

        alerts = engine.evaluate_active_alerts(now=base_time + 10.0)
        waf_alert = [a for a in alerts if a.alert_type == "WAF_EXPLOIT_SCANNING_BURST"][0]
        assert waf_alert.severity == AlertSeverity.CRITICAL
        assert "WAF Exploit Scanning Burst" in waf_alert.title
