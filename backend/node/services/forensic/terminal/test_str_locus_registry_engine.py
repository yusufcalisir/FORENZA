"""
Unit tests for 24-STR Locus Master Registry & Micro-Variant Engine
ISO/IEC 17025:2017 and SWGDAM 2020 Validation.
Derived from: research/str_24_locus_microvariants_research.md
"""

import pytest
import math
from backend.node.services.forensic.terminal.str_locus_registry_engine import (
    StrLocusRegistryEngine,
    STR_LOCUS_24_MASTER_REGISTRY,
    MICROVARIANT_MUTATIONAL_CATALOG,
    StrRepeatUnitClass,
    StrMotifClass,
    MicrovariantEtiologyClass,
)
from backend.node.services.forensic.terminal.dna_terminal_parser import STR_PANEL_24_CATALOG


class TestStrLocusMasterRegistry:
    """Test suite for 24-STR locus master catalog completeness and accuracy."""

    def test_24_loci_presence(self):
        """Verify all 24 standard loci plus sex markers are in the master registry."""
        expected_loci = [
            "D3S1358", "vWA", "FGA", "D8S1179", "D21S11", "D18S51",
            "D5S818", "D13S317", "D7S820", "D16S539", "CSF1PO", "TH01",
            "TPOX", "D1S1656", "D2S441", "D2S1338", "D10S1248", "D12S391",
            "D19S433", "D22S1045", "SE33", "Penta D", "Penta E", "Amelogenin",
            "DYS391", "SRY"
        ]
        all_loci = StrLocusRegistryEngine.get_all_loci_names()
        for locus in expected_loci:
            assert locus in STR_LOCUS_24_MASTER_REGISTRY, f"Missing locus: {locus}"
            assert StrLocusRegistryEngine.is_valid_locus(locus)

    def test_fbi_codis_20_core_loci(self):
        """Verify the 20 FBI CODIS core loci are properly tagged."""
        codis_core = StrLocusRegistryEngine.get_codis_core_loci_names()
        assert len(codis_core) == 20
        assert "D3S1358" in codis_core
        assert "SE33" not in codis_core  # SE33 is ESS / European Standard
        assert "Penta D" not in codis_core

    def test_locus_exact_research_metadata(self):
        """Verify specific research constants for key loci."""
        # D3S1358
        d3 = StrLocusRegistryEngine.get_locus_metadata("D3S1358")
        assert d3 is not None
        assert d3.cytogenetic_band == "3p21.31"
        assert d3.repeat_unit_class == StrRepeatUnitClass.TETRANUCLEOTIDE
        assert d3.repeat_unit_size_bp == 4
        assert d3.max_reverse_stutter_ratio == 0.110
        assert d3.germline_mutation_rate_10k == 1.20
        assert d3.stepwise_mutation_r == 0.850

        # SE33 (Hypervariable)
        se33 = StrLocusRegistryEngine.get_locus_metadata("SE33")
        assert se33 is not None
        assert se33.cytogenetic_band == "6q14.2"
        assert se33.motif_class == StrMotifClass.COMPLEX
        assert se33.max_reverse_stutter_ratio == 0.160
        assert se33.germline_mutation_rate_10k == 6.40
        assert se33.stepwise_mutation_r == 0.700

        # TH01
        th01 = StrLocusRegistryEngine.get_locus_metadata("TH01")
        assert th01 is not None
        assert th01.cytogenetic_band == "11p15.5"
        assert th01.max_reverse_stutter_ratio == 0.050
        assert th01.germline_mutation_rate_10k == 0.60
        assert "9.3" in th01.documented_microvariants

        # D22S1045 (Trinucleotide)
        d22 = StrLocusRegistryEngine.get_locus_metadata("D22S1045")
        assert d22 is not None
        assert d22.repeat_unit_class == StrRepeatUnitClass.TRINUCLEOTIDE
        assert d22.repeat_unit_size_bp == 3


class TestMicrovariantMutationalCatalog:
    """Test suite for fractional micro-variant catalog and mutational etiology."""

    def test_microvariant_detection(self):
        """Verify is_microvariant accurately identifies fractional alleles."""
        assert StrLocusRegistryEngine.is_microvariant("9.3") is True
        assert StrLocusRegistryEngine.is_microvariant("28.2") is True
        assert StrLocusRegistryEngine.is_microvariant("14.3") is True
        assert StrLocusRegistryEngine.is_microvariant("14.1") is True
        assert StrLocusRegistryEngine.is_microvariant("10.4") is True
        assert StrLocusRegistryEngine.is_microvariant("15") is False
        assert StrLocusRegistryEngine.is_microvariant("16.0") is False
        assert StrLocusRegistryEngine.is_microvariant("X") is False
        assert StrLocusRegistryEngine.is_microvariant("Y") is False

    def test_th01_9_3_microvariant(self):
        """Verify TH01 9.3 single-base deletion etiology and sequence representation."""
        mv = StrLocusRegistryEngine.get_microvariant_details("TH01", "9.3")
        assert mv is not None
        assert mv.fractional_allele == "9.3"
        assert mv.integer_base_repeat == 9
        assert mv.delta_bp == 3
        assert mv.alternate_delta_bp == -1
        assert mv.sequence_representation == "[AATG]6 ATG [AATG]3"
        assert mv.etiology_class == MicrovariantEtiologyClass.SINGLE_BASE_DELETION

    def test_fga_22_2_microvariant(self):
        """Verify FGA 22.2 dinucleotide deletion etiology."""
        mv = StrLocusRegistryEngine.get_microvariant_details("FGA", "22.2")
        assert mv is not None
        assert mv.fractional_allele == "22.2"
        assert mv.integer_base_repeat == 22
        assert mv.delta_bp == 2
        assert mv.etiology_class == MicrovariantEtiologyClass.DINUCLEOTIDE_INDEL

    def test_d21s11_31_2_microvariant(self):
        """Verify D21S11 31.2 internal TA invariant retention."""
        mv = StrLocusRegistryEngine.get_microvariant_details("D21S11", "31.2")
        assert mv is not None
        assert mv.fractional_allele == "31.2"
        assert mv.delta_bp == 2
        assert "TA" in mv.sequence_representation

    def test_d1s1656_17_3_microvariant(self):
        """Verify D1S1656 17.3 TCA linker inclusion."""
        mv = StrLocusRegistryEngine.get_microvariant_details("D1S1656", "17.3")
        assert mv is not None
        assert mv.fractional_allele == "17.3"
        assert mv.delta_bp == 3
        assert mv.alternate_delta_bp == -1
        assert "TCA" in mv.sequence_representation
        assert mv.etiology_class == MicrovariantEtiologyClass.TRINUCLEOTIDE_INSERTION

    def test_se33_28_2_microvariant(self):
        """Verify SE33 28.2 hypervariable AG dinucleotide frameshift."""
        mv = StrLocusRegistryEngine.get_microvariant_details("SE33", "28.2")
        assert mv is not None
        assert mv.fractional_allele == "28.2"
        assert mv.delta_bp == 2
        assert mv.etiology_class == MicrovariantEtiologyClass.COMPLEX_ARRAY_FRAMESHIFT

    def test_penta_d_2_2_microvariant(self):
        """Verify Penta D 2.2 residual pentanucleotide partial repeat."""
        mv = StrLocusRegistryEngine.get_microvariant_details("Penta D", "2.2")
        assert mv is not None
        assert mv.fractional_allele == "2.2"
        assert mv.delta_bp == 2
        assert mv.alternate_delta_bp == -3
        assert mv.etiology_class == MicrovariantEtiologyClass.PARTIAL_REPEAT_COLLAPSE

    def test_d22s1045_14_1_microvariant(self):
        """Verify D22S1045 14.1 trinucleotide single base A insertion."""
        mv = StrLocusRegistryEngine.get_microvariant_details("D22S1045", "14.1")
        assert mv is not None
        assert mv.fractional_allele == "14.1"
        assert mv.delta_bp == 1
        assert mv.alternate_delta_bp == -2
        assert mv.etiology_class == MicrovariantEtiologyClass.SINGLE_BASE_INSERTION


class TestBiocomputationalDynamics:
    """Test suite for Stepwise Mutation Model and CE sizing dynamics."""

    def test_smm_transition_probability_monotonicity(self):
        """Verify SMM probability decreases strictly with mutational step size."""
        # For D3S1358: 15 -> 16 (1 step) vs 15 -> 17 (2 steps) vs 15 -> 18 (3 steps)
        p_1step = StrLocusRegistryEngine.calculate_smm_transition_probability("D3S1358", 15.0, 16.0)
        p_2step = StrLocusRegistryEngine.calculate_smm_transition_probability("D3S1358", 15.0, 17.0)
        p_3step = StrLocusRegistryEngine.calculate_smm_transition_probability("D3S1358", 15.0, 18.0)

        assert p_1step > p_2step > p_3step > 0.0
        # Ratio of 2-step to 1-step must equal r = 0.850
        ratio = p_2step / p_1step
        assert pytest.approx(ratio, rel=1e-3) == 0.850

    def test_ce_allele_sizing_calculation(self):
        """Verify linear base-pair sizing calculation for regular and micro-variant alleles."""
        # D3S1358 (repeat_unit_size = 4): allele 15 with base_offset=67.0 -> 67 + 15*4 = 127.0 bp
        size_d3_15 = StrLocusRegistryEngine.calculate_allele_size_bp("D3S1358", "15", base_offset=67.0)
        assert size_d3_15 == 127.0

        # TH01 (repeat_unit_size = 4): allele 9 with base_offset=50.0 -> 50 + 9*4 = 86.0 bp
        size_th01_9 = StrLocusRegistryEngine.calculate_allele_size_bp("TH01", "9", base_offset=50.0)
        assert size_th01_9 == 86.0

        # TH01 9.3: 50 + 9*4 + 3 = 89.0 bp
        size_th01_93 = StrLocusRegistryEngine.calculate_allele_size_bp("TH01", "9.3", base_offset=50.0)
        assert size_th01_93 == 89.0

        # Amelogenin X (106 bp) and Y (112 bp)
        assert StrLocusRegistryEngine.calculate_allele_size_bp("Amelogenin", "X") == 106.0
        assert StrLocusRegistryEngine.calculate_allele_size_bp("Amelogenin", "Y") == 112.0

    def test_dna_terminal_parser_sync(self):
        """Verify STR_PANEL_24_CATALOG in dna_terminal_parser matches master registry."""
        for locus_name, meta in STR_LOCUS_24_MASTER_REGISTRY.items():
            assert locus_name in STR_PANEL_24_CATALOG
            parser_meta = STR_PANEL_24_CATALOG[locus_name]
            assert parser_meta.cytogenetic_band == meta.cytogenetic_band
            assert parser_meta.max_reverse_stutter_ratio == meta.max_reverse_stutter_ratio
            assert parser_meta.mutation_rate_10k == meta.germline_mutation_rate_10k
