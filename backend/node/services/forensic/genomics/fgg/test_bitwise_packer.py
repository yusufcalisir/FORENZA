"""
Unit Tests for Bitwise 2-Bit Genotype Packing and IBS0 Checking.
"""

import pytest
from backend.node.services.forensic.genomics.fgg.schemas import GenotypeStateEnum
from backend.node.services.forensic.genomics.fgg.bitwise_packer import BitwiseGenotypePacker


class TestBitwiseGenotypePacker:
    """Tests 2-bit packing, unpacking round-trip, and IBS0 checks."""

    def test_pack_unpack_roundtrip(self):
        original = [
            GenotypeStateEnum.HOM_REF,  # 0
            GenotypeStateEnum.HET,      # 1
            GenotypeStateEnum.NO_CALL,  # 2
            GenotypeStateEnum.HOM_ALT,  # 3
            GenotypeStateEnum.HOM_REF,  # 0
            GenotypeStateEnum.HOM_ALT,  # 3
            GenotypeStateEnum.HET       # 1
        ]
        packed = BitwiseGenotypePacker.pack_states(original)
        # 7 SNPs -> 2 bytes (ceil(7/4) = 2)
        assert len(packed) == 2

        unpacked = BitwiseGenotypePacker.unpack_states(packed, count=len(original))
        assert unpacked == original

    def test_opposite_homozygote_ibs0_detection(self):
        # HOM_REF vs HOM_ALT is IBS0
        assert BitwiseGenotypePacker.is_opposite_homozygote(
            GenotypeStateEnum.HOM_REF, GenotypeStateEnum.HOM_ALT
        ) is True
        assert BitwiseGenotypePacker.is_opposite_homozygote(
            GenotypeStateEnum.HOM_ALT, GenotypeStateEnum.HOM_REF
        ) is True

        # HET vs HOM_REF or HET vs HOM_ALT is NOT IBS0
        assert BitwiseGenotypePacker.is_opposite_homozygote(
            GenotypeStateEnum.HET, GenotypeStateEnum.HOM_REF
        ) is False
        assert BitwiseGenotypePacker.is_opposite_homozygote(
            GenotypeStateEnum.HET, GenotypeStateEnum.HOM_ALT
        ) is False

        # Missing call is NOT IBS0
        assert BitwiseGenotypePacker.is_opposite_homozygote(
            GenotypeStateEnum.NO_CALL, GenotypeStateEnum.HOM_ALT
        ) is False

    def test_count_ibs0_in_window(self):
        ind1 = [GenotypeStateEnum.HOM_REF, GenotypeStateEnum.HOM_ALT, GenotypeStateEnum.HET, GenotypeStateEnum.HOM_REF]
        ind2 = [GenotypeStateEnum.HOM_ALT, GenotypeStateEnum.HOM_REF, GenotypeStateEnum.HET, GenotypeStateEnum.HOM_REF]
        # Position 0: HOM_REF vs HOM_ALT (IBS0 #1)
        # Position 1: HOM_ALT vs HOM_REF (IBS0 #2)
        # Position 2: HET vs HET (not IBS0)
        # Position 3: HOM_REF vs HOM_REF (not IBS0)
        count = BitwiseGenotypePacker.count_ibs0_in_window(ind1, ind2)
        assert count == 2
