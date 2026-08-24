"""
FORENZA Biocomputational Resource & Concurrency Guard (Dimension 11 & 16).

Guards heavy mathematical solvers against CPU/memory starvation:
- MCMC Mixture Deconvolution: max 4 concurrent tasks
- Groth16 ZKP Proof Synthesis: max 2 concurrent tasks
- 3D BPA L2 Origin Solver: max 4 concurrent tasks
- Bayesian GIS Raster Fusion: max 4 concurrent tasks
- 55-AIM BGA Admixture Solver: max 6 concurrent tasks
- Asynchronous semaphore slots with graceful fail-safe timeouts.
"""

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ComputeSlotConfig:
    max_concurrent: int
    timeout_seconds: float
    description: str


class BiocomputationalResourceGuard:
    """
    Asynchronous concurrency coordinator preventing server CPU lockups.
    Ensures background jobs cannot exceed server memory/compute thresholds.
    """

    DEFAULT_SLOTS: Dict[str, ComputeSlotConfig] = {
        "mcmc_mixture": ComputeSlotConfig(max_concurrent=4, timeout_seconds=30.0, description="MCMC Mixture Deconvolution"),
        "zkp_groth16": ComputeSlotConfig(max_concurrent=2, timeout_seconds=20.0, description="Groth16 ZKP Proof Synthesis"),
        "bpa_l2_origin": ComputeSlotConfig(max_concurrent=4, timeout_seconds=15.0, description="3D Bloodstain L2 Origin Optimization"),
        "geoint_gis_fusion": ComputeSlotConfig(max_concurrent=4, timeout_seconds=25.0, description="Bayesian GIS 2D Raster Evidence Fusion"),
        "bga_aim_admixture": ComputeSlotConfig(max_concurrent=6, timeout_seconds=15.0, description="55-AIM Continental Q-Matrix Projection"),
    }

    def __init__(self, configs: Optional[Dict[str, ComputeSlotConfig]] = None):
        self.configs = configs or dict(self.DEFAULT_SLOTS)
        self._semaphores: Dict[str, asyncio.Semaphore] = {}
        self._active_counts: Dict[str, int] = {k: 0 for k in self.configs}

    def _get_semaphore(self, slot_name: str) -> asyncio.Semaphore:
        if slot_name not in self._semaphores:
            cfg = self.configs.get(slot_name, ComputeSlotConfig(max_concurrent=4, timeout_seconds=20.0, description="Generic Compute"))
            self._semaphores[slot_name] = asyncio.Semaphore(cfg.max_concurrent)
        return self._semaphores[slot_name]

    @asynccontextmanager
    async def acquire_slot(self, slot_name: str, timeout_override: Optional[float] = None):
        """
        Asynchronously acquires a computation slot.
        Fails gracefully with 503 if all slots are saturated beyond timeout.
        """
        cfg = self.configs.get(slot_name, ComputeSlotConfig(max_concurrent=4, timeout_seconds=20.0, description="Generic Compute"))
        sem = self._get_semaphore(slot_name)
        timeout = timeout_override if timeout_override is not None else cfg.timeout_seconds

        acquired = False
        try:
            try:
                await asyncio.wait_for(sem.acquire(), timeout=timeout)
                acquired = True
                self._active_counts[slot_name] = self._active_counts.get(slot_name, 0) + 1
            except asyncio.TimeoutError:
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Heavy compute capacity busy for {cfg.description}. Please retry in 5 seconds.",
                    headers={"Retry-After": "5"}
                )
            yield
        finally:
            if acquired:
                sem.release()
                self._active_counts[slot_name] = max(0, self._active_counts.get(slot_name, 1) - 1)

    def get_active_telemetry(self) -> Dict[str, Dict[str, int]]:
        """Returns real-time capacity and active jobs per slot."""
        return {
            slot: {
                "active_jobs": self._active_counts.get(slot, 0),
                "max_capacity": self.configs[slot].max_concurrent,
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
