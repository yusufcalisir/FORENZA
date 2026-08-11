"""
Unit & Integration Tests for FORENZA Touch DNA & Low-Template Package.
Tests substrate recovery efficiency (porous vs. non-porous), stochastic allele dropout P(D) = exp(-lambda * m),
low-template classification (<100 pg), MCMC contributor deconvolution, and API endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.touch_dna.touch_engine import TouchDnaEngine
from app.api.touch_routes import router as touch_router

_app = FastAPI()
_app.include_router(touch_router, prefix="/api/v1")
client = TestClient(_app)

touch_engine = TouchDnaEngine()


# ── Substrate & Stochastic Dropout Tests ────────────────────────────────────

def test_smooth_non_porous_substrate_recovery():
    # Smooth Non-Porous: eff = 0.60 -> 100 pg input = 60 pg recovered
    res = touch_engine.analyze_ltdna("TOUCH-GLASS-1", "SMOOTH_NON_POROUS", input_mass_pg=100.0, lambda_dropout=0.05)
    assert res.substrate.efficiency_factor == 0.60
    assert res.substrate.recovered_mass_pg == 60.0
    assert res.is_low_template is True


def test_stochastic_dropout_probability_bounds():
    # Mass = 100 pg -> P(D) = exp(-0.05 * 100) = exp(-5) approx 0.0067
    res = touch_engine.analyze_ltdna("TOUCH-HIGH-MASS", "SMOOTH_NON_POROUS", input_mass_pg=200.0, lambda_dropout=0.05)
    assert res.stochastic_model.dropout_probability_pd < 0.01
    assert res.is_low_template is False


def test_low_mass_high_dropout_ltdna_classification():
    # Mass = 10 pg on fabric (eff = 0.20) -> 2 pg recovered -> P(D) = exp(-0.10) = 0.9048
    res = touch_engine.analyze_ltdna("TOUCH-FABRIC-LOW", "POROUS_FABRIC", input_mass_pg=10.0, lambda_dropout=0.05)
    assert res.substrate.recovered_mass_pg == 2.0
    assert res.stochastic_model.dropout_probability_pd > 0.80
    assert res.is_low_template is True


# ── API Endpoint Integration Tests ───────────────────────────────────────────

def test_api_analyze_ltdna_endpoint():
    payload = {
        "sample_id": "TOUCH-HANDLE-001",
        "substrate_type": "TEXTURED_NON_POROUS",
        "input_mass_pg": 80.0,
        "lambda_dropout": 0.05
    }

    resp = client.post("/api/v1/forensic/touch/analyze-ltdna", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["sample_id"] == "TOUCH-HANDLE-001"
    assert data["substrate"]["efficiency_factor"] == 0.40
    assert data["substrate"]["recovered_mass_pg"] == 32.0


def test_api_contributor_deconv_endpoint():
    payload = {
        "sample_id": "TOUCH-HANDLE-001",
        "num_contributors": 2,
        "recovered_mass_pg": 32.0
    }

    resp = client.post("/api/v1/forensic/touch/contributor-deconv", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["deconvolution_status"] == "MCMC_CONVERGED"
    assert "Major_Contributor" in data["mixture_proportions"]
    assert data["log10_lr"] > 5.0
