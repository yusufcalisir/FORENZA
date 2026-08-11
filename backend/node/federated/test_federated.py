"""
Unit & Integration Tests for FORENZA Federated Multi-Node Protocol (Phase 6).
Tests PeerRegistry, NodeIdentity, FederatedQueryOrchestrator, and API endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.node.federated.node_protocol import (
    NodeIdentity, NodeRole, NodeStatus, PeerRegistry
)
from backend.node.federated.orchestrator import FederatedQueryOrchestrator
from backend.node.services.forensic.models import STRGenotype, STRProfile
from backend.app.api.federated_routes import router as federated_router

_app = FastAPI()
_app.include_router(federated_router, prefix="/api/v1")
client = TestClient(_app)


# ── Fixtures ─────────────────────────────────────────────────────────────────

def _sample_query_profile() -> STRProfile:
    return STRProfile(
        profile_id="QUERY_FED_01",
        population_group="Caucasian",
        loci={
            "TH01": STRGenotype("TH01", 6.0, 9.3),
            "FGA":  STRGenotype("FGA", 20.0, 22.0),
            "VWA":  STRGenotype("VWA", 16.0, 18.0),
        }
    )


# ── 6.1 Peer Registry Tests ──────────────────────────────────────────────────

def test_peer_registry_registration():
    reg = PeerRegistry(local_node_id="test_local")
    node = NodeIdentity(
        node_id="interpol-fr", country_code="FR", city="Lyon",
        organization="Interpol DNA Database", profile_count=300
    )
    is_new = reg.register_node(node)
    assert is_new is True
    assert len(reg.get_active_nodes()) == 1
    assert reg.get_node("interpol-fr").status == NodeStatus.ONLINE


def test_peer_registry_heartbeat_timeout():
    reg = PeerRegistry(local_node_id="test_local")
    node = NodeIdentity(
        node_id="stale-node", country_code="XX", city="Nowhere",
        organization="Stale Node", last_heartbeat_timestamp=0.0  # 1970 timestamp
    )
    reg.register_node(node)
    # Re-force stale timestamp
    reg.get_node("stale-node").last_heartbeat_timestamp = 0.0

    active = reg.get_active_nodes()
    assert len(active) == 0
    assert reg.get_node("stale-node").status == NodeStatus.OFFLINE


# ── 6.2 Federated Query Orchestrator Tests ───────────────────────────────────

def test_federated_orchestrator_query():
    reg = PeerRegistry(local_node_id="orchestrator")
    reg.register_node(NodeIdentity(
        node_id="node-a", country_code="TR", city="Ankara",
        organization="Node A", profile_count=100
    ))
    reg.register_node(NodeIdentity(
        node_id="node-b", country_code="DE", city="Berlin",
        organization="Node B", profile_count=150
    ))

    orch = FederatedQueryOrchestrator(registry=reg, default_theta=0.01)
    res = orch.execute_federated_search(_sample_query_profile(), min_log10_lr_threshold=2.0)

    assert res.total_nodes_queried == 2
    assert res.responding_nodes_count == 2
    assert res.matching_nodes_count == 2
    assert res.top_lr_value > 1.0
    assert len(res.node_responses) == 2


# ── 6.3 API Endpoint Integration Tests ───────────────────────────────────────

def test_api_federated_status():
    resp = client.get("/api/v1/federated/nodes/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_registered_nodes" in data
    assert "active_online_nodes" in data
    assert data["total_registered_nodes"] >= 3  # Pre-seeded default nodes


def test_api_federated_node_register():
    payload = {
        "node_id": "npa-jp",
        "country_code": "JP",
        "city": "Tokyo",
        "organization": "National Police Agency Japan",
        "role": "national_lab",
        "endpoint_url": "http://localhost:8103",
        "profile_count": 500
    }
    resp = client.post("/api/v1/federated/nodes/register", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["registered"] is True
    assert data["node_id"] == "npa-jp"


def test_api_federated_search():
    payload = {
        "query_profile": {
            "profile_id": "TARGET_PROB_01",
            "population_group": "Caucasian",
            "loci": [
                {"locus": "TH01", "allele1": 6.0, "allele2": 9.3},
                {"locus": "FGA", "allele1": 20.0, "allele2": 22.0},
                {"locus": "VWA", "allele1": 16.0, "allele2": 18.0}
            ]
        },
        "min_log10_lr_threshold": 2.0,
        "population": "Caucasian"
    }
    resp = client.post("/api/v1/federated/search", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "query_id" in data
    assert data["total_nodes_queried"] >= 3
    assert data["matching_nodes_count"] >= 1
    assert data["top_lr_value"] > 1.0
