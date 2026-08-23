"""
Unit tests for Transcendental Approximators, Plookup Table Lookups & Multi-Locus Lod Accumulator.
"""

import pytest
import math
from backend.node.services.forensic.zk.gadgets.transcendental import PiecewiseChebyshevLogApproximator
from backend.node.services.forensic.zk.gadgets.lookups import PlookupTableEngine
from backend.node.services.forensic.zk.gadgets.lod_accumulator import MultiLocusLodAccumulator
from backend.node.services.forensic.zk.fixed_point import FixedPointEngine


def test_piecewise_chebyshev_log_evaluation():
    chebyshev = PiecewiseChebyshevLogApproximator(scale_s=16)
    test_inputs = [0.05, 0.5, 2.5, 100.0]

    for x in test_inputs:
        approx_val, k, steps = chebyshev.evaluate_horner(x)
        expected_log10 = math.log10(x)
        # Verify approximation is within reasonable bound of true log10
        assert abs(approx_val - expected_log10) < 0.25

        # Verify witness synthesis and constraint generation
        witness, res_hat, _ = chebyshev.synthesize_witness(x, prefix=f"h_{int(x*100)}")
        constraints = chebyshev.generate_constraints(prefix=f"h_{int(x*100)}")
        for c in constraints:
            assert c.is_satisfied(witness) is True


def test_plookup_table_lookup_and_containment():
    plookup = PlookupTableEngine(table_size=256, scale_s=16)
    u, log10_hat = plookup.lookup(10)
    assert u == 10

    # log10(10) == 1.0 => quantized is 1 * 65536 = 65536
    fp = FixedPointEngine(scale_s=16)
    deq = fp.dequantize(log10_hat)
    assert abs(deq - 1.0) < 1e-3

    # Table containment check
    valid_pairs = [plookup.lookup(1), plookup.lookup(10), plookup.lookup(100)]
    assert plookup.verify_lookup_containment(valid_pairs) is True

    # Invalid pair
    invalid_pairs = [(10, 999999)]
    assert plookup.verify_lookup_containment(invalid_pairs) is False


def test_multi_locus_lod_accumulator_additivity():
    accumulator = MultiLocusLodAccumulator(scale_s=16, locus_count=4)
    per_locus = {
        "TH01": 1.25,
        "D21S11": 2.50,
        "D18S51": 0.75,
        "vWA": 1.50,
    }
    # Sum = 6.0
    witness, total_q, total_cont = accumulator.synthesize_witness(per_locus, prefix="lod_test")
    assert abs(total_cont - 6.0) < 1e-6

    fp = FixedPointEngine(scale_s=16)
    total_deq = fp.dequantize(total_q)
    assert abs(total_deq - 6.0) < 1e-3

    constraints = accumulator.generate_constraints(list(per_locus.keys()), prefix="lod_test")
    for c in constraints:
        assert c.is_satisfied(witness) is True

    # Invariant verification
    is_valid = accumulator.verify_additivity_invariant(list(per_locus.values()), total_cont)
    assert is_valid is True
