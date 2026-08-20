"""
FORENZA 1.2.5 — Deconvolution MCMCSampler Shim

Canonical roadmap path: backend/node/services/forensic/deconvolution/mcmc_sampler.py
Engine implementation:   backend/node/services/forensic/probabilistic/mcmc.py

This shim re-exports all public symbols from the validated probabilistic engine
(10/10 edge-case tests passing, 2026-08-20) so the roadmap import path resolves
without code duplication.

Research Reference: pillar_1_probabilistic_genotyping_research.md §2.5–2.9
"""

from node.services.forensic.probabilistic.mcmc import (
    # Core sampler
    MCMCSampler,
    # Result types
    MixtureLRResult,
    MCMCConvergenceDiagnostics,
    MCMCSample,
    MCMCChainResult,
    # Calibration
    CalibrationEngine,
    # Utility functions (exposed for testing)
    _gelman_rubin,
    _compute_ess,
    _sample_dirichlet,
    _log_dirichlet_pdf,
    _enfsi_verbal,
    # Constants
    N_BURN_DEFAULT,
    N_SAMPLE_DEFAULT,
    K_THIN,
    N_CHAINS,
    R_HAT_THRESHOLD,
    ESS_THRESHOLD,
)

__all__ = [
    "MCMCSampler",
    "MixtureLRResult",
    "MCMCConvergenceDiagnostics",
    "MCMCSample",
    "MCMCChainResult",
    "CalibrationEngine",
    "_gelman_rubin",
    "_compute_ess",
    "_sample_dirichlet",
    "_log_dirichlet_pdf",
    "_enfsi_verbal",
    "N_BURN_DEFAULT",
    "N_SAMPLE_DEFAULT",
    "K_THIN",
    "N_CHAINS",
    "R_HAT_THRESHOLD",
    "ESS_THRESHOLD",
]
