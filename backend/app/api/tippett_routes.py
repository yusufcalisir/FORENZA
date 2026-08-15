"""
FORENZA Tippett Calibration & ENFSI Evaluative Reporting API Router (Module 05).

Exposes endpoints for Tippett ROC Calibration and Evaluative Reporting (Pillar 1 §5):
  POST /forensic/validation/tippett-curve      — Tippett ECCDF Hp/Hd curves
  POST /forensic/validation/roc-analysis       — Empirical ROC & AUC
  POST /forensic/validation/cllr-score         — Log-Likelihood-Ratio Cost Cllr
  POST /forensic/validation/hpd-lower-bound    — Conservative 95% HPD LR_court
  POST /forensic/validation/enfsi-verbal-scale — ENFSI 2017 7-Tier EN/TR verbal scale
"""

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.validation.tippett_engine import TippettEngine
from .tippett_schemas import (
    TippettCurveRequest, TippettCurveResponse, TippettPointSchema,
    ROCAnalysisRequest, ROCAnalysisResponse,
    CllrScoreRequest, CllrScoreResponse,
    HPDLowerBoundRequest, HPDLowerBoundResponse,
    ENFSIScaleRequest, ENFSIScaleResponse,
)

router = APIRouter(
    prefix="/forensic/validation",
    tags=["Tippett Calibration & ENFSI Evaluative Reporting"],
)

_tippett_engine = TippettEngine()


# ── §5.1 Tippett Calibration Curves ──────────────────────────────────────────

@router.post(
    "/tippett-curve",
    response_model=TippettCurveResponse,
    summary="Tippett Calibration Curves (Hp / Hd Empirical Complementary CDF)",
    description=(
        "Computes Hp and Hd Tippett ECCDF curves: "
        "P(log10(LR) >= x | Hp) and P(log10(LR) >= x | Hd). "
        "Includes FPR, FNR, and discrimination power at LR=1 threshold. (Research §5.1)"
    ),
    status_code=status.HTTP_200_OK,
)
async def compute_tippett_curves(body: TippettCurveRequest) -> TippettCurveResponse:
    try:
        res = _tippett_engine.compute_tippett_curves(
            hp_log10_lrs=body.hp_log10_lrs,
            hd_log10_lrs=body.hd_log10_lrs,
            num_points=body.num_points,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Tippett curve computation failed: {str(exc)}"
        )
    return TippettCurveResponse(
        n_hp=res.n_hp,
        n_hd=res.n_hd,
        grid_points=[
            TippettPointSchema(
                threshold=pt.threshold,
                hp_exceedance=pt.hp_exceedance,
                hd_exceedance=pt.hd_exceedance,
            )
            for pt in res.grid_points
        ],
        min_threshold=res.min_threshold,
        max_threshold=res.max_threshold,
        fpr_at_zero=res.fpr_at_zero,
        fnr_at_zero=res.fnr_at_zero,
        discrimination_power=res.discrimination_power,
    )


# ── §5.2 ROC Analysis ─────────────────────────────────────────────────────────

@router.post(
    "/roc-analysis",
    response_model=ROCAnalysisResponse,
    summary="Empirical ROC Analysis — FPR, FNR, AUC, MER",
    description=(
        "Computes empirical ROC curve and AUC via trapezoidal integration. "
        "FPR = P(log10(LR) > 0 | Hd), FNR = P(log10(LR) < 0 | Hp). "
        "AUC >= 0.999 target (SWGDAM 2020). (Research §5.2)"
    ),
    status_code=status.HTTP_200_OK,
)
async def compute_roc_analysis(body: ROCAnalysisRequest) -> ROCAnalysisResponse:
    try:
        res = _tippett_engine.compute_roc_analysis(
            hp_log10_lrs=body.hp_log10_lrs,
            hd_log10_lrs=body.hd_log10_lrs,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"ROC analysis failed: {str(exc)}"
        )
    return ROCAnalysisResponse(
        n_hp=res.n_hp,
        n_hd=res.n_hd,
        auc=res.auc,
        fpr_at_lr1=res.fpr_at_lr1,
        fnr_at_lr1=res.fnr_at_lr1,
        mer_upper_bound=res.mer_upper_bound,
        interpretation=res.interpretation,
    )


# ── §5.3 Cllr Cost ────────────────────────────────────────────────────────────

@router.post(
    "/cllr-score",
    response_model=CllrScoreResponse,
    summary="Log-Likelihood-Ratio Cost (Cllr) Calibration Score",
    description=(
        "Computes Cllr = (1/2N_Hp)*SUM log2(1+1/LR_i) + (1/2N_Hd)*SUM log2(1+LR_j). "
        "Excellent calibration target: Cllr < 0.05. "
        "(Brümmer & du Preez 2006; Research §5.3)"
    ),
    status_code=status.HTTP_200_OK,
)
async def compute_cllr_score(body: CllrScoreRequest) -> CllrScoreResponse:
    try:
        res = _tippett_engine.compute_cllr_cost(
            hp_log10_lrs=body.hp_log10_lrs,
            hd_log10_lrs=body.hd_log10_lrs,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cllr computation failed: {str(exc)}"
        )
    return CllrScoreResponse(
        n_hp=res.n_hp,
        n_hd=res.n_hd,
        cllr=res.cllr,
        cllr_min=res.cllr_min,
        cllr_cal=res.cllr_cal,
        calibration_quality=res.calibration_quality,
        interpretation=res.interpretation,
    )


# ── §5.4 HPD Lower Bound ──────────────────────────────────────────────────────

@router.post(
    "/hpd-lower-bound",
    response_model=HPDLowerBoundResponse,
    summary="Conservative 95% HPD Lower Bound (LR_court)",
    description=(
        "LR_court = Percentile_5%({LR^(m)}_{m=1}^M) from MCMC posterior samples. "
        "Provides court-admissible conservative lower bound with 95% posterior coverage. (Research §5.4)"
    ),
    status_code=status.HTTP_200_OK,
)
async def compute_hpd_lower_bound(body: HPDLowerBoundRequest) -> HPDLowerBoundResponse:
    try:
        res = _tippett_engine.compute_hpd_lower_bound(
            mcmc_log10_lrs=body.mcmc_log10_lrs,
            percentile=body.percentile,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"HPD lower bound computation failed: {str(exc)}"
        )
    return HPDLowerBoundResponse(
        n_mcmc_samples=res.n_mcmc_samples,
        percentile=res.percentile,
        log10_lr_court=res.log10_lr_court,
        log10_lr_median=res.log10_lr_median,
        log10_lr_mean=res.log10_lr_mean,
        log10_lr_95ci_upper=res.log10_lr_95ci_upper,
        interpretation=res.interpretation,
    )


# ── §5.5 ENFSI 2017 Verbal Scale ─────────────────────────────────────────────

@router.post(
    "/enfsi-verbal-scale",
    response_model=ENFSIScaleResponse,
    summary="ENFSI 2017 7-Tier Verbal Reporting Scale (EN/TR + Prosecutor's Fallacy Shield)",
    description=(
        "Maps log10(LR) to the ENFSI 2017 standardized verbal predicate in English and Turkish. "
        "Active Prosecutor's Fallacy Shield (Transposed Conditional) included in response. (Research §5.5)"
    ),
    status_code=status.HTTP_200_OK,
)
async def map_enfsi_verbal_scale(body: ENFSIScaleRequest) -> ENFSIScaleResponse:
    try:
        res = _tippett_engine.map_enfsi_verbal_scale(log10_lr=body.log10_lr)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"ENFSI verbal scale mapping failed: {str(exc)}"
        )
    return ENFSIScaleResponse(
        log10_lr=res.log10_lr,
        tier=res.tier,
        tier_name_en=res.tier_name_en,
        tier_name_tr=res.tier_name_tr,
        lr_range_description=res.lr_range_description,
        prosecutors_fallacy_shield_en=res.prosecutors_fallacy_shield_en,
        prosecutors_fallacy_shield_tr=res.prosecutors_fallacy_shield_tr,
        is_positive_support=res.is_positive_support,
        likelihood_equation=res.likelihood_equation,
    )
