"""
Unit Tests for Rosenberg Informativeness (In) and Wright's Fst Calculation.
"""

import pytest
from backend.node.services.forensic.genomics.bga.schemas import ReferenceSystemEnum
from backend.node.services.forensic.genomics.bga.informativeness_engine import BGAInformativenessEngine


def test_darc_rosenberg_in_and_fst():
    """Verify high informativeness and Fst for DARC rs2814778."""
    rep = BGAInformativenessEngine.compute_rosenberg_in("rs2814778", ReferenceSystemEnum.ONE_THOUSAND_GENOMES_26)
    assert rep.locus_id == "rs2814778"
    assert rep.rosenberg_in_nats > 0.30
    assert rep.rosenberg_in_bits > 0.40
    assert rep.wright_fst > 0.50
    assert rep.mean_alt_frequency > 0.10


def test_slc24a5_rosenberg_in():
    """Verify high informativeness for SLC24A5 rs1426654."""
    rep = BGAInformativenessEngine.compute_rosenberg_in("rs1426654", ReferenceSystemEnum.ONE_THOUSAND_GENOMES_26)
    assert rep.rosenberg_in_nats > 0.30
    assert rep.wright_fst > 0.45


def test_pairwise_fst_symmetry():
    """Verify pairwise Fst is symmetric and diagonal is zero."""
    fst_eur_afr = BGAInformativenessEngine.compute_pairwise_fst("rs2814778", "EUR", "AFR")
    fst_afr_eur = BGAInformativenessEngine.compute_pairwise_fst("rs2814778", "AFR", "EUR")
    fst_eur_eur = BGAInformativenessEngine.compute_pairwise_fst("rs2814778", "EUR", "EUR")

    assert abs(fst_eur_afr - fst_afr_eur) < 1e-7
    assert fst_eur_eur == 0.0
    assert fst_eur_afr > 0.80


def test_multi_locus_pairwise_matrix():
    """Verify multi-locus pairwise Fst matrix across continental populations."""
    loci = ["rs2814778", "rs1426654", "rs16891982", "rs3827760"]
    matrix = BGAInformativenessEngine.compute_multi_locus_pairwise_fst_matrix(loci)

    assert "EUR" in matrix
    assert "AFR" in matrix
    assert "EAS" in matrix
    assert matrix["EUR"]["EUR"] == 0.0
    assert matrix["EUR"]["AFR"] > 0.40
    assert matrix["EUR"]["AFR"] == matrix["AFR"]["EUR"]
