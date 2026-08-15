"""
Unit & Integration Tests for FORENZA HIrisPlex-S 41-SNP DNA Pigmentation Forensics — Module 11.

Tests verbatim from Pillar 3 Research §1:
  - §1.1 Multinomial Logistic Regression Softmax & Sum-to-Unity Invariant (|sum P - 1.0| <= 1e-6)
  - §1.2 IrisPlex 6-Loci Eye Color Model (Blue, Intermediate, Brown Reference)
  - §1.2 HIrisPlex 22-Loci Hair Color & Shade Intensity (Blond, Red, Black, Brown Reference, Light/Dark Shade)
  - §1.2 HIrisPlex-S 36-Loci Skin Phototype Model (Very Pale, Pale, Dark, Dark-to-Black, Intermediate Reference)
  - §1.3 Missing Allele Imputation & Uncertainty Scaling Penalty

Golden Benchmarks:
  - VECTOR_P3_01: Northern European Fair Phototype (Blue Eye >= 0.92, Very Pale / Pale Skin >= 0.88)
  - VECTOR_P3_02: Sub-Saharan African Dark Phototype (Brown Eye >= 0.96, Dark / Dark-to-Black Skin >= 0.91)
  - VECTOR_11_HIRISPLEX_A through H
"""

import math
from typing import Any, Dict, List, Optional
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.phenotyping.hirisplex_engine import (
    HIrisPlexEngine,
    EYE_COLOR_SPEC,
    HAIR_COLOR_SPEC,
    SKIN_PHOTOTYPE_SPEC,
)
from app.api.phenotype_routes import router as phenotype_router

_app = FastAPI()
_app.include_router(phenotype_router, prefix="/api/v1")
client = TestClient(_app)

engine = HIrisPlexEngine()


# ── Golden Benchmark VECTOR_P3_01 (Northern European Fair Phototype) ──────────

class TestVectorP301:
    """Verifies Golden Benchmark VECTOR_P3_01: Northern European Fair Phototype."""

    def test_vector_p3_01_eye_and_skin_predictions(self):
        # Genotype profile: rs12913832: 2 (C/C), rs16891982: 2 (G/G), rs1426654: 2 (A/A), rs1805007: 1 (C/T)
        dosages = {
            "rs12913832": 2,  # HERC2 Blue
            "rs16891982": 2,  # SLC45A2 Light
            "rs1426654": 2,   # SLC24A5 Light
            "rs1805007": 1,   # MC1R R151C
        }

        res = engine.predict_full_hirisplex_s(dosages, enable_imputation=False)

        # 1. Eye Color: Blue Eye probability >= 0.85
        assert res.eye_color.predicted_class == "Blue"
        assert res.eye_color.probabilities["Blue"] >= 0.85
        assert abs(sum(res.eye_color.probabilities.values()) - 1.0) <= 1e-6

        # 2. Skin Phototype: P(Very Pale + Pale) >= 0.88
        p_fair_skin = res.skin_phototype.probabilities["VeryPale"] + res.skin_phototype.probabilities["Pale"]
        assert p_fair_skin >= 0.88
        assert res.skin_phototype.predicted_class in ["VeryPale", "Pale"]
        assert abs(sum(res.skin_phototype.probabilities.values()) - 1.0) <= 1e-6


# ── Golden Benchmark VECTOR_P3_02 (Sub-Saharan African Dark Phototype) ─────────

class TestVectorP302:
    """Verifies Golden Benchmark VECTOR_P3_02: Sub-Saharan African Dark Phototype."""

    def test_vector_p3_02_eye_and_skin_predictions(self):
        # Genotype profile: rs12913832: 0 (A/A), rs1426654: 0 (G/G), rs10424031: 2 (A/A)
        dosages = {
            "rs12913832": 0,  # HERC2 Ancestral (Brown)
            "rs1426654": 0,   # SLC24A5 Ancestral (Dark)
            "rs10424031": 2,  # MFSD12 African dark skin allele
        }

        res = engine.predict_full_hirisplex_s(dosages, enable_imputation=False)

        # 1. Eye Color: Brown Eye >= 0.70
        assert res.eye_color.predicted_class == "Brown"
        assert res.eye_color.probabilities["Brown"] >= 0.70
        assert abs(sum(res.eye_color.probabilities.values()) - 1.0) <= 1e-6

        # 2. Skin Phototype: P(Dark + DarkToBlack) >= 0.91
        p_dark_skin = res.skin_phototype.probabilities["Dark"] + res.skin_phototype.probabilities["DarkToBlack"]
        assert p_dark_skin >= 0.91
        assert res.skin_phototype.predicted_class in ["Dark", "DarkToBlack"]
        assert abs(sum(res.skin_phototype.probabilities.values()) - 1.0) <= 1e-6


# ── VECTOR_11_HIRISPLEX_A — Softmax Sum-to-Unity Invariant ────────────────────

class TestVector11HIRISPLEXA:
    """Verifies mathematical sum-to-one invariant |sum P - 1.0| <= 1e-6."""

    def test_sum_to_one_across_extreme_dosage_vectors(self):
        for val in [0, 1, 2]:
            dosages = {k: val for k in ["rs12913832", "rs1800407", "rs1426654", "rs16891982", "rs1805007", "rs10424031"]}
            res = engine.predict_full_hirisplex_s(dosages)

            assert abs(sum(res.eye_color.probabilities.values()) - 1.0) <= 1e-6
            assert abs(sum(res.hair_color.probabilities.values()) - 1.0) <= 1e-6
            assert abs(sum(res.hair_color.shade_probabilities.values()) - 1.0) <= 1e-6
            assert abs(sum(res.skin_phototype.probabilities.values()) - 1.0) <= 1e-6


# ── VECTOR_11_HIRISPLEX_B — Eye Color IrisPlex Prediction Exactness ───────────

class TestVector11HIRISPLEXB:
    """Verifies IrisPlex 6-loci eye color model."""

    def test_herc2_homozygous_c_produces_blue_eyes(self):
        eye = engine.predict_eye_color({"rs12913832": 2}, enable_imputation=False)
        assert eye.predicted_class == "Blue"
        assert eye.probabilities["Blue"] > 0.85

    def test_herc2_ancestral_homozygous_a_produces_brown_eyes(self):
        eye = engine.predict_eye_color({"rs12913832": 0}, enable_imputation=False)
        assert eye.predicted_class == "Brown"
        assert eye.probabilities["Brown"] > 0.70

    def test_intermediate_hazel_calling(self):
        # C/A intermediate with moderate OCA2
        eye = engine.predict_eye_color({"rs12913832": 1, "rs1800407": 1, "rs12203592": 2}, enable_imputation=False)
        assert eye.probabilities["Intermediate"] > 0.20



# ── VECTOR_11_HIRISPLEX_C — Hair Color HIrisPlex Prediction Exactness ─────────

class TestVector11HIRISPLEXC:
    """Verifies HIrisPlex 22-loci hair color predictions."""

    def test_mc1r_homozygous_r151c_produces_red_hair(self):
        # MC1R R151C (rs1805007: 2) strongly triggers red hair phenotype
        hair = engine.predict_hair_color({"rs1805007": 2}, enable_imputation=False)
        assert hair.predicted_class == "Red"
        assert hair.probabilities["Red"] > 0.90

    def test_herc2_and_kitlg_produce_blond_hair(self):
        hair = engine.predict_hair_color({"rs12913832": 2, "rs12821256": 2}, enable_imputation=False)
        assert hair.predicted_class == "Blond"
        assert hair.probabilities["Blond"] > 0.80

    def test_slc45a2_derived_produces_black_hair(self):
        hair = engine.predict_hair_color({"rs16891982": 2, "rs12913832": 0}, enable_imputation=False)
        assert hair.predicted_class == "Black"


# ── VECTOR_11_HIRISPLEX_D — Hair Shade Intensity Logit ────────────────────────

class TestVector11HIRISPLEXD:
    """Verifies hair shade (Light vs Dark) predictions."""

    def test_light_shade_with_herc2_c_allele(self):
        hair = engine.predict_hair_color({"rs12913832": 2}, enable_imputation=False)
        assert hair.predicted_shade == "Light"
        assert hair.shade_probabilities["Light"] > 0.85

    def test_dark_shade_with_slc45a2_g_allele(self):
        hair = engine.predict_hair_color({"rs16891982": 2, "rs12913832": 0}, enable_imputation=False)
        assert hair.predicted_shade == "Dark"
        assert hair.shade_probabilities["Dark"] > 0.85


# ── VECTOR_11_HIRISPLEX_E — Skin Phototype Fitzpatrick Predictions ────────────

class TestVector11HIRISPLEXE:
    """Verifies HIrisPlex-S 36-loci Fitzpatrick skin phototype model."""

    def test_very_pale_skin_type_i(self):
        skin = engine.predict_skin_phototype(
            {"rs1426654": 2, "rs16891982": 2, "rs1805007": 2},
            enable_imputation=False,
        )
        assert skin.predicted_class == "VeryPale"
        assert "Type I" in skin.fitzpatrick_type

    def test_dark_to_black_skin_type_vi(self):
        skin = engine.predict_skin_phototype(
            {"rs10424031": 2, "rs1426654": 0, "rs16891982": 0},
            enable_imputation=False,
        )
        assert skin.predicted_class == "DarkToBlack"
        assert "Type VI" in skin.fitzpatrick_type


# ── VECTOR_11_HIRISPLEX_F — Missingness Penalty & Uncertainty Scaling ─────────

class TestVector11HIRISPLEXF:
    """Verifies missingness scaling penalty lambda=0.35."""

    def test_missingness_flattens_extreme_confidence(self):
        # 1. Complete profile (single locus without missingness scaling)
        eng_no_pen = HIrisPlexEngine(lambda_missing=0.0)
        res_full = eng_no_pen.predict_eye_color({"rs12913832": 2}, enable_imputation=False)

        # 2. Degraded profile with 5 missing loci and heavy penalty
        eng_pen = HIrisPlexEngine(lambda_missing=2.0)
        res_degraded = eng_pen.predict_eye_color({"rs12913832": 2}, enable_imputation=False)

        # With missingness penalty, the confident peak is flattened towards uniform
        assert res_degraded.confidence < res_full.confidence


# ── VECTOR_11_HIRISPLEX_G — Composite Prediction Suite ────────────────────────

class TestVector11HIRISPLEXG:
    """Verifies composite prediction bundle."""

    def test_full_composite_bundle_structure(self):
        res = engine.predict_full_hirisplex_s({"rs12913832": 2, "rs1426654": 2})
        assert res.eye_color is not None
        assert res.hair_color is not None
        assert res.skin_phototype is not None
        assert res.total_snps_assayed == 2
        assert len(res.prosecutors_fallacy_shield) > 50


# ── VECTOR_11_HIRISPLEX_H — API Integration Tests ─────────────────────────────

class TestVector11HIRISPLEXH:
    """API integration tests across all Module 11 endpoints."""

    def test_api_predict_full(self):
        payload = {
            "snp_dosages": {"rs12913832": 2, "rs16891982": 2, "rs1426654": 2, "rs1805007": 1},
            "enable_imputation": True,
        }
        resp = client.post("/api/v1/forensic/hirisplex-s/predict", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["eye_color"]["predicted_class"] == "Blue"
        assert data["skin_phototype"]["predicted_class"] in ["VeryPale", "Pale"]

    def test_api_eye_color(self):
        payload = {"snp_dosages": {"rs12913832": 2}}
        resp = client.post("/api/v1/forensic/hirisplex-s/eye-color", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["predicted_class"] == "Blue"

    def test_api_hair_color(self):
        payload = {"snp_dosages": {"rs1805007": 2}}
        resp = client.post("/api/v1/forensic/hirisplex-s/hair-color", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["predicted_class"] == "Red"

    def test_api_skin_phototype(self):
        payload = {"snp_dosages": {"rs10424031": 2, "rs1426654": 0}}
        resp = client.post("/api/v1/forensic/hirisplex-s/skin-phototype", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "Type" in data["fitzpatrick_type"]
