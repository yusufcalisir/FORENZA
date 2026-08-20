"""
Unit Test Suite for Y-STR 27-Locus (Yfiler Plus) Mathematical Formulation Engine.
Sub-Item 2.1.1: Mathematical Formulation

Tests:
  - 27-Locus registry, 7 Rapidly Mutating loci, 2 multi-copy loci
  - Clopper-Pearson exact 95% binomial upper bound (k=0 and k>0)
  - Brenner subpopulation coancestry correction (theta)
  - Multi-copy canonical sorting & PHR evaluation
  - Nested repeat decoupling (DYS389I/II)
  - Discrete Laplace marginal probabilities
  - Stepwise Mutation Model (SMM) kinship transition probabilities
  - Full 27-locus paternal lineage Likelihood Ratio & exclusion criteria
  - Bayesian Y-DNA haplogroup prediction & posterior sum-to-one normalization
"""

import math
import pytest
import numpy as np

from node.services.forensic.ystr.ystr_mathematical_formulation import (
    YStrMutationClass,
    YStrDye,
    YSTR_27_MASTER_REGISTRY,
    YStrMathematicalFormulation,
    ClopperPearsonResult,
    PaternalKinshipResult,
    HaplogroupPredictionResult,
)


class TestYStr27LocusRegistryMetadata:
    """Verifies all 27 loci in the Yfiler Plus multiplex panel."""

    def test_all_27_loci_present(self):
        assert len(YSTR_27_MASTER_REGISTRY) == 25  # 25 systems, 2 are multi-copy (27 markers)
        expected_loci = [
            "DYS19", "DYS389I", "DYS389II", "DYS390", "DYS391", "DYS392",
            "DYS393", "DYS385a/b", "DYS437", "DYS438", "DYS439", "DYS448",
            "DYS456", "DYS458", "DYS635", "YGATAH4", "DYS460", "DYS481",
            "DYS533", "DYS570", "DYS576", "DYS627", "DYS518", "DYS449",
            "DYF387S1a/b"
        ]
        for locus in expected_loci:
            assert locus in YSTR_27_MASTER_REGISTRY, f"Missing locus: {locus}"

    def test_seven_rapidly_mutating_markers(self):
        rm_loci = [l for l, m in YSTR_27_MASTER_REGISTRY.items() if m.is_rapidly_mutating]
        expected_rm = ["DYS570", "DYS576", "DYS627", "DYS518", "DYS449", "DYF387S1a/b"]
        for locus in expected_rm:
            assert locus in rm_loci
            assert YSTR_27_MASTER_REGISTRY[locus].mutation_rate >= 0.010

    def test_two_multi_copy_systems(self):
        multi_loci = [l for l, m in YSTR_27_MASTER_REGISTRY.items() if m.is_multi_copy]
        assert "DYS385a/b" in multi_loci
        assert "DYF387S1a/b" in multi_loci
        assert len(multi_loci) == 2


class TestClopperPearsonExactBounds:
    """Verifies Clopper-Pearson exact binomial confidence bounds against research tables."""

    def test_unobserved_haplotype_zero_count_n35000(self):
        """Research Table §2.1: N=35,000, k=0 -> p_upper = 8.56e-5 (1 in 11,682)."""
        res = YStrMathematicalFormulation.compute_clopper_pearson_upper_bound(k=0, n=35000, alpha=0.05)
        expected = 1.0 - math.pow(0.05, 1.0 / 35001)
        assert abs(res.p_upper_bound - expected) < 1e-10
        assert abs(res.p_upper_bound - 8.5589e-5) < 1e-7
        assert abs(res.equivalent_match_ratio - 11683.7) < 2.0

    def test_observed_haplotype_single_match_n35000(self):
        """Research Table §2.1: N=35,000, k=1 -> p_upper ≈ 1.59e-4 (1 in 6,281)."""
        res = YStrMathematicalFormulation.compute_clopper_pearson_upper_bound(k=1, n=35000, alpha=0.05)
        assert abs(res.p_upper_bound - 1.5919e-4) < 1e-6
        assert abs(res.equivalent_match_ratio - 6281.8) < 5.0

    def test_observed_haplotype_five_matches_n35000(self):
        """Research Table §2.1: N=35,000, k=5 -> p_upper ≈ 3.33e-4 (1 in 2,999)."""
        res = YStrMathematicalFormulation.compute_clopper_pearson_upper_bound(k=5, n=35000, alpha=0.05)
        assert abs(res.p_upper_bound - 3.334e-4) < 1e-6
        assert abs(res.equivalent_match_ratio - 2999.0) < 5.0

    def test_monotonicity_with_increasing_matches(self):
        """p_upper must strictly increase with k for fixed N."""
        n = 10000
        p_vals = [
            YStrMathematicalFormulation.compute_clopper_pearson_upper_bound(k=k, n=n).p_upper_bound
            for k in range(10)
        ]
        for i in range(len(p_vals) - 1):
            assert p_vals[i] < p_vals[i + 1]

    def test_invalid_parameters_raise_error(self):
        with pytest.raises(ValueError):
            YStrMathematicalFormulation.compute_clopper_pearson_upper_bound(k=-1, n=1000)
        with pytest.raises(ValueError):
            YStrMathematicalFormulation.compute_clopper_pearson_upper_bound(k=10, n=5)


class TestBrennerSubpopulationCorrection:
    """Verifies Brenner / Surveyor coancestry correction formula."""

    def test_brenner_formula_calculation(self):
        # p_Brenner = (k + theta) / (n + theta)
        k, n, theta = 0, 10000, 0.03
        res = YStrMathematicalFormulation.compute_brenner_frequency(k=k, n=n, theta=theta)
        expected = 0.03 / 10000.03
        assert abs(res - expected) < 1e-12

    def test_brenner_theta_impact(self):
        # Higher theta increases the conservative baseline frequency for k=0
        p_theta01 = YStrMathematicalFormulation.compute_brenner_frequency(0, 10000, 0.01)
        p_theta03 = YStrMathematicalFormulation.compute_brenner_frequency(0, 10000, 0.03)
        assert p_theta03 > p_theta01


class TestMultiCopyAndNestedRepeatPhysics:
    """Verifies multi-copy sorting, PHR, and nested repeat decoupling."""

    def test_multi_copy_sorting_invariant(self):
        res1 = YStrMathematicalFormulation.normalize_multi_copy_alleles([14, 11])
        res2 = YStrMathematicalFormulation.normalize_multi_copy_alleles(["11", "14"])
        assert res1 == (11.0, 14.0)
        assert res2 == (11.0, 14.0)

    def test_multi_copy_phr_balanced_passes(self):
        phr, is_pass = YStrMathematicalFormulation.evaluate_multi_copy_phr([1200.0, 1000.0])
        assert abs(phr - (1000.0 / 1200.0)) < 1e-6
        assert is_pass is True

    def test_multi_copy_phr_imbalanced_fails(self):
        phr, is_pass = YStrMathematicalFormulation.evaluate_multi_copy_phr([1500.0, 450.0])
        assert abs(phr - 0.30) < 1e-6
        assert is_pass is False

    def test_nested_repeat_dys389_decoupling(self):
        # DYS389.2_pure = DYS389II_total - DYS389I
        dys389i = 13.0
        dys389ii_total = 29.0
        pure = YStrMathematicalFormulation.decouple_dys389(dys389i, dys389ii_total)
        assert pure == 16.0

    def test_minimum_male_contributors_inference(self):
        # Single donor profile (1 allele per single copy, 2 per multi-copy)
        single_source = {"DYS19": 1, "DYS389I": 1, "DYS385a/b": 2, "DYF387S1a/b": 2}
        assert YStrMathematicalFormulation.estimate_minimum_male_contributors(single_source) == 1

        # Two-person male mixture (3 alleles at DYS385, 2 at DYS19)
        two_males = {"DYS19": 2, "DYS389I": 2, "DYS385a/b": 3, "DYF387S1a/b": 4}
        assert YStrMathematicalFormulation.estimate_minimum_male_contributors(two_males) == 2


class TestDiscreteLaplaceModel:
    """Verifies Discrete Laplace marginal probability calculation."""

    def test_discrete_laplace_zero_distance(self):
        prob = YStrMathematicalFormulation.compute_discrete_laplace_prob(14.0, 14.0, dispersion_lambda=0.65)
        expected = (1.0 - 0.65) / (1.0 + 0.65)
        assert abs(prob - expected) < 1e-10

    def test_discrete_laplace_distance_decay(self):
        p0 = YStrMathematicalFormulation.compute_discrete_laplace_prob(14.0, 14.0, 0.65)
        p1 = YStrMathematicalFormulation.compute_discrete_laplace_prob(15.0, 14.0, 0.65)
        p2 = YStrMathematicalFormulation.compute_discrete_laplace_prob(16.0, 14.0, 0.65)
        assert p0 > p1 > p2
        assert abs(p1 / p0 - 0.65) < 1e-10
        assert abs(p2 / p1 - 0.65) < 1e-10


class TestStepwiseMutationModelAndKinship:
    """Verifies SMM transmission probabilities and full 27-locus paternal kinship LR."""

    def test_smm_identity_transmission(self):
        mu = 0.002
        p_same = YStrMathematicalFormulation.compute_smm_transition_probability(14.0, 14.0, mu, 0.90, meioses_m=1)
        assert abs(p_same - (1.0 - mu)) < 1e-10

    def test_smm_one_step_mutation(self):
        mu = 0.002
        r = 0.90
        p_1step = YStrMathematicalFormulation.compute_smm_transition_probability(14.0, 15.0, mu, r, meioses_m=1)
        expected = 0.5 * mu * (1.0 - r)
        assert abs(p_1step - expected) < 1e-10

    def test_smm_two_step_mutation_geometric_decay(self):
        mu = 0.002
        r = 0.90
        p_1step = YStrMathematicalFormulation.compute_smm_transition_probability(14.0, 15.0, mu, r, meioses_m=1)
        p_2step = YStrMathematicalFormulation.compute_smm_transition_probability(14.0, 16.0, mu, r, meioses_m=1)
        assert abs(p_2step - (p_1step * r)) < 1e-10

    def test_full_27_locus_identical_paternal_match(self):
        """27/27 exact locus match yields massive paternal lineage support (LR > 10^4)."""
        profile = {
            "DYS19": 14, "DYS389I": 13, "DYS389II": 29, "DYS390": 24, "DYS391": 11,
            "DYS392": 13, "DYS393": 13, "DYS385a/b": [11, 14], "DYS437": 15, "DYS438": 12,
            "DYS439": 12, "DYS448": 19, "DYS456": 16, "DYS458": 17, "DYS635": 23,
            "YGATAH4": 12, "DYS460": 11, "DYS481": 22, "DYS533": 12, "DYS570": 17,
            "DYS576": 18, "DYS627": 21, "DYS518": 38, "DYS449": 29, "DYF387S1a/b": [36, 38]
        }
        res = YStrMathematicalFormulation.evaluate_paternal_kinship_likelihood(
            profile_a=profile, profile_b=profile, meioses_m=1, database_size_n=38500
        )
        assert res.matching_loci_count == 25
        assert res.mutated_loci_count == 0
        assert res.is_lineage_excluded is False
        assert res.paternal_lr > 10000.0
        assert "Extremely Strong Support" in res.verbal_predicate_en

    def test_multi_locus_mutation_exclusion(self):
        """3 standard locus mismatches firmly excludes paternal lineage (LR = 0.0)."""
        profile_a = {
            "DYS19": 14, "DYS389I": 13, "DYS389II": 29, "DYS390": 24, "DYS391": 11,
            "DYS392": 13, "DYS393": 13, "DYS385a/b": [11, 14], "DYS437": 15, "DYS438": 12,
            "DYS439": 12, "DYS448": 19, "DYS456": 16, "DYS458": 17, "DYS635": 23,
            "YGATAH4": 12, "DYS460": 11, "DYS481": 22, "DYS533": 12, "DYS570": 17,
            "DYS576": 18, "DYS627": 21, "DYS518": 38, "DYS449": 29, "DYF387S1a/b": [36, 38]
        }
        profile_b = dict(profile_a)
        # Introduce 3 standard mutations
        profile_b["DYS19"] = 16
        profile_b["DYS390"] = 22
        profile_b["DYS393"] = 15

        res = YStrMathematicalFormulation.evaluate_paternal_kinship_likelihood(
            profile_a=profile_a, profile_b=profile_b, meioses_m=1
        )
        assert res.standard_mutations_count == 3
        assert res.is_lineage_excluded is True
        assert res.paternal_lr == 0.0
        assert "Exclusion" in res.verbal_predicate_en


class TestBayesianHaplogroupPrediction:
    """Verifies Bayesian Y-DNA haplogroup prediction across major modal signatures."""

    def test_r1b_canonical_profile_prediction(self):
        profile = {
            "DYS19": 14, "DYS389I": 13, "DYS389II": 29, "DYS390": 24, "DYS391": 11,
            "DYS392": 13, "DYS393": 13, "DYS385a/b": [11, 14], "DYS437": 15, "DYS438": 12,
            "DYS439": 12, "DYS448": 19, "DYS456": 16, "DYS458": 17, "DYS635": 23,
            "YGATAH4": 12, "DYS460": 11, "DYS481": 22, "DYS533": 12, "DYS570": 17,
            "DYS576": 18, "DYS627": 21, "DYS518": 38, "DYS449": 29, "DYF387S1a/b": [36, 38]
        }
        res = YStrMathematicalFormulation.predict_haplogroup(profile)
        assert res.predicted_haplogroup == "R1b"
        assert res.confidence_score > 0.50
        assert "M269" in res.primary_snp_marker

    def test_haplogroup_posteriors_probability_simplex_sum_to_one(self):
        profile = {"DYS19": 14, "DYS389I": 13, "DYS390": 24, "DYS393": 13}
        res = YStrMathematicalFormulation.predict_haplogroup(profile)
        total_p = sum(res.bayesian_posteriors.values())
        assert abs(total_p - 1.0) < 1e-5
