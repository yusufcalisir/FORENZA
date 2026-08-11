"""
FORENZA Evidence Image Analysis & BPA API — Pydantic v2 Schemas.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class AnalyzeStainRequest(BaseModel):
    stain_id: str = Field(..., examples=["STAIN-DROP-001"])
    width_mm: float = Field(..., gt=0.0, examples=[5.2])
    length_mm: float = Field(..., gt=0.0, examples=[10.4])


class BloodstainMorphometrySchema(BaseModel):
    stain_id: str
    width_mm: float
    length_mm: float
    ellipse_aspect_ratio: float
    impact_angle_deg: float


class AnalystVerificationSchema(BaseModel):
    analyst_id: str
    verification_timestamp_utc: float
    decision: str
    final_pattern_classification: str
    analyst_notes: str


class AnalyzeStainResponse(BaseModel):
    stain_id: str
    morphometry: BloodstainMorphometrySchema
    predicted_pattern: str
    review_status: str
    verification_record: Optional[AnalystVerificationSchema] = None
    bpa_summary: str


class VerifyAnalystRequest(BaseModel):
    stain_id: str = Field(..., examples=["STAIN-DROP-001"])
    width_mm: float = Field(..., gt=0.0, examples=[5.2])
    length_mm: float = Field(..., gt=0.0, examples=[10.4])
    analyst_id: str = Field(..., examples=["ANALYST-BPA-09"])
    decision: str = Field("VERIFIED_BY_ANALYST", examples=["VERIFIED_BY_ANALYST", "REJECTED"])
    final_pattern: str = Field(..., examples=["HIGH_VELOCITY_SPATTER", "PASSIVE_DROP"])
    analyst_notes: str = Field(..., examples=["Elliptical morphometry verified against high-speed video reference."])
