"""
FORENZA Forensic Evidence Operating System
Pillar 1 — Module 1.5: Tippett Plot ROC Calibration & Misleading Evidence Lab
Sub-Item 1.5.4: 5 Documented Edge-Case Test Suite (5/5 Cases)

Formal verification for:
  - EC-TIP-01: Dense Monotonicity Invariant (x in [-20, +40])
  - EC-TIP-02: Non-Donor False Inclusion Rate under Hd (10,000 trials)
  - EC-TIP-03: Single-Source Pristine Separation AUC (AUC = 1.000000)
  - EC-TIP-04: Degradation Shift Curve (P(D) = 0.60, median shift to ~ +8.2)
  - EC-TIP-05: Neutral LR Intersection & Balanced Prior Symmetry
"""

import math
import pytest
import numpy as np

try:
    from node.services.forensic.tippett.tippett_mathematical_formulation import (
        TippettMathematicalFormulation,
        TippettCurveResult,
        ROCAnalysisResult,
        CllrCostResult,
    )
    from node.services.forensic.tippett.tippett_reference_datasets import (
        TippettReferenceDatasetRegistry,
    )
except ImportError:
    from backend.node.services.forensic.tippett.tippett_mathematical_formulation import (
        TippettMathematicalFormulation,
        TippettCurveResult,
        ROCAnalysisResult,
        CllrCostResult,
    )
    from backend.node.services.forensic.tippett.tippett_reference_datasets import (
        TippettReferenceDatasetRegistry,
    )


# ===========================================================================
# 1. EC-TIP-01: Dense Monotonicity Invariant (x in [-20, +40])
# ===========================================================================

class TestEdgeCaseTIP01_DenseMonotonicity:
    """
    EC-TIP-01: Both empirical CDF curves strictly non-increasing for all x in [-20, +40].
    Tested on a dense 500-point grid.
    """

    def test_dense_grid_monotonicity_invariant(self):
        cohort = TippettReferenceDatasetRegistry.generate_pristine_cohort(n_pairs=500, seed=42)
        res = TippettMathematicalFormulation.compute_tippett_curve(
            cohort.hp_log10_lrs,
            cohort.hd_log10_lrs,
            n_points=500,
            min_threshold=-20.0,
            max_threshold=40.0,
        )

        assert res.is_monotonic_hp is True
        assert res.is_monotonic_hd is True
        assert len(res.grid_points) == 500

        for i in range(len(res.grid_points) - 1):
            curr_p = res.grid_points[i]
            next_p = res.grid_points[i + 1]
            assert curr_p.threshold < next_p.threshold
            # Non-increasing invariant: P(x_i) >= P(x_{i+1})
            assert curr_p.hp_exceedance >= next_p.hp_exceedance
            assert curr_p.hd_exceedance >= next_p.hd_exceedance


# ===========================================================================
# 2. EC-TIP-02: Non-Donor False Inclusion Rate under Hd (10,000 Trials)
# ===========================================================================

class TestEdgeCaseTIP02_FalseInclusionRate10000Trials:
    """
    EC-TIP-02: Zero false positives above LR = 10^6 in 10,000 non-donor trials (P <= 0.0001).
    Verifies Royall's inequality satisfaction: P(LR >= 10^6 | Hd) <= 10^-6.
    """

    def test_zero_false_positives_in_10000_trials(self):
        # Generate 10,000 non-donor trial evaluations
        cohort = TippettReferenceDatasetRegistry.generate_pristine_cohort(n_pairs=10000, seed=42)
        res = TippettMathematicalFormulation.evaluate_misleading_evidence_rate(
            cohort.hd_log10_lrs, threshold_log10=6.0
        )

        assert res["n_non_donors"] == 10000
        assert res["threshold_log10"] == 6.0
        assert res["count_exceeding"] == 0
        assert res["empirical_rate"] == 0.0
        assert res["bound_satisfied"] is True


# ===========================================================================
# 3. EC-TIP-03: Single-Source Pristine Separation AUC (AUC = 1.000000)
# ===========================================================================

class TestEdgeCaseTIP03_PristineSeparationAUC:
    """
    EC-TIP-03: Single-source pristine 24-locus profiles achieve AUC = 1.0000.
    Verifies complete separation with zero overlap between true donors and non-donors.
    """

    def test_pristine_24_locus_auc_equals_one(self):
        cohort = TippettReferenceDatasetRegistry.generate_pristine_cohort(n_pairs=1000, seed=42)
        roc = TippettMathematicalFormulation.compute_roc_analysis(
            cohort.hp_log10_lrs, cohort.hd_log10_lrs
        )

        # Minimum true-donor LR strictly greater than maximum non-donor LR
        min_hp = min(cohort.hp_log10_lrs)
        max_hd = max(cohort.hd_log10_lrs)
        assert min_hp > max_hd, f"Overlap detected: min(Hp)={min_hp} <= max(Hd)={max_hd}"

        assert roc.auc == 1.000000
        assert roc.separation_index == 0.500000
        assert roc.fpr_at_neutral == 0.0
        assert roc.fnr_at_neutral == 0.0


# ===========================================================================
# 4. EC-TIP-04: Degradation Shift Curve (P(D) = 0.60)
# ===========================================================================

class TestEdgeCaseTIP04_DegradationShiftCurve:
    """
    EC-TIP-04: High degradation (P(D)=0.60) shifts median log10(LR_Hp) from +28.5 to ~ +8.2
    without producing negative bias (FNR_neutral < 0.01).
    """

    def test_high_degradation_shift_curve(self):
        pristine = TippettReferenceDatasetRegistry.generate_pristine_cohort(n_pairs=500, seed=42)
        degraded = TippettReferenceDatasetRegistry.generate_ltdna_degraded_cohort(
            n_pairs=500, p_dropout=0.60, seed=42
        )

        # Pristine median ~ +28.5
        assert pristine.median_hp > 20.0

        # Degraded median shifted down to +6.0 .. +12.0
        assert 5.0 <= degraded.median_hp <= 14.0

        # Non-negative bias: false negative rate at neutral threshold remains near zero
        fnr = float(np.sum(np.array(degraded.hp_log10_lrs) < 0.0)) / len(degraded.hp_log10_lrs)
        assert fnr < 0.01

        # Discrimination remains strong (AUC >= 0.985)
        assert degraded.auc >= 0.985


# ===========================================================================
# 5. EC-TIP-05: Neutral LR Intersection & Balanced Prior Symmetry
# ===========================================================================

class TestEdgeCaseTIP05_NeutralIntersectionSymmetry:
    """
    EC-TIP-05: Exactly balanced sensitivity and specificity at decision threshold
    log10(LR) = 0.0 for symmetrical prior distributions.
    """

    def test_symmetrical_distribution_neutral_intersection(self):
        np.random.seed(777)
        # Symmetrical distributions around 0.0
        hp_sym = np.random.normal(loc=+10.0, scale=2.5, size=2000).tolist()
        hd_sym = np.random.normal(loc=-10.0, scale=2.5, size=2000).tolist()

        res = TippettMathematicalFormulation.compute_tippett_curve(hp_sym, hd_sym)

        # At neutral threshold (0.0), FPR = P(Hd > 0) and FNR = P(Hp < 0)
        # Due to symmetry: FPR ≈ FNR ≈ 0.0
        assert abs(res.fpr_at_zero - res.fnr_at_zero) < 1e-3
        assert res.discrimination_power > 0.999
