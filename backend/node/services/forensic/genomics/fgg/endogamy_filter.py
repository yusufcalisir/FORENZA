"""
Runs of Homozygosity (ROH) & Endogamy Mitigation Engine.

Computes individual inbreeding coefficients (F_ROH) and adjusts shared cM
to eliminate false close-cousin inflation in endogamous / isolated cohorts.
"""

from typing import List, Dict, Tuple
from .schemas import IngestedFGGProfile, GenotypeStateEnum, PairwiseIBDResult
from .bitwise_packer import BitwiseGenotypePacker
from .genetic_map import FGGGeneticMap


class FGGEndogamyFilter:
    """Evaluates Runs of Homozygosity (ROH) and applies excess IBD background correction."""

    MIN_ROH_LENGTH_CM: float = 5.00          # Minimum length for a true ROH segment (cM)
    MIN_ROH_SNP_COUNT: int = 200             # Minimum SNP count in ROH
    ENDOGAMY_ROH_THRESHOLD: float = 0.035    # F_ROH > 3.5% indicates endogamy / pedigree collapse
    TOTAL_GENOME_CM: float = FGGGeneticMap.TOTAL_AUTOSOMAL_CM

    @classmethod
    def compute_individual_f_roh(cls, profile: IngestedFGGProfile) -> float:
        """
        Computes the inbreeding coefficient F_ROH:
        F_ROH = Sum(L_ROH) / L_genome
        Scans all 22 autosomes for contiguous homozygous blocks lacking heterozygous calls.
        """
        total_roh_cm = 0.0

        for ch, block in profile.chromosome_blocks.items():
            if ch not in FGGGeneticMap.CHROMOSOME_MAP_DATA:
                continue

            bytes_packed = bytes.fromhex(block.packed_bytes_hex)
            states = BitwiseGenotypePacker.unpack_states(bytes_packed, block.snp_count)
            positions = block.positions_bp
            n = len(states)
            if n < cls.MIN_ROH_SNP_COUNT:
                continue

            in_roh = False
            start_idx = 0

            for i in range(n):
                s = states[i]
                if s == GenotypeStateEnum.HET:
                    if in_roh:
                        # Close ROH block
                        roh_cm = cls._evaluate_roh_segment(ch, start_idx, i - 1, positions)
                        total_roh_cm += roh_cm
                        in_roh = False
                elif s in (GenotypeStateEnum.HOM_REF, GenotypeStateEnum.HOM_ALT):
                    if not in_roh:
                        in_roh = True
                        start_idx = i

            # Tail block
            if in_roh:
                roh_cm = cls._evaluate_roh_segment(ch, start_idx, n - 1, positions)
                total_roh_cm += roh_cm

        f_roh = min(1.0, total_roh_cm / cls.TOTAL_GENOME_CM)
        return round(f_roh, 6)

    @classmethod
    def _evaluate_roh_segment(cls, chromosome: str, start_idx: int, end_idx: int, positions: List[int]) -> float:
        """Calculates genetic length if segment passes ROH threshold."""
        snp_count = end_idx - start_idx + 1
        if snp_count < cls.MIN_ROH_SNP_COUNT:
            return 0.0

        start_bp = positions[start_idx]
        end_bp = positions[end_idx]
        seg_cm = FGGGeneticMap.get_segment_length_cm(chromosome, start_bp, end_bp)
        if seg_cm >= cls.MIN_ROH_LENGTH_CM:
            return seg_cm
        return 0.0

    @classmethod
    def adjust_endogamy_ibd(
        cls,
        pairwise_result: PairwiseIBDResult,
        f_roh_a: float,
        f_roh_b: float
    ) -> Tuple[float, float, bool]:
        """
        Adjusts raw shared cM based on ROH inbreeding coefficients and segment morphology.
        Returns: (adjusted_cm, adjustment_delta_cm, is_endogamy_suspected)
        """
        raw_cm = pairwise_result.total_shared_cm
        l_max = pairwise_result.longest_segment_cm
        n_seg = pairwise_result.segment_count

        mean_roh = 0.5 * (f_roh_a + f_roh_b)
        is_endogamous = mean_roh >= cls.ENDOGAMY_ROH_THRESHOLD

        # If many fragmented segments (e.g. n_seg >= 8) with low L_max (< 18 cM) and elevated ROH
        if is_endogamous or (n_seg >= 8 and l_max < 18.0 and raw_cm > 100.0):
            # Scale reduction factor proportional to ROH and fragment count
            roh_factor = max(1.0, mean_roh * 20.0)
            fragment_penalty = min(0.65, (n_seg / 20.0) * 0.40)
            
            # Keep long intact segment contribution, discount fragmented noise
            if l_max >= 20.0:
                discount_fraction = min(0.40, fragment_penalty * 0.5)
            else:
                discount_fraction = min(0.70, fragment_penalty * roh_factor)

            adjustment_delta = raw_cm * discount_fraction
            adjusted_cm = max(0.0, raw_cm - adjustment_delta)
            return (round(adjusted_cm, 4), round(adjustment_delta, 4), True)

        return (raw_cm, 0.0, False)
