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


# ── Cryptographic Merkle Tree Ledger Schemas (Pillar 6 §1) ───────────────────

class CustodyEventInput(BaseModel):
    event_id: str = Field(..., description="Unique event identifier (e.g. EVT-001).")
    timestamp_iso: str = Field(..., description="RFC 3161 / ISO 8601 UTC timestamp string.")
    officer_id: str = Field(..., description="Forensic officer / technician identifier.")
    sample_barcode: str = Field(..., description="Evidence sample barcode.")
    location_id: str = Field(..., description="Physical or laboratory custody location.")
    action_type: str = Field(default="TRANSFER", description="Custodial action type (COLLECTION, TRANSFER, EXTRACTION, COURT_PRESENTATION).")
    notes: Optional[str] = Field(default=None, description="Optional custodial observation notes.")


class MerkleBuildTreeRequest(BaseModel):
    events: List[CustodyEventInput] = Field(
        ...,
        min_length=1,
        description="Sequential list of custody transfer events."
    )


class MerkleBuildTreeResponse(BaseModel):
    merkle_root: str
    total_events: int
    tree_depth: int
    leaf_hashes: List[str]
    layers: List[List[str]]


class MerkleGenerateProofRequest(BaseModel):
    events: List[CustodyEventInput] = Field(
        ...,
        min_length=1,
        description="Sequential list of custody events."
    )
    target_event_index: int = Field(
        ...,
        ge=0,
        description="0-indexed position of target event in sequence."
    )


class MerkleProofStep(BaseModel):
    sibling_hash: str
    direction: str


class MerkleGenerateProofResponse(BaseModel):
    target_event_id: str
    target_event_index: int
    target_leaf_hash: str
    merkle_root: str
    proof_path: List[MerkleProofStep]
    path_length: int


class MerkleVerifyProofRequest(BaseModel):
    leaf_hash: str = Field(..., description="Target leaf hash computed from questioned custody event.")
    proof_path: List[MerkleProofStep] = Field(..., description="O(log2 N) Merkle sibling proof path.")
    expected_root: str = Field(..., description="Expected immutable Merkle root commitment.")


class MerkleVerifyProofResponse(BaseModel):
    is_valid: bool
    computed_root: str
    expected_root: str
    verdict: str
    steps_evaluated: int
    step_trace: List[str]
    prosecutors_fallacy_shield: str

