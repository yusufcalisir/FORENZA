"""
FORENZA Forensic Knowledge Graph API Router.
Exposes endpoints for Case Ingestion, Shortest Path Traversal, and Subgraph Extraction
under the /forensic/graph prefix.
"""

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.graph.graph_engine import ForensicKnowledgeGraph, GraphNode, GraphEdge
from .graph_schemas import (
    IngestCaseGraphRequest, IngestCaseGraphResponse,
    PathTraversalRequest, PathTraversalResponse,
    SubgraphResponse, GraphNodeSchema, GraphEdgeSchema
)

router = APIRouter(prefix="/forensic/graph", tags=["Forensic Knowledge Graph"])

_global_graph = ForensicKnowledgeGraph()


@router.post(
    "/ingest-case",
    response_model=IngestCaseGraphResponse,
    summary="Ingest Forensic Case Knowledge Graph",
    description="Ingests nodes and directed relational edges into the in-memory Forensic Knowledge Graph.",
    status_code=status.HTTP_200_OK,
)
async def ingest_case_graph(body: IngestCaseGraphRequest) -> IngestCaseGraphResponse:
    try:
        for n in body.nodes:
            _global_graph.add_node(GraphNode(
                node_id=n.node_id,
                node_type=n.node_type,
                label=n.label,
                properties=n.properties or {}
            ))

        for e in body.edges:
            _global_graph.add_edge(GraphEdge(
                source_id=e.source_id,
                target_id=e.target_id,
                relation_type=e.relation_type,
                weight=e.weight if e.weight is not None else 1.0
            ))

        summary = f"Case Graph Ingested for {body.case_id}: {len(body.nodes)} nodes, {len(body.edges)} edges added."
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Graph ingestion failed: {str(exc)}"
        )

    return IngestCaseGraphResponse(
        case_id=body.case_id,
        nodes_ingested=len(body.nodes),
        edges_ingested=len(body.edges),
        graph_summary=summary
    )


@router.post(
    "/traverse-path",
    response_model=PathTraversalResponse,
    summary="Traverse Shortest Relational Path",
    description="Finds shortest relational path between evidence stains and target person/scene entities.",
    status_code=status.HTTP_200_OK,
)
async def traverse_path(body: PathTraversalRequest) -> PathTraversalResponse:
    res = _global_graph.traverse_shortest_path(body.source_id, body.target_id)
    return PathTraversalResponse(
        source_id=res.source_id,
        target_id=res.target_id,
        path_found=res.path_found,
        path_nodes=res.path_nodes,
        path_relations=res.path_relations,
        distance=res.distance
    )


@router.get(
    "/subgraph/{case_id}",
    response_model=SubgraphResponse,
    summary="Retrieve Case Subgraph",
    description="Returns all nodes and edges connected to a specified case ID.",
    status_code=status.HTTP_200_OK,
)
async def get_case_subgraph(case_id: str) -> SubgraphResponse:
    nodes, edges = _global_graph.extract_case_subgraph(case_id)
    return SubgraphResponse(
        case_id=case_id,
        nodes=[
            GraphNodeSchema(
                node_id=n.node_id,
                node_type=n.node_type,
                label=n.label,
                properties=n.properties
            )
            for n in nodes
        ],
        edges=[
            GraphEdgeSchema(
                source_id=e.source_id,
                target_id=e.target_id,
                relation_type=e.relation_type,
                weight=e.weight
            )
            for e in edges
        ]
    )
