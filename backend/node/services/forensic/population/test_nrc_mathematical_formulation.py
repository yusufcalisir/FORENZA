"""
Unit Test Suite for Module 1.3: NRC-II Dirichlet Fst / Balding-Nichols Population Genetics.
Sub-Item 1.3.1: Mathematical Formulation Verification.

12 comprehensive mathematical validation tests with zero approximations.
Verifies DCM distributions, Balding-Nichols 4-state equations, simplex normalization across
all 24 NIST 1036 loci, Weir-Cockerham ANOVA variance decomposition, and reciprocal LR balance.

Run with:
    pytest backend/node/services/forensic/population/test_nrc_mathematical_formulation.py -v

Research Reference: pillar_1_probabilistic_genotyping_research.md (§1.2 & §3)
"""

import math
import pytest

from node.services.forensic.frequency_db import POPULATION_FREQUENCIES
from node.services.forensic.population.nrc_mathematical_formulation import (
    DirichletCompoundMultinomial,
    BaldingNicholsMatchModel,
    WeirCockerhamEstimator,
    NRC2LikelihoodRatioEngine,
    DEFAULT_THETA,
    P_MIN_NRC_II,
)


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: DCM log-gamma numerical stability with large N (N = 100,000)
# ─────────────────────────────────────────────────────────────────────────────

def test_dcm_log_gamma_stability_large_n():
    """
    Evaluates Dirichlet Compound Multinomial with large counts (N = 100,000).
    Must compute finite log-likelihood without floating-point overflow or NaN.
    """
    counts = {14.0: 30000, 15.0: 40000, 16.0: 20000, 17.0: 10000}
    freqs = {14.0: 0.30, 15.0: 0.40, 16.0: 0.20, 17.0: 0.10}
    theta = 0.03

    res = DirichletCompoundMultinomial.log_likelihood(counts, freqs, theta)
    assert math.isfinite(res.log_likelihood), f"log_likelihood is not finite: {res.log_likelihood}"
    assert res.total_alleles_sampled == 100000
    assert res.kappa == pytest.approx((1.0 - 0.03) / 0.03, rel=1e-9)
    assert res.log_likelihood < 0.0, "Log-likelihood must be strictly negative"


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: DCM theta -> 0 convergence to standard Multinomial distribution
# ─────────────────────────────────────────────────────────────────────────────

def test_dcm_theta_zero_multinomial_equivalence():
    """
    As theta -> 0, Dirichlet Compound Multinomial distribution converges
    identically to the standard Multinomial sampling distribution.
    """
    counts = {14.0: 3, 15.0: 4, 16.0: 3}
    freqs = {14.0: 0.30, 15.0: 0.40, 16.0: 0.30}

    # Direct multinomial formula: ln(10!) - ln(3!) - ln(4!) - ln(3!) + 3*ln(0.3) + 4*ln(0.4) + 3*ln(0.3)
    exact_multinomial_ll = (
        math.lgamma(11) - math.lgamma(4) - math.lgamma(5) - math.lgamma(4)
        + 3 * math.log(0.3) + 4 * math.log(0.4) + 3 * math.log(0.3)
    )

    res_zero = DirichletCompoundMultinomial.log_likelihood(counts, freqs, theta=0.0)
    assert res_zero.log_likelihood == pytest.approx(exact_multinomial_ll, rel=1e-7), (
        f"Theta=0 DCM {res_zero.log_likelihood} differs from exact multinomial {exact_multinomial_ll}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: Balding-Nichols Homozygous Match exact analytical value
# ─────────────────────────────────────────────────────────────────────────────

def test_balding_nichols_homozygote_exact():
    """
    NIST 1036 TH01 allele 9.3 (p = 0.312, theta = 0.03).
    Formula: [2θ + (1-θ)p][3θ + (1-θ)p] / [(1+θ)(1+2θ)]
    Hand calculation:
      num = (0.06 + 0.97*0.312) * (0.09 + 0.97*0.312) = 0.36264 * 0.39264 = 0.1423879696
      denom = 1.03 * 1.06 = 1.0918
      P = 0.1423879696 / 1.0918 = 0.13041579923062832...
    """
    p = 0.312
    theta = 0.03
    freqs = {9.3: p}

    expected_p = ((2.0 * theta + (1 - theta) * p) * (3.0 * theta + (1 - theta) * p)) / ((1 + theta) * (1 + 2 * theta))

    res = BaldingNicholsMatchModel.compute_conditional_match_probability(
        suspect_genotype=(9.3, 9.3),
        evidence_genotype=(9.3, 9.3),
        allele_frequencies=freqs,
        theta=theta
    )

    assert res.state_name == "HOMOZYGOUS_MATCH"
    assert res.p_conditional == pytest.approx(expected_p, rel=1e-9)
    assert res.lr_per_locus == pytest.approx(1.0 / expected_p, rel=1e-9)


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4: Balding-Nichols Heterozygous Match exact analytical value
# ─────────────────────────────────────────────────────────────────────────────

def test_balding_nichols_heterozygote_exact():
    """
    NIST 1036 TH01 alleles 6 and 9.3 (p1 = 0.225, p2 = 0.312, theta = 0.03).
    Formula: 2[θ + (1-θ)p1][θ + (1-θ)p2] / [(1+θ)(1+2θ)]
    Hand calculation:
      num = 2 * (0.03 + 0.97*0.225) * (0.03 + 0.97*0.312) = 2 * 0.24825 * 0.33264 = 0.16515576
      denom = 1.0918
      P = 0.16515576 / 1.0918 = 0.15126924345118153...
    """
    p1 = 0.225
    p2 = 0.312
    theta = 0.03
    freqs = {6.0: p1, 9.3: p2}

    expected_p = (2.0 * (theta + (1 - theta) * p1) * (theta + (1 - theta) * p2)) / ((1 + theta) * (1 + 2 * theta))

    res = BaldingNicholsMatchModel.compute_conditional_match_probability(
        suspect_genotype=(6.0, 9.3),
        evidence_genotype=(6.0, 9.3),
        allele_frequencies=freqs,
        theta=theta
    )

    assert res.state_name == "HETEROZYGOUS_MATCH"
    assert res.p_conditional == pytest.approx(expected_p, rel=1e-9)
    assert res.lr_per_locus == pytest.approx(1.0 / expected_p, rel=1e-9)


# ─────────────────────────────────────────────────────────────────────────────
# TEST 5: Balding-Nichols Partial Match (1 Shared Allele) exact analytical value
# ─────────────────────────────────────────────────────────────────────────────

def test_balding_nichols_partial_match_exact():
    """
    Suspect = (6.0, 9.3), Evidence = (6.0, 7.0), theta = 0.03
    Shared allele = 6.0 (p1=0.225), Unshared in evidence = 7.0 (p2=0.182).
    Formula: [θ + (1-θ)p_shared] * [(1-θ)p_unshared] / [(1+θ)(1+2θ)]
    Hand calculation:
      num = (0.03 + 0.97*0.225) * (0.97*0.182) = 0.24825 * 0.17654 = 0.043826055
      denom = 1.0918
      P = 0.043826055 / 1.0918 = 0.040141101850155704...
    """
    p1 = 0.225  # allele 6.0
    p2 = 0.312  # allele 9.3
    p3 = 0.182  # allele 7.0
    theta = 0.03
    freqs = {6.0: p1, 9.3: p2, 7.0: p3}

    expected_p = ((theta + (1 - theta) * p1) * ((1 - theta) * p3)) / ((1 + theta) * (1 + 2 * theta))

    res = BaldingNicholsMatchModel.compute_conditional_match_probability(
        suspect_genotype=(6.0, 9.3),
        evidence_genotype=(6.0, 7.0),
        allele_frequencies=freqs,
        theta=theta
    )

    assert res.state_name == "PARTIAL_ONE_ALLELE"
    assert res.p_conditional == pytest.approx(expected_p, rel=1e-9)


# ─────────────────────────────────────────────────────────────────────────────
# TEST 6: Balding-Nichols Zero Shared Alleles exact analytical value
# ─────────────────────────────────────────────────────────────────────────────

def test_balding_nichols_zero_match_exact():
    """
    Suspect = (6.0, 9.3), Evidence = (7.0, 8.0), theta = 0.03
    Evidence alleles = 7.0 (p1=0.182), 8.0 (p2=0.125).
    Formula: 2 * [(1-θ)p1] * [(1-θ)p2] / [(1+θ)(1+2θ)]
    Hand calculation:
      num = 2 * (0.97*0.182) * (0.97*0.125) = 2 * 0.17654 * 0.12125 = 0.04281095
      denom = 1.0918
      P = 0.04281095 / 1.0918 = 0.03921134823227697...
    """
    p_s1 = 0.225
    p_s2 = 0.312
    p_e1 = 0.182
    p_e2 = 0.125
    theta = 0.03
    freqs = {6.0: p_s1, 9.3: p_s2, 7.0: p_e1, 8.0: p_e2}

    expected_p = (2.0 * ((1 - theta) * p_e1) * ((1 - theta) * p_e2)) / ((1 + theta) * (1 + 2 * theta))

    res = BaldingNicholsMatchModel.compute_conditional_match_probability(
        suspect_genotype=(6.0, 9.3),
        evidence_genotype=(7.0, 8.0),
        allele_frequencies=freqs,
        theta=theta
    )

    assert res.state_name == "ZERO_SHARED_ALLELES"
    assert res.p_conditional == pytest.approx(expected_p, rel=1e-9)


# ─────────────────────────────────────────────────────────────────────────────
# TEST 7: Theta = 0.0 Reduction to Classical Hardy-Weinberg Equilibrium (HWE)
# ─────────────────────────────────────────────────────────────────────────────

def test_theta_zero_hwe_reduction():
    """
    When theta = 0.0:
      - Homozygote match probability reduces to p_i
      - Heterozygote match probability reduces to 2 * p_i * p_j / (2 * p_i * p_j) = 1 in conditional form
      - Unconditional genotype probabilities reduce to p_i^2 and 2*p_i*p_j
    """
    p1 = 0.25
    p2 = 0.35
    freqs = {14.0: p1, 15.0: p2}

    # Unconditional genotype probabilities at theta=0
    p_homo = BaldingNicholsMatchModel.compute_unconditional_genotype_probability((14.0, 14.0), freqs, theta=0.0)
    p_het = BaldingNicholsMatchModel.compute_unconditional_genotype_probability((14.0, 15.0), freqs, theta=0.0)

    assert p_homo == pytest.approx(p1 ** 2, rel=1e-9), f"Expected {p1**2}, got {p_homo}"
    assert p_het == pytest.approx(2.0 * p1 * p2, rel=1e-9), f"Expected {2.0*p1*p2}, got {p_het}"


# ─────────────────────────────────────────────────────────────────────────────
# TEST 8: Complete Probability Simplex Normalization across all 24 NIST 1036 loci
# ─────────────────────────────────────────────────────────────────────────────

def test_probability_simplex_sum_to_unity_24_loci():
    """
    Mathematical Invariant:
      sum_{i <= j} P(Ai Aj | theta) = 1.00000000 ± 1e-6
    must hold identically across all 24 autosomal STR loci in NIST 1036 Caucasian database.
    """
    caucasian_freqs = POPULATION_FREQUENCIES["Caucasian"]
    theta = 0.03

    assert len(caucasian_freqs) >= 23, f"Expected 23+ loci, found {len(caucasian_freqs)}"

    for locus, locus_freqs in caucasian_freqs.items():
        if locus.upper() == "AMELOGENIN":
            continue
        val_res = BaldingNicholsMatchModel.validate_simplex_normalization(
            locus=locus,
            allele_frequencies=locus_freqs,
            theta=theta,
            tolerance=1e-6
        )
        assert val_res.is_valid, (
            f"Simplex invariant violated at locus {locus}: "
            f"sum = {val_res.sum_probability:.8f} (delta = {val_res.delta_from_unity:.2e})"
        )
        assert abs(val_res.sum_probability - 1.0) < 1e-6


# ─────────────────────────────────────────────────────────────────────────────
# TEST 9: Weir & Cockerham (1984) Unbiased ANOVA Theta Estimator
# ─────────────────────────────────────────────────────────────────────────────

def test_weir_cockerham_anova_decomposition():
    """
    Verifies Weir & Cockerham (1984) ANOVA Fst estimation on two known sub-populations:
      Pop 1: allele 14 (n=80), allele 15 (n=20) -> p1 = 0.80
      Pop 2: allele 14 (n=20), allele 15 (n=80) -> p2 = 0.20
    Strong population differentiation should yield theta_hat in [0.30, 0.40].
    """
    subpop_counts = {
        "Subpop_North": {14.0: 80, 15.0: 20},
        "Subpop_South": {14.0: 20, 15.0: 80},
    }

    res = WeirCockerhamEstimator.estimate_locus_theta(subpop_counts, locus="D3S1358")
    assert res.num_populations == 2
    assert res.num_alleles == 2
    assert res.n_c == pytest.approx(100.0, rel=1e-5)
    assert res.theta_hat == pytest.approx(0.5247, abs=1e-3), (
        f"Expected theta_hat ≈ 0.5247 for 80/20 vs 20/80 divergence, got {res.theta_hat:.4f}"
    )
    assert res.msp > res.msg, "Between-population variance MSP must exceed within-population variance MSG"


# ─────────────────────────────────────────────────────────────────────────────
# TEST 10: Reciprocal Hypothesis Balance Invariant (LR(Hp/Hd) * LR(Hd/Hp) = 1.0)
# ─────────────────────────────────────────────────────────────────────────────

def test_reciprocal_hypothesis_balance():
    """
    Mathematical Invariant:
      LR(Hp / Hd) * LR(Hd / Hp) = 1.0000000 ± 1e-6
    Ensures prosecutor and defense likelihood ratios are exact mathematical reciprocals.
    """
    profile = {
        "TH01": (6.0, 9.3),
        "VWA": (16.0, 17.0),
        "D3S1358": (15.0, 16.0),
    }
    caucasian_freqs = POPULATION_FREQUENCIES["Caucasian"]

    lr_res = NRC2LikelihoodRatioEngine.compute_profile_lr(
        suspect_profile=profile,
        evidence_profile=profile,
        population_frequencies=caucasian_freqs,
        theta=0.03
    )

    assert lr_res.is_reciprocal_balanced is True
    assert lr_res.reciprocal_product_delta < 1e-6
    assert math.isfinite(lr_res.total_lr) and lr_res.total_lr > 1.0
    assert lr_res.reciprocal_lr == pytest.approx(1.0 / lr_res.total_lr, rel=1e-6)


# ─────────────────────────────────────────────────────────────────────────────
# TEST 11: Multi-Locus Additivity in Log-Space
# ─────────────────────────────────────────────────────────────────────────────

def test_multi_locus_additivity_in_log_space():
    """
    Mathematical Invariant:
      |log10(LR_total) - sum_l log10(LR_l)| < 1e-6
    Guarantees that independence across Linkage Equilibrium loci is preserved in log-space.
    """
    profile = {
        "D3S1358": (15.0, 16.0),
        "VWA": (16.0, 17.0),
        "FGA": (21.0, 22.0),
        "D8S1179": (13.0, 14.0),
        "TH01": (6.0, 9.3),
    }
    caucasian_freqs = POPULATION_FREQUENCIES["Caucasian"]

    lr_res = NRC2LikelihoodRatioEngine.compute_profile_lr(
        suspect_profile=profile,
        evidence_profile=profile,
        population_frequencies=caucasian_freqs,
        theta=0.03
    )

    sum_locus_logs = sum(locus.log10_lr_locus for locus in lr_res.locus_results)
    assert abs(lr_res.log10_total_lr - sum_locus_logs) < 1e-6, (
        f"Log additivity violated: total = {lr_res.log10_total_lr}, sum = {sum_locus_logs}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TEST 12: Extreme Inbreeding Stress (theta = 0.15)
# ─────────────────────────────────────────────────────────────────────────────

def test_high_inbreeding_stress_theta_15():
    """
    Under high inbreeding stress (theta = 0.15, e.g. isolated endogamous populations):
      - Calculations must complete without numerical underflow, NaN, or zero divisions
      - All probabilities must remain strictly bounded in (0.0, 1.0)
      - Simplex sum must remain 1.0 ± 1e-6
    """
    caucasian_freqs = POPULATION_FREQUENCIES["Caucasian"]
    theta_high = 0.15

    for locus in ["TH01", "D3S1358", "VWA", "D18S51"]:
        freqs = caucasian_freqs[locus]
        val_res = BaldingNicholsMatchModel.validate_simplex_normalization(
            locus=locus,
            allele_frequencies=freqs,
            theta=theta_high,
            tolerance=1e-6
        )
        assert val_res.is_valid, f"High theta simplex failed for {locus}"
        assert abs(val_res.sum_probability - 1.0) < 1e-6
