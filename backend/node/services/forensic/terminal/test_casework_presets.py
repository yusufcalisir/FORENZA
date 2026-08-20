"""
FORENZA: Unit Tests for Certified Reference Standards & Multi-Format Exporter Engine
Validates all 5 certified global reference standards (NIST SRM 2391d, NA12878 CEU,
HG002 AJ, NA19240 YRI, NA18507 CHB), 100% concordance checks via ForensicMultiOmicValidator,
and export roundtrips (CODIS CMF 3.2 XML, ISO 17025 LIMS JSON, GeneMapper CSV).

Derived verbatim from research specifications:
- research/dna_snp_terminal_research.md
- research/certified_reference_standards_gold_vectors_research.md
Compliance: ISO/IEC 17025:2017 • FBI CODIS NDIS v3.2/v4.0 • SWGDAM 2020 Guidelines
"""

import json
import pytest
from xml.etree import ElementTree as ET

from .casework_presets import (
    CaseworkPresetsEngine,
    CaseworkPresetExporter,
    ForensicMultiOmicValidator,
    GOLDEN_CASEWORK_PRESETS,
    CERTIFIED_GLOBAL_REFERENCE_PRESETS,
    PRESET_NIST_SRM_2391D,
    PRESET_NA12878_CEU,
    PRESET_HG002_AJ,
    PRESET_NA19240_YRI,
    PRESET_NA18507_CHB,
)
from .dna_terminal_parser import DnaTerminalParser


class TestCertifiedReferenceStandardsConcordance:
    """
    Validates 100% concordance of all 5 globally certified human reference standards
    across 24 Autosomal STRs, 27 Y-STRs, mtDNA D-Loop, SNPs, and Epigenetics.
    """

    @pytest.fixture
    def validator(self):
        return ForensicMultiOmicValidator()

    def test_all_five_certified_standards_present(self):
        assert len(CERTIFIED_GLOBAL_REFERENCE_PRESETS) == 5
        keys = set(CERTIFIED_GLOBAL_REFERENCE_PRESETS.keys())
        expected = {
            "PRESET_NIST_SRM_2391D",
            "PRESET_NA12878_CEU",
            "PRESET_HG002_AJ",
            "PRESET_NA19240_YRI",
            "PRESET_NA18507_CHB",
        }
        assert keys == expected

    def test_nist_srm_2391d_concordance(self, validator):
        p = PRESET_NIST_SRM_2391D
        assert p.sex == "MALE"
        assert p.is_certified_standard is True
        assert len(p.str_profile) == 24
        assert len(p.ystr_profile) == 27
        assert p.str_profile["TH01"]["allele2"] == "9.3"
        assert p.str_profile["SE33"]["allele2"] == "27.2"

        # Validate 100% STR concordance
        rate, mismatches = validator.validate_str_concordance("PRESET_NIST_SRM_2391D", p.str_profile)
        assert rate == 100.0
        assert len(mismatches) == 0

        # Validate Y-STR concordance
        y_rate, y_mismatches = validator.validate_ystr_concordance("PRESET_NIST_SRM_2391D", p.ystr_profile)
        assert y_rate == 100.0
        assert len(y_mismatches) == 0

        # Validate mtDNA
        assert "263G" in p.mtdna_mutations
        assert "315.1C" in p.mtdna_mutations

        # Validate VISAGE age
        within, low, high = validator.validate_epigenetic_age_concordance("PRESET_NIST_SRM_2391D", 44.2)
        assert within is True
        assert low == 40.8
        assert high == 47.6

    def test_na12878_ceu_concordance(self, validator):
        p = PRESET_NA12878_CEU
        assert p.sex == "FEMALE"
        assert p.is_certified_standard is True
        assert len(p.str_profile) == 24
        assert len(p.ystr_profile) == 0

        # Check key microvariants
        assert p.str_profile["D1S1656"]["allele2"] == "17.3"
        assert p.str_profile["D2S441"]["allele2"] == "11.3"
        assert p.str_profile["SE33"]["allele2"] == "25.2"

        # Validate 100% STR concordance
        rate, mismatches = validator.validate_str_concordance("NA12878", p.str_profile)
        assert rate == 100.0
        assert len(mismatches) == 0

        # Female Y-STR null check
        y_rate, y_mismatches = validator.validate_ystr_concordance("NA12878", {})
        assert y_rate == 100.0

        # Validate mtDNA H1a1
        assert "309.1C" in p.mtdna_mutations
        assert "16263T" in p.mtdna_mutations

        # Validate VISAGE age 38.5
        within, low, high = validator.validate_epigenetic_age_concordance("NA12878", 38.5)
        assert within is True
        assert low == 35.1
        assert high == 41.9

    def test_hg002_aj_concordance(self, validator):
        p = PRESET_HG002_AJ
        assert p.sex == "MALE"
        assert len(p.str_profile) == 24
        assert len(p.ystr_profile) == 27

        # Check key microvariants and loci
        assert p.str_profile["D12S391"]["allele2"] == "18.3"
        assert p.str_profile["D19S433"]["allele2"] == "15.2"
        assert p.str_profile["D21S11"]["allele2"] == "31.2"

        # Validate 100% STR concordance
        rate, mismatches = validator.validate_str_concordance("HG002", p.str_profile)
        assert rate == 100.0
        assert len(mismatches) == 0

        # Validate Y-STR J2a1a1
        y_rate, y_mismatches = validator.validate_ystr_concordance("HG002", p.ystr_profile)
        assert y_rate == 100.0

        # Validate mtDNA K1a9
        assert "73G" in p.mtdna_mutations
        assert "16224C" in p.mtdna_mutations

        # Validate VISAGE age 22.1
        within, low, high = validator.validate_epigenetic_age_concordance("HG002", 22.1)
        assert within is True
        assert low == 18.7
        assert high == 25.5

    def test_na19240_yri_concordance(self, validator):
        p = PRESET_NA19240_YRI
        assert p.sex == "FEMALE"
        assert len(p.str_profile) == 24
        assert p.str_profile["D1S1656"]["allele2"] == "16.3"
        assert p.str_profile["SE33"]["allele2"] == "28.2"

        # Validate 100% STR concordance
        rate, mismatches = validator.validate_str_concordance("NA19240", p.str_profile)
        assert rate == 100.0

        # Validate mtDNA L2a1 (18 mutations including 524.1A / 524.2C)
        assert len(p.mtdna_mutations) == 18
        assert "524.1A" in p.mtdna_mutations
        assert "524.2C" in p.mtdna_mutations

        # Validate VISAGE age 31.4
        within, low, high = validator.validate_epigenetic_age_concordance("NA19240", 31.4)
        assert within is True
        assert low == 28.0
        assert high == 34.8

    def test_na18507_chb_concordance(self, validator):
        p = PRESET_NA18507_CHB
        assert p.sex == "MALE"
        assert len(p.str_profile) == 24
        assert len(p.ystr_profile) == 27
        assert p.str_profile["SE33"]["allele2"] == "22.2"

        # Validate 100% STR concordance
        rate, mismatches = validator.validate_str_concordance("NA18507", p.str_profile)
        assert rate == 100.0

        # Validate Y-STR O2a2b1
        y_rate, y_mismatches = validator.validate_ystr_concordance("NA18507", p.ystr_profile)
        assert y_rate == 100.0

        # Validate mtDNA D4a1
        assert "16362C" in p.mtdna_mutations

        # Validate VISAGE age 41.0
        within, low, high = validator.validate_epigenetic_age_concordance("NA18507", 41.0)
        assert within is True
        assert low == 37.6
        assert high == 44.4


class TestMultiOmicValidatorEngine:
    """Tests the validation engine with simulated errors and edge cases."""

    def test_str_mismatch_detected(self):
        validator = ForensicMultiOmicValidator()
        mutated_profile = dict(PRESET_NA12878_CEU.str_profile)
        # Introduce a deliberate discrepancy at TH01
        mutated_profile["TH01"] = {"allele1": "7", "allele2": "8"}

        rate, mismatches = validator.validate_str_concordance("NA12878", mutated_profile)
        assert rate < 100.0
        assert len(mismatches) == 1
        assert "TH01" in mismatches[0]

    def test_unknown_standard_raises_error(self):
        validator = ForensicMultiOmicValidator()
        with pytest.raises(ValueError, match="not found"):
            validator.validate_str_concordance("UNKNOWN_INDIVIDUAL_999", {})

    def test_epigenetic_age_out_of_bounds_detected(self):
        validator = ForensicMultiOmicValidator()
        # HG002 age is 22.1 (CI [18.7, 25.5]). Testing with 65.0 yrs
        within, low, high = validator.validate_epigenetic_age_concordance("HG002", 65.0)
        assert within is False
        assert low == 18.7
        assert high == 25.5


class TestExporters:
    """Validates export roundtrips to CODIS XML, ISO 17025 LIMS JSON, and GeneMapper CSV."""

    def test_export_to_codis_xml(self):
        p = PRESET_NA12878_CEU
        xml_str = CaseworkPresetExporter.export_to_codis_xml(
            sample_id="NA12878_CEU_TRUTH",
            str_profile=p.str_profile,
            source_lab="NIST_GIAB_LAB",
        )
        assert xml_str.startswith("<?xml")

        # Check roundtrip parsing with DnaTerminalParser
        parsed = DnaTerminalParser.parse_codis_xml(xml_str)
        assert parsed.sample_id == "NA12878_CEU_TRUTH"
        assert len(parsed.str_profile) >= 20
        assert parsed.str_profile["TH01"].allele2 == "9.3"

    def test_export_to_lims_json(self):
        p = PRESET_HG002_AJ
        json_str = CaseworkPresetExporter.export_to_lims_json(
            sample_id="HG002_AJ_TRUTH",
            str_profile=p.str_profile,
            snp_dosages=p.snp_dosages,
        )
        data = json.loads(json_str)
        assert data["title"] == "ISO17025_ForensicTerminalSchema"
        assert data["sampleMetadata"]["sampleID"] == "HG002_AJ_TRUTH"
        assert len(data["strGenotypes"]) == 24
        assert len(data["chainOfCustodyHash"]) == 64

        # Check roundtrip parsing with DnaTerminalParser
        parsed = DnaTerminalParser.parse_lims_json(json_str)
        assert parsed.sample_id == "HG002_AJ_TRUTH"
        assert parsed.str_profile["D12S391"].allele2 == "18.3"

    def test_export_to_genemapper_csv(self):
        p = PRESET_NA19240_YRI
        csv_str = CaseworkPresetExporter.export_to_genemapper_csv(
            sample_id="NA19240_YRI_TRUTH",
            str_profile=p.str_profile,
        )
        assert "Sample Name,Marker,Allele 1,Allele 2" in csv_str
        lines = csv_str.strip().split("\n")
        assert len(lines) >= 24

        # Check roundtrip parsing with DnaTerminalParser
        parsed = DnaTerminalParser.parse_genemapper(csv_str)
        assert parsed.sample_id == "NA19240_YRI_TRUTH"
        assert parsed.str_profile["SE33"].allele2 == "28.2"
