import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestMPSSTRApiEndpoints:
    """Tests all MPS / NGS STR HTTP endpoints."""

    def test_parse_sequence_endpoint(self):
        payload = {
            "locus_name": "SE33",
            "sequence_string": "CTTC [CTTT]17_rs9362477[C>T]"
        }
        resp = client.post("/api/v1/forensic/mps-str/parse-sequence", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["locus_name"] == "SE33"
        assert data["ce_length_call"] == 18.0
        assert len(data["flanking_3p_variants"]) == 1
        assert data["flanking_3p_variants"][0]["rs_id"] == "rs9362477"

    def test_analyze_se33_endpoint(self):
        payload = {
            "sequence_alleles": [
                "CTTC [CTTT]17_rs9362477[C>T]",
                "CTTC [CTTT]10 TT [CTTT]16_rs1277875566[T>C]"
            ],
            "population": "CAUCASIAN"
        }
        resp = client.post("/api/v1/forensic/mps-str/analyze-se33", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["locus"] == "SE33"
        assert data["ce_genotype"] == "18, 27.2"
        assert data["information_gain_ratio"] >= 20.0
        assert data["is_fully_concordant"] is True

    def test_deconvolve_mixture_endpoint(self):
        payload = {
            "sample_id": "MIX_BENCHMARK_901",
            "locus_sequence_map": {
                "D3S1358": [
                    "[TCTA]1 [TCTG]3 [TCTA]11",
                    "[TCTA]1 [TCTG]3 [TCTA]12"
                ]
            },
            "contributors": [
                {
                    "contributor_id": "CONTRIB_1",
                    "mixture_proportion": 0.50,
                    "assigned_alleles": ["[TCTA]1 [TCTG]3 [TCTA]11"],
                    "ce_equivalent_alleles": [15.0]
                }
            ],
            "population": "GLOBAL_COMPOSITE"
        }
        resp = client.post("/api/v1/forensic/mps-str/deconvolve-mixture", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["sample_id"] == "MIX_BENCHMARK_901"
        assert len(data["loci_deconvolutions"]) == 1
        assert "ENFSI" in data["prosecutors_fallacy_shield_en"]

    def test_biostatistics_endpoint(self):
        payload = {
            "locus_names": ["SE33", "D3S1358", "D21S11", "VWA", "TH01"],
            "population": "GLOBAL_COMPOSITE"
        }
        resp = client.post("/api/v1/forensic/mps-str/biostatistics", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["loci_reports"]) == 5
        assert data["combined_power_of_discrimination"] > 0.9999

    def test_audit_linkage_endpoint(self):
        payload = {
            "d6s1043_lr": 150.0,
            "se33_lr": 3200.0,
            "apply_single_locus_fallback": True
        }
        resp = client.post("/api/v1/forensic/mps-str/audit-linkage", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["recombination_fraction_theta"] == 0.0440
        assert data["adjusted_joint_lr"] == 3200.0

    def test_get_golden_vectors_endpoint(self):
        resp = client.get("/api/v1/forensic/mps-str/golden-vectors")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 4
        assert any(v["vector_id"] == "VECTOR_MPS_01" for v in data)
