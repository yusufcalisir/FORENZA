"""
Unit & Integration Tests for FORENZA Missing Persons & DVI Package.
Tests missing person candidate ranking across pedigrees, Interpol AM/PM disaster victim reconciliation matrix, and API endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.models import STRGenotype, STRProfile
from node.services.forensic.dvi.missing_persons import MissingPersonsEngine
from node.services.forensic.dvi.reconciliation import DviReconciliationEngine
from app.api.dvi_routes import router as dvi_router

_app = FastAPI()
_app.include_router(dvi_router, prefix="/api/v1")
client = TestClient(_app)

missing_engine = MissingPersonsEngine()
dvi_engine = DviReconciliationEngine()


def _build_profile(pid: str) -> STRProfile:
    loci = {
        "CSF1PO": STRGenotype("CSF1PO", 10.0, 12.0),
        "FGA": STRGenotype("FGA", 21.0, 23.0),
        "TH01": STRGenotype("TH01", 6.0, 9.3),
        "TPOX": STRGenotype("TPOX", 8.0, 11.0),
        "VWA": STRGenotype("VWA", 16.0, 17.0)
    }
    return STRProfile(profile_id=pid, loci=loci, population_group="Caucasian")


# ── Missing Persons Candidate Ranking Tests ──────────────────────────────────

def test_missing_persons_candidate_ranking():
    query = _build_profile("MISSING-PERSON-001")
    cand1 = _build_profile("CANDIDATE-CHILD-101")
    cand2 = _build_profile("CANDIDATE-UNRELATED-999")
    cand2.loci["TH01"] = STRGenotype("TH01", 7.0, 8.0)
    cand2.loci["FGA"] = STRGenotype("FGA", 18.0, 19.0)

    res = missing_engine.search_and_rank_candidates(query, [cand1, cand2], prior_probability=0.5)
    assert res.total_candidates_searched == 2
    assert len(res.top_candidate_hits) >= 1
    top = res.top_candidate_hits[0]
    assert top.candidate_id == "CANDIDATE-CHILD-101"
    assert top.combined_lr > 1.0
    assert top.posterior_probability > 0.50


# ── Interpol AM/PM DVI Reconciliation Tests ──────────────────────────────────

def test_dvi_am_pm_reconciliation_matrix():
    am1 = _build_profile("AM-FAMILY-REF-01")
    pm1 = _build_profile("PM-VICTIM-REMAIN-01")

    res = dvi_engine.reconcile_am_pm_profiles("DVI-FLOOD-2026", [am1], [pm1])
    assert res.total_am_profiles == 1
    assert res.total_pm_profiles == 1
    assert res.confirmed_identifications_count >= 1
    assert res.reconciliation_matrix[0].identification_status in ["CONFIRMED_IDENTIFICATION", "PROBABLE_IDENTIFICATION"]


# ── API Endpoint Integration Tests ───────────────────────────────────────────

def test_api_missing_person_search_endpoint():
    prof_json = {
        "profile_id": "MP-QUERY-1",
        "loci": {
            "TH01": {"locus": "TH01", "allele1": 6.0, "allele2": 9.3},
            "FGA": {"locus": "FGA", "allele1": 21.0, "allele2": 23.0}
        },
        "population_group": "Caucasian"
    }

    payload = {
        "query_profile": prof_json,
        "candidate_db": [prof_json],
        "prior_probability": 0.5,
        "top_k": 5
    }

    resp = client.post("/api/v1/forensic/dvi/missing-person/search", json=payload)
    assert resp.status_code == 200
    assert resp.json()["total_candidates_searched"] == 1


def test_api_dvi_reconcile_endpoint():
    am_json = {
        "profile_id": "AM-REF-1",
        "loci": {"TH01": {"locus": "TH01", "allele1": 6.0, "allele2": 9.3}},
        "population_group": "Caucasian"
    }
    pm_json = {
        "profile_id": "PM-REMAIN-1",
        "loci": {"TH01": {"locus": "TH01", "allele1": 6.0, "allele2": 9.3}},
        "population_group": "Caucasian"
    }

    payload = {
        "disaster_event_id": "DVI-EVENT-2026",
        "am_profiles": [am_json],
        "pm_profiles": [pm_json]
    }

    resp = client.post("/api/v1/forensic/dvi/reconcile", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_am_profiles"] == 1
    assert data["total_pm_profiles"] == 1
    assert len(data["reconciliation_matrix"]) == 1
