"""
FORENZA Population Genetics API — Pydantic v2 Schemas.
Module 03: Dirichlet Smoothing, HWE, Linkage Equilibrium, FST Matrix.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel, Field


class FrequencyBoundRequest(BaseModel):
    """Request body for POST /population/frequency."""
    locus: str = Field(..., examples=["TH01"])
    allele: float = Field(..., examples=[9.3])
    raw_frequency: float = Field(..., ge=0.0, le=1.0, examples=[0.001])
    observed_count: int = Field(0, ge=0)
    database_n: Optional[int] = Field(500, ge=10)


class FrequencyBoundResponse(BaseModel):
    locus: str
    allele: float
    observed_count: int
    raw_frequency: float
    bounded_frequency: float
    was_bounded: bool
    rarity_index: float
    explanation: str


class FstDistanceRequest(BaseModel):
    """Request body for POST /population/fst."""
    population1: str = Field(..., examples=["Caucasian"])
    population2: str = Field(..., examples=["AfricanAmerican"])


class FstDistanceResponse(BaseModel):
    population_pair: List[str]
    fst_value: float
    genetic_distance_neis: float
    locus_fst_breakdown: Dict[str, float]
    recommendation: str


class PopulationListResponse(BaseModel):
    supported_populations: List[str]
    default_database_n: int
    nrc2_recommendation: str


# ── Module 03 Schemas ─────────────────────────────────────────────────────────

class DirichletSmoothRequest(BaseModel):
    """Request body for POST /population/dirichlet."""
    locus: str = Field(..., examples=["TH01"])
    observed_counts: Dict[str, int] = Field(..., examples=[{"6.0": 100, "9.3": 50, "10.0": 0}])
    prior_frequencies: Dict[str, float] = Field({}, examples=[{"6.0": 0.20, "9.3": 0.40, "10.0": 0.40}])
    theta: float = Field(0.03, ge=0.001, le=0.20)
    n_individuals: Optional[int] = Field(1036, ge=10)


class DirichletAlleleResult(BaseModel):
    allele: float
    observed_count: int
    raw_frequency: float
    prior_frequency: float
    posterior_frequency: float
    dirichlet_alpha: float
    was_p_min_applied: bool
    p_min_used: float


class DirichletSmoothResponse(BaseModel):
    locus: str
    allele_posteriors: List[DirichletAlleleResult]
    n_individuals: int
    theta: float
    concentration_parameter: float
    sum_posterior: float


class HWETestRequest(BaseModel):
    """Request body for POST /population/hwe."""
    locus: str = Field(..., examples=["TH01"])
    # Genotype counts as {"a1,a2": count} string keys for JSON compat
    genotype_counts: Dict[str, int] = Field(
        ...,
        examples=[{"6.0,6.0": 25, "6.0,9.3": 50, "9.3,9.3": 25}]
    )
    n_permutations: int = Field(10000, ge=100, le=100000)


class HWETestResponse(BaseModel):
    locus: str
    n_alleles: int
    n_genotypes: int
    h_obs: float
    h_exp: float
    f_is: float
    p_value: float
    alpha_bonferroni: float
    hwe_rejected: bool
    decision: str
    n_permutations: int


class ThetaCorrectedLRRequest(BaseModel):
    """Request body for POST /population/theta-lr."""
    p_a: float = Field(..., ge=0.0, le=1.0, examples=[0.20])
    p_b: Optional[float] = Field(None, ge=0.0, le=1.0, description="If provided, treats as heterozygote")
    theta: float = Field(0.03, ge=0.001, le=0.20)


class ThetaCorrectedLRResponse(BaseModel):
    p_a: float
    p_b: Optional[float]
    theta: float
    match_probability: float
    log10_lr: float
    genotype_type: str   # 'HOMOZYGOTE' | 'HETEROZYGOTE'


class FstMatrixRequest(BaseModel):
    """Request body for POST /population/fst-matrix."""
    populations: List[str] = Field(
        ...,
        min_length=2,
        examples=[["Caucasian", "AfricanAmerican", "Hispanic", "Asian"]]
    )


class FstMatrixResponse(BaseModel):
    populations: List[str]
    n_pairs: int
    matrix: Dict[str, float]   # "pop1|pop2": fst_value
    nei_matrix: Dict[str, float]
    theta_recommendation: float
    verdict: str


# ── 24-Locus STR & Kinship Schemas ──────────────────────────────────────────

class ProfileRMPRequest(BaseModel):
    """Request body for POST /population/profile-rmp."""
    profile: Dict[str, Any] = Field(..., examples=[{"TH01": ["6", "9.3"], "D21S11": ["28", "31.2"]}])
    population: str = Field("Caucasian", examples=["Caucasian"])
    theta: float = Field(0.01, ge=0.0, le=0.20)
    use_exact_balding_nichols: bool = True
    dropout_map: Optional[Dict[str, bool]] = None
    dropout_q: float = Field(0.05, ge=0.0, le=1.0)


class MeasurementUncertaintySchema(BaseModel):
    combined_standard_uncertainty_log10: float
    coverage_factor_k: float = 2.00
    expanded_uncertainty_U95: float
    ci_95_lower: float
    ci_95_upper: float


class ProfileRMPResponse(BaseModel):
    population: str
    theta: float
    evaluated_loci_count: int
    combined_rmp: float
    combined_lr: float
    combined_log10_lr: float
    enfsi_verbal_scale: str
    measurement_uncertainty: MeasurementUncertaintySchema
    invariants: Dict[str, Any]
    locus_results: List[Dict[str, Any]]


class KinshipDuoRequest(BaseModel):
    """Request body for POST /population/kinship-duo."""
    profile1: Dict[str, Any] = Field(..., description="Child / Proband profile")
    profile2: Dict[str, Any] = Field(..., description="Alleged relative profile")
    relationship: str = Field("Parent-Child", examples=["Parent-Child", "Full Sibling", "Half Sibling", "First Cousin", "Unrelated"])
    population: str = Field("Caucasian", examples=["Caucasian"])
    theta: float = Field(0.01, ge=0.0, le=0.20)
    apply_smm: bool = True


class KinshipLocusSchema(BaseModel):
    locus_name: str
    genotype1: Tuple[str, str]
    genotype2: Tuple[str, str]
    shared_alleles: List[str]
    kinship_index: float
    log10_ki: float
    mutation_occurred: bool
    formula: str


class KinshipDuoResponse(BaseModel):
    relationship: str
    population: str
    theta: float
    evaluated_loci_count: int
    combined_kinship_index: float
    combined_log10_ki: float
    probability_of_paternity_w: float
    enfsi_verbal_scale: str
    locus_results: List[KinshipLocusSchema]
    invariants: Dict[str, Any]


