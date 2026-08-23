"""
Unit tests for ZK Circuit Gadgets (Range Check, Multiplication, Non-Deterministic Division, Threshold).
"""

import pytest
from backend.node.services.forensic.zk.gadgets.range_check import R1CSConstraint, RangeCheckGadget
from backend.node.services.forensic.zk.gadgets.arithmetic import ScaledMultiplicationGadget
from backend.node.services.forensic.zk.gadgets.division import NonDeterministicDivisionGadget
from backend.node.services.forensic.zk.gadgets.threshold import ThresholdInclusionGadget
from backend.node.services.forensic.zk.finite_field import BN254_SCALAR_FIELD_R


def test_r1cs_constraint_evaluation():
    # 2 * 3 == 6
    c = R1CSConstraint(a_terms={"x": 1}, b_terms={"y": 1}, c_terms={"z": 1})
    witness = {"x": 2, "y": 3, "z": 6}
    assert c.is_satisfied(witness) is True

    witness_bad = {"x": 2, "y": 3, "z": 7}
    assert c.is_satisfied(witness_bad) is False


def test_range_check_gadget_valid_and_overflow():
    rc16 = RangeCheckGadget(bitwidth=16)
    val = 50000  # < 65536
    witness = rc16.synthesize_witness(val, prefix="test_rc")
    constraints = rc16.generate_constraints("test_rc", prefix="test_rc")

    # Verify all constraints pass with honest witness
    for c in constraints:
        assert c.is_satisfied(witness) is True

    # Overflow: 70000 >= 65536
    with pytest.raises(ValueError):
        _ = rc16.synthesize_witness(70000, prefix="test_rc")


def test_scaled_multiplication_gadget_satisfaction():
    gadget = ScaledMultiplicationGadget(scale_s=16, max_bitwidth_b=64)
    x_hat = 2 * 65536  # 2.0
    y_hat = 3 * 65536  # 3.0

    witness, z_hat, r = gadget.synthesize_witness(x_hat, y_hat, prefix="mul1")
    assert z_hat == 6 * 65536  # 6.0
    assert r == 0

    constraints = gadget.generate_constraints(prefix="mul1")
    for c in constraints:
        assert c.is_satisfied(witness) is True


def test_non_deterministic_division_gadget_soundness():
    gadget = NonDeterministicDivisionGadget(scale_s=16, max_bitwidth_b=64)
    # N = 1000, D = 4 => LR = 250
    # N_hat = 1000 * 65536, D_hat = 4 * 65536
    # N_hat * 2^16 / D_hat = 1000 * 65536 * 65536 / (4 * 65536) = 250 * 65536
    n_hat = 1000 * 65536
    d_hat = 4 * 65536

    witness, lr_hat, r = gadget.synthesize_witness(n_hat, d_hat, prefix="div1")
    assert lr_hat == 250 * 65536
    assert r == 0

    constraints = gadget.generate_constraints(prefix="div1")
    for c in constraints:
        assert c.is_satisfied(witness) is True


def test_threshold_inclusion_gadget_true_match_and_exclusion():
    gadget = ThresholdInclusionGadget(bitwidth_b=64)

    # True Match: LR_hat = 10^8 >= M_thresh = 10^6
    lr_hat = 100000000
    thresh_hat = 1000000

    witness_match, delta, is_match = gadget.synthesize_witness(lr_hat, thresh_hat, prefix="th1")
    assert is_match is True
    assert delta == 99000000

    constraints = gadget.generate_constraints(prefix="th1")
    for c in constraints:
        assert c.is_satisfied(witness_match) is True

    # Exclusion: LR_hat = 500 < M_thresh = 1000000
    lr_low = 500
    witness_excl, delta_bad, is_match_bad = gadget.synthesize_witness(lr_low, thresh_hat, prefix="th1")
    assert is_match_bad is False
    # Constraints will fail because delta_bad is large wrap-around in F_r (cannot be decomposed in 64 bits)
    satisfied_all = all(c.is_satisfied(witness_excl) for c in constraints)
    assert satisfied_all is False
