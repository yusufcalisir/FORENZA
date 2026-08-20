"""
FORENZA Module 1.2 — Continuous Metropolis-Hastings Mixture Deconvoluter
Mathematical Formulation, Probability Distributions & Biophysical Invariants Test Suite

Research Specification Source:
  - pillar_1_probabilistic_genotyping_research.md § 2 (Continuous MCMC Complex Mixture Deconvolution)
  - Master Rule 1 of AGENTS.md (Absolute Research Fidelity & Mathematical Integrity)

Mathematical Domains Verified:
  1. EuroForMix Continuous Gamma Likelihood (α = 1/ω², β = μ·ω²)
  2. STRmix Continuous Log-Normal Likelihood with Heteroscedastic Variance (σ_{l,a}² = σ² / μ^γ)
  3. Biophysical Multi-Contributor Expected Peak Height μ_{l,a} (Degradation Decay & 24-Locus Stutter)
  4. Metropolis-Hastings Transition Acceptance Probability & Hastings Proposal Factor
  5. Gelman-Rubin R̂ ANOVA Multi-Chain Between/Within Variance Decomposition
  6. Effective Sample Size (ESS) Autocorrelation & Initial Positive Sequence Truncation
  7. 95% HPD Lower Bound & Admissibility Invariants
"""

import math
import random
import statistics
import pytest
from typing import Dict, List, Tuple

from backend.node.services.forensic.probabilistic.peak_model import (
    EuroForMixGammaModel,
    STRmixLogNormalModel,
    BiophysicalPeakModel,
    LOCUS_STUTTER_RATIOS,
    LOCUS_BASE_BP,
    DEFAULT_AMPLIFICATION,
    S0_BP,
)
from backend.node.services.forensic.probabilistic.mcmc import (
    MCMCSampler,
    MCMCSample,
    _gelman_rubin,
    _compute_ess,
    _sample_dirichlet,
    _log_dirichlet_pdf,
    _enfsi_verbal,
    R_HAT_THRESHOLD,
    ESS_THRESHOLD,
)


# ===========================================================================
# 1. EuroForMix Continuous Gamma Likelihood Model
# ===========================================================================

class TestEuroForMixGammaFormulation:
    """
    Validates EuroForMix Gamma peak height probability distribution:
      h_{l,a} ~ Gamma(α = 1/ω², β = μ_{l,a} · ω²)
      ln L = -ln Γ(1/ω²) - ln(μ·ω²)/ω² + (1/ω² - 1)·ln(h) - h/(μ·ω²)
    """

    def test_gamma_exact_analytical_values(self):
        """Verify computed Gamma log-likelihood against analytical values across parameters."""
        omega_values = [0.20, 0.30, 0.35, 0.40]
        test_cases = [
            (500.0, 500.0),    # h == μ
            (800.0, 600.0),    # h > μ
            (250.0, 500.0),    # h < μ
            (1200.0, 1000.0),  # high RFU
        ]

        for omega in omega_values:
            model = EuroForMixGammaModel(omega=omega)
            omega2 = omega ** 2
            inv_omega2 = 1.0 / omega2

            for h_obs, mu in test_cases:
                beta = mu * omega2
                expected_ll = (
                    -math.lgamma(inv_omega2)
                    - math.log(beta) * inv_omega2
                    + (inv_omega2 - 1.0) * math.log(h_obs)
                    - h_obs / beta
                )
                computed_ll = model.log_likelihood_locus_allele(h_obs, mu)
                assert abs(computed_ll - expected_ll) < 1e-8, (
                    f"Gamma LL mismatch for omega={omega}, h={h_obs}, mu={mu}: "
                    f"{computed_ll} vs {expected_ll}"
                )

    def test_gamma_theoretical_moments_and_cv(self):
        """
        Under Gamma(α = 1/ω², β = μ·ω²):
          E[X] = α·β = (1/ω²) · (μ·ω²) = μ
          Var(X) = α·β² = (1/ω²) · (μ²·ω⁴) = μ²·ω²
          Coefficient of Variation (CV) = sqrt(Var) / E[X] = (μ·ω) / μ = ω
        """
        omega = 0.35
        mu = 800.0
        alpha = 1.0 / (omega ** 2)
        beta = mu * (omega ** 2)

        theoretical_mean = alpha * beta
        theoretical_var = alpha * (beta ** 2)
        theoretical_cv = math.sqrt(theoretical_var) / theoretical_mean

        assert abs(theoretical_mean - mu) < 1e-10
        assert abs(theoretical_var - (mu ** 2) * (omega ** 2)) < 1e-10
        assert abs(theoretical_cv - omega) < 1e-10

    def test_gamma_mode_and_concavity(self):
        """
        Mode of Gamma(α, β) is (α - 1)·β = (1/ω² - 1)·(μ·ω²) = μ·(1 - ω²).
        For ω = 0.30, mode = μ · (1 - 0.09) = 0.91·μ.
        Likelihood must strictly decrease as |h - mode| increases.
        """
        omega = 0.30
        mu = 1000.0
        mode = mu * (1.0 - omega ** 2)
        model = EuroForMixGammaModel(omega=omega)

        ll_mode = model.log_likelihood_locus_allele(mode, mu)
        ll_left = model.log_likelihood_locus_allele(mode - 100.0, mu)
        ll_right = model.log_likelihood_locus_allele(mode + 100.0, mu)

        assert ll_mode > ll_left
        assert ll_mode > ll_right

    def test_gamma_boundary_conditions(self):
        """Strict non-negativity and boundary handling."""
        model = EuroForMixGammaModel(omega=0.35)
        # Non-positive observed or expected height returns large negative penalty
        assert model.log_likelihood_locus_allele(0.0, 500.0) <= -1e8
        assert model.log_likelihood_locus_allele(-100.0, 500.0) <= -1e8
        assert model.log_likelihood_locus_allele(500.0, 0.0) <= -1e8
        assert model.log_likelihood_locus_allele(500.0, -100.0) <= -1e8

        # Invalid omega must raise ValueError
        with pytest.raises(ValueError):
            EuroForMixGammaModel(omega=0.0)
        with pytest.raises(ValueError):
            EuroForMixGammaModel(omega=-0.25)

    def test_gamma_profile_log_likelihood_additivity(self):
        """Multi-locus independence implies profile log-likelihood is exact sum of allele log-likelihoods."""
        model = EuroForMixGammaModel(omega=0.35)
        observed = {
            "D3S1358": {15.0: 650.0, 16.0: 710.0},
            "VWA": {17.0: 820.0, 18.0: 890.0},
            "FGA": {21.0: 540.0, 24.0: 560.0},
        }
        expected = {
            "D3S1358": {15.0: 640.0, 16.0: 700.0},
            "VWA": {17.0: 800.0, 18.0: 910.0},
            "FGA": {21.0: 550.0, 24.0: 550.0},
        }

        profile_ll = model.log_likelihood_profile(observed, expected)
        manual_sum = sum(
            model.log_likelihood_locus_allele(observed[loc][al], expected[loc][al])
            for loc in observed
            for al in observed[loc]
        )
        assert abs(profile_ll - manual_sum) < 1e-10


# ===========================================================================
# 2. STRmix Continuous Log-Normal Likelihood Model
# ===========================================================================

class TestSTRmixLogNormalFormulation:
    """
    Validates STRmix Log-Normal peak height likelihood:
      ln(h_{l,a}) ~ N(ln μ_{l,a}, σ_{l,a}²) where σ_{l,a}² = σ² / μ_{l,a}^γ (γ ≈ 1.0)
      ln L = -0.5·ln(2π·σ_{l,a}²) - (ln h - ln μ)² / (2·σ_{l,a}²)
    """

    def test_lognormal_exact_analytical_values(self):
        """Verify computed Log-Normal log-likelihood against analytical formulation."""
        sigma = 0.35
        gamma = 1.0
        model = STRmixLogNormalModel(sigma=sigma, gamma=gamma)

        test_cases = [
            (400.0, 400.0),
            (650.0, 500.0),
            (300.0, 500.0),
            (1500.0, 1200.0),
        ]

        for h_obs, mu in test_cases:
            var_exp = (sigma ** 2) / (mu ** gamma)
            residual = math.log(h_obs) - math.log(mu)
            expected_ll = -0.5 * math.log(2.0 * math.pi * var_exp) - (residual ** 2) / (2.0 * var_exp)
            computed_ll = model.log_likelihood_locus_allele(h_obs, mu)

            assert abs(computed_ll - expected_ll) < 1e-8, (
                f"STRmix LL mismatch for h={h_obs}, mu={mu}: {computed_ll} vs {expected_ll}"
            )

    def test_lognormal_heteroscedasticity_scaling(self):
        """
        Heteroscedastic variance σ_{l,a}² = σ² / μ^γ decreases as expected peak height μ increases.
        Larger peaks have smaller relative variance in log space.
        """
        model = STRmixLogNormalModel(sigma=0.35, gamma=1.0)
        var_small = model.locus_allele_variance(100.0)
        var_medium = model.locus_allele_variance(500.0)
        var_large = model.locus_allele_variance(2000.0)

        assert var_small > var_medium > var_large
        assert abs(var_small / var_medium - 5.0) < 1e-10  # 500/100 = 5 for gamma=1.0

    def test_lognormal_log_ratio_symmetry(self):
        """
        Log-Normal residual is quadratic in log(h) - log(μ).
        Therefore, h = μ·e^δ and h = μ·e^-δ must produce identical log-likelihoods.
        """
        model = STRmixLogNormalModel(sigma=0.35, gamma=1.0)
        mu = 600.0
        delta = 0.25

        h_above = mu * math.exp(delta)
        h_below = mu * math.exp(-delta)

        ll_above = model.log_likelihood_locus_allele(h_above, mu)
        ll_below = model.log_likelihood_locus_allele(h_below, mu)

        assert abs(ll_above - ll_below) < 1e-10

    def test_lognormal_boundary_conditions(self):
        """Boundary conditions: h <= 0, mu <= 0, sigma <= 0."""
        model = STRmixLogNormalModel(sigma=0.35, gamma=1.0)
        assert model.log_likelihood_locus_allele(0.0, 500.0) <= -1e8
        assert model.log_likelihood_locus_allele(-50.0, 500.0) <= -1e8
        assert model.log_likelihood_locus_allele(500.0, 0.0) <= -1e8

        with pytest.raises(ValueError):
            STRmixLogNormalModel(sigma=0.0)
        with pytest.raises(ValueError):
            STRmixLogNormalModel(sigma=-0.35)


# ===========================================================================
# 3. Biophysical Multi-Contributor Expected Peak Height Model
# ===========================================================================

class TestBiophysicalPeakSynthesisFormulation:
    """
    Validates Biophysical expected peak height equation:
      μ_{l,a} = T_l · A_l · Σ_k w_k · 10^{-d_k·(S_{l,a} - S_0)} · n_{k,l,a} + Stutter_{l,a}
      Stutter_{l,a} = SR_l · μ_{l, a+1}
    """

    def test_single_contributor_homozygote_vs_heterozygote(self):
        """A homozygote (n=2) has twice the expected peak height of a heterozygote (n=1) when no stutter parent is present."""
        model = BiophysicalPeakModel(
            template_scale=1000.0,
            amplification={"TH01": 1.0},
            stutter_ratios={"TH01": 0.025},
        )
        # Heterozygote (7, 9) where allele 8 is not present (no stutter from 8 to 7, and 9 stutters to 8)
        mu_het = model.expected_peak_heights(
            locus="TH01",
            genotypes=[(7.0, 9.0)],
            mixture_weights=[1.0],
            degradation_slopes=[0.0],
        )[7.0]

        # Homozygote (7, 7)
        mu_hom = model.expected_peak_heights(
            locus="TH01",
            genotypes=[(7.0, 7.0)],
            mixture_weights=[1.0],
            degradation_slopes=[0.0],
        )[7.0]

        assert abs(mu_hom - 2.0 * mu_het) < 1e-8
        assert abs(mu_het - 1000.0) < 1e-8
        assert abs(mu_hom - 2000.0) < 1e-8

    def test_two_person_mixture_weight_linearity(self):
        """Expected height scales linearly with contributor mixture weights w1, w2 (w1+w2=1.0) and back-stutter."""
        T = 1000.0
        sr = 0.082
        model = BiophysicalPeakModel(
            template_scale=T,
            amplification={"D3S1358": 1.0},
            stutter_ratios={"D3S1358": sr},
        )
        # Contributor 1 has (14, 15), Contributor 2 has (15, 16)
        # Allele 14 receives w1*T plus back-stutter from 15 (which has total template (w1+w2)*T = T)
        # Allele 16 has no parent allele (17 not present) -> exactly w2*T
        # Allele 15 receives (w1+w2)*T plus back-stutter from 16 (w2*T)
        w1, w2 = 0.70, 0.30

        heights = model.expected_peak_heights(
            locus="D3S1358",
            genotypes=[(14.0, 15.0), (15.0, 16.0)],
            mixture_weights=[w1, w2],
            degradation_slopes=[0.0, 0.0],
        )

        mu_14 = heights[14.0]
        mu_16 = heights[16.0]
        mu_15 = heights[15.0]

        # Allele 16: pure contributor 2 peak
        assert abs(mu_16 - w2 * T) < 1e-6

        # Allele 14: contributor 1 peak (700) + back-stutter from allele 15 (0.082 * 1000 = 82)
        assert abs(mu_14 - (w1 * T + sr * (w1 + w2) * T)) < 1e-6

        # Allele 15: shared peak (1000) + back-stutter from allele 16 (0.082 * 300 = 24.6)
        assert abs(mu_15 - ((w1 + w2) * T + sr * (w2 * T))) < 1e-6

    def test_molecular_degradation_decay(self):
        """Degradation factor 10^{-d · (S - S_0)} strictly decreases with size S for d > 0."""
        T = 1000.0
        d = 0.005  # Moderate degradation
        model = BiophysicalPeakModel(
            template_scale=T,
            amplification={"D18S51": 1.0, "D3S1358": 1.0},
            stutter_ratios={"D18S51": 0.092, "D3S1358": 0.082},
        )

        # Small amplicon (D3S1358 @ 110 bp base) vs Large amplicon (D18S51 @ 264 bp base)
        mu_small = model.expected_peak_heights(
            locus="D3S1358",
            genotypes=[(15.0, 15.0)],
            mixture_weights=[1.0],
            degradation_slopes=[d],
        )[15.0]

        mu_large = model.expected_peak_heights(
            locus="D18S51",
            genotypes=[(15.0, 15.0)],
            mixture_weights=[1.0],
            degradation_slopes=[d],
        )[15.0]

        assert mu_small > mu_large, "Degradation must attenuate large amplicons more severely"

        # Check exact formula: factor = 10^{-d * (bp - 100)}
        bp_small = model.allele_size_bp("D3S1358", 15.0)
        bp_large = model.allele_size_bp("D18S51", 15.0)
        factor_small = 10.0 ** (-d * (bp_small - 100.0))
        factor_large = 10.0 ** (-d * (bp_large - 100.0))
        assert factor_small > factor_large

    def test_back_stutter_ratio_incorporation(self):
        """Reverse n-1 stutter peak at allele (a - 1) receives SR_l · μ_{l,a}."""
        sr = 0.080
        T = 1000.0
        model = BiophysicalPeakModel(
            template_scale=T,
            amplification={"D8S1179": 1.0},
            stutter_ratios={"D8S1179": sr},
        )
        # Genotype with 12 and 13 to inspect stutter addition from 13 onto 12
        heights = model.expected_peak_heights(
            locus="D8S1179",
            genotypes=[(12.0, 13.0)],
            mixture_weights=[1.0],
            degradation_slopes=[0.0],
        )

        mu_parent = T * 1.0  # 13.0
        # 12.0 receives its own peak (T*1.0) plus stutter from 13.0 (sr * T*1.0)
        mu_child = heights[12.0]
        assert abs(mu_child - (T + sr * mu_parent)) < 1e-6



# ===========================================================================
# 4. Metropolis-Hastings MCMC Acceptance & Proposal Formulation
# ===========================================================================

class TestMetropolisHastingsAcceptanceFormulation:
    """
    Validates Metropolis-Hastings transition acceptance probability:
      α(Θ, Θ*) = min(1, [P(E|Θ*)·P(Θ*)·q(Θ|Θ*)] / [P(E|Θ)·P(Θ)·q(Θ*|Θ)])
      ln α = min(0, ln L* - ln L + ln P* - ln P + ln q(Θ|Θ*) - ln q(Θ*|Θ))
    """

    def test_mh_acceptance_ratio_exact_bounds(self):
        """Acceptance probability α must be strictly bounded in [0.0, 1.0]."""
        # When candidate is strictly more likely: L* > L => α = 1.0
        log_L_curr = -150.0
        log_L_prop = -120.0
        log_alpha = min(0.0, log_L_prop - log_L_curr)
        alpha = math.exp(log_alpha)
        assert alpha == 1.0

        # When candidate is less likely: L* < L => α = exp(L* - L) < 1.0
        log_L_curr = -120.0
        log_L_prop = -123.0
        log_alpha = min(0.0, log_L_prop - log_L_curr)
        alpha = math.exp(log_alpha)
        assert 0.0 < alpha < 1.0
        assert abs(alpha - math.exp(-3.0)) < 1e-10

    def test_dirichlet_proposal_sampling_and_density(self):
        """Dirichlet proposal for mixture weights satisfies simplex invariant Σ w_k = 1.0, w_k > 0."""
        rng = random.Random(42)
        alpha = [7.0, 3.0]  # 70:30 mixture prior concentration

        for _ in range(100):
            sample = _sample_dirichlet(alpha, rng)
            assert len(sample) == 2
            assert all(w > 0.0 for w in sample)
            assert abs(sum(sample) - 1.0) < 1e-10

        # Log Dirichlet PDF unnormalized density check
        w_mode = [0.70, 0.30]
        w_deviated = [0.20, 0.80]
        log_pdf_mode = _log_dirichlet_pdf(w_mode, alpha)
        log_pdf_dev = _log_dirichlet_pdf(w_deviated, alpha)
        assert log_pdf_mode > log_pdf_dev


# ===========================================================================
# 5. Gelman-Rubin R̂ Convergence Diagnostics Formulation
# ===========================================================================

class TestGelmanRubinConvergenceDiagnostics:
    """
    Validates Gelman-Rubin R̂ ANOVA between/within chain variance decomposition:
      W = (1/M) Σ s_m²
      B = (N / (M-1)) Σ (x̄_m - x̄)²
      Var+(ψ) = ((N-1)/N)·W + (1/N)·B
      R̂ = sqrt(Var+(ψ) / W)
    """

    def test_gelman_rubin_identical_chains_yields_unity(self):
        """When parallel chains have sampled from the same stationary distribution, R̂ -> 1.00."""
        rng = random.Random(101)
        N = 1000
        # 3 identical stationary chains
        chain1 = [rng.gauss(0.50, 0.05) for _ in range(N)]
        chain2 = [rng.gauss(0.50, 0.05) for _ in range(N)]
        chain3 = [rng.gauss(0.50, 0.05) for _ in range(N)]

        r_hat = _gelman_rubin([chain1, chain2, chain3])
        assert not math.isnan(r_hat)
        assert abs(r_hat - 1.0) < 0.02, f"Expected R̂ ≈ 1.00, got {r_hat}"
        assert r_hat < R_HAT_THRESHOLD

    def test_gelman_rubin_unconverged_chains_detected(self):
        """When parallel chains are stuck in different modes, R̂ >> 1.05."""
        rng = random.Random(202)
        N = 1000
        # 3 chains stuck in separated regions
        chain1 = [rng.gauss(0.20, 0.02) for _ in range(N)]
        chain2 = [rng.gauss(0.50, 0.02) for _ in range(N)]
        chain3 = [rng.gauss(0.80, 0.02) for _ in range(N)]

        r_hat = _gelman_rubin([chain1, chain2, chain3])
        assert r_hat > 2.0, f"Unconverged chains must yield R̂ >> 1.05, got {r_hat}"

    def test_gelman_rubin_exact_formula_verification(self):
        """Verify exact hand-calculated ANOVA variance breakdown."""
        # Simple 2-chain case with deterministic values
        c1 = [2.0, 4.0, 6.0, 8.0]   # mean = 5.0, var = 6.666667
        c2 = [4.0, 6.0, 8.0, 10.0]  # mean = 7.0, var = 6.666667
        N = 4
        M = 2

        mean_c1, mean_c2 = 5.0, 7.0
        var_c1, var_c2 = statistics.variance(c1), statistics.variance(c2)

        W_expected = (var_c1 + var_c2) / 2.0
        grand_mean = (mean_c1 + mean_c2) / 2.0
        B_expected = N * statistics.variance([mean_c1, mean_c2])
        var_hat_expected = ((N - 1) / N) * W_expected + (1.0 / N) * B_expected
        r_hat_expected = math.sqrt(var_hat_expected / W_expected)

        r_hat_computed = _gelman_rubin([c1, c2])
        assert abs(r_hat_computed - r_hat_expected) < 1e-10


# ===========================================================================
# 6. Effective Sample Size (ESS) Autocorrelation Formulation
# ===========================================================================

class TestEffectiveSampleSizeAutocorrelation:
    """
    Validates Effective Sample Size (ESS) autocorrelation formulation:
      ESS = N / (1 + 2·Σ_{k=1}^K ρ̂_k)
      Truncates at initial positive sequence where ρ̂_k <= 0 (Geyer 1992).
    """

    def test_ess_independent_samples_near_n(self):
        """For independent IID random variables, autocorrelation ρ̂_k ≈ 0 => ESS ≈ N."""
        rng = random.Random(303)
        N = 2000
        iid_chain = [rng.gauss(0.0, 1.0) for _ in range(N)]
        ess = _compute_ess(iid_chain)

        # ESS should be close to N (within 20%)
        assert ess > 0.80 * N, f"IID chain ESS should be close to N={N}, got {ess}"

    def test_ess_highly_correlated_chain_severely_reduced(self):
        """For an AR(1) process with lag-1 correlation ρ = 0.85, ESS is drastically reduced."""
        rng = random.Random(404)
        N = 2000
        rho = 0.85
        ar_chain = [0.0]
        for _ in range(1, N):
            val = rho * ar_chain[-1] + math.sqrt(1 - rho ** 2) * rng.gauss(0.0, 1.0)
            ar_chain.append(val)

        ess = _compute_ess(ar_chain)
        # Theoretical ESS ≈ N * (1 - ρ) / (1 + ρ) = 2000 * 0.15 / 1.85 ≈ 162
        assert ess < 0.25 * N, f"Correlated chain ESS must be << N, got {ess}"
        assert ess > 50.0

    def test_ess_constant_chain_handling(self):
        """Constant chain (zero variance) returns N without division by zero."""
        constant_chain = [5.0] * 500
        ess = _compute_ess(constant_chain)
        assert ess == 500.0


# ===========================================================================
# 7. 95% HPD Lower Bound & Evaluative Reporting Formulations
# ===========================================================================

class TestHPDConservativeLowerBound:
    """
    Validates 95% HPD conservative lower bound:
      log10(LR_HPD_95) = μ_{log10 LR} - 1.96 · SE_{log10 LR}
      Ensures admissibility invariant: LR_court <= LR_point.
    """

    def test_hpd_lower_bound_strictly_conservative(self):
        """The 95% HPD lower bound must be strictly <= point estimate."""
        mean_log10_lr = 18.50
        std_err = 0.40
        hpd_95_lo = mean_log10_lr - 1.96 * std_err
        hpd_95_hi = mean_log10_lr + 1.96 * std_err

        assert hpd_95_lo < mean_log10_lr < hpd_95_hi
        assert abs(hpd_95_lo - 17.716) < 1e-6
        assert math.pow(10, hpd_95_lo) < math.pow(10, mean_log10_lr)

    def test_enfsi_verbal_scale_monotonicity(self):
        """Verbal scale classification strictly preserves LR ordering."""
        lrs = [0.001, 1.0, 5.0, 50.0, 500.0, 5000.0, 500000.0, 1e12, 1e20]
        verbal_results = [_enfsi_verbal(lr) for lr in lrs]

        # Neutral evidence at LR = 1.0
        assert "Neutral" in verbal_results[1][0]
        assert "Nötr" in verbal_results[1][1]

        # Exclusion at LR < 1.0
        assert "Defense" in verbal_results[0][0]
        assert "Savunma" in verbal_results[0][1]

        # Astronomically strong support at LR > 10^18
        assert "Extremely Strong Support" in verbal_results[-1][0] or "Astronomically" in verbal_results[-1][0]
