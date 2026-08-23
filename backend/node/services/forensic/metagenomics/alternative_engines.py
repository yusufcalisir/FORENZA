"""
FORENZA — Alternative Metagenomic Classifiers (Phase 2.3)
==========================================================

Implements three additional taxonomic classification engines:

1. Centrifuge: Compressed BWT/FM-Index + EM multi-hit allocation
2. sourmash: FracMinHash sketching + containment search C(A,B) = |A∩B|/|A|
3. Kaiju: 6-frame translation + BLOSUM62 Maximum-Exact-Match (MEM) alignment

Research §1.5 Alternative Classifiers:

    Centrifuge:
        - Compressed BWT/FM-Index storing entire bacterial collections in 4-8 GB
        - EM fractional weight distribution for multi-mapped reads
        - RAM: 4-8 GB (vs Kraken2's 50-100 GB)

    sourmash (FracMinHash):
        - Deterministic fraction 1/scaled of all k-mers retained
        - Containment: C(A,B) = |A∩B|/|A|
        - Jaccard: J(A,B) = |A∩B|/|A∪B|
        - RAM: <2 GB with precomputed sketches

    Kaiju:
        - 6-frame translation → amino acid queries
        - BLOSUM62 MEM alignment against protein database
        - Higher sensitivity for divergent uncultivated taxa
        - RAM: 12-120 GB (NCBI nr vs proGenomes)
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from .schemas import (
    ClassifierConfig,
    ClassifierEngine,
    KReportNode,
    TaxonomicProfile,
    TaxonomicRank,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# §1 CENTRIFUGE — Compressed FM-Index + EM Multi-Hit Allocation
# ═══════════════════════════════════════════════════════════════════════════════

# BLOSUM62 substitution matrix (Research §1.5 Kaiju)
# Simplified diagonal version for MEM scoring
_BLOSUM62_MATCH_SCORE: float = 5.0   # typical match score
_BLOSUM62_MISMATCH_SCORE: float = -4.0  # typical mismatch
_CENTRIFUGE_EM_CONVERGENCE: float = 1e-6
_CENTRIFUGE_MAX_ITERATIONS: int = 500


@dataclass
class CentrifugeReadHit:
    """
    Single read-to-reference mapping hit from Centrifuge FM-Index search.

    Multi-hit reads are distributed across candidate taxa using EM.
    """
    read_id: str
    candidate_taxids: List[int]         # all taxa with maximal exact matches
    mem_lengths: Dict[int, int] = field(default_factory=dict)  # taxid → MEM length
    fractional_weights: Dict[int, float] = field(default_factory=dict)  # taxid → fraction


class CentrifugeEngine:
    """
    Forensic Centrifuge BWT/FM-Index Compressed Classifier Engine.

    Key feature (Research §1.5):
        Unlike Kraken 2 (which immediately defaults to LCA for multi-hits),
        Centrifuge implements EM to assign FRACTIONAL weights across all
        equally-matching taxa. This provides finer abundance estimates
        without taxonomic inflation.

    Memory advantage:
        Standard microbial + viral collections: 4-8 GB RAM
        vs Kraken 2: 50-100 GB RAM

    EM algorithm:
        Initialize: weights[t] = 1/|candidates| for each hit
        E-step: expected_count[t] = Σ_reads (weight[t] * is_candidate(read))
        M-step: weight[t] = expected_count[t] / total_expected_count
        Repeat until max(|Δweight|) < 1e-6
    """

    def __init__(
        self,
        config: Optional[ClassifierConfig] = None,
        convergence_threshold: float = _CENTRIFUGE_EM_CONVERGENCE,
    ) -> None:
        self.config = config or ClassifierConfig(engine=ClassifierEngine.CENTRIFUGE)
        self.convergence_threshold = convergence_threshold
        self._read_hits: List[CentrifugeReadHit] = []
        self._taxid_names: Dict[int, str] = {}

        logger.info(
            f"[CentrifugeEngine] Initialized with EM convergence={convergence_threshold}"
        )

    def register_taxon(self, taxid: int, name: str) -> None:
        self._taxid_names[taxid] = name

    def add_read_hit(self, hit: CentrifugeReadHit) -> None:
        """Add a multi-hit read to the pending EM pool."""
        if hit.candidate_taxids:
            # Initialize uniform fractional weights
            n = len(hit.candidate_taxids)
            hit.fractional_weights = {t: 1.0 / n for t in hit.candidate_taxids}
            self._read_hits.append(hit)

    def run_em(self) -> Dict[int, float]:
        """
        Run EM algorithm to distribute multi-mapped reads across taxa.

        E-step: expected_count[t] = Σ_reads fractional_weight[t]
        M-step: weight[t] = expected_count[t] / Σ_t expected_count[t]

        Returns:
            Dict mapping taxid → fractional read abundance (sums to 1.0)
        """
        if not self._read_hits:
            return {}

        # Collect all candidate taxids
        all_taxids: Set[int] = set()
        for hit in self._read_hits:
            all_taxids.update(hit.candidate_taxids)

        # Initialize weights uniformly
        weights: Dict[int, float] = {t: 1.0 / len(all_taxids) for t in all_taxids}

        n_reads = len(self._read_hits)

        for iteration in range(_CENTRIFUGE_MAX_ITERATIONS):
            # E-step: compute expected counts
            expected_counts: Dict[int, float] = {t: 0.0 for t in all_taxids}
            for hit in self._read_hits:
                # Normalize fractional weights for this hit
                hit_total = sum(weights.get(t, 0.0) for t in hit.candidate_taxids)
                if hit_total > 0:
                    for taxid in hit.candidate_taxids:
                        w = weights.get(taxid, 0.0) / hit_total
                        expected_counts[taxid] = expected_counts.get(taxid, 0.0) + w
                        hit.fractional_weights[taxid] = w

            # M-step: update weights
            total_expected = sum(expected_counts.values())
            max_delta = 0.0

            new_weights: Dict[int, float] = {}
            for taxid in all_taxids:
                new_w = expected_counts[taxid] / total_expected if total_expected > 0 else 0.0
                delta = abs(new_w - weights.get(taxid, 0.0))
                max_delta = max(max_delta, delta)
                new_weights[taxid] = new_w

            weights = new_weights

            if max_delta < self.convergence_threshold:
                logger.debug(f"[CentrifugeEngine] EM converged at iteration {iteration + 1}")
                break

        return weights

    def classify_reads_batch(
        self,
        hits: List[CentrifugeReadHit],
        total_reads: int,
        sample_id: str = "UNKNOWN_SAMPLE",
        reference_db: str = "CENTRIFUGE_REFSEQ",
    ) -> TaxonomicProfile:
        """
        Classify a batch of reads and generate TaxonomicProfile via EM.

        Args:
            hits: Pre-computed CentrifugeReadHit list (from FM-index search)
            total_reads: Total input reads in the sample
            sample_id: Case identifier
            reference_db: Reference database identifier

        Returns:
            TaxonomicProfile with EM-distributed read abundances.
        """
        import time
        t0 = time.perf_counter()

        self._read_hits = []
        for hit in hits:
            self.add_read_hit(hit)

        weights = self.run_em()

        if not weights:
            return TaxonomicProfile(
                sample_id=sample_id,
                engine_used=ClassifierEngine.CENTRIFUGE,
                reference_db=reference_db,
                total_reads=total_reads,
                classified_reads=0,
                unclassified_reads=total_reads,
                unclassified_fraction=1.0,
                kreport_nodes=[],
                abundance_vector={},
                processing_time_seconds=round(time.perf_counter() - t0, 4),
                notes="Centrifuge: No read hits to classify."
            )

        classified_reads = len(hits)
        unclassified_reads = total_reads - classified_reads
        unclass_fraction = unclassified_reads / total_reads if total_reads > 0 else 0.0

        kreport_nodes: List[KReportNode] = []
        abundance_vector: Dict[int, float] = {}

        for taxid, weight in sorted(weights.items(), key=lambda x: -x[1]):
            if weight < 1e-9:
                continue
            pct = weight * classified_reads / total_reads * 100.0
            kreport_nodes.append(KReportNode(
                pct_total=round(pct, 4),
                cumulative_reads=int(weight * classified_reads),
                direct_reads=int(weight * classified_reads),
                rank_code="S",
                taxid=taxid,
                name=self._taxid_names.get(taxid, f"TaxID_{taxid}"),
            ))
            abundance_vector[taxid] = weight

        return TaxonomicProfile(
            sample_id=sample_id,
            engine_used=ClassifierEngine.CENTRIFUGE,
            reference_db=reference_db,
            total_reads=total_reads,
            classified_reads=classified_reads,
            unclassified_reads=unclassified_reads,
            unclassified_fraction=round(unclass_fraction, 6),
            kreport_nodes=kreport_nodes,
            abundance_vector=abundance_vector,
            processing_time_seconds=round(time.perf_counter() - t0, 4),
            notes=(
                f"Centrifuge EM: {len(weights)} taxa, "
                f"{len(hits)} multi-mapped reads redistributed. "
                f"Converged with threshold={self.convergence_threshold}."
            )
        )


# ═══════════════════════════════════════════════════════════════════════════════
# §2 SOURMASH — FracMinHash Sketching & Containment Search
# ═══════════════════════════════════════════════════════════════════════════════

class FracMinHashSketch:
    """
    sourmash FracMinHash sketch for a single genome or sample.

    FracMinHash (Research §1.5):
        scale factor s: retain all k-mers with hash < max_hash/s
        → ~1/s fraction of all k-mers sampled deterministically

    Containment (Research §1.5):
        C(A, B) = |A ∩ B| / |A|
        → fraction of query sketch A contained in reference sketch B

    Jaccard (for symmetric comparison):
        J(A, B) = |A ∩ B| / |A ∪ B|

    Memory: <2 GB with precomputed sketches (vs Kraken2's 50-100 GB)
    """

    def __init__(self, scaled: int = 1000, ksize: int = 31) -> None:
        """
        Initialize FracMinHash sketch.

        Args:
            scaled: Scale factor s (default 1000 → ~0.1% of k-mers sampled)
            ksize: k-mer size (default 31 for sourmash default)
        """
        self.scaled = scaled
        self.ksize = ksize
        self._max_hash = (2 ** 64) // scaled  # threshold for inclusion
        self._hashes: Set[int] = set()

    def add_hash(self, h: int) -> None:
        """Add a k-mer hash to the sketch if below the FracMinHash threshold."""
        # FracMinHash: retain if hash < max_hash (deterministic subsampling)
        if h < self._max_hash:
            self._hashes.add(h)

    def add_sequence(self, sequence: str) -> None:
        """Add all k-mers from a sequence to the sketch."""
        from .kraken2_engine import extract_canonical_kmers, _hash_mmer, KRAKEN2_K
        # Use canonical k-mer extraction with sketch ksize
        kmer_hashes = extract_canonical_kmers(sequence, k=self.ksize)
        for kh in kmer_hashes:
            # Apply FracMinHash threshold
            self.add_hash(kh & 0xFFFFFFFFFFFFFFFF)

    @property
    def hashes(self) -> Set[int]:
        return self._hashes

    def containment(self, other: "FracMinHashSketch") -> float:
        """
        Compute containment C(self, other).

        Research §1.5:
            C(A, B) = |A ∩ B| / |A|

        C(query, reference) → fraction of query k-mers found in reference.

        Returns:
            Containment score ∈ [0.0, 1.0]
        """
        if not self._hashes:
            return 0.0
        intersection = len(self._hashes & other._hashes)
        return intersection / len(self._hashes)

    def jaccard(self, other: "FracMinHashSketch") -> float:
        """
        Compute Jaccard similarity J(A, B) = |A∩B|/|A∪B|.

        Note: sourmash uses containment for database search; Jaccard for
        symmetric genome similarity estimation.
        """
        union = self._hashes | other._hashes
        if not union:
            return 0.0
        return len(self._hashes & other._hashes) / len(union)


class SourmashEngine:
    """
    Forensic sourmash FracMinHash Containment Search Engine.

    Uses precomputed FracMinHash sketches to rapidly identify which
    reference genomes are contained within a metagenomic sample sketch.

    C(A, B) = |A ∩ B| / |A|  (Research §1.5)

    Optimal for:
        - Rapid screening (<2 GB RAM)
        - Compositional decomposition of soil mixtures
        - Cross-sample similarity screening
    """

    def __init__(
        self,
        config: Optional[ClassifierConfig] = None,
    ) -> None:
        self.config = config or ClassifierConfig(engine=ClassifierEngine.SOURMASH)
        self._reference_sketches: Dict[int, Tuple[str, FracMinHashSketch]] = {}

        logger.info(
            f"[SourmashEngine] Initialized with scaled={self.config.scale_factor}"
        )

    def add_reference_sketch(self, taxid: int, name: str, sketch: FracMinHashSketch) -> None:
        """Register a reference genome sketch for containment search."""
        self._reference_sketches[taxid] = (name, sketch)

    def search_containment(
        self,
        query_sketch: FracMinHashSketch,
        min_containment: float = 0.01,
    ) -> List[Tuple[int, str, float]]:
        """
        Search all reference sketches for containment with query.

        Research §1.5:
            C(query, reference) = |query ∩ reference| / |query|
            → ranks references by fraction of query k-mers they cover

        Args:
            query_sketch: FracMinHashSketch of the questioned sample
            min_containment: Minimum containment threshold (default 0.01 = 1%)

        Returns:
            Sorted list of (taxid, name, containment_score) above threshold
        """
        results: List[Tuple[int, str, float]] = []
        for taxid, (name, ref_sketch) in self._reference_sketches.items():
            c = query_sketch.containment(ref_sketch)
            if c >= min_containment:
                results.append((taxid, name, c))
        return sorted(results, key=lambda x: -x[2])

    def classify_sample(
        self,
        query_sketch: FracMinHashSketch,
        total_reads: int,
        sample_id: str = "UNKNOWN_SAMPLE",
        min_containment: float = 0.01,
    ) -> TaxonomicProfile:
        """
        Classify a metagenomic sample via containment search.

        Returns:
            TaxonomicProfile with containment-ranked abundances.
        """
        import time
        t0 = time.perf_counter()

        matches = self.search_containment(query_sketch, min_containment=min_containment)

        if not matches:
            return TaxonomicProfile(
                sample_id=sample_id,
                engine_used=ClassifierEngine.SOURMASH,
                reference_db="SOURMASH_GTDB_R220",
                total_reads=total_reads,
                classified_reads=0,
                unclassified_reads=total_reads,
                unclassified_fraction=1.0,
                kreport_nodes=[],
                abundance_vector={},
                processing_time_seconds=round(time.perf_counter() - t0, 4),
                notes=f"sourmash: No references above min_containment={min_containment}"
            )

        # Normalize containment scores to abundance fractions
        total_containment = sum(c for _, _, c in matches)
        abundance_vector: Dict[int, float] = {}
        kreport_nodes: List[KReportNode] = []

        for taxid, name, containment in matches:
            frac = containment / total_containment if total_containment > 0 else 0.0
            pct = frac * 100.0
            abundance_vector[taxid] = frac
            kreport_nodes.append(KReportNode(
                pct_total=round(pct, 4),
                cumulative_reads=int(frac * total_reads),
                direct_reads=int(frac * total_reads),
                rank_code="S",
                taxid=taxid,
                name=name,
            ))

        classified_reads = int(query_sketch.hashes.__len__() * self.config.scale_factor)
        classified_reads = min(classified_reads, total_reads)
        unclassified_reads = total_reads - classified_reads
        unclass_fraction = unclassified_reads / total_reads if total_reads > 0 else 0.0

        return TaxonomicProfile(
            sample_id=sample_id,
            engine_used=ClassifierEngine.SOURMASH,
            reference_db="SOURMASH_GTDB_R220",
            total_reads=total_reads,
            classified_reads=classified_reads,
            unclassified_reads=unclassified_reads,
            unclassified_fraction=round(unclass_fraction, 6),
            kreport_nodes=kreport_nodes,
            abundance_vector=abundance_vector,
            processing_time_seconds=round(time.perf_counter() - t0, 4),
            notes=(
                f"sourmash FracMinHash (scaled={self.config.scale_factor}): "
                f"{len(matches)} references above C≥{min_containment}. "
                f"Query sketch size: {len(query_sketch.hashes)} k-mer hashes."
            )
        )


# ═══════════════════════════════════════════════════════════════════════════════
# §3 KAIJU — 6-Frame Translation + BLOSUM62 MEM Protein Alignment
# ═══════════════════════════════════════════════════════════════════════════════

# Standard genetic code for 6-frame translation
_CODON_TABLE: Dict[str, str] = {
    "TTT": "F", "TTC": "F", "TTA": "L", "TTG": "L",
    "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L",
    "ATT": "I", "ATC": "I", "ATA": "I", "ATG": "M",
    "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
    "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S",
    "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T",
    "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
    "TAT": "Y", "TAC": "Y", "TAA": "*", "TAG": "*",
    "CAT": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
    "AAT": "N", "AAC": "N", "AAA": "K", "AAG": "K",
    "GAT": "D", "GAC": "D", "GAA": "E", "GAG": "E",
    "TGT": "C", "TGC": "C", "TGA": "*", "TGG": "W",
    "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R",
    "AGT": "S", "AGC": "S", "AGA": "R", "AGG": "R",
    "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G",
}

_REVERSE_COMPLEMENT_MAP: Dict[str, str] = {
    "A": "T", "T": "A", "C": "G", "G": "C", "N": "N"
}


def _reverse_complement(seq: str) -> str:
    """Compute reverse complement of a DNA sequence."""
    return "".join(_REVERSE_COMPLEMENT_MAP.get(c, "N") for c in reversed(seq.upper()))


def _translate_frame(seq: str) -> str:
    """Translate a nucleotide sequence in one reading frame to amino acids."""
    aa = []
    for i in range(0, len(seq) - 2, 3):
        codon = seq[i:i+3].upper()
        aa.append(_CODON_TABLE.get(codon, "X"))
    return "".join(aa)


def translate_six_frames(nucleotide_seq: str) -> List[str]:
    """
    Translate a DNA read in all 6 reading frames (Kaiju §1.5).

    Frames:
        +1, +2, +3: forward strand offsets 0, 1, 2
        -1, -2, -3: reverse complement strand offsets 0, 1, 2

    Returns:
        List of 6 amino acid strings (each may contain stop codons '*' and 'X').
    """
    seq = nucleotide_seq.upper()
    rc = _reverse_complement(seq)
    frames = []
    for offset in range(3):
        frames.append(_translate_frame(seq[offset:]))
        frames.append(_translate_frame(rc[offset:]))
    return frames


@dataclass
class KaijuHit:
    """
    A Kaiju Maximum-Exact-Match (MEM) protein segment alignment result.

    MEM segments are scored with BLOSUM62 (Research §1.5).
    """
    read_id: str
    frame: int                  # 0-5 (6-frame)
    taxid: int                  # matched reference taxon
    mem_length: int             # length of maximum exact match (amino acids)
    blosum62_score: float       # alignment score from BLOSUM62 matrix
    protein_name: str = ""      # reference protein name


class KaijuEngine:
    """
    Forensic Kaiju 6-Frame Protein MEM Classification Engine.

    Higher sensitivity than nucleotide classifiers for divergent environmental
    taxa that share amino acid homology but lack nucleotide identity.

    Research §1.5:
        "Because protein coding sequences diverge slower than nucleotide
        sequences over evolutionary timescales, Kaiju achieves higher sensitivity
        when classifying divergent, uncultivated environmental taxa."

    Protein database options (§4.2): 12-120 GB RAM
        - NCBI nr: broadest coverage
        - proGenomes: curated microbial proteins
    """

    def __init__(
        self,
        config: Optional[ClassifierConfig] = None,
        min_blosum62_score: float = 65.0,
        min_mem_length: int = 11,
    ) -> None:
        """
        Initialize Kaiju engine.

        Args:
            config: ClassifierConfig (engine forced to KAIJU)
            min_blosum62_score: Minimum BLOSUM62 score for valid MEM alignment.
                                Default 65.0 (Kaiju default score threshold).
            min_mem_length: Minimum amino acid MEM length. Default 11 AA.
        """
        self.config = config or ClassifierConfig(engine=ClassifierEngine.KAIJU)
        self.min_blosum62_score = min_blosum62_score
        self.min_mem_length = min_mem_length
        # Protein reference index: taxid → list of reference amino acid sequences
        self._protein_index: Dict[int, List[str]] = {}
        self._taxid_names: Dict[int, str] = {}

        logger.info(
            f"[KaijuEngine] Initialized with min_blosum62={min_blosum62_score}, "
            f"min_mem={min_mem_length} aa"
        )

    def register_protein_reference(
        self,
        taxid: int,
        name: str,
        sequences: List[str]
    ) -> None:
        """Add reference protein sequences for a taxon."""
        self._protein_index[taxid] = sequences
        self._taxid_names[taxid] = name

    def _compute_mem_length(self, query_aa: str, ref_aa: str) -> int:
        """
        Find the length of the Maximum-Exact-Match between two amino acid strings.

        Simplified MEM: find the longest common substring length.
        In production Kaiju, this is performed via BWT/FM-Index MEM search.
        """
        max_len = 0
        n, m = len(query_aa), len(ref_aa)
        for i in range(n):
            for j in range(m):
                length = 0
                while (i + length < n and j + length < m and
                       query_aa[i + length] == ref_aa[j + length]):
                    length += 1
                max_len = max(max_len, length)
        return max_len

    def _blosum62_score_mem(self, mem_length: int) -> float:
        """
        Approximate BLOSUM62 score for a maximum-exact-match segment.

        In production: actual BLOSUM62 substitution scores are summed per
        amino acid pair. Here we use: score = mem_length × match_score.
        where match_score = 5.0 (typical BLOSUM62 diagonal for matched residues).
        """
        return float(mem_length) * _BLOSUM62_MATCH_SCORE

    def classify_read(self, read_id: str, sequence: str) -> Optional[KaijuHit]:
        """
        Classify a single read via 6-frame translation and BLOSUM62 MEM.

        Steps:
            1. Translate read in all 6 frames
            2. For each frame × reference: find MEM length
            3. Compute BLOSUM62 score = MEM_length × 5.0
            4. Accept hits above min_blosum62_score and min_mem_length
            5. Return the best-scoring hit (or None if below thresholds)

        Args:
            read_id: Read identifier
            sequence: Nucleotide sequence

        Returns:
            Best KaijuHit or None if no valid MEM found.
        """
        aa_frames = translate_six_frames(sequence)
        best_hit: Optional[KaijuHit] = None
        best_score: float = 0.0

        for frame_idx, query_aa in enumerate(aa_frames):
            # Remove stop codons for alignment
            query_aa_clean = query_aa.replace("*", "").replace("X", "")
            if len(query_aa_clean) < self.min_mem_length:
                continue

            for taxid, ref_proteins in self._protein_index.items():
                for ref_aa in ref_proteins:
                    mem_len = self._compute_mem_length(query_aa_clean, ref_aa)
                    if mem_len >= self.min_mem_length:
                        score = self._blosum62_score_mem(mem_len)
                        if score >= self.min_blosum62_score and score > best_score:
                            best_score = score
                            best_hit = KaijuHit(
                                read_id=read_id,
                                frame=frame_idx,
                                taxid=taxid,
                                mem_length=mem_len,
                                blosum62_score=score,
                                protein_name=self._taxid_names.get(taxid, f"TaxID_{taxid}"),
                            )

        return best_hit

    def classify_reads_batch(
        self,
        reads: List[Tuple[str, str]],
        total_reads: int,
        sample_id: str = "UNKNOWN_SAMPLE",
        reference_db: str = "KAIJU_PROGENOMES",
    ) -> TaxonomicProfile:
        """
        Classify a batch of reads via Kaiju 6-frame protein MEM.

        Args:
            reads: List of (read_id, sequence) tuples
            total_reads: Total input reads
            sample_id: Sample identifier
            reference_db: Reference database name

        Returns:
            TaxonomicProfile with protein MEM classifications.
        """
        import time
        t0 = time.perf_counter()

        taxid_counts: Dict[int, int] = {}
        classified = 0
        unclassified = 0

        for read_id, sequence in reads:
            hit = self.classify_read(read_id, sequence)
            if hit is None:
                unclassified += 1
            else:
                classified += 1
                taxid_counts[hit.taxid] = taxid_counts.get(hit.taxid, 0) + 1

        abundance_vector: Dict[int, float] = {}
        kreport_nodes: List[KReportNode] = []

        if classified > 0:
            abundance_vector = {
                tid: count / classified for tid, count in taxid_counts.items()
            }
            for taxid, count in sorted(taxid_counts.items(), key=lambda x: -x[1]):
                pct = count / total_reads * 100.0
                kreport_nodes.append(KReportNode(
                    pct_total=round(pct, 4),
                    cumulative_reads=count,
                    direct_reads=count,
                    rank_code="S",
                    taxid=taxid,
                    name=self._taxid_names.get(taxid, f"TaxID_{taxid}"),
                ))

        unclass_fraction = unclassified / total_reads if total_reads > 0 else 0.0

        return TaxonomicProfile(
            sample_id=sample_id,
            engine_used=ClassifierEngine.KAIJU,
            reference_db=reference_db,
            total_reads=total_reads,
            classified_reads=classified,
            unclassified_reads=unclassified,
            unclassified_fraction=round(unclass_fraction, 6),
            kreport_nodes=kreport_nodes,
            abundance_vector=abundance_vector,
            processing_time_seconds=round(time.perf_counter() - t0, 4),
            notes=(
                f"Kaiju 6-frame BLOSUM62 MEM: {classified}/{total_reads} reads classified. "
                f"Min BLOSUM62 score: {self.min_blosum62_score}, "
                f"min MEM: {self.min_mem_length} aa."
            )
        )
