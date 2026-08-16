"""
FORENZA: Unit Tests for Golden Casework Presets & Multi-Format Exporter Engine
Validates all 6 benchmark reference vectors (VECTOR_TERM_01 to VECTOR_TERM_06)
and export roundtrips (CODIS CMF 3.2 XML, ISO 17025 LIMS JSON, GeneMapper CSV).

Derived verbatim from research specification: research/dna_snp_terminal_research.md
Compliance: ISO/IEC 17025:2017 • FBI CODIS NDIS v3.2/v4.0 • SWGDAM 2020 Guidelines
"""

import json
from xml.etree import ElementTree as ET

from .casework_presets import CaseworkPresetsEngine, GOLDEN_CASEWORK_PRESETS
from .dna_terminal_parser import DnaTerminalParser


class TestGoldenCaseworkPresets:
    """Validates the catalog of 6 Golden Benchmark Casework Vectors."""

    def test_all_six_presets_present(self):
        presets = CaseworkPresetsEngine.get_all_presets()
        assert len(presets) == 6
        preset_ids = {p.preset_id for p in presets}
        expected_ids = {
            "VECTOR_TERM_01",
            "VECTOR_TERM_02",
            "VECTOR_TERM_03",
            "VECTOR_TERM_04",
            "VECTOR_TERM_05",
            "VECTOR_TERM_06",
        }
        assert preset_ids == expected_ids

    def test_vector_term_01_european(self):
        p = CaseworkPresetsEngine.get_preset_by_id("VECTOR_TERM_01")
        assert p is not None
        assert "European" in p.target_population or "EUR" in p.target_population
        assert p.str_profile["D3S1358"]["allele1"] == "15"
        assert p.str_profile["D3S1358"]["allele2"] == "16"
        assert p.str_profile["TH01"]["allele1"] == "9.3"
        assert p.str_profile["Amelogenin"]["allele1"] == "X"
        assert p.str_profile["Amelogenin"]["allele2"] == "Y"
        assert p.snp_dosages["rs12913832"] == 2  # HERC2 A/A
        assert p.snp_dosages["rs16891982"] == 2  # SLC45A2 C/C
        assert p.snp_dosages["rs1426654"] == 2   # SLC24A5 A/A
        assert p.degradation_index <= 1.5

    def test_vector_term_02_african(self):
        p = CaseworkPresetsEngine.get_preset_by_id("VECTOR_TERM_02")
        assert p is not None
        assert "African" in p.target_population or "AFR" in p.target_population
        assert p.str_profile["D3S1358"]["allele1"] == "16"
        assert p.str_profile["D3S1358"]["allele2"] == "17"
        assert p.snp_dosages["rs12913832"] == 0  # HERC2 G/G
        assert p.snp_dosages["rs2814778"] == 2   # DARC null

    def test_vector_term_03_east_asian(self):
        p = CaseworkPresetsEngine.get_preset_by_id("VECTOR_TERM_03")
        assert p is not None
        assert "East Asian" in p.target_population or "EAS" in p.target_population
        assert p.str_profile["D3S1358"]["allele1"] == "15"
        assert p.str_profile["D3S1358"]["allele2"] == "18"
        assert p.snp_dosages["rs3827760"] == 2  # EDAR G/G
        assert p.snp_dosages["rs1800414"] == 2  # OCA2 C/C

    def test_vector_term_04_south_asian_y_null(self):
        p = CaseworkPresetsEngine.get_preset_by_id("VECTOR_TERM_04")
        assert p is not None
        assert "South Asian" in p.target_population or "SAS" in p.target_population
        # Single X peak, Y is absent
        assert p.str_profile["Amelogenin"]["allele1"] == "X"
        assert p.str_profile["Amelogenin"]["allele2"] in ("[0]", "None", None, "")
        assert p.str_profile["Amelogenin"]["rfu1"] == 1850
        assert p.str_profile["Amelogenin"]["rfu2"] == 0
        assert p.supplementary_markers["DYS391"] == "11"
        assert p.snp_dosages["rs1426654"] == 2

    def test_vector_term_05_dvi_degraded(self):
        p = CaseworkPresetsEngine.get_preset_by_id("VECTOR_TERM_05")
        assert p is not None
        assert p.degradation_index == 8.42
        # Severe degradation DI > 5.0
        assert p.degradation_index > 5.0
        # FGA, D21S11, D18S51, SE33, Penta E have locus dropouts
        assert p.str_profile["FGA"]["allele1"] == "[0]"
        assert p.str_profile["D21S11"]["allele1"] == "[0]"
        assert p.str_profile["D18S51"]["allele1"] == "[0]"
        assert p.str_profile["SE33"]["allele1"] == "[0]"
        assert p.str_profile["Penta E"]["allele1"] == "[0]"
        # Small locus D8S1179 has RFU 842, FGA has RFU 100 -> DI = 8.42
        assert p.str_profile["D8S1179"]["rfu1"] == 842
        assert p.str_profile["FGA"]["rfu1"] == 100

    def test_vector_term_06_touch_ltdna(self):
        p = CaseworkPresetsEngine.get_preset_by_id("VECTOR_TERM_06")
        assert p is not None
        assert p.stochastic_dropout_prob == 0.35
        assert p.heterozygote_balance == 0.45
        assert p.heterozygote_balance < 0.60
        # vWA exhibits severe imbalance: 450 vs 1000 RFU (Hb = 0.45)
        assert p.str_profile["vWA"]["rfu1"] == 450
        assert p.str_profile["vWA"]["rfu2"] == 1000


class TestExporters:
    """Validates export roundtrips to CODIS XML, ISO 17025 LIMS JSON, and GeneMapper CSV."""

    def test_export_to_codis_xml(self):
        p = CaseworkPresetsEngine.get_preset_by_id("VECTOR_TERM_01")
        xml_str = CaseworkPresetsEngine.export_to_codis_xml(
            sample_id="SAMPLE_EU_01",
            str_profile=p.str_profile,
            source_lab="TEST_LAB_01",
        )
        assert xml_str.startswith("<?xml")

        # Check roundtrip parsing with DnaTerminalParser
        parsed = DnaTerminalParser.parse_codis_xml(xml_str)
        assert parsed.sample_id == "SAMPLE_EU_01"
        assert len(parsed.str_profile) >= 20
        assert parsed.str_profile["D3S1358"].allele1 == "15"
        assert parsed.str_profile["D3S1358"].allele2 == "16"

    def test_export_to_lims_json(self):
        p = CaseworkPresetsEngine.get_preset_by_id("VECTOR_TERM_01")
        json_str = CaseworkPresetsEngine.export_to_lims_json(
            sample_id="SAMPLE_EU_01",
            str_profile=p.str_profile,
            snp_dosages=p.snp_dosages,
        )
        data = json.loads(json_str)
        assert data["title"] == "ISO17025_ForensicTerminalSchema"
        assert data["sampleMetadata"]["sampleID"] == "SAMPLE_EU_01"
        assert len(data["strGenotypes"]) >= 20
        assert len(data["hirisplexGenotypes"]) >= 4
        assert len(data["chainOfCustodyHash"]) == 64

        # Check roundtrip parsing with DnaTerminalParser
        parsed = DnaTerminalParser.parse_lims_json(json_str)
        assert parsed.sample_id == "SAMPLE_EU_01"
        assert parsed.str_profile["TH01"].allele1 == "9.3"

    def test_export_to_genemapper_csv(self):
        p = CaseworkPresetsEngine.get_preset_by_id("VECTOR_TERM_02")
        csv_str = CaseworkPresetsEngine.export_to_genemapper_csv(
            sample_id="SAMPLE_AA_01",
            str_profile=p.str_profile,
        )
        assert "Sample Name,Marker,Allele 1,Allele 2" in csv_str
        lines = csv_str.strip().split("\n")
        assert len(lines) >= 24

        # Check roundtrip parsing with DnaTerminalParser
        parsed = DnaTerminalParser.parse_genemapper(csv_str)
        assert parsed.sample_id == "SAMPLE_AA_01"
        assert parsed.str_profile["D3S1358"].allele1 == "16"
        assert parsed.str_profile["D3S1358"].allele2 == "17"

