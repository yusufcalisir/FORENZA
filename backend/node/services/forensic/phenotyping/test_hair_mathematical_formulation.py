"""
Mathematical Formulation Tests for FORENZA Hair Morphology & Balding PRS (Module 3.4).

Verifies verbatim constants from Pillar 3 Research §4:
  - §4.1 Fiber Area baseline (3850.0 μm²), EDAR weight (+1420.0 μm²/allele)
  - §4.1 Curl Density Index baseline (1.20), TCHH (+1.85), WNT10A (+1.42), EDAR (-2.10)
  - §4.1 Texture category thresholds (<2.0, <4.5, <7.0)
  - §4.2 PRS weights: AR=0.982, 20p11a=0.541, 20p11b=0.485, HDAC9=0.362
  - §4.2 Hamilton-Norwood thresholds: <0.50, <1.20, <2.10
"""

import math
import pytest

from backend.node.services.forensic.phenotyping.hair_mathematical_formulation import (
    HairMathematicalFormulation,
    HAIR_TEXTURE_LOCI,
    BALDING_PRS_LOCI,
    FIBER_AREA_BASELINE_UM2,
    CURL_INDEX_BASELINE,
    HN_GRADE_I_II_THRESHOLD,
    HN_GRADE_III_THRESHOLD,
    HN_GRADE_IV_V_THRESHOLD,
    CURL_CLAMP_MIN,
    CURL_CLAMP_MAX,
)


class TestHairLociRegistry:
    """Verifies the primary loci registry constants."""

    def test_texture_loci_count(self):
        assert len(HAIR_TEXTURE_LOCI) == 3

    def test_texture_loci_rsids(self):
        assert "rs3827072" in HAIR_TEXTURE_LOCI  # EDAR
        assert "rs11803731" in HAIR_TEXTURE_LOCI  # TCHH
        assert "rs7349332" in HAIR_TEXTURE_LOCI   # WNT10A

    def test_balding_loci_count(self):
        assert len(BALDING_PRS_LOCI) == 4

    def test_balding_loci_rsids(self):
        assert "rs6152" in BALDING_PRS_LOCI    # AR
        assert "rs2180439" in BALDING_PRS_LOCI  # 20p11
        assert "rs1160312" in BALDING_PRS_LOCI  # 20p11
        assert "rs756853" in BALDING_PRS_LOCI   # HDAC9

    def test_edar_area_weight(self):
        assert HAIR_TEXTURE_LOCI["rs3827072"]["weight_area_um2"] == pytest.approx(1420.0, abs=1e-9)

    def test_edar_curl_weight(self):
        assert HAIR_TEXTURE_LOCI["rs3827072"]["weight_curl"] == pytest.approx(-2.10, abs=1e-9)

    def test_tchh_curl_weight(self):
        assert HAIR_TEXTURE_LOCI["rs11803731"]["weight_curl"] == pytest.approx(1.85, abs=1e-9)

    def test_wnt10a_curl_weight(self):
        assert HAIR_TEXTURE_LOCI["rs7349332"]["weight_curl"] == pytest.approx(1.42, abs=1e-9)

    def test_ar_prs_weight(self):
        assert BALDING_PRS_LOCI["rs6152"]["weight_prs"] == pytest.approx(0.982, abs=1e-9)

    def test_20p11a_prs_weight(self):
        assert BALDING_PRS_LOCI["rs2180439"]["weight_prs"] == pytest.approx(0.541, abs=1e-9)

    def test_20p11b_prs_weight(self):
        assert BALDING_PRS_LOCI["rs1160312"]["weight_prs"] == pytest.approx(0.485, abs=1e-9)

    def test_hdac9_prs_weight(self):
        assert BALDING_PRS_LOCI["rs756853"]["weight_prs"] == pytest.approx(0.362, abs=1e-9)


class TestFiberAreaFormula:
    """Verifies fiber cross-sectional area formula: Area = 3850.0 + 1420.0 * X_EDAR."""

    def test_baseline_area_zero_dosage(self):
        area = HairMathematicalFormulation.compute_fiber_area_um2(0.0)
        assert area == pytest.approx(FIBER_AREA_BASELINE_UM2, abs=1e-6)  # 3850.0

    def test_heterozygous_edar_area(self):
        area = HairMathematicalFormulation.compute_fiber_area_um2(1.0)
        assert area == pytest.approx(5270.0, abs=1e-6)

    def test_homozygous_edar_area(self):
        area = HairMathematicalFormulation.compute_fiber_area_um2(2.0)
        assert area == pytest.approx(6690.0, abs=1e-6)  # VECTOR_P3_03 target

    def test_area_additive_linearity(self):
        """Area increments must be exactly +1420 μm² per EDAR allele."""
        area_0 = HairMathematicalFormulation.compute_fiber_area_um2(0.0)
        area_1 = HairMathematicalFormulation.compute_fiber_area_um2(1.0)
        area_2 = HairMathematicalFormulation.compute_fiber_area_um2(2.0)
        assert (area_1 - area_0) == pytest.approx(1420.0, abs=1e-6)
        assert (area_2 - area_1) == pytest.approx(1420.0, abs=1e-6)


class TestCurlDensityIndexFormula:
    """Verifies curl density index: C_curl = 1.20 + 1.85*TCHH + 1.42*WNT10A - 2.10*EDAR."""

    def test_baseline_curl_zero_dosage(self):
        c, raw = HairMathematicalFormulation.compute_curl_density_index(0.0, 0.0, 0.0)
        assert c == pytest.approx(CURL_INDEX_BASELINE, abs=1e-3)  # 1.20

    def test_tchh_heterozygous_curl(self):
        c, _ = HairMathematicalFormulation.compute_curl_density_index(0.0, 1.0, 0.0)
        assert c == pytest.approx(1.20 + 1.85, abs=1e-3)  # 3.05

    def test_tchh_homozygous_curl(self):
        c, _ = HairMathematicalFormulation.compute_curl_density_index(0.0, 2.0, 0.0)
        assert c == pytest.approx(1.20 + 3.70, abs=1e-3)  # 4.90

    def test_wnt10a_heterozygous_curl(self):
        c, _ = HairMathematicalFormulation.compute_curl_density_index(0.0, 0.0, 1.0)
        assert c == pytest.approx(1.20 + 1.42, abs=1e-3)  # 2.62

    def test_tchh_and_wnt10a_combined_kinky(self):
        """TCHH=2 + WNT10A=2 → C_curl = 1.20 + 3.70 + 2.84 = 7.74."""
        c, raw = HairMathematicalFormulation.compute_curl_density_index(0.0, 2.0, 2.0)
        assert c == pytest.approx(7.74, abs=1e-3)
        assert raw == pytest.approx(7.74, abs=1e-3)

    def test_edar_clamps_to_zero(self):
        """EDAR=2 → raw = 1.20 - 4.20 = -3.0 → clamped to 0.0."""
        c, raw = HairMathematicalFormulation.compute_curl_density_index(2.0, 0.0, 0.0)
        assert c == pytest.approx(0.0, abs=1e-6)
        assert raw == pytest.approx(-3.0, abs=1e-3)

    def test_curl_clamp_bounds(self):
        assert CURL_CLAMP_MIN == 0.0
        assert CURL_CLAMP_MAX == 10.0


class TestTextureCategoryClassification:
    """Verifies 4-tier texture category thresholds."""

    def test_straight_below_2(self):
        assert HairMathematicalFormulation.classify_texture_category(0.0) == "STRAIGHT"
        assert HairMathematicalFormulation.classify_texture_category(1.20) == "STRAIGHT"
        assert HairMathematicalFormulation.classify_texture_category(1.99) == "STRAIGHT"

    def test_wavy_between_2_and_4_5(self):
        assert HairMathematicalFormulation.classify_texture_category(2.0) == "WAVY"
        assert HairMathematicalFormulation.classify_texture_category(3.05) == "WAVY"
        assert HairMathematicalFormulation.classify_texture_category(4.49) == "WAVY"

    def test_curly_between_4_5_and_7(self):
        assert HairMathematicalFormulation.classify_texture_category(4.5) == "CURLY"
        assert HairMathematicalFormulation.classify_texture_category(4.90) == "CURLY"
        assert HairMathematicalFormulation.classify_texture_category(6.99) == "CURLY"

    def test_kinky_woolly_at_7_and_above(self):
        assert HairMathematicalFormulation.classify_texture_category(7.0) == "KINKY_WOOLLY"
        assert HairMathematicalFormulation.classify_texture_category(7.74) == "KINKY_WOOLLY"
        assert HairMathematicalFormulation.classify_texture_category(10.0) == "KINKY_WOOLLY"


class TestBaldingPRSFormula:
    """Verifies PRS = 0.982*X_AR + 0.541*X_20p11a + 0.485*X_20p11b + 0.362*X_HDAC9."""

    def test_zero_prs_all_reference(self):
        prs = HairMathematicalFormulation.compute_balding_prs({})
        assert prs == pytest.approx(0.0, abs=1e-9)

    def test_ar_single_dose_prs(self):
        prs = HairMathematicalFormulation.compute_balding_prs({"rs6152": 1})
        assert prs == pytest.approx(0.982, abs=1e-6)

    def test_ar_double_dose_prs(self):
        prs = HairMathematicalFormulation.compute_balding_prs({"rs6152": 2})
        assert prs == pytest.approx(1.964, abs=1e-6)

    def test_20p11_single_dose(self):
        prs = HairMathematicalFormulation.compute_balding_prs({"rs2180439": 1})
        assert prs == pytest.approx(0.541, abs=1e-6)

    def test_hdac9_single_dose(self):
        prs = HairMathematicalFormulation.compute_balding_prs({"rs756853": 1})
        assert prs == pytest.approx(0.362, abs=1e-6)

    def test_max_prs_all_homozygous(self):
        """Max PRS = 2 * (0.982 + 0.541 + 0.485 + 0.362) = 4.740."""
        prs = HairMathematicalFormulation.compute_balding_prs(
            {"rs6152": 2, "rs2180439": 2, "rs1160312": 2, "rs756853": 2}
        )
        assert prs == pytest.approx(4.740, abs=1e-6)

    def test_prs_non_negative(self):
        """PRS must always be ≥ 0.0 for non-negative dosages."""
        prs = HairMathematicalFormulation.compute_balding_prs({rsid: 0 for rsid in BALDING_PRS_LOCI})
        assert prs >= 0.0


class TestHamiltonNorwoodClassification:
    """Verifies Hamilton-Norwood grade threshold assignments."""

    def test_grade_i_ii_at_zero(self):
        grade, _, risk = HairMathematicalFormulation.classify_hamilton_norwood(0.0)
        assert grade == "GRADE_I_II"
        assert risk == "LOW_RISK"

    def test_grade_i_ii_at_0_49(self):
        grade, _, risk = HairMathematicalFormulation.classify_hamilton_norwood(0.49)
        assert grade == "GRADE_I_II"
        assert risk == "LOW_RISK"

    def test_grade_iii_at_threshold(self):
        grade, _, risk = HairMathematicalFormulation.classify_hamilton_norwood(0.50)
        assert grade == "GRADE_III"
        assert risk == "MODERATE_RISK"

    def test_grade_iii_at_1_19(self):
        grade, _, risk = HairMathematicalFormulation.classify_hamilton_norwood(1.19)
        assert grade == "GRADE_III"

    def test_grade_iv_v_at_threshold(self):
        grade, _, risk = HairMathematicalFormulation.classify_hamilton_norwood(1.20)
        assert grade == "GRADE_IV_V"
        assert risk == "ELEVATED_RISK"

    def test_grade_vi_vii_at_threshold(self):
        grade, _, risk = HairMathematicalFormulation.classify_hamilton_norwood(2.10)
        assert grade == "GRADE_VI_VII"
        assert risk == "HIGH_RISK"

    def test_grade_vi_vii_at_max(self):
        grade, _, risk = HairMathematicalFormulation.classify_hamilton_norwood(4.740)
        assert grade == "GRADE_VI_VII"
        assert risk == "HIGH_RISK"


class TestFullPipelineFormulation:
    """Verifies the combined end-to-end pipeline methods."""

    def test_run_hair_texture_formulation_baseline(self):
        res = HairMathematicalFormulation.run_hair_texture_formulation({})
        assert res.fiber_cross_sectional_area_um2 == pytest.approx(3850.0, abs=0.1)
        assert res.curl_density_index == pytest.approx(1.20, abs=0.01)
        assert res.texture_category == "STRAIGHT"
        assert res.edar_dosage == 0.0
        assert res.assayed_texture_loci == 0

    def test_run_hair_texture_formulation_eas(self):
        """VECTOR_P3_03: East Asian EDAR=2."""
        res = HairMathematicalFormulation.run_hair_texture_formulation({"rs3827072": 2})
        assert res.fiber_cross_sectional_area_um2 == pytest.approx(6690.0, abs=0.1)
        assert res.curl_density_index == pytest.approx(0.0, abs=1e-6)
        assert res.texture_category == "STRAIGHT"
        assert "Thick Straight" in res.fiber_diameter_category

    def test_run_balding_prs_formulation_max(self):
        res = HairMathematicalFormulation.run_balding_prs_formulation(
            {"rs6152": 2, "rs2180439": 2, "rs1160312": 2, "rs756853": 2}
        )
        assert res.prs_score == pytest.approx(4.740, abs=1e-3)
        assert res.max_possible_prs == pytest.approx(4.740, abs=1e-3)
        assert res.hamilton_norwood_grade == "GRADE_VI_VII"
        assert res.risk_level == "HIGH_RISK"
        assert res.assayed_balding_loci == 4
