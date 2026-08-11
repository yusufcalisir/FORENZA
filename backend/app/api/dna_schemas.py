"""
FORENZA Lineage DNA API — Pydantic v2 Schemas.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class YSTRMatchRequest(BaseModel):
    evidence_id: str = Field(..., examples=["Y-EVID-101"])
    suspect_id: str = Field(..., examples=["Y-SUSPECT-202"])
    evidence_markers: Dict[str, float] = Field(..., examples=[{"DYS19": 14.0, "DYS389I": 13.0}])
    suspect_markers: Dict[str, float] = Field(..., examples=[{"DYS19": 14.0, "DYS389I": 13.0}])
    database_count: int = Field(0, ge=0)
    database_size_n: int = Field(2500, ge=100)


class YSTRMatchResponse(BaseModel):
    evidence_id: str
    suspect_id: str
    matching_loci_count: int
    evaluated_loci_count: int
    haplotype_match_status: str
    database_count: int
    database_size_n: int
    haplotype_frequency_estimate: float
    upper_bound_95_ci: float
    paternal_lineage_verdict: str


class MtDnaVariantSchema(BaseModel):
    position: int
    ref_allele: str
    alt_allele: str
    region: str = "HV1"


class MtDnaMatchRequest(BaseModel):
    evidence_id: str
    suspect_id: str
    evidence_variants: List[MtDnaVariantSchema]
    suspect_variants: List[MtDnaVariantSchema]


class MtDnaMatchResponse(BaseModel):
    evidence_id: str
    suspect_id: str
    evidence_rcrs: str
    suspect_rcrs: str
    differing_positions_count: int
    match_status: str
    maternal_lineage_verdict: str
