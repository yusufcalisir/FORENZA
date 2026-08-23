"""
Unit and Integration Tests for FORENZA SE33 Hyper-Polymorphic Engine (Phase 3).
Validates Golden Vectors VECTOR_MPS_01 and VECTOR_MPS_02.
"""

import pytest
from node.services.forensic.genomics.mps_str.se33_engine import (
    SE33HyperPolymorphicEngine,
    SE33SizeClass,
    SE33GenotypeAnalysisReport
)


class TestSE33HyperPolymorphicEngine:
    """Tests SE33 bimodal structure, flanking SNPs, and 4-bp deletion reconciliation."""

    def test_vector_mps_01_se33_isoallele_information_gain(self):
        # VECTOR_MPS_01: Caucasian SE33 18 / 27.2
        # Allele A: CTTC [CTTT]17_rs9362477[C>T] (18)
        # Allele B: CTTC [CTTT]10 TT [CTTT]16_rs1277875566[T>C] (27.2)
        seqs = [
            "CTTC [CTTT]17_rs9362477[C>T]",
            "CTTC [CTTT]10 TT [CTTT]16_rs1277875566[T>C]"
        ]
        report = SE33HyperPolymorphicEngine.analyze_se33_genotype(seqs, "CAUCASIAN")
        
        assert report.ce_genotype == "18, 27.2"
        assert report.alleles[0].size_class == SE33SizeClass.SMALL_INTEGER
        assert report.alleles[1].size_class == SE33SizeClass.LARGE_MICROVARIANT
        
        # Flanking variants detected
        assert len(report.alleles[0].flanking_variants) == 1
        assert report.alleles[0].flanking_variants[0].rs_id == "rs9362477"
        assert report.alleles[1].flanking_variants[0].rs_id == "rs1277875566"
        
        # Information gain boost: LR_mps > LR_ce
        assert report.mps_single_locus_lr > report.ce_single_locus_lr
        assert report.information_gain_ratio >= 20.0  # Significant LR gain from sequence resolution

    def test_vector_mps_02_se33_4bp_flanking_deletion_reconciliation(self):
        # VECTOR_MPS_02: 4-bp flanking deletion discordance resolver
        # CE true alleles: 16 / 23.2
        # MPS raw reads: 17 / 24.2 with rs369314007 [delTTTT] and rs1371483225 [delTCTT]
        seqs = [
            "[CTTT]17_rs369314007[delTTTT]",
            "[CTTT]12 TT [CTTT]12_rs1371483225[delTCTT]"
        ]
        report = SE33HyperPolymorphicEngine.analyze_se33_genotype(seqs, "GLOBAL_COMPOSITE")
        
        # Automatically reconciled back to official CE calls
        assert report.ce_genotype == "16, 23.2"
        assert report.alleles[0].is_4bp_deletion_reconciled is True
        assert report.alleles[1].is_4bp_deletion_reconciled is True
        assert report.is_fully_concordant is True
        assert any("rs369314007" in note for note in report.quality_assurance_notes)

    def test_se33_homozygote_analysis(self):
        seqs = ["[CTTT]18", "[CTTT]18"]
        report = SE33HyperPolymorphicEngine.analyze_se33_genotype(seqs, "GLOBAL_COMPOSITE")
        
        assert report.ce_genotype == "18, 18"
        assert report.mps_single_locus_lr > 100.0
