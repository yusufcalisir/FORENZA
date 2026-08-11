"""
Unit & Integration Tests for FORENZA Forensic Toxicology Package.
Tests quantitative drug screening, expanded measurement uncertainty (U_95%),
reference range classification (Therapeutic/Toxic/Fatal), Widmark BAC elimination,
Postmortem Redistribution (PMR) auditing, and API endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.toxicology.classifier import ForensicToxicologyEngine, ToxicologicalAnalyte
from node.services.forensic.toxicology.pharmacokinetics import EthanolWidmarkAuditor
from app.api.toxicology_routes import router as toxicology_router

_app = FastAPI()
_app.include_router(toxicology_router, prefix="/api/v1")
client = TestClient(_app)

tox_engine = ForensicToxicologyEngine()
widmark_auditor = EthanolWidmarkAuditor()


# ── Quantitative Screening & Uncertainty Tests ───────────────────────────────

def test_fatal_morphine_classification_with_uncertainty():
    analyte = ToxicologicalAnalyte(
        analyte_name="Morphine",
        matrix_type="WHOLE_BLOOD",
        measured_concentration=0.85,
        unit="mg/L"
    )

    res = tox_engine.screen_analytes("TOX-101", [analyte])
    assert len(res.analyte_reports) == 1
    rep = res.analyte_reports[0]
    assert rep.toxicological_classification == "FATAL_LETHAL"
    assert rep.expanded_uncertainty_95 > 0.0
    assert "±" in rep.concentration_formatted


def test_therapeutic_cocaine_classification():
    analyte = ToxicologicalAnalyte(
        analyte_name="Cocaine",
        matrix_type="WHOLE_BLOOD",
        measured_concentration=0.08,
        unit="mg/L"
    )

    res = tox_engine.screen_analytes("TOX-102", [analyte])
    rep = res.analyte_reports[0]
    assert rep.toxicological_classification == "THERAPEUTIC"


# ── Widmark BAC & PMR Tests ──────────────────────────────────────────────────

def test_widmark_bac_clearance():
    res = widmark_auditor.calculate_widmark_bac(
        sample_id="BAC-201",
        bac_initial=0.15,
        elapsed_hours=4.0,
        beta=0.015
    )

    assert res.bac_current_g_per_dl == 0.09
    assert res.time_to_sobriety_hours == 10.0


def test_pmr_cardiac_redistribution_elevation():
    res = widmark_auditor.calculate_widmark_bac(
        sample_id="BAC-202",
        bac_initial=0.20,
        elapsed_hours=2.0,
        c_cardiac=0.35,
        c_peripheral=0.18
    )

    assert res.pmr_ratio == 1.94
    assert "HIGH_PMR_ELEVATION" in res.pmr_interpretation


# ── API Endpoint Integration Tests ───────────────────────────────────────────

def test_api_toxicology_screen_endpoint():
    payload = {
        "sample_id": "TOX-SAMPLE-901",
        "analytes": [
            {
                "analyte_name": "Fentanyl",
                "matrix_type": "WHOLE_BLOOD",
                "measured_concentration": 0.025,
                "unit": "mg/L"
            }
        ]
    }

    resp = client.post("/api/v1/forensic/toxicology/screen", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["sample_id"] == "TOX-SAMPLE-901"
    assert data["analyte_reports"][0]["toxicological_classification"] == "FATAL_LETHAL"


def test_api_widmark_bac_endpoint():
    payload = {
        "sample_id": "BAC-CASE-101",
        "bac_initial_g_per_dl": 0.18,
        "elapsed_hours": 4.0,
        "c_cardiac": 0.22,
        "c_peripheral": 0.18
    }

    resp = client.post("/api/v1/forensic/toxicology/bac-widmark", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["bac_current_g_per_dl"] == 0.12
    assert data["pmr_ratio"] == 1.22
