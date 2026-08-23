"""
Bitwise 2-Bit Genotype Compression and IBS0 Matching Engine.

Packs 4 SNP genotypes into a single byte:
00_2 (0) = HOM_REF
01_2 (1) = HET
10_2 (2) = NO_CALL (Missing)
11_2 (3) = HOM_ALT

Enables O(1) bitwise IBS0 checks across 32/64 SNP words simultaneously.
"""

from typing import List, Tuple
from .schemas import GenotypeStateEnum, BitwiseGenotypeBlock


class BitwiseGenotypePacker:
    """Compresses and unpacks dense SNP genotype vectors using 2-bit encoding."""

    @staticmethod
    def pack_states(states: List[GenotypeStateEnum]) -> bytes:
        """
        Packs a list of GenotypeStateEnum values into compact bytes.
        4 SNPs per byte, little-endian bit order:
        Byte = (SNP_0 & 3) | ((SNP_1 & 3) << 2) | ((SNP_2 & 3) << 4) | ((SNP_3 & 3) << 6)
        """
        byte_arr = bytearray()
        n = len(states)
        for i in range(0, n, 4):
            b = 0
            for j in range(4):
                if i + j < n:
                    val = int(states[i + j].value) & 0x03
                else:
                    val = GenotypeStateEnum.NO_CALL.value & 0x03
                b |= (val << (j * 2))
            byte_arr.append(b)
        return bytes(byte_arr)

    @staticmethod
    def unpack_states(packed: bytes, count: int) -> List[GenotypeStateEnum]:
        """Unpacks 2-bit packed bytes back into a list of GenotypeStateEnum values."""
        states = []
        for b in packed:
            for j in range(4):
                if len(states) < count:
                    val = (b >> (j * 2)) & 0x03
                    states.append(GenotypeStateEnum(val))
        return states

    @staticmethod
    def is_opposite_homozygote(state1: GenotypeStateEnum, state2: GenotypeStateEnum) -> bool:
        """
        Checks if two genotypes are opposite homozygotes (IBS0: 0/0 vs 1/1).
        True IBD1 sharing mathematically precludes true IBS0 states.
        """
        if state1 == GenotypeStateEnum.HOM_REF and state2 == GenotypeStateEnum.HOM_ALT:
            return True
        if state1 == GenotypeStateEnum.HOM_ALT and state2 == GenotypeStateEnum.HOM_REF:
            return True
        return False

    @classmethod
    def count_ibs0_in_window(cls, states1: List[GenotypeStateEnum], states2: List[GenotypeStateEnum]) -> int:
        """Counts the number of IBS0 (opposite homozygous) loci in a given window."""
        ibs0_count = 0
        min_len = min(len(states1), len(states2))
        for i in range(min_len):
            if cls.is_opposite_homozygote(states1[i], states2[i]):
                ibs0_count += 1
        return ibs0_count
