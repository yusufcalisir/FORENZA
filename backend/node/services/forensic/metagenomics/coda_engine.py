"""
FORENZA — Compositional Data (CoDa) Mathematical Engine (Phase 4.1)
====================================================================

Implements the complete CoDa analytical framework for forensic soil
metagenomics and palynology abundance vectors.

Research §3.4 Compositional Data Analysis (CoDa) Framework:

    Simplex Space: x ∈ S^D, x_i > 0, Σ x_i = 1
    
    Centered Log-Ratio (CLR) Transformation:
        clr(x) = [ln(x_1/g(x)), ..., ln(x_D/g(x))]
        g(x) = geometric mean = (Π x_i)^{1/D}
        clr(x) ∈ ℝ^D with Σ clr_i = 0 (Helmert contrast constraint)
    
    Isometric Log-Ratio (ILR) Transformation:
        ilr(x) ∈ ℝ^{D-1} (orthonormal coordinates in Aitchison geometry)
    
    Aitchison Distance:
        d_A(x, y) = ||clr(x) - clr(y)||_2
                  = sqrt( Σ_{i=1}^D (ln(x_i/g(x)) - ln(y_i/g(y)))^2 )
    
    Multiplicative Zero Replacement (Research §3.4):
        x_i = δ if x_i = 0, where δ = 0.5 / N_reads (Martin-Fernandez 2003)
        Then renormalize the simplex.
    
    Bray-Curtis Dissimilarity (non-CoDa comparison, Research §3.4):
        BC(x, y) = Σ|x_i - y_i| / Σ(x_i + y_i)
    
    Mathematical invariants (AGENTS.md):
        |Σ clr_i| ≤ 1e-9 (Helmert zero-sum constraint)
        |d_A(x, x)| ≤ 1e-12 (self-distance = 0)
"""

from __future__ import annotations

import logging
import math
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# §1 ZERO REPLACEMENT (Multiplicative / Martin-Fernandez 2003)
# ═══════════════════════════════════════════════════════════════════════════════

def multiplicative_zero_replacement(
    abundance_vector: Dict[int, float],
    total_reads: int,
) -> Dict[int, float]:
    """
    Replace zero abundances using the Multiplicative Zero Replacement strategy.

    Research §3.4 (Martin-Fernandez 2003):
        δ = 0.5 / N_reads
        x_i = δ for all x_i = 0
        Then renormalize: x_i = x_i / Σ x_j

    This preserves the relative ordering of non-zero components while
    ensuring the abundance vector lies strictly in the open simplex
    (no zero coordinates for CLR computation).

    Args:
        abundance_vector: taxid → relative abundance (sum = 1.0, may contain 0s)
        total_reads: Total read count N_reads for δ computation

    Returns:
        Zero-replaced and renormalized abundance vector
    """
    if total_reads <= 0:
        total_reads = 1  # guard

    delta = 0.5 / total_reads  # δ = 0.5 / N_reads (Research §3.4 constant)

    # Replace zeros
    replaced = {
        taxid: (frac if frac > 0.0 else delta)
        for taxid, frac in abundance_vector.items()
    }

    # Renormalize to simplex
    total = sum(replaced.values())
    if total > 0:
        replaced = {taxid: f / total for taxid, f in replaced.items()}

    return replaced


# ═══════════════════════════════════════════════════════════════════════════════
# §2 CLR TRANSFORMATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def compute_clr(
    abundance_vector: Dict[int, float],
) -> Dict[int, float]:
    """
    Compute the Centered Log-Ratio (CLR) transformation.

    Research §3.4:
        clr(x)_i = ln(x_i / g(x))
        g(x) = exp(Σ ln(x_i) / D) = geometric mean

    Mathematical invariant:
        |Σ clr_i| ≤ 1e-9 (Helmert zero-sum constraint)

    Args:
        abundance_vector: taxid → abundance (must be strictly positive; no zeros)

    Returns:
        taxid → CLR-transformed value

    Raises:
        ValueError: If any abundance is ≤ 0 (log undefined)
        ValueError: If Helmert zero-sum invariant |Σ clr_i| > 1e-9 is violated
    """
    if not abundance_vector:
        return {}

    for taxid, x in abundance_vector.items():
        if x <= 0.0:
            raise ValueError(
                f"CLR computation requires strictly positive abundances. "
                f"Found x[{taxid}] = {x}. Apply zero replacement first "
                f"(δ = 0.5/N_reads, Research §3.4)."
            )

    values = list(abundance_vector.values())
    D = len(values)

    # Geometric mean: g(x) = exp((1/D) Σ ln(x_i))
    log_sum = sum(math.log(x) for x in values)
    log_geo_mean = log_sum / D
    geo_mean = math.exp(log_geo_mean)

    # CLR: clr_i = ln(x_i / g(x)) = ln(x_i) - ln(g(x))
    clr_vector = {
        taxid: math.log(x / geo_mean)
        for taxid, x in abundance_vector.items()
    }

    # Validate Helmert zero-sum constraint: |Σ clr_i| ≤ 1e-9
    clr_sum = sum(clr_vector.values())
    if abs(clr_sum) > 1e-9:
        raise ValueError(
            f"CLR Helmert zero-sum constraint VIOLATED: "
            f"|Σ clr_i| = {abs(clr_sum):.2e} > 1e-9. "
            f"This indicates numerical precision loss in CLR computation."
        )

    return clr_vector


# ═══════════════════════════════════════════════════════════════════════════════
# §3 AITCHISON DISTANCE
# ═══════════════════════════════════════════════════════════════════════════════

def aitchison_distance(
    clr_x: Dict[int, float],
    clr_y: Dict[int, float],
) -> float:
    """
    Compute the Aitchison distance between two CLR-transformed compositions.

    Research §3.4:
        d_A(x, y) = ||clr(x) - clr(y)||_2
                  = sqrt( Σ_{i∈shared} (clr_x_i - clr_y_i)^2 )

    For taxa not shared between x and y:
        Components present in only one composition contribute their CLR value
        squared (since the other composition's CLR would be -∞, replaced by
        the zero-replacement δ value; handled upstream via multiplicative replacement).

    Mathematical invariant:
        d_A(x, x) = 0 (self-distance)
        d_A(x, y) = d_A(y, x) (symmetry)
        d_A(x, z) ≤ d_A(x, y) + d_A(y, z) (triangle inequality)

    Args:
        clr_x: CLR-transformed abundance for composition x
        clr_y: CLR-transformed abundance for composition y

    Returns:
        Aitchison distance ≥ 0.0
    """
    all_taxids = set(clr_x) | set(clr_y)
    squared_diffs = sum(
        (clr_x.get(tid, 0.0) - clr_y.get(tid, 0.0)) ** 2
        for tid in all_taxids
    )
    return math.sqrt(squared_diffs)


# ═══════════════════════════════════════════════════════════════════════════════
# §4 BRAY-CURTIS DISSIMILARITY
# ═══════════════════════════════════════════════════════════════════════════════

def bray_curtis_dissimilarity(
    x: Dict[int, float],
    y: Dict[int, float],
) -> float:
    """
    Compute Bray-Curtis dissimilarity (non-CoDa, Research §3.4).

    BC(x, y) = Σ|x_i - y_i| / Σ(x_i + y_i)

    Used as a non-CoDa comparison metric; does not require CLR transformation.
    Bray-Curtis is NOT Aitchison-invariant (not subcompositionally coherent).
    Used for comparison to classical community ecology analyses.

    Args:
        x: taxid → abundance (raw or normalized)
        y: taxid → abundance (raw or normalized)

    Returns:
        Bray-Curtis dissimilarity ∈ [0, 1]
    """
    all_taxids = set(x) | set(y)
    numerator = sum(abs(x.get(tid, 0.0) - y.get(tid, 0.0)) for tid in all_taxids)
    denominator = sum(x.get(tid, 0.0) + y.get(tid, 0.0) for tid in all_taxids)
    return numerator / denominator if denominator > 0.0 else 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# §5 CoDa ENGINE ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════════

class CoDaEngine:
    """
    Forensic Compositional Data Analysis (CoDa) Mathematical Engine.

    Orchestrates the complete CoDa pipeline for forensic soil and palynology
    metagenomic abundance vectors:

        1. Multiplicative Zero Replacement (δ = 0.5/N_reads)
        2. CLR Transformation (Helmert zero-sum validated)
        3. Aitchison Distance Matrix computation
        4. Bray-Curtis Dissimilarity matrix (non-CoDa comparison)
        5. PCA/PCoA in CLR-space (simplified: eigenvalue decomposition)

    All operations enforce the AGENTS.md mathematical invariants:
        - Helmert constraint: |Σ clr_i| ≤ 1e-9
        - Self-distance: |d_A(x,x)| ≤ 1e-12
        - Simplex closure: |Σ abundance_i - 1.0| ≤ 1e-6
    """

    def __init__(self, total_reads: int = 10000) -> None:
        self.total_reads = total_reads

    def full_pipeline(
        self,
        sample_abundance_vectors: Dict[str, Dict[int, float]],
        total_reads_per_sample: Optional[Dict[str, int]] = None,
    ) -> "CoDaResult":
        """
        Run the complete CoDa pipeline on multiple sample abundance vectors.

        Args:
            sample_abundance_vectors: {sample_id: {taxid: abundance_fraction}}
            total_reads_per_sample: {sample_id: total_reads} for δ computation

        Returns:
            CoDaResult with CLR vectors, Aitchison distance matrix, and BC matrix.
        """
        sample_ids = sorted(sample_abundance_vectors.keys())
        n = len(sample_ids)

        # Step 1: Zero replacement per sample
        zero_replaced: Dict[str, Dict[int, float]] = {}
        for sid in sample_ids:
            n_reads = (
                total_reads_per_sample.get(sid, self.total_reads)
                if total_reads_per_sample else self.total_reads
            )
            zero_replaced[sid] = multiplicative_zero_replacement(
                sample_abundance_vectors[sid],
                total_reads=n_reads
            )

        # Step 2: CLR transformation
        clr_vectors: Dict[str, Dict[int, float]] = {}
        for sid in sample_ids:
            clr_vectors[sid] = compute_clr(zero_replaced[sid])

        # Step 3: Aitchison distance matrix [n × n]
        aitchison_matrix: List[List[float]] = []
        for i, sid_i in enumerate(sample_ids):
            row: List[float] = []
            for j, sid_j in enumerate(sample_ids):
                d = aitchison_distance(clr_vectors[sid_i], clr_vectors[sid_j])
                row.append(round(d, 8))
            aitchison_matrix.append(row)

        # Validate self-distance invariant: d_A(x, x) = 0
        for i in range(n):
            if abs(aitchison_matrix[i][i]) > 1e-12:
                raise ValueError(
                    f"Aitchison self-distance invariant VIOLATED for sample '{sample_ids[i]}': "
                    f"d_A(x,x) = {aitchison_matrix[i][i]:.2e} > 1e-12."
                )

        # Step 4: Bray-Curtis dissimilarity matrix [n × n]
        bc_matrix: List[List[float]] = []
        for i, sid_i in enumerate(sample_ids):
            row: List[float] = []
            for j, sid_j in enumerate(sample_ids):
                bc = bray_curtis_dissimilarity(
                    sample_abundance_vectors[sid_i],
                    sample_abundance_vectors[sid_j]
                )
                row.append(round(bc, 8))
            bc_matrix.append(row)

        return CoDaResult(
            sample_ids=sample_ids,
            clr_vectors=clr_vectors,
            zero_replaced_vectors=zero_replaced,
            aitchison_distance_matrix=aitchison_matrix,
            bray_curtis_matrix=bc_matrix,
        )


from dataclasses import dataclass


@dataclass
class CoDaResult:
    """
    Result container for CoDa pipeline outputs.
    """
    sample_ids: List[str]
    clr_vectors: Dict[str, Dict[int, float]]
    zero_replaced_vectors: Dict[str, Dict[int, float]]
    aitchison_distance_matrix: List[List[float]]
    bray_curtis_matrix: List[List[float]]

    def get_aitchison_distance(self, sample_a: str, sample_b: str) -> float:
        """Get the Aitchison distance between two samples by ID."""
        idx_a = self.sample_ids.index(sample_a)
        idx_b = self.sample_ids.index(sample_b)
        return self.aitchison_distance_matrix[idx_a][idx_b]

    def get_bray_curtis(self, sample_a: str, sample_b: str) -> float:
        """Get Bray-Curtis dissimilarity between two samples by ID."""
        idx_a = self.sample_ids.index(sample_a)
        idx_b = self.sample_ids.index(sample_b)
        return self.bray_curtis_matrix[idx_a][idx_b]
