"""
FORENZA: Forensic Evidence Operating System
Module: ZK-SNARK Proving Systems - Scaled Multiplication & Rescaling Gadget

Source of Truth: research/zk_snark_proving_systems_verifiable_forensic_computation_research.md
Scaled Fixed-Point Multiplication Gadget: x_hat * y_hat = z_hat * 2^S + r with RangeCheck_S(r).
"""

from typing import List, Tuple, Dict, Any, Optional
from ..finite_field import BN254_SCALAR_FIELD_R
from .range_check import R1CSConstraint, RangeCheckGadget


class ScaledMultiplicationGadget:
    """
    Implements fixed-point multiplication with rescale and remainder range checks.
    Constraint: x_hat * y_hat == z_hat * 2^S + r
    Auxiliary: RangeCheck_S(r), RangeCheck_B(z_hat).
    """

    def __init__(self, scale_s: int = 16, max_bitwidth_b: int = 64, modulus: int = BN254_SCALAR_FIELD_R):
        self.scale_s = scale_s
        self.scale_factor = 1 << scale_s
        self.max_bitwidth_b = max_bitwidth_b
        self.modulus = modulus
        self.rc_remainder = RangeCheckGadget(bitwidth=scale_s, modulus=modulus)
        self.rc_quotient = RangeCheckGadget(bitwidth=max_bitwidth_b, modulus=modulus)

    def synthesize_witness(
        self, x_hat: int, y_hat: int, prefix: str = "mul"
    ) -> Tuple[Dict[str, int], int, int]:
        """
        Computes quotient advice z_hat and remainder advice r, synthesizing full witness.
        """
        product = x_hat * y_hat
        z_hat = (product // self.scale_factor) % self.modulus
        r = (product % self.scale_factor) % self.modulus

        witness = {
            "ONE": 1,
            f"{prefix}_x": x_hat % self.modulus,
            f"{prefix}_y": y_hat % self.modulus,
            f"{prefix}_z": z_hat,
            f"{prefix}_r": r,
        }

        # Synthesize bit-decomposition witnesses for range checks
        witness.update(self.rc_remainder.synthesize_witness(r, prefix=f"{prefix}_r_rc"))
        witness.update(self.rc_quotient.synthesize_witness(z_hat, prefix=f"{prefix}_z_rc"))
        return witness, z_hat, r

    def generate_constraints(self, prefix: str = "mul") -> List[R1CSConstraint]:
        """Generates R1CS constraints for multiplication and remainder bounds."""
        constraints = []

        # 1. Main multiplication equation:
        # (x_hat) * (y_hat) = (2^S * z_hat + r)
        c_mul = R1CSConstraint(
            a_terms={f"{prefix}_x": 1},
            b_terms={f"{prefix}_y": 1},
            c_terms={f"{prefix}_z": self.scale_factor, f"{prefix}_r": 1}
        )
        constraints.append(c_mul)

        # 2. Range check constraints on remainder r (0 <= r < 2^S)
        constraints.extend(self.rc_remainder.generate_constraints(f"{prefix}_r", prefix=f"{prefix}_r_rc"))

        # 3. Range check constraints on quotient z_hat (0 <= z_hat < 2^B)
        constraints.extend(self.rc_quotient.generate_constraints(f"{prefix}_z", prefix=f"{prefix}_z_rc"))
        return constraints
