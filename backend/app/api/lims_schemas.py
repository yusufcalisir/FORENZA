from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class CreateCaseRequest(BaseModel):
    case_id: str = Field(default="CASE-2026-LIMS-01", description="Unique Case Tracking Identifier")
    investigator_name: str = Field(default="Dr. Sarah Connor", description="Lead Forensic Investigator Name")
    jurisdiction: str = Field(default="INTERPOL_MEMBER_STATE", description="Legal Jurisdiction")


class CreateCaseResponse(BaseModel):
    case_id: str
    investigator_name: str
    jurisdiction: str
    created_timestamp: str
    status: str
    associated_sample_ids: List[str]


class AccessionSampleRequest(BaseModel):
    case_id: str = Field(default="CASE-2026-LIMS-01")
    sample_id: str = Field(default="SAMPLE-DNA-101")
    evidence_type: str = Field(default="Blood Stain")
    collector_name: str = Field(default="Tech John")


class AccessionSampleResponse(BaseModel):
    sample_id: str
    case_id: str
    evidence_type: str
    collector_name: str
    accession_timestamp: str
    current_step: str
    current_step_index: int
    qc_status: str


class RecordWorkflowStepRequest(BaseModel):
    sample_id: str = Field(default="SAMPLE-DNA-101")
    step_name: str = Field(default="DNA_EXTRACTION")
    operator_id: str = Field(default="OP-042")
    instrument_id: str = Field(default="QIAGEN_EZ1_01")
    reagent_lot: str = Field(default="LOT-EXT-994")
    protocol_version: str = Field(default="ISO-SOP-EXT-v2.1")
    step_result: str = Field(default="Extracted 150 uL DNA solution")
    pass_qc: bool = Field(default=True)


class StepEntryDetail(BaseModel):
    step_name: str
    step_index: int
    operator: str
    instrument_id: str
    reagent_lot: str
    protocol_version: str
    timestamp: str
    step_result: str
    pass_qc: Optional[bool] = True
    hmac_signature: str


class RecordWorkflowStepResponse(BaseModel):
    step_name: str
    step_index: int
    operator: str
    instrument_id: str
    reagent_lot: str
    protocol_version: str
    timestamp: str
    step_result: str
    pass_qc: bool
    hmac_signature: str


class ChainOfCustodyResponse(BaseModel):
    sample_id: str
    case_id: str
    current_step: str
    total_steps_completed: int
    chain_intact: bool
    audit_trail: List[StepEntryDetail]
