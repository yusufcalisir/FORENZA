"""
Unit & Integration Tests for FORENZA Evidence Image Analysis & BPA Package.
Tests stain morphometry ellipse fitting, arcsin(W/L) impact angle estimation,
spatter pattern classification, human analyst verification sign-off, and API endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.bpa.analyzer import BloodstainPatternAnalyzer
from app.api.bpa_routes import router as bpa_router

_app = FastAPI()
_app.include_router(bpa_router, prefix="/api/v1")
client = TestClient(_app)

bpa_analyzer = BloodstainPatternAnalyzer()


# ── Morphometry & Impact Angle Tests ────────────────────────────────────────

def test_circular_stain_90_degree_impact():
    res = bpa_analyzer.analyze_stain("STAIN-CIRCULAR-1", width_mm=10.0, length_mm=10.0)
    assert res.morphometry.ellipse_aspect_ratio == 1.0
    assert res.morphometry.impact_angle_deg == 90.0
    assert res.predicted_pattern == "PASSIVE_DROP"
    assert res.review_status == "PENDING_HUMAN_REVIEW"


def test_elliptical_stain_30_degree_impact():
    # sin(30 deg) = 0.5 -> W = 5.0mm, L = 10.0mm
    res = bpa_analyzer.analyze_stain("STAIN-ELLIPSE-2", width_mm=5.0, length_mm=10.0)
    assert res.morphometry.ellipse_aspect_ratio == 0.5
    assert res.morphometry.impact_angle_deg == 30.0


def test_human_analyst_verification_workflow():
    initial = bpa_analyzer.analyze_stain("STAIN-FLOW-3", width_mm=2.0, length_mm=8.0)
    assert initial.review_status == "PENDING_HUMAN_REVIEW"

    verified = bpa_analyzer.verify_analysis(
        analysis_result=initial,
        analyst_id="ANALYST-BPA-77",
        decision="VERIFIED_BY_ANALYST",
        final_pattern="HIGH_VELOCITY_SPATTER",
        analyst_notes="Confirmed via microscopic tail directionality.",
        timestamp_utc=1770000000.0
    )

    assert verified.review_status == "VERIFIED_BY_ANALYST"
    assert verified.predicted_pattern == "HIGH_VELOCITY_SPATTER"
    assert verified.verification_record.analyst_id == "ANALYST-BPA-77"


# ── API Endpoint Integration Tests ───────────────────────────────────────────

def test_api_analyze_stain_endpoint():
    payload = {
        "stain_id": "STAIN-DROP-001",
        "width_mm": 5.2,
        "length_mm": 10.4
    }

    resp = client.post("/api/v1/forensic/bpa/analyze-stain", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["stain_id"] == "STAIN-DROP-001"
    assert data["morphometry"]["impact_angle_deg"] == 30.0
    assert data["review_status"] == "PENDING_HUMAN_REVIEW"


def test_api_verify_analyst_endpoint():
    payload = {
        "stain_id": "STAIN-DROP-001",
        "width_mm": 5.2,
        "length_mm": 10.4,
        "analyst_id": "ANALYST-BPA-09",
        "decision": "VERIFIED_BY_ANALYST",
        "final_pattern": "HIGH_VELOCITY_SPATTER",
        "analyst_notes": "Sign-off completed after reviewing directionality."
    }

    resp = client.post("/api/v1/forensic/bpa/verify-analyst", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["review_status"] == "VERIFIED_BY_ANALYST"
    assert data["verification_record"]["analyst_id"] == "ANALYST-BPA-09"
