from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class CompileIsoReportRequest(BaseModel):
    case_id: str = Field(default="CASE-2026-LIMS-01")
    sample_id: str = Field(default="SAMPLE-DNA-101")
    investigator_name: str = Field(default="Dr. Sarah Connor")
    primary_analyst_id: str = Field(default="ANALYST-01 (Dr. Sarah Connor)")
    technical_reviewer_id: str = Field(default="PEER-REVIEWER-02 (Dr. James Vance)")
    likelihood_ratio: float = Field(default=1.0e26)
    log10_lr: float = Field(default=26.0)
    enfsi_verbal_predicate: str = Field(default="EXTREMELY_STRONG_SUPPORT_FOR_INCLUSION")
    qc_verdict: str = Field(default="QC_PASSED")
    human_decision: str = Field(default="APPROVE_AI_PREDICATE")
    override_reason: Optional[str] = Field(default=None)


class CompileIsoReportResponse(BaseModel):
    certificate_title: str
    case_summary: Dict[str, Any]
    evidence_chain: Dict[str, Any]
    methods: Dict[str, Any]
    empirical_results: Dict[str, Any]
    statistical_interpretation: Dict[str, Any]
    limitations_and_uncertainty: Dict[str, Any]
    dual_sign_off_governance: Dict[str, Any]
    audit_trail_and_cryptography: Dict[str, Any]
    court_admissibility_certified: bool
