"""
FORENZA Deconvolution Service Package (1.2.5 — Backend Implementation)

Re-exports the MCMCSampler and related types from the probabilistic engine
so the canonical roadmap import path resolves correctly:
  from node.services.forensic.deconvolution.mcmc_sampler import MCMCSampler
"""

from .mcmc_sampler import (
    MCMCSampler,
    MixtureLRResult,
    MCMCConvergenceDiagnostics,
    MCMCSample,
    MCMCChainResult,
    CalibrationEngine,
)

__all__ = [
    "MCMCSampler",
    "MixtureLRResult",
    "MCMCConvergenceDiagnostics",
    "MCMCSample",
    "MCMCChainResult",
    "CalibrationEngine",
]
