"""
FORENZA Tippett Calibration & ENFSI Evaluative Reporting API — Pydantic v2 Schemas (Module 05).

Covers all endpoints:
  - Tippett Calibration Curves (Hp / Hd ECCDF)
  - Empirical ROC Analysis (FPR, FNR, AUC)
  - Log-Likelihood-Ratio Cost Cllr
  - Conservative 95% HPD Lower Bound (LR_court)
  - ENFSI 2017 7-Tier Verbal Scale (EN/TR + Prosecutor's Fallacy Shield)
"""

from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


# ── Tippett Calibration Curves ────────────────────────────────────────────────

class TippettCurveRequest(BaseModel):
    """
    Request for Tippett calibration curves.
    Provide log10(LR) distributions under both Hp and Hd.
    """
    hp_log10_lrs: List[float] = Field(
        ...,
        min_length=1,
        description="log10(LR) values under Hp (suspect is true contributor). Research §5.1.",
        examples=[[5.0, 6.2, 4.8, 7.1, 5.5]],
    )
    hd_log10_lrs: List[float] = Field(
        ...,
        min_length=1,
        description="log10(LR) values under Hd (unrelated individual). Research §5.1.",
        examples=[[-1.2, -0.5, 0.3, -2.1, -0.8]],
    )
    num_points: int = Field(
        100,
        ge=10,
        le=1000,
        description="Number of evaluation grid points for the Tippett ECCDF curves.",
    )


class TippettPointSchema(BaseModel):
    threshold: float
    hp_exceedance: float
    hd_exceedance: float


class TippettCurveResponse(BaseModel):
    n_hp: int
    n_hd: int
    grid_points: List[TippettPointSchema]
    min_threshold: float
    max_threshold: float
    fpr_at_zero: float
    fnr_at_zero: float
    discrimination_power: float


# ── ROC Analysis ──────────────────────────────────────────────────────────────

class ROCAnalysisRequest(BaseModel):
    """
    Request for empirical ROC analysis and AUC computation.
    """
    hp_log10_lrs: List[float] = Field(
        ...,
        min_length=2,
        description="log10(LR) values for true contributors (Hp). Research §5.2.",
        examples=[[4.5, 5.1, 6.2, 7.0, 5.8]],
    )
    hd_log10_lrs: List[float] = Field(
        ...,
        min_length=2,
        description="log10(LR) values for non-contributors (Hd). Research §5.2.",
        examples=[[-2.1, -0.5, -1.8, 0.2, -3.0]],
    )


class ROCAnalysisResponse(BaseModel):
    n_hp: int
    n_hd: int
    auc: float
    fpr_at_lr1: float
    fnr_at_lr1: float
    mer_upper_bound: float
    interpretation: str


# ── Cllr Cost ────────────────────────────────────────────────────────────────

class CllrScoreRequest(BaseModel):
    """
    Request for Log-Likelihood-Ratio Cost (Cllr) calibration score.

    Cllr = (1/(2*N_Hp)) * SUM log2(1 + 1/LR_i) + (1/(2*N_Hd)) * SUM log2(1 + LR_j)
    (Brümmer & du Preez 2006; Research §5.3)
    """
    hp_log10_lrs: List[float] = Field(
        ...,
        min_length=1,
        description="log10(LR) values under Hp (true contributor distribution). Research §5.3.",
        examples=[[5.0, 6.2, 4.8]],
    )
    hd_log10_lrs: List[float] = Field(
        ...,
        min_length=1,
        description="log10(LR) values under Hd (non-contributor distribution). Research §5.3.",
        examples=[[-1.2, -0.5, -2.1]],
    )


class CllrScoreResponse(BaseModel):
    n_hp: int
    n_hd: int
    cllr: float
    cllr_min: float
    cllr_cal: float
    calibration_quality: str
    interpretation: str


# ── HPD Lower Bound ──────────────────────────────────────────────────────────

class HPDLowerBoundRequest(BaseModel):
    """
    Request for conservative 95% HPD lower bound.

    LR_court = Percentile_{5%}({LR^(m)}_{m=1}^M)  (Research §5.4)
    """
    mcmc_log10_lrs: List[float] = Field(
        ...,
        min_length=1,
        description="MCMC posterior log10(LR) samples from probabilistic genotyping engine.",
        examples=[[25.8, 26.1, 25.5, 26.4, 25.9]],
    )
    percentile: float = Field(
        5.0,
        ge=0.1,
        le=50.0,
        description="Percentile for conservative lower bound (default 5.0 for 95% HPD). Research §5.4.",
        examples=[5.0],
    )


class HPDLowerBoundResponse(BaseModel):
    n_mcmc_samples: int
    percentile: float
    log10_lr_court: float
    log10_lr_median: float
    log10_lr_mean: float
    log10_lr_95ci_upper: float
    interpretation: str


# ── ENFSI Verbal Scale ───────────────────────────────────────────────────────

class ENFSIScaleRequest(BaseModel):
    """
    Request for ENFSI 2017 7-Tier Verbal Reporting Scale mapping.
    Maps numeric log10(LR) to standardized verbal predicates in EN & TR.
    """
    log10_lr: float = Field(
        ...,
        ge=-300.0,
        le=300.0,
        description="log10(LR) value to map to ENFSI 2017 verbal predicate. Research §5.5.",
        examples=[26.0, 3.5, -1.2, 0.0],
    )


class ENFSIScaleResponse(BaseModel):
    log10_lr: float
    tier: int
    tier_name_en: str
    tier_name_tr: str
    lr_range_description: str
    prosecutors_fallacy_shield_en: str
    prosecutors_fallacy_shield_tr: str
    is_positive_support: bool
    likelihood_equation: str
