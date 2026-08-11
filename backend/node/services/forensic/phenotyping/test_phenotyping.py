"""
Unit Tests for FORENZA Forensic DNA Phenotyping Engine (Phase 5).
Tests HIrisPlex-S eye/hair/skin predictors, BGA ancestry classifier,
and the /forensic/phenotype API endpoint.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.node.services.forensic.phenotyping.hirisplex import HiriPlexSEngine
from backend.node.services.forensic.phenotyping.ancestry import AncestryEngine
from backend.node.services.forensic.phenotyping.models import SNPInput
from backend.app.api.phenotype_routes import router as phenotype_router

_app = FastAPI()
_app.include_router(phenotype_router, prefix="/api/v1")
client = TestClient(_app)

hirisplex = HiriPlexSEngine()
ancestry_engine = AncestryEngine()


# ── Helper fixtures ───────────────────────────────────────────────────────────

def _snp(rsid: str, dosage: int) -> SNPInput:
    return SNPInput(rsid=rsid, dosage=dosage)


def _make_european_snps() -> dict:
    """
    Simulates a typical European individual.
    rs12913832 dosage=2 → strong blue eye signal
    rs16891982 dosage=2 → light skin / SLC45A2
    """
    return {
        "rs12913832": _snp("rs12913832", 2),   # HERC2 — blue eyes
        "rs1800407":  _snp("rs1800407",  0),   # OCA2
        "rs12896399": _snp("rs12896399", 1),   # SLC24A4
        "rs16891982": _snp("rs16891982", 2),   # SLC45A2
        "rs1393350":  _snp("rs1393350",  1),   # TYR
        "rs12203592": _snp("rs12203592", 0),   # IRF4
        # AIM panel SNPs typical for European
        "rs1426654":  _snp("rs1426654",  2),
        "rs4988235":  _snp("rs4988235",  1),
        "rs3340":     _snp("rs3340",     2),
    }


def _make_african_snps() -> dict:
    """Simulates a typical African individual."""
    return {
        "rs12913832": _snp("rs12913832", 0),   # No blue eye allele
        "rs1800407":  _snp("rs1800407",  0),
        "rs12896399": _snp("rs12896399", 0),
        "rs16891982": _snp("rs16891982", 0),   # SLC45A2 absent
        "rs1393350":  _snp("rs1393350",  0),
        "rs12203592": _snp("rs12203592", 0),
        # AIM panel SNPs for African
        "rs2814778":  _snp("rs2814778",  2),   # Duffy — Africa-specific
        "rs6119471":  _snp("rs6119471",  2),
        "rs1834619":  _snp("rs1834619",  2),
        "rs1426654":  _snp("rs1426654",  0),
    }


# ── 5.2 HIrisPlex-S Eye Colour ───────────────────────────────────────────────

def test_eye_colour_blue_prediction():
    """European-like genotype should predict blue eyes."""
    result = hirisplex.predict_eye_colour(_make_european_snps())
    assert result.trait == "eye_colour"
    assert abs(sum(result.probabilities.values()) - 1.0) < 1e-6
    assert result.most_likely == "blue"
    assert result.probabilities["blue"] > result.probabilities["brown"]


def test_eye_colour_brown_prediction():
    """African-like genotype (no HERC2 blue alleles) should predict brown eyes."""
    result = hirisplex.predict_eye_colour(_make_african_snps())
    assert result.most_likely == "brown"
    assert result.probabilities["brown"] > result.probabilities["blue"]


def test_eye_colour_probs_sum_to_one():
    snps = {"rs12913832": _snp("rs12913832", 1)}
    result = hirisplex.predict_eye_colour(snps)
    assert abs(sum(result.probabilities.values()) - 1.0) < 1e-6


# ── 5.2 HIrisPlex Hair Colour ────────────────────────────────────────────────

def test_hair_colour_probs_sum_to_one():
    result = hirisplex.predict_hair_colour(_make_european_snps())
    assert abs(sum(result.probabilities.values()) - 1.0) < 1e-6


def test_hair_colour_red_signal():
    """IRF4 rs12203592 dosage=2 is the strongest red hair predictor."""
    snps = {
        "rs12203592": _snp("rs12203592", 2),
        "rs1805007":  _snp("rs1805007",  2),  # MC1R — red hair variant
        "rs885479":   _snp("rs885479",   2),
    }
    result = hirisplex.predict_hair_colour(snps)
    # Red probability should be elevated vs default
    assert result.probabilities["red"] > 0.10


# ── 5.2 HIrisPlex Skin Tone ──────────────────────────────────────────────────

def test_skin_tone_pale_european():
    result = hirisplex.predict_skin_tone(_make_european_snps())
    assert abs(sum(result.probabilities.values()) - 1.0) < 1e-6
    # European genotype → lighter skin categories expected
    pale_mass = result.probabilities.get("very_pale", 0) + result.probabilities.get("pale", 0)
    dark_mass = result.probabilities.get("brown", 0) + result.probabilities.get("dark_brown", 0)
    assert pale_mass > dark_mass


def test_skin_tone_dark_african():
    result = hirisplex.predict_skin_tone(_make_african_snps())
    assert abs(sum(result.probabilities.values()) - 1.0) < 1e-6


# ── 5.3 Ancestry ────────────────────────────────────────────────────────────

def test_ancestry_european():
    result = ancestry_engine.predict_ancestry(_make_european_snps())
    assert "European" in result.probabilities
    assert result.probabilities["European"] > 0.30


def test_ancestry_african():
    result = ancestry_engine.predict_ancestry(_make_african_snps())
    assert "African" in result.probabilities
    assert result.probabilities["African"] > 0.30


def test_ancestry_no_snps_returns_uniform():
    result = ancestry_engine.predict_ancestry({})
    probs = list(result.probabilities.values())
    # All non-admixed populations should be roughly equal
    non_admixed = [v for k, v in result.probabilities.items() if k != "Admixed"]
    assert all(abs(v - non_admixed[0]) < 1e-6 for v in non_admixed)


# ── 5.4 API Endpoint ─────────────────────────────────────────────────────────

def test_phenotype_endpoint_european():
    payload = {
        "snps": [
            {"rsid": "rs12913832", "dosage": 2},
            {"rsid": "rs16891982", "dosage": 2},
            {"rsid": "rs1426654",  "dosage": 2},
            {"rsid": "rs4988235",  "dosage": 1},
        ]
    }
    resp = client.post("/api/v1/forensic/phenotype", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "eye_colour" in data
    assert "hair_colour" in data
    assert "skin_tone" in data
    assert "ancestry" in data
    assert data["snp_count_evaluated"] == 4
    assert 0.0 <= data["eye_colour"]["confidence"] <= 1.0


def test_phenotype_endpoint_empty_snps_rejected():
    resp = client.post("/api/v1/forensic/phenotype", json={"snps": []})
    assert resp.status_code == 422


def test_phenotype_endpoint_invalid_dosage():
    resp = client.post("/api/v1/forensic/phenotype",
                       json={"snps": [{"rsid": "rs12913832", "dosage": 5}]})
    assert resp.status_code == 422
