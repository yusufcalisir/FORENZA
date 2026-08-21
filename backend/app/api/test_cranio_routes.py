"""
Integration tests for Craniofacial Morphometrics REST API Routes (Module 3.3).
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_reconstruct_craniofacial_api():
    payload = {
        "snp_dosages": {
            "rs974448": 1,
            "rs12882923": 0,
            "rs11130635": 2,
            "rs13289": 0,
            "rs7559252": 1,
        },
        "sex": "FEMALE",
        "age_years": 35.0,
    }
    response = client.post("/api/v1/forensic/phenotyping/craniofacial/reconstruct", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "landmarks" in data
    assert "indices" in data
    assert data["assayed_loci_count"] == 5
    assert data["validation_status"] == "VERIFIED"
    assert "LEPTORRHINE" in data["indices"]["nasal_typology"]


def test_procrustes_superposition_api():
    mat1 = [[0.0, 10.0, 20.0], [5.0, 15.0, 25.0], [-5.0, 15.0, 25.0]]
    mat2 = [[0.0, 10.0, 20.0], [5.0, 15.0, 25.0], [-5.0, 15.0, 25.0]]
    payload = {
        "landmarks_target": mat1,
        "landmarks_source": mat2,
    }
    response = client.post("/api/v1/forensic/phenotyping/craniofacial/superposition", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["rmsd_mm"] < 1e-4
    assert len(data["rotation_matrix"]) == 3


def test_standards_api():
    response = client.get("/api/v1/forensic/phenotyping/craniofacial/standards")
    assert response.status_code == 200
    data = response.json()
    assert "standards" in data
    assert len(data["standards"]) == 5


def test_cross_validation_api():
    response = client.get("/api/v1/forensic/phenotyping/craniofacial/cross-validation")
    assert response.status_code == 200
    data = response.json()
    assert data["is_concordant"] is True


def test_reporting_shield_api():
    response = client.get("/api/v1/forensic/phenotyping/craniofacial/reporting-shield")
    assert response.status_code == 200
    data = response.json()
    assert "ENFSI" in data["legal_framework"]
