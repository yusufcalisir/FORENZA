"""
Unit Tests for AIM Panel Registry & Microhaplotype Definitions.
"""

import pytest
from backend.node.services.forensic.genomics.bga.schemas import AIMPanelTypeEnum
from backend.node.services.forensic.genomics.bga.panel_registry import AIMPanelRegistry


def test_kidd_55_locus_retrieval():
    """Verify retrieval and attributes of canonical Kidd 55-AIM loci."""
    darc = AIMPanelRegistry.get_locus("rs2814778")
    assert darc is not None
    assert darc.chromosome == "1"
    assert darc.ref_allele == "T"
    assert darc.alt_allele == "C"
    assert darc.gene_symbol == "DARC/ACKR1"
    assert darc.informativeness_in is not None
    assert darc.informativeness_in > 0.60
    assert AIMPanelTypeEnum.KIDD_55 in darc.panel_memberships


def test_phenotypic_pleiotropic_loci():
    """Verify pleiotropic overlap loci with HIrisPlex-S."""
    herc2 = AIMPanelRegistry.get_locus("rs12913832")
    assert herc2 is not None
    assert herc2.is_phenotypic_pleiotropic is True
    assert AIMPanelTypeEnum.VISAGE_BASIC_153 in herc2.panel_memberships

    slc24a5 = AIMPanelRegistry.get_locus("rs1426654")
    assert slc24a5 is not None
    assert slc24a5.is_phenotypic_pleiotropic is True


def test_microhaplotype_catalog():
    """Verify forensic microhaplotype definitions and span bounds (<300 bp)."""
    mhs = AIMPanelRegistry.get_all_microhaplotypes()
    assert len(mhs) >= 5

    mh1 = AIMPanelRegistry.get_microhaplotype("mh01KK-001")
    assert mh1 is not None
    assert mh1.chromosome == "1"
    assert mh1.length_bp < 300
    assert len(mh1.constituent_snps) == 3
    assert "rs10751448" in mh1.constituent_snps
    assert len(mh1.known_haplotypes) >= 4


def test_get_panel_loci_filtering():
    """Verify panel-specific filtering logic."""
    kidd_loci = AIMPanelRegistry.get_panel_loci(AIMPanelTypeEnum.KIDD_55)
    assert len(kidd_loci) >= 50

    custom_loci = AIMPanelRegistry.get_panel_loci(AIMPanelTypeEnum.CUSTOM)
    assert len(custom_loci) >= len(kidd_loci)
