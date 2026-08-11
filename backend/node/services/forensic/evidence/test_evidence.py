"""
Unit & Integration Tests for FORENZA Crime Scene Biological Evidence Management Package.
Tests evidence registration, spatial coordinates, custody transfer, SHA-256 chain audit, and API endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.evidence.manager import BiologicalEvidenceManager
from app.api.evidence_routes import router as evidence_router

_app = FastAPI()
_app.include_router(evidence_router, prefix="/api/v1")
client = TestClient(_app)

evidence_manager = BiologicalEvidenceManager()


# ── Evidence Registration & Custody Tests ────────────────────────────────────

def test_evidence_registration_and_genesis_hash():
    item = evidence_manager.register_evidence(
        evidence_id="EVID-BLOOD-101",
        crime_scene_id="SCENE-2026-001",
        evidence_type="Bloodstain",
        collection_method="Swab",
        collector_id="INV-DOE-12",
        preservation_condition="Dry Ambient",
        container_seal_code="SEAL-112233",
        spatial_coordinates={"x": 1.5, "y": 2.2, "z": 0.4}
    )

    assert item.evidence_id == "EVID-BLOOD-101"
    assert len(item.chain_of_custody_history) == 1
    assert item.chain_of_custody_history[0].previous_hash == "GENESIS_BLOCK"


def test_custody_transfer_and_hash_chain():
    rec = evidence_manager.transfer_custody(
        evidence_id="EVID-BLOOD-101",
        sender_id="INV-DOE-12",
        receiver_id="LAB-DNA-EXTRACTION",
        transfer_reason="Lysis and DNA Isolation"
    )

    assert rec.transfer_id == "TR-2"
    assert rec.sender_id == "INV-DOE-12"
    assert rec.receiver_id == "LAB-DNA-EXTRACTION"


def test_chain_of_custody_audit_integrity():
    audit = evidence_manager.audit_chain_of_custody("EVID-BLOOD-101")
    assert audit.chain_intact is True
    assert audit.total_transfers == 2
    assert audit.latest_custodian == "LAB-DNA-EXTRACTION"


# ── API Endpoint Integration Tests ───────────────────────────────────────────

def test_api_register_evidence_endpoint():
    payload = {
        "evidence_id": "EVID-HAIR-901",
        "crime_scene_id": "SCENE-2026-002",
        "evidence_type": "Hair",
        "collection_method": "Forceps",
        "collector_id": "INV-SMITH-44",
        "preservation_condition": "Dry Ambient",
        "container_seal_code": "SEAL-998877",
        "spatial_coordinates": {"lat": 52.3676, "lon": 4.9041}
    }

    resp = client.post("/api/v1/forensic/evidence/register", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["evidence_id"] == "EVID-HAIR-901"
    assert data["container_seal_code"] == "SEAL-998877"


def test_api_transfer_custody_endpoint():
    payload = {
        "evidence_id": "EVID-HAIR-901",
        "sender_id": "INV-SMITH-44",
        "receiver_id": "EVIDENCE-LOCKER-A",
        "transfer_reason": "Overnight Secured Storage"
    }

    resp = client.post("/api/v1/forensic/evidence/transfer-custody", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["receiver_id"] == "EVIDENCE-LOCKER-A"


def test_api_audit_chain_endpoint():
    resp = client.get("/api/v1/forensic/evidence/audit-chain/EVID-HAIR-901")
    assert resp.status_code == 200
    data = resp.json()
    assert data["chain_intact"] is True
    assert data["total_transfers"] == 2
