"""
Unit & Integration Tests for FORENZA Population Genetics Engine (Phase 7).
Tests Wright's FST, Nei's genetic distance, NRC II 5/2N minimum bounding rule,
Dirichlet smoothing, and Population API endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.node.services.forensic.population.substructure import SubstructureEngine
from backend.node.services.forensic.population.rare_allele import RareAlleleEngine
from backend.app.api.population_routes import router as population_router

_app = FastAPI()
_app.include_router(population_router, prefix="/api/v1")
client = TestClient(_app)

substructure = SubstructureEngine()
rare_engine = RareAlleleEngine(default_database_n=500)


# ── 7.1 Substructure & FST Tests ─────────────────────────────────────────────

def test_locus_fst_identical_populations():
    """Identical allele frequencies must yield FST = 0.0."""
    p1 = {6.0: 0.50, 9.3: 0.50}
    p2 = {6.0: 0.50, 9.3: 0.50}
    fst = substructure.compute_locus_fst(p1, p2)
    assert fst == 0.0


def test_locus_fst_completely_fixed_populations():
    """Completely fixed disjoint alleles (6.0 vs 9.3) must yield maximum FST = 1.0."""
    p1 = {6.0: 1.0}
    p2 = {9.3: 1.0}
    fst = substructure.compute_locus_fst(p1, p2)
    assert abs(fst - 1.0) < 1e-6


def test_pairwise_fst_caucasian_african_american():
    res = substructure.compute_pairwise_fst("Caucasian", "AfricanAmerican")
    assert res.fst_value > 0.01
    assert res.genetic_distance_neis > 0.0
    assert "substructure" in res.recommendation.lower()


# ── 7.2 Rare Allele Frequency Bounding Tests ─────────────────────────────────

def test_nrc2_minimum_frequency_bound():
    """Default N=500 (1000 alleles) -> minimum bound = 5 / 1000 = 0.005."""
    p_min = rare_engine.get_minimum_frequency_bound(n_individuals=500)
    assert abs(p_min - 0.005) < 1e-6


def test_rare_allele_bounding_applied():
    """Raw frequency of 0.0001 (below 0.005 bound) should be bounded to 0.005."""
    res = rare_engine.bound_allele_frequency(
        locus="TH01", allele=9.3, raw_freq=0.0001, observed_count=1, n_individuals=500
    )
    assert res.was_bounded is True
    assert res.bounded_frequency == 0.005
    assert res.rarity_index > 2.0


def test_common_allele_not_bounded():
    """Raw frequency of 0.25 (exceeding 0.005 bound) should remain unchanged."""
    res = rare_engine.bound_allele_frequency(
        locus="TH01", allele=9.3, raw_freq=0.25, observed_count=250, n_individuals=500
    )
    assert res.was_bounded is False
    assert res.bounded_frequency == 0.25


def test_dirichlet_smoothing():
    counts = {6.0: 100, 9.3: 50, 10.0: 0}
    smoothed = rare_engine.apply_dirichlet_smoothing(counts, alpha=1.0)
    assert len(smoothed) == 3
    assert abs(sum(smoothed.values()) - 1.0) < 1e-2
    assert smoothed[10.0] >= 0.005


# ── 7.3 API Endpoint Integration Tests ───────────────────────────────────────

def test_api_list_populations():
    resp = client.get("/api/v1/forensic/population/populations")
    assert resp.status_code == 200
    data = resp.json()
    assert "Caucasian" in data["supported_populations"]
    assert data["default_database_n"] == 500


def test_api_bound_frequency():
    payload = {
        "locus": "TH01",
        "allele": 9.3,
        "raw_frequency": 0.0005,
        "observed_count": 1,
        "database_n": 500
    }
    resp = client.post("/api/v1/forensic/population/frequency", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["was_bounded"] is True
    assert data["bounded_frequency"] == 0.005


def test_api_fst_distance():
    payload = {
        "population1": "Caucasian",
        "population2": "AfricanAmerican"
    }
    resp = client.post("/api/v1/forensic/population/fst", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["fst_value"] > 0.0
    assert data["genetic_distance_neis"] > 0.0
