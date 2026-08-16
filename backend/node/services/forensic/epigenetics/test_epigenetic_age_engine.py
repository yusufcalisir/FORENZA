"""
Unit & Integration Tests for FORENZA Multi-Tissue Epigenetic Age Clock Engine — Module 16.

Tests verbatim from Pillar 4 Research §1 & §6:
  - §1.1 Horvath Piecewise Non-Linear Link Function (y0 = 20.0 pivot boundary)
  - §1.2 10 Key Forensic Predictive CpG Markers
  - §1.3 Multi-Tissue Calibration Offsets & ISO 17025 95% Confidence Bounds

Golden Benchmarks:
  - VECTOR_P4_01 (Young Adult Blood Donor, Age 25)
  - VECTOR_P4_02 (Elderly Active Heavy Smoker, Age 68)
  - VECTOR_16_AGE_A through H
"""

import math
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.epigenetics.age_engine import (
    EpigeneticClockEngine,
)
from app.api.epigenetics_routes import router as epigenetics_router

_app = FastAPI()
_app.include_router(epigenetics_router, prefix="/api/v1")
client = TestClient(_app)

engine = EpigeneticClockEngine()


# ── VECTOR_P4_01 — Young Adult Blood Donor (Age 25) ───────────────────────────

class TestVectorP401:
    """Verifies golden vector VECTOR_P4_01 (Young Adult Blood Donor, Age 25)."""

    def test_vector_p4_01_young_adult_prediction(self):
        cpg_betas = {
            "cg16867657": 0.22,
            "cg21572722": 0.20,
            "cg06639320": 0.18,
            "cg16419235": 0.35,
            "cg04084157": 0.25,
            "cg08097417": 0.22,
            "cg09809672": 0.20,
            "cg02088308": 0.21,
            "cg17861230": 0.22,
            "cg02228185": 0.30,
        }
        res = engine.predict_age(cpg_betas, tissue_type="BLOOD", chronological_age_known=25.0)

        # Expected: 25.2 +- 3.5 yrs
        assert res["estimated_age_years"] == pytest.approx(25.2, abs=3.5)
        assert res["developmental_stage"] == "ADULT (>=20 yrs)"
        assert res["tissue_type"] == "BLOOD"
        assert res["prediction_interval_lower"] <= res["estimated_age_years"]
        assert res["prediction_interval_upper"] >= res["estimated_age_years"]
        assert res["age_acceleration_delta"] == pytest.approx(0.0, abs=3.5)


# ── VECTOR_P4_02 — Elderly Active Heavy Smoker (Age 68) ───────────────────────

class TestVectorP402:
    """Verifies golden vector VECTOR_P4_02 (Elderly Active Heavy Smoker, Age 68)."""

    def test_vector_p4_02_elderly_prediction(self):
        cpg_betas = {
            "cg16867657": 0.74,
            "cg21572722": 0.71,
            "cg06639320": 0.69,
            "cg16419235": 0.20,
            "cg04084157": 0.65,
            "cg08097417": 0.62,
            "cg09809672": 0.58,
            "cg02088308": 0.60,
            "cg17861230": 0.61,
            "cg02228185": 0.15,
        }
        res = engine.predict_age(cpg_betas, tissue_type="BLOOD", chronological_age_known=68.0)

        # Expected: ~75.3 yrs with positive biological age acceleration (smoking effect)
        assert res["estimated_age_years"] == pytest.approx(75.3, abs=1.0)
        assert res["developmental_stage"] == "ADULT (>=20 yrs)"
        assert res["tissue_type"] == "BLOOD"
        assert res["age_acceleration_delta"] > 5.0
        assert res["aging_status"] == "ACCELERATED_BIOLOGICAL_AGING"



# ── VECTOR_16_AGE_A — Pediatric Piecewise Link Function (x < 0) ───────────────

class TestVector16AgeA:
    """Verifies exponential transformation when linear predictor x < 0."""

    def test_pediatric_exponential_branch(self):
        # Very low methylation profile representing child
        cpg_betas = {
            "cg16867657": 0.02,
            "cg21572722": 0.02,
            "cg06639320": 0.02,
            "cg16419235": 0.50,
            "cg04084157": 0.02,
            "cg08097417": 0.02,
            "cg09809672": 0.02,
            "cg02088308": 0.02,
            "cg17861230": 0.02,
            "cg02228185": 0.50,
        }
        res = engine.predict_age(cpg_betas, tissue_type="BLOOD")

        assert res["linear_predictor_x"] < 0.0
        assert res["developmental_stage"] == "PEDIATRIC (<20 yrs)"
        assert res["estimated_age_years"] < 20.0


# ── VECTOR_16_AGE_B — Adult Linear Piecewise Link Function (x >= 0) ───────────

class TestVector16AgeB:
    """Verifies linear progression when linear predictor x >= 0."""

    def test_adult_linear_branch(self):
        cpg_betas = {
            "cg16867657": 0.50,
            "cg21572722": 0.50,
            "cg06639320": 0.50,
            "cg16419235": 0.20,
            "cg04084157": 0.50,
            "cg08097417": 0.50,
            "cg09809672": 0.50,
            "cg02088308": 0.50,
            "cg17861230": 0.50,
            "cg02228185": 0.20,
        }
        res = engine.predict_age(cpg_betas, tissue_type="BLOOD")

        assert res["linear_predictor_x"] >= 0.0
        assert res["developmental_stage"] == "ADULT (>=20 yrs)"
        assert res["estimated_age_years"] >= 20.0


# ── VECTOR_16_AGE_C — ELOVL2 & FHL2 Positive Driver Scaling ────────────────────

class TestVector16AgeC:
    """Verifies that increasing ELOVL2 and FHL2 methylation monotonically increases predicted age."""

    def test_elovl2_and_fhl2_positive_correlation(self):
        betas_low = {"cg16867657": 0.20, "cg06639320": 0.20}
        betas_high = {"cg16867657": 0.70, "cg06639320": 0.70}

        age_low = engine.predict_age(betas_low)["estimated_age_years"]
        age_high = engine.predict_age(betas_high)["estimated_age_years"]

        assert age_high > age_low


# ── VECTOR_16_AGE_D — ASPA & PENK Negative Correlation Modulation ──────────────

class TestVector16AgeD:
    """Verifies that increasing ASPA and PENK methylation lowers predicted age."""

    def test_aspa_and_penk_negative_correlation(self):
        betas_aspa_low = {"cg02228185": 0.10}
        betas_aspa_high = {"cg02228185": 0.90}

        age_aspa_low = engine.predict_age(betas_aspa_low)["estimated_age_years"]
        age_aspa_high = engine.predict_age(betas_aspa_high)["estimated_age_years"]

        assert age_aspa_low > age_aspa_high


# ── VECTOR_16_AGE_E — Multi-Tissue Calibration Offsets ─────────────────────────

class TestVector16AgeE:
    """Verifies exact tissue calibration offsets across Blood, Saliva, Semen, and Bone."""

    def test_tissue_offset_hierarchy(self):
        cpg_betas = {"cg16867657": 0.40, "cg06639320": 0.35}

        res_blood = engine.predict_age(cpg_betas, tissue_type="BLOOD")
        res_saliva = engine.predict_age(cpg_betas, tissue_type="SALIVA")
        res_semen = engine.predict_age(cpg_betas, tissue_type="SEMEN")
        res_bone = engine.predict_age(cpg_betas, tissue_type="BONE")

        assert res_blood["tissue_offset_applied"] == 0.00
        assert res_saliva["tissue_offset_applied"] == 0.85
        assert res_semen["tissue_offset_applied"] == -4.20
        assert res_bone["tissue_offset_applied"] == 1.10

        # Semen age must be lower due to -4.20 offset
        assert res_semen["estimated_age_years"] < res_blood["estimated_age_years"]


# ── VECTOR_16_AGE_F — Biological Age Acceleration (Delta Age) ──────────────────

class TestVector16AgeF:
    """Verifies biological age acceleration and deceleration status."""

    def test_accelerated_aging_classification(self):
        cpg_betas = {"cg16867657": 0.70, "cg06639320": 0.65, "cg04084157": 0.60}
        res = engine.predict_age(cpg_betas, tissue_type="BLOOD", chronological_age_known=25.0)

        assert res["age_acceleration_delta"] > 5.0
        assert res["aging_status"] == "ACCELERATED_BIOLOGICAL_AGING"

    def test_decelerated_aging_classification(self):
        cpg_betas = {"cg16867657": 0.20, "cg06639320": 0.20}
        res = engine.predict_age(cpg_betas, tissue_type="BLOOD", chronological_age_known=70.0)

        assert res["age_acceleration_delta"] < -5.0
        assert res["aging_status"] == "DECELERATED_BIOLOGICAL_AGING"


# ── VECTOR_16_AGE_G — ISO 17025 95% Confidence Bounds ─────────────────────────

class TestVector16AgeG:
    """Verifies ISO 17025 95% prediction interval calculation."""

    def test_prediction_bounds_symmetry_and_containment(self):
        cpg_betas = {"cg16867657": 0.45, "cg06639320": 0.40}
        res = engine.predict_age(cpg_betas, tissue_type="BLOOD")

        est = res["estimated_age_years"]
        lower = res["prediction_interval_lower"]
        upper = res["prediction_interval_upper"]
        ci95 = res["expanded_uncertainty_95"]

        assert ci95 == 7.64
        assert lower <= est <= upper
        assert (upper - est) == pytest.approx(ci95, abs=0.2)


# ── VECTOR_16_AGE_H — API Integration Tests ────────────────────────────────────

class TestVector16AgeH:
    """Verifies FastAPI endpoint /api/v1/forensic/epigenetics/predict-age."""

    def test_api_predict_age_endpoint(self):
        payload = {
            "cpg_methylation": {
                "cg16867657": 0.35,
                "cg06639320": 0.30,
                "cg04084157": 0.25,
            },
            "tissue_type": "BLOOD",
            "chronological_age_known": 30.0,
        }
        resp = client.post("/api/v1/forensic/epigenetics/predict-age", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "estimated_age_years" in data
        assert "prediction_interval_lower" in data
        assert "prediction_interval_upper" in data
        assert "cpg_locus_contributions" in data
        assert len(data["cpg_locus_contributions"]) == 10
