"""
Certified Multi-Omic Golden Standard Reference Vectors for BGA and HIrisPlex-S.

Provides ground-truth standard reference profiles across global reference individuals:
- VECTOR_BGA_01: NA12878 / HG001 (CEU European)
- VECTOR_BGA_02: NA19240 (YRI African)
- VECTOR_BGA_03: NA18507 / HG005 (CHB East Asian)
- VECTOR_BGA_04: HG002 / NA24385 (Ashkenazi Jewish / Middle Eastern)
- VECTOR_BGA_05: Tri-Racial Admixed Standard (EUR/AFR/AMR)
"""

from typing import Dict, List
from backend.node.services.forensic.genomics.bga.schemas import (
    IngestedBGASample,
    PlatformFormatEnum,
    AIMPanelTypeEnum,
    GenotypeCall
)


class BGAGoldenVectors:
    """Library of globally standardized forensic reference individuals."""

    @classmethod
    def get_vector_01_na12878_ceu(cls) -> IngestedBGASample:
        """NA12878 / HG001 CEU European Golden Vector."""
        genotypes = {
            "rs2814778": GenotypeCall(locus_id="rs2814778", allele_1="T", allele_2="T", is_heterozygous=False, dosage_alt=0.0),
            "rs1426654": GenotypeCall(locus_id="rs1426654", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0),
            "rs16891982": GenotypeCall(locus_id="rs16891982", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0),
            "rs12913832": GenotypeCall(locus_id="rs12913832", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0),
            "rs1800407": GenotypeCall(locus_id="rs1800407", allele_1="C", allele_2="C", is_heterozygous=False, dosage_alt=0.0),
            "rs3827760": GenotypeCall(locus_id="rs3827760", allele_1="A", allele_2="A", is_heterozygous=False, dosage_alt=0.0),
            "rs17822931": GenotypeCall(locus_id="rs17822931", allele_1="C", allele_2="C", is_heterozygous=False, dosage_alt=0.0)
        }
        return IngestedBGASample(
            sample_id="VECTOR_BGA_01_NA12878",
            detected_platform=PlatformFormatEnum.AMPLISEQ_TSV,
            primary_panel=AIMPanelTypeEnum.VISAGE_BASIC_153,
            genotypes=genotypes,
            total_loci_assayed=len(genotypes)
        )

    @classmethod
    def get_vector_02_na19240_yri(cls) -> IngestedBGASample:
        """NA19240 YRI Sub-Saharan African Golden Vector."""
        genotypes = {
            "rs2814778": GenotypeCall(locus_id="rs2814778", allele_1="C", allele_2="C", is_heterozygous=False, dosage_alt=2.0),
            "rs1426654": GenotypeCall(locus_id="rs1426654", allele_1="A", allele_2="A", is_heterozygous=False, dosage_alt=0.0),
            "rs16891982": GenotypeCall(locus_id="rs16891982", allele_1="C", allele_2="C", is_heterozygous=False, dosage_alt=0.0),
            "rs12913832": GenotypeCall(locus_id="rs12913832", allele_1="A", allele_2="A", is_heterozygous=False, dosage_alt=0.0),
            "rs73885319": GenotypeCall(locus_id="rs73885319", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0),
            "rs3827760": GenotypeCall(locus_id="rs3827760", allele_1="A", allele_2="A", is_heterozygous=False, dosage_alt=0.0)
        }
        return IngestedBGASample(
            sample_id="VECTOR_BGA_02_NA19240",
            detected_platform=PlatformFormatEnum.AMPLISEQ_TSV,
            primary_panel=AIMPanelTypeEnum.VISAGE_BASIC_153,
            genotypes=genotypes,
            total_loci_assayed=len(genotypes)
        )

    @classmethod
    def get_vector_03_na18507_chb(cls) -> IngestedBGASample:
        """NA18507 / HG005 CHB East Asian Golden Vector."""
        genotypes = {
            "rs2814778": GenotypeCall(locus_id="rs2814778", allele_1="T", allele_2="T", is_heterozygous=False, dosage_alt=0.0),
            "rs1426654": GenotypeCall(locus_id="rs1426654", allele_1="A", allele_2="A", is_heterozygous=False, dosage_alt=0.0),
            "rs16891982": GenotypeCall(locus_id="rs16891982", allele_1="C", allele_2="C", is_heterozygous=False, dosage_alt=0.0),
            "rs12913832": GenotypeCall(locus_id="rs12913832", allele_1="A", allele_2="A", is_heterozygous=False, dosage_alt=0.0),
            "rs3827760": GenotypeCall(locus_id="rs3827760", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0),
            "rs17822931": GenotypeCall(locus_id="rs17822931", allele_1="T", allele_2="T", is_heterozygous=False, dosage_alt=2.0),
            "rs671": GenotypeCall(locus_id="rs671", allele_1="A", allele_2="A", is_heterozygous=False, dosage_alt=2.0)
        }
        return IngestedBGASample(
            sample_id="VECTOR_BGA_03_NA18507",
            detected_platform=PlatformFormatEnum.AMPLISEQ_TSV,
            primary_panel=AIMPanelTypeEnum.VISAGE_BASIC_153,
            genotypes=genotypes,
            total_loci_assayed=len(genotypes)
        )

    @classmethod
    def get_vector_04_hg002_aj(cls) -> IngestedBGASample:
        """HG002 / NA24385 Ashkenazi Jewish Reference Vector."""
        genotypes = {
            "rs2814778": GenotypeCall(locus_id="rs2814778", allele_1="T", allele_2="T", is_heterozygous=False, dosage_alt=0.0),
            "rs1426654": GenotypeCall(locus_id="rs1426654", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0),
            "rs16891982": GenotypeCall(locus_id="rs16891982", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0),
            "rs12913832": GenotypeCall(locus_id="rs12913832", allele_1="A", allele_2="G", is_heterozygous=True, dosage_alt=1.0)
        }
        return IngestedBGASample(
            sample_id="VECTOR_BGA_04_HG002",
            detected_platform=PlatformFormatEnum.AMPLISEQ_TSV,
            primary_panel=AIMPanelTypeEnum.KIDD_55,
            genotypes=genotypes,
            total_loci_assayed=len(genotypes)
        )

    @classmethod
    def get_vector_05_admixed_tri_racial(cls) -> IngestedBGASample:
        """Synthetic Tri-Racial Admixed Reference (EUR / AFR / AMR)."""
        genotypes = {
            "rs2814778": GenotypeCall(locus_id="rs2814778", allele_1="T", allele_2="C", is_heterozygous=True, dosage_alt=1.0),
            "rs1426654": GenotypeCall(locus_id="rs1426654", allele_1="A", allele_2="G", is_heterozygous=True, dosage_alt=1.0),
            "rs16891982": GenotypeCall(locus_id="rs16891982", allele_1="C", allele_2="G", is_heterozygous=True, dosage_alt=1.0),
            "rs3827760": GenotypeCall(locus_id="rs3827760", allele_1="A", allele_2="G", is_heterozygous=True, dosage_alt=1.0)
        }
        return IngestedBGASample(
            sample_id="VECTOR_BGA_05_ADMIXED",
            detected_platform=PlatformFormatEnum.AMPLISEQ_TSV,
            primary_panel=AIMPanelTypeEnum.KIDD_55,
            genotypes=genotypes,
            total_loci_assayed=len(genotypes)
        )
