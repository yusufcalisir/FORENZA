"""
Unit Tests for Dirichlet Bayesian Frequency Smoothing.
"""

import pytest
from backend.node.services.forensic.genomics.bga.frequency_smoother import BGAFrequencySmoother


def test_biallelic_smoothing_zeros():
    """Verify zero frequency is regularized to non-zero floor while sum=1.0."""
    smooth_ref, smooth_alt = BGAFrequencySmoother.smooth_biallelic_frequencies(
        raw_freq_ref=1.0,
        raw_freq_alt=0.0,
        sample_size_n=100
    )
    assert smooth_alt > 0.0
    assert smooth_ref < 1.0
    assert abs((smooth_ref + smooth_alt) - 1.0) < 1e-7


def test_biallelic_smoothing_exact_simplex():
    """Verify sum-to-one invariant holds across variable sample sizes."""
    for n in [10, 50, 500, 2500]:
        s_ref, s_alt = BGAFrequencySmoother.smooth_biallelic_frequencies(0.72, 0.28, sample_size_n=n)
        assert abs((s_ref + s_alt) - 1.0) < 1e-7
        assert s_ref > s_alt


def test_multiallelic_microhaplotype_smoothing():
    """Verify Dirichlet smoothing for multiallelic microhaplotype frequencies."""
    raw_haps = {"AAC": 0.90, "AGT": 0.10, "GAC": 0.0, "GGT": 0.0}
    smoothed = BGAFrequencySmoother.smooth_multiallelic_frequencies(raw_haps, sample_size_n=100)

    assert len(smoothed) == 4
    for al, f in smoothed.items():
        assert f > 0.0

    total = sum(smoothed.values())
    assert abs(total - 1.0) < 1e-7
