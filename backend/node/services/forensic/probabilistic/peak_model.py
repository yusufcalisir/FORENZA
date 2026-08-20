"""
FORENZA Module 02 — Biophysical Peak Height & Continuous Likelihood Models
Implements both EuroForMix (Gamma) and STRmix (Log-Normal) likelihood functions,
the multi-contributor expected peak height formula with molecular size degradation,
and 24-locus back-stutter ratios.

Research Source: pillar_1_probabilistic_genotyping_research.md
  § 2.1  EuroForMix Gamma Likelihood
  § 2.2  STRmix Log-Normal Likelihood
  § 2.3  Biophysical Expected Peak Height μ_{l,a}
  § 2.4  Locus-Specific Back-Stutter Ratio SR_l

Mathematical Model (EuroForMix Gamma):
  h_{l,a} ~ Gamma(α = 1/ω², β = μ_{l,a}·ω²)
  ln L_Gamma = Σ_l Σ_a [-ln Γ(ω⁻²) − ln(μ_{l,a}ω²)/ω²
                         + (1/ω² − 1)·ln(h_{l,a}) − h_{l,a}/(μ_{l,a}ω²)]

Mathematical Model (STRmix Log-Normal):
  ln(h_{l,a}) ~ N(ln μ_{l,a}, σ²/μ_{l,a}^γ)  (γ ≈ 1.0)
  ln L_LogNorm = Σ_l Σ_a [-½ ln(2π σ_{l,a}²)
                            − (ln h_{l,a} − ln μ_{l,a})²/(2σ_{l,a}²)]

Biophysical Expected Peak Height:
  μ_{l,a} = T_l · A_l · Σ_k w_k · 10^{−d_k(S_{l,a}−S_0)} · n_{k,l,a} + Stutter_{l,a}
  Stutter_{l,a} = SR_l · μ_{l, a+1}   (n−1 back-stutter)
  S_0 = 100 bp molecular size reference
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# 24-Locus Back-Stutter Ratios (SR_l) — Derived from Forensic Literature
# SWGDAM (2020) locus-specific n-1 stutter slope reference table.
# ---------------------------------------------------------------------------
LOCUS_STUTTER_RATIOS: Dict[str, float] = {
    "D3S1358":  0.082,
    "VWA":      0.078,
    "D16S539":  0.079,
    "CSF1PO":   0.065,
    "TPOX":     0.042,
    "D8S1179":  0.074,
    "D21S11":   0.085,
    "D18S51":   0.092,
    "D2S441":   0.058,
    "D19S433":  0.076,
    "TH01":     0.025,
    "FGA":      0.088,
    "D22S1045": 0.058,
    "D5S818":   0.068,
    "D13S317":  0.061,
    "D7S820":   0.062,
    "SE33":     0.110,
    "D10S1248": 0.071,
    "D1S1656":  0.095,
    "D12S391":  0.112,
    "D2S1338":  0.089,
    "D6S1043":  0.072,  # ESS additional loci
    "PENTA_E":  0.040,
    "PENTA_D":  0.038,
    "AMEL":     0.000,  # Sex marker — no stutter
}

# Molecular size basepairs for allele-based degradation (S_{l,a})
# For each locus: base bp for the smallest allele in common range
LOCUS_BASE_BP: Dict[str, float] = {
    "D3S1358":  110.0, "VWA":      156.0, "D16S539":  228.0, "CSF1PO":   294.0,
    "TPOX":     224.0, "D8S1179":  128.0, "D21S11":   196.0, "D18S51":   264.0,
    "D2S441":   108.0, "D19S433":  108.0, "TH01":     166.0, "FGA":      212.0,
    "D22S1045": 100.0, "D5S818":   154.0, "D13S317":  196.0, "D7S820":   258.0,
    "SE33":     312.0, "D10S1248": 130.0, "D1S1656":  158.0, "D12S391":  237.0,
    "D2S1338":  288.0, "D6S1043":  183.0, "PENTA_E":  380.0, "PENTA_D":  340.0,
    "AMEL":     104.0,
}

# Locus amplification efficiency — relative (normalized to 1.0)
DEFAULT_AMPLIFICATION: Dict[str, float] = {locus: 1.0 for locus in LOCUS_STUTTER_RATIOS}

# Molecular size offset reference (100 bp)
S0_BP: float = 100.0


# ---------------------------------------------------------------------------
# EuroForMix (Gamma) Likelihood Model
# ---------------------------------------------------------------------------

class EuroForMixGammaModel:
    """
    EuroForMix Continuous Gamma Peak Height Likelihood Model.

    h_{l,a} ~ Gamma(α = 1/ω², β = μ_{l,a}·ω²)
    ln L = Σ [-ln Γ(ω⁻²) - ln(μω²)/ω² + (1/ω²-1)·ln(h) - h/(μω²)]
    """

    def __init__(self, omega: float = 0.35):
        """
        Args:
            omega: variance/scale coefficient (CV). Typical 0.20–0.40.
        """
        if omega <= 0:
            raise ValueError(f"omega must be positive, got {omega}")
        self.omega = omega

    def log_likelihood_locus_allele(
        self,
        observed_height: float,
        expected_height: float,
    ) -> float:
        """
        Log-likelihood of a single allele peak height under EuroForMix Gamma.

        ln L = -ln Γ(ω⁻²) - ln(μ·ω²)/ω² + (1/ω²-1)·ln(h) - h/(μ·ω²)
        """
        if observed_height <= 0.0 or expected_height <= 0.0:
            return -1e9

        omega2 = self.omega ** 2
        inv_omega2 = 1.0 / omega2
        beta = expected_height * omega2  # β = μ·ω²

        term1 = -math.lgamma(inv_omega2)
        term2 = -math.log(beta) * inv_omega2
        term3 = (inv_omega2 - 1.0) * math.log(observed_height)
        term4 = -observed_height / beta
        return term1 + term2 + term3 + term4

    def log_likelihood_profile(
        self,
        observed: Dict[str, Dict[float, float]],
        expected: Dict[str, Dict[float, float]],
    ) -> float:
        """
        Total log-likelihood over all loci and alleles.
        observed[locus][allele] = observed RFU height
        expected[locus][allele] = expected RFU height μ_{l,a}
        """
        total_ll = 0.0
        for locus, allele_obs in observed.items():
            allele_exp = expected.get(locus, {})
            for allele, h_obs in allele_obs.items():
                h_exp = allele_exp.get(allele, 0.0)
                if h_exp > 0.0:
                    total_ll += self.log_likelihood_locus_allele(h_obs, h_exp)
                else:
                    total_ll += -1e6  # Unmodeled peak penalty
        return total_ll


# ---------------------------------------------------------------------------
# STRmix (Log-Normal) Likelihood Model
# ---------------------------------------------------------------------------

class STRmixLogNormalModel:
    """
    STRmix Continuous Log-Normal Peak Height Likelihood Model.

    ln(h_{l,a}) ~ N(ln μ_{l,a}, σ²/μ_{l,a}^γ)   γ ≈ 1.0
    ln L = Σ [-½ ln(2π σ²_{l,a}) - (ln h - ln μ)² / (2σ²_{l,a})]
    """

    def __init__(self, sigma: float = 0.35, gamma: float = 1.0):
        """
        Args:
            sigma: base variance scale parameter (σ).
            gamma: heteroscedasticity power (γ ≈ 1.0, STRmix default).
        """
        if sigma <= 0:
            raise ValueError(f"sigma must be positive, got {sigma}")
        self.sigma = sigma
        self.gamma = gamma

    def locus_allele_variance(self, expected_height: float) -> float:
        """σ²_{l,a} = σ² / μ^γ  (heteroscedastic variance)."""
        if expected_height <= 0.0:
            return self.sigma ** 2
        return (self.sigma ** 2) / (expected_height ** self.gamma)

    def log_likelihood_locus_allele(
        self,
        observed_height: float,
        expected_height: float,
    ) -> float:
        """
        Log-likelihood of a single allele peak height under STRmix Log-Normal.

        ln L = -½ ln(2π σ²_{l,a}) - (ln h − ln μ)² / (2σ²_{l,a})
        """
        if observed_height <= 0.0 or expected_height <= 0.0:
            return -1e9

        var = self.locus_allele_variance(expected_height)
        var = max(1e-6, var)

        ln_obs = math.log(observed_height)
        ln_exp = math.log(expected_height)
        residual = ln_obs - ln_exp

        return -0.5 * math.log(2.0 * math.pi * var) - (residual ** 2) / (2.0 * var)

    def log_likelihood_profile(
        self,
        observed: Dict[str, Dict[float, float]],
        expected: Dict[str, Dict[float, float]],
    ) -> float:
        """
        Total log-likelihood over all loci and alleles.
        observed[locus][allele] = observed RFU height
        expected[locus][allele] = expected RFU height μ_{l,a}
        """
        total_ll = 0.0
        for locus, allele_obs in observed.items():
            allele_exp = expected.get(locus, {})
            for allele, h_obs in allele_obs.items():
                h_exp = allele_exp.get(allele, 0.0)
                if h_exp > 0.0:
                    total_ll += self.log_likelihood_locus_allele(h_obs, h_exp)
                else:
                    total_ll += -1e6
        return total_ll


# ---------------------------------------------------------------------------
# Biophysical Expected Peak Height Model (μ_{l,a})
# ---------------------------------------------------------------------------

class BiophysicalPeakModel:
    """
    Computes expected EPG peak heights for a mixture of K contributors.

    μ_{l,a} = T_l · A_l · Σ_k w_k · 10^{−d_k(S_{l,a}−S_0)} · n_{k,l,a}
              + SR_l · μ_{l, a+1}   (back-stutter)

    Parameters:
    -----------
    template_scale : T_l — Total DNA template quantity scalar (RFU units).
    amplification  : A_l per locus amplification efficiency dict.
    stutter_ratios : SR_l per locus back-stutter ratio.
    s0_bp          : S_0 = 100 bp reference molecular size.
    """

    def __init__(
        self,
        template_scale: float = 3000.0,
        amplification: Optional[Dict[str, float]] = None,
        stutter_ratios: Optional[Dict[str, float]] = None,
        s0_bp: float = S0_BP,
    ):
        self.template_scale = template_scale
        self.amplification = amplification or dict(DEFAULT_AMPLIFICATION)
        self.stutter_ratios = stutter_ratios or dict(LOCUS_STUTTER_RATIOS)
        self.s0_bp = s0_bp

    def allele_size_bp(self, locus: str, allele: float) -> float:
        """Approximate bp size for a locus allele based on LOCUS_BASE_BP + 4 bp per repeat unit."""
        base = LOCUS_BASE_BP.get(locus.upper(), 150.0)
        return base + allele * 4.0

    def degradation_factor(self, locus: str, allele: float, d_k: float) -> float:
        """
        10^{−d_k · (S_{l,a} − S_0)}
        d_k: exponential degradation slope ≥ 0.
        """
        s = self.allele_size_bp(locus, allele)
        return 10.0 ** (-d_k * max(0.0, s - self.s0_bp))

    def expected_peak_heights(
        self,
        locus: str,
        genotypes: List[Tuple[float, float]],
        mixture_weights: List[float],
        degradation_slopes: List[float],
    ) -> Dict[float, float]:
        """
        Compute expected peak height μ_{l,a} for all alleles at one locus.

        Args:
            locus           : STR locus name (e.g. "D3S1358").
            genotypes       : List of (a1, a2) tuples, one per contributor.
            mixture_weights : w_k for each contributor k. Must sum to 1.
            degradation_slopes : d_k ≥ 0 for each contributor k.

        Returns:
            Dict[allele → expected_height (RFU)]
        """
        K = len(genotypes)
        if K == 0 or len(mixture_weights) != K or len(degradation_slopes) != K:
            raise ValueError("genotypes, mixture_weights, and degradation_slopes must all be length K")

        T_l = self.template_scale
        A_l = self.amplification.get(locus.upper(), 1.0)

        # Collect all alleles across contributors
        all_alleles: set = set()
        for g in genotypes:
            all_alleles.update(g)

        # --- Phase 1: Compute pre-stutter expected heights ---
        mu_pre: Dict[float, float] = {a: 0.0 for a in all_alleles}

        for k, (g, w_k, d_k) in enumerate(zip(genotypes, mixture_weights, degradation_slopes)):
            for allele in all_alleles:
                # n_{k,l,a} = dosage (0, 1, or 2)
                n_kla = sum(1 for ga in g if abs(ga - allele) < 0.01)
                if n_kla == 0:
                    continue
                dg_factor = self.degradation_factor(locus, allele, d_k)
                mu_pre[allele] += T_l * A_l * w_k * dg_factor * n_kla

        # --- Phase 2: Add back-stutter (n−1 repeat → allele - 1) ---
        SR_l = self.stutter_ratios.get(locus.upper(), 0.07)
        mu_final: Dict[float, float] = dict(mu_pre)
        for b, h in mu_pre.items():
            if h > 0.0:
                stutter_a = round(b - 1.0, 4)
                mu_final[stutter_a] = mu_final.get(stutter_a, 0.0) + SR_l * h

        return mu_final


# ---------------------------------------------------------------------------
# Legacy compatibility: keep StutterModel and PeakHeightModel names active
# ---------------------------------------------------------------------------

class StutterModel:
    """Legacy compatibility class wrapping LOCUS_STUTTER_RATIOS."""
    def __init__(self, stutter_slopes: Optional[Dict[str, float]] = None):
        self.stutter_slopes = stutter_slopes or dict(LOCUS_STUTTER_RATIOS)

    def predict_stutter_height(self, locus_name: str, parent_height_rfu: float) -> float:
        slope = self.stutter_slopes.get(locus_name.upper(), 0.07)
        return slope * parent_height_rfu


class PeakHeightModel:
    """Legacy STRmix Log-Normal wrapper for backward compatibility."""

    def __init__(
        self,
        sigma: float = 0.35,
        gamma: float = 1.0,
        stutter_model: Optional[StutterModel] = None,
    ):
        self.sigma = sigma
        self.gamma = gamma
        self.stutter_model = stutter_model or StutterModel()
        self._model = STRmixLogNormalModel(sigma=sigma, gamma=gamma)

    def log_likelihood(
        self,
        locus_name: str,
        observed_height: float,
        expected_height: float,
    ) -> float:
        return self._model.log_likelihood_locus_allele(observed_height, expected_height)
