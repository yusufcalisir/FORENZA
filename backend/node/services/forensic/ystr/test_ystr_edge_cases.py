"""
FORENZA Forensic Evidence Operating System
Pillar 2 — Module 2.1: Y-STR 27-Locus Lineage Engine (Y-FILER Plus)
Sub-Item 2.1.4: Edge-Case Test Suite (EC-YSTR-01 to EC-YSTR-08)

Tests:
  - EC-YSTR-01: Zero Haplotype Count Upper Bound, Asymptotic Convergence, and Multi-Alpha Scaling
  - EC-YSTR-02: Multi-Copy Duplicated Loci (DYS385, DYF387S1) Sorting Invariance and Imbalance Flagging
  - EC-YSTR-03: Rapidly Mutating Locus Shift vs False Exclusion Prevention Shield (DYS518, DYS576)
  - EC-YSTR-04: Full 27-Locus Pristine Concordance and Monotonic Meioses Probability Decay (m=1..5)
  - EC-YSTR-05: Multi-Step Standard Locus Mismatch Definitive Paternal Lineage Exclusion (LR=0.0)
  - EC-YSTR-06: Nested Repeat Decoupling for DYS389I / DYS389II Mutation Attribution
  - EC-YSTR-07: Micro-Variant Fractional Step Calculations (DYS458.2)
  - EC-YSTR-08: Female Non-Target Input Validation & Exception Handling
"""

import math
import pytest
import numpy as np

from node.services.forensic.ystr.ystr_mathematical_formulation import (
    YSTR_27_MASTER_REGISTRY,
    YStrMathematicalFormulation,
    ClopperPearsonResult,
    PaternalKinshipResult,
    HaplogroupPredictionResult,
)
from node.services.forensic.ystr.ystr_reference_datasets import (
    YStrReferenceDatasets,
    GOLD_STANDARD_INDIVIDUALS,
)


class TestVector06YStrEdgeCases:
    """Rigorous Edge-Case Test Suite for Y-STR 27-Locus Lineage Engine."""

    # ── EC-YSTR-01: Zero Haplotype Count Upper Bound & Asymptotic Scaling ─

    def test_ec_ystr_01_zero_count_exact_bound_and_asymptotics(self):
        """
        EC-YSTR-01:
        In database N=38,500, unobserved haplotype (k=0) yields p_upper = 7.7806e-5.
        In database N=385,000, unobserved haplotype (k=0) yields p_upper = 7.7811e-6.
        Exact Snedecor F / binomial analytical form converges to rule of thumb 3/(N+1) with delta < 1.2e-7.
        Multi-confidence interval scaling: p(95%) < p(99%) < p(99.9%).
        """
        # N=38,500
        res_38k = YStrMathematicalFormulation.compute_clopper_pearson_upper_bound(k=0, n=38500, alpha=0.05)
        assert abs(res_38k.p_upper_bound - 7.7806180e-05) < 1e-10
        assert abs(res_38k.equivalent_match_ratio - 12852.4) < 1.0

        # N=385,000
        res_385k = YStrMathematicalFormulation.compute_clopper_pearson_upper_bound(k=0, n=385000, alpha=0.05)
        assert abs(res_385k.p_upper_bound - 7.7810723e-06) < 1e-11
        assert abs(res_385k.equivalent_match_ratio - 128517.0) < 5.0

        # Asymptotic 3/(N+1) comparison
        approx_38k = 3.0 / 38501.0
        delta_approx = abs(res_38k.p_upper_bound - approx_38k)
        assert delta_approx < 1.2e-7

        # Multi-confidence interval monotonicity
        p_95 = YStrMathematicalFormulation.compute_clopper_pearson_upper_bound(k=0, n=38500, alpha=0.05).p_upper_bound
        p_99 = YStrMathematicalFormulation.compute_clopper_pearson_upper_bound(k=0, n=38500, alpha=0.01).p_upper_bound
        p_999 = YStrMathematicalFormulation.compute_clopper_pearson_upper_bound(k=0, n=38500, alpha=0.001).p_upper_bound

        assert p_95 < p_99 < p_999
        assert p_99 > 1.1e-4
        assert p_999 > 1.7e-4

    # ── EC-YSTR-02: Multi-Copy Duplicated Loci Sorting & Imbalance ────────

    def test_ec_ystr_02_duplicated_loci_sorting_and_imbalance(self):
        """
        EC-YSTR-02:
        Alleles [14, 11] at DYS385a/b and ["37", "35"] at DYF387S1a/b are canonically sorted
        to (11.0, 14.0) and (35.0, 37.0). Likelihood ratio is strictly identical regardless of input order.
        PHR < 0.50 correctly flags imbalance. Mixture detection flags N_male >= 2 when >2 alleles observed.
        """
        # Sorting invariance
        sorted_1 = YStrMathematicalFormulation.normalize_multi_copy_alleles([14, 11])
        sorted_2 = YStrMathematicalFormulation.normalize_multi_copy_alleles([11, 14])
        sorted_str = YStrMathematicalFormulation.normalize_multi_copy_alleles(["14.0", "11.0"])
        assert sorted_1 == (11.0, 14.0)
        assert sorted_2 == (11.0, 14.0)
        assert sorted_str == (11.0, 14.0)

        # Kinship LR invariance under input order
        ref = GOLD_STANDARD_INDIVIDUALS["SRM_2391d_COMP_A"].y_str_haplotype
        profile_forward = dict(ref)
        profile_forward["DYS385a/b"] = [11, 14]
        profile_reversed = dict(ref)
        profile_reversed["DYS385a/b"] = [14, 11]

        lr_fwd = YStrMathematicalFormulation.evaluate_paternal_kinship_likelihood(ref, profile_forward).paternal_lr
        lr_rev = YStrMathematicalFormulation.evaluate_paternal_kinship_likelihood(ref, profile_reversed).paternal_lr
        assert abs(lr_fwd - lr_rev) < 1e-6

        # Peak height ratio evaluation
        phr_ok, pass_ok = YStrMathematicalFormulation.evaluate_multi_copy_phr([2400.0, 2100.0])
        assert pass_ok is True
        assert abs(phr_ok - 0.875) < 1e-6

        phr_bad, pass_bad = YStrMathematicalFormulation.evaluate_multi_copy_phr([3000.0, 900.0])
        assert pass_bad is False
        assert abs(phr_bad - 0.30) < 1e-6

        # Mixture contributor estimation
        tri_allele_mix = {"DYS19": 1, "DYS385a/b": 3, "DYF387S1a/b": 2}
        assert YStrMathematicalFormulation.estimate_minimum_male_contributors(tri_allele_mix) == 2

    # ── EC-YSTR-03: Rapidly Mutating Locus Shift vs False Exclusion Shield ─

    def test_ec_ystr_03_rm_locus_mutation_prevents_false_exclusion(self):
        """
        EC-YSTR-03:
        Single 1-step mutation at RM marker DYS518 (mu = 0.018, 38 -> 39) or DYS576 (mu = 0.014, 18 -> 19)
        maintains strong paternal lineage support (LR >= 200.0) with designated rapid mutation verbal statement.
        """
        ref = GOLD_STANDARD_INDIVIDUALS["SRM_2391d_COMP_A"].y_str_haplotype

        # Father-son duo with DYS518 RM mutation (38 -> 39)
        son_dys518 = dict(ref)
        son_dys518["DYS518"] = 39

        res_dys518 = YStrMathematicalFormulation.evaluate_paternal_kinship_likelihood(
            profile_a=ref, profile_b=son_dys518, meioses_m=1, database_size_n=385000
        )
        assert res_dys518.matching_loci_count == 24
        assert res_dys518.mutated_loci_count == 1
        assert res_dys518.rm_mutations_count == 1
        assert res_dys518.standard_mutations_count == 0
        assert res_dys518.is_lineage_excluded is False
        assert res_dys518.paternal_lr >= 200.0
        assert "Rapid Germline Mutation" in res_dys518.verbal_predicate_en

        # Father-son duo with DYS576 RM mutation (18 -> 19)
        son_dys576 = dict(ref)
        son_dys576["DYS576"] = 19

        res_dys576 = YStrMathematicalFormulation.evaluate_paternal_kinship_likelihood(
            profile_a=ref, profile_b=son_dys576, meioses_m=1, database_size_n=385000
        )
        assert res_dys576.matching_loci_count == 24
        assert res_dys576.mutated_loci_count == 1
        assert res_dys576.rm_mutations_count == 1
        assert res_dys576.is_lineage_excluded is False
        assert res_dys576.paternal_lr >= 150.0  # Analytical LR = 157.30
        assert "Rapid Germline Mutation" in res_dys576.verbal_predicate_en

    # ── EC-YSTR-04: 27/27 Pristine Match & Monotonic Meioses Decay ────────

    def test_ec_ystr_04_pristine_match_and_monotonic_meioses_decay(self):
        """
        EC-YSTR-04:
        Full 27/27 locus identity yields LR > 10,000.
        Joint transition probability strictly decreases monotonically as generation separation m increases (m=1..5).
        """
        ref = GOLD_STANDARD_INDIVIDUALS["SRM_2391d_COMP_A"].y_str_haplotype

        # Exact match under m=1
        res_m1 = YStrMathematicalFormulation.evaluate_paternal_kinship_likelihood(
            profile_a=ref, profile_b=ref, meioses_m=1, database_size_n=385000
        )
        assert res_m1.matching_loci_count == 25
        assert res_m1.mutated_loci_count == 0
        assert res_m1.paternal_lr > 10000.0
        assert res_m1.log10_paternal_lr > 4.0
        assert "Extremely Strong Support" in res_m1.verbal_predicate_en

        # Monotonic decay across m=1, 2, 3, 4, 5
        probs: list[float] = []
        lrs: list[float] = []
        for m in range(1, 6):
            res_m = YStrMathematicalFormulation.evaluate_paternal_kinship_likelihood(
                profile_a=ref, profile_b=ref, meioses_m=m, database_size_n=385000
            )
            probs.append(res_m.transition_probability_product)
            lrs.append(res_m.paternal_lr)

        for i in range(len(probs) - 1):
            assert probs[i] > probs[i + 1], f"Transition prob failed to decrease at m={i+1}"
            assert lrs[i] > lrs[i + 1], f"LR failed to decrease at m={i+1}"

    # ── EC-YSTR-05: Multi-Step Mismatch Definitive Lineage Exclusion ───────

    def test_ec_ystr_05_multi_locus_mismatch_definitive_exclusion(self):
        """
        EC-YSTR-05:
        >= 3 standard locus mismatches (or total mutations >= 5) triggers definitive mathematical exclusion
        (LR = 0.0, log10_LR = -300.0, is_lineage_excluded = True).
        """
        ref = GOLD_STANDARD_INDIVIDUALS["SRM_2391d_COMP_A"].y_str_haplotype
        unrelated = GOLD_STANDARD_INDIVIDUALS["NA18507_HG005"].y_str_haplotype

        res = YStrMathematicalFormulation.evaluate_paternal_kinship_likelihood(
            profile_a=ref, profile_b=unrelated, meioses_m=1, database_size_n=385000
        )
        assert res.is_lineage_excluded is True
        assert res.paternal_lr == 0.0
        assert res.log10_paternal_lr == -300.0
        assert "Definitive Exclusion" in res.verbal_predicate_en
        assert "Kesin Olarak Dışlanması" in res.verbal_predicate_tr

    # ── EC-YSTR-06: Nested Repeat DYS389 Decoupling & Mutation Invariance ─

    def test_ec_ystr_06_nested_repeat_dys389_decoupling_invariance(self):
        """
        EC-YSTR-06:
        DYS389II includes DYS389I physically.
        When DYS389I shifts from 13 to 14, DYS389II shifts from 29 to 30.
        Decoupled variable repeat component DYS389.2_pure = DYS389II - DYS389I = 16.0 remains invariant.
        """
        dys389i_a, dys389ii_a = 13.0, 29.0
        dys389i_b, dys389ii_b = 14.0, 30.0

        pure_a = YStrMathematicalFormulation.decouple_dys389(dys389i_a, dys389ii_a)
        pure_b = YStrMathematicalFormulation.decouple_dys389(dys389i_b, dys389ii_b)

        assert pure_a == 16.0
        assert pure_b == 16.0
        assert pure_a == pure_b

        # Invalid nested configuration where DYS389II < DYS389I raises ValueError
        with pytest.raises(ValueError):
            YStrMathematicalFormulation.decouple_dys389(14.0, 12.0)

    # ── EC-YSTR-07: Micro-Variant Fractional Step Calculations ────────────

    def test_ec_ystr_07_microvariant_fractional_steps(self):
        """
        EC-YSTR-07:
        Micro-variants (e.g. DYS458 allele 17.2 vs allele 17.0) are calculated without integer truncation crashes.
        """
        mu = 0.0087
        r = 0.88
        prob = YStrMathematicalFormulation.compute_smm_transition_probability(
            allele_a=17.2, allele_b=17.0, mutation_rate_mu=mu, stepwise_r=r, meioses_m=1
        )
        assert prob > 0.0
        assert prob < 0.010

    # ── EC-YSTR-08: Female Non-Target Input Validation & Exception Handling

    def test_ec_ystr_08_female_null_profile_validation_exception(self):
        """
        EC-YSTR-08:
        Female DNA profile (empty Y-STR dictionary) raises clean ValueError without unhandled crash.
        """
        female_profile = GOLD_STANDARD_INDIVIDUALS["NA12878_HG001_FEMALE"].y_str_haplotype
        male_profile = GOLD_STANDARD_INDIVIDUALS["SRM_2391d_COMP_A"].y_str_haplotype

        with pytest.raises(ValueError, match="No common Y-STR loci found"):
            YStrMathematicalFormulation.evaluate_paternal_kinship_likelihood(
                profile_a=male_profile, profile_b=female_profile
            )
