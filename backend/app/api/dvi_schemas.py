"""
FORENZA Interpol DVI (Disaster Victim Identification) API — Pydantic v2 Schemas (Module 09).

Covers:
  - Multi-Omic Joint Likelihood Ratio Computation
  - Interpol DVI 4-Tier Decision Boundaries
  - N x M Cross-Reconciliation Matrix Evaluation
  - Missing Persons Candidate Search & Prioritization
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# ── Joint LR Schemas ─────────────────────────────────────────────────────────

class DviMultiOmicComponentsSchema(BaseModel):
    autosomal_str_lr: float
    ystr_lr: float
    ystr_p_upper: Optional[float]
    has_ystr: bool
    mtdna_lr: float
    mtdna_p_upper: Optional[float]
    has_mtdna: bool
    snp_lr: float
    has_snp: bool


class DviJointLRRequest(BaseModel):
    """
    Request for multi-omic joint likelihood ratio calculation.
    """
    autosomal_lr: float = Field(1.0, ge=0.0, description="Autosomal STR cumulative Likelihood Ratio.", examples=[5200.0])
    ystr_p_upper: Optional[float] = Field(None, ge=0.0, le=1.0, description="Y-STR frequency upper bound (p_upper).", examples=[0.0002])
    mtdna_p_upper: Optional[float] = Field(None, ge=0.0, le=1.0, description="mtDNA frequency upper bound (p_upper).", examples=[0.0001])
    snp_lr: float = Field(1.0, ge=0.0, description="Autosomal SNP Likelihood Ratio.", examples=[1.0])
    has_ystr: bool = Field(False, description="True if male lineage data is available.", examples=[True])
    has_mtdna: bool = Field(False, description="True if maternal lineage data is available.", examples=[True])
    has_snp: bool = Field(False, description="True if SNP panel data is available.", examples=[False])


class DviJointLRResponse(BaseModel):
    joint_lr: float
    log10_joint_lr: float
    decision_tier: str
    components: DviMultiOmicComponentsSchema
    judicial_action: str
    is_definitive_identification: bool
    prosecutors_fallacy_shield: str


# ── N x M Matrix Reconciliation ──────────────────────────────────────────────

class PMRemainInputSchema(BaseModel):
    pm_id: str = Field(..., description="Post-Mortem remain identifier (e.g. 'PM-001').", examples=["PM-001"])
    autosomal_lr_map: Dict[str, float] = Field(default_factory=dict, description="Map of AM family ID to autosomal STR LR.")
    default_autosomal_lr: float = Field(1.0, description="Default autosomal LR if not in map.")
    ystr_p_upper: Optional[float] = Field(None, description="Y-STR p_upper bound for PM remain.")
    mtdna_p_upper: Optional[float] = Field(None, description="mtDNA p_upper bound for PM remain.")
    snp_lr_map: Dict[str, float] = Field(default_factory=dict, description="Map of AM family ID to SNP LR.")


class AMFamilyInputSchema(BaseModel):
    am_id: str = Field(..., description="Ante-Mortem family identifier (e.g. 'AM-FAM-101').", examples=["AM-FAM-101"])
    has_male_reference: bool = Field(False, description="True if male reference is present in family pedigree.")
    has_maternal_reference: bool = Field(False, description="True if maternal reference is present in family pedigree.")
    has_snp_data: bool = Field(False, description="True if family reference has SNP data.")


class DviPairwiseResultSchema(BaseModel):
    pm_profile_id: str
    am_family_id: str
    joint_lr: float
    log10_joint_lr: float
    decision_tier: str
    components: DviMultiOmicComponentsSchema
    judicial_action: str
    is_positive_identification: bool


class DviReconciliationMatrixRequest(BaseModel):
    disaster_event_id: str = Field(..., description="Disaster incident identifier (e.g. 'INCIDENT-FLIGHT-707').", examples=["INCIDENT-FLIGHT-707"])
    pm_remains: List[PMRemainInputSchema] = Field(..., description="List of Post-Mortem human remains.")
    am_families: List[AMFamilyInputSchema] = Field(..., description="List of Ante-Mortem missing person families.")
    threshold_lr: float = Field(1.0e6, ge=1.0, description="Judicial threshold for standalone legal identification (default: 1,000,000).", examples=[1000000.0])


class DviReconciliationMatrixResponse(BaseModel):
    disaster_event_id: str
    total_pm_remains: int
    total_am_families: int
    definitive_identifications_count: int
    probable_matches_count: int
    inconclusive_count: int
    exclusions_count: int
    reconciliation_matrix: List[DviPairwiseResultSchema]
    interpol_summary: str
    prosecutors_fallacy_shield: str


# ── Decision Tiers Reference ──────────────────────────────────────────────────

class InterpolDecisionTierMetadataSchema(BaseModel):
    tier_name: str
    min_lr: float
    max_lr: float
    min_log10: float
    max_log10: float
    judicial_action_criterion: str
    requires_secondary_corroboration: bool
    is_court_admissible_standalone: bool


class InterpolTiersResponse(BaseModel):
    standard: str
    tiers: List[InterpolDecisionTierMetadataSchema]


# ── Legacy Compatibility Schemas ──────────────────────────────────────────────

class STRGenotypeInput(BaseModel):
    locus: str
    allele1: float
    allele2: float


class STRProfileInput(BaseModel):
    profile_id: str
    loci: Dict[str, STRGenotypeInput]
    population_group: Optional[str] = "Caucasian"


class MissingPersonsSearchRequest(BaseModel):
    query_profile: STRProfileInput
    candidate_db: List[STRProfileInput]
    prior_probability: float = 0.50
    top_k: int = 5


class MissingPersonCandidateHit(BaseModel):
    candidate_id: str
    relationship_type: str
    combined_lr: float
    log10_lr: float
    posterior_probability: float
    matching_loci_count: int
    evaluated_loci_count: int
    confidence_tier: str


class MissingPersonsSearchResponse(BaseModel):
    query_id: str
    total_candidates_searched: int
    top_candidate_hits: List[MissingPersonCandidateHit]
    search_summary: str


class DviLegacyPairwiseComparison(BaseModel):
    am_profile_id: str
    pm_profile_id: str
    relationship_hypothesis: str
    lr: float
    log10_lr: float
    identification_status: str


class DviLegacyReconcileRequest(BaseModel):
    disaster_event_id: str
    am_profiles: List[STRProfileInput]
    pm_profiles: List[STRProfileInput]


class DviLegacyReconcileResponse(BaseModel):
    disaster_event_id: str
    total_am_profiles: int
    total_pm_profiles: int
    confirmed_identifications_count: int
    reconciliation_matrix: List[DviLegacyPairwiseComparison]
    dvi_summary: str

