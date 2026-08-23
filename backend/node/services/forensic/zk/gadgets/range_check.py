"""
FORENZA: Forensic Evidence Operating System
Module: ZK-SNARK Proving Systems - Strict Range Check Gadget

Source of Truth: research/zk_snark_proving_systems_verifiable_forensic_computation_research.md
Bit-Decomposition and Field Underflow / Wrap-Around Protection.
"""

from typing import List, Tuple, Dict, Any, Optional
from ..finite_field import BN254_SCALAR_FIELD_R, FieldElement


class R1CSConstraint:
    """Represents a Rank-1 constraint: (A . s) * (B . s) = (C . s) mod r."""

    def __init__(self, a_terms: Dict[str, int], b_terms: Dict[str, int], c_terms: Dict[str, int]):
        self.a_terms = a_terms  # signal_name -> coefficient
        self.b_terms = b_terms
        self.c_terms = c_terms

    def is_satisfied(self, witness: Dict[str, int], modulus: int = BN254_SCALAR_FIELD_R) -> bool:
        """Evaluates whether assignment satisfies the R1CS equation."""
        lhs_a = sum(coeff * witness.get(sig, 0) for sig, coeff in self.a_terms.items()) % modulus
        lhs_b = sum(coeff * witness.get(sig, 0) for sig, coeff in self.b_terms.items()) % modulus
        rhs_c = sum(coeff * witness.get(sig, 0) for sig, coeff in self.c_terms.items()) % modulus
        return (lhs_a * lhs_b) % modulus == rhs_c % modulus

    def __repr__(self) -> str:
        return f"R1CS({self.a_terms} * {self.b_terms} == {self.c_terms})"


class RangeCheckGadget:
    """
    Enforces strict bit-decomposition: sum(b_i * 2^i) = x with b_i * (1 - b_i) = 0.
    Guarantees x in [0, 2^bitwidth - 1].
    """

    def __init__(self, bitwidth: int, modulus: int = BN254_SCALAR_FIELD_R):
        if bitwidth < 1 or bitwidth > 252:
            raise ValueError(f"Invalid bitwidth {bitwidth}. Must be in [1, 252].")
        self.bitwidth = bitwidth
        self.modulus = modulus

    def synthesize_witness(self, value: int, prefix: str = "rc") -> Dict[str, int]:
        """
        Decomposes value into bits and returns witness signal dictionary.
        Raises ValueError if value exceeds [0, 2^bitwidth - 1].
        """
        if value < 0 or value >= (1 << self.bitwidth):
            raise ValueError(f"Value {value} out of range for bitwidth {self.bitwidth} [0, {(1 << self.bitwidth) - 1}]")

        witness = {"ONE": 1, prefix: value}
        for i in range(self.bitwidth):
            bit = (value >> i) & 1
            witness[f"{prefix}_b{i}"] = bit
        return witness

    def generate_constraints(self, signal_name: str, prefix: str = "rc") -> List[R1CSConstraint]:
        """Generates R1CS constraints for bit-decomposition and boolean checks."""
        constraints = []

        # 1. Boolean constraints: b_i * (1 - b_i) = 0 => b_i * b_i = b_i
        for i in range(self.bitwidth):
            bit_sig = f"{prefix}_b{i}"
            c = R1CSConstraint(
                a_terms={bit_sig: 1},
                b_terms={bit_sig: 1},
                c_terms={bit_sig: 1}
            )
            constraints.append(c)

        # 2. Linear sum constraint: sum(b_i * 2^i) * 1 = signal_name
        sum_terms = {f"{prefix}_b{i}": (1 << i) for i in range(self.bitwidth)}
        c_sum = R1CSConstraint(
            a_terms=sum_terms,
            b_terms={"ONE": 1},
            c_terms={signal_name: 1}
        )
        constraints.append(c_sum)
        return constraints

    def verify_assignment(self, value: int) -> bool:
        """Helper to verify if value conforms to the range bound."""
        return 0 <= value < (1 << self.bitwidth)
