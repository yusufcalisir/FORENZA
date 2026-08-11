"""
FORENZA Forensic Entomology API — Pydantic v2 Schemas.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class EntomologyPmiRequest(BaseModel):
    species_name: str = Field("Calliphora vicina", examples=["Calliphora vicina", "Lucilia sericata"])
    development_stage: str = Field("INSTAR_3", examples=["INSTAR_1", "INSTAR_2", "INSTAR_3", "PUPA"])
    mean_ambient_temp_celsius: float = Field(18.5, ge=-10.0, le=50.0, examples=[18.5])


class EntomologyPmiResponse(BaseModel):
    species_name: str
    development_stage: str
    mean_ambient_temp_celsius: float
    effective_temp_celsius: float
    required_adh: float
    estimated_pmi_hours: float
    estimated_pmi_days: float
    pmi_formatted_range: str
    entomology_summary: str


class ArthropodOccurrenceSchema(BaseModel):
    family_name: str = Field(..., examples=["Calliphoridae"])
    species_observed: str = Field(..., examples=["Calliphora vicina"])
    abundance_score: str = Field("HIGH", examples=["HIGH", "MODERATE"])


class SuccessionAuditRequest(BaseModel):
    sample_id: str = Field(..., examples=["ENTO-CASE-301"])
    occurrences: List[ArthropodOccurrenceSchema]


class SuccessionAuditResponse(BaseModel):
    sample_id: str
    inferred_decomposition_stage: str
    typical_timeframe_days: str
    observed_families: List[str]
    succession_summary: str
