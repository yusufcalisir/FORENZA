"""
FORENZA Touch DNA & Low-Template API — Pydantic v2 Schemas (Module 04).

Covers all LTDNA stochastic phenomenon endpoints verbatim from Pillar 1 §4:
  - Logistic Dropout P(D) — RFU-based and DNA mass-based calibration curves
  - Poisson Drop-in P(C=k) — count probability and exponential height PDF
  - Heterozygote Balance H_b — peak balance and stochastic quality flags
  - Curran-Gill Stochastic LTDNA Likelihood Ratio
  - Multi-Locus LTDNA Profile Likelihood Ratio
  - Substrate recovery and full LTDNA analysis
  - Dilution tiers and benchmark casework vectors
"""

from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel, Field, ConfigDict


# ── Substrate & Stochastic Schemas ───────────────────────────────────────────

class SubstrateEfficiencySchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    substrate_type: str
    efficiency_factor: float
    input_mass_pg: float
    recovered_mass_pg: float


class StochasticDropoutSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    recovered_mass_pg: float
    dropout_probability_pd: float
    dropin_probability_pc: float
    peak_imbalance_ratio: float


class AnalyzeLtdnaRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sample_id: str = Field(..., examples=["TOUCH-HANDLE-001"])
    substrate_type: str = Field(
        ..., examples=["TEXTURED_NON_POROUS", "SMOOTH_NON_POROUS", "POROUS_FABRIC", "ROUGH_WOOD"]
    )
    input_mass_pg: float = Field(..., gt=0.0, examples=[80.0])
    lambda_dropout: float = Field(0.05, gt=0.0, examples=[0.05])


class AnalyzeLtdnaResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sample_id: str
    substrate: SubstrateEfficiencySchema
    stochastic_model: StochasticDropoutSchema
    is_low_template: bool
    ltdna_summary: str


class ContributorDeconvRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sample_id: str = Field(..., examples=["TOUCH-HANDLE-001"])
    num_contributors: int = Field(..., ge=1, le=4, examples=[2])
    recovered_mass_pg: float = Field(..., gt=0.0, examples=[32.0])


class ContributorDeconvResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sample_id: str
    num_contributors: int
    deconvolution_status: str
    mixture_proportions: Dict[str, float]
    mcmc_acceptance_rate: float
    log10_lr: float


# ── §4.1 Logistic Dropout P(D) Schemas ───────────────────────────────────────

class DropoutModelRequest(BaseModel):
    """
    Request for logistic allele dropout probability computation.
    model_type: 'RFU' or 'MASS_PG' or 'FRAGMENT_BP'
    """
    model_config = ConfigDict(protected_namespaces=())
    model_type: str = Field(
        "RFU",
        description="'RFU' for peak height model (β₀=+2.50, β₁=-0.025) or "
                    "'MASS_PG' for DNA mass model (β₀=+3.20, β₁=-0.080) or "
                    "'FRAGMENT_BP' for amplicon size decay model.",
        examples=["RFU", "MASS_PG", "FRAGMENT_BP"],
    )
    input_value: float = Field(
        ...,
        description="Peak height in RFU or DNA mass in pg depending on model_type.",
        examples=[50.0, 150.0],
    )
    amplicon_bp: Optional[float] = Field(
        None,
        description="Optional amplicon size in base pairs (bp) for fragment degradation penalty.",
        examples=[175.0, 360.0],
    )
    beta_0: Optional[float] = Field(
        None,
        description="Override logistic intercept β₀ (defaults to research constants).",
    )
    beta_1: Optional[float] = Field(
        None,
        description="Override logistic slope β₁ (defaults to research constants).",
    )


class DropoutModelResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    input_value: float
    model_type: str
    beta_0: float
    beta_1: float
    logit_value: float
    dropout_probability: float
    critical_threshold: float
    is_below_critical: bool


# ── §4.2 Poisson Drop-in & Exponential Height Schemas ─────────────────────────

class DropinModelRequest(BaseModel):
    """Request for Poisson drop-in count probability and/or exponential peak height PDF."""
    model_config = ConfigDict(protected_namespaces=())
    k: int = Field(
        0,
        ge=0,
        description="Number of drop-in alleles. P(C=k) = (λ_C^k * e^{-λ_C}) / k!",
        examples=[0, 1],
    )
    lambda_c: float = Field(
        0.020,
        gt=0.0,
        description="Poisson drop-in rate per locus λ_C (default 0.020 per research §4.2).",
        examples=[0.020],
    )
    h_c: Optional[float] = Field(
        None,
        description="Optional drop-in peak height (RFU) for exponential height PDF computation.",
        examples=[75.0, 120.0],
    )
    lambda_h: float = Field(
        0.015,
        gt=0.0,
        description="Exponential height decay parameter λ_h (default 0.015 per research §4.2).",
        examples=[0.015],
    )
    at_rfu: float = Field(
        50.0,
        ge=0.0,
        description="Analytical Threshold AT in RFU (default 50.0 RFU per research §4.2).",
        examples=[50.0],
    )


class DropinModelResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    k: int
    lambda_c: float
    poisson_probability: float
    h_c: Optional[float]
    lambda_h: float
    at_rfu: float
    height_density: Optional[float]
    is_above_at: Optional[bool]


# ── §4.2 Heterozygote Balance Schemas ─────────────────────────────────────────

class HeterozygoteBalanceRequest(BaseModel):
    """Request for heterozygote peak balance and stochastic quality flag evaluation."""
    model_config = ConfigDict(protected_namespaces=())
    h1: float = Field(
        ...,
        ge=0.0,
        description="Peak height of allele 1 in RFU.",
        examples=[80.0],
    )
    h2: float = Field(
        ...,
        ge=0.0,
        description="Peak height of allele 2 in RFU.",
        examples=[200.0],
    )
    hb_threshold: float = Field(
        0.60,
        gt=0.0,
        le=1.0,
        description="Heterozygote balance flag threshold H_b (default 0.60 per research §4.2).",
        examples=[0.60],
    )
    st_threshold: float = Field(
        150.0,
        ge=0.0,
        description="Stochastic Threshold ST in RFU (default 150.0 RFU per research §4.2).",
        examples=[150.0],
    )
    at_threshold: float = Field(
        50.0,
        ge=0.0,
        description="Analytical Threshold AT in RFU (default 50.0 RFU per research §4.2).",
        examples=[50.0],
    )


class HeterozygoteBalanceResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    h1: float
    h2: float
    h_min: float
    h_max: float
    h_balance: float
    at_threshold: float
    st_threshold: float
    hb_threshold: float
    imbalance_flag: bool
    stochastic_threshold_flag: bool
    at_flag: bool
    stochastic_flag_active: bool
    interpretation: str


# ── Single-Locus Curran-Gill Stochastic LR Schemas ───────────────────────────

class StochasticLRRequest(BaseModel):
    """
    Request for Curran-Gill stochastic single-source LTDNA Likelihood Ratio.
    VECTOR_03 example: vWA locus, suspect (16,17), observed {16: 80.0}, 17 dropped.
    """
    model_config = ConfigDict(protected_namespaces=())
    locus: str = Field(
        ...,
        description="Locus name (e.g. 'vWA', 'TH01').",
        examples=["vWA"],
    )
    suspect_allele_1: float = Field(
        ...,
        description="First allele of suspect genotype.",
        examples=[16.0],
    )
    suspect_allele_2: float = Field(
        ...,
        description="Second allele of suspect genotype.",
        examples=[17.0],
    )
    observed_peaks: Dict[str, float] = Field(
        ...,
        description="Observed peak heights keyed by allele (as string). Missing alleles indicate dropout.",
        examples=[{"16": 80.0}],
    )
    p_dropout: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Allele dropout probability P(D) computed from logistic model.",
        examples=[0.6225],
    )
    p_dropin: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Allele drop-in probability P(C=1) from Poisson model.",
        examples=[0.0196],
    )
    locus_frequencies: Dict[str, float] = Field(
        ...,
        description="Population allele frequencies for this locus.",
        examples=[{"16": 0.211, "17": 0.273}],
    )
    theta: float = Field(
        0.03,
        ge=0.0,
        le=0.10,
        description="Subpopulation coancestry θ for Balding-Nichols correction.",
        examples=[0.03],
    )


class StochasticLRResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    locus: str
    suspect_genotype: List[float]
    p_dropout: float
    p_dropin: float
    prob_both_present: float
    prob_single_dropout: float
    prob_both_dropout: float
    prob_dropin_contribution: float
    pop_genotype_prob: float
    likelihood_numerator: float
    match_probability: float
    log10_lr: float
    interpretation: str


# ── Multi-Locus LTDNA Profile LR Schemas ──────────────────────────────────────

class MultiLocusLTDNARequest(BaseModel):
    """Request for composite multi-locus profile stochastic Likelihood Ratio."""
    model_config = ConfigDict(protected_namespaces=())
    suspect_profile: Dict[str, List[float]] = Field(
        ...,
        description="Suspect 24-locus diploid genotypes keyed by locus name.",
        examples=[{"vWA": [16.0, 17.0], "D3S1358": [15.0, 16.0]}],
    )
    observed_profile: Dict[str, Dict[str, float]] = Field(
        ...,
        description="Observed electropherogram peaks with peak heights per locus.",
        examples=[{"vWA": {"16": 80.0}, "D3S1358": {"15": 110.0, "16": 95.0}}],
    )
    template_pg: float = Field(
        ...,
        gt=0.0,
        description="Total DNA template mass in picograms.",
        examples=[50.0],
    )
    theta: float = Field(
        0.03,
        ge=0.0,
        le=0.15,
        description="Subpopulation coancestry theta (default 0.03).",
        examples=[0.03],
    )
    population_frequencies: Optional[Dict[str, Dict[str, float]]] = Field(
        None,
        description="Optional population allele frequency database override.",
    )


class SingleLocusLRDetail(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    locus: str
    suspect_genotype: List[float]
    observed_state: str
    likelihood_hp: float
    likelihood_hd: float
    log10_lr: float
    stochastic_flags: List[str]
    verbal_en: str
    verbal_tr: str


class MultiLocusLTDNAResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    n_loci: int
    template_pg: float
    p_dropout: float
    total_log10_lr: float
    total_lr_point: float
    total_stochastic_flags_count: int
    verbal_en: str
    verbal_tr: str
    additivity_verified: bool
    locus_breakdown: List[SingleLocusLRDetail]


# ── Reference Catalog Schemas ─────────────────────────────────────────────────

class DilutionTierDetailSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    tier_id: str
    nominal_mass_pg: float
    equivalent_cells: float
    expected_p_dropout: float
    expected_hb: float
    stochastic_zone: str
    operational_designation: str
    dropout_loci_count: int


class SubstrateDetailSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    substrate_id: str
    name: str
    description: str
    recovery_efficiency: float
    porosity_type: str
    touch_swab_protocol: str


class BenchmarkVectorDetailSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    vector_id: str
    title: str
    description: str
    nominal_template_pg: float
    substrate_id: str
    masked_dropout_loci: List[str]
