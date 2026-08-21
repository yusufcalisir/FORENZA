"""
Integration Test Suite for FORENZA Interpol DVI REST API (Module 2.4).
Tests all endpoints on /api/v1/forensic/dvi/* and HTTP 422 validation handling.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from node.services.forensic.dvi.dvi_reference_datasets import (
    DVI_CASEWORK_COHORTS,
    DVI_PEDIGREE_TEMPLATES,
)

client = TestClient(app)


class TestDviApiEndpoints:
    """Integration tests for /forensic/dvi/* endpoints."""

    def test_compute_joint_lr_endpoint(self):
        payload = {
            "autosomal_lr": 5200.0,
            "ystr_p_upper": 0.0002,
            "mtdna_p_upper": 0.0001,
            "has_ystr": True,
            "has_mtdna": True,
            "prior_probability": 0.001,
        }
        res = client.post("/api/v1/forensic/dvi/joint-lr", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["decision_tier"] == "DEFINITIVE_IDENTIFICATION"
        assert abs(data["joint_lr"] - 2.6e11) < 1e5
        assert data["posterior_probability_w"] > 0.999999
        assert data["is_definitive_identification"] is True

    def test_reconcile_matrix_endpoint(self):
        payload = {
            "disaster_event_id": "CRASH-777",
            "pm_remains": [
                {
                    "pm_id": "PM-01",
                    "autosomal_lr_map": {"AM-FAM-A": 1.5e8, "AM-FAM-B": 1.0e2},
                    "default_autosomal_lr": 1.0,
                    "ystr_p_upper": 0.0002,
                    "mtdna_p_upper": 0.0001,
                },
                {
                    "pm_id": "PM-02",
                    "autosomal_lr_map": {"AM-FAM-A": 1.0e2, "AM-FAM-B": 3.0e9},
                    "default_autosomal_lr": 1.0,
                },
            ],
            "am_families": [
                {"am_id": "AM-FAM-A", "has_male_reference": True, "has_maternal_reference": True},
                {"am_id": "AM-FAM-B", "has_male_reference": False, "has_maternal_reference": False},
            ],
            "threshold_lr": 1000000.0,
        }
        res = client.post("/api/v1/forensic/dvi/reconcile-matrix", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["total_pm_remains"] == 2
        assert data["total_am_families"] == 2
        assert len(data["reconciliation_matrix"]) == 4
        assert len(data["optimal_assignments"]) == 2

    def test_get_decision_tiers_endpoint(self):
        res = client.get("/api/v1/forensic/dvi/decision-tiers")
        assert res.status_code == 200
        data = res.json()
        assert len(data["tiers"]) == 4

    def test_get_pedigree_templates_endpoint(self):
        res = client.get("/api/v1/forensic/dvi/pedigree-templates")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 4

    def test_get_casework_cohorts_endpoint(self):
        res = client.get("/api/v1/forensic/dvi/casework-cohorts")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 5

    def test_get_reporting_disclaimer_endpoint(self):
        res = client.get("/api/v1/forensic/dvi/reporting-disclaimer")
        assert res.status_code == 200
        data = res.json()
        assert data["has_dvi_disclaimer"] is True
        assert "Interpol" in data["disclaimer_text_en"]

    def test_422_validation_errors(self):
        # Negative autosomal LR
        bad_payload = {"autosomal_lr": -50.0}
        res = client.post("/api/v1/forensic/dvi/joint-lr", json=bad_payload)
        assert res.status_code == 422
