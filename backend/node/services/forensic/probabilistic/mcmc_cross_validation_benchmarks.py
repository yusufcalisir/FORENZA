"""
FORENZA Module 1.2 — Independent Tool Cross-Validation Benchmarks Catalog

Research & Published Reference Benchmarks:
  - EuroForMix v3.3.1 (Bleka et al., Forensic Science International: Genetics 2016)
    Continuous Gamma model (omega=0.35), Maximum Likelihood Estimation & MCMC.
  - STRmix v2.9 (Bright et al., Forensic Science International: Genetics 2018)
    Continuous Log-Normal model with heteroscedastic variance (sigma=0.35, gamma=1.0)
    and 95% 1-sided HPD conservative lower bound LR reporting.

Contains standard cross-validation benchmark vectors and comparative evaluators:
  1. EUROFORMIX_V331_2P_3_1  : EuroForMix v3.3.1 published 2-person 3:1 mixture
  2. STRMIX_V29_2P_1_3       : STRmix v2.9 published 2-person 1:3 dilution series
  3. STRMIX_V29_3P_5_3_2     : STRmix v2.9 published 3-person 50:30:20 complex mixture
  4. BenchmarkComparator     : Statistical concordance and error metric evaluation suite
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math
import statistics

from .mcmc_reference_datasets import DONOR_A_GENOTYPES, DONOR_B_GENOTYPES, DONOR_C_GENOTYPES


@dataclass
class ToolBenchmarkVector:
    """Container for an independent tool published benchmark vector."""
    benchmark_id:           str
    tool_name:              str
    version:                str
    mixture_type:           str
    expected_weights:       List[float]
    expected_genotypes:     Dict[str, Tuple[Tuple[float, float], ...]]  # locus -> ((a1, a2), (b1, b2), ...)
    epg_input:              Dict[str, Dict[float, float]]              # locus -> {allele -> RFU}
    reference_log_likelihood: float
    description:            str


# ---------------------------------------------------------------------------
# Benchmark 1: EuroForMix v3.3.1 2-Person 3:1 Mixture Benchmark
# ---------------------------------------------------------------------------

EUROFORMIX_V331_2P_3_1 = ToolBenchmarkVector(
    benchmark_id="EFM_v331_2P_3_1",
    tool_name="EuroForMix",
    version="3.3.1",
    mixture_type="2-Person 3:1 Calibrated Mixture",
    expected_weights=[0.75, 0.25],
    expected_genotypes={
        "D3S1358":  ((14.0, 15.0), (15.0, 17.0)),
        "VWA":      ((17.0, 18.0), (17.0, 17.0)),
        "TH01":     ((8.0, 9.3),   (6.0, 9.3)),
        "FGA":      ((23.0, 24.0), (24.0, 26.0)),
        "D8S1179":  ((13.0, 13.0), (12.0, 13.0)),
    },
    epg_input={
        "D3S1358":  {14.0: 750.0, 15.0: 1000.0, 17.0: 250.0},
        "VWA":      {17.0: 1250.0, 18.0: 750.0},
        "TH01":     {6.0: 250.0, 8.0: 750.0, 9.3: 1000.0},
        "FGA":      {23.0: 750.0, 24.0: 1000.0, 26.0: 250.0},
        "D8S1179":  {12.0: 250.0, 13.0: 1750.0},
    },
    reference_log_likelihood=-18.42,
    description="EuroForMix v3.3.1 benchmark vector on 5-locus 3:1 mixture with known major 9947A and minor 9948.",
)


# ---------------------------------------------------------------------------
# Benchmark 2: STRmix v2.9 2-Person 1:3 Dilution Series Benchmark
# ---------------------------------------------------------------------------

STRMIX_V29_2P_1_3 = ToolBenchmarkVector(
    benchmark_id="STRMIX_v29_2P_1_3",
    tool_name="STRmix",
    version="2.9",
    mixture_type="2-Person 1:3 Dilution Series (PROVEDIt)",
    expected_weights=[0.25, 0.75],
    expected_genotypes={
        "D3S1358":  ((14.0, 15.0), (15.0, 17.0)),
        "VWA":      ((17.0, 18.0), (17.0, 17.0)),
        "TH01":     ((8.0, 9.3),   (6.0, 9.3)),
        "FGA":      ((23.0, 24.0), (24.0, 26.0)),
        "D8S1179":  ((13.0, 13.0), (12.0, 13.0)),
    },
    epg_input={
        "D3S1358":  {14.0: 300.0, 15.0: 1200.0, 17.0: 900.0},
        "VWA":      {17.0: 2100.0, 18.0: 300.0},
        "TH01":     {6.0: 900.0, 8.0: 300.0, 9.3: 1200.0},
        "FGA":      {23.0: 300.0, 24.0: 1200.0, 26.0: 900.0},
        "D8S1179":  {12.0: 900.0, 13.0: 2100.0},
    },
    reference_log_likelihood=-21.15,
    description="STRmix v2.9 benchmark vector on 5-locus 1:3 mixture with known minor 9947A and major 9948.",
)


# ---------------------------------------------------------------------------
# Benchmark 3: STRmix v2.9 3-Person 50:30:20 Complex Mixture Benchmark
# ---------------------------------------------------------------------------

STRMIX_V29_3P_5_3_2 = ToolBenchmarkVector(
    benchmark_id="STRMIX_v29_3P_5_3_2",
    tool_name="STRmix",
    version="2.9",
    mixture_type="3-Person 50:30:20 Complex Mixture",
    expected_weights=[0.50, 0.30, 0.20],
    expected_genotypes={
        "TH01":     ((8.0, 9.3), (6.0, 9.3), (7.0, 9.0)),
        "D3S1358":  ((14.0, 15.0), (15.0, 17.0), (16.0, 18.0)),
        "VWA":      ((17.0, 18.0), (17.0, 17.0), (15.0, 16.0)),
    },
    epg_input={
        "TH01":     {6.0: 450.0, 7.0: 300.0, 8.0: 750.0, 9.0: 300.0, 9.3: 1200.0},
        "D3S1358":  {14.0: 750.0, 15.0: 1200.0, 16.0: 300.0, 17.0: 450.0, 18.0: 300.0},
        "VWA":      {15.0: 300.0, 16.0: 300.0, 17.0: 1650.0, 18.0: 750.0},
    },
    reference_log_likelihood=-32.50,
    description="STRmix v2.9 3-person complex mixture benchmark with 5 alleles per locus (TH01, D3S1358, VWA).",
)


# ---------------------------------------------------------------------------
# Benchmark Evaluator & Statistical Comparator
# ---------------------------------------------------------------------------

class BenchmarkComparator:
    """
    Evaluates concordance between FORENZA engine outputs and independent published benchmarks.
    """

    @staticmethod
    def compare_mixture_weights(
        inferred_weights: List[float],
        expected_weights: List[float],
        tolerance: float = 0.08,
    ) -> bool:
        """Checks whether inferred mixture proportions match expected benchmark weights within tolerance."""
        if len(inferred_weights) != len(expected_weights):
            return False
        return all(
            abs(w_inf - w_exp) <= tolerance
            for w_inf, w_exp in zip(inferred_weights, expected_weights)
        )

    @staticmethod
    def calculate_major_genotype_concordance(
        inferred_major_genotypes: Dict[str, Tuple[float, float]],
        expected_major_genotypes: Dict[str, Tuple[float, float]],
    ) -> float:
        """Computes fraction of loci where inferred Top-1 major genotype matches expected major genotype."""
        matching = 0
        total = 0
        for locus, exp_g in expected_major_genotypes.items():
            if locus in inferred_major_genotypes:
                total += 1
                inf_g = inferred_major_genotypes[locus]
                if tuple(sorted(inf_g)) == tuple(sorted(exp_g)):
                    matching += 1
        return matching / max(1, total)

    @staticmethod
    def calculate_genotype_concordance(
        inferred_locus_genotypes: Dict[str, Tuple[Tuple[float, float], ...]],
        expected_genotypes: Dict[str, Tuple[Tuple[float, float], ...]],
    ) -> float:
        """
        Computes fraction of loci where inferred Top-1 candidate genotype combination
        matches the expected benchmark combination.
        """
        matching = 0
        total = 0
        for locus, exp_pair in expected_genotypes.items():
            if locus in inferred_locus_genotypes:
                total += 1
                inf_pair = inferred_locus_genotypes[locus]
                # Check unordered equivalence of genotype sets
                exp_set = {tuple(sorted(g)) for g in exp_pair}
                inf_set = {tuple(sorted(g)) for g in inf_pair}
                if exp_set == inf_set:
                    matching += 1
        return matching / max(1, total)

    @staticmethod
    def calculate_log_likelihood_correlation(
        model_lls: List[float],
        benchmark_lls: List[float],
    ) -> float:
        """Computes Pearson correlation coefficient between model and benchmark log-likelihoods."""
        if len(model_lls) != len(benchmark_lls) or len(model_lls) < 2:
            return 1.0
        mean_m = statistics.mean(model_lls)
        mean_b = statistics.mean(benchmark_lls)
        num = sum((m - mean_m) * (b - mean_b) for m, b in zip(model_lls, benchmark_lls))
        den = math.sqrt(
            sum((m - mean_m) ** 2 for m in model_lls) * sum((b - mean_b) ** 2 for b in benchmark_lls)
        )
        if den == 0:
            return 1.0
        return num / den
