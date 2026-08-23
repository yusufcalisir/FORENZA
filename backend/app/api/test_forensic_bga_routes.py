"""
Integration Tests for Forensic BGA & HIrisPlex-S FastAPI REST Endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from backend.app.api.forensic_bga_routes import router as bga_router

app = FastAPI()
app.include_router(bga_router)
client = TestClient(app)


def test_api_panels_endpoint():
    """Verify GET /api/forensic/bga/panels returns registered AIM panels."""
    response = client.get("/api/forensic/bga/panels")
    assert response.status_code == 200
    data = response.json()
    assert "panels" in data
    assert len(data["panels"]) >= 4


def test_api_reference_systems_endpoint():
    """Verify GET /api/forensic/bga/reference-systems returns gnomAD and 1000G panels."""
    response = client.get("/api/forensic/bga/reference-systems")
    assert response.status_code == 200
    data = response.json()
    assert "reference_systems" in data
    assert any("gnomAD" in r["name"] for r in data["reference_systems"])


def test_api_golden_vectors_endpoint():
    """Verify GET /api/forensic/bga/golden-vectors returns certified standard vectors."""
    response = client.get("/api/forensic/bga/golden-vectors")
    assert response.status_code == 200
    data = response.json()
    assert len(data["vectors"]) == 5


def test_api_ingest_endpoint():
    """Verify POST /api/forensic/bga/ingest parses raw 23andMe microarray file."""
    raw_23andme = """# 23andMe raw data
# rsid\tchromosome\tposition\tgenotype
rs2814778\t1\t159174683\tTT
rs1426654\t15\t48426484\tGG
rs16891982\t5\t33984570\tGG
rs12913832\t15\t28365618\tGG
"""
    response = client.post("/api/forensic/bga/ingest", json={
        "raw_text": raw_23andme,
        "sample_id": "TEST_API_SAMPLE"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["sample_id"] == "TEST_API_SAMPLE"
    assert data["called_loci_count"] == 4


def test_api_analyze_pipeline_international():
    """Verify POST /api/forensic/bga/analyze executes full multi-omic assessment."""
    raw_ceu = """rs2814778\tT\tT
rs1426654\tG\tG
rs16891982\tG\tG
rs12913832\tG\tG
"""
    response = client.post("/api/forensic/bga/analyze", json={
        "raw_text": raw_ceu,
        "sample_id": "API_CEU_TEST",
        "jurisdiction": "ISFG_INTERNATIONAL"
    })
    assert response.status_code == 200
    data = response.json()
    assert "ancestry_analysis" in data
    assert "phenotype_prediction" in data
    assert data["ancestry_analysis"]["top_assigned_population"] == "EUR"
    assert data["phenotype_prediction"]["eye_color"]["predicted_category"] == "Blue"


def test_api_analyze_pipeline_germany_stpo():
    """Verify POST /api/forensic/bga/analyze enforces German §81e StPO ancestry redaction."""
    raw_ceu = """rs2814778\tT\tT
rs1426654\tG\tG
rs16891982\tG\tG
rs12913832\tG\tG
"""
    response = client.post("/api/forensic/bga/analyze", json={
        "raw_text": raw_ceu,
        "sample_id": "API_GERMAN_TEST",
        "jurisdiction": "GERMANY_STPO"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["governance"]["ancestry_redacted"] is True
    assert data["ancestry_analysis"]["superpop_proportions"] == {}
    assert "[REDACTED - § 81e (2) StPO]" in data["ancestry_analysis"]["enfsi_verbal_statement"]
    # Phenotype is preserved
    assert data["phenotype_prediction"]["eye_color"]["predicted_category"] == "Blue"
