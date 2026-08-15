"""
Unit & Integration Tests for FORENZA Y-STR Haplotype Forensics & Population Genetics — Module 06.

Tests verbatim from Pillar 2 Research §1:
  - §1.1 Clopper-Pearson 95% Exact Binomial Confidence Interval (k=0 and k>0)
  - §1.1 Brenner / Surveyor Subpopulation Coancestry Correction (theta)
  - §1.1 Discrete Laplace Clonal Clustering Smoothing Model
  - §1.2 Y-FILER Plus 27-Locus Multiplex Panel & Mutation Rates
  - §1.3 Minimum Male Contributor Mixture Deconvolution (N_male)
  - §1.3 Stepwise Mutation Model (SMM) for Paternity Discrepancies

Golden Benchmark Vectors:
  VECTOR_P2_01     — Full Y-FILER Plus 27-locus match: k=0, N=25000, alpha=0.05
                     p_upper ≈ 0.00011982, LR ≈ 8345.86, log10(LR) ≈ 3.92147
  VECTOR_06_YSTR_A — 27-locus panel completeness & 6 RM loci classification
  VECTOR_06_YSTR_B — Clopper-Pearson k=0 exact bounds and monotonicity
  VECTOR_06_YSTR_C — Clopper-Pearson k>0 exact Beta / F-distribution bounds
  VECTOR_06_YSTR_D — Brenner theta subpopulation coancestry correction
  VECTOR_06_YSTR_E — Discrete Laplace clonal clustering model
  VECTOR_06_YSTR_F — Mixture contributor deconvolution (single & multi-copy)
  VECTOR_06_YSTR_G — Stepwise Mutation Model (SMM) geometric decay
  VECTOR_06_YSTR_H — API integration across all endpoints
"""

import math
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.dna.ystr_engine import (
    YSTREngine,
    LaplaceCluster,
    Y_FILER_PLUS_27_LOCI,
    normalize_ystr_locus_name,
)
from app.api.ystr_routes import router as ystr_router

_app = FastAPI()
_app.include_router(ystr_router, prefix="/api/v1")
client = TestClient(_app)

engine = YSTREngine()

# Complete standard 27-locus Y-FILER Plus haplotype benchmark
BENCHMARK_27_HAPLOTYPE = {
    "DYS19": 14.0, "DYS389I": 13.0, "DYS389II": 29.0, "DYS390": 24.0,
    "DYS391": 10.0, "DYS392": 13.0, "DYS393": 13.0,
    "DYS385a": 11.0, "DYS385b": 14.0,
    "DYS437": 15.0, "DYS438": 12.0, "DYS439": 12.0, "DYS448": 19.0,
    "DYS456": 16.0, "DYS458": 17.0, "DYS635": 23.0, "YGATAH4": 12.0,
    "DYS460": 11.0, "DYS481": 22.0, "DYS533": 12.0,
    # 6 Rapidly Mutating Loci (7 individual targets)
    "DYS570": 17.0, "DYS576": 18.0, "DYS627": 21.0, "DYS518": 39.0,
    "DYS449": 29.0, "DYF387S1a": 37.0, "DYF387S1b": 38.0,
}



# ── VECTOR_P2_01 — Canonical Golden Ground-Truth Benchmark ────────────────────

class TestVectorP201:
    """
    VECTOR_P2_01 Golden Ground-Truth Benchmark (Research §6 Artifact D).
    Full Y-FILER Plus 27-locus match: k=0, N=25000, alpha=0.05.
    Expected: p_upper ≈ 0.00011982, LR ≈ 8345.86, log10(LR) ≈ 3.92147.
    """

    def test_vector_p2_01_exact_bounds(self):
        res = engine.compute_clopper_pearson_bound(k=0, n=25000, alpha=0.05)
        # Analytical: 1 - 0.05^(1/25001) = 0.0001198205...
        expected_p = 1.0 - math.pow(0.05, 1.0 / 25001)
        expected_lr = 1.0 / expected_p
        expected_log10_lr = -math.log10(expected_p)

        assert abs(res.p_upper - expected_p) < 1e-6, f"p_upper={res.p_upper}, expected={expected_p}"
        assert abs(res.lr_upper_bound - expected_lr) < 1.0, f"LR={res.lr_upper_bound}, expected={expected_lr}"
        assert abs(res.log10_lr_upper_bound - expected_log10_lr) < 1e-4

    def test_vector_p2_01_full_evaluation(self):
        res = engine.evaluate_ystr_paternal_match(
            evidence_markers=BENCHMARK_27_HAPLOTYPE,
            suspect_markers=BENCHMARK_27_HAPLOTYPE,
            database_count_k=0,
            database_size_n=25000,
        )
        assert res.match_status == "INCLUSION"
        assert res.matching_loci_count == len(BENCHMARK_27_HAPLOTYPE)
        assert res.mismatch_loci_count == 0
        assert res.clopper_pearson.p_upper == pytest.approx(0.00011982, abs=1e-6)
        assert res.clopper_pearson.log10_lr_upper_bound == pytest.approx(3.92147, abs=1e-3)


# ── VECTOR_06_YSTR_A — 27-Locus Panel Completeness & RM Classification ─────────

class TestVector06YSTRA:
    """Verifies Y-FILER Plus 27-locus panel metadata and mutation rates."""

    def test_total_loci_count_is_27(self):
        assert len(Y_FILER_PLUS_27_LOCI) == 27

    def test_rapidly_mutating_loci_count_is_6_loci_or_7_targets(self):
        rm_loci = [k for k, v in Y_FILER_PLUS_27_LOCI.items() if v.is_rapidly_mutating]
        expected_rm = {"DYS570", "DYS576", "DYS627", "DYS518", "DYS449", "DYF387S1a", "DYF387S1b"}
        assert set(rm_loci) == expected_rm

    def test_rapidly_mutating_rates_all_ge_0011(self):
        for name, meta in Y_FILER_PLUS_27_LOCI.items():
            if meta.is_rapidly_mutating:
                assert meta.mutation_rate >= 0.011, f"{name} RM rate {meta.mutation_rate} < 0.011"
            else:
                assert meta.mutation_rate < 0.010, f"{name} standard rate {meta.mutation_rate} >= 0.010"

    def test_multicopy_loci_flags(self):
        multicopy = [k for k, v in Y_FILER_PLUS_27_LOCI.items() if v.is_multicopy]
        assert set(multicopy) == {"DYS385a", "DYS385b", "DYF387S1a", "DYF387S1b"}

    def test_locus_name_normalization(self):
        assert normalize_ystr_locus_name("dys19") == "DYS19"
        assert normalize_ystr_locus_name("DYS385A") == "DYS385a"
        assert normalize_ystr_locus_name("Y-GATA-H4") == "YGATAH4"
        assert normalize_ystr_locus_name("DYF387S1A") == "DYF387S1a"



# ── VECTOR_06_YSTR_B — Clopper-Pearson k=0 Exact Bounds & Monotonicity ─────────

class TestVector06YSTRB:
    """Clopper-Pearson exact bounds for unobserved haplotypes (k=0)."""

    def test_k0_formula_matches_exact(self):
        for n in [100, 1000, 2500, 10000, 25000]:
            res = engine.compute_clopper_pearson_bound(k=0, n=n, alpha=0.05)
            expected = 1.0 - math.pow(0.05, 1.0 / (n + 1))
            assert abs(res.p_upper - expected) < 1e-8

    def test_k0_p_upper_decreases_with_database_size(self):
        """As N increases, p_upper must strictly decrease (larger DB -> stronger evidence)."""
        sizes = [500, 1000, 2500, 5000, 10000, 25000]
        results = [engine.compute_clopper_pearson_bound(k=0, n=n) for n in sizes]
        for i in range(1, len(results)):
            assert results[i].p_upper < results[i - 1].p_upper
            assert results[i].lr_upper_bound > results[i - 1].lr_upper_bound

    def test_k0_p_lower_is_zero(self):
        res = engine.compute_clopper_pearson_bound(k=0, n=25000)
        assert res.p_lower == 0.0


# ── VECTOR_06_YSTR_C — Clopper-Pearson k>0 Exact Bounds ────────────────────────

class TestVector06YSTRC:
    """Clopper-Pearson exact bounds for observed haplotypes (k>0)."""

    def test_k_greater_than_zero_ordering(self):
        """p_lower <= point_estimate <= p_upper for any k > 0."""
        for k in [1, 5, 10, 50]:
            res = engine.compute_clopper_pearson_bound(k=k, n=25000)
            assert res.p_lower <= res.point_estimate <= res.p_upper

    def test_p_upper_increases_with_observed_count_k(self):
        """As k increases (more common haplotype), p_upper increases and LR decreases."""
        k_values = [0, 1, 2, 5, 10, 25]
        results = [engine.compute_clopper_pearson_bound(k=k, n=25000) for k in k_values]
        for i in range(1, len(results)):
            assert results[i].p_upper > results[i - 1].p_upper
            assert results[i].lr_upper_bound < results[i - 1].lr_upper_bound

    def test_k_equals_n_boundary(self):
        """k=N implies p_upper = 1.0."""
        res = engine.compute_clopper_pearson_bound(k=100, n=100)
        assert res.p_upper == pytest.approx(1.0, abs=1e-4)


# ── VECTOR_06_YSTR_D — Brenner Subpopulation Correction (theta) ───────────────

class TestVector06YSTRD:
    """Brenner (2010) subpopulation coancestry correction tests."""

    def test_brenner_formula_exact(self):
        # p = (k + theta) / (n + theta)
        k, n, theta = 0, 25000, 0.03
        res = engine.compute_brenner_frequency(k=k, n=n, theta=theta)
        expected = theta / (n + theta)
        assert abs(res.p_brenner - expected) < 1e-9

    def test_brenner_conservative_for_k0(self):
        """For k=0, Brenner frequency is greater than 0, providing a positive probability."""
        res = engine.compute_brenner_frequency(k=0, n=25000, theta=0.03)
        assert res.p_brenner > 0.0
        assert res.lr_brenner > 0.0

    def test_brenner_increases_with_theta(self):
        """Higher coancestry theta yields higher frequency estimate (more conservative)."""
        thetas = [0.005, 0.01, 0.02, 0.03, 0.05]
        results = [engine.compute_brenner_frequency(k=1, n=25000, theta=t) for t in thetas]
        for i in range(1, len(results)):
            assert results[i].p_brenner > results[i - 1].p_brenner
            assert results[i].lr_brenner < results[i - 1].lr_brenner


# ── VECTOR_06_YSTR_E — Discrete Laplace Clonal Clustering Model ───────────────

class TestVector06YSTRE:
    """Discrete Laplace model smoothing tests."""

    def test_discrete_laplace_positive_probability(self):
        cluster1 = LaplaceCluster(
            weight=1.0,
            center_haplotype={"DYS19": 14.0, "DYS389I": 13.0},
            scale_parameters={"DYS19": 1.5, "DYS389I": 1.2},
        )
        res = engine.compute_discrete_laplace_probability(
            haplotype={"DYS19": 14.0, "DYS389I": 13.0},
            clusters=[cluster1],
        )
        assert res.haplotype_probability > 0.0
        assert res.haplotype_probability <= 1.0
        assert res.lr > 1.0

    def test_discrete_laplace_decays_with_distance(self):
        """A haplotype distant from the cluster center has lower probability than the center."""
        cluster1 = LaplaceCluster(
            weight=1.0,
            center_haplotype={"DYS19": 14.0, "DYS389I": 13.0},
            scale_parameters={"DYS19": 1.5, "DYS389I": 1.2},
        )
        res_center = engine.compute_discrete_laplace_probability(
            haplotype={"DYS19": 14.0, "DYS389I": 13.0},
            clusters=[cluster1],
        )
        res_distant = engine.compute_discrete_laplace_probability(
            haplotype={"DYS19": 16.0, "DYS389I": 15.0},
            clusters=[cluster1],
        )
        assert res_center.haplotype_probability > res_distant.haplotype_probability


# ── VECTOR_06_YSTR_F — Mixture Contributor Deconvolution ──────────────────────

class TestVector06YSTRF:
    """Minimum male contributor inference tests."""

    def test_single_source_male_inferred(self):
        profile = {"DYS19": [14.0], "DYS390": [24.0], "DYS385a_b": [11.0, 14.0]}
        res = engine.estimate_minimum_male_contributors(profile)
        assert res.minimum_male_contributors == 1

    def test_two_person_male_mixture(self):
        profile = {"DYS19": [14.0, 15.0], "DYS390": [23.0, 24.0, 25.0], "DYS385a_b": [11.0, 14.0]}
        res = engine.estimate_minimum_male_contributors(profile)
        assert res.minimum_male_contributors == 2  # 3 alleles at DYS390 -> ceil(3/2) = 2

    def test_three_person_male_mixture_single_copy(self):
        profile = {"DYS19": [13.0, 14.0, 15.0, 16.0, 17.0]}
        res = engine.estimate_minimum_male_contributors(profile)
        assert res.minimum_male_contributors == 3  # ceil(5/2) = 3

    def test_multicopy_locus_more_than_4_alleles_guarantees_3_males(self):
        """DYS385a/b with 5 distinct alleles guarantees >= 3 male contributors."""
        profile = {
            "DYS19": [14.0, 15.0],
            "DYS385a_b": [11.0, 12.0, 13.0, 14.0, 15.0],  # 5 alleles on multi-copy
        }
        res = engine.estimate_minimum_male_contributors(profile)
        assert res.minimum_male_contributors >= 3
        assert res.multi_copy_locus_flag is True


# ── VECTOR_06_YSTR_G — Stepwise Mutation Model (SMM) ──────────────────────────

class TestVector06YSTRG:
    """Stepwise Mutation Model (SMM) germline transmission tests."""

    def test_smm_exact_transmission_no_mutation(self):
        res = engine.compute_smm_paternity_transition(14.0, 14.0, "DYS19")
        assert res.is_mutation is False
        assert res.step_distance_m == 0
        assert res.transition_probability == pytest.approx(1.0 - 0.0021, abs=1e-6)

    def test_smm_1_step_mutation_formula(self):
        # m=1: (mu / 2) * p^0 * (1 - p) = (mu / 2) * (1 - p)
        mu = 0.0021
        p_step = 0.10
        expected = (mu / 2.0) * (1.0 - p_step)
        res = engine.compute_smm_paternity_transition(14.0, 15.0, "DYS19", p_step=p_step)
        assert res.is_mutation is True
        assert res.step_distance_m == 1
        assert res.transition_probability == pytest.approx(expected, abs=1e-8)

    def test_smm_geometric_decay_with_step_distance(self):
        """P(mutation) strictly decreases as step distance m increases."""
        res_m1 = engine.compute_smm_paternity_transition(14.0, 15.0, "DYS19")
        res_m2 = engine.compute_smm_paternity_transition(14.0, 16.0, "DYS19")
        res_m3 = engine.compute_smm_paternity_transition(14.0, 17.0, "DYS19")
        assert res_m1.transition_probability > res_m2.transition_probability > res_m3.transition_probability

    def test_smm_rapidly_mutating_locus_higher_mutation_prob(self):
        """RM locus (e.g. DYS570) has higher 1-step mutation probability than standard locus."""
        res_std = engine.compute_smm_paternity_transition(14.0, 15.0, "DYS19")   # mu = 0.0021
        res_rm = engine.compute_smm_paternity_transition(17.0, 18.0, "DYS570")   # mu = 0.0120
        assert res_rm.transition_probability > res_std.transition_probability
        assert "RAPIDLY_MUTATING" in res_rm.mutation_classification

    def test_evaluation_with_single_step_mutation_not_excluded(self):
        """A single 1-step mutation across 27 loci is classified as MUTATION_CONSISTENT_MATCH."""
        evidence = dict(BENCHMARK_27_HAPLOTYPE)
        suspect = dict(BENCHMARK_27_HAPLOTYPE)
        # Introduce 1-step discrepancy at RM locus DYS570
        suspect["DYS570"] = suspect["DYS570"] + 1.0

        res = engine.evaluate_ystr_paternal_match(evidence, suspect)
        assert res.match_status == "MUTATION_CONSISTENT_MATCH"
        assert res.mismatch_loci_count == 1
        assert len(res.smm_mutations) == 1


# ── VECTOR_06_YSTR_H — API Integration Tests ──────────────────────────────────

class TestVector06YSTRH:
    """API integration tests across all Module 06 endpoints."""

    def test_api_panel_metadata_returns_27_loci(self):
        resp = client.get("/api/v1/forensic/lineage/ystr/panel-metadata")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_loci"] == 27
        assert data["rapidly_mutating_loci_count"] == 7
        assert data["standard_loci_count"] == 20


    def test_api_clopper_pearson_k0_vector_p2_01(self):
        payload = {"observed_count_k": 0, "database_size_n": 25000, "alpha": 0.05}
        resp = client.post("/api/v1/forensic/lineage/ystr/clopper-pearson-bound", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["p_upper"] == pytest.approx(0.00011982, abs=1e-6)
        assert data["log10_lr_upper_bound"] == pytest.approx(3.92147, abs=1e-3)

    def test_api_brenner_frequency(self):
        payload = {"observed_count_k": 0, "database_size_n": 25000, "theta": 0.03}
        resp = client.post("/api/v1/forensic/lineage/ystr/brenner-frequency", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["p_brenner"] > 0.0
        assert data["lr_brenner"] > 0.0

    def test_api_mixture_contributors(self):
        payload = {
            "locus_alleles": {
                "DYS19": [14.0, 15.0],
                "DYS389I": [13.0, 14.0, 15.0],
                "DYS385a_b": [11.0, 12.0, 13.0, 14.0, 15.0],
            }
        }
        resp = client.post("/api/v1/forensic/lineage/ystr/mixture-contributors", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["minimum_male_contributors"] >= 3
        assert data["multi_copy_locus_flag"] is True

    def test_api_smm_transition(self):
        payload = {
            "father_allele": 14.0,
            "son_allele": 15.0,
            "locus_name": "DYS570",
            "p_step": 0.10,
        }
        resp = client.post("/api/v1/forensic/lineage/ystr/smm-transition", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_mutation"] is True
        assert data["step_distance_m"] == 1
        assert "RAPIDLY_MUTATING" in data["mutation_classification"]

    def test_api_evaluate_match_inclusion(self):
        payload = {
            "evidence_id": "EVID-01",
            "suspect_id": "SUSP-01",
            "evidence_markers": BENCHMARK_27_HAPLOTYPE,
            "suspect_markers": BENCHMARK_27_HAPLOTYPE,
            "database_count_k": 0,
            "database_size_n": 25000,
            "theta": 0.03,
        }
        resp = client.post("/api/v1/forensic/lineage/ystr/evaluate-match", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["match_status"] == "INCLUSION"
        assert data["matching_loci_count"] == 27
        assert data["clopper_pearson"]["p_upper"] == pytest.approx(0.00011982, abs=1e-6)
        assert len(data["prosecutors_fallacy_shield"]) > 50
