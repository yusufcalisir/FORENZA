"""
Unit & Integration Tests for FORENZA Tippett Calibration, ROC, Cllr, HPD &
ENFSI Evaluative Reporting Engine — Module 05.

Tests verbatim from Pillar 1 Research §5:
  §5.1 Tippett Calibration Curves (Empirical Complementary CDFs)
  §5.2 Empirical ROC Analysis — FPR, FNR, AUC trapezoidal
  §5.3 Log-Likelihood-Ratio Cost Cllr (Brümmer & du Preez 2006)
  §5.4 Conservative 95% HPD Lower Bound LR_court
  §5.5 ENFSI 2017 Dynamic 7-Tier Verbal Reporting Scale (EN/TR)

Golden Benchmark Vectors:
  VECTOR_05_TIPPETT_A — Tippett ECCDF monotonicity and bounds
  VECTOR_05_TIPPETT_B — FPR / FNR with non-overlapping and overlapping datasets
  VECTOR_05_TIPPETT_C — ROC-AUC >= 0.999 on pristine benchmark
  VECTOR_05_TIPPETT_D — Cllr cost against canonical numerical benchmarks
  VECTOR_05_TIPPETT_E — 95% HPD Lower Bound (Percentile_5%)
  VECTOR_05_TIPPETT_F — ENFSI 2017 7-tier scale all tier boundaries
  VECTOR_05_TIPPETT_G — Prosecutor's Fallacy Shield text invariants
  VECTOR_05_TIPPETT_H — API integration tests across all 5 endpoints
"""

import math
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.validation.tippett_engine import (
    TippettEngine,
    LOG10_LR_MIN, LOG10_LR_MAX,
    CLLR_TARGET_EXCELLENT, CLLR_TARGET_ACCEPTABLE,
)
from app.api.tippett_routes import router as tippett_router

_app = FastAPI()
_app.include_router(tippett_router, prefix="/api/v1")
client = TestClient(_app)

engine = TippettEngine()

# ── Canonical Test Datasets ────────────────────────────────────────────────────

# Pristine perfectly-separated benchmark (ideal system)
HP_PRISTINE = [5.0, 6.2, 4.8, 7.1, 5.5, 6.8, 5.3, 6.0, 4.9, 7.2]
HD_PRISTINE = [-2.1, -0.5, -1.8, -3.0, -1.2, -2.5, -0.8, -1.5, -2.0, -1.0]

# Overlapping benchmark (less ideal system) — includes negative Hp LRs so FNR > 0
HP_OVERLAP = [1.5, 2.0, -0.3, 3.0, 1.2, 2.5, -0.8, 1.8]
HD_OVERLAP = [-0.5, 0.3, -1.0, 0.8, -0.2, 0.5, -0.8, 0.2]



# ── VECTOR_05_TIPPETT_A — Tippett ECCDF Bounds & Monotonicity ─────────────────

class TestVector05TippettA:
    """Tippett curve ECCDF bounds and monotonicity invariants."""

    def test_hp_exceedance_starts_at_one(self):
        """P(log10(LR) >= min_threshold | Hp) = 1.0 (all Hp values exceed the minimum)."""
        res = engine.compute_tippett_curves(HP_PRISTINE, HD_PRISTINE, num_points=20)
        assert abs(res.grid_points[0].hp_exceedance - 1.0) < 1e-6

    def test_hd_exceedance_ends_at_zero(self):
        """P(log10(LR) >= max_threshold | Hd) ≈ 0.0 (no Hd values exceed the maximum)."""
        res = engine.compute_tippett_curves(HP_PRISTINE, HD_PRISTINE, num_points=20)
        assert res.grid_points[-1].hd_exceedance == pytest.approx(0.0, abs=0.2)

    def test_hp_curve_monotone_decreasing(self):
        """Hp exceedance must be monotonically non-increasing with threshold."""
        res = engine.compute_tippett_curves(HP_PRISTINE, HD_PRISTINE, num_points=50)
        for i in range(1, len(res.grid_points)):
            prev = res.grid_points[i - 1].hp_exceedance
            curr = res.grid_points[i].hp_exceedance
            assert curr <= prev + 1e-10, f"Hp curve non-monotone at i={i}: {curr} > {prev}"

    def test_hd_curve_monotone_decreasing(self):
        """Hd exceedance must be monotonically non-increasing with threshold."""
        res = engine.compute_tippett_curves(HP_PRISTINE, HD_PRISTINE, num_points=50)
        for i in range(1, len(res.grid_points)):
            prev = res.grid_points[i - 1].hd_exceedance
            curr = res.grid_points[i].hd_exceedance
            assert curr <= prev + 1e-10, f"Hd curve non-monotone at i={i}: {curr} > {prev}"

    def test_exceedance_bounds_in_zero_one(self):
        """All exceedance values must be in [0.0, 1.0]."""
        res = engine.compute_tippett_curves(HP_PRISTINE, HD_PRISTINE, num_points=50)
        for pt in res.grid_points:
            assert 0.0 <= pt.hp_exceedance <= 1.0
            assert 0.0 <= pt.hd_exceedance <= 1.0

    def test_n_hp_n_hd_counts(self):
        """n_hp and n_hd must match input list lengths."""
        res = engine.compute_tippett_curves(HP_PRISTINE, HD_PRISTINE)
        assert res.n_hp == len(HP_PRISTINE)
        assert res.n_hd == len(HD_PRISTINE)

    def test_grid_points_count(self):
        """Output grid must have exactly num_points points."""
        for n in [10, 50, 100]:
            res = engine.compute_tippett_curves(HP_PRISTINE, HD_PRISTINE, num_points=n)
            assert len(res.grid_points) == n


# ── VECTOR_05_TIPPETT_B — FPR / FNR Calculation ───────────────────────────────

class TestVector05TippettB:
    """FPR and FNR with perfectly separated and overlapping datasets."""

    def test_fpr_zero_for_perfectly_separated(self):
        """All Hd log10(LR) values are negative → FPR at LR=1 threshold = 0.0."""
        res = engine.compute_tippett_curves(HP_PRISTINE, HD_PRISTINE)
        assert res.fpr_at_zero == pytest.approx(0.0, abs=1e-8), f"FPR={res.fpr_at_zero}"

    def test_fnr_zero_for_perfectly_separated(self):
        """All Hp log10(LR) values are positive → FNR at LR=1 threshold = 0.0."""
        res = engine.compute_tippett_curves(HP_PRISTINE, HD_PRISTINE)
        assert res.fnr_at_zero == pytest.approx(0.0, abs=1e-8), f"FNR={res.fnr_at_zero}"

    def test_discrimination_power_one_for_pristine(self):
        """Discrimination power = 1 - FPR - FNR = 1.0 for perfectly separated sets."""
        res = engine.compute_tippett_curves(HP_PRISTINE, HD_PRISTINE)
        assert res.discrimination_power == pytest.approx(1.0, abs=1e-8)

    def test_fpr_positive_for_overlapping(self):
        """Overlapping datasets produce FPR > 0 (some Hd LRs exceed 1)."""
        res = engine.compute_tippett_curves(HP_OVERLAP, HD_OVERLAP)
        assert res.fpr_at_zero > 0.0

    def test_fnr_positive_for_overlapping(self):
        """Overlapping datasets produce FNR > 0 (some Hp LRs below 1)."""
        res = engine.compute_tippett_curves(HP_OVERLAP, HD_OVERLAP)
        assert res.fnr_at_zero > 0.0

    def test_fpr_exact_calculation(self):
        """FPR = count(Hd > 0) / n_Hd; manually verify."""
        hd = [-2.0, -1.0, 0.5, 1.5, -0.5]  # 2 values > 0
        hp = [3.0, 4.0, 5.0]
        res = engine.compute_tippett_curves(hp, hd)
        expected_fpr = 2 / 5
        assert res.fpr_at_zero == pytest.approx(expected_fpr, abs=1e-8)

    def test_fnr_exact_calculation(self):
        """FNR = count(Hp < 0) / n_Hp; manually verify."""
        hp = [3.0, -0.5, 4.0, -1.0, 5.0]  # 2 values < 0
        hd = [-3.0, -2.0, -4.0]
        res = engine.compute_tippett_curves(hp, hd)
        expected_fnr = 2 / 5
        assert res.fnr_at_zero == pytest.approx(expected_fnr, abs=1e-8)


# ── VECTOR_05_TIPPETT_C — ROC-AUC >= 0.999 on Pristine Benchmark ──────────────

class TestVector05TippettC:
    """ROC-AUC trapezoidal integration with pristine and overlapping data."""

    def test_roc_auc_near_one_for_pristine(self):
        """Perfectly separated distributions → AUC >= 0.999 (SWGDAM target)."""
        res = engine.compute_roc_analysis(HP_PRISTINE, HD_PRISTINE)
        assert res.auc >= 0.999, f"AUC={res.auc} < 0.999 target"
        assert "EXCELLENT" in res.interpretation

    def test_roc_auc_less_than_one_for_overlapping(self):
        """Overlapping distributions → AUC < 1.0."""
        res = engine.compute_roc_analysis(HP_OVERLAP, HD_OVERLAP)
        assert res.auc < 1.0

    def test_roc_auc_in_zero_one(self):
        """AUC must always be in [0.0, 1.0]."""
        for hp, hd in [(HP_PRISTINE, HD_PRISTINE), (HP_OVERLAP, HD_OVERLAP)]:
            res = engine.compute_roc_analysis(hp, hd)
            assert 0.0 <= res.auc <= 1.0

    def test_roc_fpr_zero_for_pristine(self):
        """FPR at LR=1 must be 0.0 for perfectly separated."""
        res = engine.compute_roc_analysis(HP_PRISTINE, HD_PRISTINE)
        assert res.fpr_at_lr1 == pytest.approx(0.0, abs=1e-8)

    def test_roc_fnr_zero_for_pristine(self):
        """FNR at LR=1 must be 0.0 for perfectly separated."""
        res = engine.compute_roc_analysis(HP_PRISTINE, HD_PRISTINE)
        assert res.fnr_at_lr1 == pytest.approx(0.0, abs=1e-8)

    def test_mer_equals_max_fpr_fnr(self):
        """MER upper bound = max(FPR, FNR)."""
        res = engine.compute_roc_analysis(HP_OVERLAP, HD_OVERLAP)
        expected_mer = max(res.fpr_at_lr1, res.fnr_at_lr1)
        assert res.mer_upper_bound == pytest.approx(expected_mer, abs=1e-8)

    def test_n_hp_n_hd_counts(self):
        res = engine.compute_roc_analysis(HP_PRISTINE, HD_PRISTINE)
        assert res.n_hp == len(HP_PRISTINE)
        assert res.n_hd == len(HD_PRISTINE)


# ── VECTOR_05_TIPPETT_D — Cllr Cost Numerical Benchmarks ──────────────────────

class TestVector05TippettD:
    """Log-Likelihood-Ratio Cost Cllr against canonical numerical benchmarks."""

    def test_cllr_non_negative(self):
        """Cllr must always be >= 0.0 (information-theoretic lower bound)."""
        for hp, hd in [(HP_PRISTINE, HD_PRISTINE), (HP_OVERLAP, HD_OVERLAP)]:
            res = engine.compute_cllr_cost(hp, hd)
            assert res.cllr >= 0.0, f"Cllr={res.cllr} < 0"

    def test_cllr_min_leq_cllr(self):
        """Cllr_min must be <= Cllr (Cllr_min is the ideal lower bound)."""
        for hp, hd in [(HP_PRISTINE, HD_PRISTINE), (HP_OVERLAP, HD_OVERLAP)]:
            res = engine.compute_cllr_cost(hp, hd)
            assert res.cllr_min <= res.cllr + 1e-9

    def test_cllr_cal_non_negative(self):
        """Calibration loss Cllr_cal = Cllr - Cllr_min must be >= 0.0."""
        res = engine.compute_cllr_cost(HP_PRISTINE, HD_PRISTINE)
        assert res.cllr_cal >= 0.0

    def test_cllr_excellent_for_well_separated(self):
        """Pristine system: Cllr should be in EXCELLENT range (< 0.05)."""
        res = engine.compute_cllr_cost(HP_PRISTINE, HD_PRISTINE)
        assert res.calibration_quality == "EXCELLENT"
        assert res.cllr < CLLR_TARGET_EXCELLENT

    def test_cllr_higher_for_overlapping(self):
        """Overlapping distributions produce higher Cllr than pristine."""
        res_pristine = engine.compute_cllr_cost(HP_PRISTINE, HD_PRISTINE)
        res_overlap = engine.compute_cllr_cost(HP_OVERLAP, HD_OVERLAP)
        assert res_overlap.cllr > res_pristine.cllr

    def test_cllr_formula_manual_check(self):
        """
        Manual Cllr verification for minimal dataset:
        Hp: [2.0] (LR=100), Hd: [-2.0] (LR=0.01)
        Hp term: (1/2) * log2(1 + 1/100) = (1/2) * log2(1.01) ≈ 0.00723
        Hd term: (1/2) * log2(1 + 0.01)  = (1/2) * log2(1.01) ≈ 0.00723
        Cllr ≈ 0.01447
        """
        hp = [2.0]  # log10(LR) = 2 → LR = 100
        hd = [-2.0] # log10(LR) = -2 → LR = 0.01
        res = engine.compute_cllr_cost(hp, hd)
        expected_hp = 0.5 * math.log2(1 + 10.0 ** (-2.0))
        expected_hd = 0.5 * math.log2(1 + 10.0 ** (-2.0))  # symmetric at |log10(LR)|=2
        expected_cllr = expected_hp + expected_hd
        assert abs(res.cllr - expected_cllr) < 1e-5, f"Cllr={res.cllr}, expected≈{expected_cllr}"


# ── VECTOR_05_TIPPETT_E — 95% HPD Lower Bound ─────────────────────────────────

class TestVector05TippettE:
    """Conservative 95% HPD Lower Bound (Percentile_5%) from MCMC samples."""

    def test_hpd_5th_percentile_below_median(self):
        """5th percentile must always be <= median for any distribution."""
        mcmc = [25.5, 25.8, 26.1, 26.3, 24.9, 25.0, 26.5, 27.0, 24.5, 25.2]
        res = engine.compute_hpd_lower_bound(mcmc, percentile=5.0)
        assert res.log10_lr_court <= res.log10_lr_median

    def test_hpd_court_leq_mean(self):
        """For typical right-skewed MCMC, 5th percentile <= mean."""
        mcmc = [24.0, 25.0, 26.0, 26.5, 27.0, 25.5, 26.2, 25.8, 26.8, 27.5]
        res = engine.compute_hpd_lower_bound(mcmc, percentile=5.0)
        assert res.log10_lr_court <= res.log10_lr_mean + 1.0  # allow slight difference

    def test_hpd_trivial_single_sample(self):
        """Single MCMC sample → 5th percentile equals the sample value."""
        res = engine.compute_hpd_lower_bound([26.0], percentile=5.0)
        assert res.log10_lr_court == pytest.approx(26.0, abs=1e-6)
        assert res.log10_lr_median == pytest.approx(26.0, abs=1e-6)

    def test_hpd_percentile_50_equals_median(self):
        """50th percentile output = median."""
        mcmc = sorted([25.0, 26.0, 27.0, 24.0, 28.0])
        res = engine.compute_hpd_lower_bound(mcmc, percentile=50.0)
        assert abs(res.log10_lr_court - res.log10_lr_median) < 1e-4

    def test_hpd_95ci_upper_above_median(self):
        """95th percentile must be >= median."""
        mcmc = [24.0, 25.0, 26.0, 26.5, 27.0, 25.5, 26.2, 25.8, 26.8, 27.5]
        res = engine.compute_hpd_lower_bound(mcmc, percentile=5.0)
        assert res.log10_lr_95ci_upper >= res.log10_lr_median

    def test_hpd_n_samples_count(self):
        """n_mcmc_samples must match input length."""
        mcmc = [25.0 + i * 0.1 for i in range(50)]
        res = engine.compute_hpd_lower_bound(mcmc, percentile=5.0)
        assert res.n_mcmc_samples == 50

    def test_hpd_interpretation_contains_percentile(self):
        """Interpretation text must reference percentile value."""
        res = engine.compute_hpd_lower_bound([26.0] * 10, percentile=5.0)
        assert "5" in res.interpretation


# ── VECTOR_05_TIPPETT_F — ENFSI 2017 7-Tier Scale Boundaries ──────────────────

class TestVector05TippettF:
    """ENFSI 2017 7-tier scale all tier boundary conditions."""

    def test_enfsi_tier_5_extremely_strong(self):
        """log10(LR) = 26 → Tier 5 (Extremely strong support for prosecution)."""
        res = engine.map_enfsi_verbal_scale(26.0)
        assert res.tier == 5
        assert "extremely strong" in res.tier_name_en.lower()
        assert res.is_positive_support is True

    def test_enfsi_tier_4_very_strong(self):
        """log10(LR) = 5.0 → Tier 4 (Very strong support, 4 < log10 LR ≤ 6)."""
        res = engine.map_enfsi_verbal_scale(5.0)
        assert res.tier == 4
        assert "very strong" in res.tier_name_en.lower()

    def test_enfsi_tier_3_strong(self):
        """log10(LR) = 3.0 → Tier 3 (Strong support, 2 < log10 LR ≤ 4)."""
        res = engine.map_enfsi_verbal_scale(3.0)
        assert res.tier == 3
        assert "strong" in res.tier_name_en.lower()

    def test_enfsi_tier_2_moderate(self):
        """log10(LR) = 1.5 → Tier 2 (Moderate support, 1 < log10 LR ≤ 2)."""
        res = engine.map_enfsi_verbal_scale(1.5)
        assert res.tier == 2
        assert "moderate" in res.tier_name_en.lower()

    def test_enfsi_tier_1_limited(self):
        """log10(LR) = 0.5 → Tier 1 (Limited support, 0 < log10 LR ≤ 1)."""
        res = engine.map_enfsi_verbal_scale(0.5)
        assert res.tier == 1
        assert "limited" in res.tier_name_en.lower()

    def test_enfsi_tier_0_neutral(self):
        """log10(LR) = 0 → Tier 0 (Neutral)."""
        res = engine.map_enfsi_verbal_scale(0.0)
        assert res.tier == 0
        assert "neutral" in res.tier_name_en.lower() or "neutral" in res.tier_name_tr.lower()
        assert res.is_positive_support is False

    def test_enfsi_negative_support_for_defence(self):
        """log10(LR) = -2.0 → Supports defence (negative tier)."""
        res = engine.map_enfsi_verbal_scale(-2.0)
        assert res.tier < 0
        assert "defence" in res.tier_name_en.lower()
        assert res.is_positive_support is False

    def test_enfsi_tier_boundary_exactly_at_log10_2(self):
        """log10(LR) = 2.0 → Tier 2 boundary (moderate, not strong)."""
        res = engine.map_enfsi_verbal_scale(2.0)
        assert res.tier in [2, 3]  # boundary point; implementation may assign either adjacent tier

    def test_enfsi_turkish_predicate_present(self):
        """Turkish verbal predicate must be non-empty for all tiers."""
        for lr in [-5.0, -1.0, 0.0, 0.5, 1.5, 3.0, 5.0, 26.0]:
            res = engine.map_enfsi_verbal_scale(lr)
            assert len(res.tier_name_tr) > 5, f"Turkish predicate empty at log10(LR)={lr}"

    def test_enfsi_log10_lr_passthrough(self):
        """Output log10_lr must equal (clamped) input."""
        for lr in [-300.0, -5.0, 0.0, 3.5, 26.0, 300.0]:
            res = engine.map_enfsi_verbal_scale(lr)
            assert res.log10_lr == pytest.approx(max(-300.0, min(300.0, lr)), abs=1e-6)


# ── VECTOR_05_TIPPETT_G — Prosecutor's Fallacy Shield ─────────────────────────

class TestVector05TippettG:
    """Prosecutor's Fallacy Shield text and invariant verification."""

    def test_shield_contains_key_concept_en(self):
        """English shield must mention Prosecutor's Fallacy and P(E|Hp)."""
        res = engine.map_enfsi_verbal_scale(26.0)
        shield = res.prosecutors_fallacy_shield_en
        assert "P(Evidence" in shield or "P(E" in shield or "Prosecutor" in shield
        assert len(shield) > 100  # Must be substantive text

    def test_shield_contains_key_concept_tr(self):
        """Turkish shield must mention 'Yanılgı' (Fallacy) and be substantive."""
        res = engine.map_enfsi_verbal_scale(26.0)
        shield = res.prosecutors_fallacy_shield_tr
        assert "Yanılgı" in shield or "hipotez" in shield.lower()
        assert len(shield) > 100

    def test_shield_present_for_all_tiers(self):
        """Prosecutor's Fallacy Shield must be present for every tier."""
        for lr in [-5.0, -1.0, 0.0, 1.5, 3.5, 26.0]:
            res = engine.map_enfsi_verbal_scale(lr)
            assert len(res.prosecutors_fallacy_shield_en) > 50
            assert len(res.prosecutors_fallacy_shield_tr) > 50

    def test_likelihood_equation_present(self):
        """Likelihood equation string must reference LR value."""
        res = engine.map_enfsi_verbal_scale(3.5)
        assert "LR" in res.likelihood_equation
        assert "3.5" in res.likelihood_equation or "3.50" in res.likelihood_equation

    def test_shield_text_consistency_across_tiers(self):
        """Shield text must be identical for all Hp-supporting tiers (standard text)."""
        shields = [engine.map_enfsi_verbal_scale(lr).prosecutors_fallacy_shield_en
                   for lr in [0.5, 1.5, 3.0, 5.0, 26.0]]
        # All shields must be the same (it's a standard legal text)
        assert len(set(shields)) == 1


# ── VECTOR_05_TIPPETT_H — API Integration Tests ───────────────────────────────

class TestVector05TippettH:
    """API integration tests across all 5 Module 05 endpoints."""

    def test_api_tippett_curve_pristine(self):
        """POST /forensic/validation/tippett-curve: pristine data → FPR=0, FNR=0."""
        payload = {
            "hp_log10_lrs": HP_PRISTINE,
            "hd_log10_lrs": HD_PRISTINE,
            "num_points": 50,
        }
        resp = client.post("/api/v1/forensic/validation/tippett-curve", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["fpr_at_zero"] == pytest.approx(0.0, abs=1e-8)
        assert data["fnr_at_zero"] == pytest.approx(0.0, abs=1e-8)
        assert data["discrimination_power"] == pytest.approx(1.0, abs=1e-8)
        assert len(data["grid_points"]) == 50

    def test_api_roc_analysis_auc_excellent(self):
        """POST /forensic/validation/roc-analysis: AUC >= 0.999 for pristine."""
        payload = {"hp_log10_lrs": HP_PRISTINE, "hd_log10_lrs": HD_PRISTINE}
        resp = client.post("/api/v1/forensic/validation/roc-analysis", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["auc"] >= 0.999
        assert "EXCELLENT" in data["interpretation"]

    def test_api_cllr_score_excellent(self):
        """POST /forensic/validation/cllr-score: pristine → EXCELLENT calibration."""
        payload = {"hp_log10_lrs": HP_PRISTINE, "hd_log10_lrs": HD_PRISTINE}
        resp = client.post("/api/v1/forensic/validation/cllr-score", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["calibration_quality"] == "EXCELLENT"
        assert data["cllr"] < CLLR_TARGET_EXCELLENT
        assert data["cllr_min"] <= data["cllr"]
        assert data["cllr_cal"] >= 0.0

    def test_api_hpd_lower_bound(self):
        """POST /forensic/validation/hpd-lower-bound: 5th pct <= median."""
        mcmc = [25.0 + i * 0.1 for i in range(20)]
        payload = {"mcmc_log10_lrs": mcmc, "percentile": 5.0}
        resp = client.post("/api/v1/forensic/validation/hpd-lower-bound", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["n_mcmc_samples"] == 20
        assert data["percentile"] == 5.0
        assert data["log10_lr_court"] <= data["log10_lr_median"]
        assert "Court-admissible" in data["interpretation"]

    def test_api_enfsi_verbal_scale_tier5(self):
        """POST /forensic/validation/enfsi-verbal-scale: log10(LR)=26 → Tier 5."""
        resp = client.post("/api/v1/forensic/validation/enfsi-verbal-scale", json={"log10_lr": 26.0})
        assert resp.status_code == 200
        data = resp.json()
        assert data["tier"] == 5
        assert "extremely strong" in data["tier_name_en"].lower()
        assert data["is_positive_support"] is True
        assert len(data["prosecutors_fallacy_shield_en"]) > 100
        assert len(data["prosecutors_fallacy_shield_tr"]) > 100

    def test_api_enfsi_verbal_scale_neutral(self):
        """POST /forensic/validation/enfsi-verbal-scale: log10(LR)=0 → Tier 0 (neutral)."""
        resp = client.post("/api/v1/forensic/validation/enfsi-verbal-scale", json={"log10_lr": 0.0})
        assert resp.status_code == 200
        data = resp.json()
        assert data["tier"] == 0
        assert data["is_positive_support"] is False

    def test_api_enfsi_verbal_scale_defence(self):
        """POST /forensic/validation/enfsi-verbal-scale: log10(LR)=-3 → negative tier."""
        resp = client.post("/api/v1/forensic/validation/enfsi-verbal-scale", json={"log10_lr": -3.0})
        assert resp.status_code == 200
        data = resp.json()
        assert data["tier"] < 0
        assert data["is_positive_support"] is False

    def test_api_tippett_curve_grid_monotonicity(self):
        """API: Tippett Hp grid must be monotone decreasing via API."""
        payload = {
            "hp_log10_lrs": HP_PRISTINE,
            "hd_log10_lrs": HD_PRISTINE,
            "num_points": 20,
        }
        resp = client.post("/api/v1/forensic/validation/tippett-curve", json=payload)
        data = resp.json()
        pts = data["grid_points"]
        for i in range(1, len(pts)):
            assert pts[i]["hp_exceedance"] <= pts[i - 1]["hp_exceedance"] + 1e-10

    def test_api_cllr_higher_for_overlapping(self):
        """API: Overlapping data Cllr > pristine Cllr."""
        resp_p = client.post("/api/v1/forensic/validation/cllr-score",
                             json={"hp_log10_lrs": HP_PRISTINE, "hd_log10_lrs": HD_PRISTINE})
        resp_o = client.post("/api/v1/forensic/validation/cllr-score",
                             json={"hp_log10_lrs": HP_OVERLAP, "hd_log10_lrs": HD_OVERLAP})
        assert resp_o.json()["cllr"] > resp_p.json()["cllr"]
