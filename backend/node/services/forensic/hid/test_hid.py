"""
Unit & Integration Tests for FORENZA Human Identification (HID) Package.
Tests multi-modal joint LR calculation, skeletal degradation auditing, and HID API endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.models import STRGenotype, STRProfile
from node.services.forensic.hid.remains import HumanIdentificationEngine, MultiModalRemainsProfile
from node.services.forensic.hid.degradation import SkeletalDegradationEvaluator
from app.api.hid_routes import router as hid_router

_app = FastAPI()
_app.include_router(hid_router, prefix="/api/v1")
client = TestClient(_app)

hid_engine = HumanIdentificationEngine()
degrad_evaluator = SkeletalDegradationEvaluator()


def _build_profile(pid: str) -> STRProfile:
    loci = {
        "CSF1PO": STRGenotype("CSF1PO", 10.0, 12.0),
        "FGA": STRGenotype("FGA", 21.0, 23.0),
        "TH01": STRGenotype("TH01", 6.0, 9.3)
    }
    return STRProfile(profile_id=pid, loci=loci, population_group="Caucasian")


# ── Human Identification Tests ───────────────────────────────────────────────

def test_multi_modal_human_identification():
    remains_str = _build_profile("REMAINS-STR-01")
    cand1 = _build_profile("REF-CANDIDATE-01")

    remains = MultiModalRemainsProfile(
        remains_id="UNKNOWN-SKELETAL-BONE-101",
        sample_type="SKELETAL_BONE",
        str_profile=remains_str,
        ystr_markers={"DYS19": 14.0},
        mtdna_variants=["16189T"]
    )

    res = hid_engine.identify_unknown_remains(remains, [cand1])
    assert res.evaluated_candidates_count == 1
    assert len(res.top_candidate_hits) == 1
    top = res.top_candidate_hits[0]
    assert top.joint_lr > top.lr_str
    assert top.log10_joint_lr >= 1.0


def test_skeletal_degradation_auditor():
    prof = _build_profile("SKELETAL-BONE-DEGRADED")

    report = degrad_evaluator.audit_skeletal_profile(prof, mean_rfu=85.0)
    assert report.is_lcn_sample is True
    assert report.long_loci_dropout_risk in ["LOW", "MODERATE", "HIGH"]


# ── API Endpoint Integration Tests ───────────────────────────────────────────

def test_api_hid_identify_endpoint():
    remains_json = {
        "remains_id": "REMAINS-1",
        "sample_type": "SKELETAL_BONE",
        "str_profile": {
            "profile_id": "REMAINS-STR-1",
            "loci": {"TH01": {"locus": "TH01", "allele1": 6.0, "allele2": 9.3}},
            "population_group": "Caucasian"
        },
        "ystr_markers": {"DYS19": 14.0}
    }
    cand_json = {
        "profile_id": "CANDIDATE-1",
        "loci": {"TH01": {"locus": "TH01", "allele1": 6.0, "allele2": 9.3}},
        "population_group": "Caucasian"
    }

    payload = {
        "remains": remains_json,
        "candidate_db": [cand_json],
        "prior_probability": 0.5,
        "top_k": 5
    }

    resp = client.post("/api/v1/forensic/hid/identify", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["evaluated_candidates_count"] == 1
    assert len(data["top_candidate_hits"]) == 1


def test_api_hid_degradation_audit_endpoint():
    prof_json = {
        "profile_id": "BONE-SAMPLE-1",
        "loci": {"TH01": {"locus": "TH01", "allele1": 6.0, "allele2": 9.3}},
        "population_group": "Caucasian"
    }

    payload = {
        "profile": prof_json,
        "mean_rfu": 110.0
    }

    resp = client.post("/api/v1/forensic/hid/degradation-audit", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_lcn_sample"] is True
