"""
Unit & Integration Tests for FORENZA Environmental Epigenetics & Lifestyle Biomarkers Engine — Module 18.

Tests verbatim from Pillar 4 Research §3 & §6:
  - §3.1 Quantitative Cigarette Smoking Biomarker Model (AHRR cg05575921, F2RL3 cg03636183, ALPPL2 cg01940273 & Pack-Years)
  - §3.2 Epigenetic Body Mass Index (BMI) Model (ABCG1 cg06500161, CPT1A cg00574958, SREBF1 cg11024682)
  - Alcohol Exposure Index (SLC6A3) & Circadian Diurnal Time-of-Deposition (PER2 / BMAL1)
  - Biological Age Acceleration (Delta Age)

Golden Benchmarks:
  - VECTOR_18_LIFE_A through H
"""

import math
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.epigenetics.lifestyle_engine import (
    LifestyleEpigeneticEngine,
)
from app.api.epigenetics_routes import router as epigenetics_router

_app = FastAPI()
_app.include_router(epigenetics_router, prefix="/api/v1")
client = TestClient(_app)

engine = LifestyleEpigeneticEngine()


# ── VECTOR_18_LIFE_A — Never Smoker Baseline ──────────────────────────────────

class TestVector18LifeA:
    """Verifies baseline never-smoker classification and 0.0 pack-years."""

    def test_never_smoker_profile(self):
        res = engine.analyze_lifestyle_profile(
            ahrr_cg05575921_beta=0.88,
            f2rl3_beta=0.82,
            alppl2_beta=0.84,
        )

        assert res["smoking_status"] == "NON_SMOKER"
        assert res["smoking_score"] < 1.50
        assert res["estimated_pack_years"] == 0.0
        assert res["smoking_probability"] >= 0.80


# ── VECTOR_18_LIFE_B — Active Heavy Smoker with High Pack-Years ───────────────

class TestVector18LifeB:
    """Verifies severe hypomethylation in heavy smokers (>40 pack-years, score > 6.0)."""

    def test_active_heavy_smoker_profile(self):
        res = engine.analyze_lifestyle_profile(
            ahrr_cg05575921_beta=0.32,
            f2rl3_beta=0.28,
            alppl2_beta=0.30,
        )

        assert res["smoking_status"] == "CURRENT_HEAVY_SMOKER"
        assert res["smoking_score"] > 6.00
        assert res["estimated_pack_years"] >= 40.0
        assert res["smoking_probability"] >= 0.90


# ── VECTOR_18_LIFE_C — Former / Light Smoker Profile ──────────────────────────

class TestVector18LifeC:
    """Verifies moderate hypomethylation in former/light smokers."""

    def test_former_or_light_smoker_profile(self):
        res = engine.analyze_lifestyle_profile(
            ahrr_cg05575921_beta=0.65,
            f2rl3_beta=0.50,
            alppl2_beta=0.55,
        )

        assert res["smoking_status"] == "FORMER_OR_LIGHT_SMOKER"
        assert 1.50 <= res["smoking_score"] <= 4.50
        assert 1.0 <= res["estimated_pack_years"] <= 20.0


# ── VECTOR_18_LIFE_D — Epigenetic BMI Normal Weight Calculation ───────────────

class TestVector18LifeD:
    """Verifies epigenetic BMI model for normal weight subjects."""

    def test_normal_bmi_calculation(self):
        res = engine.analyze_lifestyle_profile(
            abcg1_beta=0.35,
            cpt1a_beta=0.45,
            srebf1_beta=0.30,
        )

        assert res["estimated_bmi"] == pytest.approx(24.4, abs=0.5)
        assert res["bmi_category"] == "NORMAL_WEIGHT"


# ── VECTOR_18_LIFE_E — Epigenetic BMI Obesity Calculation ─────────────────────

class TestVector18LifeE:
    """Verifies epigenetic BMI model for obese subjects."""

    def test_obese_bmi_calculation(self):
        res = engine.analyze_lifestyle_profile(
            abcg1_beta=0.75,
            cpt1a_beta=0.15,
            srebf1_beta=0.65,
        )

        assert res["estimated_bmi"] >= 35.0
        assert res["bmi_category"] == "OBESITY_CLASS_2_PLUS"


# ── VECTOR_18_LIFE_F — Alcohol Exposure Index Tiers ───────────────────────────

class TestVector18LifeF:
    """Verifies SLC6A3-based alcohol exposure index."""

    def test_heavy_alcohol_exposure(self):
        res = engine.analyze_lifestyle_profile(slc6a3_beta=0.10)
        assert res["alcohol_index_score"] >= 40.0
        assert res["alcohol_exposure_level"] == "HEAVY_CHRONIC_EXPOSURE"

    def test_abstainer_alcohol_exposure(self):
        res = engine.analyze_lifestyle_profile(slc6a3_beta=0.50)
        assert res["alcohol_index_score"] == 0.0
        assert res["alcohol_exposure_level"] == "LOW_OR_ABSTAINER"


# ── VECTOR_18_LIFE_G — Circadian Phase & Time-of-Deposition Windows ───────────

class TestVector18LifeG:
    """Verifies PER2/BMAL1 circadian phase estimation."""

    def test_nocturnal_phase(self):
        res = engine.analyze_lifestyle_profile(per2_beta=0.80, bmal1_beta=0.40)
        assert res["circadian_phase"] == "NOCTURNAL_PEAK_NIGHT"
        assert "22:00" in res["estimated_tod_window"]

    def test_diurnal_phase(self):
        res = engine.analyze_lifestyle_profile(per2_beta=0.50, bmal1_beta=0.50)
        assert res["circadian_phase"] == "DIURNAL_PEAK_DAYTIME"
        assert "10:00" in res["estimated_tod_window"]

    def test_matutinal_phase(self):
        res = engine.analyze_lifestyle_profile(per2_beta=0.20, bmal1_beta=0.70)
        assert res["circadian_phase"] == "MATUTINAL_PEAK_MORNING"
        assert "04:00" in res["estimated_tod_window"]



# ── VECTOR_18_LIFE_H — Age Acceleration Delta & API Integration ───────────────

class TestVector18LifeH:
    """Verifies age acceleration delta calculation and FastAPI endpoint integration."""

    def test_age_acceleration_integration(self):
        res = engine.analyze_lifestyle_profile(
            chronological_age=30.0,
            estimated_dnam_age=38.5,
        )
        assert res["age_acceleration_delta"] == pytest.approx(8.5, abs=0.1)
        assert res["aging_status"] == "ACCELERATED_BIOLOGICAL_AGING"

    def test_api_lifestyle_profile_endpoint(self):
        payload = {
            "ahrr_cg05575921_beta": 0.35,
            "f2rl3_beta": 0.30,
            "alppl2_beta": 0.32,
            "abcg1_beta": 0.50,
            "cpt1a_beta": 0.30,
            "srebf1_beta": 0.40,
            "slc6a3_beta": 0.25,
            "per2_beta": 0.70,
            "bmal1_beta": 0.30,
            "chronological_age": 45.0,
            "estimated_dnam_age": 52.0,
        }
        resp = client.post("/api/v1/forensic/epigenetics/lifestyle-profile", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["smoking_status"] == "CURRENT_HEAVY_SMOKER"
        assert data["estimated_pack_years"] >= 35.0
        assert data["estimated_bmi"] is not None
        assert data["circadian_phase"] == "NOCTURNAL_PEAK_NIGHT"
        assert data["aging_status"] == "ACCELERATED_BIOLOGICAL_AGING"
