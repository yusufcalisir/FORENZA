"""
Unit Tests for PCA SVD Projection and Orthogonal Procrustes 3D WGS84 Mapping.
"""

import pytest
from backend.node.services.forensic.genomics.bga.schemas import (
    IngestedBGASample,
    PlatformFormatEnum,
    AIMPanelTypeEnum,
    GenotypeCall
)
from backend.node.services.forensic.genomics.bga.pca_procrustes_engine import BGAPCAProcrustesEngine


def test_european_pca_projection():
    """Verify European reference genotype projects into Western Eurasian PC space and European WGS84 centroid."""
    genotypes = {
        "rs2814778": GenotypeCall(locus_id="rs2814778", allele_1="T", allele_2="T", is_heterozygous=False, dosage_alt=0.0),
        "rs1426654": GenotypeCall(locus_id="rs1426654", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0),
        "rs16891982": GenotypeCall(locus_id="rs16891982", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0),
        "rs12913832": GenotypeCall(locus_id="rs12913832", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0),
        "rs3827760": GenotypeCall(locus_id="rs3827760", allele_1="A", allele_2="A", is_heterozygous=False, dosage_alt=0.0)
    }

    sample = IngestedBGASample(
        sample_id="CEU_EURO_TEST",
        detected_platform=PlatformFormatEnum.AMPLISEQ_TSV,
        primary_panel=AIMPanelTypeEnum.KIDD_55,
        genotypes=genotypes
    )

    pca_res = BGAPCAProcrustesEngine.compute_pca_projection(sample)
    assert pca_res.pc1 < 0.0  # EUR negative PC1

    gis_res = BGAPCAProcrustesEngine.project_procrustes_wgs84(pca_res)
    assert gis_res.nearest_reference_population in ("EUR", "NFE", "MID")
    assert gis_res.centroid_latitude > 35.0
    assert gis_res.semi_major_axis_km > 0.0
    assert gis_res.semi_minor_axis_km > 0.0


def test_east_asian_pca_projection():
    """Verify East Asian reference genotype projects into positive PC2 space and East Asian centroid."""
    genotypes = {
        "rs2814778": GenotypeCall(locus_id="rs2814778", allele_1="T", allele_2="T", is_heterozygous=False, dosage_alt=0.0),
        "rs1426654": GenotypeCall(locus_id="rs1426654", allele_1="A", allele_2="A", is_heterozygous=False, dosage_alt=0.0),
        "rs3827760": GenotypeCall(locus_id="rs3827760", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0),
        "rs17822931": GenotypeCall(locus_id="rs17822931", allele_1="T", allele_2="T", is_heterozygous=False, dosage_alt=2.0),
        "rs671": GenotypeCall(locus_id="rs671", allele_1="A", allele_2="A", is_heterozygous=False, dosage_alt=2.0)
    }

    sample = IngestedBGASample(
        sample_id="CHB_EAS_TEST",
        detected_platform=PlatformFormatEnum.AMPLISEQ_TSV,
        primary_panel=AIMPanelTypeEnum.KIDD_55,
        genotypes=genotypes
    )

    pca_res = BGAPCAProcrustesEngine.compute_pca_projection(sample)
    assert pca_res.pc2 > 0.0  # EAS positive PC2

    gis_res = BGAPCAProcrustesEngine.project_procrustes_wgs84(pca_res)
    assert gis_res.nearest_reference_population in ("EAS", "AMR")
    assert gis_res.centroid_longitude > 50.0
