"""
FORENZA Body Fluid Identification API — Pydantic v2 Schemas.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class MrnaMarkerSchema(BaseModel):
    gene_symbol: str = Field(..., examples=["HBA1", "PRM1", "HTN3"])
    expression_rfu: float = Field(..., ge=0.0, examples=[4500.0])


class StainSampleSchema(BaseModel):
    sample_id: str = Field(..., examples=["FLUID-STAIN-401"])
    mrna_expressions: List[MrnaMarkerSchema]


class FluidIdentifyRequest(BaseModel):
    sample: StainSampleSchema


class BodyFluidProbabilitySchema(BaseModel):
    fluid_type: str
    probability: float
    primary_markers: List[str]


class FluidIdentifyResponse(BaseModel):
    sample_id: str
    top_predicted_fluid: str
    fluid_probabilities: List[BodyFluidProbabilitySchema]
    identification_summary: str


class CoExtractionAuditRequest(BaseModel):
    sample_id: str = Field(..., examples=["COEXT-SAMPLE-801"])
    rna_yield_ng_per_ul: float = Field(..., ge=0.0, examples=[2.5])
    rin_integrity_score: float = Field(..., ge=1.0, le=10.0, examples=[8.2])


class CoExtractionAuditResponse(BaseModel):
    sample_id: str
    rna_yield_ng_per_ul: float
    rin_integrity_score: float
    str_co_extraction_compatible: bool
    recommended_strategy: str
    audit_summary: str
