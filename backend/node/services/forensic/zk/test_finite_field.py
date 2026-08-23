"""
Unit tests for Galois Field Fr arithmetic & Elliptic Curve operations.
"""

import pytest
from backend.node.services.forensic.zk.finite_field import (
    FieldElement,
    CurvePointG1,
    BilinearPairingEngine,
    BN254_SCALAR_FIELD_R,
    BN254_BASE_FIELD_Q,
    BN254_G1_GEN_X,
    BN254_G1_GEN_Y,
)


def test_field_element_addition_and_subtraction():
    a = FieldElement(15, BN254_SCALAR_FIELD_R)
    b = FieldElement(25, BN254_SCALAR_FIELD_R)
    c = a + b
    assert c.value == 40
    d = c - a
    assert d.value == 25


def test_field_element_multiplication_and_fermat_inversion():
    a = FieldElement(7, BN254_SCALAR_FIELD_R)
    b = FieldElement(11, BN254_SCALAR_FIELD_R)
    prod = a * b
    assert prod.value == 77

    # Fermat inverse: a * a^-1 == 1 (mod r)
    inv_a = FieldElement(1, BN254_SCALAR_FIELD_R) / a
    one = a * inv_a
    assert one.value == 1


def test_field_element_division_by_zero():
    a = FieldElement(10, BN254_SCALAR_FIELD_R)
    zero = FieldElement(0, BN254_SCALAR_FIELD_R)
    with pytest.raises(ZeroDivisionError):
        _ = a / zero


def test_curve_point_g1_addition_and_scalar_mul():
    # Generator point G1 = (1, 2)
    g1 = CurvePointG1(BN254_G1_GEN_X, BN254_G1_GEN_Y)
    assert g1.is_on_curve is True

    # 2 * G1 via addition vs scalar_mul
    g2_add = g1 + g1
    g2_mul = g1.scalar_mul(2)
    assert g2_add == g2_mul

    # 0 * G1 == point at infinity
    g0 = g1.scalar_mul(0)
    assert g0.is_infinity is True


def test_bilinear_pairing_check_groth16_soundness():
    # True relation: a * b == alpha * beta + public_comb + c * delta (mod r)
    r = BN254_SCALAR_FIELD_R
    alpha = 5
    beta = 7
    gamma = 11
    delta = 13
    public_comb = 100

    c = 17
    # a * b = 5*7 + 100 + 17*13 = 35 + 100 + 221 = 356
    a = 2
    b = 178  # 2 * 178 = 356

    is_valid, res = BilinearPairingEngine.evaluate_groth16_pairing_check(
        proof_a_scalar=a,
        proof_b_scalar=b,
        proof_c_scalar=c,
        alpha_scalar=alpha,
        beta_scalar=beta,
        gamma_scalar=gamma,
        delta_scalar=delta,
        public_inputs_linear_comb=public_comb,
    )
    assert is_valid is True
    assert res == 0

    # Tampered proof: a modified -> fails
    is_invalid, res_bad = BilinearPairingEngine.evaluate_groth16_pairing_check(
        proof_a_scalar=a + 1,
        proof_b_scalar=b,
        proof_c_scalar=c,
        alpha_scalar=alpha,
        beta_scalar=beta,
        gamma_scalar=gamma,
        delta_scalar=delta,
        public_inputs_linear_comb=public_comb,
    )
    assert is_invalid is False
    assert res_bad != 0


def test_kzg_pairing_check_soundness():
    # (C - v + z * pi) == pi * tau (mod r)
    tau = 42
    z = 3
    pi = 5
    v = 10
    # C - 10 + 3*5 = 5 * 42 = 210 => C + 5 = 210 => C = 205
    c_val = 205

    is_valid, res = BilinearPairingEngine.evaluate_kzg_pairing_check(
        commitment_scalar=c_val,
        eval_value_scalar=v,
        eval_point_scalar=z,
        quotient_proof_scalar=pi,
        srs_tau_scalar=tau,
    )
    assert is_valid is True
    assert res == 0
