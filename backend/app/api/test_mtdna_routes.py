"""
Integration Test Suite for FORENZA mtDNA REST API (Module 2.3).
Tests all 9 endpoints and HTTP 422 validation error handling.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from node.services.forensic.mtdna.mtdna_reference_datasets import (
    MTDNA_CASEWORK_COHORTS,
    MTDNA_GOLD_STANDARDS,
)

client = TestClient(app)


class TestMtDnaApiEndpoints:
    """Integration test suite for /forensic/lineage/mtdna/* API endpoints."""

    def test_evaluate_maternal_match_inclusion(self):
        cohort = MTDNA_CASEWORK_COHORTS["BENCHMARK_LINEAGE_A_EUR"]
        payload = {
            "variants_a": cohort.profile_a_variants,
            "variants_b": cohort.profile_b_variants,
            "n_empop": cohort.database_size_n,
            "empop_observed_k": cohort.expected_matches_k,
        }
        res = client.post("/api/v1/forensic/lineage/mtdna/evaluate-maternal-match", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["match_status"] == "CANNOT_BE_EXCLUDED"
        assert data["maternal_lr"] > 25.0
        assert "Support for Same Maternal Lineage" in data["verbal_predicate_en"]

    def test_evaluate_maternal_match_with_profile_schemas(self):
        payload = {
            "evidence": {
                "profile_id": "EV-01",
                "haplogroup": "H1",
                "variants": [
                    {"position": 73, "ref_base": "A", "alt_base": "G", "region": "HV2", "variant_type": "SNP"},
                    {"position": 263, "ref_base": "A", "alt_base": "G", "region": "HV2", "variant_type": "SNP"},
                ],
            },
            "suspect": {
                "profile_id": "SUS-01",
                "haplogroup": "H1",
                "variants": [
                    {"position": 73, "ref_base": "A", "alt_base": "G", "region": "HV2", "variant_type": "SNP"},
                    {"position": 263, "ref_base": "A", "alt_base": "G", "region": "HV2", "variant_type": "SNP"},
                ],
            },
            "n_empop": 48500,
            "empop_observed_k": 0,
        }
        res = client.post("/api/v1/forensic/lineage/mtdna/evaluate-maternal-match", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["match_status"] == "CANNOT_BE_EXCLUDED"
        assert data["differing_positions_count"] == 0
        assert data["maternal_lr"] > 10000.0

    def test_empop_upper_bound_k0_endpoint(self):
        payload = {"k": 0, "n_empop": 48500, "alpha": 0.05}
        res = client.post("/api/v1/forensic/lineage/mtdna/empop-upper-bound", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["is_unobserved"] is True
        assert abs(data["p_upper_bound"] - 6.1764e-5) < 1e-7
        assert data["maternal_lr"] > 10000.0

    def test_database_frequency_alias_endpoint(self):
        payload = {"k": 5, "n_empop": 48500, "alpha": 0.05}
        res = client.post("/api/v1/forensic/lineage/mtdna/database-frequency", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["is_unobserved"] is False
        assert data["observed_count_k"] == 5

    def test_get_panel_metadata_endpoint(self):
        res = client.get("/api/v1/forensic/lineage/mtdna/panel-metadata")
        assert res.status_code == 200
        data = res.json()
        assert "rCRS" in data["reference_genome"]
        assert len(data["hypervariable_regions"]) == 3
        assert data["isfg_rules_active"] is True

    def test_get_reference_metadata_alias(self):
        res = client.get("/api/v1/forensic/lineage/mtdna/reference-metadata")
        assert res.status_code == 200
        data = res.json()
        assert "NC_012920.1" in data["genbank_accession"]

    def test_list_control_region_domains_endpoint(self):
        res = client.get("/api/v1/forensic/lineage/mtdna/control-region-domains")
        assert res.status_code == 200
        data = res.json()
        assert len(data["domains"]) == 7

    def test_list_gold_standards_endpoint(self):
        res = client.get("/api/v1/forensic/lineage/mtdna/gold-standards")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 5
        sample_ids = [d["sample_id"] for d in data]
        assert "NA12878_CEU_FEMALE" in sample_ids
        assert "NA19240_YRI_FEMALE" in sample_ids

    def test_list_casework_cohorts_endpoint(self):
        res = client.get("/api/v1/forensic/lineage/mtdna/casework-cohorts")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 5

    def test_get_reporting_disclaimer_endpoint(self):
        res = client.get("/api/v1/forensic/lineage/mtdna/reporting-disclaimer")
        assert res.status_code == 200
        data = res.json()
        assert data["has_matrilineal_disclaimer"] is True
        assert "ISFG" in data["disclaimer_text_en"]
        assert "ISFG" in data["disclaimer_text_tr"]

    def test_422_validation_errors(self):
        # Invalid variant notation
        bad_payload = {
            "variants_a": ["INVALID_NOTATION_XYZ"],
            "variants_b": ["263G"],
        }
        res_bad = client.post("/api/v1/forensic/lineage/mtdna/evaluate-maternal-match", json=bad_payload)
        assert res_bad.status_code == 422
