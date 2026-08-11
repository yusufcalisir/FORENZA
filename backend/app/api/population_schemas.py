"""
FORENZA Population Genetics API — Pydantic v2 Schemas.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class FrequencyBoundRequest(BaseModel):
    """Request body for POST /population/frequency."""
    locus: str = Field(..., examples=["TH01"])
    allele: float = Field(..., examples=[9.3])
    raw_frequency: float = Field(..., ge=0.0, le=1.0, examples=[0.001])
    observed_count: int = Field(0, ge=0)
    database_n: Optional[int] = Field(500, ge=10)


class FrequencyBoundResponse(BaseModel):
    locus: str
    allele: float
    observed_count: int
    raw_frequency: float
    bounded_frequency: float
    was_bounded: bool
    rarity_index: float
    explanation: str


class FstDistanceRequest(BaseModel):
    """Request body for POST /population/fst."""
    population1: str = Field(..., examples=["Caucasian"])
    population2: str = Field(..., examples=["AfricanAmerican"])


class FstDistanceResponse(BaseModel):
    population_pair: List[str]
    fst_value: float
    genetic_distance_neis: float
    locus_fst_breakdown: Dict[str, float]
    recommendation: str


class PopulationListResponse(BaseModel):
    supported_populations: List[str]
    default_database_n: int
    nrc2_recommendation: str
