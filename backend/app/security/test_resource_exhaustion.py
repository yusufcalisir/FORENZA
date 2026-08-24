"""
FORENZA Resource Exhaustion Protection Test Suite (Dimension 11).

Validates:
- Biocomputational Heavy Solver Concurrency Slots (MCMC, ZKP, BPA, GIS)
- Single-User Monopoly Concurrency Rejection (Anti-Monopoly 429)
- Memory Budget Ceiling Enforcement (413 Request Entity Too Large)
- Outbound External Reference API Quota Caps (EMPOP / NCBI / gnomAD)
- Queue Depth Backpressure & Fast Fail-Fast (503 Service Unavailable)
"""

import asyncio
import pytest
from fastapi import HTTPException

from app.security.concurrency_guard import BiocomputationalResourceGuard, ComputeSlotConfig


class TestResourceExhaustionProtection:
    @pytest.mark.asyncio
    async def test_heavy_solver_concurrency_slots(self):
        """Biyohesaplama slotları (MCMC, ZKP) başarıyla alınıp bırakılmalı."""
        guard = BiocomputationalResourceGuard()

        async with guard.acquire_slot("mcmc_mixture", user_id="user_1"):
            telemetry = guard.get_active_telemetry()
            assert telemetry["mcmc_mixture"]["active_jobs"] == 1

        # Released
        telemetry_after = guard.get_active_telemetry()
        assert telemetry_after["mcmc_mixture"]["active_jobs"] == 0

    @pytest.mark.asyncio
    async def test_single_user_concurrency_limit_rejection(self):
        """Tek bir kullanıcının birden fazla MCMC görevini aynı anda çalıştırarak sunucuyu tekeline alması engellenmeli."""
        guard = BiocomputationalResourceGuard()
        user_id = "user_greedy"

        async with guard.acquire_slot("mcmc_mixture", user_id=user_id):
            # Same user attempts to spawn a second simultaneous MCMC task (max_per_user is 1)
            with pytest.raises(HTTPException) as exc_info:
                async with guard.acquire_slot("mcmc_mixture", user_id=user_id):
                    pass
            assert exc_info.value.status_code == 429
            assert "maximum concurrent" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_memory_budget_ceiling_rejection(self):
        """İşlemin talep ettiği bellek bütçesi slot tavanını (ör. MCMC için 50MB) aştığında 413 ile reddedilmeli."""
        guard = BiocomputationalResourceGuard()

        with pytest.raises(HTTPException) as exc_info:
            async with guard.acquire_slot("mcmc_mixture", user_id="user_1", estimated_memory_mb=128):
                pass

        assert exc_info.value.status_code == 413
        assert "exceeds maximum allowed" in exc_info.value.detail.lower()

    def test_external_api_call_quota_hourly_cap(self):
        """Dış adli API (NCBI, EMPOP) çağrıları kullanıcı başına saatlik 50 çağrı ile sınırlandırılmalı."""
        guard = BiocomputationalResourceGuard()
        user_id = "user_api_caller"

        # 50 calls succeed
        for _ in range(50):
            ok, _ = guard.check_external_api_call_quota(user_id, max_calls_per_hour=50)
            assert ok is True

        # 51st call rejected
        ok_51, err_51 = guard.check_external_api_call_quota(user_id, max_calls_per_hour=50)
        assert ok_51 is False
        assert "quota" in err_51.lower()

    @pytest.mark.asyncio
    async def test_queue_depth_backpressure_fail_fast(self):
        """Kuyruk derinliği sınırına ulaştığında OOM çöküşünü önlemek için yeni istekler derhal 503 dönmeli."""
        custom_cfg = {
            "test_slot": ComputeSlotConfig(
                max_concurrent=1,
                timeout_seconds=0.2,
                max_queue_depth=1,
                max_per_user_concurrent=2,
                max_memory_mb=32,
                description="Test Slot",
            )
        }
        guard = BiocomputationalResourceGuard(configs=custom_cfg)

        async def worker(u_id: str):
            async with guard.acquire_slot("test_slot", user_id=u_id):
                await asyncio.sleep(0.1)

        # Fill active job
        task1 = asyncio.create_task(worker("u1"))
        await asyncio.sleep(0.01)

        # Fill queue slot (depth = 1)
        task2 = asyncio.create_task(worker("u2"))
        await asyncio.sleep(0.01)

        # 3rd task exceeds queue depth (max_queue_depth = 1) -> fails fast 503
        with pytest.raises(HTTPException) as exc_info:
            async with guard.acquire_slot("test_slot", user_id="u3"):
                pass

        assert exc_info.value.status_code == 503
        assert "queue depth saturated" in exc_info.value.detail.lower()

        await asyncio.gather(task1, task2, return_exceptions=True)
