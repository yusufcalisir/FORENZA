"""
Unit Tests for Coordinate Liftover and Strand Normalization.
"""

import pytest
from backend.node.services.forensic.genomics.bga.schemas import GenomicAssemblyEnum
from backend.node.services.forensic.genomics.bga.liftover_normalizer import BGALiftoverNormalizer


def test_chromosome_normalization():
    """Verify chromosome string stripping."""
    assert BGALiftoverNormalizer.normalize_chromosome("chr1") == "1"
    assert BGALiftoverNormalizer.normalize_chromosome("CHR22") == "22"
    assert BGALiftoverNormalizer.normalize_chromosome(" chrX ") == "X"


def test_strand_normalization_forward():
    """Verify forward-strand genotype retains orientation."""
    # rs2814778 ref=T, alt=C
    a1, a2, dosage = BGALiftoverNormalizer.normalize_genotype_strand("rs2814778", "T", "C")
    assert (a1, a2) == ("C", "T")
    assert dosage == 1.0

    a1, a2, dosage = BGALiftoverNormalizer.normalize_genotype_strand("rs2814778", "C", "C")
    assert (a1, a2) == ("C", "C")
    assert dosage == 2.0


def test_strand_normalization_reverse_flipping():
    """Verify reverse-strand calls are complemented to forward top strand."""
    # rs2814778 ref=T, alt=C -> reverse complement: ref=A, alt=G
    a1, a2, dosage = BGALiftoverNormalizer.normalize_genotype_strand("rs2814778", "A", "G")
    assert (a1, a2) == ("C", "T")
    assert dosage == 1.0


def test_liftover_position():
    """Verify coordinate translation between GRCh37 and GRCh38."""
    pos38 = BGALiftoverNormalizer.liftover_position("rs1426654", GenomicAssemblyEnum.GRCH37, GenomicAssemblyEnum.GRCH38)
    assert pos38 == 48187887

    pos37 = BGALiftoverNormalizer.liftover_position("rs1426654", GenomicAssemblyEnum.GRCH38, GenomicAssemblyEnum.GRCH37)
    assert pos37 == 48426484
