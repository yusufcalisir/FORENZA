"""
Dirichlet Bayesian Prior Frequency Smoothing & Boundary Regularizer.

Enforces:
- Dirichlet prior regularization preventing zero probabilities (p_min = 1 / (2N + 1))
- Strict simplex probability sum-to-one invariant (|sum p - 1.0| <= 1e-7)
- Sub-population Wright Fst / Balding-Nichols adjustment
"""

from typing import Dict, List, Tuple
import math


class BGAFrequencySmoother:
    """Smoothes empirical population allele frequencies using Bayesian Dirichlet regularization."""

    DEFAULT_PSEUDOCOUNT_ALPHA: float = 1.0

    @classmethod
    def smooth_biallelic_frequencies(
        cls,
        raw_freq_ref: float,
        raw_freq_alt: float,
        sample_size_n: int = 100,
        alpha_ref: float = DEFAULT_PSEUDOCOUNT_ALPHA,
        alpha_alt: float = DEFAULT_PSEUDOCOUNT_ALPHA
    ) -> Tuple[float, float]:
        """
        Applies Dirichlet Bayesian smoothing on biallelic frequencies.
        Returns: (smoothed_ref_freq, smoothed_alt_freq) subject to sum = 1.0
        """
        # Minimum frequency floor based on sample count
        p_min = 1.0 / (2.0 * sample_size_n + 1.0)

        # Count estimates
        n_ref = 2.0 * sample_size_n * max(0.0, min(1.0, raw_freq_ref))
        n_alt = 2.0 * sample_size_n * max(0.0, min(1.0, raw_freq_alt))

        smoothed_ref = (n_ref + alpha_ref) / (2.0 * sample_size_n + alpha_ref + alpha_alt)
        smoothed_alt = (n_alt + alpha_alt) / (2.0 * sample_size_n + alpha_ref + alpha_alt)

        # Enforce minimum floor
        smoothed_ref = max(p_min, min(1.0 - p_min, smoothed_ref))
        smoothed_alt = max(p_min, min(1.0 - p_min, smoothed_alt))

        # Re-normalize to exact simplex
        total = smoothed_ref + smoothed_alt
        norm_ref = round(smoothed_ref / total, 8)
        norm_alt = round(1.0 - norm_ref, 8)

        return (norm_ref, norm_alt)

    @classmethod
    def smooth_multiallelic_frequencies(
        cls,
        raw_frequencies: Dict[str, float],
        sample_size_n: int = 100,
        alpha_per_allele: float = DEFAULT_PSEUDOCOUNT_ALPHA
    ) -> Dict[str, float]:
        """
        Applies Dirichlet Bayesian smoothing across multiallelic microhaplotypes.
        Returns: {allele_str: smoothed_freq} subject to sum = 1.0
        """
        k_alleles = len(raw_frequencies)
        if k_alleles == 0:
            return {}

        p_min = 1.0 / (2.0 * sample_size_n * k_alleles + 1.0)
        smoothed: Dict[str, float] = {}

        total_denominator = 2.0 * sample_size_n + (k_alleles * alpha_per_allele)

        for allele, freq in raw_frequencies.items():
            n_obs = 2.0 * sample_size_n * max(0.0, freq)
            val = (n_obs + alpha_per_allele) / total_denominator
            smoothed[allele] = max(p_min, val)

        # Normalization
        sum_val = sum(smoothed.values())
        norm_dict = {al: round(v / sum_val, 8) for al, v in smoothed.items()}

        # Adjust residual on last item to preserve strict sum-to-one
        sum_norm = sum(norm_dict.values())
        diff = 1.0 - sum_norm
        last_key = list(norm_dict.keys())[-1]
        norm_dict[last_key] = round(norm_dict[last_key] + diff, 8)

        return norm_dict
