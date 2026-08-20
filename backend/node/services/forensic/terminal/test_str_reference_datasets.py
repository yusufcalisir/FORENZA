"""
Unit tests for FORENZA 24-Locus STR Reference Datasets & Ingestion Engine
Validation Suite for Sub-Item 1.1.2:
- NIST SRM 2391d Components A, B, C, D, and E (Certified Reference Profiles)
- Promega PowerPlex Fusion 24 Validation Suite (PMC7820400 Sensitivity Dilutions)
- QIAGEN Verogen ForenSeq MainstAY Kit Autosomal Core (NGS/CE Concordance)
- CODIS CMF XML & GeneMapper CSV Multi-Format Ingest Engine
Derived from: research/pillar_1_probabilistic_genotyping_research.md
"""

import pytest
from backend.node.services.forensic.terminal.str_reference_datasets import (
    STRReferenceDatasetIngestEngine,
    STR_REFERENCE_DATASET_CATALOG,
    NIST_SRM_2391D_COMP_A,
    NIST_SRM_2391D_COMP_B,
    NIST_SRM_2391D_COMP_C,
    NIST_SRM_2391D_COMP_D,
    NIST_SRM_2391D_COMP_E,
    POWERPLEX_FUSION_24_SUITE,
    VEROGEN_MAINSTAY_AUTOSOMAL_CORE,
)


class TestNistSrm2391dAllComponents:
    """Test suite for NIST SRM 2391d Components A through E certified profiles."""

    def test_catalog_contains_all_components(self):
        """Verify all 5 NIST SRM 2391d components are present in the catalog."""
        expected = [
            "NIST_SRM_2391D_COMP_A",
            "NIST_SRM_2391D_COMP_B",
            "NIST_SRM_2391D_COMP_C",
            "NIST_SRM_2391D_COMP_D",
            "NIST_SRM_2391D_COMP_E",
        ]
        for cid in expected:
            assert cid in STR_REFERENCE_DATASET_CATALOG, f"Missing reference component: {cid}"
            ds = STRReferenceDatasetIngestEngine.get_dataset(cid)
            assert ds is not None
            assert len(ds.str_profile) == 24

    def test_component_a_female_profile(self):
        """Verify Component A (9947A Female Caucasian) characteristics."""
        ds = NIST_SRM_2391D_COMP_A
        assert ds.sex == "FEMALE"
        assert ds.str_profile["AMEL"]["allele1"] == "X"
        assert ds.str_profile["AMEL"]["allele2"] == "X"
        assert ds.str_profile["TH01"]["allele1"] == "8"
        assert ds.str_profile["TH01"]["allele2"] == "9.3"
        assert ds.str_profile["SE33"]["allele1"] == "19"
        assert ds.str_profile["SE33"]["allele2"] == "29.2"
        assert ds.degradation_index == 1.00

    def test_component_b_male_african_american(self):
        """Verify Component B (9948 Male African American) characteristics."""
        ds = NIST_SRM_2391D_COMP_B
        assert ds.sex == "MALE"
        assert ds.str_profile["AMEL"]["allele1"] == "X"
        assert ds.str_profile["AMEL"]["allele2"] == "Y"
        assert ds.str_profile["D1S1656"]["allele2"] == "17.3"
        assert ds.str_profile["SE33"]["allele1"] == "22.2"
        assert ds.str_profile["SE33"]["allele2"] == "27.2"

    def test_component_c_male_caucasian(self):
        """Verify Component C (Male Caucasian) characteristics."""
        ds = NIST_SRM_2391D_COMP_C
        assert ds.sex == "MALE"
        assert ds.str_profile["D21S11"]["allele2"] == "31.2"
        assert ds.str_profile["SE33"]["allele2"] == "25.2"

    def test_component_d_degraded_bone_extract(self):
        """Verify Component D degraded DNA dropouts and low template characteristics."""
        ds = NIST_SRM_2391D_COMP_D
        assert ds.degradation_index == 4.85
        assert ds.template_mass_ng == 0.05  # 50 pg
        assert ds.stochastic_dropout_prob == 0.48
        # High molecular weight loci dropouts (>250 bp)
        assert ds.str_profile["SE33"]["allele1"] == "0"
        assert ds.str_profile["PENTA_E"]["allele1"] == "0"
        assert ds.str_profile["FGA"]["allele2"] == "0"

    def test_component_e_microvariants_catalog(self):
        """Verify Component E harbors the 8 key certified microvariants."""
        ds = NIST_SRM_2391D_COMP_E
        assert "TH01 9.3" in ds.microvariants_present
        assert "SE33 25.2" in ds.microvariants_present
        assert "SE33 27.2" in ds.microvariants_present
        assert "D1S1656 17.3" in ds.microvariants_present
        assert "D21S11 31.2" in ds.microvariants_present
        assert "D2S441 11.3" in ds.microvariants_present
        assert "D12S391 18.3" in ds.microvariants_present
        assert "D19S433 14.2" in ds.microvariants_present
        assert "FGA 22.2" in ds.microvariants_present


class TestSTRReferenceDatasetIngestEngine:
    """Test suite for concordance checking and multi-format parsing."""

    def test_exact_concordance_validation_success(self):
        """Verify 100% concordance on identical observed profile."""
        obs = {
            k: (v["allele1"], v.get("allele2", v["allele1"]))
            for k, v in NIST_SRM_2391D_COMP_A.str_profile.items()
        }
        res = STRReferenceDatasetIngestEngine.validate_concordance(obs, "NIST_SRM_2391D_COMP_A")
        assert res["is_concordant"] is True
        assert res["concordance_rate_percent"] == 100.0
        assert len(res["mismatches"]) == 0
        assert res["matched_loci_count"] == 24

    def test_concordance_validation_detects_mismatch(self):
        """Verify that allele mutations / typing errors are detected cleanly."""
        obs = {
            k: (v["allele1"], v.get("allele2", v["allele1"]))
            for k, v in NIST_SRM_2391D_COMP_A.str_profile.items()
        }
        # Inject artificial mismatch at TH01 (observed 7, 9.3 instead of 8, 9.3)
        obs["TH01"] = ("7", "9.3")

        res = STRReferenceDatasetIngestEngine.validate_concordance(obs, "NIST_SRM_2391D_COMP_A")
        assert res["is_concordant"] is False
        assert res["concordance_rate_percent"] < 100.0
        assert len(res["mismatches"]) == 1
        assert res["mismatches"][0]["locus"] == "TH01"
        assert res["mismatches"][0]["observed"] == ["7", "9.3"]
        assert res["mismatches"][0]["expected_reference"] == ["8", "9.3"]

    def test_parse_codis_cmf_xml(self):
        """Verify CODIS CMF 3.2 XML parsing."""
        sample_xml = """<?xml version="1.0" standalone="yes"?>
        <CODISEXPORT version="3.2">
            <SPECIMEN SpecimenCategory="Standard">
                <LOCUS name="D3S1358">
                    <ALLELE><ALLELEVALUE>15</ALLELEVALUE></ALLELE>
                    <ALLELE><ALLELEVALUE>16</ALLELEVALUE></ALLELE>
                </LOCUS>
                <LOCUS name="TH01">
                    <ALLELE><ALLELEVALUE>6</ALLELEVALUE></ALLELE>
                    <ALLELE><ALLELEVALUE>9.3</ALLELEVALUE></ALLELE>
                </LOCUS>
            </SPECIMEN>
        </CODISEXPORT>"""
        parsed = STRReferenceDatasetIngestEngine.parse_codis_cmf_xml(sample_xml)
        assert "D3S1358" in parsed
        assert parsed["D3S1358"] == ("15", "16")
        assert "TH01" in parsed
        assert parsed["TH01"] == ("6", "9.3")

    def test_parse_genemapper_csv(self):
        """Verify GeneMapper ID-X CSV parsing."""
        sample_csv = """Sample File,Sample Name,Marker,Allele 1,Allele 2,Size 1,Size 2,Height 1,Height 2
        File01,SRM2391d_A,D3S1358,14,15,120.4,124.5,2800,2750
        File01,SRM2391d_A,TH01,8,9.3,180.2,185.7,2900,2850
        File01,SRM2391d_A,D21S11,30,30,210.5,210.5,4000,4000
        """
        parsed = STRReferenceDatasetIngestEngine.parse_genemapper_csv(sample_csv)
        assert "D3S1358" in parsed
        assert parsed["D3S1358"] == ("14", "15")
        assert "TH01" in parsed
        assert parsed["TH01"] == ("8", "9.3")
        assert "D21S11" in parsed
        assert parsed["D21S11"] == ("30", "30")


class TestPowerPlexFusion24Suite:
    """Test suite for Promega PowerPlex Fusion 24 validation sensitivity dilutions."""

    def test_sensitivity_series_profiles(self):
        """Verify template scaling across 1.0 ng, 250 pg, and 62.5 pg."""
        suite = POWERPLEX_FUSION_24_SUITE
        assert "1.0ng" in suite
        assert "0.25ng" in suite
        assert "0.0625ng" in suite

        p_1ng = suite["1.0ng"]
        p_250pg = suite["0.25ng"]
        p_62pg = suite["0.0625ng"]

        assert p_1ng.template_mass_ng == 1.00
        assert p_250pg.template_mass_ng == 0.25
        assert p_62pg.template_mass_ng == 0.0625

        # Signal reduction check
        rfu_1ng = p_1ng.str_profile["D3S1358"]["rfu1"]
        rfu_250pg = p_250pg.str_profile["D3S1358"]["rfu1"]
        rfu_62pg = p_62pg.str_profile["D3S1358"]["rfu1"]

        assert rfu_1ng > rfu_250pg > rfu_62pg
        assert p_62pg.stochastic_dropout_prob > p_1ng.stochastic_dropout_prob


class TestVerogenMainstAYOrthogonalConcordance:
    """Test suite for QIAGEN Verogen ForenSeq MainstAY NGS concordance."""

    def test_ngs_metadata_and_concordance(self):
        """Verify ForenSeq MainstAY platform metadata and 100% CE repeat concordance."""
        ds = VEROGEN_MAINSTAY_AUTOSOMAL_CORE
        assert ds.metadata["sequencing_platform"] == "Illumina MiSeq FGx"
        assert ds.metadata["concordance_rate_percent"] == 100.0
        assert len(ds.str_profile) == 24
        assert ds.str_profile["TH01"]["allele2"] == "9.3"
