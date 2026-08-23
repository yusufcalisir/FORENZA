"""
FORENZA: Forensic Evidence Operating System
Module: ZK-SNARK Proving Systems - UltraPLONK & Plookup Table Lookup Engine

Source of Truth: research/zk_snark_proving_systems_verifiable_forensic_computation_research.md
Plookup Table Lookup Arguments for Non-Linear Log-Likelihood Tables (f(x) in T).
"""

from typing import List, Tuple, Dict, Any, Optional, Set
import math
from ..finite_field import BN254_SCALAR_FIELD_R
from ..fixed_point import FixedPointEngine


class PlookupTableEngine:
    """
    UltraPLONK / Plookup Table Engine.
    Precomputes static lookup table T = {(u, floor(log10(u) * 2^S))}
    and validates lookup multiset consistency arguments.
    """

    def __init__(
        self,
        table_size: int = 1024,
        scale_s: int = 16,
        modulus: int = BN254_SCALAR_FIELD_R
    ):
        self.table_size = table_size
        self.scale_s = scale_s
        self.scale_factor = 1 << scale_s
        self.modulus = modulus
        self.fp = FixedPointEngine(scale_s=scale_s, modulus=modulus)

        # Precompute table T for u in [1, table_size]
        # Maps integer index u -> (u, quantized_log10_u, quantized_ln_u)
        self.table_entries: Dict[int, Tuple[int, int]] = {}
        self.table_pairs: Set[Tuple[int, int]] = set()

        for u in range(1, table_size + 1):
            log10_val = math.log10(u)
            log10_hat = self.fp.quantize(log10_val)
            self.table_entries[u] = (u, log10_hat)
            self.table_pairs.add((u, log10_hat))

    def lookup(self, u: int) -> Tuple[int, int]:
        """Looks up (u, log10_hat) from table T."""
        if u not in self.table_entries:
            raise KeyError(f"Value {u} not found in precomputed Plookup table [1, {self.table_size}]")
        return self.table_entries[u]

    def verify_lookup_containment(self, input_pairs: List[Tuple[int, int]]) -> bool:
        """
        Verifies that every (x_i, y_i) in input_pairs belongs to precomputed table T.
        """
        for x, y in input_pairs:
            if (x, y) not in self.table_pairs:
                return False
        return True

    def compute_plookup_grand_product(
        self,
        query_pairs: List[Tuple[int, int]],
        gamma: int = 7,
        beta: int = 11
    ) -> int:
        """
        Simulates Plookup multiset Grand Product accumulator:
        Z = prod_{i} ( (1 + beta)*(gamma + x_i + beta*y_i) ) / ( ... )
        Returns evaluated accumulator modulo r.
        """
        r = self.modulus
        product = 1
        for x, y in query_pairs:
            compressed = (x + beta * y + gamma) % r
            product = (product * compressed) % r
        return product
