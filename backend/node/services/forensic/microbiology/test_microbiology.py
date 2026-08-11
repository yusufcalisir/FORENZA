"""
Unit & Integration Tests for FORENZA Forensic Microbiology Package.
Tests 16S rRNA taxonomic profiling, Shannon diversity index H', Bray-Curtis dissimilarity,
body site origin prediction (skin, oral, vaginal, gut), and API endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.microbiology.classifier import ForensicMicrobiologyEngine, MicrobialProfileData, TaxonAbundance
from node.services.forensic.microbiology.origin import MicrobialOriginAuditor
from app.api.microbiology_routes import router as microbiology_router

_app = FastAPI()
_app.include_router(microbiology_router, prefix="/api/v1")
client = TestClient(_app)

micro_engine = ForensicMicrobiologyEngine()
origin_auditor = MicrobialOriginAuditor()


# ── Taxonomic Profiling & Diversity Tests ────────────────────────────────────

def test_16s_taxonomic_classification():
    profile = MicrobialProfileData(
        sample_id="MIC-101",
        sample_type="BODY_TRACE",
        taxa=[
            TaxonAbundance("Cutibacterium", "Actinomycetota", 0.65),
            TaxonAbundance("Staphylococcus", "Bacillota", 0.25),
            TaxonAbundance("Corynebacterium", "Actinomycetota", 0.10),
        ]
    )

    res = micro_engine.classify_microbial_profile(profile)
    assert res.dominant_genus == "Cutibacterium"
    assert res.dominant_phylum == "Actinomycetota"
    assert res.shannon_diversity_index > 0.5


def test_bray_curtis_dissimilarity_identical():
    profile1 = MicrobialProfileData("S1", "TRACE", [TaxonAbundance("Cutibacterium", "Actinomycetota", 1.0)])
    profile2 = MicrobialProfileData("S2", "TRACE", [TaxonAbundance("Cutibacterium", "Actinomycetota", 1.0)])

    d = micro_engine.compute_bray_curtis_distance(profile1, profile2)
    assert d == 0.0


def test_bray_curtis_dissimilarity_completely_different():
    profile1 = MicrobialProfileData("S1", "TRACE", [TaxonAbundance("Cutibacterium", "Actinomycetota", 1.0)])
    profile2 = MicrobialProfileData("S2", "TRACE", [TaxonAbundance("Bacteroides", "Bacteroidota", 1.0)])

    d = micro_engine.compute_bray_curtis_distance(profile1, profile2)
    assert d == 1.0


# ── Body Site Origin Tests ───────────────────────────────────────────────────

def test_body_site_origin_skin_prediction():
    profile = MicrobialProfileData(
        sample_id="MIC-201",
        sample_type="BODY_TRACE",
        taxa=[
            TaxonAbundance("Cutibacterium", "Actinomycetota", 0.70),
            TaxonAbundance("Staphylococcus", "Bacillota", 0.20),
        ]
    )

    res = origin_auditor.predict_body_site_origin(profile)
    assert res.predicted_body_site == "SEBACEOUS_SKIN"
    assert res.origin_likelihood_ratio == 185.0


def test_body_site_origin_gut_prediction():
    profile = MicrobialProfileData(
        sample_id="MIC-202",
        sample_type="BODY_TRACE",
        taxa=[
            TaxonAbundance("Bacteroides", "Bacteroidota", 0.80),
            TaxonAbundance("Faecalibacterium", "Bacillota", 0.15),
        ]
    )

    res = origin_auditor.predict_body_site_origin(profile)
    assert res.predicted_body_site == "GUT_FECAL"
    assert res.origin_likelihood_ratio == 260.0


# ── API Endpoint Integration Tests ───────────────────────────────────────────

def test_api_microbiology_classify_endpoint():
    payload = {
        "profile": {
            "sample_id": "MIC-SAMPLE-301",
            "sample_type": "BODY_TRACE",
            "taxa": [
                {
                    "genus_name": "Streptococcus",
                    "phylum_name": "Bacillota",
                    "relative_abundance": 0.75
                }
            ]
        }
    }

    resp = client.post("/api/v1/forensic/microbiology/classify", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["sample_id"] == "MIC-SAMPLE-301"
    assert data["dominant_genus"] == "Streptococcus"


def test_api_microbiology_body_site_origin_endpoint():
    payload = {
        "profile": {
            "sample_id": "MIC-SAMPLE-302",
            "sample_type": "BODY_TRACE",
            "taxa": [
                {
                    "genus_name": "Lactobacillus",
                    "phylum_name": "Bacillota",
                    "relative_abundance": 0.90
                }
            ]
        }
    }

    resp = client.post("/api/v1/forensic/microbiology/body-site-origin", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["predicted_body_site"] == "VAGINAL_MUCOSA"
    assert data["origin_likelihood_ratio"] > 1.0
