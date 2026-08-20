"""
FORENZA Forensic Evidence Operating System
Pillar 1 — Module 1.4: Low-Template DNA (LTDNA) Stochastic Modeling Engine
Sub-Item 1.4.1: Mathematical Formulation Unit Test Suite

Tests:
  1. TestLogisticDropoutFormulation: RFU, DNA Mass, Fragment Size, Asymptotes & Derivatives.
  2. TestPoissonDropinFormulation: Discrete Poisson PMF, CDF, Simplex Normalization.
  3. TestExponentialDropinHeightFormulation: Truncated Exponential PDF, CDF, Sub-AT Culling.
  4. TestHeterozygoteBalanceFormulation: H_b ratio, Stochastic Threshold (ST), AT Flags.
  5. TestCurranGillMarkovStateTransitions: 4-State Simplex, VECTOR_03 Golden Vector, Multi-Locus Additivity.
"""

import math
import pytest
from typing import Dict, List, Tuple

from backend.node.services.forensic.ltdna.ltdna_mathematical_formulation import (
    LTDNAMathematicalFormulation,
    DROPOUT_BETA0_RFU,
    DROPOUT_BETA1_RFU,
    DROPOUT_BETA0_MASS,
    DROPOUT_BETA1_MASS,
    DROPOUT_BETAS_BP,
    DROPIN_LAMBDA_POISSON,
    DROPIN_LAMBDA_HEIGHT,
    ANALYTICAL_THRESHOLD_RFU,
    STOCHASTIC_THRESHOLD_RFU,
    HB_FLAG_THRESHOLD,
)


# ===========================================================================
# 1. Logistic Allele Dropout Mathematical Tests
# ===========================================================================

class TestLogisticDropoutFormulation:
    """Verifies logistic sigmoid allele dropout formulations across RFU and mass domains."""

    def test_rfu_dropout_exact_analytical_values(self):
        """P(D | RFU) matches analytical values at key calibration points."""
        # 50 RFU: logit = 2.50 + (-0.025)*50 = 1.25 -> 1/(1+e^-1.25) ≈ 0.777300
        res_50 = LTDNAMathematicalFormulation.compute_dropout_probability_rfu(50.0)
        assert abs(res_50.logit_value - 1.25) < 1e-6
        expected_50 = 1.0 / (1.0 + math.exp(-1.25))
        assert abs(res_50.dropout_probability - expected_50) < 1e-6
        assert abs(res_50.dropout_probability - 0.777300) < 1e-4

        # 80 RFU (VECTOR_03): logit = 2.50 + (-0.025)*80 = 0.50 -> 1/(1+e^-0.50) ≈ 0.622459
        res_80 = LTDNAMathematicalFormulation.compute_dropout_probability_rfu(80.0)
        assert abs(res_80.logit_value - 0.50) < 1e-6
        expected_80 = 1.0 / (1.0 + math.exp(-0.50))
        assert abs(res_80.dropout_probability - expected_80) < 1e-6

        # 100 RFU: logit = 2.50 + (-0.025)*100 = 0.0 -> P(D) = 0.500000
        res_100 = LTDNAMathematicalFormulation.compute_dropout_probability_rfu(100.0)
        assert abs(res_100.logit_value - 0.0) < 1e-6
        assert abs(res_100.dropout_probability - 0.500000) < 1e-6

        # 150 RFU: logit = 2.50 + (-0.025)*150 = -1.25 -> 1/(1+e^1.25) ≈ 0.222700
        res_150 = LTDNAMathematicalFormulation.compute_dropout_probability_rfu(150.0)
        assert abs(res_150.logit_value - (-1.25)) < 1e-6
        expected_150 = 1.0 / (1.0 + math.exp(1.25))
        assert abs(res_150.dropout_probability - expected_150) < 1e-6
        assert abs(res_150.dropout_probability - 0.222700) < 1e-4

    def test_mass_dropout_exact_analytical_values(self):
        """P(D | pg) matches analytical values at key template dilution points."""
        # 15 pg (single-cell range): logit = 3.20 + (-0.080)*15 = 2.00 -> 1/(1+e^-2.00) ≈ 0.880797
        res_15 = LTDNAMathematicalFormulation.compute_dropout_probability_mass(15.0)
        assert abs(res_15.logit_value - 2.00) < 1e-6
        expected_15 = 1.0 / (1.0 + math.exp(-2.00))
        assert abs(res_15.dropout_probability - expected_15) < 1e-6
        assert abs(res_15.dropout_probability - 0.880797) < 1e-4

        # 40 pg: logit = 3.20 + (-0.080)*40 = 0.0 -> P(D) = 0.500000
        res_40 = LTDNAMathematicalFormulation.compute_dropout_probability_mass(40.0)
        assert abs(res_40.logit_value - 0.0) < 1e-6
        assert abs(res_40.dropout_probability - 0.500000) < 1e-6

        # 50 pg: logit = 3.20 + (-0.080)*50 = -0.80 -> 1/(1+e^0.80) ≈ 0.310026 (31.00% drop)
        res_50 = LTDNAMathematicalFormulation.compute_dropout_probability_mass(50.0)
        assert abs(res_50.logit_value - (-0.80)) < 1e-6
        expected_50 = 1.0 / (1.0 + math.exp(0.80))
        assert abs(res_50.dropout_probability - expected_50) < 1e-6
        assert abs(res_50.dropout_probability - 0.310026) < 1e-4

        # 100 pg: logit = 3.20 + (-0.080)*100 = -4.80 -> 1/(1+e^4.80) ≈ 0.008163 (0.82% drop)
        res_100 = LTDNAMathematicalFormulation.compute_dropout_probability_mass(100.0)
        assert abs(res_100.logit_value - (-4.80)) < 1e-6
        assert res_100.dropout_probability < 0.010
        assert abs(res_100.dropout_probability - 0.008163) < 1e-4

    def test_fragment_length_degradation_penalty(self):
        """Larger amplicons (higher bp) exhibit strictly higher dropout probability."""
        mass_pg = 30.0
        res_short = LTDNAMathematicalFormulation.compute_dropout_probability_fragment_size(mass_pg, amplicon_bp=120.0)
        res_medium = LTDNAMathematicalFormulation.compute_dropout_probability_fragment_size(mass_pg, amplicon_bp=220.0)
        res_long = LTDNAMathematicalFormulation.compute_dropout_probability_fragment_size(mass_pg, amplicon_bp=350.0)

        # Longer amplicon -> larger size penalty -> larger logit -> higher dropout probability
        assert res_short.logit_value < res_medium.logit_value < res_long.logit_value
        assert res_short.dropout_probability < res_medium.dropout_probability < res_long.dropout_probability

    def test_dropout_gradient_and_monotonicity(self):
        """Derivative dP(D)/dx is strictly negative across signal and mass ranges."""
        for rfu in [20.0, 50.0, 80.0, 100.0, 150.0, 250.0, 500.0]:
            res = LTDNAMathematicalFormulation.compute_dropout_probability_rfu(rfu)
            assert res.analytical_derivative < 0.0  # slope is negative

        # Verify monotonic decrease of dropout probability with increasing template mass
        masses = [10.0, 20.0, 30.0, 40.0, 50.0, 75.0, 100.0, 200.0]
        p_drops = [LTDNAMathematicalFormulation.compute_dropout_probability_mass(m).dropout_probability for m in masses]
        for i in range(len(p_drops) - 1):
            # As template mass increases, dropout probability decreases
            assert p_drops[i] > p_drops[i + 1], f"Monotonicity failed at mass {masses[i]} -> {masses[i+1]}"

    def test_critical_threshold_boundary(self):
        """Critical threshold accurately flags when dropout is below 1%."""
        res_crit_rfu = LTDNAMathematicalFormulation.compute_dropout_probability_rfu(300.0)
        assert not res_crit_rfu.is_below_critical
        assert res_crit_rfu.dropout_probability < 0.01

        res_sub_rfu = LTDNAMathematicalFormulation.compute_dropout_probability_rfu(100.0)
        assert res_sub_rfu.is_below_critical


# ===========================================================================
# 2. Poisson Allele Drop-in Mathematical Tests
# ===========================================================================

class TestPoissonDropinFormulation:
    """Verifies discrete Poisson drop-in count distribution and cumulative simplex."""

    def test_poisson_exact_analytical_pmf(self):
        """P(C = k) matches analytical Poisson values with lambda_c = 0.020."""
        # k = 0: e^-0.020 ≈ 0.98019867
        res_0 = LTDNAMathematicalFormulation.compute_dropin_poisson_pmf(0, lambda_c=0.020)
        assert abs(res_0.poisson_pmf - math.exp(-0.020)) < 1e-9
        assert abs(res_0.poisson_pmf - 0.98019867) < 1e-6
        assert res_0.is_zero_dropin

        # k = 1: 0.020 * e^-0.020 ≈ 0.01960397
        res_1 = LTDNAMathematicalFormulation.compute_dropin_poisson_pmf(1, lambda_c=0.020)
        assert abs(res_1.poisson_pmf - (0.020 * math.exp(-0.020))) < 1e-9
        assert abs(res_1.poisson_pmf - 0.01960397) < 1e-6
        assert not res_1.is_zero_dropin

        # k = 2: (0.020^2 * e^-0.020) / 2 ≈ 0.00019604
        res_2 = LTDNAMathematicalFormulation.compute_dropin_poisson_pmf(2, lambda_c=0.020)
        expected_2 = (0.020 ** 2 * math.exp(-0.020)) / 2.0
        assert abs(res_2.poisson_pmf - expected_2) < 1e-9

    def test_poisson_cumulative_sum_to_one(self):
        """Sum of Poisson probabilities from k=0 to 10 equals 1.00000000."""
        total_p = sum(
            LTDNAMathematicalFormulation.compute_dropin_poisson_pmf(k, lambda_c=0.020).poisson_pmf
            for k in range(10)
        )
        assert abs(total_p - 1.0) < 1e-9

    def test_poisson_cdf_monotonicity(self):
        """Poisson CDF increases monotonically towards 1.0."""
        cdf_vals = [
            LTDNAMathematicalFormulation.compute_dropin_poisson_pmf(k, lambda_c=0.020).poisson_cdf
            for k in range(5)
        ]
        for i in range(len(cdf_vals) - 1):
            assert cdf_vals[i] <= cdf_vals[i + 1]
        assert abs(cdf_vals[-1] - 1.0) < 1e-6

    def test_poisson_invalid_inputs(self):
        """Negative counts or non-positive rates raise ValueError."""
        with pytest.raises(ValueError, match="non-negative"):
            LTDNAMathematicalFormulation.compute_dropin_poisson_pmf(-1)
        with pytest.raises(ValueError, match="strictly positive"):
            LTDNAMathematicalFormulation.compute_dropin_poisson_pmf(1, lambda_c=0.0)


# ===========================================================================
# 3. Truncated Exponential Drop-in Peak Height PDF Tests
# ===========================================================================

class TestExponentialDropinHeightFormulation:
    """Verifies truncated exponential drop-in peak height probability density."""

    def test_dropin_height_pdf_exact_values(self):
        """f(h_C) matches analytical exponential values above AT = 50.0 RFU."""
        # At AT (h_C = 50 RFU): f(50) = 0.015 * e^0 = 0.01500000
        res_50 = LTDNAMathematicalFormulation.compute_dropin_height_pdf(50.0, at=50.0, lambda_h=0.015)
        assert abs(res_50.height_pdf - 0.01500000) < 1e-7
        assert abs(res_50.height_cdf - 0.0) < 1e-7
        assert res_50.is_above_at

        # At 100 RFU: f(100) = 0.015 * e^(-0.015 * 50) = 0.015 * e^-0.75 ≈ 0.00708518
        res_100 = LTDNAMathematicalFormulation.compute_dropin_height_pdf(100.0, at=50.0, lambda_h=0.015)
        expected_100 = 0.015 * math.exp(-0.015 * 50.0)
        assert abs(res_100.height_pdf - expected_100) < 1e-7
        expected_cdf_100 = 1.0 - math.exp(-0.015 * 50.0)
        assert abs(res_100.height_cdf - expected_cdf_100) < 1e-7

    def test_sub_at_culling(self):
        """Peak heights below AT = 50.0 RFU return zero PDF and CDF."""
        res_sub = LTDNAMathematicalFormulation.compute_dropin_height_pdf(40.0, at=50.0, lambda_h=0.015)
        assert res_sub.height_pdf == 0.0
        assert res_sub.height_cdf == 0.0
        assert not res_sub.is_above_at

    def test_theoretical_moments_and_decay(self):
        """Theoretical mean E[h_C] = AT + 1/lambda_h = 116.667 RFU and monotonic PDF decay."""
        res = LTDNAMathematicalFormulation.compute_dropin_height_pdf(75.0, at=50.0, lambda_h=0.015)
        assert abs(res.theoretical_mean - 116.6667) < 1e-3
        assert abs(res.theoretical_variance - 4444.4444) < 1e-2

        # Verify PDF strictly decreases as height increases above AT
        heights = [50.0, 75.0, 100.0, 150.0, 200.0, 300.0]
        pdfs = [LTDNAMathematicalFormulation.compute_dropin_height_pdf(h).height_pdf for h in heights]
        for i in range(len(pdfs) - 1):
            assert pdfs[i] > pdfs[i + 1]


# ===========================================================================
# 4. Heterozygote Balance (H_b) & Stochastic Quality Assessment Tests
# ===========================================================================

class TestHeterozygoteBalanceFormulation:
    """Verifies heterozygote balance H_b computation and stochastic flags."""

    def test_balanced_heterozygote_zero_flags(self):
        """High-template balanced peaks produce H_b >= 0.85 with no active flags."""
        res = LTDNAMathematicalFormulation.evaluate_heterozygote_balance(h1=800.0, h2=850.0)
        assert abs(res.h_balance - (800.0 / 850.0)) < 1e-5
        assert not res.imbalance_flag
        assert not res.stochastic_threshold_flag
        assert not res.at_flag
        assert not res.stochastic_flag_active
        assert "BALANCED" in res.interpretation

    def test_severe_imbalance_flag(self):
        """H_b < 0.60 correctly triggers imbalance flag."""
        res = LTDNAMathematicalFormulation.evaluate_heterozygote_balance(h1=200.0, h2=500.0)
        assert abs(res.h_balance - 0.40) < 1e-5
        assert res.imbalance_flag
        assert not res.stochastic_threshold_flag  # h_min = 200 >= 150
        assert res.stochastic_flag_active

    def test_stochastic_threshold_flag(self):
        """h_min < 150.0 RFU triggers stochastic threshold flag."""
        res = LTDNAMathematicalFormulation.evaluate_heterozygote_balance(h1=120.0, h2=140.0)
        assert res.h_balance > 0.60  # 120/140 = 0.857
        assert not res.imbalance_flag
        assert res.stochastic_threshold_flag  # 120 < 150
        assert res.stochastic_flag_active

    def test_analytical_threshold_flag(self):
        """Peak below AT = 50.0 RFU triggers AT flag."""
        res = LTDNAMathematicalFormulation.evaluate_heterozygote_balance(h1=45.0, h2=200.0)
        assert res.at_flag
        assert res.stochastic_flag_active

    def test_peak_order_symmetry(self):
        """H_b(h1, h2) equals H_b(h2, h1) identically."""
        res1 = LTDNAMathematicalFormulation.evaluate_heterozygote_balance(350.0, 700.0)
        res2 = LTDNAMathematicalFormulation.evaluate_heterozygote_balance(700.0, 350.0)
        assert res1.h_balance == res2.h_balance == 0.50


# ===========================================================================
# 5. Curran-Gill 4-State Markov State Genotype Transition Tests
# ===========================================================================

class TestCurranGillMarkovStateTransitions:
    """Verifies Curran-Gill stochastic transition probabilities and LR computations."""

    def test_transition_probability_simplex_sum_to_one(self):
        """Sum of all 4 Curran-Gill transition states equals 1.00000000."""
        for p_d in [0.05, 0.20, 0.3775, 0.50, 0.70, 0.88]:
            res = LTDNAMathematicalFormulation.evaluate_curran_gill_transition_probabilities(
                p_d1=p_d, p_d2=p_d, lambda_c=0.020
            )
            assert abs(res.simplex_sum - 1.0) < 1e-6

    def test_vector_03_golden_benchmark_ltdna_dropout(self):
        """
        VECTOR_03 — Golden Benchmark LTDNA Dropout Case.
        vWA locus: suspect (16, 17), observed 16@80RFU (17 dropped).
        P(D) stochastic penalty applied -> log10(LR) is reduced relative to full match.
        """
        # P(D) at 80 RFU from RFU logistic model
        p_d_res = LTDNAMathematicalFormulation.compute_dropout_probability_rfu(80.0)
        p_d = p_d_res.dropout_probability  # ≈ 0.622459

        res_lr = LTDNAMathematicalFormulation.compute_ltdna_single_locus_lr(
            locus="vWA",
            suspect_genotype=(16.0, 17.0),
            observed_peaks={16.0: 80.0},  # 17 dropped out
            p_dropout=p_d,
            lambda_c=0.020,
            pop_freqs={16.0: 0.211, 17.0: 0.273},
            theta=0.03,
        )

        assert res_lr.observed_state == "SINGLE_DROPOUT"
        assert res_lr.log10_lr > 0.0
        assert res_lr.log10_lr < 2.0
        assert abs(res_lr.log10_lr - 0.5604) < 1e-3
        assert "Support" in res_lr.verbal_en

    def test_multi_locus_log_additivity_invariant(self):
        """Composite multi-locus log10(LR) equals exact sum of per-locus log10(LR)."""
        suspect_profile = {
            "D3S1358": (15.0, 16.0),
            "vWA": (16.0, 17.0),
            "FGA": (21.0, 22.0),
            "D8S1179": (13.0, 14.0),
        }
        observed_profile = {
            "D3S1358": {15.0: 75.0, 16.0: 80.0},
            "vWA": {16.0: 90.0},  # single dropout
            "FGA": {21.0: 110.0, 22.0: 105.0},
            "D8S1179": {13.0: 85.0},  # single dropout
        }
        pop_db = {
            "D3S1358": {15.0: 0.282, 16.0: 0.231},
            "vWA": {16.0: 0.211, 17.0: 0.273},
            "FGA": {21.0: 0.185, 22.0: 0.198},
            "D8S1179": {13.0: 0.339, 14.0: 0.201},
        }

        res_multi = LTDNAMathematicalFormulation.compute_multi_locus_ltdna_lr(
            suspect_profile=suspect_profile,
            observed_profile=observed_profile,
            template_pg=50.0,
            pop_freqs_db=pop_db,
            theta=0.03,
        )

        sum_individual = sum(loc.log10_lr for loc in res_multi.locus_results)
        assert abs(res_multi.total_log10_lr - sum_individual) < 1e-4
        assert res_multi.additivity_verified
        assert res_multi.n_loci == 4

    def test_homozygote_dropout_transition(self):
        """Homozygote single-source profile evaluated correctly under dropout."""
        res_homo = LTDNAMathematicalFormulation.compute_ltdna_single_locus_lr(
            locus="TH01",
            suspect_genotype=(9.3, 9.3),
            observed_peaks={9.3: 120.0},
            p_dropout=0.20,
            pop_freqs={9.3: 0.312},
            theta=0.01,
        )
        assert res_homo.observed_state == "BOTH_PRESENT"
        assert res_homo.log10_lr > 0.0
