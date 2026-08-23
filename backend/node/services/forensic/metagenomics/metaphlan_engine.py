"""
FORENZA — MetaPhlAn 4 Clade-Specific Marker Abundance Engine (Phase 2.1)
=========================================================================

Implements the MetaPhlAn 4 marker-gene abundance profiling workflow:
    1. Marker catalog index (GTDB SGBs >26,900 bins)
    2. Raw marker coverage: C_j = X_j / L_j
    3. Robust interquartile truncated mean: C_bar_i (discard top/bottom 10-20%)
    4. Relative abundance: A_i = C_bar_i / Σ C_bar_k × 100
    5. Simplex invariant: Σ A_i = 100.0%

Mathematical formulations (Research §1.2):
    C_j = X_j / L_j
    C_bar_i = (1/|M_i*|) Σ_{j∈M_i*} C_j   (interquartile subset M_i*)
    A_i = C_bar_i / Σ_k C_bar_k × 100       (such that Σ A_i = 100.0%)
"""

from __future__ import annotations

import logging
import math
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .schemas import (
    ClassifierConfig,
    ClassifierEngine,
    KReportNode,
    TaxonomicProfile,
    TaxonomicRank,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# §1 MARKER GENE DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MarkerGene:
    """
    Single clade-specific marker gene in the MetaPhlAn 4 catalog.

    Clade-specificity criteria (Research §1.2):
        - Ubiquity: present in ALL sequenced isolates of the target clade
        - Exclusivity: absent from ALL isolates OUTSIDE the target clade

    MetaPhlAn 4 catalog: >5.1 million unique genes across ~1 million microbial
    genomes (isolates + MAGs) covering >26,900 GTDB Species-level Genome Bins.
    """
    marker_id: str          # unique marker identifier (e.g., "UniRef90_A0A000_1")
    taxid: int              # NCBI TaxID of the target clade
    sgb_id: Optional[str]  # GTDB Species-level Genome Bin identifier
    length_bp: int          # marker gene length in base pairs (L_j)
    mapped_reads: int = 0   # X_j: reads aligning to this marker
    raw_coverage: float = 0.0  # C_j = X_j / L_j (computed)

    def compute_coverage(self) -> float:
        """
        Compute raw marker coverage C_j = X_j / L_j (Research §1.2).

        Raises:
            ZeroDivisionError: if length_bp == 0 (invalid marker)
        """
        if self.length_bp <= 0:
            raise ValueError(f"Marker {self.marker_id} has invalid length_bp={self.length_bp}")
        self.raw_coverage = self.mapped_reads / self.length_bp
        return self.raw_coverage


@dataclass
class CladeMarkerSet:
    """
    Collection of clade-specific markers for a single taxonomic clade.

    Used to compute the robust truncated mean coverage C_bar_i
    by trimming outlier markers (top/bottom 10–20% by coverage value).
    """
    taxid: int
    clade_name: str
    rank: TaxonomicRank
    sgb_id: Optional[str] = None
    markers: List[MarkerGene] = field(default_factory=list)

    def compute_truncated_mean_coverage(
        self,
        trim_fraction: float = 0.10
    ) -> float:
        """
        Compute the robust interquartile truncated mean coverage C_bar_i.

        Research §1.2 formulation:
            C_bar_i = (1/|M_i*|) Σ_{j∈M_i*} C_j
        where M_i* is the interquartile subset after discarding top and
        bottom trim_fraction (default 10%) of markers by coverage.

        Args:
            trim_fraction: Fraction of markers to discard from each tail.
                           Must be in [0, 0.5). Default 0.10 (10%).

        Returns:
            Truncated mean coverage C_bar_i. Returns 0.0 if no markers.
        """
        if not self.markers:
            return 0.0

        coverages = [m.raw_coverage for m in self.markers if m.raw_coverage >= 0]
        if not coverages:
            return 0.0

        n = len(coverages)
        if n == 1:
            return coverages[0]

        coverages_sorted = sorted(coverages)
        n_trim = max(0, int(math.floor(n * trim_fraction)))

        # Interquartile subset M_i*: discard bottom n_trim and top n_trim
        trimmed = coverages_sorted[n_trim: n - n_trim] if n > 2 * n_trim else coverages_sorted

        if not trimmed:
            return 0.0

        return sum(trimmed) / len(trimmed)


# ═══════════════════════════════════════════════════════════════════════════════
# §2 METAPHLAN 4 ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class MetaPhlAn4Engine:
    """
    FORENZA MetaPhlAn 4 Clade-Specific Marker Abundance Engine.

    Implements the full MetaPhlAn 4 analytical workflow (Research §1.2):

        Step 1: Map reads to marker catalog (Bowtie2 / simulated mapping)
        Step 2: C_j = X_j / L_j  (raw marker coverage per gene)
        Step 3: C_bar_i = truncated IQR mean (discard top/bottom 10–20%)
        Step 4: A_i = C_bar_i / Σ_k C_bar_k × 100
                enforcing simplex invariant: Σ A_i = 100.0%

    Key distinction from Kraken 2 (Research §1.3 Comparative Matrix):
        MetaPhlAn is preferred for:
            - Community composition profiling in well-characterized systems
            - Genome-size-bias normalization via marker length
            - Species/Strain resolution via GTDB SGB markers
        Kraken 2 is preferred for:
            - Trace forensic detection
            - Low-biomass samples (every read queried)
            - Viral pathogen identification

    Simplex invariant (AGENTS.md constraint):
        |Σ A_i - 100.0| ≤ 1e-5 must hold at all taxonomic levels.
    """

    def __init__(
        self,
        marker_catalog: Optional[Dict[int, CladeMarkerSet]] = None,
        config: Optional[ClassifierConfig] = None,
        trim_fraction: float = 0.10,
    ) -> None:
        """
        Initialize MetaPhlAn 4 engine.

        Args:
            marker_catalog: Dict mapping taxid → CladeMarkerSet.
                            In production, this is loaded from the ~15 GB Bowtie2 index.
            config: ClassifierConfig (engine forced to METAPHLAN4).
            trim_fraction: IQR trimming fraction (default 0.10 = 10%).
        """
        self.marker_catalog: Dict[int, CladeMarkerSet] = marker_catalog or {}
        self.config = config or ClassifierConfig(engine=ClassifierEngine.METAPHLAN4)
        self.trim_fraction = trim_fraction

        logger.info(
            f"[MetaPhlAn4Engine] Initialized with {len(self.marker_catalog)} clade marker sets, "
            f"trim_fraction={trim_fraction}"
        )

    def register_clade(self, clade: CladeMarkerSet) -> None:
        """Register or update a clade marker set in the catalog."""
        self.marker_catalog[clade.taxid] = clade

    def ingest_mapping_results(
        self,
        mapping_results: Dict[str, int]
    ) -> None:
        """
        Ingest Bowtie2 read-to-marker mapping results.

        Args:
            mapping_results: Dict mapping marker_id → read_count (X_j).
                             Simulates output of Bowtie2 alignment to marker index.
        """
        # Update mapped_reads and compute raw coverage for each hit marker
        for marker_id, read_count in mapping_results.items():
            for taxid, clade in self.marker_catalog.items():
                for marker in clade.markers:
                    if marker.marker_id == marker_id:
                        marker.mapped_reads = read_count
                        marker.compute_coverage()
                        break

    def compute_abundance_profile(
        self,
        total_reads: int,
        sample_id: str = "UNKNOWN_SAMPLE",
        reference_db: str = "GTDB_R220",
    ) -> TaxonomicProfile:
        """
        Compute relative taxonomic abundance profile.

        Full MetaPhlAn 4 pipeline (Research §1.2):
            1. For each detected clade i: compute C_bar_i (truncated mean)
            2. Normalize: A_i = C_bar_i / Σ_k C_bar_k × 100
            3. Validate simplex invariant: |Σ A_i - 100.0| ≤ 1e-5

        Research note (§1.2): MetaPhlAn excludes reads mapping to non-marker
        regions (>95% of environmental shotgun reads). Only the marker-aligning
        reads contribute to abundance estimates.

        Args:
            total_reads: Total input reads in the sample (for F_unclass computation)
            sample_id: Sample identifier
            reference_db: Reference database (default GTDB_R220)

        Returns:
            TaxonomicProfile with normalized abundance vector.

        Raises:
            ValueError: If simplex invariant |Σ A_i - 100.0| > 1e-5 after normalization.
        """
        import time
        t0 = time.perf_counter()

        # Step 2: Compute robust truncated mean coverage for each clade
        clade_coverages: Dict[int, float] = {}
        for taxid, clade in self.marker_catalog.items():
            # First compute raw coverage for all markers
            for marker in clade.markers:
                if marker.mapped_reads > 0 and marker.raw_coverage == 0.0:
                    marker.compute_coverage()

            c_bar = clade.compute_truncated_mean_coverage(self.trim_fraction)
            if c_bar > 0.0:  # only include detected clades
                clade_coverages[taxid] = c_bar

        if not clade_coverages:
            # No markers detected → all reads unclassified
            return TaxonomicProfile(
                sample_id=sample_id,
                engine_used=ClassifierEngine.METAPHLAN4,
                reference_db=reference_db,
                total_reads=total_reads,
                classified_reads=0,
                unclassified_reads=total_reads,
                unclassified_fraction=1.0,
                kreport_nodes=[],
                abundance_vector={},
                processing_time_seconds=round(time.perf_counter() - t0, 4),
                notes="MetaPhlAn 4: No marker alignments detected. All reads unclassified."
            )

        # Step 3: Normalize to relative abundance (Σ A_i = 100.0%)
        sum_coverages = sum(clade_coverages.values())
        abundance_pct: Dict[int, float] = {}
        for taxid, c_bar in clade_coverages.items():
            abundance_pct[taxid] = (c_bar / sum_coverages) * 100.0

        # Simplex invariant check: |Σ A_i - 100.0| ≤ 1e-5 (AGENTS.md constraint)
        sigma = sum(abundance_pct.values())
        if abs(sigma - 100.0) > 1e-5:
            raise ValueError(
                f"MetaPhlAn 4 simplex invariant VIOLATED: |Σ A_i - 100.0| = "
                f"{abs(sigma - 100.0):.2e} > 1e-5. "
                f"This indicates a normalization error in the abundance computation."
            )

        # Estimate classified reads from marker-hit fraction
        # MetaPhlAn uses <5% of total reads for markers (Research §1.2)
        total_marker_reads = sum(
            sum(m.mapped_reads for m in clade.markers)
            for clade in self.marker_catalog.values()
        )
        classified_reads = min(total_marker_reads, total_reads)
        unclassified_reads = total_reads - classified_reads
        unclass_fraction = unclassified_reads / total_reads if total_reads > 0 else 0.0

        # Build .kreport nodes
        kreport_nodes: List[KReportNode] = []
        for taxid, pct in sorted(abundance_pct.items(), key=lambda x: -x[1]):
            clade = self.marker_catalog.get(taxid)
            rank_code = _metaphlan_rank_code(clade.rank if clade else TaxonomicRank.SPECIES)
            kreport_nodes.append(KReportNode(
                pct_total=round(pct, 4),
                cumulative_reads=int(classified_reads * pct / 100.0),
                direct_reads=int(classified_reads * pct / 100.0),
                rank_code=rank_code,
                taxid=taxid,
                name=(
                    clade.clade_name if clade
                    else f"TaxID_{taxid}"
                ),
            ))

        # Convert abundance from pct to fraction for compatibility
        abundance_fraction: Dict[int, float] = {
            taxid: pct / 100.0 for taxid, pct in abundance_pct.items()
        }

        profile = TaxonomicProfile(
            sample_id=sample_id,
            engine_used=ClassifierEngine.METAPHLAN4,
            reference_db=reference_db,
            total_reads=total_reads,
            classified_reads=classified_reads,
            unclassified_reads=unclassified_reads,
            unclassified_fraction=round(unclass_fraction, 6),
            kreport_nodes=kreport_nodes,
            abundance_vector=abundance_fraction,
            processing_time_seconds=round(time.perf_counter() - t0, 4),
            notes=(
                f"MetaPhlAn 4: {len(abundance_pct)} clades detected. "
                f"Σ A_i = {sigma:.6f}%% (simplex invariant satisfied: "
                f"|Σ - 100.0| = {abs(sigma - 100.0):.2e} ≤ 1e-5). "
                f"Note: MetaPhlAn uses <5%% of total reads (marker-only alignment). "
                f"High unclassified fraction ({unclass_fraction:.1%}) is expected for "
                f"environmental / soil samples."
            )
        )

        logger.info(
            f"[MetaPhlAn4Engine] {sample_id}: {len(abundance_pct)} clades, "
            f"Σ A_i={sigma:.4f}%%"
        )
        return profile


def _metaphlan_rank_code(rank: TaxonomicRank) -> str:
    """Map TaxonomicRank to MetaPhlAn 4 / kreport rank code."""
    mapping = {
        TaxonomicRank.DOMAIN: "D",
        TaxonomicRank.PHYLUM: "P",
        TaxonomicRank.CLASS: "C",
        TaxonomicRank.ORDER: "O",
        TaxonomicRank.FAMILY: "F",
        TaxonomicRank.GENUS: "G",
        TaxonomicRank.SPECIES: "S",
        TaxonomicRank.STRAIN: "t",   # MetaPhlAn uses 't' for strain
        TaxonomicRank.SGB: "SGB",
    }
    return mapping.get(rank, "S")
