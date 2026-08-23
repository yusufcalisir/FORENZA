"""
Cotterman & KING-Robust Kinship Estimation Engine.

Calculates:
- Cotterman coefficients k0, k1, k2 (sum to 1.0)
- Kinship coefficient: Phi = 0.5*k2 + 0.25*k1
- Wright's relationship coefficient: r = 2*Phi = k2 + 0.5*k1
- Population-structure independent KING-robust kinship: phi_hat
"""

from typing import List, Dict, Tuple
from .schemas import IBDSegment, IBDStateEnum, IngestedFGGProfile, GenotypeStateEnum
from .genetic_map import FGGGeneticMap
from .bitwise_packer import BitwiseGenotypePacker


class FGGKinshipEstimator:
    """Computes Cotterman, Wright, and KING-robust relationship coefficients."""

    TOTAL_GENOME_CM: float = FGGGeneticMap.TOTAL_AUTOSOMAL_CM

    @classmethod
    def compute_kinship_from_segments(
        cls,
        segments: List[IBDSegment],
        profile_a: IngestedFGGProfile,
        profile_b: IngestedFGGProfile
    ) -> Dict[str, float]:
        """Calculates Cotterman k0, k1, k2, Kinship Phi, Wright r, and KING-robust Phi."""
        l_ibd1 = sum(s.length_cm for s in segments if s.ibd_state == IBDStateEnum.IBD1)
        l_ibd2 = sum(s.length_cm for s in segments if s.ibd_state == IBDStateEnum.IBD2)

        # Normalize over total autosomal genetic length (~3587.25 cM)
        k1 = min(1.0, l_ibd1 / cls.TOTAL_GENOME_CM)
        k2 = min(1.0, l_ibd2 / cls.TOTAL_GENOME_CM)

        # Ensure simplex boundary: k0 + k1 + k2 = 1.0
        if k1 + k2 > 1.0:
            scale = 1.0 / (k1 + k2)
            k1 *= scale
            k2 *= scale
            k0 = 0.0
        else:
            k0 = max(0.0, 1.0 - (k1 + k2))

        kinship_phi = (0.5 * k2) + (0.25 * k1)
        wright_r = k2 + (0.5 * k1)

        # KING-robust calculation
        king_phi = cls.compute_king_robust(profile_a, profile_b)

        return {
            "k0": round(k0, 6),
            "k1": round(k1, 6),
            "k2": round(k2, 6),
            "kinship_phi": round(kinship_phi, 6),
            "wright_r": round(wright_r, 6),
            "king_phi": round(king_phi, 6)
        }

    @classmethod
    def compute_king_robust(cls, profile_a: IngestedFGGProfile, profile_b: IngestedFGGProfile) -> float:
        """
        Computes the KING-robust kinship estimator (Manichaikul et al. 2010):
        phi_hat = (N_Aa,Aa - 2 * N_IBS0) / (N_Aa^(i) + N_Aa^(j))
        Robust against population substructure, admixture, and unknown allele frequencies.
        """
        n_double_het = 0
        n_ibs0 = 0
        n_het_a = 0
        n_het_b = 0

        shared_chroms = [str(c) for c in range(1, 23) if str(c) in profile_a.chromosome_blocks and str(c) in profile_b.chromosome_blocks]

        for ch in shared_chroms:
            ba = profile_a.chromosome_blocks[ch]
            bb = profile_b.chromosome_blocks[ch]

            bytes_a = bytes.fromhex(ba.packed_bytes_hex)
            bytes_b = bytes.fromhex(bb.packed_bytes_hex)

            states_a = BitwiseGenotypePacker.unpack_states(bytes_a, ba.snp_count)
            states_b = BitwiseGenotypePacker.unpack_states(bytes_b, bb.snp_count)

            min_len = min(len(states_a), len(states_b))
            for i in range(min_len):
                sa = states_a[i]
                sb = states_b[i]

                if sa == GenotypeStateEnum.NO_CALL or sb == GenotypeStateEnum.NO_CALL:
                    continue

                if sa == GenotypeStateEnum.HET:
                    n_het_a += 1
                if sb == GenotypeStateEnum.HET:
                    n_het_b += 1

                if sa == GenotypeStateEnum.HET and sb == GenotypeStateEnum.HET:
                    n_double_het += 1
                elif BitwiseGenotypePacker.is_opposite_homozygote(sa, sb):
                    n_ibs0 += 1

        denom = n_het_a + n_het_b
        if denom == 0:
            return 0.0

        phi_hat = (n_double_het - (2.0 * n_ibs0)) / denom
        return max(-0.5, min(0.5, phi_hat))
