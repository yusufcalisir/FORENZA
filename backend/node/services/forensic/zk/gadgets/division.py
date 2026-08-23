"""
FORENZA: Forensic Evidence Operating System
Module: ZK-SNARK Proving Systems - Non-Deterministic LR Division Gadget

Source of Truth: research/zk_snark_proving_systems_verifiable_forensic_computation_research.md
Non-Deterministic Likelihood Ratio Division: N_hat * 2^S = LR_hat * D_hat + r
with strict bounded inequalities: 0 <= r < D_hat <=> RangeCheck_S(r) and RangeCheck_S(D_hat - 1 - r).
"""

from typing import List, Tuple, Dict, Any, Optional
from ..finite_field import BN254_SCALAR_FIELD_R
from .range_check import R1CSConstraint, RangeCheckGadget


class NonDeterministicDivisionGadget:
    """
    Implements verifiable Likelihood Ratio division:
    N_hat * 2^S == LR_hat * D_hat + r
    with strictly enforced remainder bounds: 0 <= r < D_hat.
    """

    def __init__(
        self,
        scale_s: int = 16,
        max_bitwidth_b: int = 64,
        modulus: int = BN254_SCALAR_FIELD_R
    ):
        self.scale_s = scale_s
        self.scale_factor = 1 << scale_s
        self.max_bitwidth_b = max_bitwidth_b
        self.modulus = modulus
        self.rc_remainder = RangeCheckGadget(bitwidth=max_bitwidth_b, modulus=modulus)
        self.rc_slack = RangeCheckGadget(bitwidth=max_bitwidth_b, modulus=modulus)
        self.rc_quotient = RangeCheckGadget(bitwidth=max_bitwidth_b, modulus=modulus)

    def synthesize_witness(
        self, numerator_hat: int, denominator_hat: int, prefix: str = "div"
    ) -> Tuple[Dict[str, int], int, int]:
        """
        Computes non-deterministic quotient LR_hat and remainder r, synthesizing full R1CS witness.
        Enforces 0 <= r < denominator_hat.
        """
        if denominator_hat == 0:
            raise ZeroDivisionError("Division by zero in Likelihood Ratio circuit gadget")

        dividend = numerator_hat * self.scale_factor
        lr_hat = (dividend // denominator_hat) % self.modulus
        r = (dividend % denominator_hat) % self.modulus
        slack = (denominator_hat - 1 - r) % self.modulus

        if slack < 0:
            raise ValueError(f"Remainder violation: r={r} >= denominator={denominator_hat}")

        witness = {
            "ONE": 1,
            f"{prefix}_N": numerator_hat % self.modulus,
            f"{prefix}_D": denominator_hat % self.modulus,
            f"{prefix}_LR": lr_hat,
            f"{prefix}_r": r,
            f"{prefix}_slack": slack,
        }

        # Sub-witnesses for bit-decomposition range checks
        witness.update(self.rc_remainder.synthesize_witness(r, prefix=f"{prefix}_r_rc"))
        witness.update(self.rc_slack.synthesize_witness(slack, prefix=f"{prefix}_slack_rc"))
        witness.update(self.rc_quotient.synthesize_witness(lr_hat, prefix=f"{prefix}_lr_rc"))
        return witness, lr_hat, r

    def generate_constraints(self, prefix: str = "div") -> List[R1CSConstraint]:
        """Generates R1CS constraints for division equality and bounded inequalities."""
        constraints = []

        # 1. Main division relation: (LR_hat) * (D_hat) = (2^S * N_hat - r)
        # Re-arranged to R1CS format: (LR_hat) * (D_hat) = (scaled_N - r)
        # Or: (LR_hat) * (D_hat) + r = (N_hat * 2^S) => (LR_hat) * (D_hat) = (N_hat * 2^S - r)
        c_div = R1CSConstraint(
            a_terms={f"{prefix}_LR": 1},
            b_terms={f"{prefix}_D": 1},
            c_terms={f"{prefix}_N": self.scale_factor, f"{prefix}_r": -1 % self.modulus}
        )
        constraints.append(c_div)

        # 2. Slack equality constraint: (D_hat - 1 - r) * 1 == slack
        # (D_hat - r - 1) * ONE = slack => D_hat - r - ONE = slack
        c_slack = R1CSConstraint(
            a_terms={f"{prefix}_D": 1, f"{prefix}_r": -1 % self.modulus, "ONE": -1 % self.modulus},
            b_terms={"ONE": 1},
            c_terms={f"{prefix}_slack": 1}
        )
        constraints.append(c_slack)

        # 3. Range check on remainder r (0 <= r < 2^S)
        constraints.extend(self.rc_remainder.generate_constraints(f"{prefix}_r", prefix=f"{prefix}_r_rc"))

        # 4. Range check on slack (0 <= slack < 2^S => r <= D_hat - 1 < D_hat)
        constraints.extend(self.rc_slack.generate_constraints(f"{prefix}_slack", prefix=f"{prefix}_slack_rc"))

        # 5. Range check on quotient LR_hat (0 <= LR_hat < 2^B)
        constraints.extend(self.rc_quotient.generate_constraints(f"{prefix}_LR", prefix=f"{prefix}_lr_rc"))
        return constraints
