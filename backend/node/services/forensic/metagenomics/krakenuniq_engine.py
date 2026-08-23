"""
FORENZA — KrakenUniq HyperLogLog Cardinality & Horizontal Coverage Filter (Phase 1.3)
=======================================================================================

Implements the KrakenUniq orthogonal false-positive suppression filter using:
    1. 64-bit HyperLogLog cardinality estimator for unique k-mer counting
    2. Horizontal reference genome coverage computation
    3. Artifact rejection rule: k_uniq < 2,000 → flagged as spurious

Mathematical reference (Research §1.5 KrakenUniq & §1.7 Orthogonal Filtering):

    KrakenUniq extends Kraken 2 by tracking the NUMBER OF UNIQUE k-mers
    (not just total read counts) supporting each taxon.

    Filter criteria (Research §1.7):
        k_uniq ≥ 2,000 eliminates >99%% of false-positive bacterial assignments
        in low-biomass environmental metagenomes.

    A taxon supported by 1,000 reads mapping to only 2 unique k-mers is
    flagged as artifact, whereas true biological identification requires
    unique k-mers distributed evenly across the reference genome.

HyperLogLog Algorithm:
    The HLL cardinality estimator uses b precision bits and a hash function
    to maintain 2^b registers M[0..2^b-1].
    For each new k-mer hash h:
        j = h >> (64 - b)  (leading b bits → register index)
        w = h & ((1<<(64-b))-1)  (trailing bits)
        M[j] = max(M[j], clz(w) + 1)  (clz = count leading zeros)
    Cardinality estimate:
        E = α_m * m^2 * (Σ 2^(-M[j]))^(-1)
"""

from __future__ import annotations

import hashlib
import logging
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from .schemas import (
    ClassifierConfig,
    ClassifierEngine,
    KReportNode,
    MetagenomicRead,
    TaxonomicProfile,
    TaxonomicRank,
)
from .kraken2_engine import (
    KRAKEN2_K,
    KRAKEN2_M,
    TaxonomyTree,
    Kraken2Engine,
    extract_canonical_kmers,
    compute_minimizers,
    _rank_to_code,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# §1 HYPERLOGLOG CARDINALITY ESTIMATOR
# ═══════════════════════════════════════════════════════════════════════════════

# KrakenUniq artifact suppression threshold (Research §1.7)
KRAKENUNIQ_K_UNIQ_THRESHOLD: int = 2000


class HyperLogLog:
    """
    64-bit HyperLogLog cardinality estimator for unique k-mer counting.

    Used by KrakenUniq to count distinct k-mers per taxon, enabling
    the detection of taxonomic inflation artifacts.

    Parameters:
        b: Precision bits. Number of registers = 2^b.
           Higher b → more accurate but more memory.
           b=12 → 4096 registers, ~±1.6%% error.
           b=14 → 16384 registers, ~±0.81%% error.

    Algorithm:
        For each element x:
            h = hash64(x)
            j = h >> (64 - b)          → register index (leading b bits)
            w = h & mask(64 - b)       → trailing bits
            M[j] = max(M[j], clz(w)+1)  → store max run of leading zeros

        Cardinality:
            E = α_m * m^2 / Σ(2^{-M[j]})

        where α_m corrects for systematic bias:
            α_16 = 0.673, α_32 = 0.697, α_64 = 0.709, α_m>128 ≈ 0.7213/(1+1.079/m)
    """

    def __init__(self, b: int = 12) -> None:
        """
        Initialize HLL with b precision bits.

        Args:
            b: Precision (4 ≤ b ≤ 16). Default b=12 → 4096 registers.
        """
        if not (4 <= b <= 16):
            raise ValueError(f"HyperLogLog precision b must be 4 ≤ b ≤ 16, got {b}")
        self.b = b
        self.m = 1 << b  # number of registers = 2^b
        self._registers: List[int] = [0] * self.m
        self._alpha = self._compute_alpha(self.m)

    @staticmethod
    def _compute_alpha(m: int) -> float:
        """Compute the bias correction constant α_m."""
        if m == 16:
            return 0.673
        elif m == 32:
            return 0.697
        elif m == 64:
            return 0.709
        else:
            return 0.7213 / (1.0 + 1.079 / m)

    @staticmethod
    def _hash64(value: int) -> int:
        """64-bit MurmurHash-inspired integer hash for k-mer values."""
        # Avalanche mixing from finalizer of MurmurHash3
        x = value & 0xFFFFFFFFFFFFFFFF
        x = (x ^ (x >> 33)) & 0xFFFFFFFFFFFFFFFF
        x = (x * 0xFF51AFD7ED558CCD) & 0xFFFFFFFFFFFFFFFF
        x = (x ^ (x >> 33)) & 0xFFFFFFFFFFFFFFFF
        x = (x * 0xC4CEB9FE1A85EC53) & 0xFFFFFFFFFFFFFFFF
        x = (x ^ (x >> 33)) & 0xFFFFFFFFFFFFFFFF
        return x

    @staticmethod
    def _clz(w: int, width: int = 64) -> int:
        """
        Count leading zeros in a `width`-bit integer w.
        Returns width if w == 0.
        """
        if w == 0:
            return width
        count = 0
        mask = 1 << (width - 1)
        while count < width and not (w & mask):
            count += 1
            w <<= 1
        return count

    def add(self, kmer_hash) -> None:
        """
        Add a k-mer hash to the HLL estimator.

        Args:
            kmer_hash: 64-bit canonical k-mer hash integer OR bytes object.
                       If bytes, interpreted as little-endian unsigned integer.
        """
        if isinstance(kmer_hash, (bytes, bytearray)):
            kmer_hash = int.from_bytes(kmer_hash, byteorder="little", signed=False)
        h = self._hash64(kmer_hash)
        j = h >> (64 - self.b)          # leading b bits → register index
        w = h & ((1 << (64 - self.b)) - 1)  # trailing (64-b) bits
        rho = self._clz(w, 64 - self.b) + 1  # position of leftmost 1-bit + 1
        self._registers[j] = max(self._registers[j], rho)

    def estimate(self) -> int:
        """
        Estimate the cardinality (number of unique k-mers added).

        Returns:
            Integer cardinality estimate.
        """
        m = self.m
        raw = self._alpha * m * m / sum(2.0 ** (-reg) for reg in self._registers)

        # Small range correction: if E ≤ (5/2) * m and zeros present
        zero_count = self._registers.count(0)
        if raw <= (5.0 / 2.0) * m and zero_count > 0:
            raw = m * math.log(m / zero_count)  # LinearCounting

        # Large range correction
        elif raw > (2 ** 32) / 30.0:
            raw = -(2 ** 32) * math.log(1.0 - raw / (2 ** 32))

        return max(0, int(raw))

    def cardinality(self) -> int:
        """Alias for estimate() — returns the unique-element cardinality estimate."""
        return self.estimate()

    def merge(self, other: "HyperLogLog") -> None:
        """Merge another HLL estimator into this one (take register max)."""
        if self.b != other.b:
            raise ValueError(f"Cannot merge HLL with b={self.b} and b={other.b}")
        for i in range(self.m):
            self._registers[i] = max(self._registers[i], other._registers[i])


# ═══════════════════════════════════════════════════════════════════════════════
# §2 TAXON COVERAGE TRACKER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TaxonCoverageRecord:
    """
    Per-taxon coverage tracking for KrakenUniq.

    Tracks both total read count AND unique k-mer count (via HLL).
    The artifact detection logic compares these two metrics:
        - High reads + low k_uniq → artifact (same k-mer repeated)
        - High reads + high k_uniq → true biological signal (horizontal coverage)

    Horizontal coverage D_horiz = k_uniq / estimated_genome_kmer_count
    (simplified: k_uniq normalized by expected genome k-mer content)
    """
    taxid: int
    total_reads: int = 0
    direct_reads: int = 0
    hll: HyperLogLog = field(default_factory=lambda: HyperLogLog(b=12))
    k_uniq_estimate: int = 0   # updated from HLL after processing
    is_artifact_flagged: bool = False
    scientific_name: str = ""
    rank: TaxonomicRank = TaxonomicRank.UNCLASSIFIED


# ═══════════════════════════════════════════════════════════════════════════════
# §3 KRAKENUNIQ ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class KrakenUniqEngine:
    """
    Forensic KrakenUniq HyperLogLog Cardinality Filter Engine.

    Extends Kraken 2 classification with orthogonal false-positive suppression:
        1. Classify reads using Kraken 2 LCA (via Kraken2Engine delegation)
        2. For each classified read, extract canonical k-mers
        3. Add k-mer hashes to the per-taxon HyperLogLog estimator
        4. After processing all reads, estimate k_uniq per taxon
        5. Flag taxa where k_uniq < KRAKENUNIQ_K_UNIQ_THRESHOLD (= 2,000)

    Research §1.7 (KrakenUniq Orthogonal Filtering):
        "Filtering for k_uniq ≥ 2,000 eliminates greater than 99%% of
        false-positive bacterial assignments in low-biomass environmental
        metagenomes."
    """

    def __init__(
        self,
        taxonomy_tree: Optional[TaxonomyTree] = None,
        cht_lookup: Optional[Dict[int, int]] = None,
        config: Optional[ClassifierConfig] = None,
        k_uniq_threshold: int = KRAKENUNIQ_K_UNIQ_THRESHOLD,
    ) -> None:
        """
        Initialize the KrakenUniq engine.

        Args:
            taxonomy_tree: Taxonomy DAG for LCA operations.
            cht_lookup: CHT mapping minimizer_hash → taxid.
            config: ClassifierConfig (engine will be overridden to KRAKENUNIQ).
            k_uniq_threshold: Minimum unique k-mers for true biological signal.
                              Default 2,000 from Research §1.7.
        """
        # Override engine type to KRAKENUNIQ
        cfg = config or ClassifierConfig(engine=ClassifierEngine.KRAKENUNIQ)

        # Delegate k-mer classification to Kraken2Engine internals
        self._kraken2 = Kraken2Engine(
            taxonomy_tree=taxonomy_tree,
            cht_lookup=cht_lookup,
            config=cfg,
        )
        self.tree = self._kraken2.tree
        self.k_uniq_threshold = k_uniq_threshold
        self.config = cfg

        logger.info(
            f"[KrakenUniqEngine] Initialized with k_uniq_threshold={k_uniq_threshold}, "
            f"k={cfg.kmer_length}, m={cfg.minimizer_length}"
        )

    def _get_ancestor_taxids(self, taxid: int) -> List[int]:
        """Get all ancestors including self for coverage propagation."""
        return self.tree.get_ancestors(taxid)

    def classify_reads(
        self,
        reads: List[MetagenomicRead],
        sample_id: str = "UNKNOWN_SAMPLE",
        reference_db: str = "STANDARD",
    ) -> TaxonomicProfile:
        """
        Classify reads with HyperLogLog cardinality-based artifact suppression.

        Full KrakenUniq pipeline:
            1. For each read: Kraken 2 classification → taxid
            2. Extract canonical k-mers from the read
            3. Add k-mer hashes to HLL of assigned taxon AND all ancestors
            4. After all reads: estimate k_uniq per taxon via HLL.estimate()
            5. Flag taxa with k_uniq < 2,000
            6. Generate TaxonomicProfile with artifact flags in KReportNode

        Returns:
            TaxonomicProfile with k_uniq annotations and artifact flags.
        """
        import time
        t0 = time.perf_counter()

        k = self.config.kmer_length

        total = len(reads)
        classified = 0
        unclassified = 0
        coverage_records: Dict[int, TaxonCoverageRecord] = {}

        for read in reads:
            # Step 1: Classify with Kraken 2 LCA
            taxid, confidence = self._kraken2.classify_read(read)

            if taxid == 0:
                unclassified += 1
                continue

            classified += 1

            # Step 2: Extract canonical k-mers for this read
            kmer_hashes = extract_canonical_kmers(read.sequence, k=k)

            # Step 3: Add k-mer hashes to HLL for taxid and all ancestors
            ancestor_chain = self._get_ancestor_taxids(taxid)
            for ancestor_taxid in ancestor_chain:
                if ancestor_taxid not in coverage_records:
                    node = self.tree.get_node(ancestor_taxid)
                    coverage_records[ancestor_taxid] = TaxonCoverageRecord(
                        taxid=ancestor_taxid,
                        scientific_name=node.scientific_name if node else f"TaxID_{ancestor_taxid}",
                        rank=node.rank if node else TaxonomicRank.UNCLASSIFIED,
                    )
                rec = coverage_records[ancestor_taxid]
                rec.total_reads += 1
                for kh in kmer_hashes:
                    rec.hll.add(kh)

            # Direct read count only at assigned taxon
            if taxid in coverage_records:
                coverage_records[taxid].direct_reads += 1

        # Step 4 & 5: Estimate k_uniq and apply artifact flag
        kreport_nodes: List[KReportNode] = []
        abundance_vector: Dict[int, float] = {}

        for taxid, rec in sorted(coverage_records.items(), key=lambda x: -x[1].total_reads):
            rec.k_uniq_estimate = rec.hll.estimate()

            # Artifact rejection: k_uniq < 2,000 (Research §1.7)
            rec.is_artifact_flagged = rec.k_uniq_estimate < self.k_uniq_threshold

            pct = (rec.total_reads / total * 100.0) if total > 0 else 0.0
            node = self.tree.get_node(taxid)
            rank_code = _rank_to_code(rec.rank)

            kreport_nodes.append(KReportNode(
                pct_total=round(pct, 4),
                cumulative_reads=rec.total_reads,
                direct_reads=rec.direct_reads,
                rank_code=rank_code,
                taxid=taxid,
                name=rec.scientific_name,
                k_uniq=rec.k_uniq_estimate,
                is_artifact_flagged=rec.is_artifact_flagged,
            ))

            # Only include non-artifact taxa in abundance vector
            if not rec.is_artifact_flagged and rec.direct_reads > 0:
                abundance_vector[taxid] = rec.direct_reads

        # Normalize abundance vector to sum to 1.0
        total_abundance = sum(abundance_vector.values())
        if total_abundance > 0:
            abundance_vector = {
                tid: count / total_abundance
                for tid, count in abundance_vector.items()
            }

        artifact_count = sum(1 for rec in coverage_records.values() if rec.is_artifact_flagged)
        unclass_fraction = unclassified / total if total > 0 else 0.0

        profile = TaxonomicProfile(
            sample_id=sample_id,
            engine_used=ClassifierEngine.KRAKENUNIQ,
            reference_db=reference_db,
            total_reads=total,
            classified_reads=classified,
            unclassified_reads=unclassified,
            unclassified_fraction=round(unclass_fraction, 6),
            kreport_nodes=kreport_nodes,
            abundance_vector=abundance_vector,
            processing_time_seconds=round(time.perf_counter() - t0, 4),
            notes=(
                f"KrakenUniq: {artifact_count} taxa flagged as artifacts "
                f"(k_uniq < {self.k_uniq_threshold}). "
                f"Unclassified fraction: {unclass_fraction:.1%}."
            )
        )

        logger.info(
            f"[KrakenUniqEngine] Sample {sample_id}: "
            f"classified={classified}/{total}, "
            f"artifact_taxa_flagged={artifact_count}, "
            f"unclass_fraction={unclass_fraction:.3f}"
        )
        return profile

    def estimate_k_uniq(self, reads: List[MetagenomicRead], taxid: int) -> int:
        """
        Estimate unique k-mer cardinality for a specific taxon from a read list.

        This is a targeted k_uniq estimation for single-taxon artifact testing
        (used in edge-case EC-META-03).

        Args:
            reads: List of reads to extract k-mers from
            taxid: Target taxon TaxID

        Returns:
            Estimated number of unique k-mers (HyperLogLog estimate)
        """
        hll = HyperLogLog(b=12)
        k = self.config.kmer_length

        for read in reads:
            classified_taxid, _ = self._kraken2.classify_read(read)
            if classified_taxid == taxid or taxid in self.tree.get_ancestors(classified_taxid):
                for kh in extract_canonical_kmers(read.sequence, k=k):
                    hll.add(kh)

        return hll.estimate()

    def is_artifact(self, k_uniq_estimate: int) -> bool:
        """
        Evaluate whether a taxon's unique k-mer count is below the artifact threshold.

        Research §1.7:
            k_uniq ≥ 2,000 → true biological signal
            k_uniq < 2,000 → spurious artifact → FLAGGED

        Args:
            k_uniq_estimate: Estimated unique k-mer cardinality from HLL

        Returns:
            True if the taxon should be flagged as a spurious artifact
        """
        return k_uniq_estimate < self.k_uniq_threshold

    def apply_artifact_filter(
        self,
        nodes: "List[KReportNode]",
        min_k_uniq: int = 2000,
    ) -> "List[KReportNode]":
        """
        Apply the KrakenUniq k_uniq artifact filter to a list of KReportNode objects.

        Research §1.7:
            k_uniq < min_k_uniq (default 2,000) → spurious artifact → is_artifact_flagged = True
            k_uniq ≥ min_k_uniq                 → accepted as true biological signal

        Nodes without a k_uniq value (None) are accepted (no filter applied).

        Args:
            nodes: List of KReportNode objects to filter
            min_k_uniq: Minimum unique k-mer count threshold (Research default 2,000)

        Returns:
            Same list with is_artifact_flagged updated in-place.
        """
        result = []
        for node in nodes:
            if node.k_uniq is not None and node.k_uniq < min_k_uniq:
                # Create a flagged copy (KReportNode is a Pydantic model — use model_copy)
                flagged = node.model_copy(update={"is_artifact_flagged": True})
                result.append(flagged)
            else:
                result.append(node)
        return result
