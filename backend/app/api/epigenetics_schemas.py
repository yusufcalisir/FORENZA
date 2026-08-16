from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class PredictAgeRequest(BaseModel):
    cpg_methylation: Dict[str, float] = Field(
        default={
            "ELOVL2": 0.45,
            "FHL2": 0.35,
            "TRIM59": 0.25,
            "KLF14": 0.60,
            "MIR29B2CHG": 0.30
        },
        description="Dictionary mapping CpG locus names to methylation beta values in [0.0, 1.0]."
    )
    tissue_type: str = Field(
        default="BLOOD",
        description="Biological tissue type: BLOOD, BUCCAL, SALIVA, BONE, TEETH, TISSUE."
    )
    chronological_age_known: Optional[float] = Field(
        default=None,
        description="Optional known chronological age of target subject for acceleration delta calculation."
    )


class CpgContributionDetail(BaseModel):
    locus: str
    gene: Optional[str] = None
    methylation_beta: float
    weight: float
    contribution_years: float


class PredictAgeResponse(BaseModel):
    estimated_age_years: float
    model_age_before_offset: Optional[float] = None
    linear_predictor_x: Optional[float] = None
    developmental_stage: Optional[str] = None
    prediction_interval_lower: float
    prediction_interval_upper: float
    standard_error_years: float
    expanded_uncertainty_95: float
    tissue_type: str
    tissue_offset_applied: float
    age_acceleration_delta: Optional[float] = None
    aging_status: str
    cpg_locus_contributions: List[CpgContributionDetail]
    model_provenance: str
    prosecutors_fallacy_shield: Optional[str] = None



class DeconvolveTissueRequest(BaseModel):
    tdmr_methylation: Dict[str, float] = Field(
        default={
            "tDMR_BLOOD_01": 0.88,
            "tDMR_BUCCAL_01": 0.12,
            "tDMR_SALIVA_01": 0.15,
            "tDMR_SEMEN_01": 0.05,
            "tDMR_EPITHELIAL_01": 0.10,
            "tDMR_BONE_01": 0.08
        },
        description="Dictionary mapping tDMR locus names to methylation beta values in [0.0, 1.0]."
    )


class DeconvolveTissueResponse(BaseModel):
    top_predicted_tissue: str
    top_tissue_probability: float
    tissue_probabilities: Dict[str, float]
    log_likelihoods: Optional[Dict[str, float]] = None
    lr_tissue: float
    log10_lr_tissue: float
    tdmr_loci_evaluated: int
    deconvolution_method: str
    prosecutors_fallacy_shield: Optional[str] = None



class LifestyleProfileRequest(BaseModel):
    ahrr_cg05575921_beta: float = Field(
        default=0.85,
        description="Methylation beta value at AHRR locus cg05575921 [0.0, 1.0]."
    )
    slc6a3_beta: Optional[float] = Field(
        default=0.50,
        description="Optional methylation beta value at SLC6A3 [0.0, 1.0]."
    )
    per2_beta: Optional[float] = Field(
        default=0.40,
        description="Optional methylation beta value at PER2 [0.0, 1.0]."
    )
    bmal1_beta: Optional[float] = Field(
        default=0.60,
        description="Optional methylation beta value at BMAL1 [0.0, 1.0]."
    )


class LifestyleProfileResponse(BaseModel):
    ahrr_methylation_beta: float
    smoking_status: str
    smoking_probability: float
    estimated_pack_years: float
    alcohol_index_score: float
    alcohol_exposure_level: str
    circadian_phase: str
    estimated_tod_window: str
    biomarker_panel: str
