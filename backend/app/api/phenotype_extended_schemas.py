"""
FORENZA Extended Phenotyping API — Pydantic v2 Schemas.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PredictExtendedPhenotypeRequest(BaseModel):
    sample_id: str = Field(..., examples=["SAMPLE-EVC-101"])
    snp_dosages: Dict[str, int] = Field(..., examples=[{"rs12913832": 2, "rs1805007": 0, "rs16891982": 2}])
    ancestry_prior: str = Field("EUROPEAN", examples=["EUROPEAN", "AFRICAN", "EAST_ASIAN"])


class UncertaintyIntervalSchema(BaseModel):
    probability: float
    u95_uncertainty: float
    ci_lower: float
    ci_upper: float


class PredictExtendedPhenotypeResponse(BaseModel):
    sample_id: str
    eye_color_probs: Dict[str, UncertaintyIntervalSchema]
    hair_color_probs: Dict[str, UncertaintyIntervalSchema]
    hair_morphology_probs: Dict[str, UncertaintyIntervalSchema]
    skin_tone_probs: Dict[str, UncertaintyIntervalSchema]
    freckling_risk: UncertaintyIntervalSchema
    top_eye_color: str
    top_hair_color: str
    top_hair_morphology: str
    top_skin_tone: str
    biogeographic_ancestry_prior: str
    phenotype_summary: str
