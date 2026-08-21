"""
Unit Test Suite for FORENZA DVI Mathematical Formulation Engine (Module 2.4).
Validates direct AM match, trio paternity likelihood, multi-omic fusion,
Bayesian posterior updating, and Hungarian bipartite assignment.
"""

import pytest
import math

from node.services.forensic.dvi.dvi_mathematical_formulation import (
    DviMathematicalFormulation,
    InterpolDecisionTier,
    INTERPOL_TIER_RULES,
)


class TestDirectAMAndTrioLocusCalculators:
    """Verifies single-locus pedigree likelihood formulas."""

    def test_direct_am_match(self):
        lr = DviMathematicalFormulation.calculate_direct_am_locus_lr(
            pm_genotype=(14.0, 15.0),
            am_genotype=(14.0, 15.0),
            freq_p=0.10,
            freq_q=0.20,
            theta=0.0,
        )
        # P(14, 15) = 2 * 0.10 * 0.20 = 0.04 -> LR = 25.0
        assert abs(lr - 25.0) < 1e-4

    def test_direct_am_mismatch(self):
        lr = DviMathematicalFormulation.calculate_direct_am_locus_lr(
            pm_genotype=(14.0, 15.0),
            am_genotype=(16.0, 17.0),
            freq_p=0.10,
            freq_q=0.20,
        )
        assert lr == 0.0

    def test_trio_paternity_valid_transmission(self):
        # Child: (14, 16), Mother: (14, 15), Father: (16, 17)
        # Mother passes 14 (prob 0.5), Father passes 16 (prob 0.5) -> prob_hp = 0.25
        # Hd: Mother passes 14, Random man passes 16 (freq 0.10) -> prob_hd = 0.5 * 0.10 = 0.05
        # LR = 0.25 / 0.05 = 5.0
        freqs = {14.0: 0.20, 15.0: 0.15, 16.0: 0.10, 17.0: 0.05}
        lr = DviMathematicalFormulation.calculate_trio_paternity_locus_lr(
            child_gt=(14.0, 16.0),
            mother_gt=(14.0, 15.0),
            father_gt=(16.0, 17.0),
            freq_dict=freqs,
        )
        assert abs(lr - 5.0) < 1e-4

    def test_trio_paternity_mendelian_exclusion(self):
        # Child: (18, 19), Mother: (14, 15), Father: (16, 17) -> Exclusion
        freqs = {14.0: 0.20, 15.0: 0.15, 16.0: 0.10, 17.0: 0.05, 18.0: 0.05, 19.0: 0.05}
        lr = DviMathematicalFormulation.calculate_trio_paternity_locus_lr(
            child_gt=(18.0, 19.0),
            mother_gt=(14.0, 15.0),
            father_gt=(16.0, 17.0),
            freq_dict=freqs,
        )
        assert lr == 0.0


class TestMultiOmicFusionAndBayesianUpdating:
    """Verifies multi-omic fusion and Bayesian posterior calculations."""

    def test_multi_omic_joint_lr(self):
        joint_lr, log10_joint = DviMathematicalFormulation.compute_multi_omic_joint_lr(
            autosomal_lr=5.2e3,
            ystr_p_upper=0.0002,
            mtdna_p_upper=0.0001,
            has_ystr=True,
            has_mtdna=True,
        )
        # LR_Joint = 5.2e3 * 5000 * 10000 = 2.6e11
        assert abs(joint_lr - 2.6e11) < 1e5
        assert abs(log10_joint - 11.41497) < 1e-4

    def test_posterior_probability_calculation(self):
        w = DviMathematicalFormulation.compute_posterior_probability(joint_lr=1.0e6, prior=0.001)
        # (1e6 * 0.001) / (1e6 * 0.001 + 0.999) = 1000 / 1000.999 ≈ 0.999001997
        assert abs(w - 0.999001997) < 1e-6


class TestInterpolTiersAndBipartiteAssignment:
    """Verifies Interpol decision tiers and Hungarian 1-to-1 matching."""

    def test_interpol_tier_classification(self):
        tier_def, _ = DviMathematicalFormulation.classify_interpol_tier(1.5e6)
        assert tier_def == InterpolDecisionTier.DEFINITIVE_IDENTIFICATION

        tier_prob, _ = DviMathematicalFormulation.classify_interpol_tier(5.0e4)
        assert tier_prob == InterpolDecisionTier.PROBABLE_MATCH

        tier_inconc, _ = DviMathematicalFormulation.classify_interpol_tier(10.0)
        assert tier_inconc == InterpolDecisionTier.INCONCLUSIVE

        tier_excl, _ = DviMathematicalFormulation.classify_interpol_tier(1.0e-3)
        assert tier_excl == InterpolDecisionTier.EXCLUSION

    def test_bipartite_assignment_mutual_exclusivity(self):
        # Cost matrix: PM1 has highest score with AM1, PM2 also has high score with AM1 but higher with AM2
        pm_ids = ["PM1", "PM2"]
        am_ids = ["AM1", "AM2"]
        matrix = [
            [1.0e8, 1.0e2],
            [1.0e7, 1.0e9],
        ]
        assignments = DviMathematicalFormulation.solve_bipartite_assignment(matrix, pm_ids, am_ids)
        assert len(assignments) == 2
        # PM2 should match AM2 (1.0e9), PM1 should match AM1 (1.0e8)
        assigned_dict = {pm: am for pm, am, score in assignments}
        assert assigned_dict["PM2"] == "AM2"
        assert assigned_dict["PM1"] == "AM1"
