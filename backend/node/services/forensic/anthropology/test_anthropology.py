"""
Unit & Integration Tests for FORENZA Forensic Anthropology Package.
Tests biological profile estimation (sex, age, Trotter-Gleser stature, population affinity),
skeletal trauma auditing, and API endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.anthropology.profile import AnthropologyProfileEstimator, MorphometricMeasurements
from node.services.forensic.anthropology.trauma import SkeletalTraumaAuditor, TraumaObservation
from app.api.anthropology_routes import router as anthropology_router

_app = FastAPI()
_app.include_router(anthropology_router, prefix="/api/v1")
client = TestClient(_app)

profile_estimator = AnthropologyProfileEstimator()
trauma_auditor = SkeletalTraumaAuditor()


# ── Biological Profile Tests ──────────────────────────────────────────────────

def test_trotter_gleser_stature_estimation():
    m = MorphometricMeasurements(femur_length_mm=450.0, subpubic_angle_deg=95.0, pubic_symphysis_phase=2)
    res = profile_estimator.estimate_biological_profile(m)

    assert res.estimated_sex == "FEMALE"
    assert res.sex_confidence > 0.85
    assert res.estimated_stature_cm > 160.0
    assert "20 - 24 years" in res.estimated_age_range


def test_craniometric_population_affinity():
    m = MorphometricMeasurements(cranial_length_mm=190.0, cranial_breadth_mm=135.0)
    res = profile_estimator.estimate_biological_profile(m)

    assert "Dolichocephalic" in res.population_affinity or "Affinity" in res.population_affinity


# ── Skeletal Trauma Audit Tests ──────────────────────────────────────────────

def test_skeletal_perimortem_trauma_audit():
    obs = [
        TraumaObservation("Left Femur", "BLUNT_FORCE", "PERIMORTEM", "Distal fracture with sharp margins"),
        TraumaObservation("Right Tibia", "TAPHONOMIC", "POSTMORTEM", "Sun bleaching and soil staining")
    ]

    report = trauma_auditor.audit_trauma_lesions("SKEL-101", "Left Femur", obs)
    assert report.total_observations_count == 2
    assert report.has_perimortem_trauma is True
    assert "CRITICAL" in report.trauma_summary


# ── API Endpoint Integration Tests ───────────────────────────────────────────

def test_api_biological_profile_endpoint():
    payload = {
        "measurements": {
            "femur_length_mm": 445.0,
            "subpubic_angle_deg": 92.0,
            "pubic_symphysis_phase": 3
        }
    }

    resp = client.post("/api/v1/forensic/anthropology/biological-profile", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["estimated_sex"] == "FEMALE"
    assert data["estimated_stature_cm"] > 150.0


def test_api_trauma_audit_endpoint():
    payload = {
        "sample_id": "SKEL-901",
        "element_name": "Left Femur",
        "observations": [
            {
                "element_name": "Left Femur",
                "trauma_mechanism": "BALLISTIC",
                "trauma_timing": "PERIMORTEM",
                "description": "Beveling hole fracture on mid-shaft"
            }
        ]
    }

    resp = client.post("/api/v1/forensic/anthropology/trauma-audit", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["has_perimortem_trauma"] is True
    assert data["total_observations_count"] == 1
