"""
FORENZA: Forensic Evidence Operating System
Module: ZK-SNARK Proving Systems - Privacy-Preserving Threshold Inclusion Gadget

Source of Truth: research/zk_snark_proving_systems_verifiable_forensic_computation_research.md
Proves LR_hat >= M_thresh_hat via non-negative difference RangeCheck_B(Delta) with Zero Leakage.
"""

from typing import List, Tuple, Dict, Any, Optional
from ..finite_field import BN254_SCALAR_FIELD_R
from .range_check import R1CSConstraint, RangeCheckGadget


class ThresholdInclusionGadget:
    """
    Zero-Knowledge Threshold Inclusion Gadget:
    Proves LR_hat >= M_thresh_hat without revealing LR_hat.
    Enforces: (LR_hat - M_thresh_hat) * 1 == Delta
    with RangeCheck_B(Delta).
    """

    def __init__(self, bitwidth_b: int = 64, modulus: int = BN254_SCALAR_FIELD_R):
        self.bitwidth_b = bitwidth_b
        self.modulus = modulus
        self.rc_delta = RangeCheckGadget(bitwidth=bitwidth_b, modulus=modulus)

    def synthesize_witness(
        self, lr_hat: int, threshold_hat: int, prefix: str = "thresh"
    ) -> Tuple[Dict[str, int], int, bool]:
        """
        Synthesizes witness for threshold inclusion check.
        Returns (witness_dict, delta, is_satisfied).
        """
        delta = (lr_hat - threshold_hat) % self.modulus
        is_satisfied = (lr_hat >= threshold_hat) and (lr_hat - threshold_hat < (1 << self.bitwidth_b))

        witness = {
            "ONE": 1,
            f"{prefix}_LR": lr_hat % self.modulus,
            f"{prefix}_M": threshold_hat % self.modulus,
            f"{prefix}_delta": delta,
        }

        if is_satisfied:
            witness.update(self.rc_delta.synthesize_witness(lr_hat - threshold_hat, prefix=f"{prefix}_delta_rc"))
        else:
            # For unsatisfied condition, populate dummy or wrap-around (will fail range check)
            witness[f"{prefix}_delta_rc"] = delta
            for i in range(self.bitwidth_b):
                witness[f"{prefix}_delta_rc_b{i}"] = (delta >> i) & 1

        return witness, delta, is_satisfied

    def generate_constraints(self, prefix: str = "thresh") -> List[R1CSConstraint]:
        """Generates R1CS constraints for threshold difference and non-negativity."""
        constraints = []

        # 1. Subtraction equality constraint: (LR_hat - M_thresh_hat) * 1 == delta
        c_sub = R1CSConstraint(
            a_terms={f"{prefix}_LR": 1, f"{prefix}_M": -1 % self.modulus},
            b_terms={"ONE": 1},
            c_terms={f"{prefix}_delta": 1}
        )
        constraints.append(c_sub)

        # 2. Range check on delta guaranteeing 0 <= delta < 2^B
        constraints.extend(self.rc_delta.generate_constraints(f"{prefix}_delta", prefix=f"{prefix}_delta_rc"))
        return constraints
