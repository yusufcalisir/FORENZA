"""
FORENZA Forensic Reports API — Pydantic v2 Schemas.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .forensic_schemas import ProfileInput


class ReportGenerateRequest(BaseModel):
    """Request body for POST /reports/generate."""
    evidence_id: str = Field(..., examples=["EVID-2026-001"])
    suspect_id: str = Field(..., examples=["SUSPECT-9941"])
    lr_value: float = Field(..., ge=0.0, examples=[482109.34])
    log10_lr: float = Field(..., examples=[5.6831])
    population: str = Field("Caucasian")
    phenotype_summary: Optional[Dict[str, Any]] = None
    zkp_verified: bool = True
    zkp_tx_hash: Optional[str] = None


class HpdBoundsSchema(BaseModel):
    low: float
    high: float


class ZkpProofSchema(BaseModel):
    verified: bool
    tx_hash: str


class ComplianceStatusSchema(BaseModel):
    swgdam_passed: bool
    iso17025_accredited: bool


class ReportGenerateResponse(BaseModel):
    report_id: str
    created_timestamp: float
    formatted_date: str
    evidence_id: str
    suspect_id: str
    population: str
    match_status: str
    lr_value: float
    log10_lr: float
    hpd_interval_95: HpdBoundsSchema
    enfsi_verbal_scale: str
    phenotype_summary: Dict[str, Any]
    zkp_proof: ZkpProofSchema
    compliance: ComplianceStatusSchema
    disclaimer: str


class AuditRequest(BaseModel):
    """Request body for POST /reports/audit."""
    profile: ProfileInput
    theta_applied: float = Field(0.01, ge=0.0, le=0.10)
    has_zkp_proof: bool = True


class CheckItemSchema(BaseModel):
    rule_id: str
    rule_name: str
    passed: bool
    details: str


class AuditResponse(BaseModel):
    profile_id: str
    total_checks: int
    passed_checks: int
    compliance_score: float
    iso17025_status: str
    checks: List[CheckItemSchema]
    warnings: List[str]
