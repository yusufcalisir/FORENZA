from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class GenerateCourtTestimonyRequest(BaseModel):
    case_id: str = Field(default="CASE-2026-COURT-01")
    sample_id: str = Field(default="SAMPLE-DNA-101")
    expert_witness_id: str = Field(default="EXPERT-01 (Dr. Sarah Connor)")
    log10_lr: float = Field(default=26.0)
    enfsi_verbal_predicate: str = Field(default="EXTREMELY_STRONG_SUPPORT_FOR_INCLUSION")
    total_loci: int = Field(default=24)
    fst_correction: float = Field(default=0.01)
    stochastic_threshold: float = Field(default=150.0)


class TestimonyPillar(BaseModel):
    title: str
    summary: str
    details: str
    fallacy_protection_active: Optional[bool] = None


class GenerateCourtTestimonyResponse(BaseModel):
    testimony_title: str
    case_id: str
    sample_id: str
    expert_witness_id: str
    timestamp: str
    operating_mode: str
    testimony_pillars: List[TestimonyPillar]
    prosecutors_fallacy_shield: str
    testimony_hmac_hash: str
    court_admissible: bool
