"""
FORENZA — Metagenomic Domain Schemas (Phase 1.1)
=================================================

Pydantic v2 domain data contracts for all metagenomic and eDNA taxonomic
classification workflows.

Mathematical constants from research specification (Section 1.1–1.6):
    - k = 35  (canonical k-mer length, Kraken 2)
    - m = 31  (minimizer length, Kraken 2)
    - k_uniq_threshold = 2000  (KrakenUniq horizontal coverage cutoff)
    - Confidence threshold C ∈ [0, 1]  (default 0.0)

All schemas use ConfigDict(protected_namespaces=()) to suppress Pydantic v2
'model_' namespace warnings per AGENTS.md directive.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field, ConfigDict, field_validator


# ═══════════════════════════════════════════════════════════════════════════════
# §1 TAXONOMIC RANK HIERARCHY
# ═══════════════════════════════════════════════════════════════════════════════

class TaxonomicRank(str, Enum):
    """
    Standard NCBI / GTDB taxonomic rank enumeration.

    Includes SGB (Species-level Genome Bin) specific to MetaPhlAn 4 GTDB
    marker catalog (>26,900 bins across ~1 million microbial genomes).
    """
    DOMAIN = "DOMAIN"
    PHYLUM = "PHYLUM"
    CLASS = "CLASS"
    ORDER = "ORDER"
    FAMILY = "FAMILY"
    GENUS = "GENUS"
    SPECIES = "SPECIES"
    STRAIN = "STRAIN"
    SGB = "SGB"        # Species-level Genome Bin (MetaPhlAn 4 / GTDB-specific)
    UNCLASSIFIED = "UNCLASSIFIED"


# ═══════════════════════════════════════════════════════════════════════════════
# §2 TAXONOMY TREE NODE
# ═══════════════════════════════════════════════════════════════════════════════

class TaxonNode(BaseModel):
    """
    Single node in the rooted NCBI taxonomy DAG.

    Used in Kraken 2 LCA traversal (Section 1.1, Weighted LCA Traversal).
    Each node stores its weight (number of minimizers mapping to this taxon
    or descendants) for path scoring.
    """
    model_config = ConfigDict(protected_namespaces=())

    taxid: int = Field(..., description="NCBI Taxonomy Identifier", ge=1)
    scientific_name: str = Field(..., description="Scientific name (Latin binomial or clade name)")
    rank: TaxonomicRank = Field(..., description="Taxonomic rank of this node")
    parent_taxid: Optional[int] = Field(None, description="Parent node TaxID; None for root (taxid=1)")
    lineage_path: str = Field(
        default="",
        description="Pipe-delimited lineage string, e.g. 'k__Bacteria|p__Proteobacteria|...|s__E_coli'"
    )
    phylo_depth: int = Field(
        default=0,
        description="Distance from root node in the NCBI taxonomy tree",
        ge=0
    )
    weight: int = Field(
        default=0,
        description="Number of minimizers mapping to this taxon or any descendant (Kraken 2 LCA weight)",
        ge=0
    )


# ═══════════════════════════════════════════════════════════════════════════════
# §3 RAW SEQUENCING READ
# ═══════════════════════════════════════════════════════════════════════════════

class MetagenomicRead(BaseModel):
    """
    Individual sequencing read from FastQ/FASTA metagenomic or eDNA input.

    Supports both shotgun metagenomic and targeted amplicon (16S/ITS/rbcL)
    reads. The kmer_hashes list holds canonical k-mer (k=35) hash values
    extracted via 2-bit encoding:
        A=00, C=01, G=10, T=11  (Research §1.1 Minimizer-Based Indexing)
    """
    model_config = ConfigDict(protected_namespaces=())

    read_id: str = Field(..., description="Unique read identifier from FastQ header")
    sequence: str = Field(..., description="Nucleotide sequence (ACGT + N for ambiguous)")
    quality_scores: Optional[List[int]] = Field(
        None,
        description="Phred quality scores (Q-score array), None for FASTA inputs"
    )
    length: int = Field(..., description="Read length in base pairs", ge=1)
    kmer_hashes: List[int] = Field(
        default_factory=list,
        description="Canonical k-mer hash values (k=35, 2-bit encoded) extracted from this read"
    )
    is_paired: bool = Field(
        default=False,
        description="True if this read is part of a paired-end library"
    )
    pair_read_id: Optional[str] = Field(
        None,
        description="Mate read identifier for paired-end libraries"
    )

    @field_validator("sequence")
    @classmethod
    def validate_sequence(cls, v: str) -> str:
        """Allow only standard IUPAC nucleotide characters."""
        allowed = set("ACGTNacgtn")
        invalid = set(v) - allowed
        if invalid:
            raise ValueError(f"Sequence contains invalid nucleotide characters: {invalid}")
        return v.upper()


# ═══════════════════════════════════════════════════════════════════════════════
# §4 MINIMIZER HASH ENTRY (Compact Hash Table / CHT)
# ═══════════════════════════════════════════════════════════════════════════════

class KmerHashEntry(BaseModel):
    """
    Single entry in the Kraken 2 Compact Hash Table (CHT).

    Minimizer-based indexing (Research §1.1):
        Minimizer(W_k) = min_{0≤j≤k-m}{ hash(m-mer_j) }
    where k=35, m=31, sliding window size = k - m + 1 = 5.

    The minimizer_hash maps directly to a specific NCBI TaxID in the CHT.
    """
    model_config = ConfigDict(protected_namespaces=())

    minimizer_hash: int = Field(
        ...,
        description="64-bit hash of the minimizer m-mer (m=31); key in the CHT"
    )
    window_offset: int = Field(
        ...,
        description="Position of the minimizer window within the parent k-mer (0-indexed)",
        ge=0
    )
    mapped_taxid: int = Field(
        ...,
        description="NCBI TaxID to which this minimizer maps (LCA of all sequences sharing this minimizer)",
        ge=1
    )
    k_uniq_count: int = Field(
        default=1,
        description="Count of unique minimizers supporting this TaxID (KrakenUniq HyperLogLog counter)",
        ge=0
    )


# ═══════════════════════════════════════════════════════════════════════════════
# §5 CLASSIFIER ENGINE ENUM & CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

class ClassifierEngine(str, Enum):
    """
    Supported taxonomic classification engine selection.

    Benchmark matrix from Research §1.6:
        KRAKEN2:    Minimizer Hash Table, 50-100 GB RAM
        KRAKENUNIQ: Hash + HyperLogLog, 60-120 GB RAM
        BRACKEN:    Bayesian Re-estimation, <1 GB RAM
        METAPHLAN4: Bowtie2 Marker Index, 4-8 GB RAM
        CENTRIFUGE: Compressed BWT/FM-Index, 4-8 GB RAM
        SOURMASH:   FracMinHash Sketch, <2 GB RAM
        KAIJU:      Protein 6-Frame FM-Index, 12-120 GB RAM
    """
    KRAKEN2 = "KRAKEN2"
    KRAKENUNIQ = "KRAKENUNIQ"
    BRACKEN = "BRACKEN"
    METAPHLAN4 = "METAPHLAN4"
    CENTRIFUGE = "CENTRIFUGE"
    SOURMASH = "SOURMASH"
    KAIJU = "KAIJU"


class ClassifierConfig(BaseModel):
    """
    Configuration parameters for a specific classifier run.

    Confidence threshold C (Research §1.7 Kraken2 Confidence Filtering):
        k_path(T) / k_total ≥ C
    where C=0.0 maximizes sensitivity; C∈[0.1, 0.5] suppresses false positives.

    KrakenUniq spurious artifact filter (Research §1.7):
        k_uniq ≥ 2,000 eliminates >99% false-positive assignments.

    sourmash FracMinHash scale factor s=1/H means retain all k-mers
    with hash < H_threshold (deterministic subsampling fraction 1/scaled).
    """
    model_config = ConfigDict(protected_namespaces=())

    engine: ClassifierEngine = Field(
        default=ClassifierEngine.KRAKEN2,
        description="Selected taxonomic classification engine"
    )
    confidence_threshold: float = Field(
        default=0.0,
        description=(
            "Kraken 2 confidence C ∈ [0,1]. A read is assigned taxon T iff "
            "k_path(T)/k_total ≥ C. Default 0.0 maximizes sensitivity."
        ),
        ge=0.0,
        le=1.0
    )
    min_k_uniq: int = Field(
        default=2000,
        description=(
            "KrakenUniq minimum unique k-mer cardinality per taxon. "
            "Taxa with k_uniq < 2,000 are flagged as potential artifacts. "
            "(Research §1.7: eliminates >99%% false positives in low-biomass enviro metagenomes)"
        ),
        ge=0
    )
    scale_factor: int = Field(
        default=1000,
        description=(
            "sourmash FracMinHash scale factor s. Fraction retained = 1/scale_factor. "
            "Default 1000 → ~0.1%% of k-mers sampled."
        ),
        ge=1
    )
    kmer_length: int = Field(
        default=35,
        description="k-mer length k (Kraken 2 default k=35)",
        ge=15,
        le=63
    )
    minimizer_length: int = Field(
        default=31,
        description="Minimizer length m (Kraken 2 default m=31, must be ≤ kmer_length)",
        ge=10,
        le=63
    )
    read_length: int = Field(
        default=150,
        description="Sequencing read length l (Bracken simulation parameter)",
        ge=50
    )
    reference_db: str = Field(
        default="STANDARD",
        description="Reference database identifier (STANDARD, PLUS_PFP, GTDB, SILVA, UNITE, BOLD)"
    )
    min_bracken_threshold: int = Field(
        default=10,
        description="Bracken minimum read count threshold t for species inclusion",
        ge=1
    )

    @field_validator("minimizer_length")
    @classmethod
    def validate_minimizer_leq_kmer(cls, v: int, info) -> int:
        """Enforce m ≤ k (minimizer cannot exceed k-mer length)."""
        k = info.data.get("kmer_length", 35)
        if v > k:
            raise ValueError(
                f"minimizer_length ({v}) must be ≤ kmer_length ({k}). "
                f"Research spec: m=31 ≤ k=35."
            )
        return v


# ═══════════════════════════════════════════════════════════════════════════════
# §6 TAXONOMIC PROFILE OUTPUT
# ═══════════════════════════════════════════════════════════════════════════════

class KReportNode(BaseModel):
    """
    Single node in the Kraken 2 / Bracken hierarchical report (.kreport).

    Standard 6-column .kreport format (Research §4.4):
        pct_total  | cum_reads | direct_reads | rank_code | taxid | name
    """
    model_config = ConfigDict(protected_namespaces=())

    pct_total: float = Field(
        ...,
        description="Percentage of total reads covered by this subtree clade",
        ge=0.0,
        le=100.0
    )
    cumulative_reads: int = Field(
        ...,
        description="Number of reads covered by the entire subtree (clade count)",
        ge=0
    )
    direct_reads: int = Field(
        ...,
        description="Number of reads assigned directly to this taxon node",
        ge=0
    )
    rank_code: str = Field(
        ...,
        description="Single-character rank code: U, R, D, K, P, C, O, F, G, S, S1"
    )
    taxid: int = Field(
        ...,
        description="NCBI TaxID of this node",
        ge=0
    )
    name: str = Field(
        ...,
        description="Scientific name with leading spaces indicating tree depth"
    )
    k_uniq: Optional[int] = Field(
        None,
        description="KrakenUniq unique k-mer count (only present for KrakenUniq .kreport)"
    )
    is_artifact_flagged: bool = Field(
        default=False,
        description="True if k_uniq < 2,000 threshold triggered artifact flag"
    )


class TaxonomicProfile(BaseModel):
    """
    Complete classifier output for a single metagenomic / eDNA sample.

    Contains both raw read statistics and hierarchical taxonomic assignments.
    Unclassified fraction: F_unclass = N_unclass / N_total (Research §3, Failure Mode 1).
    In forensic soil metagenomics, F_unclass typically 70%–95% against standard RefSeq.
    """
    model_config = ConfigDict(protected_namespaces=())

    sample_id: str = Field(..., description="Unique sample/case identifier")
    engine_used: ClassifierEngine = Field(..., description="Classifier engine that produced this profile")
    reference_db: str = Field(..., description="Reference database used for classification")
    total_reads: int = Field(..., description="Total input reads submitted for classification", ge=0)
    classified_reads: int = Field(..., description="Reads assigned to any taxon", ge=0)
    unclassified_reads: int = Field(..., description="Reads with no database match", ge=0)
    unclassified_fraction: float = Field(
        ...,
        description="F_unclass = N_unclass / N_total (Research §3: typically 0.70–0.95 for soil)",
        ge=0.0,
        le=1.0
    )
    kreport_nodes: List[KReportNode] = Field(
        default_factory=list,
        description="Hierarchical .kreport taxonomy nodes sorted by cumulative read count"
    )
    abundance_vector: Dict[int, float] = Field(
        default_factory=dict,
        description="taxid → relative abundance fraction (sum = 1.0 at the reported taxonomic level)"
    )
    processing_time_seconds: float = Field(
        default=0.0,
        description="Wall-clock processing time in seconds",
        ge=0.0
    )
    notes: str = Field(
        default="",
        description="Free-text annotations (e.g., high unclassified fraction warnings)"
    )

    @field_validator("unclassified_fraction")
    @classmethod
    def validate_unclassified_consistency(cls, v: float, info) -> float:
        """Cross-validate that unclassified_fraction matches read counts."""
        total = info.data.get("total_reads", 0)
        unclassified = info.data.get("unclassified_reads", 0)
        if total > 0:
            expected = unclassified / total
            if abs(expected - v) > 1e-4:
                raise ValueError(
                    f"unclassified_fraction ({v:.6f}) inconsistent with "
                    f"unclassified_reads/total_reads ({expected:.6f}). "
                    f"Difference {abs(expected - v):.2e} exceeds 1e-4 tolerance."
                )
        return v


# ═══════════════════════════════════════════════════════════════════════════════
# §7 AMPLICON SEQUENCE VARIANT (ASV) FEATURE TABLE
# ═══════════════════════════════════════════════════════════════════════════════

class ASVTaxonomicAssignment(BaseModel):
    """
    Taxonomic assignment for a single Amplicon Sequence Variant (ASV).

    Generated by DADA2-compatible ASV inference (Research §3.2):
        - Denoising: DADA2 / Deblur in QIIME 2
        - Assignment: Naïve Bayes feature-classifier with bootstrap confidence ≥ 80%
    """
    model_config = ConfigDict(protected_namespaces=())

    asv_id: str = Field(..., description="Unique ASV identifier (typically a MD5/SHA hash of the sequence)")
    sequence: str = Field(..., description="Exact denoised ASV nucleotide sequence")
    kingdom: Optional[str] = Field(None, description="Kingdom-level assignment")
    phylum: Optional[str] = Field(None, description="Phylum-level assignment")
    class_: Optional[str] = Field(None, alias="class", description="Class-level assignment")
    order: Optional[str] = Field(None, description="Order-level assignment")
    family: Optional[str] = Field(None, description="Family-level assignment")
    genus: Optional[str] = Field(None, description="Genus-level assignment")
    species: Optional[str] = Field(None, description="Species-level assignment (if achievable)")
    bootstrap_confidence: float = Field(
        ...,
        description="Naïve Bayes bootstrap confidence score ∈ [0, 100]. ≥80 considered reliable.",
        ge=0.0,
        le=100.0
    )
    locus: str = Field(
        default="16S_V4",
        description="Amplicon locus (16S_V4, 16S_V3V4, ITS1, ITS2, rbcL, matK, trnL_P6, 18S_V4)"
    )

    model_config = ConfigDict(populate_by_name=True, protected_namespaces=())


class ASVFeatureTable(BaseModel):
    """
    QIIME 2-compatible ASV Amplicon Sequence Variant feature table.

    Rows = ASVs, Columns = Sample IDs, Values = read counts.
    Bootstrap confidence threshold ≥ 80% for reliable assignments
    (Research §3.2 DADA2 Taxonomic Assignment).
    """
    model_config = ConfigDict(protected_namespaces=())

    sample_ids: List[str] = Field(
        ...,
        description="Ordered list of sample identifiers (columns of count_matrix)"
    )
    asv_sequences: List[str] = Field(
        ...,
        description="Ordered list of exact ASV sequences (rows of count_matrix)"
    )
    count_matrix: List[List[int]] = Field(
        ...,
        description="2D read count matrix [n_asvs × n_samples]; count_matrix[i][j] = reads of ASV_i in Sample_j"
    )
    taxonomic_assignments: List[ASVTaxonomicAssignment] = Field(
        default_factory=list,
        description="Per-ASV taxonomic assignments including bootstrap confidence scores"
    )
    locus: str = Field(
        default="16S_V4",
        description="Amplicon locus targeted in this feature table"
    )
    total_reads_per_sample: List[int] = Field(
        default_factory=list,
        description="Total read counts per sample after denoising and chimera removal"
    )
    chimera_removed_fraction: float = Field(
        default=0.0,
        description="Fraction of reads removed as bimeric chimeras during DADA2 denoising",
        ge=0.0,
        le=1.0
    )

    @field_validator("count_matrix")
    @classmethod
    def validate_matrix_dimensions(cls, v: List[List[int]], info) -> List[List[int]]:
        """Validate count matrix dimensions match ASV and sample lists."""
        n_samples = len(info.data.get("sample_ids", []))
        n_asvs = len(info.data.get("asv_sequences", []))
        if v and len(v) != n_asvs:
            raise ValueError(
                f"count_matrix has {len(v)} rows but asv_sequences has {n_asvs} entries."
            )
        for row in v:
            if len(row) != n_samples:
                raise ValueError(
                    f"count_matrix row has {len(row)} columns but sample_ids has {n_samples} entries."
                )
        return v
