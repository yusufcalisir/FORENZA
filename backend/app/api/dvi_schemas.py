"""
FORENZA DVI & Missing Persons API — Pydantic v2 Schemas.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class STRGenotypeSchema(BaseModel):
    locus: str
    allele1: float
    allele2: Optional[float] = None


class STRProfileSchema(BaseModel):
    profile_id: str
    loci: Dict[str, STRGenotypeSchema]
    population_group: str = "Caucasian"


class MissingPersonSearchRequest(BaseModel):
    query_profile: STRProfileSchema
    candidate_db: List[STRProfileSchema]
    prior_probability: float = Field(0.50, ge=0.01, le=0.99)
    top_k: int = Field(5, ge=1, le=50)


class CandidateHitSchema(BaseModel):
    candidate_id: str
    relationship_type: str
    combined_lr: float
    log10_lr: float
    posterior_probability: float
    matching_loci_count: int
    evaluated_loci_count: int
    confidence_tier: str


class MissingPersonSearchResponse(BaseModel):
    query_id: str
    total_candidates_searched: int
    top_candidate_hits: List[CandidateHitSchema]
    search_summary: str


class DviReconcileRequest(BaseModel):
    disaster_event_id: str = Field(..., examples=["DVI-EVENT-TURKEY-2026"])
    am_profiles: List[STRProfileSchema]
    pm_profiles: List[STRProfileSchema]


class DviPairwiseSchema(BaseModel):
    am_profile_id: str
    pm_profile_id: str
    relationship_hypothesis: str
    lr: float
    log10_lr: float
    identification_status: str


class DviReconcileResponse(BaseModel):
    disaster_event_id: str
    total_am_profiles: int
    total_pm_profiles: int
    confirmed_identifications_count: int
    reconciliation_matrix: List[DviPairwiseSchema]
    dvi_summary: str
