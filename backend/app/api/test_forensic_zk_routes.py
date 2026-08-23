"""
Integration tests for FastAPI ZK-SNARK Proving Systems & Verifiable Forensic Computation API.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.node.services.forensic.zk.golden_vectors import (
    VECTOR_ZK_CODIS_MATCH_INSTANCE,
    VECTOR_ZK_CODIS_MATCH_WITNESS,
)


@pytest.fixture
def client():
    return TestClient(app)


def test_api_get_zk_catalog(client):
    response = client.get("/api/v1/forensic/zk/catalog")
    assert response.status_code == 200
    data = response.json()
    assert "proving_systems" in data
    assert len(data["proving_systems"]) == 4
    system_ids = [s["id"] for s in data["proving_systems"]]
    assert "GROTH16" in system_ids
    assert "PLONK_KZG" in system_ids


def test_api_get_golden_vectors(client):
    response = client.get("/api/v1/forensic/zk/golden-vectors")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 5
    assert "VECTOR_ZK_CODIS_MATCH" in data["golden_vectors"]


def test_api_synthesize_and_verify_groth16_proof(client):
    # 1. Synthesize Groth16 proof
    synth_payload = {
        "instance": VECTOR_ZK_CODIS_MATCH_INSTANCE.model_dump(),
        "witness": VECTOR_ZK_CODIS_MATCH_WITNESS.model_dump(),
        "proving_system": "GROTH16",
    }
    synth_res = client.post("/api/v1/forensic/zk/synthesize-proof", json=synth_payload)
    assert synth_res.status_code == 200
    synth_data = synth_res.json()
    assert synth_data["status"] == "SUCCESS"
    assert "proof" in synth_data
    assert synth_data["proof"]["proof_size_bytes"] == 128

    # 2. Verify synthesized proof
    verify_payload = {
        "instance": VECTOR_ZK_CODIS_MATCH_INSTANCE.model_dump(),
        "proof_payload": synth_data["proof"],
        "proving_system": "GROTH16",
    }
    verify_res = client.post("/api/v1/forensic/zk/verify-proof", json=verify_payload)
    assert verify_res.status_code == 200
    verify_data = verify_res.json()
    assert verify_data["status"] == "SUCCESS"
    assert verify_data["verification_result"]["is_valid"] is True
    assert verify_data["iso17025_certificate"]["verdict"] == "VERIFIED_MATCH"


def test_api_synthesize_and_verify_plonk_proof(client):
    synth_payload = {
        "instance": VECTOR_ZK_CODIS_MATCH_INSTANCE.model_dump(),
        "witness": VECTOR_ZK_CODIS_MATCH_WITNESS.model_dump(),
        "proving_system": "PLONK_KZG",
    }
    synth_res = client.post("/api/v1/forensic/zk/synthesize-proof", json=synth_payload)
    assert synth_res.status_code == 200
    synth_data = synth_res.json()
    assert synth_data["proof"]["proof_size_bytes"] == 576

    verify_payload = {
        "instance": VECTOR_ZK_CODIS_MATCH_INSTANCE.model_dump(),
        "proof_payload": synth_data["proof"],
        "proving_system": "PLONK_KZG",
    }
    verify_res = client.post("/api/v1/forensic/zk/verify-proof", json=verify_payload)
    assert verify_res.status_code == 200
    verify_data = verify_res.json()
    assert verify_data["verification_result"]["is_valid"] is True


def test_api_verify_ceremony_transcript(client):
    import hashlib
    acc_hash = "0x7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069"
    final_hash = hashlib.sha256(acc_hash.encode("utf-8")).hexdigest()
    transcript_payload = {
        "ceremony_name": "Perpetual Powers of Tau (Hermez)",
        "max_degree": 268435456,
        "participant_count": 1,
        "participants": [
            {
                "participant_id": "Auditor-01",
                "contribution_index": 1,
                "accumulator_hash": acc_hash,
                "dlog_proof_of_knowledge": "0x9b74c9897bac770ffc029102a200c5deac24863e1081addd200126d9069a1122",
                "verified": True,
            }
        ],
        "final_srs_hash": final_hash,
        "is_transcript_valid": True,
    }
    response = client.post("/api/v1/forensic/zk/verify-ceremony-transcript", json=transcript_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True


def test_api_audit_smt_soundness(client):
    response = client.post("/api/v1/forensic/zk/audit-smt-soundness", json={"circuit_name": "Autosomal24STRCircuit"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["soundness_report"]["is_sound"] is True
