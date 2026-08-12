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
    methylation_beta: float
    weight: float
    contribution_years: float


class PredictAgeResponse(BaseModel):
    estimated_age_years: float
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
