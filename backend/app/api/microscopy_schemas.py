"""
FORENZA Microscopy Intelligence API — Pydantic v2 Schemas.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ClassifyCellRequest(BaseModel):
    cell_id: str = Field(..., examples=["SPERM-CELL-01"])
    head_length_um: float = Field(..., gt=0.0, examples=[4.5])
    head_width_um: float = Field(..., gt=0.0, examples=[2.8])
    acrosome_coverage_pct: float = Field(..., ge=0.0, le=100.0, examples=[55.0])


class ClassifyCellResponse(BaseModel):
    cell_id: str
    cell_type: str
    head_length_um: float
    head_width_um: float
    acrosome_coverage_pct: float
    normal_morphology: bool


class HairMorphologyRequest(BaseModel):
    hair_id: str = Field(..., examples=["HAIR-SAMPLE-501"])
    hair_diameter_um: float = Field(..., gt=0.0, examples=[80.0])
    medulla_diameter_um: float = Field(..., ge=0.0, examples=[18.0])
    root_status: str = Field(..., examples=["ANAGEN_WITH_SHEATH", "TELOGEN_NO_SHEATH"])


class HairMorphologyResponse(BaseModel):
    hair_id: str
    hair_diameter_um: float
    medulla_diameter_um: float
    medullary_index: float
    species_origin: str
    root_status: str
    dna_routing: str
    microscopy_summary: str
