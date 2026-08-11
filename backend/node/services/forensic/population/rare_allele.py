"""
FORENZA Rare Allele Frequency Bounding & Smoothing Engine.
Implements NRC II Recommendation 4.1 rule (minimum frequency bound = 5 / 2N),
Dirichlet pseudo-count smoothing, and private allele rarity scoring.

Reference:
  National Research Council (NRC II, 1996). The Evaluation of Forensic DNA Evidence.
  Recommendation 4.1: Minimum allele frequency bound = 5 / (2N) where N is database size.
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class RareAlleleBoundedResult:
    locus: str
    allele: float
    observed_count: int
    raw_frequency: float
    bounded_frequency: float
    was_bounded: bool
    rarity_index: float
    explanation: str


class RareAlleleEngine:
    """
    Enforces minimum frequency bounds and Dirichlet pseudo-count smoothing
    for rare or unobserved alleles in accordance with NRC II Recommendation 4.1.
    """

    def __init__(self, default_database_n: int = 500):
        self.database_n = default_database_n

    def get_minimum_frequency_bound(self, n_individuals: Optional[int] = None) -> float:
        """
        Computes NRC II Rec 4.1 minimum frequency bound:
        p_min = 5 / (2 * N)
        For default N = 500 (1000 alleles): p_min = 5 / 1000 = 0.005
        """
        n = n_individuals if (n_individuals and n_individuals > 0) else self.database_n
        return 5.0 / (2.0 * n)

    def bound_allele_frequency(
        self,
        locus: str,
        allele: float,
        raw_freq: float,
        observed_count: int = 0,
        n_individuals: Optional[int] = None
    ) -> RareAlleleBoundedResult:
        """
        Applies NRC II 5/2N minimum bound if raw_freq < p_min.
        Also calculates private allele Rarity Index R = -log10(bounded_freq).
        """
        p_min = self.get_minimum_frequency_bound(n_individuals)
        was_bounded = False

        if raw_freq < p_min or observed_count < 5:
            bounded_freq = p_min
            was_bounded = True
            expl = f"Frequency bounded to NRC II Rec 4.1 minimum (5/2N = {p_min:.4f})"
        else:
            bounded_freq = raw_freq
            expl = f"Observed frequency ({raw_freq:.4f}) exceeds minimum bound ({p_min:.4f})"

        rarity_index = -math.log10(max(1e-12, bounded_freq))

        return RareAlleleBoundedResult(
            locus=locus,
            allele=allele,
            observed_count=observed_count,
            raw_frequency=round(raw_freq, 6),
            bounded_frequency=round(bounded_freq, 6),
            was_bounded=was_bounded,
            rarity_index=round(rarity_index, 4),
            explanation=expl
        )

    def apply_dirichlet_smoothing(
        self,
        counts_map: Dict[float, int],
        alpha: float = 1.0,
        n_individuals: Optional[int] = None
    ) -> Dict[float, float]:
        """
        Applies Dirichlet Laplace pseudo-count smoothing to allele counts:
        p_i = (count_i + alpha) / (total_counts + alpha * total_categories)
        """
        total_counts = sum(counts_map.values())
        k = len(counts_map)
        if k == 0:
            return {}

        smoothed: Dict[float, float] = {}
        denom = total_counts + alpha * k
        p_min = self.get_minimum_frequency_bound(n_individuals)

        for allele, count in counts_map.items():
            p_smooth = (count + alpha) / denom
            smoothed[allele] = round(max(p_min, p_smooth), 6)

        return smoothed
