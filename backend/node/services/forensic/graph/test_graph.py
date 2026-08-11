"""
Unit & Integration Tests for FORENZA Forensic Knowledge Graph Package.
Tests node ingestion, directed relation linking, BFS shortest path traversal,
case subgraph extraction, and FastAPI endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.graph.graph_engine import ForensicKnowledgeGraph, GraphNode, GraphEdge
from app.api.graph_routes import router as graph_router

_app = FastAPI()
_app.include_router(graph_router, prefix="/api/v1")
client = TestClient(_app)

graph_engine = ForensicKnowledgeGraph()


# ── Node & Edge Ingestion Tests ──────────────────────────────────────────────

def test_graph_node_and_edge_ingestion():
    c_node = GraphNode("CASE-2026-001", "Case", "Homicide Investigation 001")
    e_node = GraphNode("EVID-STAIN-1", "Evidence", "Bloodstain on Door Handle")
    p_node = GraphNode("PERSON-A", "Person", "Suspect John Doe")

    graph_engine.add_node(c_node)
    graph_engine.add_node(e_node)
    graph_engine.add_node(p_node)

    e1 = GraphEdge("CASE-2026-001", "EVID-STAIN-1", "ASSOCIATED_CASE")
    e2 = GraphEdge("EVID-STAIN-1", "PERSON-A", "DNA_CONTRIBUTOR")

    graph_engine.add_edge(e1)
    graph_engine.add_edge(e2)

    assert "CASE-2026-001" in graph_engine.nodes
    assert len(graph_engine.adjacency["EVID-STAIN-1"]) == 1


def test_shortest_path_traversal():
    res = graph_engine.traverse_shortest_path("CASE-2026-001", "PERSON-A")
    assert res.path_found is True
    assert res.distance == 2
    assert res.path_nodes == ["CASE-2026-001", "EVID-STAIN-1", "PERSON-A"]
    assert res.path_relations == ["ASSOCIATED_CASE", "DNA_CONTRIBUTOR"]


def test_case_subgraph_extraction():
    nodes, edges = graph_engine.extract_case_subgraph("CASE-2026-001")
    assert len(nodes) >= 2
    assert len(edges) >= 1


# ── API Endpoint Integration Tests ───────────────────────────────────────────

def test_api_ingest_case_endpoint():
    payload = {
        "case_id": "CASE-TEST-999",
        "nodes": [
            {"node_id": "CASE-TEST-999", "node_type": "Case", "label": "Test Case"},
            {"node_id": "STAIN-X", "node_type": "Evidence", "label": "Swab Stain"},
            {"node_id": "SUSPECT-Y", "node_type": "Person", "label": "Suspect Y"}
        ],
        "edges": [
            {"source_id": "CASE-TEST-999", "target_id": "STAIN-X", "relation_type": "ASSOCIATED_CASE"},
            {"source_id": "STAIN-X", "target_id": "SUSPECT-Y", "relation_type": "DNA_CONTRIBUTOR"}
        ]
    }

    resp = client.post("/api/v1/forensic/graph/ingest-case", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["nodes_ingested"] == 3
    assert data["edges_ingested"] == 2


def test_api_traverse_path_endpoint():
    payload = {
        "source_id": "CASE-TEST-999",
        "target_id": "SUSPECT-Y"
    }

    resp = client.post("/api/v1/forensic/graph/traverse-path", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["path_found"] is True
    assert data["distance"] == 2


def test_api_subgraph_endpoint():
    resp = client.get("/api/v1/forensic/graph/subgraph/CASE-TEST-999")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["nodes"]) >= 2
