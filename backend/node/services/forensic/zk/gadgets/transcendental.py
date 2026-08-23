"""
FORENZA: Forensic Evidence Operating System
Module: ZK-SNARK Proving Systems - Piecewise Polynomial Transcendental Evaluator

Source of Truth: research/zk_snark_proving_systems_verifiable_forensic_computation_research.md
Piecewise Chebyshev / Remez Polynomial Approximation for ln(x) & log10(x) with Horner Circuit Evaluation.
"""

from typing import List, Tuple, Dict, Any, Optional
import math
from ..finite_field import BN254_SCALAR_FIELD_R
from ..fixed_point import FixedPointEngine
from .range_check import R1CSConstraint


class PiecewiseChebyshevLogApproximator:
    """
    Evaluates log10(x) or ln(x) using cubic piecewise polynomials via Horner's method:
    P_k(x) = c0 + x * (c1 + x * (c2 + x * c3))
    """

    def __init__(
        self,
        scale_s: int = 16,
        modulus: int = BN254_SCALAR_FIELD_R,
        intervals: Optional[List[Tuple[float, float]]] = None
    ):
        self.scale_s = scale_s
        self.scale_factor = 1 << scale_s
        self.modulus = modulus
        self.fp = FixedPointEngine(scale_s=scale_s, modulus=modulus)

        # 4 Standard intervals for x in [0.01, 1000.0]
        # [0.01, 0.1], [0.1, 1.0], [1.0, 10.0], [10.0, 1000.0]
        self.intervals = intervals or [
            (0.01, 0.1),
            (0.1, 1.0),
            (1.0, 10.0),
            (10.0, 1000.0),
        ]
        # Precomputed Chebyshev Remez coefficients for log10(x)
        self.coeffs_log10 = [
            (-2.3320, 36.550, -342.10, 1098.00),  # interval 0: [0.01, 0.1]
            (-1.3320, 3.6550, -3.4210, 1.0980),   # interval 1: [0.1, 1.0]
            (-0.2100, 0.2950, -0.0275, 0.0009),   # interval 2: [1.0, 10.0]
            (0.95000, 0.0135, -0.000021, 0.00000001), # interval 3: [10.0, 1000.0]
        ]

    def find_interval(self, x: float) -> int:
        """Finds interval index k containing x."""
        for k, (low, high) in enumerate(self.intervals):
            if low <= x <= high:
                return k
        if x < self.intervals[0][0]:
            return 0
        return len(self.intervals) - 1

    def evaluate_horner(self, x: float) -> Tuple[float, int, List[float]]:
        """
        Evaluates cubic polynomial via Horner's method:
        c0 + x * (c1 + x * (c2 + x * c3))
        Returns (approx_value, interval_idx, intermediate_steps).
        """
        k = self.find_interval(x)
        c0, c1, c2, c3 = self.coeffs_log10[k]

        step1 = c2 + x * c3
        step2 = c1 + x * step1
        res = c0 + x * step2
        return res, k, [step1, step2, res]

    def synthesize_witness(
        self, x_val: float, prefix: str = "horner"
    ) -> Tuple[Dict[str, int], int, float]:
        """
        Synthesizes fixed-point witness for Horner circuit evaluation with exact integer arithmetic.
        """
        approx_val, k, _ = self.evaluate_horner(x_val)
        c0, c1, c2, c3 = self.coeffs_log10[k]

        x_hat = self.fp.quantize(x_val)
        c0_hat = self.fp.quantize(c0)
        c1_hat = self.fp.quantize(c1)
        c2_hat = self.fp.quantize(c2)
        c3_hat = self.fp.quantize(c3)

        # Step 1: z1 = (x_hat * c3_hat) // 2^S, s1 = c2_hat + z1
        prod1 = x_hat * c3_hat
        z1_hat = (prod1 // self.scale_factor) % self.modulus
        r1 = (prod1 % self.scale_factor) % self.modulus
        s1_hat = (c2_hat + z1_hat) % self.modulus

        # Step 2: z2 = (x_hat * s1_hat) // 2^S, s2 = c1_hat + z2
        prod2 = x_hat * s1_hat
        z2_hat = (prod2 // self.scale_factor) % self.modulus
        r2 = (prod2 % self.scale_factor) % self.modulus
        s2_hat = (c1_hat + z2_hat) % self.modulus

        # Step 3: z3 = (x_hat * s2_hat) // 2^S, res = c0_hat + z3
        prod3 = x_hat * s2_hat
        z3_hat = (prod3 // self.scale_factor) % self.modulus
        r3 = (prod3 % self.scale_factor) % self.modulus
        res_hat = (c0_hat + z3_hat) % self.modulus

        witness = {
            "ONE": 1,
            f"{prefix}_x": x_hat,
            f"{prefix}_c0": c0_hat,
            f"{prefix}_c1": c1_hat,
            f"{prefix}_c2": c2_hat,
            f"{prefix}_c3": c3_hat,
            f"{prefix}_z1": z1_hat,
            f"{prefix}_r1": r1,
            f"{prefix}_s1": s1_hat,
            f"{prefix}_z2": z2_hat,
            f"{prefix}_r2": r2,
            f"{prefix}_s2": s2_hat,
            f"{prefix}_z3": z3_hat,
            f"{prefix}_r3": r3,
            f"{prefix}_res": res_hat,
        }
        return witness, res_hat, approx_val

    def generate_constraints(self, prefix: str = "horner") -> List[R1CSConstraint]:
        """
        Generates R1CS constraints for Horner's evaluation:
        1. (x_hat) * (c3_hat) = z1_hat * 2^S + r1
        2. (s1_hat) * ONE = c2_hat + z1_hat
        3. (x_hat) * (s1_hat) = z2_hat * 2^S + r2
        4. (s2_hat) * ONE = c1_hat + z2_hat
        5. (x_hat) * (s2_hat) = z3_hat * 2^S + r3
        6. (res_hat) * ONE = c0_hat + z3_hat
        """
        constraints = []
        # Step 1
        c1_mul = R1CSConstraint(
            a_terms={f"{prefix}_x": 1},
            b_terms={f"{prefix}_c3": 1},
            c_terms={f"{prefix}_z1": self.scale_factor, f"{prefix}_r1": 1}
        )
        c1_add = R1CSConstraint(
            a_terms={f"{prefix}_s1": 1},
            b_terms={"ONE": 1},
            c_terms={f"{prefix}_c2": 1, f"{prefix}_z1": 1}
        )
        # Step 2
        c2_mul = R1CSConstraint(
            a_terms={f"{prefix}_x": 1},
            b_terms={f"{prefix}_s1": 1},
            c_terms={f"{prefix}_z2": self.scale_factor, f"{prefix}_r2": 1}
        )
        c2_add = R1CSConstraint(
            a_terms={f"{prefix}_s2": 1},
            b_terms={"ONE": 1},
            c_terms={f"{prefix}_c1": 1, f"{prefix}_z2": 1}
        )
        # Step 3
        c3_mul = R1CSConstraint(
            a_terms={f"{prefix}_x": 1},
            b_terms={f"{prefix}_s2": 1},
            c_terms={f"{prefix}_z3": self.scale_factor, f"{prefix}_r3": 1}
        )
        c3_add = R1CSConstraint(
            a_terms={f"{prefix}_res": 1},
            b_terms={"ONE": 1},
            c_terms={f"{prefix}_c0": 1, f"{prefix}_z3": 1}
        )
        constraints.extend([c1_mul, c1_add, c2_mul, c2_add, c3_mul, c3_add])
        return constraints
