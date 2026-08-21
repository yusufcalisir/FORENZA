"""
Unit Test Suite for FORENZA X-STR 12-Locus Mathematical Formulation (Module 2.2).
Validates Argus X-12 registry, Kosambi map function, male hemizygous validation,
and complex female kinship models.
"""

import math
import pytest

from node.services.forensic.xstr.xstr_mathematical_formulation import (
    XStrMathematicalFormulation,
    ARGUS_X12_MASTER_REGISTRY,
    ARGUS_X12_LINKAGE_GROUPS,
    KinshipRelationshipType,
)


class TestArgusX12MasterRegistry:
    """Verifies Argus X-12 12-locus registry and 4 linkage groups."""

    def test_total_loci_count_is_12(self):
        assert len(ARGUS_X12_MASTER_REGISTRY) == 12

    def test_four_linkage_groups_present(self):
        assert len(ARGUS_X12_LINKAGE_GROUPS) == 4
        assert set(ARGUS_X12_LINKAGE_GROUPS.keys()) == {"LG1", "LG2", "LG3", "LG4"}

    def test_each_linkage_group_has_three_loci(self):
        for g_id, g_meta in ARGUS_X12_LINKAGE_GROUPS.items():
            assert len(g_meta.loci) == 3
            for loc in g_meta.loci:
                assert loc in ARGUS_X12_MASTER_REGISTRY
                assert ARGUS_X12_MASTER_REGISTRY[loc].linkage_group == g_id

    def test_physical_and_genetic_coordinates_monotonic_within_groups(self):
        for g_id, g_meta in ARGUS_X12_LINKAGE_GROUPS.items():
            loci = g_meta.loci
            for i in range(len(loci) - 1):
                loc_a = ARGUS_X12_MASTER_REGISTRY[loci[i]]
                loc_b = ARGUS_X12_MASTER_REGISTRY[loci[i + 1]]
                assert loc_b.physical_position_mb > loc_a.physical_position_mb
                assert loc_b.genetic_map_cm > loc_a.genetic_map_cm


class TestKosambiMappingFunction:
    """Verifies Kosambi mapping function r = 0.5 * tanh(2d/100) and its inverse."""

    def test_kosambi_zero_distance(self):
        assert XStrMathematicalFormulation.kosambi_map(0.0) == 0.0

    def test_kosambi_50_cm(self):
        # r = 0.5 * tanh(2 * 50 / 100) = 0.5 * tanh(1.0) ≈ 0.380797
        r = XStrMathematicalFormulation.kosambi_map(50.0)
        expected = 0.5 * math.tanh(1.0)
        assert abs(r - expected) < 1e-6
        assert abs(r - 0.380797) < 1e-5

    def test_kosambi_asymptotic_limit(self):
        r_large = XStrMathematicalFormulation.kosambi_map(500.0)
        assert abs(r_large - 0.50) < 1e-4

    def test_kosambi_strictly_monotonic(self):
        distances = [0.1, 1.0, 5.0, 10.0, 20.0, 50.0, 100.0]
        results = [XStrMathematicalFormulation.kosambi_map(d) for d in distances]
        for i in range(1, len(results)):
            assert results[i] > results[i - 1]

    def test_inverse_kosambi_recovers_original_distance(self):
        test_distances = [0.5, 2.0, 5.0, 15.0, 30.0, 45.0]
        for d in test_distances:
            r = XStrMathematicalFormulation.kosambi_map(d)
            d_rec = XStrMathematicalFormulation.inverse_kosambi_map(r)
            assert abs(d_rec - d) < 1e-6

    def test_haldane_comparison_positive_interference(self):
        """For a fixed genetic distance d, Kosambi recombination exceeds Haldane."""
        d = 20.0  # 20 cM
        r_kosambi = XStrMathematicalFormulation.kosambi_map(d)
        r_haldane = XStrMathematicalFormulation.haldane_map(d)
        assert r_kosambi > r_haldane
        # Conversely, to achieve recombination fraction r, Kosambi requires less map distance
        d_kos = XStrMathematicalFormulation.inverse_kosambi_map(0.15)
        # d_haldane = -50 * ln(1 - 2*0.15) ≈ 17.83 cM > d_kos (15.42 cM)
        assert d_kos < 17.83


class TestMaleHemizygoteAndFemaleValidation:
    """Verifies sex-specific cytogenetic ploidy constraints."""

    def test_valid_male_hemizygous_profile(self):
        male_prof = {"DXS10148": 26.0, "DXS10135": 19.0, "DXS8378": 11.0}
        val = XStrMathematicalFormulation.validate_profile(male_prof, "MALE", "MALE_01")
        assert len(val) == 3
        assert val["DXS10148"] == [26.0]

    def test_male_diallelic_profile_raises_validation_error(self):
        """Male 46,XY cannot possess > 1 allele at any X-STR locus (EC-XSTR-04)."""
        bad_male_prof = {"DXS10148": [26.0, 28.0], "DXS10135": 19.0}
        with pytest.raises(ValueError, match="Hemizygous male.*cannot possess multiple alleles"):
            XStrMathematicalFormulation.validate_profile(bad_male_prof, "MALE", "BAD_MALE")

    def test_valid_female_heterozygous_profile(self):
        female_prof = {"DXS10148": [26.0, 28.0], "DXS10135": [19.0, 21.0]}
        val = XStrMathematicalFormulation.validate_profile(female_prof, "FEMALE", "FEMALE_01")
        assert len(val) == 2
        assert val["DXS10148"] == [26.0, 28.0]

    def test_female_tri_allelic_raises_validation_error(self):
        bad_female_prof = {"DXS10148": [24.0, 26.0, 28.0]}
        with pytest.raises(ValueError, match="Female.*cannot possess > 2 alleles"):
            XStrMathematicalFormulation.validate_profile(bad_female_prof, "FEMALE", "BAD_FEMALE")


class TestKinshipFormulations:
    """Verifies Kinship Index formulations across standard pedigree relationships."""

    def test_father_daughter_exact_match(self):
        father = {loc: 15.0 for loc in ARGUS_X12_MASTER_REGISTRY}
        daughter = {loc: [15.0, 18.0] for loc in ARGUS_X12_MASTER_REGISTRY}
        res = XStrMathematicalFormulation.evaluate_xstr_kinship(
            profile_a=father,
            profile_b=daughter,
            sex_a="MALE",
            sex_b="FEMALE",
            relationship=KinshipRelationshipType.FATHER_DAUGHTER,
        )
        assert res.matching_loci_count == 12
        assert res.mismatch_loci_count == 0
        assert res.combined_ki > 1e6
        assert "Extremely Strong Support" in res.verbal_predicate_en

    def test_paternal_half_sisters_sharing(self):
        sister_1 = {loc: [15.0, 18.0] for loc in ARGUS_X12_MASTER_REGISTRY}
        sister_2 = {loc: [15.0, 22.0] for loc in ARGUS_X12_MASTER_REGISTRY}
        res = XStrMathematicalFormulation.evaluate_xstr_kinship(
            profile_a=sister_1,
            profile_b=sister_2,
            sex_a="FEMALE",
            sex_b="FEMALE",
            relationship=KinshipRelationshipType.PATERNAL_HALF_SISTERS,
        )
        assert res.matching_loci_count == 12
        assert res.combined_ki > 1e4
        assert res.is_kinship_supported is True

    def test_mother_son_transmission(self):
        mother = {"DXS10148": [26.0, 28.0]}
        son = {"DXS10148": 26.0}
        res = XStrMathematicalFormulation.evaluate_xstr_kinship(
            profile_a=mother,
            profile_b=son,
            sex_a="FEMALE",
            sex_b="MALE",
            relationship=KinshipRelationshipType.MOTHER_SON,
        )
        assert res.matching_loci_count == 1
        assert res.combined_ki > 0.0


class TestMultiClusterIndependenceAndLogAdditivity:
    """Verifies cluster independence and log10 LR additivity invariant."""

    def test_log10_ki_additivity_invariant(self):
        prof_a = {loc: [14.0, 16.0] for loc in ARGUS_X12_MASTER_REGISTRY}
        prof_b = {loc: [14.0, 18.0] for loc in ARGUS_X12_MASTER_REGISTRY}
        res = XStrMathematicalFormulation.evaluate_xstr_kinship(
            profile_a=prof_a,
            profile_b=prof_b,
            sex_a="FEMALE",
            sex_b="FEMALE",
            relationship=KinshipRelationshipType.PATERNAL_HALF_SISTERS,
        )
        sum_of_group_logs = sum(g.log10_ki_group for g in res.linkage_group_results.values())
        assert abs(res.log10_combined_ki - sum_of_group_logs) < 1e-6
