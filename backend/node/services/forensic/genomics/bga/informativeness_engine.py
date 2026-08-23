"""
Mathematical Engine for Rosenberg Informativeness (In) and Wright's Fixation Index (Fst).

Implements:
- Rosenberg et al. (2003) Informativeness for Assignment (In)
- Wright's Fixation Index (Fst) and Pairwise Population Distance Matrix
- Discriminative Locus Ranking for Multi-Tier AIM Panels
"""

import math
from typing import Dict, List, Tuple, Optional
from backend.node.services.forensic.genomics.bga.schemas import (
    ReferenceSystemEnum,
    LocusInformativenessReport
)
from backend.node.services.forensic.genomics.bga.reference_matrices import BGAReferenceMatrices
from backend.node.services.forensic.genomics.bga.frequency_smoother import BGAFrequencySmoother


class BGAInformativenessEngine:
    """Calculates population genetic differentiation and assignment informativeness."""

    @classmethod
    def compute_rosenberg_in(
        cls,
        rs_id: str,
        ref_system: ReferenceSystemEnum = ReferenceSystemEnum.ONE_THOUSAND_GENOMES_26
    ) -> LocusInformativenessReport:
        """
        Computes Rosenberg's In and Wright's Fst for a specific biallelic AIM SNP across K reference populations.
        """
        pop_freqs_raw = BGAReferenceMatrices.get_allele_frequencies(rs_id, ref_system)
        k_pops = len(pop_freqs_raw)
        if k_pops == 0:
            return LocusInformativenessReport(
                locus_id=rs_id,
                reference_system=ref_system,
                rosenberg_in_nats=0.0,
                rosenberg_in_bits=0.0,
                wright_fst=0.0,
                mean_ref_frequency=0.5,
                mean_alt_frequency=0.5,
                population_frequencies={}
            )

        # Smooth frequencies to prevent log(0) singularity
        smoothed_pops: Dict[str, Tuple[float, float]] = {}
        for pop, (r, a) in pop_freqs_raw.items():
            s_r, s_a = BGAFrequencySmoother.smooth_biallelic_frequencies(r, a, sample_size_n=100)
            smoothed_pops[pop] = (s_r, s_a)

        # Compute mean allele frequencies p_bar across K populations
        mean_ref = sum(pair[0] for pair in smoothed_pops.values()) / k_pops
        mean_alt = sum(pair[1] for pair in smoothed_pops.values()) / k_pops

        # Rosenberg In calculation: In = sum_{j=1}^2 [ - p_bar_j * ln(p_bar_j) + (1/K) * sum_{k=1}^K p_kj * ln(p_kj) ]
        def xlogx(x: float) -> float:
            return x * math.log(x) if x > 1e-12 else 0.0

        term_ref = -xlogx(mean_ref) + (sum(xlogx(pair[0]) for pair in smoothed_pops.values()) / k_pops)
        term_alt = -xlogx(mean_alt) + (sum(xlogx(pair[1]) for pair in smoothed_pops.values()) / k_pops)
        in_nats = max(0.0, term_ref + term_alt)
        in_bits = in_nats / math.log(2.0)

        # Wright's Fst calculation: Fst = Var(p) / (p_bar * (1 - p_bar))
        var_alt = sum((pair[1] - mean_alt) ** 2 for pair in smoothed_pops.values()) / k_pops
        denominator = mean_alt * (1.0 - mean_alt)
        fst = (var_alt / denominator) if denominator > 1e-9 else 0.0
        fst = max(0.0, min(1.0, fst))

        alt_freq_dict = {pop: pair[1] for pop, pair in smoothed_pops.items()}

        return LocusInformativenessReport(
            locus_id=rs_id,
            reference_system=ref_system,
            rosenberg_in_nats=round(in_nats, 6),
            rosenberg_in_bits=round(in_bits, 6),
            wright_fst=round(fst, 6),
            mean_ref_frequency=round(mean_ref, 6),
            mean_alt_frequency=round(mean_alt, 6),
            population_frequencies=alt_freq_dict
        )

    @classmethod
    def compute_pairwise_fst(
        cls,
        rs_id: str,
        pop_a: str,
        pop_b: str,
        ref_system: ReferenceSystemEnum = ReferenceSystemEnum.ONE_THOUSAND_GENOMES_26
    ) -> float:
        """
        Computes pairwise Fst between two populations for a single locus:
        Fst(A, B) = (p_A - p_B)^2 / (4 * p_bar * (1 - p_bar))
        """
        freqs = BGAReferenceMatrices.get_allele_frequencies(rs_id, ref_system)
        if pop_a not in freqs or pop_b not in freqs:
            return 0.0

        p_a = freqs[pop_a][1]
        p_b = freqs[pop_b][1]

        p_bar = (p_a + p_b) / 2.0
        if p_bar <= 1e-9 or p_bar >= (1.0 - 1e-9):
            return 0.0

        numerator = (p_a - p_b) ** 2
        denominator = 4.0 * p_bar * (1.0 - p_bar)
        return min(1.0, max(0.0, numerator / denominator))

    @classmethod
    def compute_multi_locus_pairwise_fst_matrix(
        cls,
        locus_ids: List[str],
        ref_system: ReferenceSystemEnum = ReferenceSystemEnum.ONE_THOUSAND_GENOMES_26
    ) -> Dict[str, Dict[str, float]]:
        """
        Computes multi-locus average pairwise Fst distance matrix across all populations in the reference system.
        """
        pops = BGAReferenceMatrices.get_population_list(ref_system)
        matrix: Dict[str, Dict[str, float]] = {p: {q: 0.0 for q in pops} for p in pops}

        if not locus_ids:
            return matrix

        for p in pops:
            for q in pops:
                if p == q:
                    matrix[p][q] = 0.0
                elif matrix[q][p] > 0.0:
                    matrix[p][q] = matrix[q][p]
                else:
                    sum_fst = sum(cls.compute_pairwise_fst(loc, p, q, ref_system) for loc in locus_ids)
                    avg_fst = sum_fst / len(locus_ids)
                    matrix[p][q] = round(avg_fst, 6)
                    matrix[q][p] = round(avg_fst, 6)

        return matrix
