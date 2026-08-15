"""
Unit & Integration Tests for FORENZA Population Genetics Engine (Phase 7 + Module 03).
Tests Wright's FST, Nei's genetic distance, NRC II 5/2N minimum bounding rule,
Dirichlet smoothing, HWE exact test, Linkage Equilibrium, FST matrix, and Population API endpoints.
"""

import math
import random
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.node.services.forensic.population.substructure import SubstructureEngine
from backend.node.services.forensic.population.rare_allele import RareAlleleEngine
from backend.node.services.forensic.population.dirichlet_smoothing import DirichletSmoothingEngine
from backend.node.services.forensic.population.hwe_engine import HWEEngine
from backend.node.services.forensic.population.linkage_engine import LinkageEquilibriumEngine
from backend.app.api.population_routes import router as population_router

_app = FastAPI()
_app.include_router(population_router, prefix="/api/v1")
client = TestClient(_app)

substructure = SubstructureEngine()
rare_engine = RareAlleleEngine(default_database_n=500)
_dirichlet = DirichletSmoothingEngine()
_hwe = HWEEngine()
_le = LinkageEquilibriumEngine()


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


# ── VECTOR_03_POPGEN_A: NRC II p_min NIST 1036 ───────────────────────────────

def test_vector_03_popgen_a_nrc_ii_pmin_nist1036():
    """
    VECTOR_03_POPGEN_A — NRC II Rec 4.1 minimum frequency bound.
    N=1036 -> p_min = 5/(2*1036) = 5/2072 = 0.002413...
    """
    p_min = _dirichlet.get_nrc_ii_bound(n_individuals=1036)
    assert abs(p_min - 5.0 / 2072.0) < 1e-8, f"p_min={p_min}"


# ── VECTOR_03_POPGEN_B: Dirichlet kappa at theta=0.03 ────────────────────────

def test_vector_03_popgen_b_dirichlet_kappa_theta_003():
    """
    VECTOR_03_POPGEN_B — kappa = (1-theta)/theta.
    theta=0.03 -> kappa = 0.97/0.03 = 32.3333...
    """
    kappa = _dirichlet.compute_kappa(theta=0.03)
    expected = 0.97 / 0.03
    assert abs(kappa - expected) < 1e-8, f"kappa={kappa}"


# ── VECTOR_03_POPGEN_C: Posterior mean frequency ─────────────────────────────

def test_vector_03_popgen_c_posterior_mean_frequency():
    """
    VECTOR_03_POPGEN_C — Dirichlet posterior mean frequency.
    n_i=10, p0=0.10, N=100, theta=0.03
    kappa=32.3333; alpha_i=3.2333; p_tilde=(10+3.2333)/(100+32.3333)
    """
    posterior = _dirichlet.compute_posterior_allele_frequency(
        observed_count=10,
        prior_frequency=0.10,
        N=100,
        theta=0.03,
    )
    kappa = 0.97 / 0.03
    expected = (10 + 0.10 * kappa) / (100 + kappa)
    assert abs(posterior - expected) < 1e-6, f"posterior={posterior}"
    assert posterior > 0.025  # above p_min for N=100


# ── VECTOR_03_POPGEN_D: Laplace smoothing invariant ──────────────────────────

def test_vector_03_popgen_d_laplace_smoothing_sum_invariant():
    """
    VECTOR_03_POPGEN_D — Laplace smoothing output frequencies approximately sum to 1.
    Counts: {6.0: 100, 9.3: 50, 10.0: 0}, alpha=1.0, N=1000.
    """
    counts = {6.0: 100, 9.3: 50, 10.0: 0}
    smoothed = _dirichlet.apply_laplace_smoothing(counts, alpha=1.0, n_individuals=1000)
    p_min = _dirichlet.get_nrc_ii_bound(1000)
    assert len(smoothed) == 3
    for allele, freq in smoothed.items():
        assert freq >= p_min, f"allele {allele}: freq {freq} < p_min {p_min}"
    s = sum(smoothed.values())
    assert 0.99 <= s <= 1.10, f"sum={s}"


# ── VECTOR_03_POPGEN_E: HWE F_IS formula ─────────────────────────────────────

def test_vector_03_popgen_e_inbreeding_coefficient_fis():
    """
    VECTOR_03_POPGEN_E — F_IS = 1 - H_obs/H_exp.
    H_obs=0.60, H_exp=0.70 -> F_IS = 1 - 0.60/0.70 = 0.14286...
    """
    f_is = _hwe.compute_inbreeding_coefficient(h_obs=0.60, h_exp=0.70)
    expected = 1.0 - 0.60 / 0.70
    assert abs(f_is - expected) < 1e-6, f"F_IS={f_is}"


# ── VECTOR_03_POPGEN_F: HWE expected heterozygosity ──────────────────────────

def test_vector_03_popgen_f_expected_heterozygosity():
    """
    VECTOR_03_POPGEN_F — H_exp = 1 - sum(p_i^2).
    Biallelic equal (0.5, 0.5): H_exp = 1 - (0.25+0.25) = 0.50
    """
    freqs = {6.0: 0.5, 9.3: 0.5}
    h_exp = _hwe.compute_expected_heterozygosity(freqs)
    assert abs(h_exp - 0.50) < 1e-8, f"H_exp={h_exp}"


# ── VECTOR_03_POPGEN_G: HWE satisfied for balanced population ────────────────

def test_vector_03_popgen_g_hwe_satisfied_balanced_genotypes():
    """
    VECTOR_03_POPGEN_G — Balanced biallelic genotypes satisfy HWE.
    AA=25, AB=50, BB=25 at p=q=0.5 (exactly on equilibrium).
    """
    geno = {(6.0, 6.0): 25, (6.0, 9.3): 50, (9.3, 9.3): 25}
    result = _hwe.test_locus_hwe('TH01', geno, n_permutations=1000, seed=42)
    assert result.decision == 'HWE_SATISFIED'
    assert abs(result.h_exp - 0.50) < 0.01


# ── VECTOR_03_POPGEN_H: LE r^2 for independent loci ─────────────────────────

def test_vector_03_popgen_h_le_r2_independent_loci():
    """
    VECTOR_03_POPGEN_H — Independent loci must produce small r^2.
    Random independent genotypes across two loci.
    """
    rng = random.Random(42)
    alleles_l1 = [6.0, 9.3]
    alleles_l2 = [10.0, 11.0]
    genos_l1 = [(rng.choice(alleles_l1), rng.choice(alleles_l1)) for _ in range(200)]
    genos_l2 = [(rng.choice(alleles_l2), rng.choice(alleles_l2)) for _ in range(200)]
    result = _le.test_pairwise_linkage('TH01', 'CSF1PO', genos_l1, genos_l2)
    assert result.r_squared < 0.10, f"r^2={result.r_squared}"


# ── VECTOR_03_POPGEN_I: Theta-corrected LR homozygote ────────────────────────

def test_vector_03_popgen_i_theta_corrected_lr_homozygote():
    """
    VECTOR_03_POPGEN_I — NRC II Rec 4.10b theta-corrected homozygote match prob.
    p_a=0.2, theta=0.03.
    pi = [0.03+0.97*0.2]*[0.06+0.97*0.2] / [(1.03)*(1.06)]
    """
    pi = SubstructureEngine.theta_corrected_lr(p_a=0.2, theta=0.03)
    numerator = (0.03 + 0.97 * 0.2) * (0.06 + 0.97 * 0.2)
    denominator = 1.03 * 1.06
    expected = numerator / denominator
    assert abs(pi - expected) < 1e-8, f"pi={pi}, expected={expected}"


# ── VECTOR_03_POPGEN_J: FST matrix all 4 populations ────────────────────────

def test_vector_03_popgen_j_fst_matrix_four_populations():
    """
    VECTOR_03_POPGEN_J — Pairwise FST matrix for 4 CODIS populations.
    C(4,2) = 6 pairs. All FST >= 0.
    """
    pops = ['Caucasian', 'AfricanAmerican', 'Hispanic', 'Asian']
    result = substructure.compute_fst_matrix(pops)
    assert len(result.matrix) == 6, f"Expected 6 pairs, got {len(result.matrix)}"
    assert all(v >= 0 for v in result.matrix.values())
    assert result.theta_recommendation in [0.01, 0.03, 0.05]


# ── VECTOR_03_POPGEN_K: Weir-Cockerham theta estimator ───────────────────────

def test_vector_03_popgen_k_weir_cockerham_theta():
    """
    VECTOR_03_POPGEN_K — Weir & Cockerham (1984) theta estimator.
    Two populations, two loci. avg_theta must be in [0, 0.10].
    """
    locus_data = {
        'TH01': {
            'Caucasian': {6.0: 0.20, 9.3: 0.40, 10.0: 0.40},
            'AfricanAmerican': {6.0: 0.30, 9.3: 0.35, 10.0: 0.35},
        },
        'VWA': {
            'Caucasian': {14.0: 0.30, 15.0: 0.40, 16.0: 0.30},
            'AfricanAmerican': {14.0: 0.20, 15.0: 0.50, 16.0: 0.30},
        },
    }
    result = SubstructureEngine.weir_cockerham_theta_estimator(locus_data)
    assert len(result.locus_theta) == 2
    assert 0.0 <= result.avg_theta <= 0.10


# ── Module 03 API Integration Tests ──────────────────────────────────────────

def test_api_dirichlet_smooth():
    """POST /population/dirichlet returns allele posteriors with p_min floor."""
    payload = {
        "locus": "TH01",
        "observed_counts": {"6.0": 100, "9.3": 50, "10.0": 0},
        "prior_frequencies": {"6.0": 0.20, "9.3": 0.40, "10.0": 0.40},
        "theta": 0.03,
        "n_individuals": 1036,
    }
    resp = client.post("/api/v1/forensic/population/dirichlet", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["locus"] == "TH01"
    assert len(data["allele_posteriors"]) == 3
    for ar in data["allele_posteriors"]:
        assert ar["posterior_frequency"] >= ar["p_min_used"]
    assert data["theta"] == 0.03


def test_api_hwe_balanced_genotypes():
    """POST /population/hwe: balanced biallelic population satisfies HWE."""
    payload = {
        "locus": "TH01",
        "genotype_counts": {"6.0,6.0": 25, "6.0,9.3": 50, "9.3,9.3": 25},
        "n_permutations": 500,
    }
    resp = client.post("/api/v1/forensic/population/hwe", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["decision"] == "HWE_SATISFIED"
    assert abs(data["h_exp"] - 0.50) < 0.02


def test_api_theta_corrected_lr_homozygote():
    """POST /population/theta-lr: homozygote NRC II Rec 4.10b formula."""
    payload = {"p_a": 0.20, "theta": 0.03}
    resp = client.post("/api/v1/forensic/population/theta-lr", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["genotype_type"] == "HOMOZYGOTE"
    assert data["match_probability"] > 0.0
    assert data["log10_lr"] > 0.0


def test_api_theta_corrected_lr_heterozygote():
    """POST /population/theta-lr: heterozygote NRC II Rec 4.10b formula."""
    payload = {"p_a": 0.20, "p_b": 0.15, "theta": 0.03}
    resp = client.post("/api/v1/forensic/population/theta-lr", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["genotype_type"] == "HETEROZYGOTE"
    assert data["match_probability"] > 0.0


def test_api_fst_matrix_four_populations():
    """POST /population/fst-matrix: 4 populations -> 6 pairs."""
    payload = {"populations": ["Caucasian", "AfricanAmerican", "Hispanic", "Asian"]}
    resp = client.post("/api/v1/forensic/population/fst-matrix", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["n_pairs"] == 6
    assert data["theta_recommendation"] in [0.01, 0.03, 0.05]
    assert len(data["matrix"]) == 6

