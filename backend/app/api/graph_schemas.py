"""
FORENZA Forensic Knowledge Graph API — Pydantic v2 Schemas.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class GraphNodeSchema(BaseModel):
    node_id: str = Field(..., examples=["PERSON-A", "EVIDENCE-STAIN-101"])
    node_type: str = Field(..., examples=["Person", "Evidence", "Case", "DnaProfile"])
    label: str = Field(..., examples=["Suspect John Doe", "Bloodstain 1"])
    properties: Optional[Dict[str, str]] = Field(default_factory=dict)


class GraphEdgeSchema(BaseModel):
    source_id: str = Field(..., examples=["EVIDENCE-STAIN-101"])
    target_id: str = Field(..., examples=["PERSON-A"])
    relation_type: str = Field(..., examples=["DNA_CONTRIBUTOR", "BIOLOGICAL_PARENT", "COLLECTED_FROM"])
    weight: Optional[float] = Field(1.0, ge=0.0)


class IngestCaseGraphRequest(BaseModel):
    case_id: str = Field(..., examples=["CASE-2026-001"])
    nodes: List[GraphNodeSchema]
    edges: List[GraphEdgeSchema]


class IngestCaseGraphResponse(BaseModel):
    case_id: str
    nodes_ingested: int
    edges_ingested: int
    graph_summary: str


class PathTraversalRequest(BaseModel):
    source_id: str = Field(..., examples=["EVIDENCE-STAIN-101"])
    target_id: str = Field(..., examples=["PERSON-A"])


class PathTraversalResponse(BaseModel):
    source_id: str
    target_id: str
    path_found: bool
    path_nodes: List[str]
    path_relations: List[str]
    distance: int


class SubgraphResponse(BaseModel):
    case_id: str
    nodes: List[GraphNodeSchema]
    edges: List[GraphEdgeSchema]
