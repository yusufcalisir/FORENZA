"""
Integration Tests for FORENZA Forensic Microbiology & Thanatometagenomics REST API Endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.microbiology_routes import router as microbiology_router

app = FastAPI()
app.include_router(microbiology_router, prefix="/api/v1")
client = TestClient(app)


class TestMicrobiologyApiEndpoints:
    """Tests all Forensic Microbiology HTTP endpoints."""

    def test_classify_endpoint(self):
        payload = {
            "profile": {
                "sample_id": "TEST_ORAL_01",
                "sample_type": "BODY_TRACE",
                "taxa": [
                    {"genus_name": "Streptococcus", "phylum_name": "Bacillota", "relative_abundance": 0.65},
                    {"genus_name": "Veillonella", "phylum_name": "Bacillota", "relative_abundance": 0.25},
                    {"genus_name": "Prevotella", "phylum_name": "Bacteroidota", "relative_abundance": 0.10}
                ]
            }
        }
        resp = client.post("/api/v1/forensic/microbiology/classify", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["dominant_genus"] == "Streptococcus"
        assert data["dominant_phylum"] == "Bacillota"
        assert data["shannon_diversity_index"] > 0.0

    def test_body_site_origin_endpoint(self):
        payload = {
            "profile": {
                "sample_id": "TEST_SKIN_01",
                "sample_type": "BODY_TRACE",
                "taxa": [
                    {"genus_name": "Cutibacterium", "phylum_name": "Actinomycetota", "relative_abundance": 0.70},
                    {"genus_name": "Staphylococcus", "phylum_name": "Bacillota", "relative_abundance": 0.20},
                    {"genus_name": "Corynebacterium", "phylum_name": "Actinomycetota", "relative_abundance": 0.10}
                ]
            }
        }
        resp = client.post("/api/v1/forensic/microbiology/body-site-origin", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["predicted_body_site"] == "SEBACEOUS_SKIN"
        assert data["site_confidence_score"] >= 0.70

    def test_thanato_pmi_endpoint(self):
        payload = {
            "profile": {
                "sample_id": "VECTOR_MB_01_BUCCAL",
                "sample_type": "BUCCAL_SWAB",
                "taxa": [
                    {"taxon_name": "Streptococcus_salivarius", "relative_abundance": 0.082},
                    {"taxon_name": "Prevotella_melaninogenica", "relative_abundance": 0.215},
                    {"taxon_name": "Veillonella_dispar", "relative_abundance": 0.142},
                    {"taxon_name": "Clostridium_perfringens", "relative_abundance": 0.284},
                    {"taxon_name": "Enterobacteriaceae_unclassified", "relative_abundance": 0.186},
                    {"taxon_name": "Fusobacterium_nucleatum", "relative_abundance": 0.091}
                ]
            },
            "ambient_temp_celsius": 20.0,
            "base_temp_celsius": 0.0
        }
        resp = client.post("/api/v1/forensic/microbiology/thanato-pmi", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["predicted_add"] == 82.5
        assert data["predicted_pmi_hours"] == 99.0
        assert data["conformal_add_interval"]["lower_bound"] == 68.0
        assert data["conformal_add_interval"]["upper_bound"] == 97.0

    def test_touch_trace_match_endpoint(self):
        payload = {
            "evidentiary_profile": {
                "sample_id": "STEERING_WHEEL_TRACE",
                "sample_type": "TOUCH_TRACE",
                "taxa": [
                    {"taxon_name": "Cutibacterium_acnes_clade_IA", "relative_abundance": 0.55},
                    {"taxon_name": "Staphylococcus_epidermidis_SNP1", "relative_abundance": 0.25},
                    {"taxon_name": "Corynebacterium_jeikeium_SNP4", "relative_abundance": 0.12},
                    {"taxon_name": "Micrococcus_luteus", "relative_abundance": 0.08}
                ]
            },
            "reference_profile": {
                "sample_id": "SUSPECT_PALM_SWAB",
                "sample_type": "TOUCH_TRACE",
                "taxa": [
                    {"taxon_name": "Cutibacterium_acnes_clade_IA", "relative_abundance": 0.52},
                    {"taxon_name": "Staphylococcus_epidermidis_SNP1", "relative_abundance": 0.28},
                    {"taxon_name": "Corynebacterium_jeikeium_SNP4", "relative_abundance": 0.11},
                    {"taxon_name": "Micrococcus_luteus", "relative_abundance": 0.09}
                ]
            },
            "panel_type": "HIDSKINPLEX_PLUS"
        }
        resp = client.post("/api/v1/forensic/microbiology/touch-trace-match", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["metrics"]["calibrated_likelihood_ratio"] >= 10000.0
        assert "VERY_STRONG" in data["enfsi_reporting"]["evidential_tier"]
        assert "Prosecutor's Fallacy" in data["enfsi_reporting"]["prosecutors_fallacy_shield_en"]

    def test_body_fluid_endpoint(self):
        payload = {
            "profile": {
                "sample_id": "FABRIC_STAIN_04",
                "sample_type": "BODY_FLUID",
                "taxa": [
                    {"taxon_name": "Lactobacillus_crispatus", "relative_abundance": 0.62},
                    {"taxon_name": "Lactobacillus_iners", "relative_abundance": 0.22},
                    {"taxon_name": "Gardnerella_vaginalis", "relative_abundance": 0.10},
                    {"taxon_name": "Cutibacterium_acnes", "relative_abundance": 0.04},
                    {"taxon_name": "Streptococcus_salivarius", "relative_abundance": 0.02}
                ]
            }
        }
        resp = client.post("/api/v1/forensic/microbiology/body-fluid", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["predicted_fluid_origin"] == "VAGINAL_FLUID"
        assert data["calibrated_probabilities"]["vaginal_fluid"] == 0.887

    def test_soil_cdi_endpoint(self):
        payload = {
            "soil_profile": {
                "sample_id": "VECTOR_MB_02_SOIL_CDI",
                "sample_type": "SOIL_CDI",
                "taxa": [
                    {"taxon_name": "Ignatzschineria_larvae", "relative_abundance": 0.312},
                    {"taxon_name": "Wohlfahrtiimonas_chitiniclastica", "relative_abundance": 0.184},
                    {"taxon_name": "Acinetobacter_radioresistens", "relative_abundance": 0.126},
                    {"taxon_name": "Yarrowia_lipolytica_ITS", "relative_abundance": 0.218},
                    {"taxon_name": "Candida_albidus_ITS", "relative_abundance": 0.115},
                    {"taxon_name": "Native_Acidobacteriota_Soil", "relative_abundance": 0.045}
                ]
            }
        }
        resp = client.post("/api/v1/forensic/microbiology/soil-cdi", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["stage_probabilities"]["dominant_stage"] == "ADVANCED_DECAY"
        assert data["stage_probabilities"]["advanced_decay"] == 0.841
