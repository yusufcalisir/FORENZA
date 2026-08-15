"""
Integration Tests for FORENZA Forensic API Endpoints (Phase 4).
Uses FastAPI TestClient (httpx) to hit /forensic/lr, /forensic/kinship, /forensic/validate.
Imports only the router directly — no full app boot required.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.forensic_routes import router
from app.api.genomics_routes import router as genomics_router

# Minimal test app — avoids booting full main.py with blockchain / DSPy deps
_app = FastAPI()
_app.include_router(router, prefix="/api/v1")
_app.include_router(genomics_router, prefix="/api/v1")
client = TestClient(_app)


# ── Fixtures ─────────────────────────────────────────────────────────────────

MATCHING_PROFILE = {
    "profile_id": "SUSPECT-01",
    "population_group": "Caucasian",
    "loci": [
        {"locus": "TH01",    "allele1": 6.0,  "allele2": 9.3},
        {"locus": "FGA",     "allele1": 20.0, "allele2": 22.0},
        {"locus": "CSF1PO",  "allele1": 10.0, "allele2": 11.0},
        {"locus": "VWA",     "allele1": 16.0, "allele2": 18.0},
        {"locus": "D3S1358", "allele1": 15.0, "allele2": 17.0},
    ]
}

DIFFERENT_PROFILE = {
    "profile_id": "SUSPECT-02",
    "population_group": "Caucasian",
    "loci": [
        {"locus": "TH01",    "allele1": 7.0,  "allele2": 8.0},   # mismatch
        {"locus": "FGA",     "allele1": 20.0, "allele2": 22.0},
        {"locus": "CSF1PO",  "allele1": 10.0, "allele2": 11.0},
        {"locus": "VWA",     "allele1": 16.0, "allele2": 18.0},
        {"locus": "D3S1358", "allele1": 15.0, "allele2": 17.0},
    ]
}


# ── POST /forensic/lr — INCLUSION ────────────────────────────────────────────

def test_lr_inclusion():
    payload = {
        "evidence_profile": MATCHING_PROFILE,
        "suspect_profile": MATCHING_PROFILE,
        "theta": 0.01
    }
    resp = client.post("/api/v1/forensic/lr", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["match_status"] == "INCLUSION"
    assert data["lr_value"] > 1.0
    assert data["log10_lr"] > 0.0
    assert "confidence_interval" in data
    assert data["confidence_interval"]["high"] > data["lr_value"]
    assert len(data["locus_scores"]) >= 5


# ── POST /forensic/lr — EXCLUSION ────────────────────────────────────────────

def test_lr_exclusion():
    payload = {
        "evidence_profile": MATCHING_PROFILE,
        "suspect_profile": DIFFERENT_PROFILE,
        "theta": 0.01
    }
    resp = client.post("/api/v1/forensic/lr", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["match_status"] == "EXCLUSION"
    assert data["lr_value"] == 0.0


# ── POST /forensic/lr — schema validation ────────────────────────────────────

def test_lr_schema_validation_too_few_loci():
    """Fewer than 3 loci should be rejected by Pydantic."""
    payload = {
        "evidence_profile": {
            "profile_id": "E",
            "population_group": "Caucasian",
            "loci": [{"locus": "TH01", "allele1": 6.0, "allele2": 9.3}]  # only 1 locus
        },
        "suspect_profile": MATCHING_PROFILE,
    }
    resp = client.post("/api/v1/forensic/lr", json=payload)
    assert resp.status_code == 422


# ── POST /forensic/kinship ────────────────────────────────────────────────────

def test_kinship_parent_child():
    # Child shares one allele with alleged father at TH01: father (6, 9.3), child (9.3, 8)
    father = {**MATCHING_PROFILE, "profile_id": "FATHER"}
    child = {
        "profile_id": "CHILD",
        "population_group": "Caucasian",
        "loci": [
            {"locus": "TH01",    "allele1": 9.3,  "allele2": 8.0},
            {"locus": "FGA",     "allele1": 22.0, "allele2": 24.0},
            {"locus": "CSF1PO",  "allele1": 11.0, "allele2": 12.0},
            {"locus": "VWA",     "allele1": 18.0, "allele2": 14.0},
            {"locus": "D3S1358", "allele1": 17.0, "allele2": 16.0},
        ]
    }
    payload = {"profile1": father, "profile2": child, "relationship": "parent_child", "theta": 0.01}
    resp = client.post("/api/v1/forensic/kinship", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["relationship"] == "parent_child"
    assert data["ki_value"] > 1.0
    assert data["posterior_probability"] > 0.5


def test_kinship_invalid_relationship():
    payload = {
        "profile1": MATCHING_PROFILE,
        "profile2": MATCHING_PROFILE,
        "relationship": "clone"  # invalid
    }
    resp = client.post("/api/v1/forensic/kinship", json=payload)
    assert resp.status_code == 422


# ── POST /forensic/validate ───────────────────────────────────────────────────

def test_validate_endpoint_smoke():
    payload = {"n_per_type": 20, "population": "Caucasian", "theta": 0.01, "seed": 7}
    resp = client.post("/api/v1/forensic/validate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert 0.0 <= data["accuracy"] <= 1.0
    assert data["false_inclusion_rate"] >= 0.0
    assert data["n_pairs_per_type"] == 20
    assert "true_match" in data["per_type_mean_log10_lr"]


def test_validate_n_per_type_out_of_range():
    """n_per_type below minimum (10) must be rejected."""
    payload = {"n_per_type": 2, "population": "Caucasian", "theta": 0.01, "seed": 0}
    resp = client.post("/api/v1/forensic/validate", json=payload)
    assert resp.status_code == 422


# ── POST /forensic/genomics/deconvolve ────────────────────────────────────────

def test_deconvolve_mixture_endpoint():
    payload = {
        "observed_peaks": {
            "TH01": {"6.0": 700.0, "9.3": 300.0},
            "CSF1PO": {"10.0": 600.0, "11.0": 600.0, "12.0": 300.0, "13.0": 300.0}
        },
        "num_contributors": 2,
        "model_engine": "STRmix",
        "n_burn": 100,
        "n_sample": 300,
        "n_chains": 1,
    }
    resp = client.post("/api/v1/forensic/genomics/deconvolve", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["num_contributors"] == 2
    assert "log10_lr" in data
    assert "posterior_mixture_weights" in data
    assert len(data["posterior_mixture_weights"]) == 2
    assert len(data["verbal_scale_en"]) > 0
    assert len(data["verbal_scale_tr"]) > 0

