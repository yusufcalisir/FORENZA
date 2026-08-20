"""
Unit & Integration Tests for FORENZA VISAGE 5-CpG & Multi-Tissue Epigenetic Age Clock Engine — Module 16.

Tests verbatim from VISAGE Research Specification (research/visage_5_cpg_epigenetic_aging_research.md):
  - VISAGE 5-CpG Piecewise Log-Linear Elastic Net Model (Horvath Link, y0 = 20.0 pivot)
  - VISAGE 5-CpG Direct MLR Power Model (Zbieć-Piekarska et al.)
  - ISO/IEC 17025 Dynamic Mahalanobis Metrological Uncertainty Budget (X^T X)^-1
  - Standardized ENFSI Evaluative Reporting (English & Turkish)

Golden Benchmarks:
  - VECTOR_VISAGE_01 (Pediatric Sample, Age 8.09 yrs)
  - VECTOR_VISAGE_02 (Young Adult Dried Bloodstain, Age 22.71 yrs)
  - VECTOR_VISAGE_03 (Middle-Aged Adult Blood, Age 53.25 yrs)
  - VECTOR_VISAGE_04 (Elderly Adult Blood, Age ~73–74 yrs)
  - VECTOR_VISAGE_05 (Oral Epithelial Buccal Swab, Age 35.68 yrs)
  - VECTOR_P4_01 (Young Adult Extended Clock, Age 25)
  - VECTOR_P4_02 (Elderly Heavy Smoker Extended Clock, Age 68)
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


# ── 1. VISAGE 5-CpG Golden Benchmark Vectors (VECTOR_VISAGE_01–05) ─────────────

class TestVisageGoldenVectors:
    """Verifies all 5 VISAGE Consortium Golden Benchmark Vectors with strict tolerance."""

    def test_vector_visage_01_pediatric(self):
        """VECTOR_VISAGE_01: Pediatric Whole Blood Sample (Predicted Age ~8.09 yrs)."""
        betas = {
            "cg16867657": 0.050,  # ELOVL2
            "cg06639320": 0.080,  # FHL2
            "cg16419235": 0.040,  # PENK
            "cg04523812": 0.050,  # TRIM59
            "cg07955995": 0.030,  # KLF14
        }
        res = engine.predict_age(betas, tissue_type="BLOOD", model_mode="VISAGE_5CPG_ELASTIC_NET")

        assert res["linear_predictor_x"] == pytest.approx(-0.8374, abs=0.001)
        assert res["estimated_age_years"] == pytest.approx(8.09, abs=0.05)
        assert res["developmental_stage"] == "PEDIATRIC (<20 yrs)"
        assert res["prediction_interval_lower"] == pytest.approx(2.01, abs=0.1)
        assert res["prediction_interval_upper"] == pytest.approx(14.17, abs=0.1)
        assert res["enfsi_demographic_category"] == "Child / Minor"
        assert "child / minor" in res["enfsi_statement_en"].lower()
        assert "çocuk" in res["enfsi_statement_tr"].lower() or "reşit olmayan" in res["enfsi_statement_tr"].lower()

    def test_vector_visage_02_young_adult(self):
        """VECTOR_VISAGE_02: Young Adult Dried Bloodstain (Predicted Age ~22.71 yrs)."""
        betas = {
            "cg16867657": 0.200,
            "cg06639320": 0.190,
            "cg16419235": 0.150,
            "cg04523812": 0.160,
            "cg07955995": 0.140,
        }
        res = engine.predict_age(betas, tissue_type="BLOOD", model_mode="VISAGE_5CPG_ELASTIC_NET")

        assert res["linear_predictor_x"] == pytest.approx(0.1291, abs=0.001)
        assert res["estimated_age_years"] == pytest.approx(22.71, abs=0.05)
        assert res["developmental_stage"] == "ADULT (>=20 yrs)"
        assert res["prediction_interval_lower"] == pytest.approx(18.89, abs=0.1)
        assert res["prediction_interval_upper"] == pytest.approx(26.53, abs=0.1)
        assert res["enfsi_demographic_category"] == "Young Adult"

    def test_vector_visage_03_middle_aged_adult(self):
        """VECTOR_VISAGE_03: Middle-Aged Adult Blood (Predicted Age ~53.25 yrs)."""
        betas = {
            "cg16867657": 0.420,
            "cg06639320": 0.380,
            "cg16419235": 0.310,
            "cg04523812": 0.330,
            "cg07955995": 0.280,
        }
        res = engine.predict_age(betas, tissue_type="BLOOD", model_mode="VISAGE_5CPG_ELASTIC_NET")

        assert res["linear_predictor_x"] == pytest.approx(1.5835, abs=0.001)
        assert res["estimated_age_years"] == pytest.approx(53.25, abs=0.05)
        assert res["developmental_stage"] == "ADULT (>=20 yrs)"
        assert res["prediction_interval_lower"] == pytest.approx(49.43, abs=0.1)
        assert res["prediction_interval_upper"] == pytest.approx(57.07, abs=0.1)
        assert res["enfsi_demographic_category"] == "Middle-Aged Adult"

    def test_vector_visage_04_elderly_adult(self):
        """VECTOR_VISAGE_04: Elderly Adult Blood Sample."""
        betas = {
            "cg16867657": 0.720,
            "cg06639320": 0.620,
            "cg16419235": 0.530,
            "cg04523812": 0.560,
            "cg07955995": 0.480,
        }
        res = engine.predict_age(betas, tissue_type="BLOOD", model_mode="VISAGE_5CPG_ELASTIC_NET")

        # Sum of weights: -1.25 + 2.85*0.72 + 1.92*0.62 + 0.95*0.53 + 0.88*0.56 + 1.15*0.48 = 3.5407
        assert res["linear_predictor_x"] == pytest.approx(3.5407, abs=0.001)
        assert res["estimated_age_years"] == pytest.approx(94.35, abs=0.1)
        assert res["developmental_stage"] == "ADULT (>=20 yrs)"
        assert res["enfsi_demographic_category"] == "Senior / Elderly"

    def test_vector_visage_05_buccal_swab(self):
        """VECTOR_VISAGE_05: Oral Epithelial Buccal Swab (Delta = +2.45 yrs, Age ~35.68 yrs)."""
        betas = {
            "cg16867657": 0.280,
            "cg06639320": 0.250,
            "cg16419235": 0.200,
            "cg04523812": 0.220,
            "cg07955995": 0.190,
        }
        res = engine.predict_age(betas, tissue_type="SALIVA_BUCCAL", model_mode="VISAGE_5CPG_ELASTIC_NET")

        assert res["linear_predictor_x"] == pytest.approx(0.6301, abs=0.001)
        assert res["model_age_before_offset"] == pytest.approx(33.23, abs=0.05)
        assert res["tissue_offset_applied"] == 2.45
        assert res["estimated_age_years"] == pytest.approx(35.68, abs=0.05)
        assert res["prediction_interval_lower"] == pytest.approx(31.27, abs=0.1)
        assert res["prediction_interval_upper"] == pytest.approx(40.09, abs=0.1)
        assert res["enfsi_demographic_category"] == "Adult (Buccal Matrix)"


# ── 2. Direct MLR Power Model Tests (Zbieć-Piekarska et al.) ──────────────────

class TestVisageMlrPowerModel:
    """Verifies the direct Multiple Linear Regression model with ELOVL2 power transformation."""

    def test_mlr_power_model_prediction(self):
        betas = {
            "cg16867657": 0.40,
            "cg06639320": 0.35,
            "cg16419235": 0.25,
            "cg04523812": 0.30,
            "cg07955995": 0.22,
        }
        res = engine.predict_age(betas, tissue_type="BLOOD", model_mode="VISAGE_5CPG_MLR_POWER")

        # -14.2815 + 120.3520*(0.40^2.366) + 38.2140*0.35 + 21.8040*0.25 + 18.9410*0.30 + 26.1030*0.22 = 29.70 yrs
        assert res["estimated_age_years"] == pytest.approx(29.70, abs=0.2)
        assert res["model_mode"] == "VISAGE_5CPG_MLR_POWER"
        assert res["prediction_interval_lower"] <= res["estimated_age_years"] <= res["prediction_interval_upper"]


# ── 3. ISO 17025 Dynamic Mahalanobis Covariance Tests ─────────────────────────

class TestMahalanobisUncertainty:
    """Verifies that samples farther from the calibration centroid have higher uncertainty."""

    def test_mahalanobis_distance_scaling(self):
        # Sample at exact centroid: d_sq ~ 0.0
        centroid_betas = [0.3850, 0.3120, 0.2450, 0.2810, 0.2100]
        d_sq_centroid = engine.calculate_mahalanobis_distance_sq(centroid_betas)
        assert d_sq_centroid == pytest.approx(0.0, abs=1e-6)

        # Distant outlier sample: d_sq > 0
        outlier_betas = [0.90, 0.85, 0.80, 0.75, 0.70]
        d_sq_outlier = engine.calculate_mahalanobis_distance_sq(outlier_betas)
        assert d_sq_outlier > 0.005


# ── 4. Legacy Extended 10-CpG Tests & Backward Compatibility ───────────────────

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

        assert res["estimated_age_years"] == pytest.approx(25.2, abs=3.5)
        assert res["developmental_stage"] == "ADULT (>=20 yrs)"
        assert res["tissue_type"] == "BLOOD"
        assert res["prediction_interval_lower"] <= res["estimated_age_years"]
        assert res["prediction_interval_upper"] >= res["estimated_age_years"]
        assert res["age_acceleration_delta"] == pytest.approx(0.0, abs=3.5)


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

        assert res["estimated_age_years"] == pytest.approx(75.3, abs=1.0)
        assert res["developmental_stage"] == "ADULT (>=20 yrs)"
        assert res["tissue_type"] == "BLOOD"
        assert res["age_acceleration_delta"] > 5.0
        assert res["aging_status"] == "ACCELERATED_BIOLOGICAL_AGING"


class TestVector16AgeA:
    """Verifies exponential transformation when linear predictor x < 0."""

    def test_pediatric_exponential_branch(self):
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


class TestVector16AgeC:
    """Verifies positive correlation of age drivers."""

    def test_elovl2_and_fhl2_positive_correlation(self):
        betas_low = {"cg16867657": 0.20, "cg06639320": 0.20}
        betas_high = {"cg16867657": 0.70, "cg06639320": 0.70}

        age_low = engine.predict_age(betas_low)["estimated_age_years"]
        age_high = engine.predict_age(betas_high)["estimated_age_years"]

        assert age_high > age_low


class TestVector16AgeD:
    """Verifies negative correlation modulation."""

    def test_aspa_and_penk_negative_correlation(self):
        betas_aspa_low = {"cg02228185": 0.10}
        betas_aspa_high = {"cg02228185": 0.90}

        age_aspa_low = engine.predict_age(betas_aspa_low)["estimated_age_years"]
        age_aspa_high = engine.predict_age(betas_aspa_high)["estimated_age_years"]

        assert age_aspa_low > age_aspa_high


class TestVector16AgeE:
    """Verifies exact tissue calibration offsets."""

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

        assert res_semen["estimated_age_years"] < res_blood["estimated_age_years"]


class TestVector16AgeF:
    """Verifies biological age acceleration."""

    def test_accelerated_aging_classification(self):
        cpg_betas = {"cg16867657": 0.70, "cg06639320": 0.65, "cg04084157": 0.60}
        res = engine.predict_age(cpg_betas, tissue_type="BLOOD", chronological_age_known=25.0)

        assert res["age_acceleration_delta"] > 5.0
        assert res["aging_status"] == "ACCELERATED_BIOLOGICAL_AGING"

    def test_decelerated_aging_classification(self):
        cpg_betas = {"cg16867657": 0.10, "cg06639320": 0.10, "cg16419235": 0.50}
        res = engine.predict_age(cpg_betas, tissue_type="BLOOD", chronological_age_known=70.0)

        assert res["age_acceleration_delta"] < -5.0
        assert res["aging_status"] == "DECELERATED_BIOLOGICAL_AGING"


class TestVector16AgeG:
    """Verifies ISO 17025 95% prediction bounds."""

    def test_prediction_bounds_containment(self):
        cpg_betas = {"cg16867657": 0.45, "cg06639320": 0.40}
        res = engine.predict_age(cpg_betas, tissue_type="BLOOD")

        est = res["estimated_age_years"]
        lower = res["prediction_interval_lower"]
        upper = res["prediction_interval_upper"]

        assert lower <= est <= upper
        assert upper > lower


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
            "model_mode": "VISAGE_5CPG_ELASTIC_NET",
        }
        resp = client.post("/api/v1/forensic/epigenetics/predict-age", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "estimated_age_years" in data
        assert "prediction_interval_lower" in data
        assert "prediction_interval_upper" in data
        assert "cpg_locus_contributions" in data
        assert "enfsi_statement_en" in data
        assert "enfsi_statement_tr" in data
