"""
FORENZA Federated Node API — Pydantic v2 Request / Response Schemas.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .forensic_schemas import ProfileInput


class NodeRegistrationRequest(BaseModel):
    """Request body for POST /federated/nodes/register."""
    node_id: str = Field(..., min_length=2, max_length=32, examples=["jandarma-tr"])
    country_code: str = Field(..., min_length=2, max_length=2, examples=["TR"])
    city: str = Field(..., min_length=2, examples=["Ankara"])
    organization: str = Field(..., min_length=2, examples=["Turkish Gendarmerie Forensic Dept"])
    role: str = Field("national_lab", description="orchestrator | national_lab | field_station")
    endpoint_url: str = Field("http://localhost:8101")
    profile_count: int = Field(0, ge=0)
    mtls_cert_fingerprint: Optional[str] = None


class NodeRegistrationResponse(BaseModel):
    registered: bool
    node_id: str
    message: str
    active_nodes_in_network: int


class FederatedSearchRequest(BaseModel):
    """Request body for POST /federated/search."""
    query_profile: ProfileInput
    min_log10_lr_threshold: float = Field(4.0, ge=0.0, le=15.0)
    population: str = Field("Caucasian")


class NodeMatchSchema(BaseModel):
    node_id: str
    country_code: str
    matched_profile_id: Optional[str]
    lr_value: float
    log10_lr: float
    is_inclusion: bool
    zkp_proof_verified: bool
    query_latency_ms: float


class FederatedSearchResponse(BaseModel):
    query_id: str
    target_profile_id: str
    total_nodes_queried: int
    responding_nodes_count: int
    matching_nodes_count: int
    top_lr_value: float
    top_log10_lr: float
    top_matching_node_id: Optional[str]
    node_responses: List[NodeMatchSchema]
    elapsed_seconds: float


class NetworkStatusResponse(BaseModel):
    total_registered_nodes: int
    active_online_nodes: int
    nodes: List[Dict[str, Any]]
