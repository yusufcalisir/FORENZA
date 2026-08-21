"""
FORENZA Y-STR Haplotype Forensics API — Pydantic v2 Schemas (Module 2.1).
Standards Compliance: ISO/IEC 17025:2017, SWGDAM Lineage Guidelines (2020), ENFSI Evaluative Reporting (2017).
Research Source: research/pillar_2_lineage_kinship_research.md & research/ystr_27_mtdna_empop_lineage_research.md
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, ConfigDict


# ── 1. Match & Kinship Evaluation Schemas ────────────────────────────────────

class PaternalKinshipRequest(BaseModel):
    """Request for full 27-locus Y-FILER Plus paternal lineage kinship evaluation."""
    model_config = ConfigDict(protected_namespaces=())

    evidence_id: str = Field("EVIDENCE-YSTR-01", description="Evidence sample identifier.")
    suspect_id: str = Field("SUSPECT-YSTR-01", description="Suspect/Reference sample identifier.")
    evidence_markers: Dict[str, Any] = Field(
        ...,
        description="Evidence Y-STR allele map (e.g. {'DYS19': 14, 'DYS385a/b': [11, 14], ...}).",
        examples=[{"DYS19": 14, "DYS389I": 13, "DYS389II": 29, "DYS390": 24, "DYS385a/b": [11, 14]}],
    )
    suspect_markers: Dict[str, Any] = Field(
        ...,
        description="Suspect/Reference Y-STR allele map.",
        examples=[{"DYS19": 14, "DYS389I": 13, "DYS389II": 29, "DYS390": 24, "DYS385a/b": [11, 14]}],
    )
    meioses_m: int = Field(1, ge=1, le=10, description="Number of father-to-son meioses separating individuals.")
    database_size_n: int = Field(385000, ge=100, description="YHRD reference database size N.")
    theta: float = Field(0.03, ge=0.0, le=0.20, description="Brenner subpopulation coancestry theta.")


class LocusKinshipDetailSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    allele_a: Any
    allele_b: Any
    is_match: bool
    transition_probability: float
    is_rm: bool
    mutation_rate: float


class PaternalKinshipResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    evidence_id: str
    suspect_id: str
    meioses_m: int
    total_loci_evaluated: int
    matching_loci_count: int
    mutated_loci_count: int
    rm_mutations_count: int
    standard_mutations_count: int
    transition_probability_product: float
    haplotype_p_upper: float
    paternal_lr: float
    log10_paternal_lr: float
    is_lineage_excluded: bool
    locus_evaluations: Dict[str, LocusKinshipDetailSchema]
    verbal_predicate_en: str
    verbal_predicate_tr: str
    patrilineal_disclaimer_en: str
    patrilineal_disclaimer_tr: str


# ── 2. Population Frequency & Confidence Bounds ─────────────────────────────

class ClopperPearsonRequest(BaseModel):
    """Request for exact Clopper-Pearson 95% binomial upper confidence bound."""
    model_config = ConfigDict(protected_namespaces=())

    observed_count_k: int = Field(0, ge=0, description="Observed haplotype matches in database (k).")
    database_size_n: int = Field(385000, ge=1, description="Database size (N).")
    alpha: float = Field(0.05, gt=0.0, lt=1.0, description="Significance level (default 0.05 for 95% CI).")


class ClopperPearsonResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    database_size_n: int
    observed_matches_k: int
    alpha: float
    point_estimate: float
    p_upper_bound: float
    p_upper: float = 0.0
    p_lower: float = 0.0
    lr_upper_bound: float = 0.0
    log10_lr_upper_bound: float = 0.0
    equivalent_match_ratio: float = 0.0
    method: str


class BrennerFrequencyRequest(BaseModel):
    """Request for Brenner / Surveyor subpopulation coancestry correction."""
    model_config = ConfigDict(protected_namespaces=())

    observed_count_k: int = Field(0, ge=0, description="Observed haplotype matches (k).")
    database_size_n: int = Field(385000, ge=1, description="Database size (N).")
    theta: float = Field(0.03, ge=0.0, le=0.20, description="Coancestry coefficient theta (Fst).")


class BrennerFrequencyResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    observed_count_k: int
    database_size_n: int
    theta: float
    p_brenner: float
    lr_brenner: float = 0.0
    log10_lr_brenner: float = 0.0
    equivalent_match_ratio: float = 0.0


# ── 3. Haplogroup Prediction ────────────────────────────────────────────────

class HaplogroupPredictionRequest(BaseModel):
    """Request for Bayesian Y-DNA haplogroup prediction from 27-locus vector."""
    model_config = ConfigDict(protected_namespaces=())

    y_str_markers: Dict[str, Any] = Field(
        ...,
        description="27-locus Y-STR profile dictionary.",
        examples=[{"DYS19": 14, "DYS389I": 13, "DYS389II": 29, "DYS390": 24, "DYS393": 13}],
    )


class HaplogroupPredictionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    predicted_haplogroup: str
    confidence_score: float
    primary_snp_marker: str
    distance_to_modal: float
    description: str
    bayesian_posteriors: Dict[str, float]


# ── 4. Decoupling & Mixture Helpers ─────────────────────────────────────────

class DecoupleDys389Request(BaseModel):
    """Request to decouple nested repeat system DYS389."""
    model_config = ConfigDict(protected_namespaces=())

    dys389i: float = Field(..., ge=8.0, le=20.0, description="Nested DYS389I repeat count.")
    dys389ii_total: float = Field(..., ge=20.0, le=40.0, description="Total DYS389II amplicon repeat count.")


class DecoupleDys389Response(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    dys389i: float
    dys389ii_total: float
    dys389_2_pure: float
    explanation: str


class MixtureContributorsRequest(BaseModel):
    """Request to estimate minimum male contributors from multi-allele mixture."""
    model_config = ConfigDict(protected_namespaces=())

    locus_allele_counts: Optional[Dict[str, int]] = Field(
        None,
        description="Observed peak/allele counts per locus.",
        examples=[{"DYS19": 2, "DYS389I": 2, "DYS385a/b": 3, "DYF387S1a/b": 4}],
    )
    locus_alleles: Optional[Dict[str, List[float]]] = Field(
        None,
        description="Observed allele lists per locus.",
        examples=[{"DYS19": [14.0, 15.0], "DYS389I": [13.0, 14.0, 15.0]}],
    )


class MixtureContributorsResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    minimum_male_contributors: int
    multi_copy_locus_flag: bool = False
    locus_allele_counts: Dict[str, int] = Field(default_factory=dict)
    methodology: str = ""


# ── 5. SMM & Legacy Match Schemas ───────────────────────────────────────────

class SMMTransitionRequest(BaseModel):
    """Request to compute SMM paternity transmission probability."""
    model_config = ConfigDict(protected_namespaces=())

    father_allele: float
    son_allele: float
    locus_name: str
    p_step: float = 0.10
    mutation_rate: Optional[float] = None


class SMMTransitionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    locus_name: str
    father_allele: float
    son_allele: float
    step_distance_m: int
    is_mutation: bool
    mutation_rate: float
    transition_probability: float
    log10_transition_probability: float
    mutation_classification: str


class YSTRMatchRequest(BaseModel):
    """Request for Y-STR paternal match evaluation."""
    model_config = ConfigDict(protected_namespaces=())

    evidence_id: str = "EVID-01"
    suspect_id: str = "SUSP-01"
    evidence_markers: Dict[str, Any]
    suspect_markers: Dict[str, Any]
    database_count_k: int = 0
    database_size_n: int = 25000
    theta: float = 0.03
    alpha: float = 0.05


class YSTRMatchResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    evidence_id: str
    suspect_id: str
    match_status: str
    matching_loci_count: int
    total_evaluated_loci: int
    mismatch_loci_count: int
    database_count_k: int
    database_size_n: int
    theta: float
    clopper_pearson: Dict[str, Any]
    brenner: Optional[Dict[str, Any]] = None
    brenner_correction: Optional[Dict[str, Any]] = None
    smm_mutations: List[Dict[str, Any]] = Field(default_factory=list)
    paternal_lineage_verdict: str
    prosecutors_fallacy_shield: str


# ── 6. Reference Catalogs & Cohorts ─────────────────────────────────────────

class YStrLocusMetadataSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    locus_name: str
    cytogenetic_band: str
    grch38_start: int
    grch38_end: int
    repeat_unit_bp: int
    canonical_motif: str
    ce_dye: str
    amplicon_min_bp: int
    amplicon_max_bp: int
    mutation_rate: float
    stepwise_param_r: float
    mutation_class: str
    is_rapidly_mutating: bool
    is_multi_copy: bool


class PanelMetadataResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    total_loci: int = 27
    rapidly_mutating_loci_count: int = 7
    standard_loci_count: int = 20
    loci: List[YStrLocusMetadataSchema] = Field(default_factory=list)


class YhrdMetapopulationSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    code: str
    name: str
    database_size_n: int
    default_theta: float
    description: str
    primary_modal_haplogroups: List[str]


class GoldStandardIndividualSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    sample_id: str
    coriell_id: str
    nist_srm_designation: Optional[str]
    sex: str
    population_group: str
    certified_haplogroup: str
    primary_snp: str
    description: str
    y_str_haplotype: Dict[str, Any]


class CaseworkCohortSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    cohort_id: str
    name: str
    description: str
    meioses_m: int
    expected_outcome: str
    expected_matching_loci: int
    expected_mutation_count: int
    expected_min_lr: float
    profile_a: Dict[str, Any]
    profile_b: Dict[str, Any]

