"""
FORENZA Ancient DNA & Degraded Forensic SNP Damage / Human ID (HID) — Pydantic v2 Schemas (Module 10).

Covers:
  - MapDamage / Briggs Cytosine Deamination Kinetics
  - Exponential DNA Fragmentation Length Distribution
  - Low-Coverage Forensic SNP Genotype Likelihood (GL)
  - Cumulative Multi-SNP Likelihood Ratio (LR_SNP)
  - Skeletal Remains Degradation Index & LCN Audit
  - Multi-Modal Human Identification Remains Synthesis
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# ── MapDamage Kinetics ───────────────────────────────────────────────────────

class MapDamageRequest(BaseModel):
    delta_0: float = Field(0.25, ge=0.0, le=1.0, description="Terminal 5' C->T deamination probability.", examples=[0.25])
    decay_alpha: float = Field(0.10, ge=0.0, description="Exponential decay rate per base distance.", examples=[0.10])
    max_position: int = Field(25, ge=1, le=100, description="Maximum position from termini to compute curve.", examples=[25])


class MapDamageResponse(BaseModel):
    delta_0: float
    decay_alpha: float
    max_position: int
    damage_curve: Dict[int, float]
    model_description: str


# ── Fragmentation Distribution ────────────────────────────────────────────────

class FragmentationDistributionRequest(BaseModel):
    lambda_param: float = Field(0.025, gt=0.0, description="Exponential rate parameter lambda.", examples=[0.025])
    l_min: float = Field(30.0, ge=0.0, description="Minimum detectable fragment length (bp).", examples=[30.0])


class FragmentationDistributionResponse(BaseModel):
    lambda_param: float
    l_min: float
    mean_length: float
    median_length: float
    cdf_at_100bp: float
    dropout_risk_assessment: str


# ── Low-Coverage SNP Genotype Likelihood ──────────────────────────────────────

class SNPLowCoverageGLRequest(BaseModel):
    locus_id: str = Field(..., description="SNP marker identifier (e.g. 'rs12913832' or 'SNP-HID-01').", examples=["rs12913832"])
    read_bases: List[str] = Field(..., description="Observed base calls across sequenced reads.", examples=[["C", "C", "T", "C"]])
    read_positions: List[int] = Field(..., description="Distance in bp of each read base from 5' terminus (1-indexed).", examples=[[1, 5, 2, 12]])
    ref_allele: str = Field("C", description="Reference allele nucleotide.", examples=["C"])
    alt_allele: str = Field("T", description="Alternative allele nucleotide.", examples=["T"])
    delta_0: float = Field(0.25, ge=0.0, le=1.0, description="Terminal 5' deamination probability.", examples=[0.25])
    decay_alpha: float = Field(0.10, ge=0.0, description="Deamination decay rate.", examples=[0.10])
    sequencing_error_rate: float = Field(0.01, ge=0.0, le=0.20, description="Base sequencing error rate e_r.", examples=[0.01])
    prior_genotypes: Optional[Dict[str, float]] = Field(None, description="Prior genotype probabilities (AA, AB, BB).")


class SNPLowCoverageGLResponse(BaseModel):
    locus_id: str
    ref_allele: str
    alt_allele: str
    read_count: int
    raw_likelihoods: Dict[str, float]
    log10_likelihoods: Dict[str, float]
    posterior_probabilities: Dict[str, float]
    called_genotype: str
    is_damage_compensated: bool
    deamination_risk_flag: bool


# ── Multi-SNP Panel Likelihood Ratio ──────────────────────────────────────────

class SNPObservationInput(BaseModel):
    locus_id: str
    read_bases: List[str]
    read_positions: List[int]
    ref_allele: str = "C"
    alt_allele: str = "T"


class MultiSNPLRRequest(BaseModel):
    snp_observations: List[SNPObservationInput] = Field(..., description="List of assayed low-coverage SNPs.")
    suspect_genotypes: Dict[str, str] = Field(..., description="Suspect/Reference known genotypes per locus.")
    delta_0: float = Field(0.25, ge=0.0, le=1.0)
    sequencing_error_rate: float = Field(0.01, ge=0.0, le=0.20)


class MultiSNPLRResponse(BaseModel):
    total_snps: int
    cumulative_lr: float
    log10_cumulative_lr: float
    per_locus_lr: Dict[str, float]
    prosecutors_fallacy_shield: str


# ── Skeletal Degradation Audit ────────────────────────────────────────────────

class SkeletalDegradationAuditRequest(BaseModel):
    profile_id: str = Field(..., description="Sample profile identifier.", examples=["BONE-SAMPLE-101"])
    small_loci_rfu: float = Field(1200.0, ge=0.0, description="Mean peak height of short amplicons (<150 bp).", examples=[1200.0])
    large_loci_rfu: float = Field(350.0, ge=0.0, description="Mean peak height of long amplicons (>300 bp).", examples=[350.0])
    dna_input_pg: Optional[float] = Field(None, ge=0.0, description="Total DNA template input in picograms (pg).", examples=[85.0])


class SkeletalDegradationAuditResponse(BaseModel):
    profile_id: str
    degradation_index: float
    small_loci_rfu: float
    large_loci_rfu: float
    dna_input_pg: Optional[float]
    is_lcn_sample: bool
    long_amplicon_dropout_risk: str
    recommended_technology: str
    stochastic_warning: Optional[str]


# ── Legacy Compatibility Schemas ──────────────────────────────────────────────

class STRGenotypeSchema(BaseModel):
    locus: Optional[str] = None
    locus_name: Optional[str] = None
    allele1: float
    allele2: float


class STRProfileSchema(BaseModel):
    profile_id: str
    loci: Dict[str, STRGenotypeSchema]
    population_group: Optional[str] = "Caucasian"


class RemainsInputSchema(BaseModel):
    remains_id: str
    sample_type: str = "SKELETAL_BONE"
    str_profile: Optional[STRProfileSchema] = None
    ystr_markers: Optional[Dict[str, float]] = None
    mtdna_variants: Optional[List[str]] = None
    snp_profile: Optional[Dict[str, int]] = None


class LegacyIdentifyRequest(BaseModel):
    remains: RemainsInputSchema
    candidate_db: List[STRProfileSchema]
    prior_probability: float = 0.50
    top_k: int = 5


class MultiModalRemainsRequest(BaseModel):
    remains_id: str
    sample_type: str = "SKELETAL_BONE"
    str_profile: Optional[STRProfileSchema] = None
    ystr_markers: Optional[Dict[str, float]] = None
    mtdna_variants: Optional[List[str]] = None
    snp_profile: Optional[Dict[str, int]] = None
    candidate_db: List[STRProfileSchema]
    prior_probability: float = 0.50
    top_k: int = 5


class HumanIdentificationCandidateHitSchema(BaseModel):
    candidate_id: str
    lr_str: float
    lr_ystr: float
    lr_mtdna: float
    lr_snp: float
    joint_lr: float
    log10_joint_lr: float
    posterior_probability: float
    identification_verdict: str


class MultiModalRemainsResponse(BaseModel):
    remains_id: str
    sample_type: str
    evaluated_candidates_count: int
    top_candidate_hits: List[HumanIdentificationCandidateHitSchema]
    hid_summary: str


class LegacyDegradationAuditRequest(BaseModel):
    profile: STRProfileSchema
    mean_rfu: float = 120.0


class LegacyDegradationAuditResponse(BaseModel):
    profile_id: str
    degradation_index: float
    long_loci_dropout_risk: str
    is_lcn_sample: bool
    stochastic_warning: Optional[str] = None
    recommended_amplification_strategy: str

