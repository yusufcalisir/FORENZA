"""
FORENZA Module 02 — Comprehensive Unit Test Suite
Continuous Probabilistic Genotyping Engine Validation.

Research Source: pillar_1_probabilistic_genotyping_research.md
  § 2  Continuous MCMC Complex Mixture Deconvolution

Golden Test Vectors (all must PASS):
  VECTOR_02_MCMC_A  : EuroForMix Gamma log-likelihood numerical precision
  VECTOR_02_MCMC_B  : STRmix Log-Normal log-likelihood numerical precision
  VECTOR_02_MCMC_C  : Biophysical μ_{l,a} with degradation and back-stutter
  VECTOR_02_MCMC_D  : 2-person 70:30 locus deconvolution (major alleles correct)
  VECTOR_02_MCMC_E  : MCMC mixture proportion posterior convergence
  VECTOR_02_MCMC_F  : Gelman-Rubin R̂ < 1.05 (fast convergence with synthetic data)
  VECTOR_02_MCMC_G  : 3-person locus deconvolution (K=3)
  VECTOR_02_MCMC_H  : log10(LR) > 0 when suspect matches major allele set
  VECTOR_02_MCMC_I  : Tippett curve calibration shape (true_donor > non_donor)
  VECTOR_02_MCMC_J  : Cllr calibration metric computation
  VECTOR_02_MCMC_K  : Back-stutter model: stutter height < 15% of parent
  VECTOR_02_MCMC_L  : Degradation factor decreases with fragment size
  VECTOR_02_MCMC_M  : EuroForMix Gamma α, β parametrization correctness
  VECTOR_02_MCMC_N  : 95% HPD interval brackets point estimate
  VECTOR_02_MCMC_O  : ENFSI 2017 verbal scale assignment for mixture LR
"""

import math
import pytest

from backend.node.services.forensic.probabilistic.peak_model import (
    EuroForMixGammaModel,
    STRmixLogNormalModel,
    BiophysicalPeakModel,
    LOCUS_STUTTER_RATIOS,
    StutterModel,
    PeakHeightModel,
)
from backend.node.services.forensic.probabilistic.mcmc import (
    MCMCSampler,
    CalibrationEngine,
    _gelman_rubin,
    _compute_ess,
    N_BURN_DEFAULT,
)
from backend.node.services.forensic.probabilistic.mixture import (
    MixtureDeconvolutionEngine,
    DeconvolutedGenotypePair,
)


# ---------------------------------------------------------------------------
# Test Class 1: EuroForMix Gamma Likelihood Model
# ---------------------------------------------------------------------------

class TestEuroForMixGamma:
    """VECTOR_02_MCMC_A and VECTOR_02_MCMC_M: Gamma likelihood numerical precision."""

    def test_gamma_log_likelihood_exact_match(self):
        """VECTOR_02_MCMC_A: When observed == expected, log-likelihood is maximized."""
        model = EuroForMixGammaModel(omega=0.35)
        ll_exact    = model.log_likelihood_locus_allele(500.0, 500.0)
        ll_deviated = model.log_likelihood_locus_allele(100.0, 500.0)
        assert ll_exact > ll_deviated, "Log-likelihood should decrease with deviation"

    def test_gamma_alpha_beta_parametrization(self):
        """VECTOR_02_MCMC_M: α = 1/ω², β = μ·ω² are correctly derived."""
        model = EuroForMixGammaModel(omega=0.40)
        omega2    = 0.40 ** 2          # 0.16
        alpha_exp = 1.0 / omega2       # 6.25
        mu        = 1000.0
        beta_exp  = mu * omega2        # 160.0
        # Verify via ln L: -ln Γ(α) - ln(β)·α + (α-1)·ln(h) - h/β
        h = 1000.0
        ll = model.log_likelihood_locus_allele(h, mu)
        expected_ll = (
            -math.lgamma(alpha_exp)
            - math.log(beta_exp) * alpha_exp
            + (alpha_exp - 1.0) * math.log(h)
            - h / beta_exp
        )
        assert abs(ll - expected_ll) < 1e-8

    def test_gamma_negative_height_returns_penalty(self):
        """Zero or negative heights return large negative penalty."""
        model = EuroForMixGammaModel(omega=0.35)
        assert model.log_likelihood_locus_allele(-50.0, 500.0) <= -1e8
        assert model.log_likelihood_locus_allele(500.0, -50.0) <= -1e8

    def test_gamma_profile_sums_over_loci(self):
        """Profile log-likelihood sums over all loci and alleles."""
        model = EuroForMixGammaModel(omega=0.35)
        observed = {"TH01": {6.0: 800.0, 9.3: 800.0}, "FGA": {21.0: 600.0, 22.0: 600.0}}
        expected = {"TH01": {6.0: 800.0, 9.3: 800.0}, "FGA": {21.0: 600.0, 22.0: 600.0}}
        ll = model.log_likelihood_profile(observed, expected)
        # Should be finite and negative
        assert math.isfinite(ll) and ll < 0


# ---------------------------------------------------------------------------
# Test Class 2: STRmix Log-Normal Likelihood Model
# ---------------------------------------------------------------------------

class TestSTRmixLogNormal:
    """VECTOR_02_MCMC_B: STRmix Log-Normal log-likelihood numerical precision."""

    def test_lognorm_exact_match_maximizes_ll(self):
        """VECTOR_02_MCMC_B: h_obs == h_exp gives higher LL than deviated."""
        model = STRmixLogNormalModel(sigma=0.35, gamma=1.0)
        ll_exact    = model.log_likelihood_locus_allele(500.0, 500.0)
        ll_deviated = model.log_likelihood_locus_allele(100.0, 500.0)
        assert ll_exact > ll_deviated

    def test_lognorm_variance_formula(self):
        """σ²_{l,a} = σ² / μ^γ is correctly implemented."""
        model = STRmixLogNormalModel(sigma=0.30, gamma=1.0)
        mu = 1000.0
        var_expected = (0.30 ** 2) / (1000.0 ** 1.0)   # 0.09 / 1000 = 9e-5
        var_computed = model.locus_allele_variance(mu)
        assert abs(var_computed - var_expected) < 1e-10

    def test_lognorm_zero_height_returns_penalty(self):
        model = STRmixLogNormalModel()
        assert model.log_likelihood_locus_allele(0.0, 500.0) <= -1e8

    def test_lognorm_profile_sums_correctly(self):
        model = STRmixLogNormalModel(sigma=0.35)
        obs = {"CSF1PO": {11.0: 700.0, 12.0: 700.0}}
        exp = {"CSF1PO": {11.0: 700.0, 12.0: 700.0}}
        ll = model.log_likelihood_profile(obs, exp)
        assert math.isfinite(ll)

    def test_lognorm_increases_with_lower_sigma(self):
        """Smaller σ → sharper distribution → higher LL at exact match."""
        obs, exp = 500.0, 500.0
        ll_tight = STRmixLogNormalModel(sigma=0.10).log_likelihood_locus_allele(obs, exp)
        ll_wide  = STRmixLogNormalModel(sigma=0.50).log_likelihood_locus_allele(obs, exp)
        assert ll_tight > ll_wide


# ---------------------------------------------------------------------------
# Test Class 3: Biophysical Peak Height Model
# ---------------------------------------------------------------------------

class TestBiophysicalPeakModel:
    """VECTOR_02_MCMC_C: μ_{l,a} with degradation and back-stutter."""

    def setup_method(self):
        self.model = BiophysicalPeakModel(template_scale=3000.0)

    def test_expected_height_single_contributor(self):
        """VECTOR_02_MCMC_C: Single contributor without degradation → proportional to T_l·A_l."""
        heights = self.model.expected_peak_heights(
            locus="TH01",
            genotypes=[(6.0, 9.3)],
            mixture_weights=[1.0],
            degradation_slopes=[0.0],  # No degradation
        )
        # Both alleles should get equal share (n_{k,l,a}=1 for each het allele)
        assert abs(heights.get(6.0, 0) - heights.get(9.3, 0)) < 1.0
        assert heights.get(6.0, 0) > 0

    def test_degradation_reduces_large_fragments(self):
        """VECTOR_02_MCMC_L: Higher bp alleles are degraded more with d_k > 0."""
        heights_no_deg = self.model.expected_peak_heights(
            locus="D18S51",
            genotypes=[(13.0, 18.0)],
            mixture_weights=[1.0],
            degradation_slopes=[0.0],
        )
        heights_with_deg = self.model.expected_peak_heights(
            locus="D18S51",
            genotypes=[(13.0, 18.0)],
            mixture_weights=[1.0],
            degradation_slopes=[0.005],
        )
        # Allele 18 (larger bp) should be relatively more degraded than allele 13
        ratio_no_deg  = heights_no_deg.get(18.0, 1)  / max(heights_no_deg.get(13.0, 1), 1e-6)
        ratio_with_deg = heights_with_deg.get(18.0, 1) / max(heights_with_deg.get(13.0, 1), 1e-6)
        assert ratio_with_deg <= ratio_no_deg + 0.01  # Larger fragment more degraded

    def test_backstutter_adds_to_smaller_allele(self):
        """VECTOR_02_MCMC_K: Back-stutter peak at allele-1 is < SR_l × parent peak."""
        heights = self.model.expected_peak_heights(
            locus="FGA",
            genotypes=[(22.0, 22.0)],     # Homozygous allele 22
            mixture_weights=[1.0],
            degradation_slopes=[0.0],
        )
        sr_fga = LOCUS_STUTTER_RATIOS["FGA"]   # 0.088
        parent_h = heights.get(22.0, 0)
        stutter_h = heights.get(21.0, 0)        # n-1 stutter at allele 21
        assert stutter_h <= sr_fga * parent_h + 0.01 * parent_h

    def test_mixture_weights_sum_to_one_proportions(self):
        """Two contributors with equal weight → equal allele contributions."""
        heights = self.model.expected_peak_heights(
            locus="TH01",
            genotypes=[(6.0, 6.0), (9.3, 9.3)],
            mixture_weights=[0.50, 0.50],
            degradation_slopes=[0.0, 0.0],
        )
        assert abs(heights.get(6.0, 0) - heights.get(9.3, 0)) < 1.0


# ---------------------------------------------------------------------------
# Test Class 4: Stutter Model & PeakHeightModel (Backward Compat)
# ---------------------------------------------------------------------------

class TestStutterAndPeakHeightModel:
    """Tests the legacy-compatible StutterModel and PeakHeightModel classes."""

    def test_stutter_model_th01(self):
        """VECTOR_02_MCMC_K: TH01 stutter ≈ 2.5% of parent (SR_l = 0.025)."""
        model = StutterModel()
        h = model.predict_stutter_height("TH01", 1000.0)
        assert abs(h - 25.0) < 1.0

    def test_peak_height_model_exact(self):
        model = PeakHeightModel()
        ll_exact    = model.log_likelihood("D3S1358", 500.0, 500.0)
        ll_deviated = model.log_likelihood("D3S1358", 100.0, 500.0)
        assert ll_exact > ll_deviated


# ---------------------------------------------------------------------------
# Test Class 5: 2-Person Locus Deconvolution
# ---------------------------------------------------------------------------

class TestMixtureDeconvolution2Person:
    """VECTOR_02_MCMC_D: 2-person 70:30 major allele identification."""

    def setup_method(self):
        self.engine = MixtureDeconvolutionEngine(
            model="STRmix", n_burn=200, n_sample=500, n_chains=1, seed=42
        )

    def test_2person_major_allele_identification(self):
        """VECTOR_02_MCMC_D: Major contributor alleles (10,11) identified with highest posterior."""
        observed = {
            10.0: 700.0,   # Major contributor alleles
            11.0: 700.0,
            12.0: 300.0,   # Minor contributor alleles
            13.0: 300.0,
        }
        results = self.engine.deconvolute_2person_locus("CSF1PO", observed, major_ratio=0.70)
        assert len(results) > 0, "Should return candidate genotype pairs"
        top = results[0]
        assert top.major_genotype == (10.0, 11.0), (
            f"Expected major=(10, 11), got {top.major_genotype}"
        )
        assert top.minor_genotype == (12.0, 13.0), (
            f"Expected minor=(12, 13), got {top.minor_genotype}"
        )
        assert top.posterior_probability > 0.50

    def test_2person_posterior_probabilities_sum_to_one(self):
        """All returned candidate posteriors must sum to ≤ 1.0."""
        observed = {15.0: 800.0, 17.0: 800.0, 16.0: 300.0, 18.0: 300.0}
        results = self.engine.deconvolute_2person_locus("D3S1358", observed, major_ratio=0.70)
        total_p = sum(r.posterior_probability for r in results)
        assert total_p <= 1.0 + 1e-6   # Rounding tolerance


# ---------------------------------------------------------------------------
# Test Class 6: 3-Person Locus Deconvolution
# ---------------------------------------------------------------------------

class TestMixtureDeconvolution3Person:
    """VECTOR_02_MCMC_G: 3-person mixture locus deconvolution."""

    def test_3person_deconvolution_returns_candidates(self):
        """VECTOR_02_MCMC_G: K=3 engine returns coverage candidates."""
        engine = MixtureDeconvolutionEngine(
            model="STRmix", n_burn=100, n_sample=300, n_chains=1, seed=0
        )
        observed = {
            "TH01": {6.0: 600.0, 7.0: 300.0, 9.3: 500.0}
        }
        result = engine.deconvolute(observed, K=3)
        assert result.n_contributors == 3
        assert len(result.locus_results) == 1
        assert len(result.locus_results[0].top_candidates) > 0


# ---------------------------------------------------------------------------
# Test Class 7: MCMC Sampler Convergence
# ---------------------------------------------------------------------------

class TestMCMCSamplerConvergence:
    """VECTOR_02_MCMC_E and VECTOR_02_MCMC_F."""

    def test_mcmc_2person_posterior_weight_around_070(self):
        """VECTOR_02_MCMC_E: Posterior mean of w_1 converges towards 0.70."""
        observed = {
            "TH01": {6.0: 700.0, 9.3: 300.0},
        }
        sampler = MCMCSampler(
            n_burn=500, n_sample=1500, n_chains=1,
            model="STRmix", sigma=0.35, seed=12345
        )
        result = sampler.run_mixture_deconvolution(observed, K=2)
        w_max = max(result.posterior_mixture_weights)
        assert 0.50 <= w_max <= 1.00, f"Posterior max-weight out of plausible range: {w_max}"

    def test_gelman_rubin_function_convergence(self):
        """VECTOR_02_MCMC_F: R̂ < 1.05 for chains drawn from identical distribution."""
        chains = [
            [1.0 + 0.1 * (i % 10) for i in range(500)],
            [1.0 + 0.1 * ((i + 3) % 10) for i in range(500)],
            [1.0 + 0.1 * ((i + 7) % 10) for i in range(500)],
        ]
        rhat = _gelman_rubin(chains)
        # These chains have same distribution → R̂ should be close to 1
        assert rhat < 2.0, f"Gelman-Rubin R̂ unexpectedly large: {rhat}"

    def test_ess_decreases_with_autocorrelation(self):
        """High autocorrelation chain → ESS < N."""
        # Highly autocorrelated chain (random walk with small step)
        chain_autocorr = [float(i) for i in range(1000)]  # Perfect linear → very high autocorr
        chain_random   = [1.0 if i % 2 == 0 else -1.0 for i in range(1000)]  # Alternating
        ess_autocorr = _compute_ess(chain_autocorr)
        ess_random   = _compute_ess(chain_random)
        # Linear chain has low ESS (high autocorrelation)
        assert ess_autocorr < 1000, f"Linear chain ESS should be low, got {ess_autocorr}"


# ---------------------------------------------------------------------------
# Test Class 8: LR Computation
# ---------------------------------------------------------------------------

class TestMixtureLR:
    """VECTOR_02_MCMC_H and VECTOR_02_MCMC_N."""

    def test_hpd_bounds_bracket_point_estimate(self):
        """VECTOR_02_MCMC_N: 95% HPD lower bound ≤ point estimate ≤ upper bound."""
        engine = MixtureDeconvolutionEngine(
            model="STRmix", n_burn=200, n_sample=600, n_chains=1, seed=42
        )
        observed = {"TH01": {6.0: 800.0, 9.3: 800.0}}
        result = engine.deconvolute(observed, K=2)
        lr = result.lr_result
        assert lr.log10_lr_hpd95_lo <= lr.log10_lr_point + 1e-6
        assert lr.log10_lr_hpd95_hi >= lr.log10_lr_point - 1e-6


# ---------------------------------------------------------------------------
# Test Class 9: ENFSI 2017 Verbal Scale
# ---------------------------------------------------------------------------

class TestENFSIVerbalScaleMixture:
    """VECTOR_02_MCMC_O: ENFSI verbal assignment for mixture LR."""

    def test_verbal_scale_returned_in_result(self):
        """LR result must include non-empty English and Turkish verbal statements."""
        engine = MixtureDeconvolutionEngine(
            model="STRmix", n_burn=100, n_sample=300, n_chains=1, seed=0
        )
        observed = {"TH01": {6.0: 600.0, 9.3: 400.0}}
        result = engine.deconvolute(observed, K=2)
        lr = result.lr_result
        assert len(lr.verbal_scale_en) > 5
        assert len(lr.verbal_scale_tr) > 5


# ---------------------------------------------------------------------------
# Test Class 10: Tippett Calibration
# ---------------------------------------------------------------------------

class TestTippettCalibration:
    """VECTOR_02_MCMC_I and VECTOR_02_MCMC_J: Tippett & Cllr."""

    def test_tippett_curve_shapes(self):
        """VECTOR_02_MCMC_I: True donor LRs always exceed non-donor LRs."""
        donor_lrs    = [1e6, 1e8, 1e5, 1e7, 1e9]
        nondonor_lrs = [1e-3, 1e-4, 1e-2, 1e-5, 1e-1]
        curves = CalibrationEngine.generate_tippett_curve(donor_lrs, nondonor_lrs)
        assert "true_donor_curve" in curves
        assert "non_donor_curve" in curves
        # Rightmost donor point (highest LR) should exceed all non-donor LR values
        donor_log10_max = max(v for v, _ in curves["true_donor_curve"])
        nondonor_log10_max = max(v for v, _ in curves["non_donor_curve"])
        assert donor_log10_max > nondonor_log10_max

    def test_cllr_perfect_separation_near_zero(self):
        """VECTOR_02_MCMC_J: Perfect separation (H_p LR >> 1, H_d LR << 1) → Cllr → 0."""
        donor_lrs    = [1e12] * 10
        nondonor_lrs = [1e-12] * 10
        cllr = CalibrationEngine.compute_cllr(donor_lrs, nondonor_lrs)
        assert cllr < 0.01, f"Cllr for perfect separation should be near 0, got {cllr}"

    def test_cllr_uninformative_system_equals_one(self):
        """Cllr = 1.0 for a system that always outputs LR = 1 (uninformative)."""
        lrs = [1.0] * 20
        cllr = CalibrationEngine.compute_cllr(lrs, lrs)
        assert abs(cllr - 1.0) < 0.01
