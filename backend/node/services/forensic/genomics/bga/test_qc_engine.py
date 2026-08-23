"""
Unit Tests for BGA Quality Control Engine.
"""

import pytest
from backend.node.services.forensic.genomics.bga.schemas import (
    IngestedBGASample,
    PlatformFormatEnum,
    AIMPanelTypeEnum,
    QCStatusEnum,
    GenotypeCall
)
from backend.node.services.forensic.genomics.bga.panel_registry import AIMPanelRegistry
from backend.node.services.forensic.genomics.bga.qc_engine import BGAQualityControlEngine


def test_high_quality_sample_qc_pass():
    """Verify pristine sample passes QC with 100% call rate."""
    kidd_loci = AIMPanelRegistry.get_panel_loci(AIMPanelTypeEnum.KIDD_55)
    genotypes = {}
    for i, loc in enumerate(kidd_loci):
        is_het = (i % 4 == 0)
        a1 = loc.ref_allele
        a2 = loc.alt_allele if is_het else loc.ref_allele
        genotypes[loc.rs_id] = GenotypeCall(
            locus_id=loc.rs_id,
            allele_1=a1,
            allele_2=a2,
            is_heterozygous=is_het,
            dosage_alt=1.0 if is_het else 0.0
        )

    sample = IngestedBGASample(
        sample_id="PRISTINE_TEST",
        detected_platform=PlatformFormatEnum.AMPLISEQ_TSV,
        primary_panel=AIMPanelTypeEnum.KIDD_55,
        genotypes=genotypes,
        total_loci_assayed=len(kidd_loci)
    )

    qc_sample = BGAQualityControlEngine.evaluate_sample(sample)
    assert qc_sample.qc_status == QCStatusEnum.PASS
    assert qc_sample.call_rate >= 95.0
    assert qc_sample.heterozygosity_rate > 15.0
    assert qc_sample.heterozygosity_rate < 35.0


def test_low_call_rate_qc_fail():
    """Verify degraded sample with <80% call rate fails QC gate."""
    genotypes = {
        "rs2814778": GenotypeCall(locus_id="rs2814778", allele_1="T", allele_2="C", is_heterozygous=True, dosage_alt=1.0),
        "rs1426654": GenotypeCall(locus_id="rs1426654", allele_1="A", allele_2="A", is_heterozygous=False, dosage_alt=0.0)
    }
    sample = IngestedBGASample(
        sample_id="DEGRADED_TEST",
        detected_platform=PlatformFormatEnum.SNAPSHOT_CE_TABLE,
        primary_panel=AIMPanelTypeEnum.KIDD_55,
        genotypes=genotypes,
        total_loci_assayed=55
    )
    qc_sample = BGAQualityControlEngine.evaluate_sample(sample)
    assert qc_sample.qc_status == QCStatusEnum.FAIL
    assert qc_sample.call_rate < 10.0
    assert any("Severely depleted call rate" in f for f in qc_sample.qc_flags)


def test_missing_logit_penalty_calculation():
    """Verify missing penalty lambda scaling factor."""
    sample_full = IngestedBGASample(
        sample_id="FULL",
        detected_platform=PlatformFormatEnum.AMPLISEQ_TSV,
        primary_panel=AIMPanelTypeEnum.KIDD_55,
        call_rate=100.0
    )
    assert BGAQualityControlEngine.compute_missing_logit_penalty(sample_full) == 0.0

    sample_half = IngestedBGASample(
        sample_id="HALF",
        detected_platform=PlatformFormatEnum.AMPLISEQ_TSV,
        primary_panel=AIMPanelTypeEnum.KIDD_55,
        call_rate=50.0
    )
    # (1.0 - 0.5) * 0.35 = 0.175
    assert BGAQualityControlEngine.compute_missing_logit_penalty(sample_half) == 0.175
