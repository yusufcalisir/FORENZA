"""
FastAPI Integration Tests for Forensic Epigenetic Clocks & Multimodal PMI API Endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_api_get_clock_catalog():
    """Verify GET /api/v1/forensic/epigenetics/clocks/catalog endpoint."""
    response = client.get("/api/v1/forensic/epigenetics/clocks/catalog")
    assert response.status_code == 200
    data = response.json()
    assert data["clock_count"] >= 6
    assert "horvath_2013" in data["clocks"]
    assert "visage_enhanced" in data["clocks"]
    assert "grimage" in data["clocks"]


def test_api_get_tissue_offsets():
    """Verify GET /api/v1/forensic/epigenetics/clocks/tissue-offsets endpoint."""
    response = client.get("/api/v1/forensic/epigenetics/clocks/tissue-offsets")
    assert response.status_code == 200
    data = response.json()
    offsets = data["offsets"]
    assert offsets["SEMEN"]["baseline_offset_years"] == 18.60
    assert offsets["WHOLE_BLOOD"]["baseline_offset_years"] == 0.00
    assert offsets["SALIVA_BUCCAL"]["baseline_offset_years"] == 2.45


def test_api_get_golden_vectors():
    """Verify GET /api/v1/forensic/epigenetics/clocks/golden-vectors endpoint."""
    response = client.get("/api/v1/forensic/epigenetics/clocks/golden-vectors")
    assert response.status_code == 200
    data = response.json()
    assert "VECTOR_NIST_2391D_A" in data["vectors"]
    assert "VECTOR_NA12878_CEU" in data["vectors"]


def test_api_estimate_chronological_age():
    """Verify POST /api/v1/forensic/epigenetics/clocks/estimate-age endpoint."""
    payload = {
        "sample": {
            "sample_id": "TEST_CASE_API_01",
            "tissue_type": "WHOLE_BLOOD",
            "platform": "ILLUMINA_EPIC",
            "input_dna_pg": 500.0,
            "beta_values": {
                "cg16867657": 0.380,
                "cg24724428": 0.400,
                "cg21572722": 0.340,
                "cg06639320": 0.300,
                "cg16419235": 0.230,
                "cg04523812": 0.270,
                "cg07955995": 0.210,
                "cg02228185": 0.410,
                "cg17861230": 0.310,
                "cg02085975": 0.560,
                "cg09809672": 0.360,
                "cg05575921": 0.810,
            },
        },
        "selected_clocks": ["horvath_2013", "visage_enhanced", "visage_basic"],
        "chronological_age_known": 38.0,
        "jurisdiction": "GERMANY_STPO",
    }

    response = client.post("/api/v1/forensic/epigenetics/clocks/estimate-age", json=payload)
    if response.status_code != 200:
        print("ESTIMATE AGE ERROR RESPONSE:", response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["sample_id"] == "TEST_CASE_API_01"
    assert len(data["clock_results"]) == 3
    assert "judicial_report" in data
    assert "81e" in data["judicial_report"]["statutory_compliance_status"]


def test_api_biological_aging():
    """Verify POST /api/v1/forensic/epigenetics/clocks/biological-aging endpoint."""
    payload = {
        "sample_id": "TEST_BIO_SAMPLE",
        "tissue_type": "WHOLE_BLOOD",
        "beta_values": {
            "cg05575921": 0.480,  # Smoker AHRR
            "cg16867657": 0.450,
            "cg06639320": 0.380,
            "cg07955995": 0.280,
        },
    }

    response = client.post(
        "/api/v1/forensic/epigenetics/clocks/biological-aging?chronological_age=50.0&smoking_pack_years=25.0&biological_sex=MALE",
        json=payload,
    )
    assert response.status_code == 200
    data = response.json()
    assert "phenoage" in data
    assert "grimage" in data
    assert "dunedin_pace" in data
    assert data["grimage"]["surrogate_biomarkers"]["DNAm_PACKYRS"] > 20.0


def test_api_multimodal_pmi():
    """Verify POST /api/v1/forensic/epigenetics/clocks/multimodal-pmi endpoint."""
    payload = {
        "sample_id": "CASE_API_PMI",
        "rectal_temp_celsius": 26.5,
        "ambient_temp_celsius": 17.0,
        "body_mass_kg": 75.0,
        "clothing_factor": 1.0,
        "vitreous_potassium_mmol_l": 9.2,
        "accumulated_degree_days": 12.0,
    }

    response = client.post("/api/v1/forensic/epigenetics/clocks/multimodal-pmi", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["estimated_pmi_hours"] > 12.0
    assert data["epigenetic_5mc_stability_status"] == "STABLE_ARREST"
    assert len(data["modalities_used"]) == 3
