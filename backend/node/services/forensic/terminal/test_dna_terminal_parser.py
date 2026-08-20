"""
Unit Test Suite for Forensic DNA & SNP Terminal Ingestion Engine
Verifies all 6 Golden Benchmark Vectors (VECTOR_TERM_01 to VECTOR_TERM_06) and Multi-Format Ingestion.
Derived verbatim from research specification: research/dna_snp_terminal_research.md
"""

import pytest
import math
from backend.node.services.forensic.terminal.dna_terminal_parser import (
    DnaTerminalParser,
    ParsedForensicProfile,
    LocusSTRCall,
    SnpGenotypeCall,
    QualityAssessmentResult,
    SexDeterminationResult,
    SexClassificationEnum,
    PopGenMatchProbabilityResult,
    STR_PANEL_24_CATALOG,
    NIST_1036_SAMPLE_COUNT,
    NRC_II_P_MIN,
    ANALYTICAL_THRESHOLD_RFU,
    STOCHASTIC_THRESHOLD_RFU,
    HETEROZYGOTE_BALANCE_THRESHOLD,
    AMEL_Y_NULL_PRIOR_SAS,
    AMEL_Y_NULL_PRIOR_EUR,
)


class TestDnaTerminalParser:

    # ── 1. Constants & Panel Metadata Verification ──
    def test_01_constants_and_24_locus_catalog(self):
        assert NIST_1036_SAMPLE_COUNT == 1036
        assert math.isclose(NRC_II_P_MIN, 5.0 / 2072.0, rel_tol=1e-9)
        assert NRC_II_P_MIN < 0.002414
        assert ANALYTICAL_THRESHOLD_RFU == 50.0
        assert STOCHASTIC_THRESHOLD_RFU == 200.0
        assert HETEROZYGOTE_BALANCE_THRESHOLD == 0.60
        assert AMEL_Y_NULL_PRIOR_SAS == 0.0180
        assert AMEL_Y_NULL_PRIOR_EUR == 0.0002

        assert len(STR_PANEL_24_CATALOG) >= 24
        assert "D3S1358" in STR_PANEL_24_CATALOG
        assert "vWA" in STR_PANEL_24_CATALOG
        assert "FGA" in STR_PANEL_24_CATALOG
        assert "SE33" in STR_PANEL_24_CATALOG
        assert "Penta D" in STR_PANEL_24_CATALOG
        assert "Penta E" in STR_PANEL_24_CATALOG
        assert "Amelogenin" in STR_PANEL_24_CATALOG
        assert "DYS391" in STR_PANEL_24_CATALOG

        # Check TH01 microvariant and stutter
        th01 = STR_PANEL_24_CATALOG["TH01"]
        assert "9.3" in th01.common_microvariants
        assert th01.max_reverse_stutter_ratio == 0.050

    # ── 2. VECTOR_TERM_01: Northern European Reference (Sample EU) ──
    def test_02_vector_term_01_european_reference(self):
        csv_data = """Sample Name,Marker,Allele 1,Allele 2,Height 1,Height 2,Size 1,Size 2,Data Point 1,Data Point 2
VECTOR_TERM_01,D3S1358,15,16,1250,1180,121.5,125.5,2410,2490
VECTOR_TERM_01,vWA,17,18,980,940,165.2,169.2,3100,3180
VECTOR_TERM_01,FGA,21,23,890,860,225.4,233.4,4200,4320
VECTOR_TERM_01,D8S1179,13,14,1420,1380,130.1,134.1,2500,2580
VECTOR_TERM_01,D21S11,28,30,1100,1050,201.2,209.2,3800,3920
VECTOR_TERM_01,D18S51,12,15,780,750,270.3,282.3,5100,5280
VECTOR_TERM_01,D5S818,11,12,1300,1270,140.5,144.5,2700,2780
VECTOR_TERM_01,D13S317,11,13,1150,1100,180.2,188.2,3400,3520
VECTOR_TERM_01,D7S820,10,11,1020,990,195.4,199.4,3700,3780
VECTOR_TERM_01,D16S539,11,12,1210,1180,240.1,244.1,4500,4580
VECTOR_TERM_01,CSF1PO,10,12,950,920,305.2,313.2,5700,5820
VECTOR_TERM_01,TH01,9.3,9.3,2100,2100,175.8,175.8,3250,3250
VECTOR_TERM_01,TPOX,8,11,880,840,220.1,232.1,4100,4280
VECTOR_TERM_01,D1S1656,14,17.3,740,710,185.3,198.6,3500,3720
VECTOR_TERM_01,D2S441,11,12,1350,1310,110.2,114.2,2100,2180
VECTOR_TERM_01,D2S1338,19,23,690,660,290.4,306.4,5400,5640
VECTOR_TERM_01,D10S1248,13,14,1480,1440,95.1,99.1,1800,1880
VECTOR_TERM_01,D12S391,18,19,820,790,215.2,219.2,4000,4080
VECTOR_TERM_01,D19S433,13,14,1120,1080,105.4,109.4,2000,2080
VECTOR_TERM_01,D22S1045,15,16,1280,1240,155.3,158.3,2900,2960
VECTOR_TERM_01,SE33,26.2,28.2,540,510,320.5,328.5,5900,6020
VECTOR_TERM_01,Penta D,9,12,920,890,145.2,160.2,2800,3020
VECTOR_TERM_01,Penta E,7,12,710,680,380.1,405.1,6800,7200
VECTOR_TERM_01,Amelogenin,X,Y,1500,1450,106.0,112.0,2050,2150
"""
        profile = DnaTerminalParser.parse_genemapper(csv_data)
        assert profile.sample_id == "VECTOR_TERM_01"
        assert len(profile.str_profile) == 24
        assert profile.str_profile["TH01"].allele1 == "9.3"
        assert profile.str_profile["TH01"].is_homozygous is True

        # PopGen Match Probability under NRC II and Balding-Nichols
        res = DnaTerminalParser.calculate_popgen_match_probability(profile, population="Caucasian", theta=0.01)
        assert res.combined_match_probability < 1e-20
        assert res.log10_lr > 20.0
        assert "Extremely Strong Support" in res.enfsi_verbal_scale

        # Sex determination
        sex_res = DnaTerminalParser.validate_sex_and_aneuploidy(profile)
        assert sex_res.sex_classification == SexClassificationEnum.STANDARD_MALE

        # Quality assessment
        qc = DnaTerminalParser.assess_quality_and_stochastic_gates(profile)
        assert qc.passed_qc is True
        assert qc.dropout_loci_count == 0
        assert qc.degradation_severity == "NORMAL"

    # ── 3. VECTOR_TERM_02: West African Reference (Sample AA) ──
    def test_03_vector_term_02_west_african_reference(self):
        json_data = """{
            "sampleMetadata": {
                "sampleID": "VECTOR_TERM_02",
                "laboratoryORI": "AFR_FORENSIC_LAB_01",
                "analysisTimestamp": "2026-08-16T12:00:00Z",
                "operatorID": "ANALYST_AA"
            },
            "strGenotypes": [
                {"locusName": "D3S1358", "allele1": "16", "allele2": "17", "rfu1": 1100, "rfu2": 1050},
                {"locusName": "vWA", "allele1": "15", "allele2": "18", "rfu1": 950, "rfu2": 920},
                {"locusName": "TH01", "allele1": "7", "allele2": "9", "rfu1": 1300, "rfu2": 1250},
                {"locusName": "Amelogenin", "allele1": "X", "allele2": "Y", "rfu1": 1400, "rfu2": 1350}
            ],
            "aimGenotypes": [
                {"rsID": "rs12913832", "genotypeCall": "0/0"},
                {"rsID": "rs1426654", "genotypeCall": "0/0"},
                {"rsID": "rs16891982", "genotypeCall": "0/0"}
            ],
            "hirisplexGenotypes": [
                {"rsID": "rs12913832", "dosageValue": 0},
                {"rsID": "rs1426654", "dosageValue": 0},
                {"rsID": "rs16891982", "dosageValue": 0}
            ],
            "chainOfCustodyHash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        }"""
        profile = DnaTerminalParser.parse_lims_json(json_data)
        assert profile.sample_id == "VECTOR_TERM_02"
        assert len(profile.snp_profile) == 3
        assert profile.snp_profile["rs12913832"].dosage_value == 0
        assert profile.snp_profile["rs1426654"].dosage_value == 0

        sex_res = DnaTerminalParser.validate_sex_and_aneuploidy(profile)
        assert sex_res.sex_classification == SexClassificationEnum.STANDARD_MALE

    # ── 4. VECTOR_TERM_03: East Asian Reference (Sample EAS) ──
    def test_04_vector_term_03_east_asian_reference(self):
        vcf_data = """##fileformat=VCFv4.2
##fileDate=20260816
##source=ForensicNGSTerminal_v4.2
##reference=GRCh38
##INFO=<ID=STR,Number=1,Type=String,Description="STR Repeat Allele Call">
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Read Depth">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	VECTOR_TERM_03
chr2	109513601	rs3827760	A	G	999	PASS	.	GT:DP	1/1:1500
chr15	28365618	rs12913832	A	G	999	PASS	.	GT:DP	0/0:1400
chr15	28230318	rs1800414	T	C	999	PASS	.	GT:DP	1/1:1350
chr11	2149300	TH01	AATG	AATG	999	PASS	STR=6,9;DP=800	GT:DP	0/1:800
"""
        profile = DnaTerminalParser.parse_ngs_vcf(vcf_data)
        assert profile.sample_id == "VECTOR_TERM_03"
        assert "rs3827760" in profile.snp_profile
        assert profile.snp_profile["rs3827760"].dosage_value == 2  # EDAR G/G
        assert profile.str_profile["TH01"].allele1 == "6"
        assert profile.str_profile["TH01"].allele2 == "9"

    # ── 5. VECTOR_TERM_04: South Asian with Amelogenin Y-Null Deletion ──
    def test_05_vector_term_04_south_asian_y_null(self):
        csv_data = """Sample Name,Marker,Allele 1,Allele 2,Height 1,Height 2
VECTOR_TERM_04,Amelogenin,X,[0],1850,0
VECTOR_TERM_04,DYS391,11,,820,
VECTOR_TERM_04,TH01,7,9.3,1200,1150
VECTOR_TERM_04,D3S1358,14,15,1050,980
"""
        profile = DnaTerminalParser.parse_genemapper(csv_data)
        assert profile.sample_id == "VECTOR_TERM_04"
        assert profile.str_profile["Amelogenin"].allele1 == "X"
        assert profile.supplementary_markers.get("DYS391") == "11"

        # Validating Amelogenin Y-null deletion logic
        sex_res = DnaTerminalParser.validate_sex_and_aneuploidy(profile)
        assert sex_res.sex_classification == SexClassificationEnum.Y_NULL_DELETION
        assert "AMELY" in sex_res.operational_action
        assert sex_res.prior_y_null_prob_sas == 0.0180

    # ── 6. VECTOR_TERM_05: Degraded Skeletal Remains (Sample DVI_DEGRADED) ──
    def test_06_vector_term_05_degraded_skeletal_remains(self):
        csv_data = """Sample Name,Marker,Allele 1,Allele 2,Height 1,Height 2
VECTOR_TERM_05,D8S1179,13,[0],842,0
VECTOR_TERM_05,FGA,22,24,100,95
VECTOR_TERM_05,D21S11,[0],[0],0,0
VECTOR_TERM_05,D18S51,[0],[0],0,0
VECTOR_TERM_05,SE33,[0],[0],0,0
VECTOR_TERM_05,Penta E,[0],[0],0,0
VECTOR_TERM_05,TH01,9.3,9.3,950,950
VECTOR_TERM_05,Amelogenin,X,Y,600,580
"""
        profile = DnaTerminalParser.parse_genemapper(csv_data)
        qc = DnaTerminalParser.assess_quality_and_stochastic_gates(profile)
        
        # Check Degradation Index DI = 842 / 100 = 8.42
        assert math.isclose(qc.degradation_index, 8.42, rel_tol=1e-2)
        assert qc.degradation_severity == "SEVERE"
        assert qc.passed_qc is False
        assert qc.dropout_loci_count >= 4

    # ── 7. VECTOR_TERM_06: Low-Template Touch DNA Mixture (Sample TOUCH_LTDNA) ──
    def test_07_vector_term_06_touch_ltdna(self):
        csv_data = """Sample Name,Marker,Allele 1,Allele 2,Height 1,Height 2
VECTOR_TERM_06,vWA,16,18,180,80
VECTOR_TERM_06,D8S1179,12,14,140,60
VECTOR_TERM_06,FGA,22,24,95,40
VECTOR_TERM_06,TH01,6,9.3,110,48
VECTOR_TERM_06,D3S1358,15,[0],120,0
"""
        profile = DnaTerminalParser.parse_genemapper(csv_data)
        qc = DnaTerminalParser.assess_quality_and_stochastic_gates(profile)
        
        # Heterozygote balance: 80 / 180 = 0.444 < 0.60
        assert qc.imbalanced_loci_count >= 2
        assert qc.stochastic_mixture_flag is True

    # ── 8. CODIS CMF XML Parsing Test ──
    def test_08_codis_cmf_xml_parsing(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<CODISImportFile xmlns="http://www.fbi.gov/codis/cmf/3.2" HeaderVersion="3.2">
  <HEADER>
    <SOURCELAB>VA122015Y</SOURCELAB>
    <DESTINATIONLAB>VA010015Y</DESTINATIONLAB>
    <CREATIONDATE>2026-08-16T09:00:00</CREATIONDATE>
    <SUBMITTYPENAME>Casework</SUBMITTYPENAME>
    <BATCHID>BATCH_2026_TERM_01</BATCHID>
  </HEADER>
  <SPECIMEN>
    <SPECIMENID>CODIS_TEST_SPECIMEN</SPECIMENID>
    <SPECIMENCATEGORY>Forensic Unknown</SPECIMENCATEGORY>
    <DISCLAIMER>ISO17025 Verified Profile</DISCLAIMER>
    <BATCH>
      <KIT>GlobalFiler Express</KIT>
      <READING>
        <READINGBY>ANALYST_01</READINGBY>
        <READINGDATE>2026-08-16</READINGDATE>
        <LOCUS>
          <LOCUSNAME>D3S1358</LOCUSNAME>
          <ALLELE><ALLELEVALUE>15</ALLELEVALUE></ALLELE>
          <ALLELE><ALLELEVALUE>16</ALLELEVALUE></ALLELE>
        </LOCUS>
        <LOCUS>
          <LOCUSNAME>TH01</LOCUSNAME>
          <ALLELE><ALLELEVALUE>9.3</ALLELEVALUE></ALLELE>
        </LOCUS>
      </READING>
    </BATCH>
  </SPECIMEN>
</CODISImportFile>"""
        profile = DnaTerminalParser.parse_codis_xml(xml_data)
        assert profile.sample_id == "CODIS_TEST_SPECIMEN"
        assert profile.laboratory_ori == "VA122015Y"
        assert profile.operator_id == "ANALYST_01"
        assert profile.str_profile["D3S1358"].allele1 == "15"
        assert profile.str_profile["D3S1358"].allele2 == "16"
        assert profile.str_profile["TH01"].allele1 == "9.3"
        assert profile.str_profile["TH01"].is_homozygous is True
