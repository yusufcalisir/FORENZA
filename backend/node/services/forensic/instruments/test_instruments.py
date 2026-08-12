import pytest
from backend.node.services.forensic.instruments.parser_gateway import InstrumentParserGateway


def test_parse_ce_genemapper_valid_csv():
    gateway = InstrumentParserGateway()
    csv_data = """Sample Name,Locus,Allele 1,Allele 2,Height 1,Height 2
SAMPLE-01,D3S1358,15,16,1200,1150
SAMPLE-01,vWA,16,17,950,980
"""
    result = gateway.parse_ce_genemapper(csv_data)
    assert result["instrument_type"] == "CAPILLARY_ELECTROPHORESIS_CE"
    assert result["total_loci_parsed"] == 2
    assert result["parsed_peaks"][0]["locus"] == "D3S1358"
    assert result["parsed_peaks"][0]["alleles"] == ["15", "16"]


def test_parse_qpcr_quantifiler_intact():
    gateway = InstrumentParserGateway()
    res = gateway.parse_qpcr_quantifiler(
        small_autosomal_conc_ng_ul=0.85,
        large_autosomal_conc_ng_ul=0.80,
        male_y_conc_ng_ul=0.82
    )
    assert res["degradation_index_di"] <= 1.5
    assert res["degradation_assessment"] == "INTACT_NO_DEGRADATION"


def test_parse_qpcr_quantifiler_degraded():
    gateway = InstrumentParserGateway()
    res = gateway.parse_qpcr_quantifiler(
        small_autosomal_conc_ng_ul=1.20,
        large_autosomal_conc_ng_ul=0.20,
        male_y_conc_ng_ul=0.50
    )
    assert res["degradation_index_di"] == 6.0
    assert res["degradation_assessment"] == "SEVERELY_DEGRADED"


def test_parse_ngs_vcf_valid_variants():
    gateway = InstrumentParserGateway()
    vcf_data = """##fileformat=VCFv4.2
#CHROM\tPOS\tID\tREF\tALT
chr15\t28365618\trs12913832\tA\tG
chr16\t89986117\trs1805007\tC\tT
"""
    res = gateway.parse_ngs_vcf(vcf_data)
    assert res["instrument_type"] == "NGS_ILLUMINA_MISEQ"
    assert res["total_snps_parsed"] == 2
    assert res["parsed_variants"][0]["variant_id"] == "rs12913832"


def test_empty_ce_csv_raises_error():
    gateway = InstrumentParserGateway()
    with pytest.raises(ValueError, match="cannot be empty"):
        gateway.parse_ce_genemapper("")


def test_negative_qpcr_conc_raises_error():
    gateway = InstrumentParserGateway()
    with pytest.raises(ValueError, match="must be non-negative"):
        gateway.parse_qpcr_quantifiler(-0.5, 0.2, 0.1)
