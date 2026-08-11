"""
FORENZA Human Identification API — Pydantic v2 Schemas.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from .dvi_schemas import STRProfileSchema


class MultiModalRemainsSchema(BaseModel):
    remains_id: str = Field(..., examples=["UNKNOWN-REMAINS-BONE-101"])
    sample_type: str = Field("SKELETAL_BONE", examples=["SKELETAL_BONE", "DEGRADED_TISSUE"])
    str_profile: Optional[STRProfileSchema] = None
    ystr_markers: Optional[Dict[str, float]] = None
    mtdna_variants: Optional[List[str]] = None
    snp_profile: Optional[Dict[str, int]] = None


class HumanIdentifyRequest(BaseModel):
    remains: MultiModalRemainsSchema
    candidate_db: List[STRProfileSchema]
    prior_probability: float = Field(0.50, ge=0.01, le=0.99)
    top_k: int = Field(5, ge=1, le=50)


class HumanCandidateHitSchema(BaseModel):
    candidate_id: str
    lr_str: float
    lr_ystr: float
    lr_mtdna: float
    lr_snp: float
    joint_lr: float
    log10_joint_lr: float
    posterior_probability: float
    identification_verdict: str


class HumanIdentifyResponse(BaseModel):
    remains_id: str
    sample_type: str
    evaluated_candidates_count: int
    top_candidate_hits: List[HumanCandidateHitSchema]
    hid_summary: str


class DegradationAuditRequest(BaseModel):
    profile: STRProfileSchema
    mean_rfu: float = Field(120.0, ge=10.0, le=10000.0)


class DegradationAuditResponse(BaseModel):
    profile_id: str
    degradation_index: float
    long_loci_dropout_risk: str
    is_lcn_sample: bool
    stochastic_warning: Optional[str]
    recommended_amplification_strategy: str
