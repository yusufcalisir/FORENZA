"""
Integration Tests for FORENZA Machine Learning STR Calling REST API Endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestMLSTRApiEndpoints:
    """Tests all ML STR HTTP endpoints."""

    def test_extract_features_endpoint(self):
        payload = {
            "locus_name": "TH01",
            "peak_id": "Peak_9.3",
            "peak_height": 1850.0,
            "bp_position": 180.0,
            "major_allele_bp": 180.0,
            "sequence_string": "[AATG]6 ATG [AATG]3"
        }
        resp = client.post("/api/v1/forensic/ml-str/extract-features", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["locus_name"] == "TH01"
        assert len(data["vector"]) == 24
        assert data["morphology"]["peak_height"] == 1850.0

    def test_classify_peak_endpoint(self):
        # Extract first
        feat_resp = client.post(
            "/api/v1/forensic/ml-str/extract-features",
            json={
                "locus_name": "D21S11",
                "peak_id": "Allele_30",
                "peak_height": 2400.0,
                "bp_position": 214.0,
                "major_allele_bp": 214.0
            }
        )
        feat_data = feat_resp.json()

        # Classify
        resp = client.post("/api/v1/forensic/ml-str/classify-peak", json={"feature_vector": feat_data})
        assert resp.status_code == 200
        data = resp.json()
        assert data["predicted_class"] == "CLASS_TRUE_ALLELE"
        assert data["is_true_allele_candidate"] is True

    def test_translate_isfg_endpoint(self):
        payload = {
            "locus_name": "D3S1358",
            "sequence_or_bracketed_string": "[TCTA]1 [TCTG]3 [TCTA]12"
        }
        resp = client.post("/api/v1/forensic/ml-str/translate-isfg", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["locus_name"] == "D3S1358"
        assert data["ce_equivalent_length_call"] == 16.0
        assert data["level_2_alignment_mapping"]["chromosome"] == "chr3"

    def test_get_golden_vectors_endpoint(self):
        resp = client.get("/api/v1/forensic/ml-str/golden-vectors")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 4
        assert any(v["vector_id"] == "VECTOR_MLSTR_01" for v in data)
