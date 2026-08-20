"""
FORENZA 1.2.5 — MCMC Mixture Deconvolution API Schemas (Pydantic v2)

Pydantic v2 request / response models for the MCMC mixture deconvolution
REST endpoint (POST /api/v1/forensic/mixture).

Research Reference:
  pillar_1_probabilistic_genotyping_research.md §2.1–2.9
  pillar_6_lims_zkp_reporting_research.md (ISO 17025 GUM Expanded Uncertainty §U95)

Pydantic v2 Rule (AGENTS.md):
  ConfigDict(protected_namespaces=()) required on all models with model_* fields.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ─────────────────────────────────────────────────────────────────────────────
# Sub-models
# ─────────────────────────────────────────────────────────────────────────────

class ConvergenceDiagnosticsOut(BaseModel):
    """
    Gelman-Rubin R̂ and ESS convergence summary.
    Derived verbatim from: pillar_1_probabilistic_genotyping_research.md §2.7–2.8
      R̂ = sqrt([(M-1)/M·W + 1/M·B] / W)  → converged when < 1.05
      ESS = N / (1 + 2·Σ_k ρ_k)           → reliable when > 1000
    """
    model_config = ConfigDict(protected_namespaces=())

    r_hat_per_param:     Dict[str, float] = Field(
        description="Per-parameter Gelman-Rubin R̂ values"
    )
    r_hat_max:           float = Field(
        description="Maximum R̂ across all parameters (SWGDAM 2020 threshold ≤ 1.10)"
    )
    ess_per_param:       Dict[str, float] = Field(
        description="Per-parameter Effective Sample Size"
    )
    ess_min:             float = Field(
        description="Minimum ESS across all parameters (threshold > 1000)"
    )
    converged:           bool  = Field(
        description="True if r_hat_max < 1.05 AND ess_min > 1000"
    )
    n_samples_per_chain: int   = Field(
        description="Number of retained samples per chain (post burn-in, post thinning)"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Request Schema
# ─────────────────────────────────────────────────────────────────────────────

class MCMCMixtureRequest(BaseModel):
    """
    POST /api/v1/forensic/mixture — MCMC Mixture Deconvolution Request.

    EPG data format: {locus_name: {allele_str: rfu_height}}
    Allele keys may be integer strings ("14") or float strings ("14.0", "9.3").

    Research Reference: pillar_1_probabilistic_genotyping_research.md §2.4–2.6
    """
    model_config = ConfigDict(protected_namespaces=())

    epg_data: Dict[str, Dict[str, float]] = Field(
        ...,
        description=(
            "Electropherogram peak heights: {locus → {allele_string → RFU}}. "
            "Allele strings must be parseable as float (e.g. '14', '14.0', '9.3'). "
            "Minimum 1 locus required."
        ),
        examples=[{
            "D3S1358": {"14.0": 800.0, "15.0": 750.0, "16.0": 520.0, "17.0": 490.0},
            "VWA":     {"17.0": 1200.0, "18.0": 1100.0},
        }],
    )

    K: int = Field(
        default=2,
        ge=2,
        le=4,
        description="Number of contributors (2 ≤ K ≤ 4). K=2 for standard 2-person mixtures.",
    )

    model: Literal["STRmix", "EuroForMix"] = Field(
        default="STRmix",
        description=(
            "Likelihood model: 'STRmix' (Log-Normal, σ=0.35) or "
            "'EuroForMix' (Gamma, ω=0.35 CV). "
            "Research: pillar_1_probabilistic_genotyping_research.md §2.2–2.3"
        ),
    )

    n_burn: int = Field(
        default=2_000,
        ge=500,
        le=50_000,
        description=(
            "Burn-in iterations (discarded). Production: 10,000. "
            "Fast-mode default: 2,000 for HTTP response latency."
        ),
    )

    n_sample: int = Field(
        default=6_000,
        ge=1_000,
        le=100_000,
        description=(
            "Post-burn-in sampling iterations. Production: 50,000. "
            "Fast-mode default: 6,000."
        ),
    )

    n_chains: int = Field(
        default=3,
        ge=2,
        le=6,
        description="Number of independent parallel MCMC chains. Minimum 2 for R̂ computation.",
    )

    k_thin: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Thinning interval — retain every k_thin-th sample to reduce autocorrelation.",
    )

    sigma: float = Field(
        default=0.35,
        ge=0.10,
        le=1.0,
        description="STRmix log-normal dispersion parameter σ (used when model='STRmix').",
    )

    omega: float = Field(
        default=0.35,
        ge=0.10,
        le=1.0,
        description="EuroForMix Gamma coefficient of variation ω (used when model='EuroForMix').",
    )

    suspect_genotype: Optional[Dict[str, List[float]]] = Field(
        default=None,
        description=(
            "Per-locus suspect genotype for H_p computation: {locus → [allele1, allele2]}. "
            "If None, returns Random Match Probability (H_d denominator only). "
            "Each locus must have exactly 2 allele values."
        ),
        examples=[{"D3S1358": [14.0, 15.0], "VWA": [17.0, 18.0]}],
    )

    seed: Optional[int] = Field(
        default=None,
        description="Random seed for MCMC reproducibility (None = non-deterministic).",
    )

    # ── Validators ──────────────────────────────────────────────────────────

    @field_validator("epg_data")
    @classmethod
    def validate_epg_allele_keys(
        cls, v: Dict[str, Dict[str, float]]
    ) -> Dict[str, Dict[str, float]]:
        """Verify all allele string keys are parseable as float."""
        if not v:
            raise ValueError("epg_data must contain at least 1 locus")
        for locus, allele_dict in v.items():
            if not allele_dict:
                raise ValueError(f"Locus '{locus}' has no allele entries")
            for allele_key in allele_dict:
                try:
                    float(allele_key)
                except (ValueError, TypeError):
                    raise ValueError(
                        f"Allele key '{allele_key}' at locus '{locus}' is not "
                        f"parseable as a float. Valid examples: '14', '14.0', '9.3'"
                    )
        return v

    @field_validator("suspect_genotype")
    @classmethod
    def validate_suspect_genotype(
        cls, v: Optional[Dict[str, List[float]]]
    ) -> Optional[Dict[str, List[float]]]:
        """Each locus in suspect_genotype must have exactly 2 allele values."""
        if v is None:
            return v
        for locus, alleles in v.items():
            if len(alleles) != 2:
                raise ValueError(
                    f"suspect_genotype['{locus}'] must have exactly 2 allele values, "
                    f"got {len(alleles)}: {alleles}"
                )
            for a in alleles:
                if not (isinstance(a, (int, float)) and a > 0):
                    raise ValueError(
                        f"suspect_genotype['{locus}'] allele value {a!r} must be "
                        f"a positive number"
                    )
        return v

    @model_validator(mode="after")
    def validate_run_size(self) -> "MCMCMixtureRequest":
        """
        Guard against excessively long synchronous runs.
        n_burn + n_sample > 60,000 requires the async job endpoint (future 1.2.6+).
        """
        total = self.n_burn + self.n_sample
        if total > 60_000:
            raise ValueError(
                f"n_burn ({self.n_burn}) + n_sample ({self.n_sample}) = {total} "
                f"exceeds the synchronous HTTP limit of 60,000 iterations. "
                f"Use the async batch endpoint for full production runs."
            )
        return self


# ─────────────────────────────────────────────────────────────────────────────
# Response Schema
# ─────────────────────────────────────────────────────────────────────────────

class MCMCMixtureResponse(BaseModel):
    """
    POST /api/v1/forensic/mixture — MCMC Mixture Deconvolution Response.

    ISO 17025 GUM Expanded Uncertainty (pillar_6 §U95):
      U₉₅ = log10_lr_hpd95_hi − log10_lr_point  (conservative HPD bound)

    ENFSI 2017 7-Tier Verbal Scale:
      verbal_scale_en (EN) and verbal_scale_tr (TR) are mandatory per AGENTS.md §Legal.
    """
    model_config = ConfigDict(protected_namespaces=())

    log10_lr_point:     float = Field(
        description="Posterior mean log₁₀(LR) point estimate"
    )
    log10_lr_hpd95_lo:  float = Field(
        description="95% HPD credible interval lower bound (conservative)"
    )
    log10_lr_hpd95_hi:  float = Field(
        description="95% HPD credible interval upper bound"
    )
    lr_point:           float = Field(
        description="LR point estimate = 10^log10_lr_point (clamped to [1e-300, 1e300])"
    )
    n_contributors:     int   = Field(description="K used in this analysis")
    model_engine:       str   = Field(description="'EuroForMix' or 'STRmix'")

    posterior_mixture_weights: List[float] = Field(
        description="Posterior mean mixture weights [w_1, …, w_K]; Σ = 1.0 ± 1e-6"
    )
    posterior_degradation: List[float] = Field(
        description="Posterior mean degradation slopes [d_1, …, d_K] (RFU/bp)"
    )

    convergence:        ConvergenceDiagnosticsOut = Field(
        description="Gelman-Rubin R̂ and ESS convergence diagnostics"
    )

    verbal_scale_en:    str = Field(
        description="ENFSI 2017 7-tier verbal scale statement (English)"
    )
    verbal_scale_tr:    str = Field(
        description="ENFSI 2017 7-tier verbal scale statement (Turkish)"
    )
    assumptions:        List[str] = Field(
        description="Model assumptions and analytical parameters"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Health & Models Endpoints
# ─────────────────────────────────────────────────────────────────────────────

class MixtureHealthResponse(BaseModel):
    """GET /api/v1/forensic/mixture/health"""
    model_config = ConfigDict(protected_namespaces=())

    status:               str  = Field(description="'ok' or 'degraded'")
    engine_importable:    bool = Field(description="MCMCSampler import successful")
    stutter_key_present:  bool = Field(description="BiophysicalPeakModel stutter key b-1.0 generated")
    peak_model_version:   str  = Field(description="Peak model phase/version tag")
    mcmc_engine_version:  str  = Field(description="MCMC engine module version tag")


class ModelParameterInfo(BaseModel):
    """Describes one likelihood model's parameters."""
    model_config = ConfigDict(protected_namespaces=())

    name:        str        = Field(description="Model identifier")
    description: str        = Field(description="Full model description")
    parameters:  Dict[str, Any] = Field(description="Parameter names → default values")
    reference:   str        = Field(description="Research specification reference")


class MixtureModelsResponse(BaseModel):
    """GET /api/v1/forensic/mixture/models"""
    model_config = ConfigDict(protected_namespaces=())

    available_models: List[ModelParameterInfo]
    default_model:    str
    max_contributors: int = Field(description="Maximum K supported (4)")
    min_contributors: int = Field(description="Minimum K supported (2)")
