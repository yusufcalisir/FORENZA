"""
Unit & Integration Tests for FORENZA Forensic Serology Package.
Tests classical blood group antigen matching (ABO, Rh, Kell), Lewis secretor status,
dual Serology + DNA Likelihood Ratio integration (LR_combined = LR_serology * LR_STR), and API endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.serology.serology import ForensicSerologyEngine, SerologicalPhenotypeData
from node.services.forensic.serology.integration import SerologyDnaIntegrator
from app.api.serology_routes import router as serology_router

_app = FastAPI()
_app.include_router(serology_router, prefix="/api/v1")
client = TestClient(_app)

serology_engine = ForensicSerologyEngine()
integrator = SerologyDnaIntegrator()


# ── Phenotype & Secretor Tests ───────────────────────────────────────────────

def test_abo_rh_serological_evaluation():
    sample = SerologicalPhenotypeData(
        sample_id="SER-101",
        abo_group="A",
        rh_factor="D+",
        kell_status="K-",
        lewis_phenotype="Lea-b+"
    )

    res = serology_engine.evaluate_phenotype(sample)
    assert res.abo_group == "A"
    assert res.rh_factor == "D+"
    assert res.secretor_status == "SECRETOR"
    assert res.combined_serology_frequency == 0.3094
    assert res.serology_likelihood_ratio == 3.23


def test_lewis_non_secretor_status():
    sample = SerologicalPhenotypeData(
        sample_id="SER-102",
        abo_group="O",
        rh_factor="D-",
        lewis_phenotype="Lea+b-"
    )

    res = serology_engine.evaluate_phenotype(sample)
    assert res.secretor_status == "NON_SECRETOR"
    assert res.combined_serology_frequency < 0.10


# ── Dual Serology + DNA Integration Tests ────────────────────────────────────

def test_dual_serology_dna_fusion():
    sample = SerologicalPhenotypeData("SER-201", "B", "D+")
    ser_res = serology_engine.evaluate_phenotype(sample)

    fusion = integrator.integrate_serology_and_dna("SER-201", ser_res, lr_str=100000.0)
    assert fusion.lr_serology > 1.0
    assert fusion.lr_combined > fusion.lr_str
    assert fusion.log10_lr_combined >= 5.0


# ── API Endpoint Integration Tests ───────────────────────────────────────────

def test_api_serology_phenotype_endpoint():
    payload = {
        "sample": {
            "sample_id": "SER-SAMPLE-701",
            "abo_group": "AB",
            "rh_factor": "D+",
            "lewis_phenotype": "Lea-b+"
        }
    }

    resp = client.post("/api/v1/forensic/serology/phenotype", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["sample_id"] == "SER-SAMPLE-701"
    assert data["abo_group"] == "AB"
    assert data["secretor_status"] == "SECRETOR"


def test_api_serology_integrate_dna_endpoint():
    payload = {
        "sample": {
            "sample_id": "SER-SAMPLE-702",
            "abo_group": "A",
            "rh_factor": "D+"
        },
        "lr_str": 1000000.0
    }

    resp = client.post("/api/v1/forensic/serology/integrate-dna", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["lr_combined"] > 1000000.0
    assert "Extremely strong support" in data["verbal_statement"]
