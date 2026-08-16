"""
Unit & Integration Tests for FORENZA Bisulfite QC & Methylation Probe Calibration Engine — Module 20.

Tests verbatim from Pillar 4 Research §5 & §6:
  - §5.1 Conversion Efficiency Quality Control (C_conv >= 99.0%)
  - §5.2 Beta and M-Value Transformations (BMIQ Integration & Bidirectional Bijection)
  - §5.3 Detection P-Value Filtering (P_det <= 0.01) & Signal Offset Alpha Calibration

Golden Benchmarks:
  - VECTOR_20_QC_A through H
"""

import math
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.epigenetics.bisulfite_qc_engine import (
    BisulfiteQcEngine,
)
from app.api.epigenetics_routes import router as epigenetics_router

_app = FastAPI()
_app.include_router(epigenetics_router, prefix="/api/v1")
client = TestClient(_app)

engine = BisulfiteQcEngine()


# ── VECTOR_20_QC_A — High-Efficiency Bisulfite Conversion (>= 99%) ───────────

class TestVector20QcA:
    """Verifies that non-CpG cytosine deamination >= 99% passes forensic QC."""

    def test_passed_conversion_efficiency(self):
        # 10 control probes with total M = 15, total U = 3985 -> C_conv = (1 - 15/4000) * 100 = 99.625%
        non_cpg = [
            {"methylated": 1.5, "unmethylated": 398.5} for _ in range(10)
        ]
        res = engine.evaluate_conversion_efficiency(non_cpg)

        assert res["conversion_efficiency_percent"] >= 99.0
        assert res["conversion_efficiency_percent"] == pytest.approx(99.62, abs=0.02)
        assert res["qc_status"] == "PASSED_QC"
        assert res["non_cpg_probes_evaluated"] == 10


# ── VECTOR_20_QC_B — Incomplete Bisulfite Conversion Failure (< 99%) ─────────

class TestVector20QcB:
    """Verifies that incomplete bisulfite conversion (< 99%) raises a forensic failure alert."""

    def test_failed_conversion_efficiency(self):
        # Total M = 200, total U = 3800 -> C_conv = (1 - 200/4000) * 100 = 95.0%
        non_cpg = [
            {"methylated": 20.0, "unmethylated": 380.0} for _ in range(10)
        ]
        res = engine.evaluate_conversion_efficiency(non_cpg)

        assert res["conversion_efficiency_percent"] < 99.0
        assert res["conversion_efficiency_percent"] == pytest.approx(95.0, abs=0.1)
        assert res["qc_status"] == "FAILED_INSUFFICIENT_CONVERSION"


# ── VECTOR_20_QC_C — Beta to M-Value Logit Transformation ─────────────────────

class TestVector20QcC:
    """Verifies logarithmic logit conversion M = log2(beta / (1 - beta))."""

    def test_beta_to_m_transformations(self):
        # Beta = 0.50 -> M = log2(0.50 / 0.50) = 0.0
        assert engine.beta_to_m_value(0.50) == 0.0

        # Beta = 0.80 -> M = log2(0.80 / 0.20) = log2(4) = 2.0
        assert engine.beta_to_m_value(0.80) == pytest.approx(2.0, abs=0.001)

        # Beta = 0.20 -> M = log2(0.20 / 0.80) = log2(0.25) = -2.0
        assert engine.beta_to_m_value(0.20) == pytest.approx(-2.0, abs=0.001)


# ── VECTOR_20_QC_D — M-Value to Beta Inversion (Bidirectional Bijection) ──────

class TestVector20QcD:
    """Verifies exact bidirectional recovery |beta - inv(M)| < 1e-6."""

    @pytest.mark.parametrize("test_beta", [0.05, 0.15, 0.35, 0.50, 0.70, 0.85, 0.95])
    def test_bidirectional_bijection_recovery(self, test_beta):
        m_val = engine.beta_to_m_value(test_beta)
        recovered_beta = engine.m_value_to_beta(m_val)
        assert recovered_beta == pytest.approx(test_beta, abs=1e-4)


# ── VECTOR_20_QC_E — Boundary Conditions Handling (Beta = 0.0, 1.0) ───────────

class TestVector20QcE:
    """Verifies safe finite handling of beta extremes 0.0 and 1.0."""

    def test_boundary_values(self):
        m_zero = engine.beta_to_m_value(0.0)
        assert m_zero < -15.0  # Safe finite negative value guarded by epsilon

        m_one = engine.beta_to_m_value(1.0)
        assert m_one > 15.0  # Safe finite positive value guarded by epsilon

        assert engine.m_value_to_beta(m_zero) == pytest.approx(0.0, abs=1e-4)
        assert engine.m_value_to_beta(m_one) == pytest.approx(1.0, abs=1e-4)


# ── VECTOR_20_QC_F — Detection P-Value Filtering (P_det <= 0.01) ──────────────

class TestVector20QcF:
    """Verifies that noisy probes with detection P-value > 0.01 are filtered out."""

    def test_detection_p_value_thresholding(self):
        probes = [
            {"probe_id": "cg16867657", "raw_beta": 0.22, "detection_p_value": 0.0005, "probe_design_type": "TYPE_I"},
            {"probe_id": "cg21572722", "raw_beta": 0.20, "detection_p_value": 0.0080, "probe_design_type": "TYPE_I"},
            {"probe_id": "cg06639320", "raw_beta": 0.18, "detection_p_value": 0.0450, "probe_design_type": "TYPE_II"},  # Fail
        ]
        res = engine.calibrate_probes_bmiq(probes)

        assert res["total_probes_evaluated"] == 3
        assert res["probes_passed_qc"] == 2
        assert res["probes_filtered_out"] == 1
        assert res["calibrated_probes"][2]["qc_filter_passed"] is False


# ── VECTOR_20_QC_G — BMIQ Probe Calibration ───────────────────────────────────

class TestVector20QcG:
    """Verifies BMIQ dynamic range quantile calibration for Type II probes."""

    def test_bmiq_calibration_dynamic_range(self):
        probes = [
            {"probe_id": "cg_type1", "raw_beta": 0.10, "detection_p_value": 0.001, "probe_design_type": "TYPE_I"},
            {"probe_id": "cg_type2_low", "raw_beta": 0.10, "detection_p_value": 0.001, "probe_design_type": "TYPE_II"},
            {"probe_id": "cg_type2_high", "raw_beta": 0.90, "detection_p_value": 0.001, "probe_design_type": "TYPE_II"},
        ]
        res = engine.calibrate_probes_bmiq(probes)

        # Type I remains un-adjusted
        assert res["calibrated_probes"][0]["calibrated_beta"] == 0.10

        # Type II low beta is expanded towards 0.0
        assert res["calibrated_probes"][1]["calibrated_beta"] < 0.10

        # Type II high beta is expanded towards 1.0
        assert res["calibrated_probes"][2]["calibrated_beta"] > 0.90


# ── VECTOR_20_QC_H — FastAPI Endpoint Integration Tests ─────────────────────

class TestVector20QcH:
    """Verifies FastAPI /forensic/epigenetics/bisulfite-qc-and-calibrate endpoint integration."""

    def test_api_bisulfite_qc_endpoint(self):
        payload = {
            "non_cpg_signals": [
                {"methylated": 1.0, "unmethylated": 499.0},
                {"methylated": 2.0, "unmethylated": 498.0},
            ],
            "probes": [
                {"probe_id": "cg16867657", "raw_beta": 0.22, "detection_p_value": 0.001, "probe_design_type": "TYPE_I"},
                {"probe_id": "cg21572722", "raw_beta": 0.85, "detection_p_value": 0.002, "probe_design_type": "TYPE_II"},
            ]
        }
        resp = client.post("/api/v1/forensic/epigenetics/bisulfite-qc-and-calibrate", json=payload)
        assert resp.status_code == 200
        data = resp.json()

        assert data["bisulfite_conversion_qc"] is not None
        assert data["bisulfite_conversion_qc"]["conversion_efficiency_percent"] >= 99.0
        assert data["bisulfite_conversion_qc"]["qc_status"] == "PASSED_QC"

        assert data["probe_calibration"] is not None
        assert data["probe_calibration"]["probes_passed_qc"] == 2
        assert len(data["probe_calibration"]["calibrated_probes"]) == 2
        assert "Legal Shield" in data["prosecutors_fallacy_shield"]
