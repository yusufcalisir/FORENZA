"""
Integration Tests for FORENZA HIrisPlex-S REST API Endpoints (Module 3.1).
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.hirisplex_routes import router as hirisplex_router

app = FastAPI()
app.include_router(hirisplex_router, prefix="/api/v1")
client = TestClient(app)


class TestHIrisPlexApiEndpoints:
    """Tests all HIrisPlex-S HTTP endpoints."""

    def test_predict_full_endpoint(self):
        payload = {
            "genotype_dosages": {
                "rs12913832": 2.0,
                "rs16891982": 2.0,
                "rs1426654": 2.0,
                "rs1805007": 1.0,
            },
            "enable_imputation": True,
        }
        resp = client.post("/api/v1/forensic/phenotyping/hirisplex/predict-full", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["eye_color"]["predicted_class"] == "Blue"
        assert data["eye_color"]["probabilities"]["Blue"] >= 0.85
        assert data["skin_phototype"]["predicted_class"] in ["VeryPale", "Pale"]
        assert "ENFSI" in data["prosecutors_fallacy_shield"]

    def test_get_standards_endpoint(self):
        resp = client.get("/api/v1/forensic/phenotyping/hirisplex/standards")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 5
        assert any(s["standard_id"] == "NA12878_CEU_EUROPEAN" for s in data)

    def test_get_cross_validation_endpoint(self):
        resp = client.get("/api/v1/forensic/phenotyping/hirisplex/cross-validation")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3
        assert all(item["is_concordant"] is True for item in data)

    def test_get_reporting_shield_endpoint(self):
        resp = client.get("/api/v1/forensic/phenotyping/hirisplex/reporting-shield")
        assert resp.status_code == 200
        data = resp.json()
        assert data["has_phenotype_disclaimer"] is True
        assert "VISAGE" in data["disclaimer_text_en"]
        assert "VISAGE" in data["disclaimer_text_tr"]
