"""
Unit & Integration Tests for FORENZA Microscopy Intelligence & Hair Package.
Tests sperm cell morphometry, hair medullary index (I_medulla), species discrimination (Human vs. Animal),
follicular root sheath nDNA/mtDNA routing, and API endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.microscopy.classifier import MicroscopyIntelligenceEngine
from app.api.microscopy_routes import router as microscopy_router

_app = FastAPI()
_app.include_router(microscopy_router, prefix="/api/v1")
client = TestClient(_app)

micro_engine = MicroscopyIntelligenceEngine()


# ── Cell Morphometry & Hair Index Tests ─────────────────────────────────────

def test_sperm_cell_morphometry():
    cell = micro_engine.classify_sperm_cell("SPERM-1", head_length_um=4.2, head_width_um=2.6, acrosome_coverage_pct=55.0)
    assert cell.cell_type == "Spermatozoa"
    assert cell.normal_morphology is True


def test_human_hair_medullary_index_and_ndna_routing():
    # Human hair: I_medulla < 0.33 (e.g. 15um / 80um = 0.1875)
    res = micro_engine.analyze_hair_morphology(
        hair_id="HAIR-HUMAN-1",
        hair_diameter_um=80.0,
        medulla_diameter_um=15.0,
        root_status="ANAGEN_WITH_SHEATH"
    )

    assert res.species_origin == "HUMAN"
    assert res.medullary_index == 0.1875
    assert res.dna_routing == "NUCLEAR_STR_OPTIMAL"


def test_animal_hair_medullary_index_and_mtdna_routing():
    # Animal hair: I_medulla >= 0.50 (e.g. 50um / 80um = 0.625)
    res = micro_engine.analyze_hair_morphology(
        hair_id="HAIR-ANIMAL-2",
        hair_diameter_um=80.0,
        medulla_diameter_um=50.0,
        root_status="TELOGEN_NO_SHEATH"
    )

    assert res.species_origin == "NON_HUMAN_ANIMAL"
    assert res.medullary_index == 0.625
    assert res.dna_routing == "MITOCHONDRIAL_HV1_HV2"


# ── API Endpoint Integration Tests ───────────────────────────────────────────

def test_api_classify_cell_endpoint():
    payload = {
        "cell_id": "SPERM-CELL-01",
        "head_length_um": 4.5,
        "head_width_um": 2.8,
        "acrosome_coverage_pct": 55.0
    }

    resp = client.post("/api/v1/forensic/microscopy/classify-cell", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["cell_id"] == "SPERM-CELL-01"
    assert data["normal_morphology"] is True


def test_api_hair_morphology_endpoint():
    payload = {
        "hair_id": "HAIR-SAMPLE-501",
        "hair_diameter_um": 85.0,
        "medulla_diameter_um": 18.0,
        "root_status": "ANAGEN_WITH_SHEATH"
    }

    resp = client.post("/api/v1/forensic/microscopy/hair-morphology", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["hair_id"] == "HAIR-SAMPLE-501"
    assert data["species_origin"] == "HUMAN"
    assert data["dna_routing"] == "NUCLEAR_STR_OPTIMAL"
