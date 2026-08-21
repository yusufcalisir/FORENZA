"""
Empirical Edge-Case Test Suite for Hair Morphology & Balding PRS (Module 3.4).

Covers:
  - EC-HAIR-01: EDAR Curl Clamping Invariant (C_curl ∈ [0.0, 10.0])
  - EC-HAIR-02: Curl Index Additivity & TCHH/WNT10A Superposition (|Δ| < 1e-6)
  - EC-HAIR-03: PRS Non-Negativity & Additive Monotonicity
  - EC-HAIR-04: Hamilton-Norwood Grade Boundary Exactness (all 3 thresholds)
  - EC-HAIR-05: VECTOR_P3_03 East Asian EDAR Golden Benchmark (|area - 6690.0| < 0.1)
"""

import pytest
import math

from backend.node.services.forensic.phenotyping.hair_mathematical_formulation import (
    HairMathematicalFormulation,
    BALDING_PRS_LOCI,
    HN_GRADE_I_II_THRESHOLD,
    HN_GRADE_III_THRESHOLD,
    HN_GRADE_IV_V_THRESHOLD,
)


def test_ec_hair_01_edar_curl_clamping_invariant():
    """
    EC-HAIR-01: EDAR Curl Clamping Invariant.

    For any EDAR dosage X_EDAR ∈ {0, 1, 2} with zero TCHH and WNT10A,
    the clamped C_curl must always satisfy:
      C_curl ∈ [0.0, 10.0]

    Specifically, high EDAR drives raw C_curl negative (-3.0 at X_EDAR=2),
    which MUST be clamped to exactly 0.0.
    The raw value (pre-clamp) should be correctly returned for diagnostics.
    """
    # X_EDAR=2 → raw = 1.20 - 4.20 = -3.0 → clamped must be 0.0
    c_clamped, c_raw = HairMathematicalFormulation.compute_curl_density_index(2.0, 0.0, 0.0)
    assert c_clamped == pytest.approx(0.0, abs=1e-9), (
        f"EDAR=2 clamp failed: got {c_clamped}, expected 0.0"
    )
    assert c_raw == pytest.approx(-3.0, abs=1e-3), (
        f"EDAR=2 raw curl failed: got {c_raw}, expected -3.0"
    )

    # All permutations of EDAR ∈ {0, 1, 2} must produce C_curl ∈ [0.0, 10.0]
    for edar in [0, 1, 2]:
        for tchh in [0, 1, 2]:
            for wnt10a in [0, 1, 2]:
                c, _ = HairMathematicalFormulation.compute_curl_density_index(
                    float(edar), float(tchh), float(wnt10a)
                )
                assert 0.0 <= c <= 10.0, (
                    f"Clamp violated for EDAR={edar}, TCHH={tchh}, WNT10A={wnt10a}: C_curl={c}"
                )


def test_ec_hair_02_curl_additivity_superposition():
    """
    EC-HAIR-02: Curl Index Additivity & TCHH/WNT10A Superposition.

    The combined TCHH=2 + WNT10A=2 curl index must exactly equal the
    sum of individual contributions plus baseline:
      C_curl(TCHH=2, WNT10A=2) = C_curl(TCHH=2) + C_curl(WNT10A=2) - baseline
                                 = (1.20 + 3.70) + (1.20 + 2.84) - 1.20
                                 = 4.90 + 4.04 - 1.20 = 7.74

    Mathematical equivalence: |Δ| < 1e-6.
    """
    baseline = 1.20
    c_tchh2, _ = HairMathematicalFormulation.compute_curl_density_index(0.0, 2.0, 0.0)
    c_wnt2, _ = HairMathematicalFormulation.compute_curl_density_index(0.0, 0.0, 2.0)
    c_combined, _ = HairMathematicalFormulation.compute_curl_density_index(0.0, 2.0, 2.0)

    expected_combined = (c_tchh2 + c_wnt2) - baseline
    delta = abs(c_combined - expected_combined)

    assert delta < 1e-6, (
        f"Curl superposition failed: combined={c_combined}, "
        f"expected (sum-baseline)={expected_combined}, Δ={delta}"
    )
    assert c_combined == pytest.approx(7.74, abs=1e-3)


def test_ec_hair_03_prs_non_negativity_and_monotonicity():
    """
    EC-HAIR-03: PRS Non-Negativity & Additive Monotonicity.

    1. PRS must be ≥ 0 for all non-negative dosages.
    2. PRS must be strictly monotonically increasing as each locus dosage increases:
       PRS(X_i=0) < PRS(X_i=1) < PRS(X_i=2) for every locus, holding others at 0.
    """
    # Non-negativity across all 3^4 = 81 permutations
    for d1 in [0, 1, 2]:
        for d2 in [0, 1, 2]:
            for d3 in [0, 1, 2]:
                for d4 in [0, 1, 2]:
                    prs = HairMathematicalFormulation.compute_balding_prs(
                        {"rs6152": d1, "rs2180439": d2, "rs1160312": d3, "rs756853": d4}
                    )
                    assert prs >= 0.0, (
                        f"PRS negative: {prs} for dosages ({d1},{d2},{d3},{d4})"
                    )

    # Strict monotonicity per locus (holding others at 0)
    for rsid in BALDING_PRS_LOCI:
        prs_0 = HairMathematicalFormulation.compute_balding_prs({rsid: 0})
        prs_1 = HairMathematicalFormulation.compute_balding_prs({rsid: 1})
        prs_2 = HairMathematicalFormulation.compute_balding_prs({rsid: 2})
        assert prs_0 < prs_1 < prs_2, (
            f"Monotonicity violated for {rsid}: PRS_0={prs_0}, PRS_1={prs_1}, PRS_2={prs_2}"
        )


def test_ec_hair_04_hamilton_norwood_boundary_exactness():
    """
    EC-HAIR-04: Hamilton-Norwood Grade Boundary Exactness.

    All three grade boundaries must produce the correct UPPER grade assignment:
      PRS = 0.50 → GRADE_III (at threshold → new grade)
      PRS = 1.20 → GRADE_IV_V
      PRS = 2.10 → GRADE_VI_VII

    And the immediately sub-threshold values must produce the LOWER grade:
      PRS = 0.499999 → GRADE_I_II
      PRS = 1.199999 → GRADE_III
      PRS = 2.099999 → GRADE_IV_V
    """
    # At threshold → upper grade
    grade_at_050, _, _ = HairMathematicalFormulation.classify_hamilton_norwood(0.50)
    assert grade_at_050 == "GRADE_III", f"At PRS=0.50: expected GRADE_III, got {grade_at_050}"

    grade_at_120, _, _ = HairMathematicalFormulation.classify_hamilton_norwood(1.20)
    assert grade_at_120 == "GRADE_IV_V", f"At PRS=1.20: expected GRADE_IV_V, got {grade_at_120}"

    grade_at_210, _, _ = HairMathematicalFormulation.classify_hamilton_norwood(2.10)
    assert grade_at_210 == "GRADE_VI_VII", f"At PRS=2.10: expected GRADE_VI_VII, got {grade_at_210}"

    # Just below threshold → lower grade
    grade_below_050, _, _ = HairMathematicalFormulation.classify_hamilton_norwood(0.499999)
    assert grade_below_050 == "GRADE_I_II", f"Below PRS=0.50: expected GRADE_I_II, got {grade_below_050}"

    grade_below_120, _, _ = HairMathematicalFormulation.classify_hamilton_norwood(1.199999)
    assert grade_below_120 == "GRADE_III", f"Below PRS=1.20: expected GRADE_III, got {grade_below_120}"

    grade_below_210, _, _ = HairMathematicalFormulation.classify_hamilton_norwood(2.099999)
    assert grade_below_210 == "GRADE_IV_V", f"Below PRS=2.10: expected GRADE_IV_V, got {grade_below_210}"


def test_ec_hair_05_vector_p3_03_east_asian_golden_benchmark():
    """
    EC-HAIR-05: VECTOR_P3_03 East Asian EDAR Golden Benchmark.

    Research §4 Golden Vector: rs3827072=2 (EDAR Val370Ala homozygous)
    Expected:
      - Fiber Area = 6690.0 μm²  (|computed - 6690.0| < 0.1)
      - C_curl = 0.00            (clamped, |computed - 0.0| < 1e-6)
      - Texture = STRAIGHT
      - Fiber diameter = Thick Straight / Asian Variant
      - PRS = 0.00 (no balding loci)
      - Hamilton-Norwood = GRADE_I_II
    """
    # Exact VECTOR_P3_03 genotype
    snp_dosages = {
        "rs3827072": 2,    # EDAR Val370Ala homozygous
        "rs11803731": 0,   # TCHH reference
        "rs7349332": 0,    # WNT10A reference
    }

    tex = HairMathematicalFormulation.run_hair_texture_formulation(snp_dosages)
    bld = HairMathematicalFormulation.run_balding_prs_formulation(snp_dosages)

    # Fiber area golden check
    assert abs(tex.fiber_cross_sectional_area_um2 - 6690.0) < 0.1, (
        f"VECTOR_P3_03 area failed: got {tex.fiber_cross_sectional_area_um2}, expected 6690.0"
    )

    # Curl index golden check
    assert abs(tex.curl_density_index - 0.0) < 1e-6, (
        f"VECTOR_P3_03 curl failed: got {tex.curl_density_index}, expected 0.0"
    )

    # Texture category
    assert tex.texture_category == "STRAIGHT"

    # Diameter category must mention "Thick Straight"
    assert "Thick Straight" in tex.fiber_diameter_category, (
        f"VECTOR_P3_03 diameter: got '{tex.fiber_diameter_category}'"
    )

    # PRS golden check
    assert bld.prs_score == pytest.approx(0.0, abs=1e-9)
    assert bld.hamilton_norwood_grade == "GRADE_I_II"
    assert bld.risk_level == "LOW_RISK"
