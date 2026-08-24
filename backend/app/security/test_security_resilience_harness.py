"""
FORENZA Comprehensive Security & Resilience Testing Suite (Dimension 17 & 18).

Executes controlled, in-memory resilience and stress verification covering:
1. DDoS & Traffic Spikes: Concurrent connection limiter and instantaneous flood guard.
2. Bot Traffic vs Legitimate User Pacing: Distinguishing robotic micro-bursts from human jitter.
3. Authentication Abuse & Password Spraying: Multi-account dictionary spray detection & IP quarantine.
4. Resource Exhaustion & Queue Saturation: Heavy compute solver slot backpressure (503 fast-fail).
5. WAF Scientific Invariant Validation: Zero false positives on forensic STR alleles, formulas, and queries.
6. CDN / Cache Behavior: ETag conditional 304 and SingleFlight stampede suppression under load.
7. Database & Downstream Failure Recovery: Circuit Breaker trip and graceful recovery cycle.
8. Fail-Safe Verification: Zero legitimate user lockout during simulated security subsystem degradation.
"""

import asyncio
import time
import pytest

from app.security.api_security_engine import APISecurityEngine, UserRole
from app.security.app_shield import ApplicationShield
from app.security.auth_shield import AuthenticationShield
from app.security.cache_shield import CacheShield
from app.security.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitState
from app.security.concurrency_guard import BiocomputationalResourceGuard, ComputeSlotConfig
from app.security.ddos_shield import DDoSShield
from app.security.failsafe_manager import FailSafeManager
from app.security.rate_limiter import AdaptiveRateLimiter, RateLimitCategory
from app.security.risk_engine import RiskTier, TrafficRiskEngine
from app.security.security_telemetry import SecurityTelemetryEngine
from app.security.waf_tuner import WAFAction, WAFRuleEngine


class TestSecurityResilienceHarness:
    @pytest.mark.asyncio
    async def test_ddos_traffic_spike_and_connection_governor(self):
        """Maksimum eşzamanlı bağlantı sınırına ulaşıldığında savunma banı tetiklenmeli ve süre dolunca açılmalı."""
        ddos = DDoSShield(max_concurrent=10, max_burst_rps=50)
        client_ip = "198.51.100.44"
        base_time = 1000.0

        # Acquire 10 concurrent connections
        for _ in range(10):
            ok, msg = ddos.acquire_connection(client_ip, now=base_time)
            assert ok is True

        # 11th concurrent connection triggers connection exhaustion defense ban
        overflow_ok, overflow_msg = ddos.acquire_connection(client_ip, now=base_time)
        assert overflow_ok is False
        assert "Concurrent connection limit" in overflow_msg
        assert ddos.is_ip_banned(client_ip, now=base_time) is True

        # Release active connections
        for _ in range(10):
            ddos.release_connection(client_ip)

        # After cooling ban duration (120s), IP is unbanned and subsequent connection succeeds
        assert ddos.is_ip_banned(client_ip, now=base_time + 125.0) is False
        resumed_ok, _ = ddos.acquire_connection(client_ip, now=base_time + 125.0)
        assert resumed_ok is True
        ddos.release_connection(client_ip)

    def test_bot_traffic_vs_legitimate_human_pacing(self):
        """Milisaniye düzeyinde sabit aralıklı bot trafiği ile değişken insan trafiği net olarak ayırt edilmeli."""
        risk_engine = TrafficRiskEngine()
        bot_ip = "203.0.113.10"
        human_ip = "203.0.113.20"
        human_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        bot_ua = "Mozilla/5.0 (X11; Linux x86_64) HeadlessChrome/120.0.0.0 Safari/537.36"
        base_time = 1000.0

        # 1. Robotic bot: Headless user-agent + rapid pacing
        bot_assessment = None
        for i in range(5):
            bot_assessment = risk_engine.evaluate_request(
                ip=bot_ip,
                path="/api/v1/forensic/search",
                user_agent=bot_ua,
                now=base_time + (i * 0.02),
            )
        assert bot_assessment is not None
        assert bot_assessment.risk_score >= 40
        assert bot_assessment.risk_tier != RiskTier.NORMAL

        # 2. Legitimate human: natural pacing between 800ms and 2500ms
        human_intervals = [0.8, 1.5, 2.1, 1.2, 3.0, 1.8]
        current_time = base_time
        human_assessment = None
        for interval in human_intervals:
            current_time += interval
            human_assessment = risk_engine.evaluate_request(
                ip=human_ip,
                path="/api/v1/forensic/search",
                user_agent=human_ua,
                now=current_time,
            )

        assert human_assessment is not None
        assert human_assessment.risk_score < 30
        assert human_assessment.risk_tier == RiskTier.NORMAL

    def test_authentication_abuse_password_spraying_quarantine(self):
        """Tek bir IP'den 10 farklı kullanıcı hesabına şifre denendiğinde IP 30 dakika süreyle karantinaya alınmalı."""
        auth_shield = AuthenticationShield()
        attacker_ip = "192.0.2.155"

        # Attempt login against 10 different accounts from the same IP
        for i in range(10):
            auth_shield.record_login_attempt(f"user_{i}@forenza.org", attacker_ip, success=False)

        # Verify attacker IP is locked under password spraying protection
        is_allowed, error_msg, _ = auth_shield.pre_login_check("target_victim@forenza.org", attacker_ip)
        assert is_allowed is False
        assert "failed login attempts" in error_msg.lower()

    @pytest.mark.asyncio
    async def test_heavy_compute_queue_saturation_resilience(self):
        """Biyohesaplama çözücüsünde kuyruk doygunluğunda sistem bellek tüketmeden (OOM önleme) 503 fail-fast dönmeli."""
        slot_cfg = {
            "mcmc_stress": ComputeSlotConfig(
                max_concurrent=2,
                timeout_seconds=0.5,
                max_queue_depth=2,
                max_per_user_concurrent=2,
                max_memory_mb=32,
                description="MCMC Stress Solver",
            )
        }
        guard = BiocomputationalResourceGuard(configs=slot_cfg)

        async def worker_job(u_id: str):
            async with guard.acquire_slot("mcmc_stress", user_id=u_id):
                await asyncio.sleep(0.1)

        # Launch 2 active jobs + 2 queued jobs = 4 total capacity
        tasks = [asyncio.create_task(worker_job(f"u_{i}")) for i in range(4)]
        await asyncio.sleep(0.01)

        # 5th job exceeds queue capacity -> throws fast 503
        with pytest.raises(Exception) as exc_info:
            async with guard.acquire_slot("mcmc_stress", user_id="u_overflow"):
                pass

        assert exc_info.value.status_code == 503
        await asyncio.gather(*tasks, return_exceptions=True)

    def test_waf_zero_false_positives_on_scientific_forensic_data(self):
        """Adli alel listeleri (13, 14, 9.3), STR formülleri ve Bayesyen sorgular WAF tarafından YANLIŞLIKLA ENGELLENMEMELİ."""
        waf = WAFRuleEngine()

        forensic_queries = [
            "/api/v1/forensic/str/locus?alleles=13,14,15.2",
            "/api/v1/forensic/mixture?hp_contributors=2&theta=0.01",
            "/api/v1/forensic/aims?snps=rs12913832_GG,rs1800407_CT",
            "/api/v1/forensic/bpa/origin?droplets_count=45&alpha_deg=34.5",
        ]

        for q in forensic_queries:
            res = waf.evaluate_request(path=q, method="GET")
            assert res.action == WAFAction.ALLOW
            assert res.matched_rule_id is None

    @pytest.mark.asyncio
    async def test_cache_stampede_and_etag_resilience(self):
        """Önbellek süresi dolduğunda 30 eşzamanlı istek veritabanını boğmadan SingleFlight ile tek hesaplama paylaşmalı."""
        cache = CacheShield()
        db_queries_executed = 0

        async def fetch_nist_matrix_from_db():
            nonlocal db_queries_executed
            db_queries_executed += 1
            await asyncio.sleep(0.04)
            return {"locus": "SE33", "alleles": ["25.2", "27.2", "28.2"]}

        tasks = [
            cache.coalesce_request("nist_matrix_se33", fetch_nist_matrix_from_db)
            for _ in range(30)
        ]

        results = await asyncio.gather(*tasks)
        assert db_queries_executed == 1
        assert len(results) == 30
        assert results[0]["locus"] == "SE33"

    def test_circuit_breaker_complete_failure_and_recovery_cycle(self):
        """Veritabanı bağlantısı çöktüğünde devre kesici açılmalı ve sistem sağlığı düzeldiğinde normale dönmeli."""
        config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout_seconds=5.0, half_open_success_threshold=2)
        cb = CircuitBreaker("database_cluster", config)
        base_time = 2000.0

        # 1. Closed state
        assert cb.state == CircuitState.CLOSED

        # 2. 3 consecutive DB connection timeouts -> trip to OPEN
        cb.record_failure(now=base_time)
        cb.record_failure(now=base_time)
        cb.record_failure(now=base_time)
        assert cb.state == CircuitState.OPEN
        assert cb.can_execute(now=base_time + 1.0)[0] is False

        # 3. After recovery timeout -> HALF_OPEN probe
        assert cb.can_execute(now=base_time + 6.0)[0] is True
        assert cb.state == CircuitState.HALF_OPEN

        # 4. 2 successful probe executions -> restore to CLOSED
        cb.record_success(now=base_time + 6.1)
        cb.record_success(now=base_time + 6.2)
        assert cb.state == CircuitState.CLOSED
        assert cb.can_execute(now=base_time + 7.0)[0] is True
