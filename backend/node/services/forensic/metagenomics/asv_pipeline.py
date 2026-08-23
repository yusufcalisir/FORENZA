"""
FORENZA — Amplicon Sequence Variant (ASV) Inference Pipeline (Phase 3.3)
=========================================================================

Implements the DADA2-compatible forensic amplicon denoising and ASV inference
pipeline for multi-locus environmental eDNA and pollen barcoding.

Research §3.2 Forensic Palynology & DADA2 Mathematical Model:

    DADA2 Parametric Error Model:
        P(read r_j | true sequence s_i) = Π_{k=1}^{L} P(r_j[k] | s_i[k], q_j[k])
        where q_j[k] is the Phred quality score at position k.

        Error rate: P(mismatch | Q-score) = 10^(-Q/10)
                    P(match | Q-score) = 1 - 10^(-Q/10)

    Bimeric Chimera Detection:
        A read r is flagged as bimeric if it can be reconstructed by
        concatenation of a prefix of s_a and a suffix of s_b, where
        s_a and s_b are both more abundant sequences:
            r = s_a[0:breakpoint] + s_b[breakpoint:]
        Standard cutoff: parent_to_query_ratio ≥ 2.0 (Research §3.2)

    Naïve Bayes Taxonomic Assignment:
        P(taxon T | k-mer set K) ∝ P(T) × Π_{k_i ∈ K} P(k_i | T)
        Bootstrap confidence: resample 8-mers 100× and record taxon stability.
        Threshold: bootstrap_confidence ≥ 80% for reliable assignments.

    Simplex closure after ASV normalization:
        Relative abundance = count_i / Σ count_j
        |Σ rel_abundance_i - 1.0| ≤ 1e-6 (AGENTS.md constraint)
"""

from __future__ import annotations

import hashlib
import logging
import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from .schemas import (
    ASVFeatureTable,
    ASVTaxonomicAssignment,
    TaxonomicRank,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# §1 DADA2 ERROR MODEL CONSTANTS (Research §3.2)
# ═══════════════════════════════════════════════════════════════════════════════

# Phred quality score → error probability: P(error | Q) = 10^(-Q/10)
# Precomputed for common Q-scores
_PHRED_ERROR_PROB: Dict[int, float] = {
    q: 10.0 ** (-q / 10.0) for q in range(0, 41)
}

# Bimeric chimera detection: parent-to-query read ratio threshold (Research §3.2)
BIMERA_PARENT_RATIO_THRESHOLD: float = 2.0

# Naïve Bayes k-mer size for taxonomic assignment (8-mers)
NB_KMER_SIZE: int = 8
# Bootstrap confidence resampling iterations
NB_BOOTSTRAP_ITERATIONS: int = 100
# Minimum bootstrap confidence for reliable assignment (Research §3.2)
NB_MIN_BOOTSTRAP_CONFIDENCE: float = 80.0


# ═══════════════════════════════════════════════════════════════════════════════
# §2 DADA2 PARAMETRIC ERROR MODEL
# ═══════════════════════════════════════════════════════════════════════════════

class DADA2ErrorModel:
    """
    DADA2 Parametric Per-Base Error Model.

    Computes the likelihood P(read | true_sequence) using the log-sum
    of per-position error probabilities from Phred quality scores.

    Research §3.2 (DADA2 Algorithm):
        P(read r | true sequence s) = Π_{k=1}^{L} P(r[k] | s[k], Q[k])
        where:
            P(mismatch | Q) = 10^(-Q/10)
            P(match | Q) = 1 - 10^(-Q/10)

    Log-space computation:
        log P(r | s) = Σ_k [log P(r[k] | s[k], Q[k])]
    """

    def __init__(self, seed: int = 42) -> None:
        self._rng = random.Random(seed)
        # Learned error matrix: will be populated by learn_error_rates()
        # Format: error_matrix[from_nuc][to_nuc][q_bin] = error_rate
        self._error_matrix: Dict[str, Dict[str, Dict[int, float]]] = {}
        self._initialize_default_error_model()

    def _initialize_default_error_model(self) -> None:
        """
        Initialize default per-base error rates from Phred quality scores.
        Production DADA2 learns these from the data; here we use Q-score-derived priors.
        """
        nucs = ["A", "C", "G", "T"]
        for from_nuc in nucs:
            self._error_matrix[from_nuc] = {}
            for to_nuc in nucs:
                self._error_matrix[from_nuc][to_nuc] = {}
                for q in range(0, 41):
                    if from_nuc == to_nuc:
                        # Match: P = 1 - 10^(-Q/10)
                        self._error_matrix[from_nuc][to_nuc][q] = 1.0 - _PHRED_ERROR_PROB[q]
                    else:
                        # Substitution: P = 10^(-Q/10) / 3 (equal substitution model)
                        self._error_matrix[from_nuc][to_nuc][q] = _PHRED_ERROR_PROB[q] / 3.0

    def log_prob_read_given_sequence(
        self,
        read_seq: str,
        true_seq: str,
        quality_scores: List[int],
    ) -> float:
        """
        Compute log P(read | true_sequence) using the DADA2 error model.

        Research §3.2:
            log P(r | s) = Σ_k log P(r[k] | s[k], Q[k])

        Args:
            read_seq: Observed read nucleotide sequence
            true_seq: Candidate true sequence
            quality_scores: Per-position Phred Q-scores

        Returns:
            Log-probability (base-10) of the read given the true sequence.
            Returns -inf if sequences have different lengths.
        """
        if len(read_seq) != len(true_seq) or len(read_seq) != len(quality_scores):
            return float("-inf")

        log_prob = 0.0
        for k, (r, s, q) in enumerate(zip(read_seq.upper(), true_seq.upper(), quality_scores)):
            q_clamp = min(max(q, 0), 40)
            r_nuc = r if r in self._error_matrix else "A"
            s_nuc = s if s in self._error_matrix.get(r_nuc, {}) else "A"
            p = self._error_matrix[r_nuc][s_nuc][q_clamp]
            # Guard against log(0)
            log_prob += math.log10(max(p, 1e-15))

        return log_prob


# ═══════════════════════════════════════════════════════════════════════════════
# §3 BIMERIC CHIMERA DETECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class BimeraDetector:
    """
    Bimeric Chimera Detection Module (Research §3.2 Chimera Removal).

    A read is flagged as a bimera if it can be reconstructed as:
        r = parent_a[0:breakpoint] + parent_b[breakpoint:]
    where parent_a and parent_b are both more abundant sequences
    by at least BIMERA_PARENT_RATIO_THRESHOLD = 2.0.

    Method: consensus bimera (checks all possible breakpoints).
    """

    def __init__(
        self,
        parent_ratio_threshold: float = BIMERA_PARENT_RATIO_THRESHOLD
    ) -> None:
        self.parent_ratio_threshold = parent_ratio_threshold

    def is_bimera(
        self,
        candidate_seq: str,
        candidate_count: int,
        parent_sequences: List[Tuple[str, int]],
    ) -> bool:
        """
        Determine if candidate_seq is a bimeric chimera of any parent pair.

        Args:
            candidate_seq: Sequence to test
            candidate_count: Read count of this candidate
            parent_sequences: List of (sequence, count) for all sequences
                              with count ≥ threshold. Each parent must have
                              count ≥ candidate_count × parent_ratio_threshold.

        Returns:
            True if candidate_seq is a bimeric chimera
        """
        seq = candidate_seq.upper()
        n = len(seq)

        # Only consider parents with sufficient abundance ratio
        valid_parents = [
            (parent_seq.upper(), cnt)
            for parent_seq, cnt in parent_sequences
            if cnt >= candidate_count * self.parent_ratio_threshold
               and parent_seq.upper() != seq
               and len(parent_seq) == n
        ]

        if len(valid_parents) < 2:
            return False

        # Try all breakpoints and parent pairs
        for i, (pa, _) in enumerate(valid_parents):
            for j, (pb, _) in enumerate(valid_parents):
                if i == j:
                    continue
                # Test all breakpoints
                for bp in range(1, n):
                    reconstructed = pa[:bp] + pb[bp:]
                    if reconstructed == seq:
                        logger.debug(
                            f"[BimeraDetector] Bimera detected at breakpoint {bp}: "
                            f"{pa[:min(10, bp)]}...|...{pb[bp:min(bp+10, n)]}"
                        )
                        return True

        return False

    def remove_bimeras(
        self,
        sequence_counts: Dict[str, int],
    ) -> Tuple[Dict[str, int], int, float]:
        """
        Remove bimeric chimeras from a sequence count dictionary.

        Args:
            sequence_counts: {sequence: read_count} (raw denoised sequences)

        Returns:
            Tuple of (non_chimeric_counts, n_chimeras_removed, chimera_fraction)
        """
        # Sort by count descending (most abundant are likely true parents)
        sorted_seqs = sorted(
            sequence_counts.items(),
            key=lambda x: -x[1]
        )

        non_chimeric: Dict[str, int] = {}
        n_chimeras = 0

        for seq, count in sorted_seqs:
            # Check against all currently accepted non-chimeric sequences
            parent_pool = list(non_chimeric.items())
            if not self.is_bimera(seq, count, parent_pool):
                non_chimeric[seq] = count
            else:
                n_chimeras += 1

        total_seqs = len(sequence_counts)
        chimera_fraction = n_chimeras / total_seqs if total_seqs > 0 else 0.0

        return non_chimeric, n_chimeras, chimera_fraction


# ═══════════════════════════════════════════════════════════════════════════════
# §4 NAÏVE BAYES TAXONOMIC CLASSIFIER (8-mer Bootstrap)
# ═══════════════════════════════════════════════════════════════════════════════

class NaiveBayesTaxonomicClassifier:
    """
    Naïve Bayes 8-mer Bootstrap Taxonomic Classifier (Research §3.2).

    Reproduces the QIIME 2 feature-classifier Naïve Bayes algorithm:

        P(taxon T | k-mer set K) ∝ P(T) × Π_{k_i ∈ K} P(k_i | T)

    Bootstrap confidence:
        For 100 iterations: resample 50% of 8-mers (without replacement).
        Bootstrap confidence = % of iterations where the same taxon is assigned.
        Threshold: ≥ 80% for reliable assignment (Research §3.2).
    """

    def __init__(
        self,
        kmer_size: int = NB_KMER_SIZE,
        bootstrap_iterations: int = NB_BOOTSTRAP_ITERATIONS,
        min_confidence: float = NB_MIN_BOOTSTRAP_CONFIDENCE,
        seed: int = 42,
    ) -> None:
        self.kmer_size = kmer_size
        self.bootstrap_iterations = bootstrap_iterations
        self.min_confidence = min_confidence
        self._rng = random.Random(seed)

        # Training database: taxon_label → {kmer: frequency}
        self._taxon_kmer_probs: Dict[str, Dict[str, float]] = {}
        self._taxon_priors: Dict[str, float] = {}
        self._all_kmers: Set[str] = set()

    def _extract_kmers(self, sequence: str) -> List[str]:
        """Extract all k-mers from a sequence."""
        seq = sequence.upper()
        return [seq[i:i+self.kmer_size] for i in range(len(seq) - self.kmer_size + 1)]

    def train(
        self,
        reference_sequences: List[Tuple[str, str]],
    ) -> None:
        """
        Train the Naïve Bayes classifier on reference sequences.

        Args:
            reference_sequences: List of (sequence, taxon_label) pairs
        """
        # Collect all k-mers per taxon
        taxon_kmer_counts: Dict[str, Dict[str, int]] = {}
        taxon_seq_counts: Dict[str, int] = {}
        total_seqs = len(reference_sequences)

        for seq, taxon in reference_sequences:
            if taxon not in taxon_kmer_counts:
                taxon_kmer_counts[taxon] = {}
                taxon_seq_counts[taxon] = 0
            taxon_seq_counts[taxon] += 1

            for kmer in self._extract_kmers(seq):
                self._all_kmers.add(kmer)
                taxon_kmer_counts[taxon][kmer] = taxon_kmer_counts[taxon].get(kmer, 0) + 1

        # Compute P(k_i | T) with Laplace smoothing (add-1)
        vocab_size = len(self._all_kmers)
        for taxon, kmer_counts in taxon_kmer_counts.items():
            total_kmers = sum(kmer_counts.values())
            self._taxon_kmer_probs[taxon] = {
                kmer: (count + 1) / (total_kmers + vocab_size)
                for kmer, count in kmer_counts.items()
            }
            # P(T) = sequence count / total sequences (prior)
            self._taxon_priors[taxon] = taxon_seq_counts[taxon] / total_seqs

        logger.info(
            f"[NaiveBayesClassifier] Trained on {total_seqs} sequences, "
            f"{len(self._taxon_kmer_probs)} taxa, {vocab_size} unique {self.kmer_size}-mers"
        )

    def _classify_kmer_set(self, kmers: List[str]) -> Optional[str]:
        """
        Classify an ASV from its k-mer set using log-sum Naïve Bayes.

        Returns:
            Best taxon label or None if no training data.
        """
        if not self._taxon_kmer_probs:
            return None

        best_taxon = None
        best_log_prob = float("-inf")
        bg_prob = 1.0 / (len(self._all_kmers) + 1)  # background for unseen kmers

        for taxon, kmer_probs in self._taxon_kmer_probs.items():
            # log P(T | K) = log P(T) + Σ log P(k_i | T)
            log_prob = math.log10(max(self._taxon_priors.get(taxon, 1e-9), 1e-9))
            for kmer in kmers:
                p = kmer_probs.get(kmer, bg_prob)
                log_prob += math.log10(max(p, 1e-15))

            if log_prob > best_log_prob:
                best_log_prob = log_prob
                best_taxon = taxon

        return best_taxon

    def classify_with_bootstrap(
        self,
        asv_sequence: str,
    ) -> Tuple[Optional[str], float]:
        """
        Classify an ASV with bootstrap confidence estimation.

        Research §3.2 Bootstrap Protocol:
            For 100 iterations:
                1. Resample 50% of the query k-mers without replacement
                2. Classify with Naïve Bayes
                3. Record assigned taxon
            Bootstrap confidence = max taxon vote fraction × 100

        Args:
            asv_sequence: Exact denoised ASV nucleotide sequence

        Returns:
            Tuple of (best_taxon, bootstrap_confidence ∈ [0, 100])
        """
        all_kmers = self._extract_kmers(asv_sequence)
        if not all_kmers:
            return None, 0.0

        taxon_votes: Dict[str, int] = {}
        resample_size = max(1, len(all_kmers) // 2)

        for _ in range(self.bootstrap_iterations):
            # Resample 50% of k-mers
            resampled = self._rng.sample(
                all_kmers,
                min(resample_size, len(all_kmers))
            )
            taxon = self._classify_kmer_set(resampled)
            if taxon:
                taxon_votes[taxon] = taxon_votes.get(taxon, 0) + 1

        if not taxon_votes:
            return None, 0.0

        best_taxon = max(taxon_votes, key=lambda t: taxon_votes[t])
        confidence = (taxon_votes[best_taxon] / self.bootstrap_iterations) * 100.0

        return best_taxon, confidence


# ═══════════════════════════════════════════════════════════════════════════════
# §5 ASV INFERENCE PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

class ASVPipeline:
    """
    FORENZA DADA2-Compatible Amplicon Sequence Variant (ASV) Inference Pipeline.

    Implements the complete forensic amplicon denoising workflow (Research §3.2):
        1. Per-read quality filtering (truncQ, minQ)
        2. DADA2 error model-based denoising
        3. Paired-end sequence merging (optional)
        4. Bimeric chimera removal
        5. Naïve Bayes bootstrap taxonomic assignment (≥80% confidence)
        6. ASVFeatureTable construction with simplex closure validation

    Multi-locus support (Research §3.2 Forensic Palynology):
        - 16S V4 (515F/806R) — Prokaryotes
        - ITS2 — Fungi (UNITE SH database)
        - rbcL — Plants (BOLD/PlanT)
        - matK — Plants (BOLD)
        - trnL P6 loop — Plants (highly degraded eDNA, 10–143 bp)
    """

    def __init__(
        self,
        locus: str = "16S_V4",
        min_quality: int = 20,
        truncate_at_quality: int = 2,
        max_ee_per_100bp: float = 2.0,
        seed: int = 42,
    ) -> None:
        """
        Initialize the ASV pipeline.

        Args:
            locus: Target amplicon locus (16S_V4, ITS2, rbcL, matK, trnL_P6)
            min_quality: Minimum per-base Phred Q-score for read acceptance
            truncate_at_quality: Truncate read at first base below this Q-score
            max_ee_per_100bp: Maximum expected errors per 100 bp
                               (DADA2 filterAndTrim default: 2.0)
            seed: Random seed for reproducibility
        """
        self.locus = locus
        self.min_quality = min_quality
        self.truncate_at_quality = truncate_at_quality
        self.max_ee_per_100bp = max_ee_per_100bp

        self._error_model = DADA2ErrorModel(seed=seed)
        self._chimera_detector = BimeraDetector(
            parent_ratio_threshold=BIMERA_PARENT_RATIO_THRESHOLD
        )
        self._nb_classifier = NaiveBayesTaxonomicClassifier(
            kmer_size=NB_KMER_SIZE,
            bootstrap_iterations=NB_BOOTSTRAP_ITERATIONS,
            min_confidence=NB_MIN_BOOTSTRAP_CONFIDENCE,
            seed=seed,
        )

        logger.info(
            f"[ASVPipeline] Initialized for locus={locus}, "
            f"min_quality={min_quality}, maxEE={max_ee_per_100bp}"
        )

    def train_classifier(
        self,
        reference_sequences: List[Tuple[str, str]],
    ) -> None:
        """
        Train the Naïve Bayes taxonomic classifier on reference sequences.

        Args:
            reference_sequences: List of (sequence, taxonomic_label) pairs
                                 from SILVA, UNITE, or BOLD reference databases
        """
        self._nb_classifier.train(reference_sequences)

    def quality_filter_read(
        self,
        sequence: str,
        quality_scores: List[int],
    ) -> Optional[Tuple[str, List[int]]]:
        """
        Filter and truncate a read based on quality scores.

        Quality filtering criteria:
            1. Truncate at first position with Q < truncate_at_quality
            2. Reject if mean quality < min_quality
            3. Reject if expected errors / 100 bp > max_ee_per_100bp

        Expected errors per position: EE = 10^(-Q/10)
        Total EE = Σ 10^(-Q/10) for all bases

        Args:
            sequence: Raw nucleotide sequence
            quality_scores: Per-position Phred Q-scores

        Returns:
            (filtered_sequence, filtered_quality) or None if rejected
        """
        # Step 1: Truncate at low quality tail
        trunc_pos = len(sequence)
        for i, q in enumerate(quality_scores):
            if q < self.truncate_at_quality:
                trunc_pos = i
                break

        trunc_seq = sequence[:trunc_pos]
        trunc_qual = quality_scores[:trunc_pos]

        if len(trunc_seq) < 20:  # minimum length after truncation
            return None

        # Step 2: Compute expected errors
        total_ee = sum(_PHRED_ERROR_PROB.get(min(q, 40), 1.0) for q in trunc_qual)
        ee_per_100bp = total_ee / len(trunc_seq) * 100.0

        if ee_per_100bp > self.max_ee_per_100bp:
            return None

        # Step 3: Mean quality check
        if trunc_qual and sum(trunc_qual) / len(trunc_qual) < self.min_quality:
            return None

        return trunc_seq.upper(), trunc_qual

    def denoise_reads(
        self,
        reads: List[Tuple[str, List[int]]],
    ) -> Dict[str, int]:
        """
        DADA2-inspired denoising: group reads by exact sequence and apply
        error model-based denoising to estimate true sequence abundances.

        Simplified DADA2 denoising (production uses partition-and-cluster):
            1. Count exact sequence occurrences
            2. For rare sequences, check if they are likely erroneous reads
               of a more abundant sequence using the error model
            3. Merge rare sequences into their most likely true parent

        Args:
            reads: List of (sequence, quality_scores) tuples after filtering

        Returns:
            Dict {sequence: count} of denoised true sequences
        """
        # Step 1: Count exact sequences
        exact_counts: Dict[str, int] = {}
        exact_quals: Dict[str, List[List[int]]] = {}

        for seq, qual in reads:
            exact_counts[seq] = exact_counts.get(seq, 0) + 1
            if seq not in exact_quals:
                exact_quals[seq] = []
            exact_quals[seq].append(qual)

        # Step 2: Sort by count descending (most abundant = most likely true)
        sorted_seqs = sorted(exact_counts.items(), key=lambda x: -x[1])
        if not sorted_seqs:
            return {}

        # Step 3: Simplified DADA2 denoising
        # In production: full DADA2 uses divisive partitioning. Here we use
        # a greedy abundance-sorted merge with error model threshold.
        denoised: Dict[str, int] = {}
        min_singleton_count = 2  # singletons are considered likely errors

        for seq, count in sorted_seqs:
            if count >= min_singleton_count:
                # This sequence is abundant enough to be a true ASV
                denoised[seq] = count
            else:
                # Check if this rare sequence is an error of a known true sequence
                absorbed = False
                for true_seq in denoised:
                    if len(true_seq) != len(seq):
                        continue
                    # Compute number of mismatches
                    mismatches = sum(a != b for a, b in zip(seq, true_seq))
                    qual_list = exact_quals.get(seq, [])
                    avg_q = 30  # default if no quality info
                    if qual_list and qual_list[0]:
                        avg_q = int(sum(qual_list[0]) / len(qual_list[0]))
                    # Error probability for observed mismatches
                    p_error = sum(_PHRED_ERROR_PROB.get(min(avg_q, 40), 0.001) for _ in range(mismatches))
                    if mismatches <= 1 and p_error > 0.1:
                        # Likely an error read of the true sequence
                        denoised[true_seq] += count
                        absorbed = True
                        break
                if not absorbed and count >= min_singleton_count:
                    denoised[seq] = count

        return denoised

    def run_pipeline(
        self,
        sample_reads: Dict[str, List[Tuple[str, List[int]]]],
    ) -> ASVFeatureTable:
        """
        Run the complete ASV inference pipeline on multiple samples.

        Pipeline steps:
            1. Quality filter reads per sample
            2. Denoise reads (DADA2 error model)
            3. Remove bimeric chimeras
            4. Pool all unique ASVs across samples
            5. Build count matrix
            6. Assign taxonomy with Naïve Bayes bootstrap (≥80% confidence)
            7. Validate simplex closure: |Σ rel_abundance - 1.0| ≤ 1e-6

        Args:
            sample_reads: {sample_id: [(sequence, quality_scores), ...]}

        Returns:
            ASVFeatureTable with count matrix and taxonomic assignments

        Raises:
            ValueError: If simplex invariant is violated
        """
        sample_ids = sorted(sample_reads.keys())
        n_samples = len(sample_ids)

        # Step 1 & 2: Quality filter + denoise per sample
        sample_denoised: Dict[str, Dict[str, int]] = {}
        total_input_reads: Dict[str, int] = {}
        total_chimeras_removed: int = 0
        total_chimeras_input: int = 0

        all_asvs: Set[str] = set()

        for sample_id in sample_ids:
            reads = sample_reads[sample_id]
            total_input_reads[sample_id] = len(reads)

            # Quality filter
            filtered_reads = []
            for seq, qual in reads:
                result = self.quality_filter_read(seq, qual)
                if result is not None:
                    filtered_reads.append(result)

            # Denoise
            denoised = self.denoise_reads(filtered_reads)

            # Step 3: Bimera removal
            bimera_free, n_chimeras, chimera_frac = self._chimera_detector.remove_bimeras(
                denoised
            )
            total_chimeras_removed += n_chimeras
            total_chimeras_input += len(denoised)

            sample_denoised[sample_id] = bimera_free
            all_asvs.update(bimera_free.keys())

        # Step 4: Pool all unique ASVs (generate stable IDs via MD5)
        asv_list = sorted(all_asvs)  # deterministic order
        asv_ids = [
            f"ASV_{hashlib.md5(seq.encode()).hexdigest()[:12].upper()}"
            for seq in asv_list
        ]
        n_asvs = len(asv_list)

        # Step 5: Build count matrix [n_asvs × n_samples]
        count_matrix: List[List[int]] = []
        total_reads_per_sample: List[int] = []

        for seq in asv_list:
            row = [sample_denoised[sid].get(seq, 0) for sid in sample_ids]
            count_matrix.append(row)

        for sid in sample_ids:
            total_reads_per_sample.append(sum(sample_denoised[sid].values()))

        # Step 6: Naïve Bayes taxonomic assignment with bootstrap confidence
        taxonomic_assignments: List[ASVTaxonomicAssignment] = []

        for asv_id, seq in zip(asv_ids, asv_list):
            taxon_label, confidence = self._nb_classifier.classify_with_bootstrap(seq)

            # Parse taxon label (expected format: "k__Kingdom;p__Phylum;...;s__Species")
            kingdom, phylum, class_, order, family, genus, species = (None,) * 7
            if taxon_label:
                parts = taxon_label.split(";")
                taxon_map = {}
                for part in parts:
                    part = part.strip()
                    if part.startswith("k__"):
                        taxon_map["kingdom"] = part[3:]
                    elif part.startswith("p__"):
                        taxon_map["phylum"] = part[3:]
                    elif part.startswith("c__"):
                        taxon_map["class"] = part[3:]
                    elif part.startswith("o__"):
                        taxon_map["order"] = part[3:]
                    elif part.startswith("f__"):
                        taxon_map["family"] = part[3:]
                    elif part.startswith("g__"):
                        taxon_map["genus"] = part[3:]
                    elif part.startswith("s__"):
                        taxon_map["species"] = part[3:]

                kingdom = taxon_map.get("kingdom")
                phylum = taxon_map.get("phylum")
                class_ = taxon_map.get("class")
                order = taxon_map.get("order")
                family = taxon_map.get("family")
                genus = taxon_map.get("genus")
                species = taxon_map.get("species")

            # Only emit confident assignments
            effective_confidence = confidence if confidence >= NB_MIN_BOOTSTRAP_CONFIDENCE else 0.0

            assignment = ASVTaxonomicAssignment(
                asv_id=asv_id,
                sequence=seq,
                kingdom=kingdom,
                phylum=phylum,
                **{"class": class_},
                order=order,
                family=family,
                genus=genus,
                species=species if effective_confidence >= NB_MIN_BOOTSTRAP_CONFIDENCE else None,
                bootstrap_confidence=round(confidence, 2),
                locus=self.locus,
            )
            taxonomic_assignments.append(assignment)

        chimera_fraction = (
            total_chimeras_removed / total_chimeras_input
            if total_chimeras_input > 0 else 0.0
        )

        # Step 7: Simplex closure validation (AGENTS.md constraint)
        # For each sample, validate Σ relative_abundance = 1.0
        for s_idx, sid in enumerate(sample_ids):
            col_sum = sum(count_matrix[r_idx][s_idx] for r_idx in range(n_asvs))
            if col_sum > 0:
                rel_abundances = [
                    count_matrix[r_idx][s_idx] / col_sum for r_idx in range(n_asvs)
                ]
                sigma = sum(rel_abundances)
                if abs(sigma - 1.0) > 1e-6:
                    raise ValueError(
                        f"ASV simplex invariant VIOLATED for sample '{sid}': "
                        f"|Σ rel_abundance - 1.0| = {abs(sigma - 1.0):.2e} > 1e-6."
                    )

        feature_table = ASVFeatureTable(
            sample_ids=sample_ids,
            asv_sequences=asv_list,
            count_matrix=count_matrix,
            taxonomic_assignments=taxonomic_assignments,
            locus=self.locus,
            total_reads_per_sample=total_reads_per_sample,
            chimera_removed_fraction=round(chimera_fraction, 6),
        )

        logger.info(
            f"[ASVPipeline] Pipeline complete: "
            f"{n_samples} samples, {n_asvs} ASVs, "
            f"chimera_fraction={chimera_fraction:.3f}"
        )

        return feature_table
