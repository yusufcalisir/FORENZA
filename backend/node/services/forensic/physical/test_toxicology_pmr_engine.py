r"""
Unit & Integration Tests for FORENZA Toxicology PMR & Antemortem Extrapolation Engine — Module 25.

Tests verbatim from Pillar 5 Research §5 & §6:
  - §5.1 Physicochemical Determinants of PMR and C_heart / C_femoral Ratios
  - §5.2 Elimination Kinetics and Antemortem Back-Extrapolation (Widmark & First-Order)

Golden Benchmarks:
  - VECTOR_25_TOX_A through H
"""

import pytest
import math
from typing import List, Dict, Any
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.physical.toxicology_pmr_engine import (
    ForensicToxicologyPmrEngine,
    XENOBIOTIC_DATABASE,
)
from app.api.physical_routes import router as physical_router

_app = FastAPI()
_app.include_router(physical_router, prefix="/api/v1")
client = TestClient(_app)

engine = ForensicToxicologyPmrEngine()


# ── VECTOR_25_TOX_A — Ethanol Zero-Order Widmark Elimination ──────────────────

class TestVector25ToxA:
    """Verifies Ethanol zero-order back-extrapolation: C_antemortem = C_femoral + (beta_60 * dt)."""

    def test_ethanol_widmark_elimination(self):
        c_femoral = 0.50  # g/L
        dt = 4.0  # hours
        beta_60 = 0.15  # g/L/h

        res = engine.extrapolate_antemortem_concentration(
            compound_name="Ethanol",
            c_femoral=c_femoral,
            elapsed_hours=dt,
            unit="g/L",
        )
        expected = c_femoral + (beta_60 * dt)  # 0.50 + 0.60 = 1.10 g/L
        assert math.isclose(res["c_antemortem_extrapolated"], expected, rel_tol=1e-5)
        assert res["elimination_type"] == "Zero-Order"
        assert res["beta_60_g_l_h"] == 0.15


# ── VECTOR_25_TOX_B — Fentanyl First-Order Half-Life Elimination ──────────────

class TestVector25ToxB:
    """Verifies Fentanyl first-order elimination: C_antemortem = C_femoral * exp(ke * dt)."""

    def test_fentanyl_first_order_elimination(self):
        c_femoral = 5.0  # ug/L
        t_half = 7.0  # hours
        dt = 7.0  # exactly 1 half-life elapsed

        res = engine.extrapolate_antemortem_concentration(
            compound_name="Fentanyl",
            c_femoral=c_femoral,
            elapsed_hours=dt,
            unit="ug/L",
        )
        # Exactly 1 half-life back in time means antemortem concentration was exactly 2x postmortem
        expected = c_femoral * 2.0  # 10.0 ug/L
        assert math.isclose(res["c_antemortem_extrapolated"], expected, rel_tol=1e-3)
        assert res["elimination_type"] == "First-Order"
        assert res["half_life_hours"] == 7.0


# ── VECTOR_25_TOX_C — Amitriptyline Massive PMR Cardiac Overestimation ────────

class TestVector25ToxC:
    """Verifies high Vd (20.0 L/kg) Amitriptyline triggers cardiac overestimation alert."""

    def test_amitriptyline_pmr_alert(self):
        c_heart = 4.50  # mg/L
        c_femoral = 1.00  # mg/L

        res = engine.evaluate_pmr_ratio(
            compound_name="Amitriptyline",
            c_heart=c_heart,
            c_femoral=c_femoral,
            unit="mg/L",
        )
        assert res["cp_observed"] == 4.50
        assert res["pmr_risk_tier"] == "Very High"
        assert res["is_cardiac_overestimated"] is True
        assert res["overestimation_percentage"] == 350.0
        assert "OVERESTIMATION ALERT" in res["alert_message"]


# ── VECTOR_25_TOX_D — Acetaminophen Minimal PMR Baseline ──────────────────────

class TestVector25ToxD:
    """Verifies low Vd (0.9 L/kg) Acetaminophen exhibits minimal redistribution."""

    def test_acetaminophen_low_pmr(self):
        c_heart = 10.5  # mg/L
        c_femoral = 10.0  # mg/L

        res = engine.evaluate_pmr_ratio(
            compound_name="Acetaminophen",
            c_heart=c_heart,
            c_femoral=c_femoral,
            unit="mg/L",
        )
        assert res["cp_observed"] == 1.05
        assert res["pmr_risk_tier"] == "Low"
        assert res["is_cardiac_overestimated"] is False


# ── VECTOR_25_TOX_E — First-Order Rate Constant Invariant ────────────────────

class TestVector25ToxE:
    """Verifies ke = ln(2) / t_half invariant across various half-lives."""

    def test_rate_constant_ke(self):
        for drug, info in XENOBIOTIC_DATABASE.items():
            if info["elimination_type"] == "First-Order" and info["half_life_hours"]:
                t_half = info["half_life_hours"]
                res = engine.extrapolate_antemortem_concentration(drug, 1.0, 1.0)
                expected_ke = math.log(2.0) / t_half
                assert math.isclose(res["elimination_rate_constant_ke_h"], expected_ke, rel_tol=1e-3)


# ── VECTOR_25_TOX_F — Domain Validation for Concentrations and Time ──────────

class TestVector25ToxF:
    """Verifies non-positive concentrations or negative elapsed time raise ValueError."""

    def test_non_positive_femoral_raises(self):
        with pytest.raises(ValueError, match="strictly positive"):
            engine.evaluate_pmr_ratio("Ethanol", 0.5, 0.0)

        with pytest.raises(ValueError, match="strictly positive"):
            engine.extrapolate_antemortem_concentration("Ethanol", 0.0, 2.0)

    def test_negative_time_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            engine.extrapolate_antemortem_concentration("Ethanol", 1.0, -1.5)


# ── VECTOR_25_TOX_G — Generic Xenobiotic Fallback ─────────────────────────────

class TestVector25ToxG:
    """Verifies uncataloged compound safely falls back to conservative generic defaults."""

    def test_uncataloged_compound_fallback(self):
        res = engine.evaluate_pmr_ratio("NovelSyntheticOpioidX", 2.0, 1.0)
        assert res["cp_observed"] == 2.0
        assert "Uncataloged" in res["clinical_guideline"]


# ── VECTOR_25_TOX_H — FastAPI Endpoint Integration Tests ─────────────────────

class TestVector25ToxH:
    """Verifies FastAPI /forensic/physical toxicology PMR endpoints."""

    def test_api_pmr_evaluation(self):
        payload = {
            "compound_name": "Morphine",
            "c_heart": 0.36,
            "c_femoral": 0.20,
            "unit": "mg/L"
        }
        resp = client.post("/api/v1/forensic/physical/toxicology-pmr-evaluation", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["cp_observed"] == 1.8
        assert data["pmr_risk_tier"] == "Moderate"

    def test_api_antemortem_extrapolation(self):
        payload = {
            "compound_name": "Ethanol",
            "c_femoral": 0.80,
            "elapsed_hours": 3.0,
            "unit": "g/L"
        }
        resp = client.post("/api/v1/forensic/physical/toxicology-antemortem-extrapolation", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["c_antemortem_extrapolated"] == 1.25
