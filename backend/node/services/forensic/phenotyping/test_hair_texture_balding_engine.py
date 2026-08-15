"""
Unit & Integration Tests for FORENZA Hair Texture Dynamics & Balding Risk PRS — Module 14.

Tests verbatim from Pillar 3 Research §4:
  - §4.1 Hair Fiber Cross-Sectional Area & Curl Density Index (C_curl)
  - §4.2 Androgenetic Alopecia Polygenic Risk Score (PRS_balding) and Hamilton-Norwood Scale Mapping

Golden Benchmarks:
  - VECTOR_P3_03 (East Asian EDAR Thick Straight Hair)
  - VECTOR_14_HAIR_A through H
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.phenotyping.hair_texture_balding_engine import (
    HairTextureBaldingEngine,
    HairTextureResult,
    BaldingPRSResult,
)
from app.api.phenotype_routes import router as phenotype_router

_app = FastAPI()
_app.include_router(phenotype_router, prefix="/api/v1")
client = TestClient(_app)

engine = HairTextureBaldingEngine()


# ── VECTOR_P3_03 — East Asian Thick Straight Hair & Low Balding Risk ─────────

class TestVectorP303:
    """Verifies golden vector VECTOR_P3_03 (East Asian EDAR Val370Ala derived genotype)."""

    def test_vector_p3_03_hair_morphology(self):
        # East Asian EDAR homozygous (rs3827072 = 2)
        res = engine.analyze_hair_profile({"rs3827072": 2, "rs11803731": 0, "rs7349332": 0})

        # Area = 3850 + 1420*2 = 6690.0 um^2
        assert res.texture.fiber_cross_sectional_area_um2 == pytest.approx(6690.0, abs=1e-2)
        # Curl index = max(0, 1.20 - 2.10*2) = 0.00
        assert res.texture.curl_density_index == 0.00
        assert res.texture.texture_category == "STRAIGHT"
        assert "Thick Straight" in res.texture.estimated_fiber_diameter_um


# ── VECTOR_14_HAIR_A — Baseline Reference Profile ──────────────────────────────

class TestVector14HairA:
    """Verifies baseline reference state when all effect dosages are 0."""

    def test_baseline_hair_morphology_and_balding(self):
        res = engine.analyze_hair_profile({})

        assert res.texture.fiber_cross_sectional_area_um2 == pytest.approx(3850.0, abs=1e-2)
        assert res.texture.curl_density_index == pytest.approx(1.20, abs=1e-2)
        assert res.texture.texture_category == "STRAIGHT"

        assert res.balding.prs_score == 0.00
        assert res.balding.hamilton_norwood_grade == "GRADE_I_II"
        assert res.balding.risk_level == "LOW_RISK"


# ── VECTOR_14_HAIR_B — EDAR Cross-Sectional Area Scaling ───────────────────────

class TestVector14HairB:
    """Verifies linear dosage scaling of fiber cross-sectional area via EDAR."""

    def test_edar_additive_area_scaling(self):
        area_0 = engine.compute_hair_texture({"rs3827072": 0}).fiber_cross_sectional_area_um2
        area_1 = engine.compute_hair_texture({"rs3827072": 1}).fiber_cross_sectional_area_um2
        area_2 = engine.compute_hair_texture({"rs3827072": 2}).fiber_cross_sectional_area_um2

        assert area_0 == pytest.approx(3850.0, abs=1e-2)
        assert area_1 == pytest.approx(5270.0, abs=1e-2)
        assert area_2 == pytest.approx(6690.0, abs=1e-2)
        assert (area_2 - area_1) == pytest.approx(1420.0, abs=1e-2)


# ── VECTOR_14_HAIR_C — TCHH & WNT10A Curl Induction ───────────────────────────

class TestVector14HairC:
    """Verifies high curl density index and kinky/woolly classification."""

    def test_tchh_and_wnt10a_produce_kinky_woolly_hair(self):
        # TCHH homozygous (2) + WNT10A homozygous (2)
        res = engine.compute_hair_texture({"rs11803731": 2, "rs7349332": 2, "rs3827072": 0})
        # 1.20 + 1.85*2 + 1.42*2 = 1.20 + 3.70 + 2.84 = 7.74
        assert res.curl_density_index == pytest.approx(7.74, abs=1e-2)
        assert res.texture_category == "KINKY_WOOLLY"


# ── VECTOR_14_HAIR_D — Wavy and Curly Category Transitions ────────────────────

class TestVector14HairD:
    """Verifies intermediate curl density thresholds for Wavy and Curly hair."""

    def test_wavy_texture_threshold(self):
        # TCHH heterozygous (1) -> 1.20 + 1.85 = 3.05 -> WAVY
        res = engine.compute_hair_texture({"rs11803731": 1})
        assert res.curl_density_index == pytest.approx(3.05, abs=1e-2)
        assert res.texture_category == "WAVY"

    def test_curly_texture_threshold(self):
        # TCHH homozygous (2) -> 1.20 + 3.70 = 4.90 -> CURLY
        res = engine.compute_hair_texture({"rs11803731": 2})
        assert res.curl_density_index == pytest.approx(4.90, abs=1e-2)
        assert res.texture_category == "CURLY"


# ── VECTOR_14_HAIR_E — Balding PRS Mathematical Weights ───────────────────────

class TestVector14HairE:
    """Verifies exact additive weights for androgenetic alopecia PRS."""

    def test_single_locus_prs_contributions(self):
        # AR locus rs6152 homozygous
        prs_ar = engine.compute_balding_prs({"rs6152": 2}).prs_score
        assert prs_ar == pytest.approx(1.964, abs=1e-3)

        # 20p11 locus rs2180439 heterozygous
        prs_20p = engine.compute_balding_prs({"rs2180439": 1}).prs_score
        assert prs_20p == pytest.approx(0.541, abs=1e-3)


# ── VECTOR_14_HAIR_F — Hamilton-Norwood Grade Classification ──────────────────

class TestVector14HairF:
    """Verifies 4-tier Hamilton-Norwood risk grade assignment."""

    def test_grade_i_ii_low_risk(self):
        res = engine.compute_balding_prs({"rs756853": 1})  # PRS = 0.362 < 0.50
        assert res.hamilton_norwood_grade == "GRADE_I_II"
        assert res.risk_level == "LOW_RISK"

    def test_grade_iii_moderate_risk(self):
        res = engine.compute_balding_prs({"rs6152": 1})  # PRS = 0.982 (0.50 - 1.20)
        assert res.hamilton_norwood_grade == "GRADE_III"
        assert res.risk_level == "MODERATE_RISK"

    def test_grade_iv_v_elevated_risk(self):
        res = engine.compute_balding_prs({"rs6152": 1, "rs2180439": 1})  # PRS = 0.982 + 0.541 = 1.523 (1.20 - 2.10)
        assert res.hamilton_norwood_grade == "GRADE_IV_V"
        assert res.risk_level == "ELEVATED_RISK"

    def test_grade_vi_vii_severe_risk(self):
        res = engine.compute_balding_prs({"rs6152": 2, "rs2180439": 2})  # PRS = 1.964 + 1.082 = 3.046 >= 2.10
        assert res.hamilton_norwood_grade == "GRADE_VI_VII"
        assert res.risk_level == "HIGH_RISK"


# ── VECTOR_14_HAIR_G — Mathematical Invariants & Clamping ──────────────────────

class TestVector14HairG:
    """Verifies Curl Index bounds [0.0, 10.0] and PRS non-negativity."""

    def test_curl_clamping_at_zero(self):
        # Extreme negative curl raw value
        res = engine.compute_hair_texture({"rs3827072": 2, "rs11803731": 0, "rs7349332": 0})
        assert res.curl_density_index >= 0.0

    def test_prs_maximum_boundary(self):
        # All 4 loci homozygous derived
        dosages = {"rs6152": 2, "rs2180439": 2, "rs1160312": 2, "rs756853": 2}
        prs = engine.compute_balding_prs(dosages).prs_score
        # 2 * (0.982 + 0.541 + 0.485 + 0.362) = 2 * 2.370 = 4.740
        assert prs == pytest.approx(4.740, abs=1e-3)


# ── VECTOR_14_HAIR_H — API Integration Tests ───────────────────────────────────

class TestVector14HairH:
    """Verifies FastAPI endpoints for hair morphology and balding PRS."""

    def test_api_combined_hair_endpoint(self):
        payload = {
            "snp_dosages": {"rs3827072": 2, "rs6152": 2}
        }
        resp = client.post("/api/v1/forensic/phenotyping/hair/morphology-and-balding", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "texture" in data
        assert "balding" in data
        assert data["texture"]["fiber_cross_sectional_area_um2"] == 6690.0
        assert data["balding"]["prs_score"] == 1.964

    def test_api_texture_index_endpoint(self):
        payload = {"snp_dosages": {"rs11803731": 2}}
        resp = client.post("/api/v1/forensic/phenotyping/hair/texture-index", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["texture_category"] == "CURLY"

    def test_api_balding_prs_endpoint(self):
        payload = {"snp_dosages": {"rs6152": 2, "rs2180439": 2}}
        resp = client.post("/api/v1/forensic/phenotyping/hair/balding-prs", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["hamilton_norwood_grade"] == "GRADE_VI_VII"
