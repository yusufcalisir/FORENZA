"""
Integration Tests for AURA LOGIC, Search, and Gateway REST API Endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAuraLogicRoutes:
    """Tests for AURA LOGIC AI Assistant Endpoint."""

    def test_aura_logic_chat_turkish(self):
        payload = {
            "message": "CODIS 24 lokus analizi ve LR hesabı hakkında bilgi verir misin?",
            "lang": "tr"
        }
        resp = client.post("/api/v1/aura-logic/chat", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "reply" in data
        assert len(data["reply"]) > 0
        assert "provider" in data

    def test_aura_logic_chat_english(self):
        payload = {
            "message": "Explain how Likelihood Ratio (LR) is computed for degraded DNA samples.",
            "lang": "en"
        }
        resp = client.post("/api/v1/aura-logic/chat", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "reply" in data
        assert len(data["reply"]) > 0

    def test_aura_logic_empty_message_rejection(self):
        payload = {
            "message": "   ",
            "lang": "tr"
        }
        resp = client.post("/api/v1/aura-logic/chat", json=payload)
        assert resp.status_code == 400


class TestSearchRoutes:
    """Tests for Genomic Vector STR Profile Similarity Search Endpoint."""

    def test_search_profiles_endpoint_valid(self):
        # 10 valid loci
        markers = {
            "D3S1358": {"allele_1": 15.0, "allele_2": 16.0, "is_homozygous": False},
            "VWA": {"allele_1": 17.0, "allele_2": 17.0, "is_homozygous": True},
            "FGA": {"allele_1": 21.0, "allele_2": 24.0, "is_homozygous": False},
            "D8S1179": {"allele_1": 12.0, "allele_2": 14.0, "is_homozygous": False},
            "D21S11": {"allele_1": 28.0, "allele_2": 30.0, "is_homozygous": False},
            "D18S51": {"allele_1": 13.0, "allele_2": 16.0, "is_homozygous": False},
            "D5S818": {"allele_1": 11.0, "allele_2": 12.0, "is_homozygous": False},
            "D13S317": {"allele_1": 9.0, "allele_2": 11.0, "is_homozygous": False},
            "D7S820": {"allele_1": 8.0, "allele_2": 10.0, "is_homozygous": False},
            "TH01": {"allele_1": 6.0, "allele_2": 9.3, "is_homozygous": False},
        }

        payload = {
            "str_markers": markers,
            "min_loci_threshold": 8
        }
        resp = client.post("/api/v1/search/", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "query_id" in data
        assert data["loci_valid"] == 10
        assert "results" in data

    def test_search_profiles_insufficient_loci(self):
        markers = {
            "TH01": {"allele_1": 6.0, "allele_2": 9.0, "is_homozygous": False},
            "vWA": {"allele_1": 15.0, "allele_2": 16.0, "is_homozygous": False},
        }
        payload = {
            "str_markers": markers,
            "min_loci_threshold": 8
        }
        resp = client.post("/api/v1/search/", json=payload)
        assert resp.status_code == 422


class TestGatewayRoutes:
    """Tests for Inter-Agency Law Enforcement Gateway Endpoint."""

    def test_gateway_status(self):
        resp = client.get("/api/v1/gateway/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "operational"
        assert data["registered_agencies"] >= 1

    def test_gateway_query_unauthorized(self):
        resp = client.post("/api/v1/gateway/query", json={"target_profile_id": "TEST_01"})
        assert resp.status_code == 422 or resp.status_code == 401

    def test_gateway_query_invalid_key(self):
        resp = client.post(
            "/api/v1/gateway/query",
            json={"target_profile_id": "TEST_01"},
            headers={"X-API-Key": "INVALID_KEY_12345"}
        )
        assert resp.status_code == 401
