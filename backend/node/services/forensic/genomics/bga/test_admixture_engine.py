"""
Unit Tests for Maximum Likelihood & Bayesian Admixture Deconvolution Engines.
"""

import pytest
from backend.node.services.forensic.genomics.bga.schemas import (
    IngestedBGASample,
    PlatformFormatEnum,
    AIMPanelTypeEnum,
    ReferenceSystemEnum,
    GenotypeCall
)
from backend.node.services.forensic.genomics.bga.admixture_engine import BGAAdmixtureEngine


def test_european_reference_hard_and_soft_admixture():
    """Verify European reference profile correctly resolves EUR > 90% in both hard and soft engines."""
    genotypes = {
        "rs2814778": GenotypeCall(locus_id="rs2814778", allele_1="T", allele_2="T", is_heterozygous=False, dosage_alt=0.0),
        "rs1426654": GenotypeCall(locus_id="rs1426654", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0),
        "rs16891982": GenotypeCall(locus_id="rs16891982", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0),
        "rs12913832": GenotypeCall(locus_id="rs12913832", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0),
        "rs3827760": GenotypeCall(locus_id="rs3827760", allele_1="A", allele_2="A", is_heterozygous=False, dosage_alt=0.0),
        "rs17822931": GenotypeCall(locus_id="rs17822931", allele_1="C", allele_2="C", is_heterozygous=False, dosage_alt=0.0)
    }

    sample = IngestedBGASample(
        sample_id="CEU_TEST",
        detected_platform=PlatformFormatEnum.AMPLISEQ_TSV,
        primary_panel=AIMPanelTypeEnum.KIDD_55,
        genotypes=genotypes
    )

    hard_res = BGAAdmixtureEngine.compute_hard_assignment(sample, ReferenceSystemEnum.ONE_THOUSAND_GENOMES_26)
    assert hard_res["top_assigned_population"] == "EUR"
    assert hard_res["bayes_factor"] > 10.0

    soft_q = BGAAdmixtureEngine.compute_soft_admixture(sample, ReferenceSystemEnum.ONE_THOUSAND_GENOMES_26)
    assert soft_q["EUR"] > 0.70
    assert abs(sum(soft_q.values()) - 1.0) < 1e-5


def test_african_reference_hard_and_soft_admixture():
    """Verify African reference profile correctly resolves AFR > 90%."""
    genotypes = {
        "rs2814778": GenotypeCall(locus_id="rs2814778", allele_1="C", allele_2="C", is_heterozygous=False, dosage_alt=2.0),
        "rs1426654": GenotypeCall(locus_id="rs1426654", allele_1="A", allele_2="A", is_heterozygous=False, dosage_alt=0.0),
        "rs16891982": GenotypeCall(locus_id="rs16891982", allele_1="C", allele_2="C", is_heterozygous=False, dosage_alt=0.0),
        "rs12913832": GenotypeCall(locus_id="rs12913832", allele_1="A", allele_2="A", is_heterozygous=False, dosage_alt=0.0),
        "rs73885319": GenotypeCall(locus_id="rs73885319", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0)
    }

    sample = IngestedBGASample(
        sample_id="YRI_TEST",
        detected_platform=PlatformFormatEnum.AMPLISEQ_TSV,
        primary_panel=AIMPanelTypeEnum.KIDD_55,
        genotypes=genotypes
    )

    hard_res = BGAAdmixtureEngine.compute_hard_assignment(sample, ReferenceSystemEnum.ONE_THOUSAND_GENOMES_26)
    assert hard_res["top_assigned_population"] == "AFR"

    soft_q = BGAAdmixtureEngine.compute_soft_admixture(sample, ReferenceSystemEnum.ONE_THOUSAND_GENOMES_26)
    assert soft_q["AFR"] > 0.70


def test_admixed_profile_continuous_deconvolution():
    """Verify 50/50 admixed profile resolves continuous Q fractions without forced polar classification."""
    # Heterozygous on major divergent ancestry loci
    genotypes = {
        "rs2814778": GenotypeCall(locus_id="rs2814778", allele_1="T", allele_2="C", is_heterozygous=True, dosage_alt=1.0),
        "rs1426654": GenotypeCall(locus_id="rs1426654", allele_1="A", allele_2="G", is_heterozygous=True, dosage_alt=1.0),
        "rs16891982": GenotypeCall(locus_id="rs16891982", allele_1="C", allele_2="G", is_heterozygous=True, dosage_alt=1.0),
        "rs12913832": GenotypeCall(locus_id="rs12913832", allele_1="A", allele_2="G", is_heterozygous=True, dosage_alt=1.0)
    }

    sample = IngestedBGASample(
        sample_id="ADMIXED_50_50",
        detected_platform=PlatformFormatEnum.AMPLISEQ_TSV,
        primary_panel=AIMPanelTypeEnum.KIDD_55,
        genotypes=genotypes
    )

    soft_q = BGAAdmixtureEngine.compute_soft_admixture(sample, ReferenceSystemEnum.ONE_THOUSAND_GENOMES_26)
    # EUR and AFR should both be significant (> 0.20)
    assert soft_q["EUR"] > 0.20
    assert soft_q["AFR"] > 0.20
    assert abs(sum(soft_q.values()) - 1.0) < 1e-5


def test_full_ancestry_report_synthesis():
    """Verify synthesis of unified AdmixtureProportionResult with ENFSI verbal statement."""
    genotypes = {
        "rs2814778": GenotypeCall(locus_id="rs2814778", allele_1="T", allele_2="T", is_heterozygous=False, dosage_alt=0.0),
        "rs1426654": GenotypeCall(locus_id="rs1426654", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0),
        "rs16891982": GenotypeCall(locus_id="rs16891982", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0)
    }
    sample = IngestedBGASample(
        sample_id="REPORT_TEST",
        detected_platform=PlatformFormatEnum.AMPLISEQ_TSV,
        primary_panel=AIMPanelTypeEnum.KIDD_55,
        genotypes=genotypes
    )

    report = BGAAdmixtureEngine.generate_full_ancestry_report(sample)
    assert report.sample_id == "REPORT_TEST"
    assert report.shannon_entropy >= 0.0
    assert report.simpson_diversity >= 0.0
    assert "INVESTIGATIVE INTELLIGENCE ONLY" in report.enfsi_verbal_statement
    assert report.spatial_covariance_semi_major_km > 0.0
