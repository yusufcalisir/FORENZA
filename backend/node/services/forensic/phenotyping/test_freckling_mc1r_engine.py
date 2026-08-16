"""
Unit & Integration Tests for FORENZA Ephelides (Freckling), MC1R Epistasis & UV Sensitivity — Module 15.

Tests verbatim from Pillar 3 Research §5:
  - §5.1 MC1R Functional Variant Classification Matrix ('R', 'r', wt)
  - §5.2 Compound Heterozygosity and Quantitative Freckling Score (F_score)
  - Minimal Erythema Dose (MED) & UV Sensitivity Tiers

Golden Benchmarks:
  - VECTOR_15_FRECKLE_A through H
"""

import math
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.phenotyping.freckling_mc1r_engine import (
    FrecklingMC1REngine,
    MC1RDiplotypeResult,
    FrecklingScoreResult,
    UVSensitivityResult,
)
from app.api.phenotype_routes import router as phenotype_router

_app = FastAPI()
_app.include_router(phenotype_router, prefix="/api/v1")
client = TestClient(_app)

engine = FrecklingMC1REngine()


# ── VECTOR_15_FRECKLE_A — Baseline Wild-Type Profile ──────────────────────────

class TestVector15FreckleA:
    """Verifies baseline wild-type state (wt/wt) with low freckling score and high MED."""

    def test_baseline_wildtype_profile(self):
        res = engine.analyze_ephelides_profile({})

        assert res.mc1r.diplotype == "wt/wt"
        assert res.mc1r.functional_classification == "WILD_TYPE"
        assert res.mc1r.total_mc1r_loss_weight == 0.0

        # logit = -2.50 -> 100 / (1 + exp(2.50)) = 7.59%
        assert res.freckling.freckling_score_pct == pytest.approx(7.59, abs=0.1)
        assert res.freckling.freckling_intensity == "MINIMAL (Rare / No Visible Ephelides)"

        assert "> 50 mJ/cm2" in res.uv_sensitivity.minimal_erythema_dose_category
        assert res.uv_sensitivity.tanning_capacity == "NORMAL_TAN_RARE_BURN"


# ── VECTOR_15_FRECKLE_B — Homozygous 'R' High-Risk Allele ─────────────────────

class TestVector15FreckleB:
    """Verifies homozygous 'R' allele (R151C rs1805007 = 2) producing dense freckles."""

    def test_homozygous_r_r151c_severe_loss(self):
        res = engine.analyze_ephelides_profile({"rs1805007": 2})

        assert res.mc1r.diplotype == "R/R"
        assert res.mc1r.functional_classification == "SEVERE_LOSS"
        assert res.mc1r.total_mc1r_loss_weight == pytest.approx(5.70, abs=1e-3)
        assert res.mc1r.r_high_risk_alleles_count == 2

        # logit = -2.50 + 1.35*5.70 = 5.195 -> 99.45%
        assert res.freckling.freckling_score_pct >= 99.0
        assert "DENSE" in res.freckling.freckling_intensity

        assert "< 20 mJ/cm2" in res.uv_sensitivity.minimal_erythema_dose_category
        assert res.uv_sensitivity.tanning_capacity == "NEVER_TANS_ALWAYS_BURNS"


# ── VECTOR_15_FRECKLE_C — Compound Heterozygosity R/r ─────────────────────────

class TestVector15FreckleC:
    """Verifies compound heterozygosity with one 'R' and one 'r' variant."""

    def test_compound_heterozygous_r_and_r_variants(self):
        # rs1805007 (R151C, Class R, w=2.85) + rs1805005 (V60L, Class r, w=1.10)
        res = engine.analyze_ephelides_profile({"rs1805007": 1, "rs1805005": 1})

        assert res.mc1r.diplotype == "R/r"
        assert res.mc1r.functional_classification == "MODERATE_LOSS"
        assert res.mc1r.total_mc1r_loss_weight == pytest.approx(3.95, abs=1e-3)
        assert res.mc1r.r_high_risk_alleles_count == 1
        assert res.mc1r.r_low_risk_alleles_count == 1

        # logit = -2.50 + 1.35*3.95 = 2.8325 -> 94.44%
        assert res.freckling.freckling_score_pct == pytest.approx(94.44, abs=0.2)
        assert "20 - 35 mJ/cm2" in res.uv_sensitivity.minimal_erythema_dose_category
        assert res.uv_sensitivity.tanning_capacity == "RARE_TAN_FREQUENT_BURN"


# ── VECTOR_15_FRECKLE_D — Partial Loss r/r Diplotype ──────────────────────────

class TestVector15FreckleD:
    """Verifies homozygous 'r' low-risk variants (r/r diplotype)."""

    def test_homozygous_r_partial_loss(self):
        # rs1805005 (V60L, Class r, w=1.10) homozygous -> dosage = 2
        res = engine.analyze_ephelides_profile({"rs1805005": 2})

        assert res.mc1r.diplotype == "r/r"
        assert res.mc1r.functional_classification == "MILD_LOSS"
        assert res.mc1r.total_mc1r_loss_weight == pytest.approx(2.20, abs=1e-3)
        assert res.mc1r.r_high_risk_alleles_count == 0
        assert res.mc1r.r_low_risk_alleles_count == 2

        # logit = -2.50 + 1.35*2.20 = 0.47 -> 61.54%
        assert res.freckling.freckling_score_pct == pytest.approx(61.54, abs=0.2)
        assert "MODERATE" in res.freckling.freckling_intensity
        assert "35 - 50 mJ/cm2" in res.uv_sensitivity.minimal_erythema_dose_category


# ── VECTOR_15_FRECKLE_E — Single 'r' Variant Carrier r/wt ─────────────────────

class TestVector15FreckleE:
    """Verifies single 'r' carrier (r/wt diplotype)."""

    def test_single_r_carrier(self):
        # rs885479 (R163Q, Class r, w=0.75) heterozygous -> dosage = 1
        res = engine.analyze_ephelides_profile({"rs885479": 1})

        assert res.mc1r.diplotype == "r/wt"
        assert res.mc1r.functional_classification == "MILD_LOSS"
        assert res.mc1r.total_mc1r_loss_weight == pytest.approx(0.75, abs=1e-3)

        # logit = -2.50 + 1.35*0.75 = -1.4875 -> 18.43%
        assert res.freckling.freckling_score_pct == pytest.approx(18.43, abs=0.2)
        assert res.freckling.freckling_intensity == "MINIMAL (Rare / No Visible Ephelides)"


# ── VECTOR_15_FRECKLE_F — ASIP & BNC2 Epistatic Boosting ───────────────────────

class TestVector15FreckleF:
    """Verifies epistatic modifier boosting via ASIP rs1015362 and BNC2 rs10756819."""

    def test_asip_and_bnc2_boost_freckling_score(self):
        # Baseline with no MC1R mutations but with ASIP (2) + BNC2 (2)
        res = engine.analyze_ephelides_profile({"rs1015362": 2, "rs10756819": 2})

        # logit = -2.50 + 0.85*2 + 0.65*2 = -2.50 + 1.70 + 1.30 = 0.50 -> 62.25%
        assert res.freckling.freckling_score_pct == pytest.approx(62.25, abs=0.2)
        assert res.freckling.freckling_score_pct > 7.59  # Substantial increase over pure wild-type


# ── VECTOR_15_FRECKLE_G — Mathematical Invariants & Clamping ──────────────────

class TestVector15FreckleG:
    """Verifies F_score strictly clamped in [0.0, 100.0]%."""

    def test_f_score_bounds(self):
        # Extreme positive dosages
        extreme_dosages = {
            "rs1805007": 2, "rs1805008": 2, "rs1015362": 2, "rs10756819": 2
        }
        res = engine.analyze_ephelides_profile(extreme_dosages)
        assert 0.0 <= res.freckling.freckling_score_pct <= 100.0


# ── VECTOR_15_FRECKLE_H — API Integration Tests ─────────────────────────────────

class TestVector15FreckleH:
    """Verifies FastAPI endpoints for freckling score and MC1R diplotyping."""

    def test_api_freckling_and_uv_endpoint(self):
        payload = {"snp_dosages": {"rs1805007": 2, "rs1015362": 1}}
        resp = client.post("/api/v1/forensic/phenotyping/ephelides/freckling-and-uv", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "mc1r" in data
        assert "freckling" in data
        assert "uv_sensitivity" in data
        assert data["mc1r"]["diplotype"] == "R/R"
        assert data["freckling"]["freckling_score_pct"] >= 99.0

    def test_api_mc1r_genotype_endpoint(self):
        payload = {"snp_dosages": {"rs1805006": 1, "rs1805005": 1}}
        resp = client.post("/api/v1/forensic/phenotyping/ephelides/mc1r-genotype", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["diplotype"] == "R/r"
        assert data["total_mc1r_loss_weight"] == pytest.approx(3.60, abs=1e-2)
