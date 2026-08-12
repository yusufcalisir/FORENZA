from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class SubmitReviewRequest(BaseModel):
    sample_id: str = Field(default="SAMPLE-DNA-01")
    ai_recommendation: str = Field(default="INCLUSION (LR = 10^26)")
    human_decision: str = Field(default="APPROVE_AI_PREDICATE", description="APPROVE_AI_PREDICATE, OVERRIDE_MODIFIED_PREDICATE, REJECT_RE_ANALYSIS")
    primary_analyst_id: str = Field(default="ANALYST-01")
    technical_reviewer_id: str = Field(default="PEER-REVIEWER-02")
    override_reason: Optional[str] = Field(default=None, description="Required if human_decision is OVERRIDE_MODIFIED_PREDICATE")
    final_verdict: Optional[str] = Field(default=None)


class SubmitReviewResponse(BaseModel):
    review_id: str
    sample_id: str
    ai_recommendation: str
    human_decision: str
    is_override: bool
    override_reason: Optional[str]
    final_verdict: str
    primary_analyst_id: str
    technical_reviewer_id: str
    dual_sign_off_verified: bool
    timestamp: str
    court_admissibility_status: str
    hmac_signature: str


class GetReviewAuditResponse(BaseModel):
    sample_id: str
    total_reviews: int
    chain_intact: bool
    review_history: List[SubmitReviewResponse]
    legal_provenance: str
