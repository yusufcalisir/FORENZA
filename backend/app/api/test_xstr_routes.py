"""
Integration Test Suite for FORENZA X-STR Kinship REST API (Module 2.2).
Tests all 8 endpoints and HTTP 422 validation error handling.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from node.services.forensic.xstr.xstr_reference_datasets import (
    XSTR_CASEWORK_COHORTS,
    XSTR_GOLD_STANDARDS,
)

client = TestClient(app)


class TestXStrApiEndpoints:
    """Integration test suite for /forensic/lineage/xstr/* API endpoints."""

    def test_evaluate_kinship_phs_endpoint(self):
        phs = XSTR_CASEWORK_COHORTS["VECTOR_P2_02_PATERNAL_HALF_SISTERS"]
        payload = {
            "profile_a": phs.profile_a,
            "profile_b": phs.profile_b,
            "sex_a": "FEMALE",
            "sex_b": "FEMALE",
            "relationship": "PATERNAL_HALF_SISTERS",
        }
        res = client.post("/api/v1/forensic/lineage/xstr/evaluate-kinship", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["evaluated_loci_count"] == 12
        assert data["combined_ki_x"] > 10000.0
        assert data["is_excluded"] is False
        assert len(data["linkage_group_results"]) == 4
        assert "Support for Paternal Kinship" in data["verbal_predicate_en"]

    def test_evaluate_kinship_father_daughter_endpoint(self):
        fd = XSTR_CASEWORK_COHORTS["COHORT_FATHER_DAUGHTER_DUO"]
        payload = {
            "profile_a": fd.profile_a,
            "profile_b": fd.profile_b,
            "sex_a": "MALE",
            "sex_b": "FEMALE",
            "relationship": "FATHER_DAUGHTER",
        }
        res = client.post("/api/v1/forensic/lineage/xstr/evaluate-kinship", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["evaluated_loci_count"] == 12
        assert data["combined_ki_x"] > 350000.0
        assert data["is_excluded"] is False

    def test_kosambi_map_endpoint(self):
        payload = {"genetic_distance_cm": 18.5}
        res = client.post("/api/v1/forensic/lineage/xstr/kosambi-map", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["recombination_fraction_r"] > 0.0
        assert data["recombination_fraction_r"] < 0.50

    def test_kosambi_recombination_alias_endpoint(self):
        payload = {"genetic_distance_cm": 50.0}
        res = client.post("/api/v1/forensic/lineage/xstr/kosambi-recombination", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert abs(data["recombination_fraction_r"] - 0.380797) < 1e-4

    def test_get_panel_metadata_endpoint(self):
        res = client.get("/api/v1/forensic/lineage/xstr/panel-metadata")
        assert res.status_code == 200
        data = res.json()
        assert data["total_loci"] == 12
        assert data["total_linkage_groups"] == 4
        assert len(data["linkage_groups"]) == 4
        assert len(data["loci"]) == 12

    def test_list_linkage_groups_endpoint(self):
        res = client.get("/api/v1/forensic/lineage/xstr/linkage-groups")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 4
        group_ids = [d["group_id"] for d in data]
        assert set(group_ids) == {"LG1", "LG2", "LG3", "LG4"}

    def test_get_population_frequencies_endpoint(self):
        res = client.get("/api/v1/forensic/lineage/xstr/population-frequencies")
        assert res.status_code == 200
        data = res.json()
        assert "Tillmar" in data["dataset"]
        assert len(data["frequencies"]) == 12

    def test_list_gold_standards_endpoint(self):
        res = client.get("/api/v1/forensic/lineage/xstr/gold-standards")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 4
        sample_ids = [d["sample_id"] for d in data]
        assert "NA12878_CEU_FEMALE" in sample_ids
        assert "SRM_2391d_COMP_A_MALE" in sample_ids

    def test_list_casework_cohorts_endpoint(self):
        res = client.get("/api/v1/forensic/lineage/xstr/casework-cohorts")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 3

    def test_get_reporting_disclaimer_endpoint(self):
        res = client.get("/api/v1/forensic/lineage/xstr/reporting-disclaimer")
        assert res.status_code == 200
        data = res.json()
        assert data["has_patrilineal_disclaimer"] is True
        assert "ISFG" in data["disclaimer_text_en"]
        assert "ISFG" in data["disclaimer_text_tr"]

    def test_422_validation_errors(self):
        # Male with diallelic genotype
        bad_male_payload = {
            "profile_a": {"DXS10148": [24.0, 26.0]},
            "profile_b": {"DXS10148": [26.0]},
            "sex_a": "MALE",
            "sex_b": "MALE",
            "relationship": "FATHER_DAUGHTER",
        }
        res_male = client.post("/api/v1/forensic/lineage/xstr/evaluate-kinship", json=bad_male_payload)
        assert res_male.status_code == 422

        # Negative Kosambi distance
        bad_kosambi = {"genetic_distance_cm": -10.0}
        res_kos = client.post("/api/v1/forensic/lineage/xstr/kosambi-map", json=bad_kosambi)
        assert res_kos.status_code == 422
