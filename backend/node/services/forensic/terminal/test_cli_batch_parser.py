"""
Unit and Integration Tests for Forensic CLI Batch Ingestion Engine & EBNF Lexer.
Compliant with ISO/IEC 17025:2017 §7.5 and SWGDAM 2020.
Verifies all 6 Golden Benchmark Vectors (VECTOR_CLI_01 through VECTOR_CLI_06) from research/terminal_cli_batch_input_research.md.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.node.services.forensic.terminal.cli_batch_parser import (
    ForensicCliBatchParser,
    ForensicCliLexer,
    CliSyntaxError,
    ExecutionMode,
    DomainPrefix,
)
from backend.app.api.terminal_routes import router as terminal_router

_app = FastAPI()
_app.include_router(terminal_router, prefix="/api/v1")
client = TestClient(_app)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. GOLDEN BENCHMARK VECTORS (VECTOR_CLI_01 to VECTOR_CLI_06)
# ═══════════════════════════════════════════════════════════════════════════════

class TestGoldenBenchmarkVectors:
    """Verifies all 6 Golden Benchmark Vectors defined in research specification."""

    def test_vector_cli_01_autosomal_str_batch(self):
        """VECTOR_CLI_01: Pristine 24-Locus Autosomal STR Batch Entry (str set-batch)."""
        cmd = (
            'str set-batch --data "AMEL:X,Y;CSF1PO:10,12;D1S1656:12,15.3;D2S441:11,14;D2S1338:17,23;'
            'D3S1358:15,18;D5S818:11,13;D7S820:8,11;D8S1179:12,14;D10S1248:13,15;D12S391:18,22;D13S317:11,12;'
            'D16S539:9,13;D18S51:14,20;D19S433:13,14.2;D21S11:28,30;D22S1045:11,16;FGA:21,24;TH01:6,9.3;'
            'TPOX:8,11;VWA:16,18;SE33:17,25.2;PENTA_D:9,12;PENTA_E:7,14" '
            '--rfu "AMEL:1250,1180;CSF1PO:850,910;D1S1656:1100,1050;D2S441:950,980;D2S1338:1300,1210;'
            'D3S1358:1400,1350;D5S818:880,920;D7S820:790,810;D8S1179:1150,1120;D10S1248:1020,990;D12S391:650,620;'
            'D13S317:900,870;D16S539:840,860;D18S51:710,690;D19S433:980,940;D21S11:1050,1010;D22S1045:1120,1080;'
            'FGA:890,850;TH01:1500,1420;TPOX:1100,1050;VWA:1350,1280;SE33:550,510;PENTA_D:920,890;PENTA_E:810,780" '
            '--mode STRICT'
        )
        res = ForensicCliBatchParser.execute_command(cmd)

        assert res["domain"] == "AUTOSOMAL_STR"
        assert res["status"] == "COMMITTED"
        assert res["execution_mode"] == "STRICT"
        assert res["loci_count"] == 24
        assert res["profiles"]["TH01"]["alleles"] == ["6", "9.3"]
        assert res["profiles"]["TH01"]["is_microvariant"] is True
        assert res["profiles"]["TH01"]["rfu"] == [1500, 1420]
        assert res["profiles"]["AMEL"]["alleles"] == ["X", "Y"]
        assert res["audit"]["iso17025_compliant"] is True
        assert len(res["audit"]["raw_command_hash"]) == 64
        assert len(res["audit"]["canonical_state_hash"]) == 64

    def test_vector_cli_02_ystr_27_locus_batch(self):
        """VECTOR_CLI_02: Complete 27-Locus Y-FILER Plus Batch Entry (ystr set-batch)."""
        cmd = (
            'ystr set-batch --data "DYS19:14;DYS389I:13;DYS389II:29;DYS390:24;DYS391:11;DYS392:13;DYS393:13;'
            'DYS385a/b:11,14;DYS437:15;DYS438:12;DYS439:12;DYS448:19;DYS456:15;DYS458:17;DYS635:23;'
            'Y-GATA-H4:12;DYS481:22;DYS533:12;DYS549:12;DYS570:17;DYS576:18;DYS643:10;DYS518:38;DYS627:21;'
            'DYS449:30;DYF387S1a/b:35,37;DYS460:11" --mode STRICT'
        )
        res = ForensicCliBatchParser.execute_command(cmd)

        assert res["domain"] == "Y_STR"
        assert res["status"] == "COMMITTED"
        assert res["loci_count"] == 27
        assert res["haplotype"]["DYS385a/b"]["copy_number"] == 2
        assert res["haplotype"]["DYS385a/b"]["alleles"] == ["11", "14"]
        assert res["haplotype"]["DYS570"]["is_rapidly_mutating"] is True
        assert res["haplotype"]["DYF387S1a/b"]["is_rapidly_mutating"] is True
        assert res["haplotype"]["DYS19"]["is_rapidly_mutating"] is False

    def test_vector_cli_03_mtdna_dloop_batch(self):
        """VECTOR_CLI_03: Mitochondrial DNA D-Loop Mutation Batch (mtdna set-batch)."""
        cmd = 'mtdna set-batch --data "263G, 315.1C, 524del, 16093Y, 16189R, 16519C" --ref rCRS'
        res = ForensicCliBatchParser.execute_command(cmd)

        assert res["domain"] == "MITOCHONDRIAL_DNA"
        assert res["reference_sequence"] == "rCRS_NC_012920.1"
        assert res["status"] == "COMMITTED"
        assert res["variant_count"] == 6

        var_map = {v["empop_notation"]: v for v in res["aligned_variants"]}
        assert var_map["263G"]["variant_type"] == "SUBSTITUTION"
        assert var_map["315.1C"]["variant_type"] == "INSERTION"
        assert var_map["524del"]["variant_type"] == "DELETION"
        assert var_map["16093Y"]["variant_type"] == "POINT_HETEROPLASMY"
        assert var_map["16093Y"]["is_heteroplasmy"] is True
        assert set(var_map["16093Y"]["base_components"]) == {"C", "T"}
        assert var_map["16189R"]["variant_type"] == "POINT_HETEROPLASMY"
        assert set(var_map["16189R"]["base_components"]) == {"A", "G"}

    def test_vector_cli_04_snp_aim_ancestry_batch(self):
        """VECTOR_CLI_04: 55-SNP AIM Continental Ancestry Batch Entry (snp set-batch)."""
        cmd = 'snp set-batch --data "rs12913832:2, rs1805007:1, rs16891982:0, rs1426654:2, rs1042602:1, rs1800404:0, rs28777:2, rs12203592:1"'
        res = ForensicCliBatchParser.execute_command(cmd)

        assert res["domain"] == "SNP_ANCESTRY"
        assert res["panel_name"] == "Kidd_55_AISNP_Panel"
        assert res["status"] == "COMMITTED"
        assert res["snp_count"] == 8
        assert res["genotypes"]["rs12913832"]["dosage"] == 2
        assert res["genotypes"]["rs12913832"]["effect_allele"] == "G"
        assert res["genotypes"]["rs1805007"]["dosage"] == 1
        assert res["genotypes"]["rs16891982"]["dosage"] == 0
        assert res["ancestry_inference_ready"] is True

    def test_vector_cli_05_snp_hirisplex_phenotype_batch(self):
        """VECTOR_CLI_05: 41-SNP HIrisPlex-S Phenotype Batch Entry (snp set-batch)."""
        cmd = 'snp set-batch --data "rs12913832:G/G, rs1805007:C/T, rs16891982:C/C, rs12203592:C/T, rs1042602:C/A, rs12821256:T/T, rs28777:A/A"'
        res = ForensicCliBatchParser.execute_command(cmd)

        assert res["domain"] == "SNP_PHENOTYPE"
        assert res["panel_name"] == "HIrisPlex_S_41_Panel"
        assert res["status"] == "COMMITTED"
        assert res["snp_count"] == 7
        assert res["phenotype_markers"]["rs12913832"]["genotype"] == "G/G"
        assert res["phenotype_markers"]["rs12913832"]["derived_dosage"] == 2
        assert res["phenotype_markers"]["rs1805007"]["genotype"] == "C/T"
        assert res["phenotype_markers"]["rs1805007"]["derived_dosage"] == 1
        assert res["phenotype_prediction_ready"] is True

    def test_vector_cli_06_cpg_visage_age_batch(self):
        """VECTOR_CLI_06: VISAGE 5-CpG Epigenetic Aging Batch Entry (cpg set-batch)."""
        cmd = 'cpg set-batch --data "ELOVL2:0.42, FHL2:0.38, PENK:0.31, TRIM59:0.33, KLF14:0.28" --tissue BLOOD'
        res = ForensicCliBatchParser.execute_command(cmd)

        assert res["domain"] == "EPIGENETIC_AGE"
        assert res["panel_name"] == "VISAGE_5_CpG_Core_Clock"
        assert res["tissue_calibration"] == "BLOOD"
        assert res["cpg_count"] == 5
        assert res["methylation_profile"]["ELOVL2"]["beta_fraction"] == 0.42
        assert res["methylation_profile"]["ELOVL2"]["m_value"] == pytest.approx(-0.465, abs=0.01)
        assert res["age_estimation_model_output"]["calibrated_tissue"] == "BLOOD"
        assert res["age_estimation_model_output"]["predicted_chronological_age_years"] > 0


# ═══════════════════════════════════════════════════════════════════════════════
# 2. SINGLE LOCUS MUTATION COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

class TestSingleLocusCommands:
    """Verifies single locus ingestion commands (str set, ystr set, mtdna set, snp set, cpg set)."""

    def test_single_str_set(self):
        cmd = "str set D8S1179 12,14 1150,1120"
        res = ForensicCliBatchParser.execute_command(cmd)
        assert res["domain"] == "AUTOSOMAL_STR"
        assert "D8S1179" in res["profiles"]
        assert res["profiles"]["D8S1179"]["alleles"] == ["12", "14"]
        assert res["profiles"]["D8S1179"]["rfu"] == [1150, 1120]

    def test_single_ystr_set(self):
        cmd = "ystr set DYS570 17"
        res = ForensicCliBatchParser.execute_command(cmd)
        assert res["domain"] == "Y_STR"
        assert res["haplotype"]["DYS570"]["alleles"] == ["17"]
        assert res["haplotype"]["DYS570"]["is_rapidly_mutating"] is True

    def test_single_mtdna_set(self):
        cmd = "mtdna set 263 G"
        res = ForensicCliBatchParser.execute_command(cmd)
        assert res["domain"] == "MITOCHONDRIAL_DNA"
        assert res["aligned_variants"][0]["empop_notation"] == "263G"

    def test_single_snp_set(self):
        cmd = "snp set rs12913832 2"
        res = ForensicCliBatchParser.execute_command(cmd)
        assert res["domain"] == "SNP_ANCESTRY"
        assert res["genotypes"]["rs12913832"]["dosage"] == 2

    def test_single_cpg_set(self):
        cmd = "cpg set ELOVL2 0.42"
        res = ForensicCliBatchParser.execute_command(cmd)
        assert res["domain"] == "EPIGENETIC_AGE"
        assert res["methylation_profile"]["ELOVL2"]["beta_fraction"] == 0.42


# ═══════════════════════════════════════════════════════════════════════════════
# 3. SYNTAX VALIDATION & ERROR HANDLING
# ═══════════════════════════════════════════════════════════════════════════════

class TestValidationAndAtomicity:
    """Verifies strict vs lenient execution modes and error reporting."""

    def test_invalid_microvariant_suffix_rejected_strict(self):
        cmd = 'str set-batch --data "TH01:9.4" --mode STRICT'
        with pytest.raises(CliSyntaxError) as exc:
            ForensicCliBatchParser.execute_command(cmd)
        assert "Invalid microvariant suffix" in str(exc.value)

    def test_invalid_cpg_fraction_rejected_strict(self):
        cmd = 'cpg set-batch --data "ELOVL2:1.45" --mode STRICT'
        with pytest.raises(CliSyntaxError) as exc:
            ForensicCliBatchParser.execute_command(cmd)
        assert "must be within [0.0, 1.0]" in str(exc.value)

    def test_lenient_mode_collects_warnings_without_crash(self):
        cmd = 'str set-batch --data "TH01:9.4;D8S1179:13,14" --mode LENIENT'
        res = ForensicCliBatchParser.execute_command(cmd)
        assert res["status"] == "COMMITTED"
        assert len(res["warnings"]) >= 1
        assert "D8S1179" in res["profiles"]


# ═══════════════════════════════════════════════════════════════════════════════
# 4. FASTAPI ROUTE INTEGRATION TEST
# ═══════════════════════════════════════════════════════════════════════════════

class TestFastApiCliBatchEndpoint:
    """Verifies the /api/v1/forensic/terminal/cli-batch REST API endpoint."""

    def test_api_cli_batch_success(self):
        payload = {
            "command_line": 'str set-batch --data "D8S1179:12,14;TH01:6,9.3" --rfu "D8S1179:1150,1120;TH01:1500,1420"'
        }
        resp = client.post("/api/v1/forensic/terminal/cli-batch", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["domain"] == "AUTOSOMAL_STR"
        assert data["status"] == "COMMITTED"
        assert "transaction_id" in data
        assert "audit" in data
        assert data["audit"]["iso17025_compliant"] is True

    def test_api_cli_batch_syntax_error(self):
        payload = {
            "command_line": 'str set-batch --data "TH01:9.4" --mode STRICT'
        }
        resp = client.post("/api/v1/forensic/terminal/cli-batch", json=payload)
        assert resp.status_code == 400
        data = resp.json()
        assert "CLI_SYNTAX_ERROR" in str(data)
