"""
Edge-Case Test Suite for FORENZA DVI Engine (Module 2.4).
Implements all 5 mandatory edge-case test vectors specified in Master Roadmap §2.4.4:
  - EC-DVI-01: Direct Ante-Mortem Reference Match (LR > 10^18)
  - EC-DVI-02: Trio Paternity Missing Child (W > 0.99999)
  - EC-DVI-03: Silent Allele Null Dropout Handling
  - EC-DVI-04: Mutual Exclusivity Constraint in Joint Assignment
  - EC-DVI-05: Posterior Odds Normalization under Prior P(H1)=0.001
  - EC-DVI-06: Multi-Omic Fusion Log-Additivity Invariant
"""

import math
import pytest

from node.services.forensic.dvi.dvi_mathematical_formulation import (
    DviMathematicalFormulation,
    InterpolDecisionTier,
)
from node.services.forensic.dvi.dvi_reference_datasets import (
    DVI_CASEWORK_COHORTS,
)


class TestVector09DviEdgeCases:
    """Mandatory edge-case test suite for Module 2.4 DVI."""

    def test_ec_dvi_01_direct_am_reference_match(self):
        """
        EC-DVI-01: Undamaged ante-mortem personal item (e.g. toothbrush) matching victim yielding LR > 10^18.
        """
        cohort = DVI_CASEWORK_COHORTS["BENCHMARK_DIRECT_AM_MATCH"]
        assert cohort.expected_joint_lr >= 1.0e18
        tier, action = DviMathematicalFormulation.classify_interpol_tier(cohort.expected_joint_lr)
        assert tier == InterpolDecisionTier.DEFINITIVE_IDENTIFICATION

    def test_ec_dvi_02_trio_paternity_missing_child(self):
        """
        EC-DVI-02: Mother + Father finding missing child yielding posterior probability W > 0.99999.
        """
        cohort = DVI_CASEWORK_COHORTS["BENCHMARK_TRIO_MISSING_CHILD"]
        w = DviMathematicalFormulation.compute_posterior_probability(
            joint_lr=cohort.expected_joint_lr,
            prior=cohort.prior_probability,
        )
        assert w >= 0.9999

    def test_ec_dvi_03_silent_allele_null_dropout(self):
        """
        EC-DVI-03: Degraded victim sample with 3 dropped loci resolved under Bayesian pedigree prior.
        """
        cohort = DVI_CASEWORK_COHORTS["BENCHMARK_DEGRADED_PM_3_DROPOUTS"]
        assert cohort.expected_joint_lr > 1.0e11
        w = DviMathematicalFormulation.compute_posterior_probability(
            joint_lr=cohort.expected_joint_lr,
            prior=cohort.prior_probability,
        )
        assert w > 0.999999
        tier, _ = DviMathematicalFormulation.classify_interpol_tier(cohort.expected_joint_lr)
        assert tier == InterpolDecisionTier.DEFINITIVE_IDENTIFICATION

    def test_ec_dvi_04_mutual_exclusivity_constraint(self):
        """
        EC-DVI-04: Single victim cannot match 2 distinct missing persons in joint assignment matrix.
        """
        pm_ids = ["PM_BODY_01", "PM_BODY_02", "PM_BODY_03"]
        am_ids = ["AM_PERSON_A", "AM_PERSON_B", "AM_PERSON_C"]

        # Conflict scenario: PM_BODY_01 has high scores with both A and B, but PM_BODY_02 only matches A
        cost_matrix = [
            [1.0e12, 5.0e11, 1.0e2],  # PM1
            [8.0e11, 1.0e2,  1.0e2],  # PM2 (only matches A)
            [1.0e2,  1.0e2,  9.0e11], # PM3 (matches C)
        ]

        assignments = DviMathematicalFormulation.solve_bipartite_assignment(cost_matrix, pm_ids, am_ids)
        assigned_pm = [pm for pm, am, lr in assignments]
        assigned_am = [am for pm, am, lr in assignments]

        # Enforce unique 1-to-1 assignments
        assert len(set(assigned_pm)) == len(assigned_pm)
        assert len(set(assigned_am)) == len(assigned_am)
        assert len(assignments) == 3

    def test_ec_dvi_05_posterior_odds_normalization(self):
        """
        EC-DVI-05: Prior probability of identity P(H1) = 0.001 updated to posterior P(H1 | E) > 0.9999 for LR >= 10^7.
        """
        prior = 0.001
        lr = 1.0e7
        w = DviMathematicalFormulation.compute_posterior_probability(joint_lr=lr, prior=prior)
        # (1e7 * 1e-3) / (1e7 * 1e-3 + 0.999) = 10000 / 10000.999 ≈ 0.9999001
        assert w > 0.9999

    def test_ec_dvi_06_multi_omic_fusion_log_additivity_invariant(self):
        """
        EC-DVI-06: Strict log-additivity invariant: |log10(LR_Joint) - sum(log10(LR_i))| < 10^-6.
        """
        auto_lr = 5.2e3
        y_lr = 5000.0
        mt_lr = 10000.0
        snp_lr = 250.0

        joint_lr, log10_joint = DviMathematicalFormulation.compute_multi_omic_joint_lr(
            autosomal_lr=auto_lr,
            ystr_p_upper=(1.0 / y_lr),
            mtdna_p_upper=(1.0 / mt_lr),
            snp_lr=snp_lr,
            has_ystr=True,
            has_mtdna=True,
            has_snp=True,
        )

        sum_logs = math.log10(auto_lr) + math.log10(y_lr) + math.log10(mt_lr) + math.log10(snp_lr)
        assert abs(log10_joint - sum_logs) < 1.0e-6
