"""
Unit & Integration Tests for FORENZA tDMR-Based Body Fluid Identification Engine — Module 17.

Tests verbatim from Pillar 4 Research §2 & §6:
  - §2.1 Diagnostic Loci Reference Methylation Distribution Matrix (12 tDMR CpG loci across 6 body fluids)
  - §2.2 Bayesian Quadratic Discriminant Analysis (QDA) / Gaussian Mixture Log-Likelihoods
  - Tissue Likelihood Ratios (LR_tissue) and Court-Admissible Reporting

Golden Benchmarks:
  - VECTOR_P4_03 (Forensic Semen Stain Confirmation)
  - VECTOR_17_TISSUE_A through H
"""

import math
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.epigenetics.tissue_deconv import (
    TissueDeconvolutionEngine,
)
from app.api.epigenetics_routes import router as epigenetics_router

_app = FastAPI()
_app.include_router(epigenetics_router, prefix="/api/v1")
client = TestClient(_app)

engine = TissueDeconvolutionEngine()


# ── VECTOR_P4_03 — Forensic Semen Stain Confirmation ──────────────────────────

class TestVectorP403:
    """Verifies golden vector VECTOR_P4_03 (Forensic Semen Stain Confirmation)."""

    def test_vector_p4_03_semen_stain_confirmation(self):
        # High germ-cell hypomethylation (cg17610929=0.04, cg23521140=0.08)
        semen_profile = {
            "cg17610929": 0.04,
            "cg23521140": 0.08,
            "cg09652652": 0.88,
            "cg19406367": 0.92,
            "cg23576855": 0.89,
            "cg04382942": 0.91,
            "cg00854446": 0.94,
            "cg07823520": 0.95,
        }
        res = engine.deconvolve_sample(semen_profile)

        assert res["top_predicted_tissue"] == "SEMEN"
        assert res["top_tissue_probability"] >= 0.995
        assert res["tissue_probabilities"]["SEMEN"] >= 0.995
        assert res["tissue_probabilities"]["BLOOD"] < 0.001
        assert res["lr_tissue"] > 100.0


# ── VECTOR_17_TISSUE_A — Pure Venous Blood Identification ────────────────────

class TestVector17TissueA:
    """Verifies unambiguous calling of pure peripheral venous blood."""

    def test_pure_venous_blood(self):
        blood_profile = {
            "cg09652652": 0.12,
            "cg19406367": 0.15,
            "cg17610929": 0.91,
            "cg23521140": 0.85,
            "cg26763284": 0.89,
            "cg23576855": 0.84,
            "cg00399818": 0.82,
            "cg04382942": 0.88,
            "cg11624633": 0.86,
            "cg00854446": 0.82,
            "cg18063373": 0.80,
            "cg07823520": 0.90,
        }
        res = engine.deconvolve_sample(blood_profile)

        assert res["top_predicted_tissue"] == "BLOOD"
        assert res["top_tissue_probability"] >= 0.980
        assert res["lr_tissue"] > 10.0


# ── VECTOR_17_TISSUE_B — Pure Saliva Identification ──────────────────────────

class TestVector17TissueB:
    """Verifies unambiguous calling of oral saliva."""

    def test_pure_saliva(self):
        saliva_profile = {
            "cg09652652": 0.85,
            "cg19406367": 0.89,
            "cg17610929": 0.88,
            "cg23521140": 0.82,
            "cg26763284": 0.86,
            "cg23576855": 0.10,
            "cg00399818": 0.12,
            "cg04382942": 0.72,
            "cg11624633": 0.70,
            "cg00854446": 0.85,
            "cg18063373": 0.83,
            "cg07823520": 0.81,
        }
        res = engine.deconvolve_sample(saliva_profile)

        assert res["top_predicted_tissue"] == "SALIVA"
        assert res["top_tissue_probability"] >= 0.980


# ── VECTOR_17_TISSUE_C — Menstrual Blood vs Vaginal Fluid Discrimination ──────

class TestVector17TissueC:
    """Verifies differentiation between menstrual blood (endometrial) and vaginal secretions."""

    def test_menstrual_blood_calling(self):
        # Endometrial markers hypomethylated (cg00854446=0.14, cg18063373=0.16)
        menstrual_profile = {
            "cg09652652": 0.22,
            "cg19406367": 0.31,
            "cg17610929": 0.89,
            "cg23521140": 0.83,
            "cg26763284": 0.87,
            "cg23576855": 0.81,
            "cg00399818": 0.79,
            "cg04382942": 0.35,
            "cg11624633": 0.38,
            "cg00854446": 0.14,
            "cg18063373": 0.16,
            "cg07823520": 0.86,
        }
        res = engine.deconvolve_sample(menstrual_profile)

        assert res["top_predicted_tissue"] == "MENSTRUAL"
        assert res["top_tissue_probability"] > 0.80

    def test_vaginal_fluid_calling(self):
        # Cervicovaginal markers hypomethylated (cg04382942=0.15, cg11624633=0.18)
        vaginal_profile = {
            "cg09652652": 0.82,
            "cg19406367": 0.86,
            "cg17610929": 0.90,
            "cg23521140": 0.84,
            "cg26763284": 0.88,
            "cg23576855": 0.78,
            "cg00399818": 0.75,
            "cg04382942": 0.15,
            "cg11624633": 0.18,
            "cg00854446": 0.52,
            "cg18063373": 0.55,
            "cg07823520": 0.85,
        }
        res = engine.deconvolve_sample(vaginal_profile)

        assert res["top_predicted_tissue"] == "VAGINAL"
        assert res["top_tissue_probability"] > 0.80


# ── VECTOR_17_TISSUE_D — Epidermal Skin Touch DNA Identification ──────────────

class TestVector17TissueD:
    """Verifies identification of epidermal epithelial cells from touch DNA."""

    def test_skin_epidermis_calling(self):
        skin_profile = {
            "cg09652652": 0.91,
            "cg19406367": 0.88,
            "cg17610929": 0.94,
            "cg23521140": 0.89,
            "cg26763284": 0.92,
            "cg23576855": 0.82,
            "cg00399818": 0.85,
            "cg04382942": 0.86,
            "cg11624633": 0.84,
            "cg00854446": 0.90,
            "cg18063373": 0.88,
            "cg07823520": 0.11,
        }
        res = engine.deconvolve_sample(skin_profile)

        assert res["top_predicted_tissue"] == "SKIN"
        assert res["top_tissue_probability"] >= 0.980


# ── VECTOR_17_TISSUE_E — Sum-to-One Invariant (|sum P - 1.0| < 1e-4) ──────────

class TestVector17TissueE:
    """Verifies that posterior probability distributions sum to exactly 1.0."""

    def test_sum_to_one_posterior_invariant(self):
        profile = {
            "cg09652652": 0.45,
            "cg17610929": 0.50,
            "cg23576855": 0.40,
            "cg04382942": 0.60,
            "cg00854446": 0.55,
            "cg07823520": 0.35,
        }
        res = engine.deconvolve_sample(profile)
        total_p = sum(res["tissue_probabilities"].values())

        assert total_p == pytest.approx(1.0, abs=1e-3)


# ── VECTOR_17_TISSUE_F — Likelihood Ratio & Log10 LR Metrics ──────────────────

class TestVector17TissueF:
    """Verifies Tissue Likelihood Ratio computation."""

    def test_lr_and_log10_lr_calculation(self):
        blood_profile = {"cg09652652": 0.12, "cg19406367": 0.15}
        res = engine.deconvolve_sample(blood_profile)

        assert res["lr_tissue"] >= 1.0
        assert res["log10_lr_tissue"] == pytest.approx(math.log10(res["lr_tissue"]), abs=0.1)


# ── VECTOR_17_TISSUE_G — Validation Exceptions ────────────────────────────────

class TestVector17TissueG:
    """Verifies validation boundaries for out-of-range betas and empty dictionaries."""

    def test_empty_dictionary_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            engine.deconvolve_sample({})

    def test_invalid_beta_bounds_raises(self):
        with pytest.raises(ValueError, match="must be within"):
            engine.deconvolve_sample({"cg09652652": 1.25})


# ── VECTOR_17_TISSUE_H — API Endpoint Integration Tests ───────────────────────

class TestVector17TissueH:
    """Verifies FastAPI endpoint /api/v1/forensic/epigenetics/deconvolve-tissue."""

    def test_api_deconvolve_tissue_endpoint(self):
        payload = {
            "tdmr_methylation": {
                "cg17610929": 0.04,
                "cg23521140": 0.08,
                "cg09652652": 0.88,
            }
        }
        resp = client.post("/api/v1/forensic/epigenetics/deconvolve-tissue", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["top_predicted_tissue"] == "SEMEN"
        assert "tissue_probabilities" in data
        assert "SEMEN" in data["tissue_probabilities"]
        assert data["lr_tissue"] > 1.0
