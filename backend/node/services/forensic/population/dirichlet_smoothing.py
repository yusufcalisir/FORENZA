"""
FORENZA Module 03 - Dirichlet Prior Bayesian Smoothing Engine.
Implements verbatim from pillar_1_probabilistic_genotyping_research.md Section 3.1:

  Dirichlet prior:  alpha_i = p0_i * kappa,  kappa = (1 - theta) / theta
  Posterior mean:   p_tilde_i = (n_i + alpha_i) / (N + kappa)

NRC II Recommendation 4.1 minimum frequency bound:
  p_min = max(5 / (2N), 0.001)  ~= 0.00241  (NIST 1036, N=1036 individuals)
"""

import math
from dataclasses import dataclass
from typing import Dict, Optional

# Exact constants from research specification
_NIST_1036_N: int = 1036
_P_MIN_NIST: float = 5.0 / (2 * _NIST_1036_N)   # = 0.002413...


@dataclass
class DirichletSmoothingResult:
    """Per-allele result of Bayesian Dirichlet posterior mean frequency computation."""
    allele: float
    observed_count: int
    raw_frequency: float
    prior_frequency: float
    posterior_frequency: float
    dirichlet_alpha: float          # alpha_i = p0_i * kappa
    was_p_min_applied: bool
    p_min_used: float
    theta_used: float


@dataclass
class DirichletSmoothingLocus:
    """Complete Dirichlet smoothing result for a single STR locus."""
    locus: str
    allele_posteriors: Dict[float, DirichletSmoothingResult]
    n_individuals: int
    theta: float
    concentration_parameter: float   # kappa = (1-theta)/theta
    sum_posterior: float             # invariant: must be close to 1.0


class DirichletSmoothingEngine:
    """
    Bayesian Dirichlet prior conjugate smoothing for STR allele frequency estimation.

    All formulas verbatim from pillar_1_probabilistic_genotyping_research.md Section 3.1:
      p ~ Dirichlet(alpha)
      alpha_i = p_i^0 * (1-theta)/theta
      p_tilde_i = E[p_i | n] = (n_i + alpha_i) / (N + kappa)

    NRC II Rec 4.1 floor is always applied:
      p_min = max(5/(2N), 0.001)
    """

    def __init__(self, default_n: int = _NIST_1036_N):
        self.default_n = default_n

    # ── Public API ────────────────────────────────────────────────────────────

    def get_nrc_ii_bound(self, n_individuals: Optional[int] = None) -> float:
        """
        NRC II Recommendation 4.1 minimum allele frequency bound.
        p_min = max(5 / (2*N), 0.001)
        For NIST 1036 (N=1036): p_min = 0.002413...
        """
        n = n_individuals if (n_individuals and n_individuals > 0) else self.default_n
        return max(5.0 / (2.0 * n), 0.001)

    def compute_kappa(self, theta: float) -> float:
        """
        Concentration parameter kappa = (1 - theta) / theta.
        Provides total Dirichlet pseudo-count mass.
        """
        if theta <= 0.0 or theta >= 1.0:
            raise ValueError(f"theta must be in (0, 1), got {theta}")
        return (1.0 - theta) / theta

    def compute_posterior_allele_frequency(
        self,
        observed_count: int,
        prior_frequency: float,
        N: int,
        theta: float,
        p_min: Optional[float] = None,
    ) -> float:
        """
        Single-allele posterior mean frequency (verbatim research formula §3.1):
          alpha_i = p0_i * kappa
          p_tilde_i = (n_i + alpha_i) / (N + kappa)

        Floored at NRC II Rec 4.1 p_min.
        """
        kappa = self.compute_kappa(theta)
        alpha_i = prior_frequency * kappa
        posterior = (observed_count + alpha_i) / (N + kappa)
        if p_min is None:
            p_min = self.get_nrc_ii_bound(N)
        return max(posterior, p_min)

    def compute_locus_posteriors(
        self,
        locus: str,
        observed_counts: Dict[float, int],
        prior_frequencies: Dict[float, float],
        theta: float = 0.03,
        n_individuals: Optional[int] = None,
    ) -> DirichletSmoothingLocus:
        """
        Full Dirichlet Bayesian smoothing for one STR locus.

        Args:
            locus: e.g. 'TH01'
            observed_counts: {allele_value: count_observed}
            prior_frequencies: {allele_value: p0_i} (reference database prior)
            theta: coancestry coefficient in [0.01, 0.05]
            n_individuals: database size N

        Returns:
            DirichletSmoothingLocus with per-allele posterior frequencies
            and mathematical invariant check (sum_posterior).
        """
        n = n_individuals if (n_individuals and n_individuals > 0) else self.default_n
        p_min = self.get_nrc_ii_bound(n)
        kappa = self.compute_kappa(theta)
        N_total = sum(observed_counts.values())

        all_alleles = sorted(
            set(observed_counts.keys()).union(set(prior_frequencies.keys()))
        )

        allele_posteriors: Dict[float, DirichletSmoothingResult] = {}
        sum_posterior = 0.0

        for allele in all_alleles:
            n_i = observed_counts.get(allele, 0)
            p0_i = prior_frequencies.get(allele, p_min)
            alpha_i = p0_i * kappa
            raw_freq = n_i / max(N_total, 1)

            # Verbatim posterior mean formula
            posterior_raw = (n_i + alpha_i) / (N_total + kappa)
            was_bounded = posterior_raw < p_min
            posterior_final = max(posterior_raw, p_min)
            sum_posterior += posterior_final

            allele_posteriors[allele] = DirichletSmoothingResult(
                allele=allele,
                observed_count=n_i,
                raw_frequency=round(raw_freq, 6),
                prior_frequency=round(p0_i, 6),
                posterior_frequency=round(posterior_final, 6),
                dirichlet_alpha=round(alpha_i, 6),
                was_p_min_applied=was_bounded,
                p_min_used=round(p_min, 6),
                theta_used=theta,
            )

        return DirichletSmoothingLocus(
            locus=locus,
            allele_posteriors=allele_posteriors,
            n_individuals=n,
            theta=theta,
            concentration_parameter=round(kappa, 4),
            sum_posterior=round(sum_posterior, 6),
        )

    def apply_laplace_smoothing(
        self,
        counts_map: Dict[float, int],
        alpha: float = 1.0,
        n_individuals: Optional[int] = None,
    ) -> Dict[float, float]:
        """
        Laplace add-alpha pseudo-count smoothing:
          p_i = (n_i + alpha) / (N_total + alpha * K)

        NRC II 4.1 p_min floor applied to all outputs.
        """
        p_min = self.get_nrc_ii_bound(n_individuals)
        total_counts = sum(counts_map.values())
        k = len(counts_map)
        if k == 0:
            return {}
        denom = total_counts + alpha * k
        return {
            allele: round(max(p_min, (count + alpha) / denom), 6)
            for allele, count in counts_map.items()
        }
