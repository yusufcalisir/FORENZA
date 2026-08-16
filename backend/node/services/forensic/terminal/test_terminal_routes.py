"""
Integration Test Suite for Forensic DNA & SNP Terminal REST API
Tests all 4 endpoints under /api/v1/forensic/terminal/*
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_api_terminal_parse_genemapper_csv():
    csv_payload = """Sample Name,Marker,Allele 1,Allele 2,Height 1,Height 2
CASE_API_01,D3S1358,15,16,1200,1150
CASE_API_01,TH01,9.3,9.3,1800,1800
CASE_API_01,Amelogenin,X,Y,1500,1450
"""
    res = client.post("/api/v1/forensic/terminal/parse", json={"file_content": csv_payload})
    assert res.status_code == 200
    data = res.json()
    assert data["sample_id"] == "CASE_API_01"
    assert data["str_marker_count"] == 3
    assert data["str_profile"]["TH01"]["allele1"] == "9.3"
    assert data["str_profile"]["TH01"]["is_homozygous"] is True
    assert len(data["chain_of_custody_hash"]) == 64


def test_api_terminal_popgen_probability():
    req = {
        "str_profile": {
            "D3S1358": {"allele1": "15", "allele2": "16", "rfu1": 1200, "rfu2": 1150},
            "TH01": {"allele1": "9.3", "allele2": "9.3", "rfu1": 1800, "rfu2": 1800},
            "vWA": {"allele1": "17", "allele2": "18", "rfu1": 1100, "rfu2": 1050}
        },
        "population": "Caucasian",
        "theta": 0.01
    }
    res = client.post("/api/v1/forensic/terminal/popgen-probability", json=req)
    assert res.status_code == 200
    data = res.json()
    assert data["combined_match_probability"] < 0.01
    assert data["log10_lr"] > 2.0
    assert "minimum_allele_freq_pmin" in data


def test_api_terminal_sex_determination_y_null():
    req = {
        "amelogenin_allele1": "X",
        "amelogenin_allele2": None,
        "amelogenin_rfu1": 1850.0,
        "amelogenin_rfu2": 0.0,
        "dys391_signal": "11"
    }
    res = client.post("/api/v1/forensic/terminal/sex-determination", json=req)
    assert res.status_code == 200
    data = res.json()
    assert "AMELY" in data["sex_classification"] or "Yp11.2" in data["sex_classification"]
    assert data["prior_y_null_prob_sas"] == 0.0180


def test_api_terminal_quality_assessment():
    req = {
        "str_profile": {
            "D8S1179": {"allele1": "13", "allele2": "[0]", "rfu1": 842, "rfu2": 0},
            "FGA": {"allele1": "22", "allele2": "24", "rfu1": 100, "rfu2": 95},
            "D21S11": {"allele1": "[0]", "allele2": "[0]", "rfu1": 0, "rfu2": 0}
        }
    }
    res = client.post("/api/v1/forensic/terminal/quality-assessment", json=req)
    assert res.status_code == 200
    data = res.json()
    assert data["degradation_index"] == 8.42
    assert data["degradation_severity"] == "SEVERE"
    assert data["passed_qc"] is False


def test_api_terminal_bga():
    req = {
        "sample_id": "API_BGA_EU",
        "genotype_dosages": {
            "rs12913832": 2,
            "rs16891982": 2,
            "rs1426654": 2,
        }
    }
    res = client.post("/api/v1/forensic/terminal/bga", json=req)
    assert res.status_code == 200
    data = res.json()
    assert data["sample_id"] == "API_BGA_EU"
    assert data["dominant_ancestry"] == "EUR"
    assert data["dominant_probability"] > 0.85
    assert len(data["continental_breakdown"]) == 7


def test_api_terminal_hirisplex():
    req = {
        "sample_id": "API_HIRISPLEX_EU",
        "genotype_dosages": {
            "rs12913832": 2,  # HERC2 A/A
            "rs16891982": 2,  # SLC45A2 C/C
            "rs1426654": 2,   # SLC24A5 A/A
        }
    }
    res = client.post("/api/v1/forensic/terminal/hirisplex", json=req)
    assert res.status_code == 200
    data = res.json()
    assert data["predicted_eye_color"] == "Blue"
    assert data["eye_color_probabilities"]["Blue"] > 0.90
    assert data["predicted_skin_phototype"] in ("Very_Pale_Type_I", "Pale_Type_II")


def test_api_terminal_comprehensive():
    csv_payload = """Sample Name,Marker,Allele 1,Allele 2,Height 1,Height 2
COMP_01,D3S1358,15,16,1250,1180
COMP_01,TH01,9.3,9.3,2100,2100
COMP_01,Amelogenin,X,Y,1500,1450
"""
    req = {
        "file_content": csv_payload,
        "snp_dosages": {
            "rs12913832": 2,
            "rs16891982": 2,
            "rs1426654": 2,
        },
        "population": "Caucasian",
        "theta": 0.01
    }
    res = client.post("/api/v1/forensic/terminal/comprehensive", json=req)
    assert res.status_code == 200
    data = res.json()
    assert data["sample_id"] == "COMP_01"
    assert data["popgen"]["log10_lr"] > 0.0
    assert "Standard Male" in data["sex"]["sex_classification"]
    assert data["qc"]["passed_qc"] is True
    assert data["bga"]["dominant_ancestry"] == "EUR"
    assert data["hirisplex"]["predicted_eye_color"] == "Blue"
