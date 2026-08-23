"""
Pydantic v2 Schemas for FORENZA Forensic Microbiomics, Thanatometagenomics & Touch Microbial Intelligence.
Complies with ISO/IEC 17025:2017 and ENFSI (2017) Evaluative Reporting Guidelines.
"""

from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class TaxonAbundance(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    taxon_name: str = Field(..., description="Taxon scientific name or ASV identifier")
    phylum: Optional[str] = Field(None, description="Taxon phylum classification")
    relative_abundance: float = Field(..., ge=0.0, le=1.0, description="Relative abundance fraction [0.0, 1.0]")
    raw_read_count: Optional[int] = Field(None, ge=0, description="Raw sequencing read count")


class SampleMicrobiomeProfile(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sample_id: str = Field(..., description="Sample identifier")
    sample_type: Literal["BUCCAL_SWAB", "RECTAL_SWAB", "SKIN_EPINECROTIC", "SOIL_CDI", "TOUCH_TRACE", "BODY_FLUID"]
    taxa: List[TaxonAbundance] = Field(..., min_length=1)
    sequencing_target: Optional[str] = Field("16S_V4", description="16S_V4, 16S_V3_V4, ITS2, or SHOTGUN_MAG")


# --- 1. Thanatomicrobiome & PMI Schemas ---

class ThanatoPmiRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    profile: SampleMicrobiomeProfile
    ambient_temp_celsius: float = Field(20.0, description="Mean ambient crime scene temperature in Celsius")
    base_temp_celsius: float = Field(0.0, description="Base physiological threshold (default 0.0 C)")
    anatomical_locus: Literal["ORAL_BUCCAL", "RECTAL", "SKIN_FACE", "SOIL_CDI"] = "ORAL_BUCCAL"
    regression_model: Literal["RANDOM_FOREST", "ELASTIC_NET"] = "RANDOM_FOREST"


class ConformalInterval(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    lower_bound: float
    upper_bound: float
    coverage_percentage: float = 95.0
    unit: str = "ADD"


class DecompositionStageProbabilities(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    fresh: float
    bloat: float
    active_decay: float
    advanced_decay: float
    skeletonization: float
    dominant_stage: str


class ThanatoPmiResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sample_id: str
    predicted_add: float = Field(..., description="Predicted Accumulated Degree Days (ADD)")
    predicted_adh: float = Field(..., description="Predicted Accumulated Degree Hours (ADH)")
    predicted_pmi_hours: float = Field(..., description="Estimated Post-Mortem Interval in chronological hours")
    predicted_pmi_days: float = Field(..., description="Estimated Post-Mortem Interval in chronological days")
    conformal_add_interval: ConformalInterval
    conformal_hours_interval: ConformalInterval
    decomposition_stage: DecompositionStageProbabilities
    geometric_mean_abundance: float
    clr_coordinates: Dict[str, float]
    indicator_biomarkers: List[str]
    audit_notes: str


# --- 2. Touch Trace & hidSkinPlex+ Schemas ---

class TouchTraceMatchRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    evidentiary_profile: SampleMicrobiomeProfile
    reference_profile: SampleMicrobiomeProfile
    panel_type: Literal["HIDSKINPLEX_PLUS", "16S_SKIN_CLADE"] = "HIDSKINPLEX_PLUS"
    target_substrate: Optional[str] = Field("SMOOTH_SURFACE", description="e.g., STEERING_WHEEL, PHONE, WEAPON_GRIP")
    elapsed_days_post_deposition: float = Field(0.0, ge=0.0, description="Estimated days elapsed since deposition")


class ScoreLrResult(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    aitchison_distance: float
    bray_curtis_dissimilarity: float
    density_given_hp: float
    density_given_hd: float
    raw_likelihood_ratio: float
    calibrated_likelihood_ratio: float
    log10_raw_lr: float
    log10_calibrated_lr: float
    system_cllr: float


class EnfsiReport(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    verbal_predicate_en: str
    verbal_predicate_tr: str
    evidential_tier: str
    prosecutors_fallacy_shield_en: str
    prosecutors_fallacy_shield_tr: str


class TouchTraceMatchResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    evidentiary_sample_id: str
    reference_sample_id: str
    metrics: ScoreLrResult
    enfsi_reporting: EnfsiReport
    shared_informative_snps_count: int
    decay_correction_factor: float
    audit_summary: str


# --- 3. Body Fluid Attribution Schemas ---

class BodyFluidMicrobiomeRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    profile: SampleMicrobiomeProfile
    include_menstrual_differentiation: bool = True


class FluidClassProbabilities(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    saliva: float
    semen: float
    hand_skin: float
    penile_skin: float
    urine: float
    vaginal_fluid: float


class BodyFluidMicrobiomeResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sample_id: str
    raw_probabilities: FluidClassProbabilities
    calibrated_probabilities: FluidClassProbabilities
    predicted_fluid_origin: str
    calibrated_confidence: float
    diagnostic_taxa_found: List[str]
    degradation_indicator_score: float
    is_mixed_stain: bool
    summary: str


# --- 4. Soil CDI & Taphonomy Schemas ---

class SoilCdiTaphonomyRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    soil_profile: SampleMicrobiomeProfile
    control_baseline_profile: Optional[SampleMicrobiomeProfile] = None


class SoilCdiTaphonomyResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sample_id: str
    cdi_perturbation_index: float
    stage_probabilities: DecompositionStageProbabilities
    bacterial_fungal_ratio: float
    saprophytic_taxa_detected: List[str]
    soil_provenance_confidence: float
    summary: str
