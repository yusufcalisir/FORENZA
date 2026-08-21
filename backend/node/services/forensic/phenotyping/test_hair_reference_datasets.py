"""
Reference Dataset Tests for FORENZA Hair Morphology & Balding PRS (Module 3.4).

Tests all 5 certified reference standards against expected phenotypic outputs.
"""

import pytest

from backend.node.services.forensic.phenotyping.hair_mathematical_formulation import (
    HairMathematicalFormulation,
)
from backend.node.services.forensic.phenotyping.hair_reference_datasets import (
    HAIR_STANDARDS,
)


class TestHairReferenceStandardsRegistry:
    """Verifies registry completeness and metadata."""

    def test_five_standards_registered(self):
        assert len(HAIR_STANDARDS) == 5

    def test_all_required_keys_present(self):
        required = {
            "NA18507_EAS_HAIR",
            "NA19240_YRI_KINKY",
            "NA12878_EUR_WAVY",
            "HG002_AJ_HIGH_AGA",
            "BASELINE_REF",
        }
        assert set(HAIR_STANDARDS.keys()) == required

    def test_standard_ids_unique(self):
        ids = [s.standard_id for s in HAIR_STANDARDS.values()]
        assert len(ids) == len(set(ids))


class TestStd01EASThickStraight:
    """STD-HAIR-01: East Asian EDAR Val370Ala homozygous — VECTOR_P3_03."""

    def test_fiber_area_6690(self):
        std = HAIR_STANDARDS["NA18507_EAS_HAIR"]
        res = HairMathematicalFormulation.run_hair_texture_formulation(std.snp_dosages)
        assert res.fiber_cross_sectional_area_um2 == pytest.approx(6690.0, abs=0.1)

    def test_curl_clamped_to_zero(self):
        std = HAIR_STANDARDS["NA18507_EAS_HAIR"]
        res = HairMathematicalFormulation.run_hair_texture_formulation(std.snp_dosages)
        assert res.curl_density_index == pytest.approx(0.0, abs=1e-6)

    def test_texture_is_straight(self):
        std = HAIR_STANDARDS["NA18507_EAS_HAIR"]
        res = HairMathematicalFormulation.run_hair_texture_formulation(std.snp_dosages)
        assert res.texture_category == "STRAIGHT"

    def test_balding_grade_i_ii(self):
        std = HAIR_STANDARDS["NA18507_EAS_HAIR"]
        res = HairMathematicalFormulation.run_balding_prs_formulation(std.snp_dosages)
        assert res.hamilton_norwood_grade == "GRADE_I_II"
        assert res.risk_level == "LOW_RISK"


class TestStd02AFRKinkyWoolly:
    """STD-HAIR-02: African YRI kinky/woolly hair — TCHH + WNT10A max curl."""

    def test_curl_index_7_74(self):
        std = HAIR_STANDARDS["NA19240_YRI_KINKY"]
        res = HairMathematicalFormulation.run_hair_texture_formulation(std.snp_dosages)
        assert res.curl_density_index == pytest.approx(7.74, abs=0.01)

    def test_texture_is_kinky_woolly(self):
        std = HAIR_STANDARDS["NA19240_YRI_KINKY"]
        res = HairMathematicalFormulation.run_hair_texture_formulation(std.snp_dosages)
        assert res.texture_category == "KINKY_WOOLLY"

    def test_fiber_area_baseline(self):
        std = HAIR_STANDARDS["NA19240_YRI_KINKY"]
        res = HairMathematicalFormulation.run_hair_texture_formulation(std.snp_dosages)
        # No EDAR → area = 3850.0
        assert res.fiber_cross_sectional_area_um2 == pytest.approx(3850.0, abs=0.1)


class TestStd03EURWavy:
    """STD-HAIR-03: European wavy hair — TCHH heterozygous."""

    def test_curl_index_3_05(self):
        std = HAIR_STANDARDS["NA12878_EUR_WAVY"]
        res = HairMathematicalFormulation.run_hair_texture_formulation(std.snp_dosages)
        assert res.curl_density_index == pytest.approx(3.05, abs=0.01)

    def test_texture_is_wavy(self):
        std = HAIR_STANDARDS["NA12878_EUR_WAVY"]
        res = HairMathematicalFormulation.run_hair_texture_formulation(std.snp_dosages)
        assert res.texture_category == "WAVY"


class TestStd04HighAGA:
    """STD-HAIR-04: High AGA risk — AR + 20p11 homozygous."""

    def test_prs_3_046(self):
        std = HAIR_STANDARDS["HG002_AJ_HIGH_AGA"]
        res = HairMathematicalFormulation.run_balding_prs_formulation(std.snp_dosages)
        # PRS = 0.982*2 + 0.541*2 = 1.964 + 1.082 = 3.046
        assert res.prs_score == pytest.approx(3.046, abs=0.001)

    def test_grade_vi_vii(self):
        std = HAIR_STANDARDS["HG002_AJ_HIGH_AGA"]
        res = HairMathematicalFormulation.run_balding_prs_formulation(std.snp_dosages)
        assert res.hamilton_norwood_grade == "GRADE_VI_VII"
        assert res.risk_level == "HIGH_RISK"


class TestStd05Baseline:
    """STD-HAIR-05: All-zero baseline reference."""

    def test_area_exactly_3850(self):
        std = HAIR_STANDARDS["BASELINE_REF"]
        res = HairMathematicalFormulation.run_hair_texture_formulation(std.snp_dosages)
        assert res.fiber_cross_sectional_area_um2 == pytest.approx(3850.0, abs=1e-6)

    def test_curl_exactly_1_20(self):
        std = HAIR_STANDARDS["BASELINE_REF"]
        res = HairMathematicalFormulation.run_hair_texture_formulation(std.snp_dosages)
        assert res.curl_density_index == pytest.approx(1.20, abs=1e-6)

    def test_prs_exactly_zero(self):
        std = HAIR_STANDARDS["BASELINE_REF"]
        res = HairMathematicalFormulation.run_balding_prs_formulation(std.snp_dosages)
        assert res.prs_score == pytest.approx(0.0, abs=1e-9)
        assert res.hamilton_norwood_grade == "GRADE_I_II"
