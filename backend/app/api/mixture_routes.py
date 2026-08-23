"""
FORENZA 1.2.5 — MCMC Mixture Deconvolution FastAPI Router

Exposes three production endpoints under /forensic/mixture:
  POST /forensic/mixture          — Run MCMC mixture deconvolution (synchronous fast-mode)
  GET  /forensic/mixture/health   — Engine import & stutter key sanity check
  GET  /forensic/mixture/models   — List available likelihood models and parameters

Research References:
  pillar_1_probabilistic_genotyping_research.md §2.1–2.9  (MCMC engine)
  pillar_6_lims_zkp_reporting_research.md (ISO 17025 GUM U₉₅, ENFSI 7-tier)

SWGDAM 2020 Synchronous Run Limit:
  n_burn + n_sample ≤ 60,000 for HTTP responses.
  Enforced by MCMCMixtureRequest model_validator (422 on violation).
"""

import logging
from typing import Dict, Tuple

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.probabilistic.mcmc import (
    MCMCSampler,
    MCMCConvergenceDiagnostics,
    MixtureLRResult,
)
from node.services.forensic.probabilistic.peak_model import (
    BiophysicalPeakModel,
    LOCUS_STUTTER_RATIOS,
)

from .mixture_schemas import (
    ConvergenceDiagnosticsOut,
    MCMCMixtureRequest,
    MCMCMixtureResponse,
    MixtureHealthResponse,
    MixtureModelsResponse,
    ModelParameterInfo,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/forensic/mixture",
    tags=["MCMC Mixture Deconvolution"],
)

# ---------------------------------------------------------------------------
# Helper: convert EPG string allele keys → float keys required by MCMCSampler
# ---------------------------------------------------------------------------

def _parse_epg_keys(
    epg_data: Dict[str, Dict[str, float]]
) -> Dict[str, Dict[float, float]]:
    """
    Convert {locus → {str_allele → rfu}} to {locus → {float_allele → rfu}}.
    Validated upstream by MCMCMixtureRequest.validate_epg_allele_keys.
    """
    return {
        locus: {float(allele_key): rfu for allele_key, rfu in allele_dict.items()}
        for locus, allele_dict in epg_data.items()
    }


def _parse_suspect_genotype(
    suspect_genotype: Dict[str, list] | None
) -> Dict[str, Tuple[float, float]] | None:
    """Convert {locus → [a1, a2]} to {locus → (a1, a2)} for MCMCSampler."""
    if suspect_genotype is None:
        return None
    return {
        locus: (float(alleles[0]), float(alleles[1]))
        for locus, alleles in suspect_genotype.items()
    }


def _map_convergence(conv: MCMCConvergenceDiagnostics) -> ConvergenceDiagnosticsOut:
    """Map engine dataclass → Pydantic response sub-model."""
    return ConvergenceDiagnosticsOut(
        r_hat_per_param=conv.r_hat_per_param,
        r_hat_max=conv.r_hat_max,
        ess_per_param=conv.ess_per_param,
        ess_min=conv.ess_min,
        converged=conv.converged,
        n_samples_per_chain=conv.n_samples_per_chain,
    )


def _map_result(result: MixtureLRResult) -> MCMCMixtureResponse:
    """Map MixtureLRResult dataclass → MCMCMixtureResponse Pydantic model."""
    return MCMCMixtureResponse(
        log10_lr_point=result.log10_lr_point,
        log10_lr_hpd95_lo=result.log10_lr_hpd95_lo,
        log10_lr_hpd95_hi=result.log10_lr_hpd95_hi,
        lr_point=result.lr_point,
        n_contributors=result.n_contributors,
        model_engine=result.model_engine,
        posterior_mixture_weights=result.posterior_mixture_weights,
        posterior_degradation=result.posterior_degradation,
        convergence=_map_convergence(result.convergence),
        verbal_scale_en=result.verbal_scale_en,
        verbal_scale_tr=result.verbal_scale_tr,
        assumptions=result.assumptions,
    )


# ---------------------------------------------------------------------------
# POST /forensic/mixture — Main deconvolution endpoint
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=MCMCMixtureResponse,
    summary="MCMC Mixture Deconvolution",
    description=(
        "Runs a Metropolis-Hastings MCMC sampler to deconvolve K-contributor "
        "DNA mixtures from electropherogram (EPG) peak heights. "
        "Returns posterior mixture weights, 95% HPD log₁₀(LR) interval, "
        "Gelman-Rubin R̂ convergence diagnostics, and ENFSI 2017 7-tier verbal scale. "
        "\n\n"
        "**Fast-mode defaults** (HTTP synchronous): n_burn=2000, n_sample=6000. "
        "Total n_burn+n_sample must not exceed 60,000. "
        "\n\n"
        "Research: pillar_1_probabilistic_genotyping_research.md §2.5–2.9"
    ),
    status_code=status.HTTP_200_OK,
)
async def run_mcmc_mixture(body: MCMCMixtureRequest) -> MCMCMixtureResponse:
    """
    Execute MCMC mixture deconvolution.

    Validation and timeout guard are enforced by the MCMCMixtureRequest schema.
    Engine errors are wrapped in appropriate HTTP status codes.
    """
    try:
        observed = _parse_epg_keys(body.epg_data)
        suspect  = _parse_suspect_genotype(body.suspect_genotype)

        sampler = MCMCSampler(
            n_burn=body.n_burn,
            n_sample=body.n_sample,
            k_thin=body.k_thin,
            n_chains=body.n_chains,
            model=body.model,
            sigma=body.sigma,
            omega=body.omega,
            seed=body.seed,
        )

        result = sampler.run_mixture_deconvolution(
            observed=observed,
            K=body.K,
            suspect_genotype=suspect,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"MCMC parameter validation error: {str(exc)}",
        )
    except RuntimeError as exc:
        logger.exception("MCMC engine runtime error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MCMC engine failure: {str(exc)}",
        )
    except Exception as exc:
        logger.exception("Unexpected error in MCMC mixture deconvolution")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(exc)}",
        )

    return _map_result(result)


# ---------------------------------------------------------------------------
# GET /forensic/mixture/health — Engine sanity check
# ---------------------------------------------------------------------------

@router.get(
    "/health",
    response_model=MixtureHealthResponse,
    summary="MCMC Mixture Engine Health Check",
    description=(
        "Verifies that MCMCSampler is importable and that the BiophysicalPeakModel "
        "generates back-stutter keys correctly (EC-MCMC-04 regression guard). "
        "Returns 200 if all checks pass, 503 if engine is degraded."
    ),
    status_code=status.HTTP_200_OK,
)
async def mixture_health() -> MixtureHealthResponse:
    """Sanity check: import + stutter key generation."""
    engine_importable = False
    stutter_key_present = False
    peak_model_version = "unknown"
    mcmc_engine_version = "unknown"

    try:
        # 1. Import check
        from node.services.forensic.probabilistic.mcmc import MCMCSampler as _S
        engine_importable = True
        mcmc_engine_version = "MCMC-MH v1.2.5 (pillar_1 §2.5–2.9)"

        # 2. Stutter key regression guard (EC-MCMC-04)
        bphys = BiophysicalPeakModel(template_scale=1000.0)
        expected = bphys.expected_peak_heights(
            "D3S1358", [(15.0, 15.0)], [1.0], [0.0]
        )
        stutter_key_present = 14.0 in expected
        peak_model_version = "BiophysicalPeakModel Phase-2 (stutter b-1 fix, 2026-08-20)"

    except Exception as exc:
        logger.error(f"[health] MCMC engine health check failed: {exc}")

    http_status = status.HTTP_200_OK if (engine_importable and stutter_key_present) else status.HTTP_503_SERVICE_UNAVAILABLE

    response = MixtureHealthResponse(
        status="ok" if (engine_importable and stutter_key_present) else "degraded",
        engine_importable=engine_importable,
        stutter_key_present=stutter_key_present,
        peak_model_version=peak_model_version,
        mcmc_engine_version=mcmc_engine_version,
    )

    if http_status != status.HTTP_200_OK:
        raise HTTPException(
            status_code=http_status,
            detail=response.model_dump(),
        )

    return response


# ---------------------------------------------------------------------------
# GET /forensic/mixture/models — Available likelihood models
# ---------------------------------------------------------------------------

@router.get(
    "/models",
    response_model=MixtureModelsResponse,
    summary="List Available MCMC Likelihood Models",
    description=(
        "Returns the list of supported likelihood models (STRmix Log-Normal and "
        "EuroForMix Gamma) with their parameters and research references."
    ),
    status_code=status.HTTP_200_OK,
)
async def list_mixture_models() -> MixtureModelsResponse:
    """Enumerate available likelihood engines and their parameters."""
    return MixtureModelsResponse(
        available_models=[
            ModelParameterInfo(
                name="STRmix",
                description=(
                    "STRmix Log-Normal peak height model. "
                    "h_{l,a} ~ LogNormal(log(μ_{l,a}), σ²). "
                    "Default model for standard casework."
                ),
                parameters={
                    "sigma": 0.35,
                    "gamma": 1.0,
                    "description": "σ = dispersion (log-scale SD); γ = heteroscedasticity exponent",
                },
                reference="pillar_1_probabilistic_genotyping_research.md §2.3 (STRmix Log-Normal)",
            ),
            ModelParameterInfo(
                name="EuroForMix",
                description=(
                    "EuroForMix Gamma peak height model. "
                    "h_{l,a} ~ Gamma(α=μ²/σ², β=μ/σ²) where σ = ω·μ. "
                    "Used for cross-validation against EuroForMix v3.3.1."
                ),
                parameters={
                    "omega": 0.35,
                    "description": "ω = coefficient of variation (CV); α = (μ/ω)², β = μ/ω²",
                },
                reference="pillar_1_probabilistic_genotyping_research.md §2.2 (EuroForMix Gamma)",
            ),
        ],
        default_model="STRmix",
        max_contributors=4,
        min_contributors=2,
    )
