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
    f2rl3_beta: Optional[float] = Field(
        default=None,
        description="Optional methylation beta value at F2RL3 locus cg03636183 [0.0, 1.0]."
    )
    alppl2_beta: Optional[float] = Field(
        default=None,
        description="Optional methylation beta value at ALPPL2 locus cg01940273 [0.0, 1.0]."
    )
    abcg1_beta: Optional[float] = Field(
        default=None,
        description="Optional methylation beta value at ABCG1 locus cg06500161 [0.0, 1.0]."
    )
    cpt1a_beta: Optional[float] = Field(
        default=None,
        description="Optional methylation beta value at CPT1A locus cg00574958 [0.0, 1.0]."
    )
    srebf1_beta: Optional[float] = Field(
        default=None,
        description="Optional methylation beta value at SREBF1 locus cg11024682 [0.0, 1.0]."
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
    chronological_age: Optional[float] = Field(
        default=None,
        description="Optional known chronological age of target subject for acceleration delta calculation."
    )
    estimated_dnam_age: Optional[float] = Field(
        default=None,
        description="Optional estimated DNA methylation age for acceleration delta calculation."
    )


class LifestyleProfileResponse(BaseModel):
    ahrr_methylation_beta: float
    f2rl3_methylation_beta: Optional[float] = None
    alppl2_methylation_beta: Optional[float] = None
    smoking_score: Optional[float] = None
    smoking_status: str
    smoking_probability: float
    estimated_pack_years: float
    abcg1_methylation_beta: Optional[float] = None
    cpt1a_methylation_beta: Optional[float] = None
    srebf1_methylation_beta: Optional[float] = None
    estimated_bmi: Optional[float] = None
    bmi_category: Optional[str] = None
    alcohol_index_score: float
    alcohol_exposure_level: str
    circadian_phase: str
    estimated_tod_window: str
    age_acceleration_delta: Optional[float] = None
    aging_status: Optional[str] = None
    prosecutors_fallacy_shield: Optional[str] = None


class TelomerePmiRequest(BaseModel):
    ts_ratio: Optional[float] = Field(
        default=None,
        description="Relative Telomere Length (T/S ratio = 2^-ddCt)."
    )
    delta_delta_ct: Optional[float] = Field(
        default=None,
        description="Optional Delta Delta Ct value for telomere estimation."
    )
    observed_pmi_beta: Optional[float] = Field(
        default=None,
        description="Residual CpG methylation beta value for Post-Mortem Interval calculation."
    )
    ambient_temperature_celsius: float = Field(
        default=20.0,
        description="Ambient environmental temperature in Celsius for ADH thermal summation."
    )
    tissue1_betas: Optional[Dict[str, float]] = Field(
        default=None,
        description="CpG beta profile for tissue 1 (for somatic mosaicism comparison)."
    )
    tissue2_betas: Optional[Dict[str, float]] = Field(
        default=None,
        description="CpG beta profile for tissue 2 (for somatic mosaicism comparison)."
    )


class TelomerePmiResponse(BaseModel):
    telomere: Optional[Dict[str, Any]] = None
    pmi: Optional[Dict[str, Any]] = None
    mosaicism: Optional[Dict[str, Any]] = None
    prosecutors_fallacy_shield: str


class BisulfiteQcRequest(BaseModel):
    non_cpg_signals: Optional[List[Dict[str, float]]] = Field(
        default=None,
        description="List of non-CpG control cytosine probe signals with 'methylated' and 'unmethylated' intensities."
    )
    probes: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="List of probe dictionaries with 'probe_id', 'raw_beta', 'detection_p_value', 'probe_design_type'."
    )


class BisulfiteQcResponse(BaseModel):
    bisulfite_conversion_qc: Optional[Dict[str, Any]] = None
    probe_calibration: Optional[Dict[str, Any]] = None
    prosecutors_fallacy_shield: str



