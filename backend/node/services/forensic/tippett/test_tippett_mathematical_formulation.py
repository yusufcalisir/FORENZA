"""
FORENZA Forensic Evidence Operating System
Pillar 1 — Module 1.5: Tippett Plot ROC Calibration & Misleading Evidence Lab
Sub-Item 1.5.1: Mathematical Formulation Unit Test Suite
"""

import math
import pytest
import numpy as np

try:
    from node.services.forensic.tippett.tippett_mathematical_formulation import (
        TippettMathematicalFormulation,
        TippettPoint,
        TippettCurveResult,
        ROCAnalysisResult,
        CllrCostResult,
        HPDLowerBoundResult,
        LOG10_LR_MIN,
        LOG10_LR_MAX,
        CLLR_TARGET_EXCELLENT,
        CLLR_TARGET_ACCEPTABLE,
        MIN_ECCDF_SAMPLES,
        ROYALL_MISLEADING_BOUND_EXPONENT,
    )
except ImportError:
    from backend.node.services.forensic.tippett.tippett_mathematical_formulation import (
        TippettMathematicalFormulation,
        TippettPoint,
        TippettCurveResult,
        ROCAnalysisResult,
        CllrCostResult,
        HPDLowerBoundResult,
        LOG10_LR_MIN,
        LOG10_LR_MAX,
        CLLR_TARGET_EXCELLENT,
        CLLR_TARGET_ACCEPTABLE,
        MIN_ECCDF_SAMPLES,
        ROYALL_MISLEADING_BOUND_EXPONENT,
    )


# ===========================================================================
# 1. Test Suite: Tippett ECCDF Monotonicity & Asymptotes
# ===========================================================================

class TestTippettECCDFMonotonicity:
    """Tests for empirical complementary cumulative distribution functions."""

    @pytest.fixture
    def canonical_synthetic_pairs(self):
        np.random.seed(42)
        hp = np.random.normal(loc=18.5, scale=3.0, size=500).tolist()
        hd = np.random.normal(loc=-15.2, scale=2.5, size=500).tolist()
        return hp, hd

    def test_tippett_curve_strict_monotonicity(self, canonical_synthetic_pairs):
        hp, hd = canonical_synthetic_pairs
        res = TippettMathematicalFormulation.compute_tippett_curve(hp, hd, n_points=100)

        assert res.is_monotonic_hp is True
        assert res.is_monotonic_hd is True
        assert len(res.grid_points) == 100

        for i in range(len(res.grid_points) - 1):
            p_curr = res.grid_points[i]
            p_next = res.grid_points[i + 1]
            assert p_curr.threshold < p_next.threshold
            assert p_curr.hp_exceedance >= p_next.hp_exceedance
            assert p_curr.hd_exceedance >= p_next.hd_exceedance

    def test_tippett_asymptotic_boundary_limits(self, canonical_synthetic_pairs):
        hp, hd = canonical_synthetic_pairs
        min_v = float(min(min(hp), min(hd))) - 10.0
        max_v = float(max(max(hp), max(hd))) + 10.0
        res = TippettMathematicalFormulation.compute_tippett_curve(
            hp, hd, n_points=50, min_threshold=min_v, max_threshold=max_v
        )

        first_pt = res.grid_points[0]
        last_pt = res.grid_points[-1]

        # Below the minimum value, all points exceed (P = 1.0)
        assert first_pt.hp_exceedance == 1.0
        assert first_pt.hd_exceedance == 1.0

        # Beyond the maximum value, zero points exceed (P = 0.0)
        assert last_pt.hp_exceedance == 0.0
        assert last_pt.hd_exceedance == 0.0

    def test_tippett_discrimination_power_bounds(self, canonical_synthetic_pairs):
        hp, hd = canonical_synthetic_pairs
        res = TippettMathematicalFormulation.compute_tippett_curve(hp, hd)

        assert 0.0 <= res.discrimination_power <= 1.0
        assert res.fpr_at_zero == 0.0  # All Hd are negative in this canonical set
        assert res.fnr_at_zero == 0.0  # All Hp are positive in this canonical set
        assert res.discrimination_power == 1.0

    def test_tippett_insufficient_samples_raises_error(self):
        with pytest.raises(ValueError, match="Insufficient samples"):
            TippettMathematicalFormulation.compute_tippett_curve([1.0, 2.0], [0.5, 0.2])


# ===========================================================================
# 2. Test Suite: Non-Parametric ROC Analysis & Mann-Whitney AUC
# ===========================================================================

class TestROCAnalysisMannWhitneyAUC:
    """Tests for non-parametric ROC curves and Mann-Whitney U area under curve."""

    def test_perfect_separation_auc_equals_one(self):
        hp = [10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0]
        hd = [-10.0, -12.0, -14.0, -16.0, -18.0, -20.0, -22.0, -24.0, -26.0, -28.0]

        res = TippettMathematicalFormulation.compute_roc_analysis(hp, hd)
        assert res.auc == 1.000000
        assert res.separation_index == 0.500000
        assert res.fpr_at_neutral == 0.0
        assert res.fnr_at_neutral == 0.0
        assert "Perfect" in res.interpretation

    def test_complete_overlap_auc_equals_half(self):
        # Identical distributions
        arr = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
        res = TippettMathematicalFormulation.compute_roc_analysis(arr, arr)
        assert abs(res.auc - 0.50) < 1e-4
        assert res.separation_index == 0.0

    def test_inverted_distribution_auc_less_than_half(self):
        hp = [-5.0, -6.0, -7.0, -8.0, -9.0, -10.0, -11.0, -12.0, -13.0, -14.0]
        hd = [5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0]

        res = TippettMathematicalFormulation.compute_roc_analysis(hp, hd)
        assert res.auc == 0.0
        assert "Weak" in res.interpretation

    def test_roc_arrays_length_consistency(self):
        hp = list(range(10, 30))
        hd = list(range(-20, 0))

        res = TippettMathematicalFormulation.compute_roc_analysis(hp, hd, n_thresholds=50)
        assert len(res.thresholds) == 50
        assert len(res.tpr_values) == 50
        assert len(res.fpr_values) == 50


# ===========================================================================
# 3. Test Suite: Log-Likelihood-Ratio Cost (Cllr) & PAV Calibration
# ===========================================================================

class TestCllrCalibrationCostDecomposition:
    """Tests for Cllr cost metric and PAV discrimination/calibration decomposition."""

    def test_excellent_calibration_score(self):
        # High confidence true donors and true non-donors
        hp = [15.0, 18.0, 20.0, 22.0, 25.0, 26.0, 28.0, 30.0, 32.0, 35.0]
        hd = [-15.0, -18.0, -20.0, -22.0, -25.0, -26.0, -28.0, -30.0, -32.0, -35.0]

        res = TippettMathematicalFormulation.compute_cllr_cost(hp, hd)
        assert res.cllr_raw < CLLR_TARGET_EXCELLENT
        assert res.cllr_min >= 0.0
        assert res.cllr_cal >= 0.0
        assert res.calibration_grade == "EXCELLENT"

    def test_cllr_cost_invariant_raw_greater_equal_min(self):
        np.random.seed(123)
        hp = np.random.normal(loc=5.0, scale=4.0, size=100).tolist()
        hd = np.random.normal(loc=-4.0, scale=4.0, size=100).tolist()

        res = TippettMathematicalFormulation.compute_cllr_cost(hp, hd)
        assert res.cllr_raw >= res.cllr_min - 1e-9
        assert abs(res.cllr_cal - (res.cllr_raw - res.cllr_min)) < 1e-6

    def test_uninformative_system_cllr_greater_than_one(self):
        # Inverted distributions where high LRs occur under Hd
        hp = [-10.0] * 10
        hd = [+10.0] * 10

        res = TippettMathematicalFormulation.compute_cllr_cost(hp, hd)
        assert res.cllr_raw > 1.0
        assert res.calibration_grade in ["MISCALIBRATED", "UNINFORMATIVE"]


# ===========================================================================
# 4. Test Suite: Royall Misleading Evidence Inequality
# ===========================================================================

class TestRoyallMisleadingEvidence:
    """Tests for Royall's Inequality P(LR >= 10^k | Hd) <= 10^(-k)."""

    def test_royall_inequality_bound_standard_non_donors(self):
        # 10,000 non-donor trials
        np.random.seed(999)
        hd_samples = np.random.normal(loc=-12.0, scale=3.0, size=10000).tolist()

        res = TippettMathematicalFormulation.evaluate_misleading_evidence_rate(
            hd_samples, threshold_log10=ROYALL_MISLEADING_BOUND_EXPONENT
        )

        assert res["n_non_donors"] == 10000
        assert res["threshold_log10"] == 6.0
        assert res["count_exceeding"] == 0
        assert res["empirical_rate"] == 0.0
        assert res["bound_satisfied"] is True

    def test_royall_inequality_neutral_boundary(self):
        # Neutral threshold: threshold_log10 = 0.0 => bound = 1.0
        hd_samples = [-5.0, -3.0, -1.0, 0.5, -2.0, -4.0, -6.0, -8.0, -10.0, -12.0]
        res = TippettMathematicalFormulation.evaluate_misleading_evidence_rate(
            hd_samples, threshold_log10=0.0
        )
        assert res["count_exceeding"] == 1
        assert res["empirical_rate"] == 0.10
        assert res["theoretical_royall_bound"] == 1.0
        assert res["bound_satisfied"] is True


# ===========================================================================
# 5. Test Suite: Conservative 95% HPD Lower Bound
# ===========================================================================

class TestHPDConservativeLowerBound:
    """Tests for 95% HPD (5th percentile) lower bound computation."""

    def test_hpd_lower_bound_percentile_ordering(self):
        samples = [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0]
        res = TippettMathematicalFormulation.compute_95_hpd_lower_bound(samples, alpha=0.05)

        assert res.n_samples == 11
        assert res.lower_bound_5pct < res.median_log10_lr < res.upper_bound_95pct
        assert res.court_admissible_lr == pytest.approx(10.0 ** res.lower_bound_5pct, rel=1e-4)
        assert res.prosecutor_shield_active is True

    def test_hpd_variance_impact(self):
        # Low variance vs high variance on same mean
        low_var = [15.0, 15.1, 14.9, 15.0, 15.2, 14.8, 15.0, 15.1, 14.9, 15.0]
        high_var = [15.0, 22.0, 8.0, 15.0, 25.0, 5.0, 15.0, 20.0, 10.0, 15.0]

        res_low = TippettMathematicalFormulation.compute_95_hpd_lower_bound(low_var)
        res_high = TippettMathematicalFormulation.compute_95_hpd_lower_bound(high_var)

        # Higher variance results in lower conservative 5th percentile bound
        assert res_high.lower_bound_5pct < res_low.lower_bound_5pct
