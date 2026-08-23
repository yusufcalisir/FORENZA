"""
Unit Tests for Population Reference Matrices (1000G, gnomAD v4, Microhaplotypes).
"""

import pytest
from backend.node.services.forensic.genomics.bga.schemas import ReferenceSystemEnum
from backend.node.services.forensic.genomics.bga.reference_matrices import BGAReferenceMatrices


def test_1000g_frequency_retrieval():
    """Verify frequency retrieval for canonical AIM SNPs across 1000G super-populations."""
    freqs = BGAReferenceMatrices.get_allele_frequencies("rs2814778", ReferenceSystemEnum.ONE_THOUSAND_GENOMES_26)
    assert "EUR" in freqs
    assert "AFR" in freqs
    assert "EAS" in freqs

    # DARC rs2814778 ALT (C) frequency in AFR > 0.95, in EUR < 0.05
    ref_eur, alt_eur = freqs["EUR"]
    ref_afr, alt_afr = freqs["AFR"]
    assert alt_eur < 0.01
    assert alt_afr > 0.95


def test_gnomad_v4_frequency_retrieval():
    """Verify frequency retrieval for gnomAD v4.1 across 9 genetic ancestry groups."""
    freqs = BGAReferenceMatrices.get_allele_frequencies("rs1426654", ReferenceSystemEnum.GNOMAD_V4_9POP)
    assert len(freqs) >= 8
    assert "NFE" in freqs
    assert "FIN" in freqs
    assert "AFR" in freqs
    assert "ASJ" in freqs

    # SLC24A5 rs1426654 ALT (G) in NFE/FIN > 0.99, in AFR < 0.05
    ref_nfe, alt_nfe = freqs["NFE"]
    ref_afr, alt_afr = freqs["AFR"]
    assert alt_nfe > 0.99
    assert alt_afr < 0.05


def test_microhaplotype_frequency_retrieval():
    """Verify multiallelic microhaplotype frequencies sum to ~1.0."""
    mh_freqs = BGAReferenceMatrices.get_microhaplotype_frequencies("mh01KK-001", ReferenceSystemEnum.ONE_THOUSAND_GENOMES_26)
    assert "EUR" in mh_freqs
    assert "AFR" in mh_freqs

    for pop, haps in mh_freqs.items():
        total = sum(haps.values())
        assert abs(total - 1.0) < 1e-4
        assert len(haps) >= 4


def test_fallback_unmapped_locus():
    """Verify fallback frequency for locus not explicitly in catalog."""
    freqs = BGAReferenceMatrices.get_allele_frequencies("rs999999999", ReferenceSystemEnum.ONE_THOUSAND_GENOMES_26)
    assert "EUR" in freqs
    assert freqs["EUR"] == (0.50, 0.50)
