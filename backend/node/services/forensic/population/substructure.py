"""
FORENZA Advanced Population Genetics — Substructure & Wright's FST Engine.
Implements Wright's FST fixating index calculation, locus heterozygosity (He),
and subpopulation genetic distance matrices in accordance with NRC II & SWGDAM standards.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class PopulationSubstructureResult:
    population_pair: Tuple[str, str]
    fst_value: float
    genetic_distance_neis: float
    locus_fst_breakdown: Dict[str, float]
    recommendation: str


# ── FST Reference Matrices across major CODIS populations ─────────────────────
# Baseline pairwise FST values from FBI/CODIS population studies
CODIS_PAIRWISE_FST: Dict[Tuple[str, str], float] = {
    ("Caucasian", "AfricanAmerican"): 0.038,
    ("Caucasian", "Hispanic"):        0.015,
    ("Caucasian", "Asian"):           0.042,
    ("AfricanAmerican", "Hispanic"): 0.029,
    ("AfricanAmerican", "Asian"):    0.055,
    ("Hispanic", "Asian"):           0.035,
}


class SubstructureEngine:
    """
    Computes Wright's FST and Nei's standard genetic distance between populations
    across CODIS STR loci to assess population differentiation.
    """

    @staticmethod
    def compute_locus_fst(freqs_pop1: Dict[float, float], freqs_pop2: Dict[float, float]) -> float:
        """
        Computes Wright's FST for a single locus across two populations:
        FST = (HT - HS) / HT
        HS = average subpopulation heterozygosity
        HT = total population heterozygosity under pooled allele frequencies
        """
        all_alleles = set(freqs_pop1.keys()).union(set(freqs_pop2.keys()))
        if not all_alleles:
            return 0.0

        # Subpopulation heterozygosities HS1 and HS2
        h_s1 = 1.0 - sum(p ** 2 for p in freqs_pop1.values())
        h_s2 = 1.0 - sum(p ** 2 for p in freqs_pop2.values())
        h_s = (h_s1 + h_s2) / 2.0

        # Pooled allele frequencies and HT
        h_t_sum = 0.0
        for a in all_alleles:
            p_bar = (freqs_pop1.get(a, 0.0) + freqs_pop2.get(a, 0.0)) / 2.0
            h_t_sum += p_bar ** 2
        h_t = 1.0 - h_t_sum

        if h_t <= 0:
            return 0.0

        fst = (h_t - h_s) / h_t
        return max(0.0, min(1.0, fst))

    def compute_pairwise_fst(
        self,
        pop1: str,
        pop2: str,
        loci_freqs: Optional[Dict[str, Dict[str, Dict[float, float]]]] = None
    ) -> PopulationSubstructureResult:
        """
        Computes multi-locus average FST and Nei's genetic distance D = -ln(1 - FST).
        Falls back to CODIS baseline empirical FST matrices if loci frequencies not supplied.
        """
        pair_key = (pop1, pop2) if (pop1, pop2) in CODIS_PAIRWISE_FST else (pop2, pop1)
        baseline_fst = CODIS_PAIRWISE_FST.get(pair_key, 0.020)

        locus_breakdown: Dict[str, float] = {}

        if loci_freqs and pop1 in loci_freqs and pop2 in loci_freqs:
            fst_sum = 0.0
            evaluated = 0
            for locus, p1_map in loci_freqs[pop1].items():
                if locus in loci_freqs[pop2]:
                    f = self.compute_locus_fst(p1_map, loci_freqs[pop2][locus])
                    locus_breakdown[locus] = round(f, 4)
                    fst_sum += f
                    evaluated += 1

            avg_fst = (fst_sum / evaluated) if evaluated > 0 else baseline_fst
        else:
            avg_fst = baseline_fst
            locus_breakdown = {"CODIS_COMPOSITE": round(baseline_fst, 4)}

        # Nei's standard genetic distance D = -ln(1 - FST)
        nei_d = -math.log(max(1e-6, 1.0 - avg_fst))

        if avg_fst < 0.01:
            rec = "Negligible substructure differentiation (theta = 0.01 sufficient)"
        elif avg_fst < 0.05:
            rec = "Moderate substructure differentiation (apply NRC II theta = 0.01 to 0.03)"
        else:
            rec = "Substantial substructure differentiation (apply NRC II theta = 0.03 to 0.05)"

        return PopulationSubstructureResult(
            population_pair=(pop1, pop2),
            fst_value=round(avg_fst, 4),
            genetic_distance_neis=round(nei_d, 4),
            locus_fst_breakdown=locus_breakdown,
            recommendation=rec
        )
