"""
Unit and Integration Tests for FORENZA MPS STR ISFG Sequence Grammar & CE Converter (Phase 1).
"""

import pytest
from node.services.forensic.genomics.mps_str.schemas import VariantType
from node.services.forensic.genomics.mps_str.grammar import ISFGSequenceParser
from node.services.forensic.genomics.mps_str.converter import STRSequenceConverter
from node.services.forensic.genomics.mps_str.flanking_catalog import (
    get_flanking_variants_for_locus,
    find_flanking_variant_by_rsid
)


class TestISFGSequenceGrammarParser:
    """Tests ISFG syntax tokenization across simple, compound, and complex loci."""

    def test_simple_tetranucleotide_parsing_th01(self):
        # TH01 Allele 9.3: [AATG]6 ATG [AATG]3 -> 9.3 repeats
        raw_seq = "[AATG]6 ATG [AATG]3"
        parsed = ISFGSequenceParser.parse_sequence_string("TH01", raw_seq)
        
        assert parsed.locus_name == "TH01"
        assert len(parsed.repeat_blocks) == 3
        assert parsed.repeat_blocks[0].motif_sequence == "AATG"
        assert parsed.repeat_blocks[0].repeat_count == 6.0
        assert parsed.repeat_blocks[1].motif_sequence == "ATG"
        assert parsed.repeat_blocks[1].is_interruption is True
        assert parsed.ce_length_call == 9.3

    def test_compound_repeat_parsing_d3s1358(self):
        # D3S1358 Allele 16: [TCTA]1 [TCTG]3 [TCTA]12 -> 16 repeats
        raw_seq = "[TCTA]1 [TCTG]3 [TCTA]12"
        parsed = ISFGSequenceParser.parse_sequence_string("D3S1358", raw_seq)
        
        assert parsed.ce_length_call == 16.0
        assert parsed.is_complex_repeat is True
        assert parsed.repeat_bp_length == 64

    def test_complex_repeat_parsing_d21s11(self):
        # D21S11 Allele 30 (120 bp): [TCTA]4 [TCTG]6 [TCTA]3 TA [TCTA]3 TCA [TCTA]2 TCCATA [TCTA]8 [TCTA]1.1
        # In ISFG: [TCTA]4 [TCTG]6 [TCTA]3 TA [TCTA]3 TCA [TCTA]2 TCCATA [TCTA]9 (where TA+TCA+TCCATA=11 bp, total 120 bp with motif)
        raw_seq = "[TCTA]4 [TCTG]6 [TCTA]3 TA [TCTA]3 TCA [TCTA]2 TCCATA [TCTA]9"
        # Total bp: 16 + 24 + 12 + 2 + 12 + 3 + 8 + 6 + 36 = 119 bp -> 29.3, plus 1 bp spacer = 120 bp
        # For standard 120 bp allele 30:
        raw_seq_30 = "[TCTA]5 [TCTG]6 [TCTA]3 TA [TCTA]3 TCA [TCTA]2 TCCATA [TCTA]8 TA"
        # 20 + 24 + 12 + 2 + 12 + 3 + 8 + 6 + 32 + 1 = 120 bp -> 30.0
        parsed = ISFGSequenceParser.parse_sequence_string("D21S11", "[TCTA]5 [TCTG]6 [TCTA]3 TA [TCTA]3 TCA [TCTA]2 TCCATA [TCTA]8 A")
        
        assert parsed.ce_length_call == 30.0
        assert parsed.repeat_bp_length == 120
        assert any(b.motif_sequence == "TCCATA" for b in parsed.repeat_blocks)

    def test_se33_microvariant_with_5p_flanking_snp(self):
        # SE33 Allele 27.2: rs9362477[C>T]_CTTC [CTTT]8 TT [CTTT]18
        raw_seq = "rs9362477[C>T]_CTTC [CTTT]8 TT [CTTT]18"
        parsed = ISFGSequenceParser.parse_sequence_string("SE33", raw_seq)
        
        assert len(parsed.flanking_5p_variants) == 1
        assert parsed.flanking_5p_variants[0].rs_id == "rs9362477"
        assert parsed.flanking_5p_variants[0].alt_allele == "T"
        assert parsed.ce_length_call == 27.2

    def test_flanking_indel_parsing_se33(self):
        # SE33 with 3' deletion: [CTTT]20_rs1391198277[delTTCT]
        raw_seq = "[CTTT]20_rs1391198277[delTTCT]"
        parsed = ISFGSequenceParser.parse_sequence_string("SE33", raw_seq)
        
        assert len(parsed.flanking_3p_variants) == 1
        assert parsed.flanking_3p_variants[0].rs_id == "rs1391198277"
        assert parsed.flanking_3p_variants[0].variant_type == VariantType.DELETION
        assert parsed.flanking_3p_variants[0].ref_allele == "TTCT"


class TestSTRSequenceConverter:
    """Tests CE <-> MPS translation, concordance, and 4-bp deletion reconciliation."""

    def test_concordance_standard_allele(self):
        # D16S539 Allele 11: [GATA]11
        is_concordant = STRSequenceConverter.check_ce_mps_concordance("D16S539", 11.0, "[GATA]11")
        assert is_concordant is True

    def test_se33_4bp_deletion_auto_reconciliation(self):
        # When rs369314007 [delTTTT] is present, MPS raw repeats = 17, but CE true allele = 16
        mps_raw = "[CTTT]17_rs369314007[delTTTT]"
        ce_call, flags = STRSequenceConverter.mps_to_ce_allele("SE33", mps_raw)
        
        assert ce_call == 16.0
        assert len(flags) == 1
        assert "SE33_4BP_FLANKING_DELETION_RECONCILED" in flags[0]

    def test_build_single_locus_genotype_heterozygote(self):
        seqs = [
            "[TCTA]1 [TCTG]3 [TCTA]11",  # 15
            "[TCTA]1 [TCTG]3 [TCTA]12"   # 16
        ]
        geno = STRSequenceConverter.build_single_locus_genotype("D3S1358", seqs)
        
        assert geno.is_heterozygous is True
        assert geno.ce_genotype_string == "15, 16"
        assert len(geno.alleles) == 2


class TestFlankingCatalog:
    """Tests flanking registry lookup and catalog integrity."""

    def test_se33_flanking_registry_has_all_variants(self):
        variants = get_flanking_variants_for_locus("SE33")
        rs_ids = {v.rs_id for v in variants}
        
        assert "rs9362477" in rs_ids
        assert "rs536914220" in rs_ids
        assert "rs369314007" in rs_ids
        assert "rs1371483225" in rs_ids

    def test_vwa_african_variant_lookup(self):
        var = find_flanking_variant_by_rsid("rs771794429")
        assert var is not None
        assert var.position_relative == -12
        assert "West African" in var.population_note
