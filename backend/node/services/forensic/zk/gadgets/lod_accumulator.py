"""
FORENZA: Forensic Evidence Operating System
Module: ZK-SNARK Proving Systems - Multi-Locus Lod Score Accumulator

Source of Truth: research/zk_snark_proving_systems_verifiable_forensic_computation_research.md
Multi-Locus Autosomal 24-STR Lod Score Linear Invariant Accumulator: log10(LR_total) = sum(log10(LR_l)).
"""

from typing import List, Tuple, Dict, Any, Optional
from ..finite_field import BN254_SCALAR_FIELD_R
from ..fixed_point import FixedPointEngine
from .range_check import R1CSConstraint


class MultiLocusLodAccumulator:
    """
    Accumulates per-locus log-likelihood ratios over 24 forensic loci:
    log10_LR_total = sum(log10_LR_l)
    Enforces strict linear additivity invariant in circuit.
    """

    def __init__(
        self,
        scale_s: int = 16,
        locus_count: int = 24,
        modulus: int = BN254_SCALAR_FIELD_R
    ):
        self.scale_s = scale_s
        self.scale_factor = 1 << scale_s
        self.locus_count = locus_count
        self.modulus = modulus
        self.fp = FixedPointEngine(scale_s=scale_s, modulus=modulus)

    def synthesize_witness(
        self, locus_log10_lrs: Dict[str, float], prefix: str = "lod"
    ) -> Tuple[Dict[str, int], int, float]:
        """
        Synthesizes fixed-point witness for multi-locus log10 accumulation.
        Returns (witness_dict, total_quantized, total_continuous).
        """
        witness = {"ONE": 1}
        total_continuous = 0.0
        total_quantized = 0

        for locus_idx, (locus_name, log_val) in enumerate(locus_log10_lrs.items(), start=1):
            q_val = self.fp.quantize(log_val)
            witness[f"{prefix}_locus_{locus_idx}"] = q_val
            total_continuous += log_val
            total_quantized = (total_quantized + q_val) % self.modulus

        witness[f"{prefix}_total"] = total_quantized
        return witness, total_quantized, total_continuous

    def generate_constraints(
        self, locus_names: List[str], prefix: str = "lod"
    ) -> List[R1CSConstraint]:
        """
        Generates linear combination R1CS constraint:
        sum(locus_i) * 1 == lod_total
        """
        sum_terms = {f"{prefix}_locus_{i}": 1 for i in range(1, len(locus_names) + 1)}
        c_lod = R1CSConstraint(
            a_terms=sum_terms,
            b_terms={"ONE": 1},
            c_terms={f"{prefix}_total": 1}
        )
        return [c_lod]

    def verify_additivity_invariant(
        self, per_locus_logs: List[float], total_log: float, epsilon: float = 1e-5
    ) -> bool:
        """Verifies |total_log - sum(per_locus_logs)| < epsilon."""
        computed_sum = sum(per_locus_logs)
        return abs(computed_sum - total_log) < epsilon
