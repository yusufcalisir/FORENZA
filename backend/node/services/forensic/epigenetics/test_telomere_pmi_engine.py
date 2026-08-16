"""
Unit & Integration Tests for FORENZA Telomere Length, Post-Mortem Interval (PMI) & Somatic Mosaicism Engine — Module 19.

Tests verbatim from Pillar 4 Research §4 & §6:
  - §4.1 Relative Telomere Length (T/S Ratio) Decay Kinetics (T/S = 1.420 - 0.0085 * Age)
  - §4.2 Post-Mortem Epigenetic Decay Kinetics & Thermal Summation (PMI / ADH)
  - §4.3 Somatic Mosaicism & Intra-Individual Epigenetic Drift Index (M)

Golden Benchmarks:
  - VECTOR_19_PMI_A through H
"""

import math
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.epigenetics.telomere_pmi_engine import (
    TelomerePmiEngine,
)
from app.api.epigenetics_routes import router as epigenetics_router

_app = FastAPI()
_app.include_router(epigenetics_router, prefix="/api/v1")
client = TestClient(_app)

engine = TelomerePmiEngine()


# ── VECTOR_19_PMI_A — Telomere Length at Birth / Young Donor ──────────────────

class TestVector19PmiA:
    """Verifies baseline telomere length at birth (Age 0) and young donor (Age 25)."""

    def test_birth_baseline_telomere_length(self):
        res = engine.estimate_telomere_age(ts_ratio=1.420)
        assert res["estimated_telomere_age_years"] == 0.0
        assert res["telomere_age_group"] == "NEWBORN_INFANT"

    def test_young_adult_telomere_length(self):
        res = engine.estimate_telomere_age(ts_ratio=1.2075)
        assert res["estimated_telomere_age_years"] == pytest.approx(25.0, abs=0.1)
        assert res["telomere_age_group"] == "YOUNG_ADULT"


# ── VECTOR_19_PMI_B — Telomere Length in Elderly Subjects ─────────────────────

class TestVector19PmiB:
    """Verifies telomere shortening in elderly subjects (Age 75)."""

    def test_elderly_telomere_length(self):
        res = engine.estimate_telomere_age(ts_ratio=0.7825)
        assert res["estimated_telomere_age_years"] == pytest.approx(75.0, abs=0.1)
        assert res["telomere_age_group"] == "ELDERLY"


# ── VECTOR_19_PMI_C — Delta Delta Ct to T/S Ratio Conversion ─────────────────

class TestVector19PmiC:
    """Verifies conversion from qPCR ddCt value to relative T/S ratio."""

    def test_ddct_conversion(self):
        # 2^(-0.0) = 1.0 -> Age = (1.420 - 1.0) / 0.0085 = 49.4 yrs
        res = engine.estimate_telomere_age(delta_delta_ct=0.0)
        assert res["relative_ts_ratio"] == 1.0
        assert res["estimated_telomere_age_years"] == pytest.approx(49.4, abs=0.2)
        assert res["telomere_age_group"] == "MIDDLE_AGED"


# ── VECTOR_19_PMI_D — Post-Mortem Interval (PMI) Thermal Summation ────────────

class TestVector19PmiD:
    """Verifies inverse PMI calculation from residual de-methylation under ADH."""

    def test_pmi_residual_methylation_calculation(self):
        # If observed beta is 0.50 at 20 C
        res = engine.estimate_post_mortem_interval(
            observed_beta=0.50,
            ambient_temperature_celsius=20.0,
        )

        assert res["accumulated_degree_hours"] > 0.0
        assert res["estimated_pmi_hours"] > 0.0
        assert res["estimated_pmi_days"] > 0.0
        assert len(res["pmi_confidence_interval_hours"]) == 2
        assert res["pmi_confidence_interval_hours"][0] < res["estimated_pmi_hours"] < res["pmi_confidence_interval_hours"][1]


# ── VECTOR_19_PMI_E — Ambient Temperature Effect on PMI Kinetics ─────────────

class TestVector19PmiE:
    """Verifies that colder ambient temperatures prolong estimated PMI for same residual beta."""

    def test_temperature_cooling_effect(self):
        res_warm = engine.estimate_post_mortem_interval(observed_beta=0.45, ambient_temperature_celsius=20.0)
        res_cold = engine.estimate_post_mortem_interval(observed_beta=0.45, ambient_temperature_celsius=10.0)

        # Same ADH thermal sum, but colder requires 2x hours
        assert res_warm["accumulated_degree_hours"] == pytest.approx(res_cold["accumulated_degree_hours"], abs=0.1)
        assert res_cold["estimated_pmi_hours"] == pytest.approx(res_warm["estimated_pmi_hours"] * 2.0, abs=0.5)


# ── VECTOR_19_PMI_F — Somatic Mosaicism Clonal Homogeneity ───────────────────

class TestVector19PmiF:
    """Verifies clonal homogeneity when tissue profiles exhibit minimal epigenetic drift."""

    def test_clonal_homogeneity(self):
        tissue1 = {"cg16867657": 0.22, "cg21572722": 0.20, "cg06639320": 0.18}
        tissue2 = {"cg16867657": 0.23, "cg21572722": 0.19, "cg06639320": 0.18}

        res = engine.compute_somatic_mosaicism_index(tissue1, tissue2)
        assert res["mosaicism_index_m"] < 0.05
        assert res["mosaicism_classification"] == "CLONAL_HOMOGENEITY"
        assert res["loci_evaluated"] == 3


# ── VECTOR_19_PMI_G — High Somatic Mosaicism Drift ───────────────────────────

class TestVector19PmiG:
    """Verifies high somatic mosaicism detection when tissue divergence is significant."""

    def test_high_somatic_mosaicism(self):
        tissue1 = {"cg16867657": 0.22, "cg21572722": 0.20, "cg06639320": 0.18}
        tissue2 = {"cg16867657": 0.65, "cg21572722": 0.70, "cg06639320": 0.85}

        res = engine.compute_somatic_mosaicism_index(tissue1, tissue2)
        assert res["mosaicism_index_m"] > 0.15
        assert res["mosaicism_classification"] == "HIGH_SOMATIC_MOSAICISM"


# ── VECTOR_19_PMI_H — FastAPI Endpoint Integration Tests ─────────────────────

class TestVector19PmiH:
    """Verifies FastAPI /forensic/epigenetics/telomere-and-pmi endpoint integration."""

    def test_api_comprehensive_endpoint(self):
        payload = {
            "ts_ratio": 1.10,
            "observed_pmi_beta": 0.55,
            "ambient_temperature_celsius": 18.0,
            "tissue1_betas": {"cg16867657": 0.22, "cg21572722": 0.20},
            "tissue2_betas": {"cg16867657": 0.23, "cg21572722": 0.21},
        }
        resp = client.post("/api/v1/forensic/epigenetics/telomere-and-pmi", json=payload)
        assert resp.status_code == 200
        data = resp.json()

        assert data["telomere"] is not None
        assert data["telomere"]["estimated_telomere_age_years"] == pytest.approx(37.6, abs=0.2)

        assert data["pmi"] is not None
        assert data["pmi"]["estimated_pmi_hours"] > 0.0

        assert data["mosaicism"] is not None
        assert data["mosaicism"]["mosaicism_classification"] == "CLONAL_HOMOGENEITY"
        assert "Legal Shield" in data["prosecutors_fallacy_shield"]
