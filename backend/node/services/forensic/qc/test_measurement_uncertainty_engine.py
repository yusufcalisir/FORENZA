r"""
Unit & Integration Tests for FORENZA ISO/IEC 17025 Measurement Uncertainty Engine — Module 28.

Tests verbatim from Pillar 6 Research §3 & §6:
  - §3.1 Combined and Expanded Measurement Uncertainty (GUM / JCGM 100:2008 & k=2.00)
  - §3.2 Quantitative Calibration Uncertainty Budget & Proficiency Testing z-Scores

Golden Benchmarks:
  - VECTOR_P6_02 (Canonical 4-Component Calibration Budget Ground Truth)
  - VECTOR_28_UNCERT_A through G
"""

import pytest
import math
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.qc.measurement_uncertainty_engine import (
    ForensicMeasurementUncertaintyEngine,
    UncertaintyComponent,
)
from app.api.qc_routes import router as qc_router

_app = FastAPI()
_app.include_router(qc_router, prefix="/api/v1")
client = TestClient(_app)

engine = ForensicMeasurementUncertaintyEngine()


# ── VECTOR_P6_02 — Canonical 4-Component Calibration Budget Ground Truth ───────

class TestVectorP602:
    """Verifies combined u_c = 0.05385 ng/uL and expanded U_95% = 0.10770 ng/uL (k=2.00)."""

    def test_canonical_4_component_budget(self):
        nominal_conc = 1.250  # 1.250 ng/uL
        res = engine.calculate_uncertainty_budget(
            nominal_concentration=nominal_conc,
            coverage_factor=2.00,
        )

        # Expected variance: 0.000175 + 0.000225 + 0.0009 + 0.0016 = 0.002900
        assert abs(res["total_variance"] - 0.0029) < 1e-6
        # Combined u_c = sqrt(0.002900) ≈ 0.0538516...
        assert abs(res["combined_standard_uncertainty"] - 0.05385) < 1e-4
        # Expanded U_95% = 2.00 * u_c ≈ 0.107703...
        assert abs(res["expanded_uncertainty"] - 0.10770) < 1e-4


        # Verify reported interval bounds
        assert abs(res["reported_interval"]["lower_bound"] - (1.250 - 0.10770)) < 1e-4
        assert abs(res["reported_interval"]["upper_bound"] - (1.250 + 0.10770)) < 1e-4


# ── VECTOR_28_UNCERT_A — Custom Sensitivity Coefficients ─────────────────────

class TestVector28UncertA:
    """Verifies propagation of non-unity sensitivity coefficients c_i."""

    def test_custom_sensitivity_coefficients(self):
        custom_components = [
            UncertaintyComponent(name="Dilution Factor", standard_uncertainty=0.010, sensitivity_coefficient=2.0),
            UncertaintyComponent(name="Temperature Shift", standard_uncertainty=0.020, sensitivity_coefficient=1.5),
        ]
        # (2.0 * 0.010)^2 + (1.5 * 0.020)^2 = 0.02^2 + 0.03^2 = 0.0004 + 0.0009 = 0.0013
        res = engine.calculate_uncertainty_budget(
            nominal_concentration=0.500,
            components=custom_components,
            coverage_factor=2.00,
        )
        assert abs(res["total_variance"] - 0.0013) < 1e-6
        expected_uc = math.sqrt(0.0013)
        assert abs(res["combined_standard_uncertainty"] - expected_uc) < 1e-4


# ── VECTOR_28_UNCERT_B — Correlated Components Covariance Expansion ──────────

class TestVector28UncertB:
    """Verifies positive correlation r_ij expands combined uncertainty."""

    def test_correlated_components(self):
        comps = [
            UncertaintyComponent(name="Pipet A", standard_uncertainty=0.020),
            UncertaintyComponent(name="Pipet B", standard_uncertainty=0.030),
        ]
        # Independent variance: 0.02^2 + 0.03^2 = 0.0013
        res_indep = engine.calculate_uncertainty_budget(1.0, components=comps)

        # Correlated with r = 0.50 -> 2 * 1 * 1 * 0.50 * 0.02 * 0.03 = 0.0006 -> Total = 0.0019
        correlations = {"Pipet A:Pipet B": 0.50}
        res_corr = engine.calculate_uncertainty_budget(1.0, components=comps, correlations=correlations)

        assert abs(res_corr["total_variance"] - 0.0019) < 1e-6
        assert res_corr["combined_standard_uncertainty"] > res_indep["combined_standard_uncertainty"]


# ── VECTOR_28_UNCERT_C — Satisfactory Proficiency Test (|z| <= 2.0) ──────────

class TestVector28UncertC:
    """Verifies |z| <= 2.0 classifies as SATISFACTORY (Fully Calibrated)."""

    def test_satisfactory_proficiency(self):
        # Lab = 1.05, Consensus Mean = 1.00, Std = 0.05 -> z = +1.0
        res = engine.evaluate_proficiency_z_score(
            lab_measured_value=1.05,
            consensus_mean=1.00,
            consensus_std=0.05,
        )
        assert abs(res["z_score"] - 1.000) < 1e-4
        assert res["performance_tier"] == "SATISFACTORY"
        assert res["is_compliant"] is True


# ── VECTOR_28_UNCERT_D — Questionable Proficiency Warning (2.0 < |z| < 3.0) ──

class TestVector28UncertD:
    """Verifies 2.0 < |z| < 3.0 classifies as QUESTIONABLE (Warning State)."""

    def test_questionable_proficiency(self):
        # Lab = 1.12, Consensus Mean = 1.00, Std = 0.05 -> z = +2.4
        res = engine.evaluate_proficiency_z_score(
            lab_measured_value=1.12,
            consensus_mean=1.00,
            consensus_std=0.05,
        )
        assert abs(res["z_score"] - 2.400) < 1e-4
        assert res["performance_tier"] == "QUESTIONABLE"
        assert res["is_compliant"] is False


# ── VECTOR_28_UNCERT_E — Unsatisfactory Proficiency Breach (|z| >= 3.0) ──────

class TestVector28UncertE:
    """Verifies |z| >= 3.0 classifies as UNSATISFACTORY (Non-Compliant Alert)."""

    def test_unsatisfactory_proficiency(self):
        # Lab = 1.20, Consensus Mean = 1.00, Std = 0.05 -> z = +4.0
        res = engine.evaluate_proficiency_z_score(
            lab_measured_value=1.20,
            consensus_mean=1.00,
            consensus_std=0.05,
        )
        assert abs(res["z_score"] - 4.000) < 1e-4
        assert res["performance_tier"] == "UNSATISFACTORY"
        assert res["is_compliant"] is False


# ── VECTOR_28_UNCERT_F — Domain Validation for Invalid Parameters ─────────────

class TestVector28UncertF:
    """Verifies negative concentration or non-positive std raises ValueError."""

    def test_domain_validation_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            engine.calculate_uncertainty_budget(-0.5)

        with pytest.raises(ValueError, match="strictly positive"):
            engine.evaluate_proficiency_z_score(1.0, 1.0, 0.0)

        with pytest.raises(ValueError, match="cannot be negative"):
            bad_comp = [UncertaintyComponent(name="Bad", standard_uncertainty=-0.01)]
            engine.calculate_uncertainty_budget(1.0, components=bad_comp)


# ── VECTOR_28_UNCERT_G — FastAPI Endpoints Integration ────────────────────────

class TestVector28UncertG:
    """Verifies FastAPI /forensic/qc/uncertainty endpoints."""

    def test_api_calculate_budget(self):
        res = client.post(
            "/api/v1/forensic/qc/uncertainty/calculate-budget",
            json={"nominal_concentration": 2.50, "coverage_factor": 2.00}
        )
        assert res.status_code == 200
        data = res.json()
        assert abs(data["combined_standard_uncertainty"] - 0.05385) < 1e-4
        assert abs(data["expanded_uncertainty"] - 0.10770) < 1e-4

    def test_api_proficiency_z_score(self):
        res = client.post(
            "/api/v1/forensic/qc/uncertainty/proficiency-z-score",
            json={"lab_measured_value": 1.02, "consensus_mean": 1.00, "consensus_std": 0.05}
        )
        assert res.status_code == 200
        data = res.json()
        assert data["performance_tier"] == "SATISFACTORY"
        assert data["is_compliant"] is True
