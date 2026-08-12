from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class GetSystemArchitectureResponse(BaseModel):
    platform_name: str
    platform_version: str
    architecture_type: str
    total_subsystems: int
    layers: List[Dict[str, Any]]
    system_status: str
    compliance_standards: List[str]


class RunUnifiedOsPipelineRequest(BaseModel):
    case_id: str = Field(default="CASE-2026-OS-01")
    sample_id: str = Field(default="SAMPLE-DNA-101")
    primary_analyst: str = Field(default="ANALYST-01 (Dr. Sarah Connor)")
    technical_reviewer: str = Field(default="PEER-REVIEWER-02 (Dr. James Vance)")


class RunUnifiedOsPipelineResponse(BaseModel):
    pipeline_id: str
    case_id: str
    sample_id: str
    execution_timestamp: str
    unified_pipeline_status: str
    execution_layers: Dict[str, Any]
    master_os_hmac_hash: str
