"""
Integration Test Suite for FORENZA Y-STR Haplotype Forensics REST API (Module 2.1).
Tests all 11 endpoints and HTTP 422 validation error handling.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from node.services.forensic.ystr.ystr_reference_datasets import (
    GOLD_STANDARD_INDIVIDUALS,
)

client = TestClient(app)


class TestYStrApiEndpoints:
    """Integration test suite for /forensic/lineage/ystr/* API endpoints."""

    def test_evaluate_paternal_kinship_exact_match(self):
        ref = GOLD_STANDARD_INDIVIDUALS["SRM_2391d_COMP_A"].y_str_haplotype
        payload = {
            "evidence_id": "EV-01",
            "suspect_id": "SUSP-01",
            "evidence_markers": ref,
            "suspect_markers": ref,
            "meioses_m": 1,
            "database_size_n": 385000,
            "theta": 0.03,
        }
        res = client.post("/api/v1/forensic/lineage/ystr/evaluate-paternal-kinship", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["matching_loci_count"] == 25
        assert data["mutated_loci_count"] == 0
        assert data["paternal_lr"] > 10000.0
        assert data["is_lineage_excluded"] is False
        assert "Extremely Strong Support" in data["verbal_predicate_en"]
        assert "MANDATORY ISFG" in data["patrilineal_disclaimer_en"]

    def test_evaluate_paternal_kinship_unrelated_exclusion(self):
        ref_a = GOLD_STANDARD_INDIVIDUALS["SRM_2391d_COMP_A"].y_str_haplotype
        ref_b = GOLD_STANDARD_INDIVIDUALS["NA18507_HG005"].y_str_haplotype
        payload = {
            "evidence_id": "EV-EUR",
            "suspect_id": "SUSP-EAS",
            "evidence_markers": ref_a,
            "suspect_markers": ref_b,
            "meioses_m": 1,
            "database_size_n": 385000,
            "theta": 0.03,
        }
        res = client.post("/api/v1/forensic/lineage/ystr/evaluate-paternal-kinship", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["is_lineage_excluded"] is True
        assert data["paternal_lr"] == 0.0
        assert data["log10_paternal_lr"] == -300.0
        assert "Definitive Exclusion" in data["verbal_predicate_en"]

    def test_clopper_pearson_bound_endpoint(self):
        payload = {
            "observed_count_k": 0,
            "database_size_n": 385000,
            "alpha": 0.05,
        }
        res = client.post("/api/v1/forensic/lineage/ystr/clopper-pearson-bound", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert abs(data["p_upper_bound"] - 7.7810723e-06) < 1e-10
        assert abs(data["equivalent_match_ratio"] - 128517.0) < 2.0

    def test_brenner_frequency_endpoint(self):
        payload = {
            "observed_count_k": 0,
            "database_size_n": 385000,
            "theta": 0.03,
        }
        res = client.post("/api/v1/forensic/lineage/ystr/brenner-frequency", json=payload)
        assert res.status_code == 200
        data = res.json()
        expected_p = 0.03 / 385000.03
        assert abs(data["p_brenner"] - expected_p) < 1e-12

    def test_predict_haplogroup_endpoint(self):
        ref = GOLD_STANDARD_INDIVIDUALS["SRM_2391d_COMP_A"].y_str_haplotype
        payload = {
            "y_str_markers": ref,
        }
        res = client.post("/api/v1/forensic/lineage/ystr/predict-haplogroup", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["predicted_haplogroup"] == "R1b"
        assert data["confidence_score"] > 0.50
        assert "M269" in data["primary_snp_marker"]
        assert abs(sum(data["bayesian_posteriors"].values()) - 1.0) < 1e-5

    def test_decouple_dys389_endpoint(self):
        payload = {
            "dys389i": 13.0,
            "dys389ii_total": 29.0,
        }
        res = client.post("/api/v1/forensic/lineage/ystr/decouple-dys389", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["dys389_2_pure"] == 16.0

    def test_mixture_contributors_endpoint(self):
        payload = {
            "locus_allele_counts": {
                "DYS19": 2,
                "DYS389I": 2,
                "DYS385a/b": 3,
                "DYF387S1a/b": 4,
            }
        }
        res = client.post("/api/v1/forensic/lineage/ystr/mixture-contributors", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["minimum_male_contributors"] == 2

    def test_get_panel_metadata_endpoint(self):
        res = client.get("/api/v1/forensic/lineage/ystr/panel-metadata")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 25
        loci_names = [d["locus_name"] for d in data]
        assert "DYS19" in loci_names
        assert "DYS385a/b" in loci_names
        assert "DYS518" in loci_names

    def test_list_metapopulations_endpoint(self):
        res = client.get("/api/v1/forensic/lineage/ystr/metapopulations")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 6
        codes = [d["code"] for d in data]
        assert "GLOBAL" in codes
        assert "WEST_EURASIAN" in codes

    def test_list_gold_standards_endpoint(self):
        res = client.get("/api/v1/forensic/lineage/ystr/gold-standards")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 5
        sample_ids = [d["sample_id"] for d in data]
        assert "SRM_2391d_COMP_A" in sample_ids
        assert "HG002_NA24385" in sample_ids

    def test_list_casework_cohorts_endpoint(self):
        res = client.get("/api/v1/forensic/lineage/ystr/casework-cohorts")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 4
        cohort_ids = [d["cohort_id"] for d in data]
        assert "COHORT_PATERNAL_DUO_FATHER_SON" in cohort_ids
        assert "COHORT_UNRELATED_MALES" in cohort_ids

    def test_get_patrilineal_disclaimer_endpoint(self):
        res = client.get("/api/v1/forensic/lineage/ystr/patrilineal-disclaimer")
        assert res.status_code == 200
        data = res.json()
        assert data["has_patrilineal_disclaimer"] is True
        assert data["prosecutors_fallacy_shield_active"] is True
        assert "ISFG" in data["disclaimer_text_en"]
        assert "ISFG" in data["disclaimer_text_tr"]

    def test_422_validation_error_handling(self):
        # Invalid database size N <= 0
        bad_cp = {"observed_count_k": 0, "database_size_n": -50, "alpha": 0.05}
        res_cp = client.post("/api/v1/forensic/lineage/ystr/clopper-pearson-bound", json=bad_cp)
        assert res_cp.status_code == 422

        # Invalid DYS389II < DYS389I
        bad_dys = {"dys389i": 15.0, "dys389ii_total": 12.0}
        res_dys = client.post("/api/v1/forensic/lineage/ystr/decouple-dys389", json=bad_dys)
        assert res_dys.status_code == 422

        # Female null profile without common loci
        bad_kinship = {
            "evidence_id": "EV",
            "suspect_id": "SUSP",
            "evidence_markers": {},
            "suspect_markers": {},
            "meioses_m": 1,
            "database_size_n": 385000,
            "theta": 0.03,
        }
        res_kin = client.post("/api/v1/forensic/lineage/ystr/evaluate-paternal-kinship", json=bad_kinship)
        assert res_kin.status_code == 422
