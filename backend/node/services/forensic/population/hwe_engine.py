"""
FORENZA Module 03 - Hardy-Weinberg Equilibrium (HWE) Exact Test Engine.
Implements verbatim from pillar_1_probabilistic_genotyping_research.md Section 3.2:

  Guo & Thompson (1992) HWE Exact Test:
    P(N | {n_i}) = [ prod(n_i!) * 2^(N - sum(N_ii)) ] / [ N! * prod(N_ij!) ]

  Bonferroni correction for 24 loci:
    alpha_bonferroni = 0.05 / 24 = 0.00208...

  Inbreeding coefficient (Wahlund effect):
    F_IS = 1 - H_obs / H_exp
"""

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# Exact constants from research specification
_N_LOCI_CODIS24: int = 24
_ALPHA_OVERALL: float = 0.05
_ALPHA_BONFERRONI: float = _ALPHA_OVERALL / _N_LOCI_CODIS24   # = 0.002083...


@dataclass
class HWETestResult:
    """Result of Guo & Thompson HWE exact test for one locus."""
    locus: str
    n_alleles: int                   # number of distinct alleles observed
    n_genotypes: int                 # total genotypes sampled
    h_obs: float                     # observed heterozygosity
    h_exp: float                     # expected heterozygosity under HWE
    f_is: float                      # inbreeding coefficient F_IS = 1 - H_obs/H_exp
    p_value: float                   # Monte Carlo permutation p-value
    alpha_bonferroni: float          # Bonferroni threshold used
    hwe_rejected: bool               # True if p-value < alpha_bonferroni
    decision: str                    # 'HWE_SATISFIED' | 'HWE_VIOLATED'
    n_permutations: int


@dataclass
class HWE24LociResult:
    """Summary of HWE testing across all 24 STR loci."""
    locus_results: Dict[str, HWETestResult]
    n_loci_tested: int
    n_loci_violated: int
    n_loci_satisfied: int
    bonferroni_alpha: float
    wahlund_detected: bool           # True if any locus has F_IS > 0.10 (strong inbreeding)
    overall_hwe_passed: bool         # True if zero loci violated after Bonferroni


class HWEEngine:
    """
    Hardy-Weinberg Equilibrium exact test engine.

    Guo & Thompson (1992) Markov chain Monte Carlo permutation test:
      P(N | {n_i}) = [prod(n_i!) * 2^(N - sum(N_ii))] / [N! * prod(N_ij!)]

    Bonferroni correction for 24 loci:
      alpha_bonferroni = 0.05 / 24 = 0.002083...
    """

    # ── Core Statistics ───────────────────────────────────────────────────────

    @staticmethod
    def compute_expected_heterozygosity(
        allele_frequencies: Dict[float, float]
    ) -> float:
        """
        Expected heterozygosity under Hardy-Weinberg:
          H_exp = 1 - sum(p_i^2)
        """
        return 1.0 - sum(p ** 2 for p in allele_frequencies.values())

    @staticmethod
    def compute_observed_heterozygosity(
        genotype_counts: Dict[Tuple[float, float], int]
    ) -> Tuple[float, int]:
        """
        Observed heterozygosity:
          H_obs = N_het / N_total
        Returns (H_obs, N_total).
        """
        n_het = sum(
            count for (a1, a2), count in genotype_counts.items() if a1 != a2
        )
        n_total = sum(genotype_counts.values())
        if n_total == 0:
            return 0.0, 0
        return n_het / n_total, n_total

    @staticmethod
    def compute_inbreeding_coefficient(h_obs: float, h_exp: float) -> float:
        """
        Wright's inbreeding coefficient:
          F_IS = 1 - H_obs / H_exp
        Positive: heterozygote deficit (inbreeding / Wahlund effect).
        Negative: heterozygote excess (outbreeding).
        """
        if h_exp <= 0:
            return 0.0
        return 1.0 - (h_obs / h_exp)

    # ── Guo & Thompson Exact Test (Monte Carlo permutation) ───────────────────

    @staticmethod
    def _compute_log_p_observed(
        genotype_counts: Dict[Tuple[float, float], int],
        allele_counts: Dict[float, int],
        n_total: int,
    ) -> float:
        """
        Log of Guo & Thompson exact test statistic:
          log P(N | {n_i}) = sum(log n_i!) + (N - sum(N_ii)) * log(2) - log(N!) - sum(log N_ij!)
        """
        # sum(log n_i!) — allele marginal counts
        log_stat = sum(math.lgamma(c + 1) for c in allele_counts.values())
        # + (N - N_homozygous) * log(2)
        n_hom = sum(
            count for (a1, a2), count in genotype_counts.items() if a1 == a2
        )
        log_stat += (n_total - n_hom) * math.log(2.0)
        # - log(N!)
        log_stat -= math.lgamma(n_total + 1)
        # - sum(log N_ij!)
        log_stat -= sum(math.lgamma(c + 1) for c in genotype_counts.values())
        return log_stat

    def test_locus_hwe(
        self,
        locus: str,
        genotype_counts: Dict[Tuple[float, float], int],
        n_permutations: int = 10000,
        seed: int = 42,
    ) -> HWETestResult:
        """
        Guo & Thompson (1992) HWE Exact Test via Monte Carlo permutation.

        Permutation strategy: randomly shuffle observed alleles into genotype pairs
        and count proportion of permuted configurations at least as extreme as observed.

        Args:
            locus: locus name
            genotype_counts: {(a1, a2): count} observed genotype frequencies
            n_permutations: Monte Carlo iterations (default 10,000)
            seed: RNG seed for reproducibility

        Returns:
            HWETestResult with p-value and Bonferroni decision.
        """
        rng = random.Random(seed)

        # Build allele pool and marginal counts
        allele_pool: List[float] = []
        allele_counts: Dict[float, int] = {}
        for (a1, a2), count in genotype_counts.items():
            for _ in range(count):
                allele_pool.append(a1)
                allele_pool.append(a2)
            allele_counts[a1] = allele_counts.get(a1, 0) + count
            allele_counts[a2] = allele_counts.get(a2, 0) + count

        n_total = sum(genotype_counts.values())
        if n_total == 0:
            return HWETestResult(
                locus=locus, n_alleles=0, n_genotypes=0,
                h_obs=0.0, h_exp=0.0, f_is=0.0,
                p_value=1.0, alpha_bonferroni=_ALPHA_BONFERRONI,
                hwe_rejected=False, decision='HWE_SATISFIED',
                n_permutations=n_permutations,
            )

        # Allele frequencies for H_exp
        total_alleles = len(allele_pool)
        allele_freqs = {a: c / total_alleles for a, c in allele_counts.items()}

        h_exp = self.compute_expected_heterozygosity(allele_freqs)
        h_obs, _ = self.compute_observed_heterozygosity(genotype_counts)
        f_is = self.compute_inbreeding_coefficient(h_obs, h_exp)

        # Observed log-probability
        log_p_obs = self._compute_log_p_observed(genotype_counts, allele_counts, n_total)

        # Monte Carlo permutation
        n_extreme = 0
        for _ in range(n_permutations):
            # Shuffle allele pool and pair into genotypes
            shuffled = allele_pool[:]
            rng.shuffle(shuffled)
            perm_geno: Dict[Tuple[float, float], int] = {}
            for i in range(0, len(shuffled), 2):
                pair = (min(shuffled[i], shuffled[i + 1]),
                        max(shuffled[i], shuffled[i + 1]))
                perm_geno[pair] = perm_geno.get(pair, 0) + 1

            log_p_perm = self._compute_log_p_observed(perm_geno, allele_counts, n_total)
            if log_p_perm <= log_p_obs + 1e-10:   # as extreme or more extreme
                n_extreme += 1

        p_value = n_extreme / n_permutations
        hwe_rejected = p_value < _ALPHA_BONFERRONI

        return HWETestResult(
            locus=locus,
            n_alleles=len(allele_counts),
            n_genotypes=n_total,
            h_obs=round(h_obs, 4),
            h_exp=round(h_exp, 4),
            f_is=round(f_is, 4),
            p_value=round(p_value, 6),
            alpha_bonferroni=round(_ALPHA_BONFERRONI, 6),
            hwe_rejected=hwe_rejected,
            decision='HWE_VIOLATED' if hwe_rejected else 'HWE_SATISFIED',
            n_permutations=n_permutations,
        )

    def evaluate_24_loci_hwe(
        self,
        population_genotypes: Dict[str, Dict[Tuple[float, float], int]],
        n_permutations: int = 10000,
        seed: int = 42,
    ) -> HWE24LociResult:
        """
        Tests all loci (up to 24) with Bonferroni-corrected threshold.
        Detects Wahlund effect (F_IS > 0.10 in any locus).

        Args:
            population_genotypes: {locus: {(a1,a2): count}}
            n_permutations: per-locus Monte Carlo iterations
            seed: global RNG seed

        Returns:
            HWE24LociResult with per-locus decisions and overall verdict.
        """
        locus_results: Dict[str, HWETestResult] = {}
        for idx, (locus, geno_counts) in enumerate(population_genotypes.items()):
            result = self.test_locus_hwe(
                locus=locus,
                genotype_counts=geno_counts,
                n_permutations=n_permutations,
                seed=seed + idx,
            )
            locus_results[locus] = result

        n_violated = sum(1 for r in locus_results.values() if r.hwe_rejected)
        n_satisfied = len(locus_results) - n_violated
        wahlund = any(r.f_is > 0.10 for r in locus_results.values())

        return HWE24LociResult(
            locus_results=locus_results,
            n_loci_tested=len(locus_results),
            n_loci_violated=n_violated,
            n_loci_satisfied=n_satisfied,
            bonferroni_alpha=round(_ALPHA_BONFERRONI, 6),
            wahlund_detected=wahlund,
            overall_hwe_passed=n_violated == 0,
        )

    def compute_inbreeding_coefficient_locus(
        self,
        h_obs: float,
        h_exp: float,
    ) -> float:
        """
        Wrapper: F_IS = 1 - H_obs / H_exp
        Positive = inbreeding / Wahlund effect.
        Negative = outbreeding.
        """
        return self.compute_inbreeding_coefficient(h_obs, h_exp)
