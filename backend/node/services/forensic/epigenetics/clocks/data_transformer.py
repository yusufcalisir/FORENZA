"""
FORENZA Epigenetic Data Transformer & Quality Control Engine (Pillar 4 §5).

Provides bijective beta/M-value transformations, targeted bisulfite MPS read-depth
quantification, bisulfite conversion efficiency validation, and quality-controlled imputation.
"""

import math
from typing import Dict, Optional, Tuple, Any, List
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    MethylationSample,
    EpigeneticPlatform,
)
from backend.node.services.forensic.epigenetics.clocks.clock_registry import (
    MASTER_CPG_REGISTRY,
    EpigeneticClockRegistry,
)


class EpigeneticDataTransformer:
    """Mathematical engine for DNA methylation transformations and QC."""

    EPSILON: float = 1e-6
    OFFSET_ALPHA: float = 100.0
    MIN_BISULFITE_EFFICIENCY: float = 0.985
    MAX_DETECTION_P_VALUE: float = 0.01
    MIN_MPS_READ_DEPTH: int = 20

    @classmethod
    def beta_to_m_value(cls, beta: float) -> float:
        """
        Transform a DNA methylation beta-value in [0.0, 1.0] to an M-value:
        M = log2(beta / (1 - beta)).
        """
        clamped_beta = max(cls.EPSILON, min(1.0 - cls.EPSILON, beta))
        return math.log2(clamped_beta / (1.0 - clamped_beta))

    @classmethod
    def m_to_beta_value(cls, m_val: float) -> float:
        """
        Analytically invert an M-value back to a DNA methylation beta-value:
        beta = 2^M / (1 + 2^M).
        """
        try:
            exp_val = math.pow(2.0, m_val)
            return exp_val / (1.0 + exp_val)
        except OverflowError:
            return 1.0 if m_val > 0 else 0.0

    @classmethod
    def intensities_to_beta(cls, m_intensity: float, u_intensity: float, alpha: float = 100.0) -> float:
        """
        Calculate beta-value from raw array fluorescent intensities:
        beta = M / (M + U + alpha).
        """
        denom = m_intensity + u_intensity + alpha
        if denom <= 0.0:
            return 0.0
        return max(0.0, min(1.0, m_intensity / denom))

    @classmethod
    def read_counts_to_beta(cls, c_reads: int, t_reads: int) -> Tuple[float, int, bool]:
        """
        Calculate beta-value from targeted bisulfite MPS read counts:
        beta = C / (C + T).
        Returns: (beta, total_depth, is_valid_depth).
        """
        depth = c_reads + t_reads
        if depth == 0:
            return 0.0, 0, False
        beta = float(c_reads) / float(depth)
        is_valid = depth >= cls.MIN_MPS_READ_DEPTH
        return max(0.0, min(1.0, beta)), depth, is_valid

    @classmethod
    def process_and_qc_sample(
        cls,
        sample: MethylationSample,
        required_probes: Optional[set] = None,
        auto_impute: bool = True
    ) -> Tuple[Dict[str, float], Dict[str, Any]]:
        """
        Validate QC parameters (bisulfite conversion, p-values), normalize inputs,
        and optionally impute missing required loci using population references.
        """
        qc_meta: Dict[str, Any] = {
            "bisulfite_pass": sample.bisulfite_conversion_efficiency >= cls.MIN_BISULFITE_EFFICIENCY,
            "bisulfite_efficiency": sample.bisulfite_conversion_efficiency,
            "masked_p_value_count": 0,
            "imputed_probes": [],
            "low_depth_probes": [],
        }

        if not qc_meta["bisulfite_pass"]:
            qc_meta["warning"] = (
                f"Bisulfite conversion efficiency ({sample.bisulfite_conversion_efficiency:.3f}) "
                f"is below mandatory ISO 17025 threshold ({cls.MIN_BISULFITE_EFFICIENCY})."
            )

        processed_betas: Dict[str, float] = {}

        # 1. Ingest from direct beta values if present
        for pid, bval in sample.beta_values.items():
            # Check detection p-value if provided
            if sample.detection_p_values and pid in sample.detection_p_values:
                if sample.detection_p_values[pid] > cls.MAX_DETECTION_P_VALUE:
                    qc_meta["masked_p_value_count"] += 1
                    continue  # Mask noisy probe
            processed_betas[pid] = max(0.0, min(1.0, float(bval)))

        # 2. Ingest from read counts if MPS and not already populated
        if sample.read_counts_c and sample.read_counts_t:
            for pid, c_cnt in sample.read_counts_c.items():
                if pid not in processed_betas and pid in sample.read_counts_t:
                    t_cnt = sample.read_counts_t[pid]
                    beta, depth, valid = cls.read_counts_to_beta(c_cnt, t_cnt)
                    if not valid:
                        qc_meta["low_depth_probes"].append({"probe_id": pid, "depth": depth})
                    processed_betas[pid] = beta

        # 3. Ingest from M-values if provided and beta is absent
        if sample.m_values:
            for pid, mval in sample.m_values.items():
                if pid not in processed_betas:
                    processed_betas[pid] = cls.m_to_beta_value(mval)

        # 4. Impute missing required probes if requested
        if auto_impute and required_probes:
            for req_pid in required_probes:
                if req_pid not in processed_betas:
                    rec = MASTER_CPG_REGISTRY.get(req_pid)
                    fallback_beta = rec.mean_reference_beta if rec else 0.50
                    processed_betas[req_pid] = fallback_beta
                    qc_meta["imputed_probes"].append(req_pid)

        return processed_betas, qc_meta
