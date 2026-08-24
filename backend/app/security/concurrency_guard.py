"""
FORENZA Biocomputational Resource & Concurrency Guard (Dimension 11 & 18).

Guards heavy mathematical solvers against CPU/memory starvation & resource exhaustion:
- MCMC Mixture Deconvolution: max 4 concurrent tasks, max 1 per user, 30s timeout, max queue depth 10.
- Groth16 ZKP Proof Synthesis: max 2 concurrent tasks, max 1 per user, 20s timeout, max queue depth 5.
- 3D BPA L2 Origin Solver: max 4 concurrent tasks, max 2 per user, 15s timeout, max queue depth 10.
- Bayesian GIS Raster Fusion: max 4 concurrent tasks, max 1 per user, 25s timeout, max queue depth 10.
- 55-AIM BGA Admixture Solver: max 6 concurrent tasks, max 2 per user, 15s timeout, max queue depth 15.
- External Reference API Integration (EMPOP/NCBI): max 8 concurrent, 5s timeout, 50 calls/hr/user.
- Queue Backpressure: Fast 503 fail-fast when queue depth exceeds threshold (prevents OOM).
- Memory Budget Enforcement: 50MB peak buffer ceiling per solver.
"""

import asyncio
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Deque, Dict, Optional, Set, Tuple


@dataclass
class ComputeSlotConfig:
    max_concurrent: int = 4
    timeout_seconds: float = 20.0
    max_queue_depth: int = 10
    max_per_user_concurrent: int = 2
    max_memory_mb: int = 48
    description: str = "Generic Compute Task"



class BiocomputationalResourceGuard:
    """
    Asynchronous resource coordinator preventing server CPU/memory lockups and queue exhaustion.
    """

    DEFAULT_SLOTS: Dict[str, ComputeSlotConfig] = {
        "mcmc_mixture": ComputeSlotConfig(
            max_concurrent=4,
            timeout_seconds=30.0,
            max_queue_depth=10,
            max_per_user_concurrent=1,
            max_memory_mb=50,
            description="MCMC Mixture Deconvolution (EuroForMix/STRmix)",
        ),
        "zkp_groth16": ComputeSlotConfig(
            max_concurrent=2,
            timeout_seconds=20.0,
            max_queue_depth=5,
            max_per_user_concurrent=1,
            max_memory_mb=64,
            description="Groth16 ZKP Proof Synthesis (BN254 Pairings)",
        ),
        "bpa_l2_origin": ComputeSlotConfig(
            max_concurrent=4,
            timeout_seconds=15.0,
            max_queue_depth=10,
            max_per_user_concurrent=2,
            max_memory_mb=32,
            description="3D Bloodstain L2 Origin Optimization",
        ),
        "geoint_gis_fusion": ComputeSlotConfig(
            max_concurrent=4,
            timeout_seconds=25.0,
            max_queue_depth=10,
            max_per_user_concurrent=1,
            max_memory_mb=48,
            description="Bayesian GIS 2D Raster Evidence Fusion",
        ),
        "bga_aim_admixture": ComputeSlotConfig(
            max_concurrent=6,
            timeout_seconds=15.0,
            max_queue_depth=15,
            max_per_user_concurrent=2,
            max_memory_mb=32,
            description="55-AIM Continental Q-Matrix Projection",
        ),
        "external_api_lookup": ComputeSlotConfig(
            max_concurrent=8,
            timeout_seconds=5.0,
            max_queue_depth=20,
            max_per_user_concurrent=4,
            max_memory_mb=16,
            description="External Reference Lookup (EMPOP/NCBI/gnomAD)",
        ),
    }

    def __init__(self, configs: Optional[Dict[str, ComputeSlotConfig]] = None):
        self.configs = configs or dict(self.DEFAULT_SLOTS)
        self._semaphores: Dict[str, asyncio.Semaphore] = {}
        self._active_counts: Dict[str, int] = {k: 0 for k in self.configs}
        self._queue_depths: Dict[str, int] = {k: 0 for k in self.configs}
        self._user_active_jobs: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int)) # user_id -> slot -> count
        self._user_external_api_calls: Dict[str, Deque[float]] = defaultdict(deque) # user_id -> timestamps

    def _get_semaphore(self, slot_name: str) -> asyncio.Semaphore:
        if slot_name not in self._semaphores:
            cfg = self.configs.get(
                slot_name,
                ComputeSlotConfig(
                    max_concurrent=4,
                    timeout_seconds=20.0,
                    max_queue_depth=10,
                    max_per_user_concurrent=1,
                    max_memory_mb=32,
                    description="Generic Compute",
                ),
            )
            self._semaphores[slot_name] = asyncio.Semaphore(cfg.max_concurrent)
        return self._semaphores[slot_name]

    @asynccontextmanager
    async def acquire_slot(
        self,
        slot_name: str,
        user_id: str = "anonymous_user",
        timeout_override: Optional[float] = None,
        estimated_memory_mb: Optional[int] = None,
    ):
        """
        Asynchronously acquires a computation slot with queue backpressure and user concurrency limits.
        Fails fast with HTTP 503 if queue is saturated or user exceeds single-user concurrency ceiling.
        """
        from fastapi import HTTPException, status

        cfg = self.configs.get(
            slot_name,
            ComputeSlotConfig(
                max_concurrent=4,
                timeout_seconds=20.0,
                max_queue_depth=10,
                max_per_user_concurrent=1,
                max_memory_mb=32,
                description="Generic Compute",
            ),
        )

        # 1. Memory Budget Guard
        if estimated_memory_mb and estimated_memory_mb > cfg.max_memory_mb:
            raise HTTPException(
                status_code=getattr(status, "HTTP_413_CONTENT_TOO_LARGE", 413),
                detail=f"Requested memory budget ({estimated_memory_mb} MB) exceeds maximum allowed ({cfg.max_memory_mb} MB) for {cfg.description}."
            )


        # 2. Per-User Single Concurrency Ceiling (Anti-Monopoly)
        user_active = self._user_active_jobs[user_id][slot_name]
        if user_active >= cfg.max_per_user_concurrent:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"You have reached the maximum concurrent {cfg.description} tasks ({cfg.max_per_user_concurrent}). Please wait for active task to finish.",
                headers={"Retry-After": "5"}
            )

        # 3. Queue Depth Backpressure (Anti-OOM)
        if self._queue_depths[slot_name] >= cfg.max_queue_depth:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Task queue depth saturated ({cfg.max_queue_depth}) for {cfg.description}. Fast failing to protect system stability.",
                headers={"Retry-After": "10"}
            )

        sem = self._get_semaphore(slot_name)
        timeout = timeout_override if timeout_override is not None else cfg.timeout_seconds

        self._queue_depths[slot_name] += 1
        acquired = False
        try:
            try:
                await asyncio.wait_for(sem.acquire(), timeout=timeout)
                acquired = True
                self._queue_depths[slot_name] = max(0, self._queue_depths[slot_name] - 1)
                self._active_counts[slot_name] += 1
                self._user_active_jobs[user_id][slot_name] += 1
            except asyncio.TimeoutError:
                self._queue_depths[slot_name] = max(0, self._queue_depths[slot_name] - 1)
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Heavy compute capacity busy for {cfg.description}. Please retry in {int(timeout)} seconds.",
                    headers={"Retry-After": str(int(timeout))}
                )
            yield
        finally:
            if acquired:
                sem.release()
                self._active_counts[slot_name] = max(0, self._active_counts.get(slot_name, 1) - 1)
                self._user_active_jobs[user_id][slot_name] = max(0, self._user_active_jobs[user_id][slot_name] - 1)

    def check_external_api_call_quota(self, user_id: str, max_calls_per_hour: int = 50) -> Tuple[bool, Optional[str]]:
        """
        Guards outbound external API calls (EMPOP, NCBI, gnomAD) against automated exhaustion.
        """
        now = time.time()
        calls = self._user_external_api_calls[user_id]
        cutoff = now - 3600.0

        while calls and calls[0] < cutoff:
            calls.popleft()

        if len(calls) >= max_calls_per_hour:
            return False, f"Hourly external API reference lookup quota ({max_calls_per_hour}) reached for user."

        calls.append(now)
        return True, None

    def get_active_telemetry(self) -> Dict[str, Dict[str, int]]:
        """Returns real-time capacity, active jobs, and queue depth per slot."""
        return {
            slot: {
                "active_jobs": self._active_counts.get(slot, 0),
                "queue_depth": self._queue_depths.get(slot, 0),
                "max_capacity": self.configs[slot].max_concurrent,
                "max_queue_depth": self.configs[slot].max_queue_depth,
            }
            for slot in self.configs
        }


# Global singleton instance
_guard_instance: Optional[BiocomputationalResourceGuard] = None


def get_resource_guard() -> BiocomputationalResourceGuard:
    global _guard_instance
    if _guard_instance is None:
        _guard_instance = BiocomputationalResourceGuard()
    return _guard_instance
