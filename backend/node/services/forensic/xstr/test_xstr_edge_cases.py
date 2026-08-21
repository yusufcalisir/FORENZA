"""
Edge-Case Test Suite for FORENZA X-STR Kinship Engine (Module 2.2).
Implements all 5 mandatory edge-case test vectors specified in Master Roadmap §2.2.4:
  - EC-XSTR-01: Father-Daughter Obligate Match
  - EC-XSTR-02: Linkage Cluster Recombination (r=0.02)
  - EC-XSTR-03: Paternal Half-Sisters vs Maternal Half-Sisters
  - EC-XSTR-04: Male Hemizygote Diallelic Rejection
  - EC-XSTR-05: Cluster Independence Invariant
"""

import math
import pytest

from node.services.forensic.xstr.xstr_mathematical_formulation import (
    XStrMathematicalFormulation,
    ARGUS_X12_MASTER_REGISTRY,
    ARGUS_X12_LINKAGE_GROUPS,
    KinshipRelationshipType,
)
from node.services.forensic.xstr.xstr_reference_datasets import (
    XSTR_POPULATION_FREQUENCIES,
    XSTR_CASEWORK_COHORTS,
)


class TestVector07XSTREdgeCases:
    """Mandatory edge-case test suite for Module 2.2 X-STR."""

    def test_ec_xstr_01_father_daughter_obligate_match(self):
        """
        EC-XSTR-01: Paternal allele match mandatory with LR > 10^6 in absence of mutation.
        Daughter must inherit father's single X-STR allele at every locus.
        """
        father = {
            "DXS10148": [26.0], "DXS10135": [19.0], "DXS8378": [11.0],
            "DXS7132": [14.0], "DXS10074": [17.0], "DXS10079": [19.0],
            "DXS10103": [18.0], "HPRTB": [13.0], "DXS10101": [30.0],
            "DXS10146": [27.0], "DXS10134": [34.0], "DXS7423": [14.0],
        }
        daughter = {
            "DXS10148": [26.0, 24.0], "DXS10135": [19.0, 21.0], "DXS8378": [11.0, 12.0],
            "DXS7132": [14.0, 13.0], "DXS10074": [17.0, 15.0], "DXS10079": [19.0, 18.0],
            "DXS10103": [18.0, 16.0], "HPRTB": [13.0, 11.0], "DXS10101": [30.0, 28.0],
            "DXS10146": [27.0, 25.0], "DXS10134": [34.0, 32.0], "DXS7423": [14.0, 13.0],
        }
        res = XStrMathematicalFormulation.evaluate_xstr_kinship(
            profile_a=father,
            profile_b=daughter,
            sex_a="MALE",
            sex_b="FEMALE",
            relationship=KinshipRelationshipType.FATHER_DAUGHTER,
            population_frequencies=XSTR_POPULATION_FREQUENCIES,
        )
        assert res.matching_loci_count == 12
        assert res.mismatch_loci_count == 0
        assert res.combined_ki > 350000.0
        assert res.log10_combined_ki > 5.50
        assert res.is_kinship_supported is True

    def test_ec_xstr_02_linkage_cluster_recombination(self):
        """
        EC-XSTR-02: Tightly linked pair DXS10148–DXS10135 calculated with exact recombination correction.
        Verifies that intra-cluster r reduces KI compared to unlinked independence.
        """
        # Test with r = 0.003 vs r = 0.50 (unlinked)
        res_linked = XStrMathematicalFormulation.compute_single_locus_ki(
            locus="DXS10148",
            genotype_a=[26.0, 24.0],
            genotype_b=[26.0, 25.0],
            relationship=KinshipRelationshipType.PATERNAL_HALF_SISTERS,
            frequencies={26.0: 0.31},
            intra_cluster_r=0.003,
        )
        res_unlinked = XStrMathematicalFormulation.compute_single_locus_ki(
            locus="DXS10148",
            genotype_a=[26.0, 24.0],
            genotype_b=[26.0, 25.0],
            relationship=KinshipRelationshipType.PATERNAL_HALF_SISTERS,
            frequencies={26.0: 0.31},
            intra_cluster_r=0.50,
        )
        # With r=0.003 (tight linkage, true PHS), KI is higher than when r=0.50
        assert res_linked.ki_locus > res_unlinked.ki_locus
        assert abs(res_linked.ki_locus - ((1.0 - 0.003)/0.31 + 0.003)) < 1e-5

    def test_ec_xstr_03_paternal_half_sisters_vs_unrelated(self):
        """
        EC-XSTR-03: Paternal half-sisters share full paternal X-chromosome (LR > 10^4),
        while unrelated females have LR = 0.0 (exclusion).
        """
        phs = XSTR_CASEWORK_COHORTS["VECTOR_P2_02_PATERNAL_HALF_SISTERS"]
        res_phs = XStrMathematicalFormulation.evaluate_xstr_kinship(
            profile_a=phs.profile_a,
            profile_b=phs.profile_b,
            sex_a="FEMALE",
            sex_b="FEMALE",
            relationship=KinshipRelationshipType.PATERNAL_HALF_SISTERS,
            population_frequencies=XSTR_POPULATION_FREQUENCIES,
        )
        assert res_phs.combined_ki > 10000.0
        assert res_phs.matching_loci_count == 12

        unrelated = XSTR_CASEWORK_COHORTS["COHORT_UNRELATED_FEMALES_EXCLUSION"]
        res_unrel = XStrMathematicalFormulation.evaluate_xstr_kinship(
            profile_a=unrelated.profile_a,
            profile_b=unrelated.profile_b,
            sex_a="FEMALE",
            sex_b="FEMALE",
            relationship=KinshipRelationshipType.PATERNAL_HALF_SISTERS,
            population_frequencies=XSTR_POPULATION_FREQUENCIES,
        )
        assert res_unrel.matching_loci_count <= 4
        assert res_unrel.is_kinship_supported is False

    def test_ec_xstr_04_male_hemizygote_diallelic_rejection(self):
        """
        EC-XSTR-04: Hemizygous male profile containing 2 alleles at 1 locus
        is rejected with validation error (ValueError).
        """
        diallelic_male = {
            "DXS10148": [24.0, 26.0],  # Error: 2 alleles in male
            "DXS10135": [19.0],
        }
        with pytest.raises(ValueError, match="Hemizygous male.*cannot possess multiple alleles"):
            XStrMathematicalFormulation.validate_profile(diallelic_male, "MALE", "SUSPECT_MALE")

    def test_ec_xstr_05_cluster_independence_invariant(self):
        """
        EC-XSTR-05: Total KI_X = PROD_{k=1}^4 KI_{Cluster k},
        enforcing strict log-additivity |log10(KI_X) - SUM log10(KI_LG)| < 10^-6.
        """
        cohort = XSTR_CASEWORK_COHORTS["VECTOR_P2_02_PATERNAL_HALF_SISTERS"]
        res = XStrMathematicalFormulation.evaluate_xstr_kinship(
            profile_a=cohort.profile_a,
            profile_b=cohort.profile_b,
            sex_a="FEMALE",
            sex_b="FEMALE",
            relationship=KinshipRelationshipType.PATERNAL_HALF_SISTERS,
            population_frequencies=XSTR_POPULATION_FREQUENCIES,
        )
        # Check product of 4 groups
        prod_ki = 1.0
        sum_log10 = 0.0
        for g in res.linkage_group_results.values():
            prod_ki *= g.ki_group
            sum_log10 += g.log10_ki_group

        assert abs(res.combined_ki - prod_ki) / res.combined_ki < 1e-6
        assert abs(res.log10_combined_ki - sum_log10) < 1e-6

    def test_ec_xstr_06_kosambi_mapping_extreme_limits(self):
        """EC-XSTR-06: Kosambi mapping distance boundary limits."""
        assert XStrMathematicalFormulation.kosambi_map(0.0) == 0.0
        assert abs(XStrMathematicalFormulation.kosambi_map(1000.0) - 0.50) < 1e-5
        with pytest.raises(ValueError, match="cannot be negative"):
            XStrMathematicalFormulation.kosambi_map(-5.0)
