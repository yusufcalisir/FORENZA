"""
Unit Test Suite for Continuous Probabilistic Genotyping Engine (Phase 2 Validation).
Tests dropout/drop-in stochastic models, peak height log-likelihoods,
2-person mixture deconvolution, and MCMC Tippett calibration.
"""

import pytest
from backend.node.services.forensic.probabilistic.stochastic import StochasticModel, DropoutModel, DropInModel
from backend.node.services.forensic.probabilistic.peak_model import PeakHeightModel, StutterModel
from backend.node.services.forensic.probabilistic.mixture import MixtureDeconvolutionEngine
from backend.node.services.forensic.probabilistic.mcmc import MCMCSampler, CalibrationEngine


def test_dropout_model():
    # P(D|x) = 1/(1+exp(beta0 + beta1*x))
    # beta0=-3.5, beta1=0.015: high RFU → exponent > 0 → P(D) → 0
    model = DropoutModel(beta0=-3.5, beta1=0.015)
    high_rfu_dropout = model.calculate_dropout_probability(500.0)
    low_rfu_dropout = model.calculate_dropout_probability(30.0)

    assert high_rfu_dropout < 0.05  # Low dropout for high peak height
    assert low_rfu_dropout > 0.90   # High dropout for trace peak height


def test_dropin_model():
    model = DropInModel(lambda_c=0.05, analytical_threshold=50.0)
    p_zero = model.count_probability(0)
    p_one = model.count_probability(1)

    assert p_zero > p_one  # Zero drop-in is more probable than 1 event
    assert model.height_density(100.0) > 0.0


def test_stutter_and_peak_height_model():
    stutter = StutterModel()
    pred_h = stutter.predict_stutter_height("TH01", 1000.0)
    assert 20.0 <= pred_h <= 30.0  # TH01 ~2.5% stutter

    peak_model = PeakHeightModel()
    ll_exact = peak_model.log_likelihood("TH01", 500.0, 500.0)
    ll_deviated = peak_model.log_likelihood("TH01", 100.0, 500.0)
    assert ll_exact > ll_deviated  # Log-likelihood drops with deviation


def test_mixture_deconvolution_2person():
    engine = MixtureDeconvolutionEngine()
    observed_alleles = {10.0: 700.0, 11.0: 700.0, 12.0: 300.0, 13.0: 300.0}

    results = engine.deconvolute_2person_locus("CSF1PO", observed_alleles, major_ratio=0.70)
    assert len(results) > 0
    top_candidate = results[0]

    # Major contributor should get higher RFU alleles (10, 11)
    assert top_candidate.major_genotype == (10.0, 11.0)
    assert top_candidate.minor_genotype == (12.0, 13.0)
    assert top_candidate.posterior_probability > 0.50


def test_mcmc_sampler_and_tippett_calibration():
    sampler = MCMCSampler(n_iterations=200, burn_in=50)
    samples = sampler.sample_mixture_ratio(initial_ratio=0.50)

    assert len(samples) == 150
    avg_ratio = sum(s.major_ratio for s in samples) / len(samples)
    assert 0.60 <= avg_ratio <= 0.80  # Converges toward target ~0.70

    donor_lrs = [1e6, 1e8, 1e5, 1e7]
    nondonor_lrs = [1e-3, 1e-4, 1e-2, 1e-5]
    tippett = CalibrationEngine.generate_tippett_curve(donor_lrs, nondonor_lrs)

    assert len(tippett["true_donor_curve"]) == 4
    assert len(tippett["non_donor_curve"]) == 4
