"""
FORENZA Forensic Toxicology API — Pydantic v2 Schemas.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ToxicologicalAnalyteSchema(BaseModel):
    analyte_name: str = Field(..., examples=["Morphine", "Fentanyl", "Ethanol"])
    matrix_type: str = Field("WHOLE_BLOOD", examples=["WHOLE_BLOOD", "URINE", "VITREOUS_HUMOR"])
    measured_concentration: float = Field(..., ge=0.0, examples=[0.45])
    unit: str = Field("mg/L", examples=["mg/L", "ng/mL", "g/dL"])
    u_cal_rel: Optional[float] = Field(0.03, ge=0.0, le=0.20)
    u_rep_rel: Optional[float] = Field(0.04, ge=0.0, le=0.20)
    u_matrix_rel: Optional[float] = Field(0.02, ge=0.0, le=0.20)


class ToxicologyScreenRequest(BaseModel):
    sample_id: str = Field(..., examples=["TOX-SAMPLE-901"])
    analytes: List[ToxicologicalAnalyteSchema]


class AnalyteReportSchema(BaseModel):
    analyte_name: str
    matrix_type: str
    measured_concentration: float
    expanded_uncertainty_95: float
    concentration_formatted: str
    toxicological_classification: str
    reference_range_description: str


class ToxicologyScreenResponse(BaseModel):
    sample_id: str
    analyte_reports: List[AnalyteReportSchema]
    toxicology_summary: str


class WidmarkBacRequest(BaseModel):
    sample_id: str = Field(..., examples=["BAC-CASE-101"])
    bac_initial_g_per_dl: float = Field(..., ge=0.0, le=1.0, examples=[0.18])
    elapsed_hours: float = Field(..., ge=0.0, examples=[4.0])
    elimination_rate_beta: Optional[float] = Field(0.015, ge=0.005, le=0.040)
    c_cardiac: Optional[float] = Field(None, ge=0.0, examples=[0.22])
    c_peripheral: Optional[float] = Field(None, ge=0.0, examples=[0.18])


class WidmarkBacResponse(BaseModel):
    sample_id: str
    bac_initial_g_per_dl: float
    elapsed_hours: float
    elimination_rate_beta: float
    bac_current_g_per_dl: float
    time_to_sobriety_hours: float
    pmr_ratio: float
    pmr_interpretation: str
    widmark_summary: str
