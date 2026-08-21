"""
FORENZA Interpol DVI (Disaster Victim Identification) API — Pydantic v2 Schemas (Module 2.4).
Standards Compliance: ISO/IEC 17025:2017, Interpol DVI Guide Section 4 (2018, 2023),
ENFSI Guidelines for Evaluative Reporting in Forensic Science (2017).

Covers:
  - Multi-Omic Joint Likelihood Ratio Computation
  - Interpol DVI 4-Tier Decision Boundaries & Posterior Odds
  - N x M Cross-Reconciliation Matrix Evaluation & Optimal Bipartite Assignment
  - Missing Persons Candidate Search & Pedigree Templates
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


# ── Joint LR Schemas ─────────────────────────────────────────────────────────

class DviMultiOmicComponentsSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    autosomal_str_lr: float
    ystr_lr: float
    ystr_p_upper: Optional[float] = None
    has_ystr: bool
    mtdna_lr: float
    mtdna_p_upper: Optional[float] = None
    has_mtdna: bool
    snp_lr: float
    has_snp: bool


class DviJointLRRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    autosomal_lr: float = Field(1.0, ge=0.0, description="Autosomal STR cumulative Likelihood Ratio.", examples=[5200.0])
    ystr_p_upper: Optional[float] = Field(None, ge=0.0, le=1.0, description="Y-STR frequency upper bound (p_upper).", examples=[0.0002])
    mtdna_p_upper: Optional[float] = Field(None, ge=0.0, le=1.0, description="mtDNA frequency upper bound (p_upper).", examples=[0.0001])
    snp_lr: float = Field(1.0, ge=0.0, description="Autosomal SNP Likelihood Ratio.", examples=[1.0])
    has_ystr: bool = Field(False, description="True if male lineage data is available.", examples=[True])
    has_mtdna: bool = Field(False, description="True if maternal lineage data is available.", examples=[True])
    has_snp: bool = Field(False, description="True if SNP panel data is available.", examples=[False])
    prior_probability: float = Field(0.001, ge=0.000001, le=0.999999, description="Bayesian prior probability of identity (default 0.001).", examples=[0.001])


class DviJointLRResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    joint_lr: float
    log10_joint_lr: float
    decision_tier: str
    components: DviMultiOmicComponentsSchema
    posterior_probability_w: float
    prior_probability: float
    judicial_action: str
    is_definitive_identification: bool
    verbal_predicate_en: str
    verbal_predicate_tr: str
    prosecutors_fallacy_shield: str


# ── N x M Matrix Reconciliation ──────────────────────────────────────────────

class PMRemainInputSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    pm_id: str = Field(..., description="Post-Mortem remain identifier (e.g. 'PM-001').", examples=["PM-001"])
    autosomal_lr_map: Dict[str, float] = Field(default_factory=dict, description="Map of AM family ID to autosomal STR LR.")
    default_autosomal_lr: float = Field(1.0, description="Default autosomal LR if not in map.")
    ystr_p_upper: Optional[float] = Field(None, description="Y-STR p_upper bound for PM remain.")
    mtdna_p_upper: Optional[float] = Field(None, description="mtDNA p_upper bound for PM remain.")
    snp_lr_map: Dict[str, float] = Field(default_factory=dict, description="Map of AM family ID to SNP LR.")


class AMFamilyInputSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    am_id: str = Field(..., description="Ante-Mortem family identifier (e.g. 'AM-FAM-101').", examples=["AM-FAM-101"])
    has_male_reference: bool = Field(False, description="True if male reference is present in family pedigree.")
    has_maternal_reference: bool = Field(False, description="True if maternal reference is present in family pedigree.")
    has_snp_data: bool = Field(False, description="True if family reference has SNP data.")


class DviPairwiseResultSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    pm_profile_id: str
    am_family_id: str
    joint_lr: float
    log10_joint_lr: float
    decision_tier: str
    components: DviMultiOmicComponentsSchema
    judicial_action: str
    is_positive_identification: bool


class DviOptimalAssignmentSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    pm_id: str
    am_id: str
    joint_lr: float
    log10_joint_lr: float
    decision_tier: str


class DviReconciliationMatrixRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    disaster_event_id: str = Field(..., description="Disaster incident identifier (e.g. 'INCIDENT-FLIGHT-707').", examples=["INCIDENT-FLIGHT-707"])
    pm_remains: List[PMRemainInputSchema] = Field(..., description="List of Post-Mortem human remains.")
    am_families: List[AMFamilyInputSchema] = Field(..., description="List of Ante-Mortem missing person families.")
    threshold_lr: float = Field(1.0e6, ge=1.0, description="Judicial threshold for standalone legal identification (default: 1,000,000).", examples=[1000000.0])


class DviReconciliationMatrixResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    disaster_event_id: str
    total_pm_remains: int
    total_am_families: int
    definitive_identifications_count: int
    probable_matches_count: int
    inconclusive_count: int
    exclusions_count: int
    reconciliation_matrix: List[DviPairwiseResultSchema]
    optimal_assignments: List[DviOptimalAssignmentSchema] = Field(default_factory=list)
    interpol_summary: str
    prosecutors_fallacy_shield: str


# ── Decision Tiers & Metadata ────────────────────────────────────────────────

class InterpolDecisionTierMetadataSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    tier: str
    tier_name: Optional[str] = None
    min_lr: float
    max_lr: float
    min_log10: float
    max_log10: float
    judicial_action_criterion: str
    requires_secondary_corroboration: bool
    is_court_admissible_standalone: bool


class InterpolTiersResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    standard: str
    version: str
    tiers: List[InterpolDecisionTierMetadataSchema]


class DviPedigreeTemplateSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    template_id: str
    name: str
    description: str
    required_am_members: List[str]
    expected_min_autosomal_lr: float


class DviCaseworkCohortSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    cohort_id: str
    name: str
    pedigree_type: str
    description: str
    autosomal_lr: float
    ystr_p_upper: float
    mtdna_p_upper: float
    snp_lr: float
    has_ystr: bool
    has_mtdna: bool
    has_snp: bool
    expected_joint_lr: float
    expected_log10_lr: float
    expected_tier: str
    prior_probability: float
    expected_min_w: float
