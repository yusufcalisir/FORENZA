"""
Integration Test Suite for FORENZA Ancient DNA & Degraded SNP API Endpoints (Module 2.5).
Tests all 7 REST endpoints and error boundaries with FastAPI TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api.adna_routes import router as adna_router


_app = FastAPI(title="Test aDNA API")
_app.include_router(adna_router, prefix="/api/v1")
client = TestClient(_app)


class TestAdnaApiEndpoints:
    """Tests all REST endpoints in /api/v1/forensic/adna/*."""

    def test_mapdamage_profile_endpoint(self):
        payload = {
            "delta_0": 0.25,
            "decay_alpha": 0.10,
            "baseline_error": 0.005,
            "max_position": 25,
            "g_to_a_ratio": 1.0,
        }
        resp = client.post("/api/v1/forensic/adna/mapdamage-profile", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["delta_0"] == 0.25
        assert len(data["curve_5p_c_to_t"]) == 25
        assert len(data["curve_3p_g_to_a"]) == 25
        assert "curve_5p_c_to_t" in data

    def test_fragmentation_endpoint(self):
        payload = {
            "lambda_param": 0.0446,
            "l_min": 30.0,
        }
        resp = client.post("/api/v1/forensic/adna/fragmentation", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["mean_length"] == pytest.approx(52.42, abs=0.2)
        assert data["degradation_tier"] == "SEVERE"
        assert data["recommended_technology"] == "MICRO_SNP_PANEL_40_70BP"

    def test_snp_likelihood_endpoint(self):
        payload = {
            "locus_id": "rs1800407",
            "ref_allele": "C",
            "alt_allele": "T",
            "read_bases": ["T", "T", "C"],
            "read_positions": [1, 2, 15],
            "delta_0": 0.35,
            "decay_alpha": 0.12,
            "sequencing_error_rate": 0.01,
            "prior_p_ref": 0.50,
        }
        resp = client.post("/api/v1/forensic/adna/snp-likelihood", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["locus_id"] == "rs1800407"
        assert data["is_damage_compensated"] is True
        assert data["deamination_risk_flag"] is True
        assert "AA" in data["raw_likelihoods"]

    def test_contamination_subtraction_endpoint(self):
        payload = {
            "observed_curve": {"1": 0.22, "2": 0.198, "3": 0.178},
            "contamination_fraction": 0.12,
            "modern_terminal_rate": 0.002,
        }
        resp = client.post("/api/v1/forensic/adna/contamination-subtraction", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["contamination_fraction"] == 0.12
        assert data["true_ancient_terminal_damage"] > data["observed_terminal_damage"]

    def test_purine_excess_endpoint(self):
        payload = {
            "purine_minus1_count": 720,
            "total_reads": 1000,
        }
        resp = client.post("/api/v1/forensic/adna/purine-excess", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["purine_fraction"] == 0.72
        assert data["is_ancient_depurination_signature"] is True

    def test_get_casework_cohorts_endpoint(self):
        resp = client.get("/api/v1/forensic/adna/casework-cohorts")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 5
        cohort_ids = {c["cohort_id"] for c in data}
        assert "BENCHMARK_COLUMBUS_SKELETAL" in cohort_ids
        assert "BENCHMARK_BRIGGS_ANCIENT" in cohort_ids

    def test_get_reporting_disclaimer_endpoint(self):
        resp = client.get("/api/v1/forensic/adna/reporting-disclaimer")
        assert resp.status_code == 200
        data = resp.json()
        assert data["has_adna_disclaimer"] is True
        assert "ISFG" in data["disclaimer_text_en"]

    def test_422_validation_errors(self):
        # Negative lambda_param should fail validation
        resp = client.post("/api/v1/forensic/adna/fragmentation", json={"lambda_param": -0.5, "l_min": 30.0})
        assert resp.status_code == 422

        # delta_0 > 1.0 should fail validation
        resp = client.post("/api/v1/forensic/adna/mapdamage-profile", json={"delta_0": 1.5, "decay_alpha": 0.10})
        assert resp.status_code == 422
