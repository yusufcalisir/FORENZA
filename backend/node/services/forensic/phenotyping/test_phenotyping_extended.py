"""
Unit & Integration Tests for FORENZA Extended Phenotyping Package.
Tests HIrisPlex-S EVC predictions (Eye, Hair, Hair Morphology, Skin Tone, Freckling),
biogeographic ancestry calibration, ISO 17025 U_95% measurement uncertainty, and API endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.phenotyping.phenotype_engine import AdvancedPhenotypeEngine
from app.api.phenotype_routes import router as phenotype_router

_app = FastAPI()
_app.include_router(phenotype_router, prefix="/api/v1")
client = TestClient(_app)

adv_engine = AdvancedPhenotypeEngine()


# ── Phenotype Prediction & Uncertainty Tests ────────────────────────────────

def test_blue_eye_blond_hair_extended_phenotype():
    dosages = {"rs12913832": 2, "rs1805007": 0, "rs16891982": 2}
    res = adv_engine.predict_extended_phenotype("SAMPLE-BLUE-1", dosages, ancestry_prior="EUROPEAN")

    assert res.top_eye_color == "Blue"
    assert res.eye_color_probs["Blue"].probability > 0.80
    assert res.eye_color_probs["Blue"].u95_uncertainty > 0.0
    assert res.top_hair_color == "Blond"
    assert res.top_skin_tone == "Very Pale"


def test_red_hair_freckles_extended_phenotype():
    dosages = {"rs12913832": 0, "rs1805007": 1, "rs16891982": 1}
    res = adv_engine.predict_extended_phenotype("SAMPLE-RED-2", dosages, ancestry_prior="EUROPEAN")

    assert res.top_hair_color == "Red"
    assert res.freckling_risk.probability >= 0.80
    assert res.freckling_risk.ci_lower < res.freckling_risk.probability < res.freckling_risk.ci_upper


# ── API Endpoint Integration Tests ───────────────────────────────────────────

def test_api_predict_extended_phenotype_endpoint():
    payload = {
        "sample_id": "SAMPLE-EVC-101",
        "snp_dosages": {"rs12913832": 2, "rs1805007": 0, "rs16891982": 2},
        "ancestry_prior": "EUROPEAN"
    }

    resp = client.post("/api/v1/forensic/phenotype/predict-extended", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["sample_id"] == "SAMPLE-EVC-101"
    assert data["top_eye_color"] == "Blue"
    assert data["freckling_risk"]["u95_uncertainty"] > 0.0
