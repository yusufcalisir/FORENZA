"""
FORENZA Crime Scene Biological Evidence Management API — Pydantic v2 Schemas.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class RegisterEvidenceRequest(BaseModel):
    evidence_id: str = Field(..., examples=["EVID-BLOOD-001"])
    crime_scene_id: str = Field(..., examples=["SCENE-2026-001"])
    evidence_type: str = Field(..., examples=["Bloodstain", "Hair", "Saliva", "TouchDNA", "Tissue", "Bone", "Insect", "PlantMaterial"])
    collection_method: str = Field(..., examples=["Swab", "Tape Lift", "Excision", "Forceps"])
    collector_id: str = Field(..., examples=["INV-SMITH-44"])
    preservation_condition: str = Field("Dry Ambient", examples=["Dry Ambient", "Frozen -20C"])
    container_seal_code: str = Field(..., examples=["SEAL-987654"])
    spatial_coordinates: Dict[str, float] = Field(..., examples=[{"x": 2.4, "y": 1.8, "z": 0.5}])


class CustodyTransferRecordSchema(BaseModel):
    transfer_id: str
    sender_id: str
    receiver_id: str
    timestamp_utc: float
    transfer_reason: str
    previous_hash: str
    current_hash: str


class RegisterEvidenceResponse(BaseModel):
    evidence_id: str
    crime_scene_id: str
    evidence_type: str
    container_seal_code: str
    genesis_hash: str
    registration_summary: str


class TransferCustodyRequest(BaseModel):
    evidence_id: str = Field(..., examples=["EVID-BLOOD-001"])
    sender_id: str = Field(..., examples=["INV-SMITH-44"])
    receiver_id: str = Field(..., examples=["LAB-TECH-JONES"])
    transfer_reason: str = Field(..., examples=["Transfer to DNA Extraction Lab"])


class TransferCustodyResponse(BaseModel):
    evidence_id: str
    transfer_id: str
    sender_id: str
    receiver_id: str
    current_hash: str
    transfer_summary: str


class AuditChainResponse(BaseModel):
    evidence_id: str
    chain_intact: bool
    total_transfers: int
    latest_custodian: str
    audit_summary: str
