"""
FORENZA 1.2.5 — MCMC Mixture Deconvolution API Integration Tests
POST /forensic/mixture | GET /forensic/mixture/health | GET /forensic/mixture/models

10 integration tests covering schema validation, route responses, mathematical
invariants, and error handling.

Run with:
    pytest backend/app/api/test_mcmc_api.py -v

Research Reference: pillar_1_probabilistic_genotyping_research.md §2.5–2.9
AGENTS.md §3.4: Targeted Module Tests Only (no global suite).
"""

import math

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.mixture_routes import router

# ── Minimal test app — avoids booting full main.py with blockchain / DSPy deps ──
_app = FastAPI()
_app.include_router(router, prefix="/api/v1")
client = TestClient(_app)

# ── Shared EPG fixtures (2-locus, deliberately small for test speed) ──────────
# Fast MCMC params: n_burn=500, n_sample=1000, n_chains=2 → ~2–4s per test.

FAST_PARAMS = {
    "n_burn": 500,
    "n_sample": 1000,
    "n_chains": 2,
    "k_thin": 2,
    "seed": 42,
}

# 2-person mixture EPG: D3S1358 + VWA — 4 alleles each implies K=2 contributors.
EPG_2P = {
    "D3S1358": {"14.0": 820.0, "15.0": 780.0, "16.0": 510.0, "17.0": 490.0},
    "VWA":     {"17.0": 1150.0, "18.0": 1080.0, "19.0": 440.0, "20.0": 380.0},
}

# Suspect genotype consistent with major contributor in EPG_2P
SUSPECT_GT = {"D3S1358": [14.0, 15.0], "VWA": [17.0, 18.0]}


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: GET /forensic/mixture/health — sanity check
# ─────────────────────────────────────────────────────────────────────────────

def test_mixture_health_endpoint():
    """
    GET /api/v1/forensic/mixture/health must return 200 with:
      - status: "ok"
      - engine_importable: true
      - stutter_key_present: true  (EC-MCMC-04 regression guard)
    """
    r = client.get("/api/v1/forensic/mixture/health")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    body = r.json()
    assert body["status"] == "ok", f"Health degraded: {body}"
    assert body["engine_importable"] is True
    assert body["stutter_key_present"] is True, (
        "BiophysicalPeakModel stutter key regression detected — check peak_model.py Phase-2 fix"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: GET /forensic/mixture/models — model enumeration
# ─────────────────────────────────────────────────────────────────────────────

def test_mixture_models_endpoint():
    """
    GET /api/v1/forensic/mixture/models must list STRmix and EuroForMix
    with correct contributor bounds.
    """
    r = client.get("/api/v1/forensic/mixture/models")
    assert r.status_code == 200, r.text
    body = r.json()
    model_names = {m["name"] for m in body["available_models"]}
    assert "STRmix" in model_names, f"STRmix not in models: {model_names}"
    assert "EuroForMix" in model_names, f"EuroForMix not in models: {model_names}"
    assert body["default_model"] == "STRmix"
    assert body["max_contributors"] == 4
    assert body["min_contributors"] == 2


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: POST /forensic/mixture — basic 2-person run
# ─────────────────────────────────────────────────────────────────────────────

def test_mixture_2p_basic_run():
    """
    POST with 2-locus EPG, K=2 (fast params) must return 200.
    Verifies: n_contributors=2, response fields present.
    """
    payload = {
        "epg_data": EPG_2P,
        "K": 2,
        **FAST_PARAMS,
    }
    r = client.post("/api/v1/forensic/mixture", json=payload, timeout=120.0)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    body = r.json()
    assert body["n_contributors"] == 2
    assert "log10_lr_point" in body
    assert "log10_lr_hpd95_lo" in body
    assert "log10_lr_hpd95_hi" in body
    assert "lr_point" in body
    assert "model_engine" in body
    assert "convergence" in body
    assert "verbal_scale_en" in body
    assert "verbal_scale_tr" in body
    assert "assumptions" in body
    assert isinstance(body["assumptions"], list) and len(body["assumptions"]) > 0


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4: Probability simplex invariant — Σ w_k = 1.0 ± 1e-6
# ─────────────────────────────────────────────────────────────────────────────

def test_mixture_simplex_invariant():
    """
    Mathematical invariant: posterior_mixture_weights must sum to 1.0 ± 1e-6.
    Research: pillar_1_probabilistic_genotyping_research.md §2.4 (Dirichlet simplex).
    """
    payload = {
        "epg_data": EPG_2P,
        "K": 2,
        **FAST_PARAMS,
    }
    r = client.post("/api/v1/forensic/mixture", json=payload, timeout=120.0)
    assert r.status_code == 200, r.text
    body = r.json()
    weights = body["posterior_mixture_weights"]
    assert len(weights) == 2, f"Expected 2 weights, got {len(weights)}"
    total = sum(weights)
    assert abs(total - 1.0) < 1e-6, (
        f"Simplex invariant violated: Σw_k = {total:.8f} (expected 1.0 ± 1e-6)"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TEST 5: Convergence diagnostics present and finite
# ─────────────────────────────────────────────────────────────────────────────

def test_mixture_convergence_diagnostics_present():
    """
    Convergence block must contain r_hat_max, ess_min, converged — all finite.
    Gelman-Rubin R̂ > 0 and ESS > 0.
    """
    payload = {
        "epg_data": EPG_2P,
        "K": 2,
        **FAST_PARAMS,
    }
    r = client.post("/api/v1/forensic/mixture", json=payload, timeout=120.0)
    assert r.status_code == 200, r.text
    conv = r.json()["convergence"]
    assert "r_hat_max" in conv
    assert "ess_min" in conv
    assert "converged" in conv
    assert "n_samples_per_chain" in conv
    r_hat = conv["r_hat_max"]
    ess = conv["ess_min"]
    assert math.isfinite(r_hat), f"r_hat_max is not finite: {r_hat}"
    assert r_hat > 0, f"r_hat_max must be > 0, got {r_hat}"
    assert math.isfinite(ess), f"ess_min is not finite: {ess}"
    assert ess > 0, f"ess_min must be > 0, got {ess}"
    assert isinstance(conv["converged"], bool)


# ─────────────────────────────────────────────────────────────────────────────
# TEST 6: ENFSI verbal scale bilingual — both EN and TR non-empty
# ─────────────────────────────────────────────────────────────────────────────

def test_mixture_enfsi_verbal_scale_bilingual():
    """
    verbal_scale_en and verbal_scale_tr must both be non-empty strings.
    AGENTS.md §Legal: "Translate numerical LRs into standardized 7-tier ENFSI statements
    in English and Turkish with active Prosecutor's Fallacy shields."
    """
    payload = {
        "epg_data": EPG_2P,
        "K": 2,
        **FAST_PARAMS,
    }
    r = client.post("/api/v1/forensic/mixture", json=payload, timeout=120.0)
    assert r.status_code == 200, r.text
    body = r.json()
    en = body["verbal_scale_en"]
    tr = body["verbal_scale_tr"]
    assert isinstance(en, str) and len(en.strip()) > 0, f"verbal_scale_en is empty: {en!r}"
    assert isinstance(tr, str) and len(tr.strip()) > 0, f"verbal_scale_tr is empty: {tr!r}"


# ─────────────────────────────────────────────────────────────────────────────
# TEST 7: Schema validation — K=5 returns 422
# ─────────────────────────────────────────────────────────────────────────────

def test_mixture_schema_validation_K_out_of_range():
    """
    K=5 exceeds the validated range [2,4]. Must return 422 Unprocessable Entity.
    """
    payload = {
        "epg_data": EPG_2P,
        "K": 5,
        **FAST_PARAMS,
    }
    r = client.post("/api/v1/forensic/mixture", json=payload)
    assert r.status_code == 422, (
        f"Expected 422 for K=5, got {r.status_code}: {r.text}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TEST 8: Schema validation — non-numeric allele key returns 422
# ─────────────────────────────────────────────────────────────────────────────

def test_mixture_schema_invalid_epg_nonnumeric_allele():
    """
    Allele key 'abc' is not parseable as float.
    Must return 422 with validation detail.
    """
    payload = {
        "epg_data": {"D3S1358": {"abc": 1000.0}},
        "K": 2,
        **FAST_PARAMS,
    }
    r = client.post("/api/v1/forensic/mixture", json=payload)
    assert r.status_code == 422, (
        f"Expected 422 for non-numeric allele 'abc', got {r.status_code}: {r.text}"
    )
    # Verify the error message mentions the problematic key
    detail_text = str(r.json())
    assert "abc" in detail_text or "parseable" in detail_text or "float" in detail_text, (
        f"422 detail doesn't reference the allele key issue: {detail_text}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TEST 9: suspect_genotype accepted — H_p computation enabled
# ─────────────────────────────────────────────────────────────────────────────

def test_mixture_suspect_genotype_accepted():
    """
    POST with suspect_genotype must succeed (200) and not crash.
    The LR point estimate may differ from the no-suspect run (H_d vs H_p/H_d ratio).
    """
    payload = {
        "epg_data": EPG_2P,
        "K": 2,
        "suspect_genotype": SUSPECT_GT,
        **FAST_PARAMS,
    }
    r = client.post("/api/v1/forensic/mixture", json=payload, timeout=120.0)
    assert r.status_code == 200, (
        f"suspect_genotype POST failed with {r.status_code}: {r.text}"
    )
    body = r.json()
    assert math.isfinite(body["log10_lr_point"]), (
        f"log10_lr_point is not finite with suspect_genotype: {body['log10_lr_point']}"
    )
    # Posterior weights still form a valid simplex
    weights = body["posterior_mixture_weights"]
    assert abs(sum(weights) - 1.0) < 1e-6, f"Simplex violated with suspect: Σw={sum(weights)}"


# ─────────────────────────────────────────────────────────────────────────────
# TEST 10: Timeout guard — n_burn+n_sample > 60,000 returns 422
# ─────────────────────────────────────────────────────────────────────────────

def test_mixture_timeout_guard_large_run():
    """
    n_burn=40,000 + n_sample=30,000 = 70,000 > 60,000 synchronous limit.
    model_validator must reject with 422 before any computation begins.
    """
    payload = {
        "epg_data": EPG_2P,
        "K": 2,
        "n_burn": 40_000,
        "n_sample": 30_000,
        "n_chains": 2,
        "seed": 42,
    }
    r = client.post("/api/v1/forensic/mixture", json=payload)
    assert r.status_code == 422, (
        f"Expected 422 for n_burn+n_sample=70,000, got {r.status_code}: {r.text}"
    )
    detail_text = str(r.json())
    assert "60,000" in detail_text or "60000" in detail_text or "synchronous" in detail_text, (
        f"422 detail doesn't mention the run-size limit: {detail_text}"
    )
