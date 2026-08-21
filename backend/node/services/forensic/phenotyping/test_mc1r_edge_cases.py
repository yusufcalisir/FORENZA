"""
Empirical Edge-Case Test Suite for MC1R Epistasis & UV Sensitivity (Module 3.5).

Covers:
  - EC-MC1R-01: F_score Clamping Invariant (0 ≤ F_score ≤ 100.0)
  - EC-MC1R-02: Diplotype Classification Monotonicity (n_R accumulation)
  - EC-MC1R-03: Modifier Loci Additivity (ASIP + BNC2 super-position |Δ| < 1e-6)
  - EC-MC1R-04: Diplotype Boundary Exactness (all 6 diplotype state transitions)
  - EC-MC1R-05: VECTOR_15_FRECKLE_B Golden Benchmark (R151C hom, |W-5.70|<1e-3, F≥99%)
"""

import math
import pytest

from backend.node.services.forensic.phenotyping.mc1r_mathematical_formulation import (
    MC1RMathematicalFormulation,
    MC1R_R_WEIGHTS,
    MC1R_r_WEIGHTS,
)


def test_ec_mc1r_01_f_score_clamping_invariant():
    """
    EC-MC1R-01: F_score Clamping Invariant.

    For all valid SNP dosage combinations (dosages ∈ {0, 1, 2} for all 10 loci),
    the resulting F_score must always satisfy 0.0 ≤ F_score ≤ 100.0.

    Specifically tests the extreme upper-bound case of all variants at maximum
    dosage and modifier loci at maximum, which must not exceed 100.0%.
    """
    # Maximum possible: all 5 R-variants at dosage=2, all 3 r-variants at dosage=2, ASIP=2, BNC2=2
    max_dosages = {rsid: 2 for rsid in MC1R_R_WEIGHTS}
    max_dosages.update({rsid: 2 for rsid in MC1R_r_WEIGHTS})
    max_dosages["rs1015362"] = 2
    max_dosages["rs10756819"] = 2

    mc1r = MC1RMathematicalFormulation.run_mc1r_formulation(max_dosages)
    freckle = MC1RMathematicalFormulation.run_freckling_formulation(max_dosages, mc1r.total_mc1r_loss_weight)
    assert 0.0 <= freckle.freckling_score_pct <= 100.0

    # All-zero reference must also be in bounds
    mc1r_zero = MC1RMathematicalFormulation.run_mc1r_formulation({})
    freckle_zero = MC1RMathematicalFormulation.run_freckling_formulation({}, 0.0)
    assert 0.0 <= freckle_zero.freckling_score_pct <= 100.0

    # Exhaustive check: sweep all combinations of single-locus dosages
    all_loci = list(MC1R_R_WEIGHTS.keys()) + list(MC1R_r_WEIGHTS.keys()) + ["rs1015362", "rs10756819"]
    for rsid in all_loci:
        for dose in [0, 1, 2]:
            mc1r = MC1RMathematicalFormulation.run_mc1r_formulation({rsid: dose})
            freckle = MC1RMathematicalFormulation.run_freckling_formulation(
                {rsid: dose}, mc1r.total_mc1r_loss_weight
            )
            assert 0.0 <= freckle.freckling_score_pct <= 100.0, (
                f"Clamp violated for {rsid}={dose}: F_score={freckle.freckling_score_pct}"
            )


def test_ec_mc1r_02_diplotype_monotonicity():
    """
    EC-MC1R-02: Diplotype Classification Monotonicity.

    As n_R increases from 0 to 1 to 2+, the diplotype severity classification
    must monotonically increase (not decrease). Specifically:
      n_R=0, n_r=0 → WILD_TYPE
      n_R=1, n_r=0 → MODERATE_LOSS
      n_R=2, n_r=0 → SEVERE_LOSS

    And with n_r contributions:
      n_R=0, n_r=1 → MILD_LOSS
      n_R=0, n_r=2 → MILD_LOSS (same tier but more loci)
      n_R=1, n_r=1 → MODERATE_LOSS

    Monotonicity = functional classification severity never decreases as dosage increases.
    """
    SEVERITY = {"WILD_TYPE": 0, "MILD_LOSS": 1, "MODERATE_LOSS": 2, "SEVERE_LOSS": 3}

    # Increasing n_R at fixed n_r=0
    prev_sev = 0
    for n_R in range(0, 4):
        _, cls = MC1RMathematicalFormulation.classify_diplotype(n_R, 0)
        sev = SEVERITY[cls]
        assert sev >= prev_sev, (
            f"Monotonicity violated: n_R={n_R} → {cls} (sev={sev}) < prev_sev={prev_sev}"
        )
        prev_sev = sev

    # Adding n_r=1 to each n_R level should not decrease severity
    for n_R in range(0, 3):
        _, cls_no_r = MC1RMathematicalFormulation.classify_diplotype(n_R, 0)
        _, cls_with_r = MC1RMathematicalFormulation.classify_diplotype(n_R, 1)
        sev_no = SEVERITY[cls_no_r]
        sev_with = SEVERITY[cls_with_r]
        assert sev_with >= sev_no, (
            f"Adding n_r=1 decreased severity for n_R={n_R}: {cls_no_r} → {cls_with_r}"
        )


def test_ec_mc1r_03_modifier_additivity_superposition():
    """
    EC-MC1R-03: ASIP + BNC2 Modifier Additivity.

    The combined logit contribution from ASIP=2 and BNC2=2 must equal exactly:
      logit_combined = logit_ASIP_only(2) + logit_BNC2_only(2) - logit_baseline
      = (logit_base + 2*0.85) + (logit_base + 2*0.65) - logit_base
      = logit_base + 1.70 + 1.30 = logit_base + 3.00

    Mathematical superposition residual: |Δ| < 1e-6.
    """
    baseline_f, logit_base = MC1RMathematicalFormulation.compute_freckling_score(0.0, 0.0, 0.0)
    asip2_f, logit_asip2 = MC1RMathematicalFormulation.compute_freckling_score(0.0, 2.0, 0.0)
    bnc2_f, logit_bnc2 = MC1RMathematicalFormulation.compute_freckling_score(0.0, 0.0, 2.0)
    combined_f, logit_combined = MC1RMathematicalFormulation.compute_freckling_score(0.0, 2.0, 2.0)

    # Logit superposition: combined = asip2 + bnc2 - base
    expected_combined_logit = logit_asip2 + logit_bnc2 - logit_base
    delta = abs(logit_combined - expected_combined_logit)
    assert delta < 1e-6, (
        f"ASIP+BNC2 superposition failed: combined_logit={logit_combined}, "
        f"expected={expected_combined_logit}, Δ={delta}"
    )

    # Combined logit should be -2.50 + 1.70 + 1.30 = 0.50
    assert logit_combined == pytest.approx(0.50, abs=1e-6)


def test_ec_mc1r_04_diplotype_boundary_exactness():
    """
    EC-MC1R-04: Diplotype Boundary Exactness.

    All 6 diplotype state transitions must be exactly correct at their boundaries:
      n_R=0, n_r=0 → wt/wt
      n_R=0, n_r=1 → r/wt
      n_R=0, n_r=2 → r/r
      n_R=1, n_r=0 → R/wt
      n_R=1, n_r=1 → R/r
      n_R=2, n_r=0 → R/R
    """
    expected_map = [
        (0, 0, "wt/wt", "WILD_TYPE"),
        (0, 1, "r/wt", "MILD_LOSS"),
        (0, 2, "r/r", "MILD_LOSS"),
        (1, 0, "R/wt", "MODERATE_LOSS"),
        (1, 1, "R/r", "MODERATE_LOSS"),
        (2, 0, "R/R", "SEVERE_LOSS"),
    ]

    for n_R, n_r, expected_dip, expected_cls in expected_map:
        d, c = MC1RMathematicalFormulation.classify_diplotype(n_R, n_r)
        assert d == expected_dip, (
            f"n_R={n_R}, n_r={n_r}: expected diplotype '{expected_dip}', got '{d}'"
        )
        assert c == expected_cls, (
            f"n_R={n_R}, n_r={n_r}: expected class '{expected_cls}', got '{c}'"
        )


def test_ec_mc1r_05_vector_15_freckle_b_golden_benchmark():
    """
    EC-MC1R-05: VECTOR_15_FRECKLE_B Golden Benchmark (R151C Homozygous).

    Research §5 Golden Vector: rs1805007 = 2 (R151C Val370Ala homozygous)
    Expected:
      - W_MC1R = 5.70   (|computed - 5.70| < 1e-3)
      - Diplotype = R/R
      - Functional class = SEVERE_LOSS
      - F_score ≥ 99.0% (logit = -2.50 + 1.35*5.70 = 5.195)
      - Intensity = DENSE
      - MED = < 20 mJ/cm²
      - Tanning = NEVER_TANS_ALWAYS_BURNS
    """
    snp_dosages = {"rs1805007": 2}

    mc1r = MC1RMathematicalFormulation.run_mc1r_formulation(snp_dosages)
    freckle = MC1RMathematicalFormulation.run_freckling_formulation(snp_dosages, mc1r.total_mc1r_loss_weight)
    uv = MC1RMathematicalFormulation.run_uv_formulation(mc1r.diplotype)

    # W_MC1R golden check
    assert abs(mc1r.total_mc1r_loss_weight - 5.70) < 1e-3, (
        f"VECTOR_15_FRECKLE_B W_MC1R failed: got {mc1r.total_mc1r_loss_weight}, expected 5.70"
    )

    # Diplotype golden check
    assert mc1r.diplotype == "R/R"
    assert mc1r.functional_classification == "SEVERE_LOSS"
    assert mc1r.r_high_risk_alleles_count == 2

    # Freckling golden check
    assert freckle.freckling_score_pct >= 99.0, (
        f"VECTOR_15_FRECKLE_B F_score failed: got {freckle.freckling_score_pct}, expected ≥99.0"
    )
    assert "DENSE" in freckle.freckling_intensity

    # MED golden check
    assert "< 20" in uv.minimal_erythema_dose_category
    assert uv.tanning_capacity == "NEVER_TANS_ALWAYS_BURNS"
