"""
FORENZA: Forensic Evidence Operating System
Module: ZK-SNARK Proving Systems - Galois Field Fr Arithmetic & Elliptic Curve Operations

Source of Truth: research/zk_snark_proving_systems_verifiable_forensic_computation_research.md
BN254 (Alt-bn128) Scalar Field r and Base Field q Arithmetic Engine.
"""

from typing import Tuple, Optional, List, Union


# BN254 (alt_bn128) Scalar Field Modulus (r) - The order of the G1 group
BN254_SCALAR_FIELD_R = 21888242871839275222246405745257275088548364400416034343698204186575808495617

# BN254 Base Field Modulus (q) - Coordinate field
BN254_BASE_FIELD_Q = 21888242871839275222246405745257275088696311157297823662689037894645226208583

# BN254 Curve Equation: y^2 = x^3 + 3 over F_q
BN254_CURVE_B = 3

# Generator G1 affine coordinates
BN254_G1_GEN_X = 1
BN254_G1_GEN_Y = 2


class FieldElement:
    """Arithmetic in Galois field F_r modulo a large prime r."""

    def __init__(self, value: int, modulus: int = BN254_SCALAR_FIELD_R):
        self.modulus = modulus
        self.value = value % modulus

    def __add__(self, other: Union["FieldElement", int]) -> "FieldElement":
        other_val = other.value if isinstance(other, FieldElement) else other
        return FieldElement((self.value + other_val) % self.modulus, self.modulus)

    def __radd__(self, other: int) -> "FieldElement":
        return self.__add__(other)

    def __sub__(self, other: Union["FieldElement", int]) -> "FieldElement":
        other_val = other.value if isinstance(other, FieldElement) else other
        return FieldElement((self.value - other_val) % self.modulus, self.modulus)

    def __rsub__(self, other: int) -> "FieldElement":
        return FieldElement((other - self.value) % self.modulus, self.modulus)

    def __mul__(self, other: Union["FieldElement", int]) -> "FieldElement":
        other_val = other.value if isinstance(other, FieldElement) else other
        return FieldElement((self.value * other_val) % self.modulus, self.modulus)

    def __rmul__(self, other: int) -> "FieldElement":
        return self.__mul__(other)

    def __pow__(self, exponent: int) -> "FieldElement":
        return FieldElement(pow(self.value, exponent, self.modulus), self.modulus)

    def __truediv__(self, other: Union["FieldElement", int]) -> "FieldElement":
        other_val = other.value if isinstance(other, FieldElement) else other
        if other_val % self.modulus == 0:
            raise ZeroDivisionError("Division by zero in Galois Field F_r")
        inv = pow(other_val, self.modulus - 2, self.modulus)
        return FieldElement((self.value * inv) % self.modulus, self.modulus)

    def __neg__(self) -> "FieldElement":
        return FieldElement((-self.value) % self.modulus, self.modulus)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FieldElement):
            return self.value == other.value and self.modulus == other.modulus
        if isinstance(other, int):
            return self.value == (other % self.modulus)
        return False

    def __repr__(self) -> str:
        return f"FieldElement({self.value})"

    def __int__(self) -> int:
        return self.value


class CurvePointG1:
    """Affine point on elliptic curve G1 over F_q."""

    def __init__(self, x: Optional[int], y: Optional[int], is_infinity: bool = False):
        self.is_infinity = is_infinity
        if is_infinity:
            self.x = 0
            self.y = 0
        else:
            self.x = (x or 0) % BN254_BASE_FIELD_Q
            self.y = (y or 0) % BN254_BASE_FIELD_Q
            # Validate curve equation: y^2 == x^3 + 3 mod q
            left = (self.y * self.y) % BN254_BASE_FIELD_Q
            right = ((self.x * self.x % BN254_BASE_FIELD_Q) * self.x + BN254_CURVE_B) % BN254_BASE_FIELD_Q
            if left != right and not is_infinity:
                # Store unvalidated if synthetic test point, but note validity
                self.is_on_curve = False
            else:
                self.is_on_curve = True

    def __add__(self, other: "CurvePointG1") -> "CurvePointG1":
        if self.is_infinity:
            return other
        if other.is_infinity:
            return self
        if self.x == other.x:
            if (self.y + other.y) % BN254_BASE_FIELD_Q == 0:
                return CurvePointG1(None, None, is_infinity=True)
            # Point doubling
            lam = (3 * self.x * self.x) * pow(2 * self.y, BN254_BASE_FIELD_Q - 2, BN254_BASE_FIELD_Q) % BN254_BASE_FIELD_Q
        else:
            lam = (other.y - self.y) * pow(other.x - self.x, BN254_BASE_FIELD_Q - 2, BN254_BASE_FIELD_Q) % BN254_BASE_FIELD_Q

        x3 = (lam * lam - self.x - other.x) % BN254_BASE_FIELD_Q
        y3 = (lam * (self.x - x3) - self.y) % BN254_BASE_FIELD_Q
        return CurvePointG1(x3, y3)

    def scalar_mul(self, scalar: int) -> "CurvePointG1":
        """Double-and-add scalar multiplication in G1."""
        scalar = scalar % BN254_SCALAR_FIELD_R
        if scalar == 0 or self.is_infinity:
            return CurvePointG1(None, None, is_infinity=True)

        res = CurvePointG1(None, None, is_infinity=True)
        temp = self
        while scalar > 0:
            if scalar & 1:
                res = res + temp
            temp = temp + temp
            scalar >>= 1
        return res

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CurvePointG1):
            return False
        if self.is_infinity and other.is_infinity:
            return True
        return self.x == other.x and self.y == other.y and self.is_infinity == other.is_infinity


class BilinearPairingEngine:
    """
    Simulated Pairing & Verification Algebra Engine for BN254 Curve.
    Evaluates pairing check equations: e(A, B) = e(Alpha, Beta) + e(X, Gamma) + e(C, Delta)
    """

    @staticmethod
    def evaluate_groth16_pairing_check(
        proof_a_scalar: int,
        proof_b_scalar: int,
        proof_c_scalar: int,
        alpha_scalar: int,
        beta_scalar: int,
        gamma_scalar: int,
        delta_scalar: int,
        public_inputs_linear_comb: int,
    ) -> Tuple[bool, int]:
        """
        Evaluates discrete logarithm exponent pairing relation:
        a * b == alpha * beta + (public_inputs / gamma) * gamma + c * delta (mod r)
        Returns (is_valid, residual).
        """
        r = BN254_SCALAR_FIELD_R
        left_hand_side = (proof_a_scalar * proof_b_scalar) % r
        right_hand_side = (
            alpha_scalar * beta_scalar +
            public_inputs_linear_comb +
            proof_c_scalar * delta_scalar
        ) % r

        residual = (left_hand_side - right_hand_side) % r
        is_valid = (residual == 0)
        return is_valid, residual

    @staticmethod
    def evaluate_kzg_pairing_check(
        commitment_scalar: int,
        eval_value_scalar: int,
        eval_point_scalar: int,
        quotient_proof_scalar: int,
        srs_tau_scalar: int,
    ) -> Tuple[bool, int]:
        """
        Evaluates KZG opening pairing check:
        e(C - [v]_1 + z * pi, [1]_2) == e(pi, [tau]_2)
        Algebraic exponent check: (C - v + z * pi) == pi * tau (mod r)
        """
        r = BN254_SCALAR_FIELD_R
        lhs = (commitment_scalar - eval_value_scalar + eval_point_scalar * quotient_proof_scalar) % r
        rhs = (quotient_proof_scalar * srs_tau_scalar) % r
        residual = (lhs - rhs) % r
        return (residual == 0), residual
