"""
Unit & Integration Tests for FORENZA Lineage DNA Forensics Package (Y-STR, X-STR, mtDNA).
Tests Y-STR paternal haplotype matching, Clopper-Pearson upper confidence bounds,
X-STR kinship, mtDNA rCRS alignment, and API routes.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.node.services.forensic.dna.ystr import YSTREngine, YSTRHaplotype
from backend.node.services.forensic.dna.xstr import XSTREngine, XSTRGenotype, XSTRProfile
from backend.node.services.forensic.dna.mtdna import MtDnaEngine, MtDnaProfile, MtDnaVariant
from backend.app.api.dna_routes import router as dna_router

_app = FastAPI()
_app.include_router(dna_router, prefix="/api/v1")
client = TestClient(_app)

ystr_engine = YSTREngine()
xstr_engine = XSTREngine()
mtdna_engine = MtDnaEngine()


# ── Y-STR Tests ──────────────────────────────────────────────────────────────

def test_ystr_full_haplotype_match():
    ev = YSTRHaplotype("Y-EVID-1", {"DYS19": 14.0, "DYS389I": 13.0, "DYS390": 24.0})
    sus = YSTRHaplotype("Y-SUSP-1", {"DYS19": 14.0, "DYS389I": 13.0, "DYS390": 24.0})

    res = ystr_engine.evaluate_ystr_match(ev, sus, database_count=0, database_size_n=2500)
    assert res.haplotype_match_status == "INCLUSION"
    assert res.matching_loci_count == 3
    assert res.upper_bound_95_ci < 0.005


def test_ystr_haplotype_exclusion():
    ev = YSTRHaplotype("Y-EVID-1", {"DYS19": 14.0, "DYS389I": 13.0})
    sus = YSTRHaplotype("Y-SUSP-1", {"DYS19": 15.0, "DYS389I": 12.0})

    res = ystr_engine.evaluate_ystr_match(ev, sus)
    assert res.haplotype_match_status == "EXCLUSION"


# ── X-STR Kinship Tests ──────────────────────────────────────────────────────

def test_xstr_father_daughter_kinship():
    # Father has 1 X allele per locus (hemizygous)
    father = XSTRProfile("FATHER-1", is_male=True, loci={
        "DXS10101": XSTRGenotype("DXS10101", 10.0),
        "DXS10103": XSTRGenotype("DXS10103", 18.0)
    })
    # Daughter inherits Father's X alleles
    daughter = XSTRProfile("DAUGHTER-1", is_male=False, loci={
        "DXS10101": XSTRGenotype("DXS10101", 10.0, 12.0),
        "DXS10103": XSTRGenotype("DXS10103", 18.0, 19.0)
    })

    res = xstr_engine.evaluate_x_kinship(father, daughter, "FATHER_DAUGHTER")
    assert res.combined_ki_x > 1.0
    assert "SUPPORTED" in res.kinship_verdict


# ── mtDNA Alignment Tests ────────────────────────────────────────────────────

def test_mtdna_maternal_match():
    ev_vars = [MtDnaVariant(16189, "C", "T", "HV1"), MtDnaVariant(263, "A", "G", "HV2")]
    sus_vars = [MtDnaVariant(16189, "C", "T", "HV1"), MtDnaVariant(263, "A", "G", "HV2")]

    ev_prof = MtDnaProfile("MT-EVID-1", "H1", ev_vars)
    sus_prof = MtDnaProfile("MT-SUSP-1", "H1", sus_vars)

    res = mtdna_engine.evaluate_mtdna_match(ev_prof, sus_prof)
    assert res.match_status == "CANNOT_BE_EXCLUDED"
    assert res.differing_positions_count == 0


def test_mtdna_maternal_exclusion():
    ev_vars = [MtDnaVariant(16189, "C", "T", "HV1")]
    sus_vars = [MtDnaVariant(16223, "C", "T", "HV1"), MtDnaVariant(263, "A", "G", "HV2")]

    ev_prof = MtDnaProfile("MT-EVID-1", "H1", ev_vars)
    sus_prof = MtDnaProfile("MT-SUSP-1", "U5", sus_vars)

    res = mtdna_engine.evaluate_mtdna_match(ev_prof, sus_prof)
    assert res.match_status == "EXCLUDED"
    assert res.differing_positions_count == 3


# ── API Endpoint Integration Tests ───────────────────────────────────────────

def test_api_ystr_endpoint():
    payload = {
        "evidence_id": "Y-EV-1",
        "suspect_id": "Y-SU-1",
        "evidence_markers": {"DYS19": 14.0, "DYS389I": 13.0},
        "suspect_markers": {"DYS19": 14.0, "DYS389I": 13.0},
        "database_count": 0,
        "database_size_n": 2500
    }
    resp = client.post("/api/v1/forensic/dna/ystr", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["haplotype_match_status"] == "INCLUSION"
    assert data["upper_bound_95_ci"] < 0.005


def test_api_mtdna_endpoint():
    payload = {
        "evidence_id": "MT-EV-1",
        "suspect_id": "MT-SU-1",
        "evidence_variants": [{"position": 16189, "ref_allele": "C", "alt_allele": "T", "region": "HV1"}],
        "suspect_variants": [{"position": 16189, "ref_allele": "C", "alt_allele": "T", "region": "HV1"}]
    }
    resp = client.post("/api/v1/forensic/dna/mtdna", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["match_status"] == "CANNOT_BE_EXCLUDED"
    assert data["differing_positions_count"] == 0
