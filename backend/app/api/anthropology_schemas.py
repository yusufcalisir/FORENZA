"""
FORENZA Forensic Anthropology API — Pydantic v2 Schemas.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class MorphometricsSchema(BaseModel):
    femur_length_mm: Optional[float] = Field(None, ge=100.0, le=700.0, examples=[445.0])
    tibia_length_mm: Optional[float] = Field(None, ge=100.0, le=600.0, examples=[365.0])
    pelvic_notch_score: Optional[int] = Field(None, ge=1, le=5, examples=[1])
    subpubic_angle_deg: Optional[float] = Field(None, ge=40.0, le=140.0, examples=[95.0])
    pubic_symphysis_phase: Optional[int] = Field(None, ge=1, le=6, examples=[3])
    cranial_breadth_mm: Optional[float] = Field(None, ge=80.0, le=220.0, examples=[140.0])
    cranial_length_mm: Optional[float] = Field(None, ge=100.0, le=250.0, examples=[185.0])


class BiologicalProfileRequest(BaseModel):
    measurements: MorphometricsSchema


class BiologicalProfileResponse(BaseModel):
    estimated_sex: str
    sex_confidence: float
    estimated_age_range: str
    estimated_stature_cm: float
    stature_margin_error_cm: float
    stature_range_formatted: str
    population_affinity: str
    anthropology_summary: str


class TraumaObservationSchema(BaseModel):
    element_name: str = Field(..., examples=["Left Femur"])
    trauma_mechanism: str = Field(..., examples=["BLUNT_FORCE"])
    trauma_timing: str = Field(..., examples=["PERIMORTEM"])
    description: str = Field(..., examples=["Radiating linear fracture on distal shaft"])


class TraumaAuditRequest(BaseModel):
    sample_id: str = Field(..., examples=["SKEL-SAMPLE-901"])
    element_name: str = Field(..., examples=["Left Femur"])
    observations: List[TraumaObservationSchema]


class TraumaAuditResponse(BaseModel):
    sample_id: str
    element_classified: str
    total_observations_count: int
    has_perimortem_trauma: bool
    observations: List[TraumaObservationSchema]
    trauma_summary: str
