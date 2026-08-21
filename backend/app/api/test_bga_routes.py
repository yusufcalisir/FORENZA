"""
FastAPI TestClient integration tests for FORENZA BGA-55 REST API routes (Module 3.2).
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.bga_routes import router as bga_router

app = FastAPI()
app.include_router(bga_router, prefix="/api/v1")
client = TestClient(app)


class TestBGARoutes:
    """Verifies all BGA-55 REST endpoints."""

    def test_predict_full_european_standard(self):
        payload = {
            "snp_dosages": {
                "rs1426654": 2.0,
                "rs16891982": 2.0,
                "rs12913832": 2.0,
                "rs2814778": 0.0,
            }
        }
        res = client.post("/api/v1/forensic/phenotyping/bga/predict-full", json=payload)
        assert res.status_code == 200
        data = res.json()

        assert "admixture" in data
        assert "gis" in data
        assert data["admixture"]["dominant_population"] == "EUR"
        assert data["admixture"]["is_simplex_valid"] is True
        assert "European" in data["gis"]["nearest_centroid"]
        assert "ENFSI" in data["prosecutors_fallacy_shield"]

    def test_get_standards_endpoint(self):
        res = client.get("/api/v1/forensic/phenotyping/bga/standards")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 5
        standard_ids = [s["standard_id"] for s in data]
        assert "NA12878_CEU_EUROPEAN" in standard_ids
        assert "NA19240_YRI_AFRICAN" in standard_ids
        assert "NA18507_CHB_EAST_ASIAN" in standard_ids

    def test_get_cross_validation_endpoint(self):
        res = client.get("/api/v1/forensic/phenotyping/bga/cross-validation")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 3
        for item in data:
            assert item["is_concordant"] is True
            assert item["absolute_residual"] <= 0.05

    def test_get_reporting_shield_endpoint(self):
        res = client.get("/api/v1/forensic/phenotyping/bga/reporting-shield")
        assert res.status_code == 200
        data = res.json()
        assert data["has_bga_disclaimer"] is True
        assert data["prosecutors_fallacy_shield_active"] is True
        assert "ENFSI" in data["disclaimer_text_en"]
