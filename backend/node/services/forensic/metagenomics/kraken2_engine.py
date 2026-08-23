"""
FORENZA — Kraken 2 Minimizer k-mer Classification Engine (Phase 1.2)
=====================================================================

Implements the core Kraken 2 bioinformatic classification algorithm using:
    1. Canonical k-mer extraction (k=35, 2-bit encoding)
    2. Minimizer spaced-seed calculation (m=31, window size = k-m+1 = 5)
    3. Weighted Lowest Common Ancestor (LCA) path traversal
    4. Confidence threshold filtering

All constants are exact research specification values (Section 1.1):
    k = 35        (canonical k-mer length)
    m = 31        (minimizer length)
    A = 00        (2-bit encoding)
    C = 01
    G = 10
    T = 11
    Window = k - m + 1 = 5

Mathematical formulations (Research §1.1):
    Minimizer(W_k) = min_{0≤j≤k-m}{ hash(m-mer_j) }
    Score(Path_p) = Σ_{v∈Path_p} Weight(v)
    Classification condition: k_path(T) / k_total ≥ C
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from .schemas import (
    ClassifierConfig,
    ClassifierEngine,
    KmerHashEntry,
    KReportNode,
    MetagenomicRead,
    TaxonNode,
    TaxonomicProfile,
    TaxonomicRank,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# §1 NUCLEOTIDE ENCODING CONSTANTS (Research §1.1)
# ═══════════════════════════════════════════════════════════════════════════════

_NUC_2BIT: Dict[str, int] = {
    "A": 0b00,  # 00
    "C": 0b01,  # 01
    "G": 0b10,  # 10
    "T": 0b11,  # 11
}

_COMPLEMENT_2BIT: Dict[int, int] = {
    0b00: 0b11,  # A ↔ T
    0b01: 0b10,  # C ↔ G
    0b10: 0b01,  # G ↔ C
    0b11: 0b00,  # T ↔ A
}

# Kraken 2 research parameters (exact constants — no arbitrary values)
KRAKEN2_K: int = 35   # k-mer length
KRAKEN2_M: int = 31   # minimizer length
KRAKEN2_WINDOW: int = KRAKEN2_K - KRAKEN2_M + 1  # = 5


# ═══════════════════════════════════════════════════════════════════════════════
# §2 TAXONOMY NODE STORE (In-memory lightweight LCA structure)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LCANode:
    """
    Lightweight in-memory node for the LCA taxonomy DAG.

    During Kraken 2 classification, every taxon in the database is stored
    as an LCANode with its parent reference, enabling O(depth) LCA lookups.
    """
    taxid: int
    parent_taxid: Optional[int]
    rank: TaxonomicRank
    scientific_name: str
    weight: int = 0              # minimizers mapped to this node or descendants
    children: List[int] = field(default_factory=list)


class TaxonomyTree:
    """
    Rooted taxonomy DAG for Kraken 2 LCA traversal.

    Supports:
        - Node registration from NCBI taxonomy dump
        - LCA(a, b) computation in O(depth)
        - Root-to-leaf path scoring
        - Ancestor chain retrieval for confidence threshold filtering

    NCBI Taxonomy root: taxid=1 (root of life)
    """

    def __init__(self) -> None:
        self._nodes: Dict[int, LCANode] = {}
        # Pre-register root
        self._nodes[1] = LCANode(
            taxid=1,
            parent_taxid=None,
            rank=TaxonomicRank.DOMAIN,
            scientific_name="root"
        )

    def add_node(self, node: TaxonNode) -> None:
        """Register a TaxonNode into the in-memory DAG."""
        lca_node = LCANode(
            taxid=node.taxid,
            parent_taxid=node.parent_taxid,
            rank=node.rank,
            scientific_name=node.scientific_name,
            weight=node.weight,
        )
        self._nodes[node.taxid] = lca_node
        if node.parent_taxid and node.parent_taxid in self._nodes:
            self._nodes[node.parent_taxid].children.append(node.taxid)

    def get_ancestors(self, taxid: int) -> List[int]:
        """
        Return ordered ancestor chain [taxid, parent, grandparent, ..., root].
        O(depth) traversal.
        """
        chain: List[int] = []
        current = taxid
        visited: Set[int] = set()
        while current is not None and current not in visited:
            chain.append(current)
            visited.add(current)
            node = self._nodes.get(current)
            if node is None or node.parent_taxid is None:
                break
            current = node.parent_taxid
        return chain

    def lca(self, taxid_a: int, taxid_b: int) -> int:
        """
        Compute the Lowest Common Ancestor of two taxa.

        Uses ancestor set intersection — efficient for shallow trees.
        Falls back to root (taxid=1) if no shared ancestor found.
        """
        ancestors_a: Set[int] = set(self.get_ancestors(taxid_a))
        for anc in self.get_ancestors(taxid_b):
            if anc in ancestors_a:
                return anc
        return 1  # root fallback

    def compute_path_score(self, taxid: int, weight_map: Dict[int, int]) -> int:
        """
        Score a root-to-leaf path by summing node weights along the lineage.

        Research §1.1:
            Score(Path_p) = Σ_{v∈Path_p} Weight(v)
        """
        return sum(weight_map.get(anc, 0) for anc in self.get_ancestors(taxid))

    def get_node(self, taxid: int) -> Optional[LCANode]:
        return self._nodes.get(taxid)

    def has_node(self, taxid: int) -> bool:
        return taxid in self._nodes


# ═══════════════════════════════════════════════════════════════════════════════
# §3 CANONICAL k-MER EXTRACTION (Research §1.1 — 2-bit encoding)
# ═══════════════════════════════════════════════════════════════════════════════

def _encode_kmer(seq: str) -> Optional[int]:
    """
    Convert a nucleotide string into its canonical 2-bit integer representation.

    Canonical k-mer = lexicographically smallest of (forward, reverse_complement).
    Returns None if the sequence contains ambiguous (N) bases.

    Encoding: A=00, C=01, G=10, T=11  (Research §1.1 Two-bit encoding)
    """
    bits = 0
    for ch in seq:
        code = _NUC_2BIT.get(ch)
        if code is None:
            return None  # ambiguous base
        bits = (bits << 2) | code

    # Compute reverse complement
    rc_bits = 0
    length = len(seq)
    for i in range(length):
        # Extract 2-bit from position i of forward
        fwd_base = (bits >> (2 * (length - 1 - i))) & 0b11
        rc_base = _COMPLEMENT_2BIT[fwd_base]
        rc_bits = (rc_bits << 2) | rc_base

    # Return canonical (min of forward and reverse complement)
    return min(bits, rc_bits)


def extract_canonical_kmers(sequence: str, k: int = KRAKEN2_K) -> List[int]:
    """
    Extract all valid canonical k-mers from a nucleotide sequence.

    Sliding window extraction; k-mers with ambiguous bases are skipped.

    Args:
        sequence: Raw nucleotide string (upper-case ACGTN)
        k: k-mer length (default KRAKEN2_K=35)

    Returns:
        List of canonical 2-bit integer k-mer hashes.
    """
    kmers: List[int] = []
    seq = sequence.upper()
    n = len(seq)
    for i in range(n - k + 1):
        kmer = seq[i:i + k]
        code = _encode_kmer(kmer)
        if code is not None:
            kmers.append(code)
    return kmers


# ═══════════════════════════════════════════════════════════════════════════════
# §4 MINIMIZER EXTRACTION (Research §1.1)
# ═══════════════════════════════════════════════════════════════════════════════

def _hash_mmer(m_bits: int) -> int:
    """
    Compute the minimizer hash for an m-mer (already in 2-bit representation).

    Uses Python's built-in hash for computational efficiency in simulation.
    In production Kraken 2, a modular arithmetic hash is used.
    """
    # XOR with a Kraken-style shuffling constant for better distribution
    return m_bits ^ (m_bits >> 17) ^ (m_bits << 7 & 0xFFFFFFFFFFFFFFFF)


def compute_minimizers(
    kmer_hashes: List[int],
    k: int = KRAKEN2_K,
    m: int = KRAKEN2_M
) -> List[KmerHashEntry]:
    """
    Compute minimizers for all canonical k-mers in a read.

    Mathematical definition (Research §1.1):
        Minimizer(W_k) = min_{0≤j≤k-m}{ hash(m-mer_j) }

    Window size = k - m + 1 = 5 (with default k=35, m=31).

    Each k-mer integer contains k*2 bits. The function extracts all
    overlapping m-mers (size m*2 bits) and selects the minimum hash value.

    Args:
        kmer_hashes: Canonical k-mer hash integers for a read
        k: k-mer length (default 35)
        m: minimizer length (default 31)

    Returns:
        List of KmerHashEntry objects (mapped_taxid defaults to 0 = unresolved).
    """
    window_size = k - m + 1  # = 5
    mask = (1 << (m * 2)) - 1  # mask to extract m*2 lower bits

    entries: List[KmerHashEntry] = []

    for kmer_val in kmer_hashes:
        min_hash = None
        min_offset = 0
        for j in range(window_size):
            # Shift out the j rightmost 2-bit positions from k-mer
            shift = 2 * (window_size - 1 - j)
            m_bits = (kmer_val >> shift) & mask
            h = _hash_mmer(m_bits)
            if min_hash is None or h < min_hash:
                min_hash = h
                min_offset = j

        if min_hash is not None:
            entries.append(KmerHashEntry(
                minimizer_hash=min_hash,
                window_offset=min_offset,
                mapped_taxid=1,  # default to root; resolved by CHT lookup
            ))

    return entries


# ═══════════════════════════════════════════════════════════════════════════════
# §5 KRAKEN 2 ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class Kraken2Engine:
    """
    Forensic Kraken 2 Exact k-mer Classification Engine.

    Implements the full bioinformatic pipeline from Research §1.1:
        1. Canonical k-mer extraction (k=35, 2-bit encoding)
        2. Minimizer calculation (m=31, window size 5)
        3. CHT lookup → TaxID per minimizer
        4. Weighted LCA pruned tree construction
        5. Root-to-leaf path scoring: Score(Path_p) = Σ_{v∈Path_p} Weight(v)
        6. Confidence threshold: k_path(T)/k_total ≥ C

    Note: This is a forensic simulation engine operating on symbolic
    taxonomy trees and CHT tables. Full Kraken 2 requires the actual
    50–100 GB binary CHT database. This engine provides mathematically
    faithful simulation for casework reporting and golden vector testing.
    """

    def __init__(
        self,
        taxonomy_tree: Optional[TaxonomyTree] = None,
        cht_lookup: Optional[Dict[int, int]] = None,
        config: Optional[ClassifierConfig] = None,
    ) -> None:
        """
        Initialize the Kraken 2 engine with taxonomy tree and CHT.

        Args:
            taxonomy_tree: Pre-built LCA taxonomy DAG (TaxonomyTree instance).
                           If None, an empty root-only tree is used.
            cht_lookup: Compact Hash Table mapping minimizer_hash → taxid.
                        If None, all lookups return root (taxid=1).
            config: ClassifierConfig with k, m, confidence threshold etc.
        """
        self.tree = taxonomy_tree or TaxonomyTree()
        self.cht = cht_lookup or {}
        self.config = config or ClassifierConfig(engine=ClassifierEngine.KRAKEN2)

        logger.info(
            f"[Kraken2Engine] Initialized with k={self.config.kmer_length}, "
            f"m={self.config.minimizer_length}, "
            f"C={self.config.confidence_threshold}, "
            f"CHT entries={len(self.cht)}"
        )

    def _lookup_taxid(self, minimizer_hash: int) -> int:
        """
        Look up a minimizer hash in the CHT.

        Returns the mapped TaxID or 0 (unclassified) if not found.
        In real Kraken 2, this is an O(1) direct hash table lookup.
        """
        return self.cht.get(minimizer_hash, 0)

    def classify_read(self, read: MetagenomicRead) -> Tuple[int, float]:
        """
        Classify a single metagenomic read against the indexed CHT.

        Steps:
            1. Extract canonical k-mers (k=35)
            2. Compute minimizers for each k-mer (m=31)
            3. Look up each minimizer in CHT → taxid
            4. Build weighted taxonomy tree from mapped taxids
            5. Score all root-to-leaf paths
            6. Apply confidence threshold: k_path(T)/k_total ≥ C

        Returns:
            Tuple of (assigned_taxid, confidence_score):
                assigned_taxid = 0 if unclassified
                confidence_score = k_path(T)/k_total ∈ [0, 1]
        """
        k = self.config.kmer_length
        m = self.config.minimizer_length
        C = self.config.confidence_threshold

        # Step 1: Extract canonical k-mers
        kmer_hashes = extract_canonical_kmers(read.sequence, k=k)
        if not kmer_hashes:
            return 0, 0.0  # unclassified: read too short or all ambiguous

        # Step 2: Compute minimizers
        minimizer_entries = compute_minimizers(kmer_hashes, k=k, m=m)
        k_total = len(minimizer_entries)

        if k_total == 0:
            return 0, 0.0

        # Step 3: Map minimizers to TaxIDs via CHT
        taxid_hit_counts: Dict[int, int] = {}
        for entry in minimizer_entries:
            taxid = self._lookup_taxid(entry.minimizer_hash)
            if taxid > 0:  # taxid=0 means no hit
                taxid_hit_counts[taxid] = taxid_hit_counts.get(taxid, 0) + 1

        if not taxid_hit_counts:
            return 0, 0.0  # no database hits

        # Step 4: Build weight map — propagate weights up to LCA
        # For each taxid hit, accumulate weight to all ancestors
        weight_map: Dict[int, int] = {}
        for taxid, count in taxid_hit_counts.items():
            for ancestor in self.tree.get_ancestors(taxid):
                weight_map[ancestor] = weight_map.get(ancestor, 0) + count

        # Step 5: Score all candidate leaf taxa
        # The assigned taxon is the leaf node with the maximum path score
        best_taxid = 0
        best_score = 0

        # Only evaluate taxa that had direct hits (leaves of the pruned tree)
        for taxid in taxid_hit_counts:
            path_score = self.compute_path_score(taxid, weight_map)
            if path_score > best_score:
                best_score = path_score
                best_taxid = taxid
            elif path_score == best_score and best_taxid != 0:
                # Tie → elevate to LCA (Research §1.1 — prevents overconfident classification)
                best_taxid = self.tree.lca(best_taxid, taxid)

        if best_taxid == 0 or best_taxid == 1:
            return 0, 0.0

        # Step 6: Apply confidence threshold
        # k_path(T) = number of minimizers mapping to T or descendants
        k_path = weight_map.get(best_taxid, 0)
        confidence = k_path / k_total

        if confidence < C:
            # Find lowest ancestor that meets threshold
            for ancestor in self.tree.get_ancestors(best_taxid)[1:]:  # skip self
                anc_k_path = weight_map.get(ancestor, 0)
                anc_confidence = anc_k_path / k_total
                if anc_confidence >= C:
                    return ancestor, anc_confidence
            return 0, 0.0  # no ancestor meets threshold → unclassified

        return best_taxid, confidence

    def compute_path_score(self, taxid: int, weight_map: Dict[int, int]) -> int:
        """
        Compute the path score for a root-to-leaf path.

        Research §1.1:
            Score(Path_p) = Σ_{v∈Path_p} Weight(v)
        """
        return sum(weight_map.get(anc, 0) for anc in self.tree.get_ancestors(taxid))

    def classify_reads(
        self,
        reads: List[MetagenomicRead],
        sample_id: str = "UNKNOWN_SAMPLE",
        reference_db: str = "STANDARD",
    ) -> TaxonomicProfile:
        """
        Classify a full batch of metagenomic reads and generate a TaxonomicProfile.

        Args:
            reads: List of MetagenomicRead objects
            sample_id: Case/sample identifier
            reference_db: Reference database identifier

        Returns:
            TaxonomicProfile with per-read classifications aggregated into
            hierarchical .kreport nodes and relative abundance vector.
        """
        import time
        t0 = time.perf_counter()

        total = len(reads)
        classified = 0
        unclassified = 0
        taxid_counts: Dict[int, int] = {}

        for read in reads:
            taxid, confidence = self.classify_read(read)
            if taxid == 0:
                unclassified += 1
            else:
                classified += 1
                taxid_counts[taxid] = taxid_counts.get(taxid, 0) + 1

        # Build abundance vector (normalize classified reads)
        abundance_vector: Dict[int, float] = {}
        if classified > 0:
            abundance_vector = {
                tid: count / classified
                for tid, count in taxid_counts.items()
            }

        # Build kreport nodes from classified taxid counts
        kreport_nodes: List[KReportNode] = []
        for tid, count in sorted(taxid_counts.items(), key=lambda x: -x[1]):
            pct = (count / total * 100) if total > 0 else 0.0
            node = self.tree.get_node(tid)
            rank_code = _rank_to_code(node.rank if node else TaxonomicRank.UNCLASSIFIED)
            kreport_nodes.append(KReportNode(
                pct_total=round(pct, 4),
                cumulative_reads=count,
                direct_reads=count,
                rank_code=rank_code,
                taxid=tid,
                name=node.scientific_name if node else f"TaxID_{tid}",
            ))

        unclass_fraction = unclassified / total if total > 0 else 0.0

        profile = TaxonomicProfile(
            sample_id=sample_id,
            engine_used=ClassifierEngine.KRAKEN2,
            reference_db=reference_db,
            total_reads=total,
            classified_reads=classified,
            unclassified_reads=unclassified,
            unclassified_fraction=round(unclass_fraction, 6),
            kreport_nodes=kreport_nodes,
            abundance_vector=abundance_vector,
            processing_time_seconds=round(time.perf_counter() - t0, 4),
            notes=(
                f"High unclassified fraction: {unclass_fraction:.1%} "
                f"(typical for forensic soil: 70–95%% against standard RefSeq)"
                if unclass_fraction > 0.70 else ""
            )
        )

        logger.info(
            f"[Kraken2Engine] Classified {sample_id}: "
            f"{classified}/{total} reads ({classified/total*100:.1f}%%) "
            f"unclassified_fraction={unclass_fraction:.3f}"
        )
        return profile


def _rank_to_code(rank: TaxonomicRank) -> str:
    """Map TaxonomicRank to Kraken 2 .kreport single-character rank code."""
    mapping = {
        TaxonomicRank.DOMAIN: "D",
        TaxonomicRank.PHYLUM: "P",
        TaxonomicRank.CLASS: "C",
        TaxonomicRank.ORDER: "O",
        TaxonomicRank.FAMILY: "F",
        TaxonomicRank.GENUS: "G",
        TaxonomicRank.SPECIES: "S",
        TaxonomicRank.STRAIN: "S1",
        TaxonomicRank.SGB: "SGB",
        TaxonomicRank.UNCLASSIFIED: "U",
    }
    return mapping.get(rank, "U")
