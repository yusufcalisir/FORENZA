"""
Unit & Integration Tests for FORENZA Forensic Botany Package.
Tests plant DNA barcoding (rbcL, matK), palynological pollen morphology matching,
habitat origin inference, and API endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.botany.species import ForensicBotanyEngine, BotanicalSpecimenData
from node.services.forensic.botany.habitat import PlantHabitatAuditor, PlantAssemblageEntry
from app.api.botany_routes import router as botany_router

_app = FastAPI()
_app.include_router(botany_router, prefix="/api/v1")
client = TestClient(_app)

botany_engine = ForensicBotanyEngine()
habitat_auditor = PlantHabitatAuditor()


# ── DNA Barcoding & Species ID Tests ─────────────────────────────────────────

def test_plant_dna_barcoding_species_id():
    specimen = BotanicalSpecimenData(
        specimen_id="BOT-101",
        sample_type="POLLEN_GRAIN",
        rbcl_sequence="ATCGGTTACGAATTCCGCTA",
        pollen_aperture_type="BISACCATE",
        exine_ornamentation="RETICULATE"
    )

    res = botany_engine.identify_species(specimen)
    assert len(res.top_species_hits) > 0
    top = res.top_species_hits[0]
    assert top.species_name == "Pinus sylvestris"
    assert top.dna_similarity_score >= 0.95


def test_pollen_morphology_match():
    specimen = BotanicalSpecimenData(
        specimen_id="BOT-102",
        sample_type="POLLEN_GRAIN",
        pollen_aperture_type="TRICOLPATE",
        exine_ornamentation="PSILATE"
    )

    res = botany_engine.identify_species(specimen)
    quercus_hit = next(h for h in res.top_species_hits if h.species_name == "Quercus robur")
    assert quercus_hit.pollen_morphology_match is True


# ── Habitat Inference Tests ──────────────────────────────────────────────────

def test_habitat_origin_inference():
    assemblage = [
        PlantAssemblageEntry("Pinus sylvestris", 75.0)
    ]

    report = habitat_auditor.infer_habitat("BOT-CASE-201", assemblage)
    assert report.inferred_habitat_type == "MONTANE_CONIFEROUS"
    assert report.habitat_match_lr == 240.0


# ── API Endpoint Integration Tests ───────────────────────────────────────────

def test_api_botany_identify_endpoint():
    payload = {
        "specimen": {
            "specimen_id": "BOT-SAMPLE-501",
            "sample_type": "POLLEN_GRAIN",
            "rbcl_sequence": "ATCGGTTACGAATTCCGCTA",
            "pollen_aperture_type": "BISACCATE"
        }
    }

    resp = client.post("/api/v1/forensic/botany/identify", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["specimen_id"] == "BOT-SAMPLE-501"
    assert len(data["top_species_hits"]) > 0


def test_api_botany_habitat_inference_endpoint():
    payload = {
        "sample_id": "BOT-HABITAT-101",
        "assemblage": [
            {
                "species_name": "Taraxacum officinale",
                "abundance_percentage": 80.0
            }
        ]
    }

    resp = client.post("/api/v1/forensic/botany/habitat-inference", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["inferred_habitat_type"] == "URBAN_RUDERAL"
    assert data["habitat_match_lr"] > 1.0
