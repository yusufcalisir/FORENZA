"""
Unit & Integration Tests for FORENZA Forensic Entomology Package.
Tests Accumulated Degree Hours (ADH) PMI calculation, species thermal constants,
insect succession auditing, and API endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.entomology.pmi import EntomologyPmiEstimator
from node.services.forensic.entomology.succession import InsectSuccessionAuditor, ArthropodOccurrence
from app.api.entomology_routes import router as entomology_router

_app = FastAPI()
_app.include_router(entomology_router, prefix="/api/v1")
client = TestClient(_app)

pmi_estimator = EntomologyPmiEstimator()
succession_auditor = InsectSuccessionAuditor()


# ── ADH PMI Tests ─────────────────────────────────────────────────────────────

def test_adh_pmi_calculation():
    res = pmi_estimator.estimate_pmi("Calliphora vicina", "INSTAR_3", mean_ambient_temp_celsius=18.0)

    assert res.species_name == "Calliphora vicina"
    assert res.required_adh == 2200.0
    assert res.effective_temp_celsius == 12.0  # 18.0 - 6.0
    assert res.estimated_pmi_hours == 183.3   # 2200 / 12
    assert res.estimated_pmi_days > 7.0


def test_adh_pmi_different_species():
    res1 = pmi_estimator.estimate_pmi("Calliphora vicina", "PUPA", mean_ambient_temp_celsius=20.0)
    res2 = pmi_estimator.estimate_pmi("Lucilia sericata", "PUPA", mean_ambient_temp_celsius=20.0)

    assert res1.required_adh != res2.required_adh
    assert res1.estimated_pmi_days > 0.0
    assert res2.estimated_pmi_days > 0.0


# ── Insect Succession Wave Tests ─────────────────────────────────────────────

def test_insect_succession_audit():
    occ = [
        ArthropodOccurrence("Calliphoridae", "Calliphora vicina", "HIGH"),
        ArthropodOccurrence("Silphidae", "Nicrophorus vespilloides", "MODERATE")
    ]

    report = succession_auditor.audit_succession_wave("ENTO-101", occ)
    assert report.inferred_decomposition_stage == "BLOATED_STAGE"
    assert "3 - 7 days" in report.typical_timeframe_days


# ── API Endpoint Integration Tests ───────────────────────────────────────────

def test_api_entomology_pmi_endpoint():
    payload = {
        "species_name": "Calliphora vicina",
        "development_stage": "INSTAR_3",
        "mean_ambient_temp_celsius": 18.5
    }

    resp = client.post("/api/v1/forensic/entomology/pmi", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["estimated_pmi_days"] > 5.0
    assert "days" in data["pmi_formatted_range"]


def test_api_entomology_succession_endpoint():
    payload = {
        "sample_id": "ENTO-CASE-301",
        "occurrences": [
            {
                "family_name": "Calliphoridae",
                "species_observed": "Calliphora vicina",
                "abundance_score": "HIGH"
            }
        ]
    }

    resp = client.post("/api/v1/forensic/entomology/succession", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["inferred_decomposition_stage"] == "FRESH_STAGE"
