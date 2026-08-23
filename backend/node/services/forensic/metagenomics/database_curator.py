"""
FORENZA — Multi-Domain Reference Database Curators (Phase 3.1)
==============================================================

Implements reference database management for all metagenomic domains:
    - Prokaryotes (Bacteria & Archaea): GTDB Release 220 + RefSeq microbial
    - Fungi: UNITE v10 Species Hypotheses (SH, 97% & 99% thresholds)
    - Eukaryota & Plants: SILVA 138.2 (16S/18S SSU, 23S/28S LSU)
                          PlanT / BOLD / Bellcord (rbcL, matK, trnL P6 loop)

Research §2 Reference Databases:
    Coverage gaps for forensic soil (§2.2):
        - <1% of soil microorganisms are cultivable
        - Standard RefSeq fails dominant soil phyla:
          Acidobacteriota, Verrucomicrobiota, Planctomycetota, CPR lineages
        - Plant nuclear genomes missing (Pinus >20-30 Gb genome)
        - Barcode repositories essential: rbcL, matK, trnL P6 loop, ITS2

Research §3.2 Forensic Palynology:
    Multi-locus plant barcoding strategy:
        ITS2 (nuclear): high species discrimination, rapid substitution
        rbcL (chloroplastic): universal, lower species resolution
        matK (chloroplastic): high variation, variable primer binding
        trnL P6 loop (chloroplastic): optimized for degraded eDNA (<150 bp)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .schemas import TaxonomicRank

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# §1 DATABASE IDENTIFIERS & METADATA
# ═══════════════════════════════════════════════════════════════════════════════

class ReferenceDatabaseType(str, Enum):
    """Supported forensic metagenomic reference databases."""
    GTDB_R220 = "GTDB_R220"        # GTDB Release 220: Bacteria & Archaea SGBs
    REFSEQ_MICROBIAL = "REFSEQ_MICROBIAL"  # NCBI RefSeq microbial genomes
    SILVA_138_2_SSU = "SILVA_138_2_SSU"    # SILVA 16S/18S SSU
    SILVA_138_2_LSU = "SILVA_138_2_LSU"    # SILVA 23S/28S LSU
    UNITE_V10_97 = "UNITE_V10_97"   # UNITE v10 97% SH fungal ITS
    UNITE_V10_99 = "UNITE_V10_99"   # UNITE v10 99% SH fungal ITS
    BOLD_PLANT = "BOLD_PLANT"       # BOLD plant barcodes (rbcL, matK, ITS2, COI)
    PLANT_CHR = "PLANT_CHR"         # PlanT chloroplastic barcodes
    BELLCORD = "BELLCORD"           # Bellcord multi-locus barcode library
    NCBI_NR = "NCBI_NR"            # NCBI non-redundant protein (Kaiju)
    PROGENOMES3 = "PROGENOMES3"     # proGenomes 3 curated microbial proteins


class BarcodeLocus(str, Enum):
    """
    Forensic plant & fungal barcoding loci (Research §3.2 & §2.1).

    Multi-locus strategy is required because no single locus resolves
    all land plants (Embryophyta). Each locus has distinct trade-offs.
    """
    ITS2 = "ITS2"           # Nuclear ribosomal: high species discrimination
    RBCL = "rbcL"           # Chloroplast coding: universal, lower species resolution
    MATK = "matK"           # Chloroplast maturase K: high variation, primer issues
    TRNL_P6 = "trnL_P6"    # Chloroplast trnL P6 loop: optimized for degraded eDNA
    ITS1 = "ITS1"           # Fungal nuclear ITS1 region
    V4_16S = "16S_V4"      # Prokaryotic 16S V4 hypervariable region (515F/806R)
    V3V4_16S = "16S_V3V4"  # Prokaryotic 16S V3-V4 region
    V4_18S = "18S_V4"      # Eukaryotic 18S V4 region
    V9_18S = "18S_V9"      # Eukaryotic 18S V9 region
    COI = "COI"             # Cytochrome c Oxidase I (animals/metazoa)


@dataclass
class ReferenceSequenceEntry:
    """
    Single reference sequence entry in a curated forensic database.
    """
    accession: str              # Database accession (e.g., "NR_074513.1")
    taxid: int                  # NCBI TaxID
    scientific_name: str
    rank: TaxonomicRank
    locus: BarcodeLocus         # Target barcoding locus
    sequence: str               # Reference nucleotide sequence
    length_bp: int              # Sequence length in base pairs
    database_version: str       # e.g., "SILVA_138.2", "UNITE_v10", "GTDB_R220"
    species_hypothesis: Optional[str] = None  # UNITE SH identifier (e.g., "SH1234567.10FU")
    sh_similarity: Optional[float] = None     # UNITE SH clustering threshold (0.97 or 0.99)


@dataclass
class ReferenceDatabase:
    """
    Curated forensic reference database for a specific taxonomic domain.

    Maintains an indexed collection of reference sequences for:
        - Taxonomic assignment (BLASTn, VSEARCH, Naïve Bayes)
        - Database coverage metrics for forensic reporting
    """
    db_type: ReferenceDatabaseType
    version: str
    description: str
    target_loci: List[BarcodeLocus] = field(default_factory=list)
    entries: List[ReferenceSequenceEntry] = field(default_factory=list)

    # Indexes for fast lookup
    _taxid_index: Dict[int, List[int]] = field(default_factory=dict, repr=False)
    _accession_index: Dict[str, int] = field(default_factory=dict, repr=False)

    def add_entry(self, entry: ReferenceSequenceEntry) -> None:
        """Add a reference sequence and update indexes."""
        idx = len(self.entries)
        self.entries.append(entry)
        if entry.taxid not in self._taxid_index:
            self._taxid_index[entry.taxid] = []
        self._taxid_index[entry.taxid].append(idx)
        self._accession_index[entry.accession] = idx

    def get_by_taxid(self, taxid: int) -> List[ReferenceSequenceEntry]:
        """Retrieve all entries for a given TaxID."""
        indices = self._taxid_index.get(taxid, [])
        return [self.entries[i] for i in indices]

    def get_by_accession(self, accession: str) -> Optional[ReferenceSequenceEntry]:
        """Retrieve entry by accession number."""
        idx = self._accession_index.get(accession)
        return self.entries[idx] if idx is not None else None

    @property
    def total_sequences(self) -> int:
        return len(self.entries)

    @property
    def unique_taxa(self) -> int:
        return len(self._taxid_index)


# ═══════════════════════════════════════════════════════════════════════════════
# §2 DATABASE CURATOR CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class ForensicDatabaseCurator:
    """
    Multi-Domain Forensic Reference Database Curator.

    Manages curated reference databases for all target organism domains:
        1. Prokaryotes (Bacteria & Archaea): GTDB R220 + RefSeq
        2. Fungi: UNITE v10 Species Hypotheses (97% and 99% thresholds)
        3. Eukaryota & Plants: SILVA 138.2 + PlanT + BOLD + Bellcord

    Research §2 Coverage Framework:
        - GTDB R220: Resolves soil prokaryotic dark matter via MAGs
        - SILVA 138.2: Curated SSU/LSU alignments (secondary-structure aligned)
        - UNITE v10: Fungal SH clustering at 97% and 99% similarity
        - PlanT/BOLD: Plant barcode repositories (rbcL, matK, trnL, ITS2)

    Research §2.2 Environmental Deficit Notes:
        - Acidobacteriota, Verrucomicrobiota, Planctomycetota → underrepresented
          in RefSeq; GTDB MAGs provide better coverage
        - Pinus / angiosperm genomes (>20-30 Gb) → whole-genome absent;
          only chloroplast barcodes available
    """

    def __init__(self) -> None:
        self._databases: Dict[ReferenceDatabaseType, ReferenceDatabase] = {}
        self._initialize_catalog_metadata()

    def _initialize_catalog_metadata(self) -> None:
        """
        Register all supported forensic reference databases with metadata.

        These are metadata-only registrations (no sequences loaded yet).
        Sequences are loaded on demand via load_database().
        """
        catalog = [
            ReferenceDatabase(
                db_type=ReferenceDatabaseType.GTDB_R220,
                version="R220",
                description=(
                    "Genome Taxonomy Database Release 220: Bacterial and Archaeal "
                    "Species-level Genome Bins (SGBs) based on 120 conserved bacterial "
                    "and 53 archaeal marker gene phylogenetics. Covers >26,900 SGBs "
                    "across ~1 million microbial genomes including environmental MAGs. "
                    "Primary solution for forensic soil prokaryotic dark matter. "
                    "(Research §2.1, §1.2)"
                ),
                target_loci=[BarcodeLocus.V4_16S, BarcodeLocus.V3V4_16S],
            ),
            ReferenceDatabase(
                db_type=ReferenceDatabaseType.SILVA_138_2_SSU,
                version="138.2",
                description=(
                    "SILVA Small Sub-Unit ribosomal RNA database. Contains curated "
                    "16S rRNA (prokaryotes) and 18S rRNA (eukaryotes) sequences aligned "
                    "to secondary-structure consensus. Standard reference for amplicon "
                    "metabarcoding classification (515F/806R amplicons). (Research §2.1)"
                ),
                target_loci=[BarcodeLocus.V4_16S, BarcodeLocus.V3V4_16S,
                             BarcodeLocus.V4_18S, BarcodeLocus.V9_18S],
            ),
            ReferenceDatabase(
                db_type=ReferenceDatabaseType.SILVA_138_2_LSU,
                version="138.2",
                description=(
                    "SILVA Large Sub-Unit ribosomal RNA database. Contains curated "
                    "23S rRNA (prokaryotes) and 28S rRNA (eukaryotes) sequences. "
                    "Secondary-structure aligned for phylogenetic consistency. (Research §2.1)"
                ),
                target_loci=[],
            ),
            ReferenceDatabase(
                db_type=ReferenceDatabaseType.UNITE_V10_97,
                version="v10",
                description=(
                    "UNITE Fungal ITS Species Hypotheses (SH) at 97% similarity threshold. "
                    "Contains nuclear ITS1-5.8S-ITS2 sequences for all known fungal taxa. "
                    "Annual releases with SH identifier stability. Primary forensic "
                    "fungal identification database. (Research §2.1)"
                ),
                target_loci=[BarcodeLocus.ITS1, BarcodeLocus.ITS2],
            ),
            ReferenceDatabase(
                db_type=ReferenceDatabaseType.UNITE_V10_99,
                version="v10",
                description=(
                    "UNITE Fungal ITS Species Hypotheses (SH) at 99% similarity threshold. "
                    "Higher resolution than 97% threshold; may split populations but "
                    "provides finer geographic discrimination for forensic soil mycobiome. "
                    "(Research §2.1)"
                ),
                target_loci=[BarcodeLocus.ITS1, BarcodeLocus.ITS2],
            ),
            ReferenceDatabase(
                db_type=ReferenceDatabaseType.BOLD_PLANT,
                version="2024",
                description=(
                    "Barcode Of Life Data System — Plant division. Specimen-vouchered "
                    "plant barcode sequences for rbcL, matK, ITS2, and COI loci. "
                    "Covers angiosperms and gymnosperms for forensic palynology. "
                    "Note: Pinus and large-genome plants are barcode-only; no whole-genome "
                    "sequences available. (Research §2.1, §3.2)"
                ),
                target_loci=[BarcodeLocus.RBCL, BarcodeLocus.MATK,
                             BarcodeLocus.ITS2, BarcodeLocus.COI],
            ),
            ReferenceDatabase(
                db_type=ReferenceDatabaseType.PLANT_CHR,
                version="2024",
                description=(
                    "PlanT chloroplastic barcode library. Optimized for forensic "
                    "palynology applications targeting chloroplast gene markers. "
                    "trnL P6 loop (10-143 bp): optimized for highly degraded eDNA, "
                    "aged forensic exhibits, honey, dust, and ancient soils. "
                    "(Research §3.2)"
                ),
                target_loci=[BarcodeLocus.TRNL_P6, BarcodeLocus.RBCL, BarcodeLocus.MATK],
            ),
        ]

        for db in catalog:
            self._databases[db.db_type] = db
            logger.info(
                f"[DatabaseCurator] Registered: {db.db_type.value} v{db.version} "
                f"({len(db.target_loci)} target loci)"
            )

    def load_database(
        self,
        db_type: ReferenceDatabaseType,
        entries: List[ReferenceSequenceEntry],
    ) -> None:
        """
        Load reference sequences into a registered database.

        Args:
            db_type: Database type identifier
            entries: List of ReferenceSequenceEntry to load
        """
        if db_type not in self._databases:
            raise ValueError(f"Unknown database type: {db_type}")
        db = self._databases[db_type]
        for entry in entries:
            db.add_entry(entry)
        logger.info(
            f"[DatabaseCurator] Loaded {len(entries)} sequences into {db_type.value}. "
            f"Total: {db.total_sequences} sequences, {db.unique_taxa} unique taxa."
        )

    def get_database(self, db_type: ReferenceDatabaseType) -> Optional[ReferenceDatabase]:
        """Retrieve a registered reference database."""
        return self._databases.get(db_type)

    def get_coverage_report(self) -> Dict[str, Any]:
        """
        Generate a forensic database coverage audit report.

        Documents known forensic soil and palynology coverage gaps
        per Research §2.2 (Environmental Representation Deficits).

        Returns:
            Dict with database statistics and forensic coverage notes.
        """
        report: Dict[str, Any] = {
            "databases": {},
            "forensic_soil_coverage_gaps": [
                "Acidobacteriota: underrepresented in RefSeq; partially covered by GTDB R220 MAGs",
                "Verrucomicrobiota: rare in RefSeq; GTDB R220 provides MAG coverage",
                "Planctomycetota: rare in RefSeq; GTDB R220 provides MAG coverage",
                "Candidate Phyla Radiation (CPR): virtually absent from all databases",
                "Soil micro-eukaryotes (nematodes, protozoa, rotifers): limited genomic coverage",
            ],
            "forensic_palynology_coverage_gaps": [
                "Pinus and large gymnosperm genomes (>20-30 Gb): whole-genome absent; barcode only",
                "Most angiosperm taxa: no whole-genome assemblies; rbcL/matK/ITS2 barcode only",
                "Anemophilous pollen: Poaceae and Asteraceae are morphologically and barcoding-uniform",
                "Ancient pollen eDNA: trnL P6 loop only viable locus for <50 bp fragments",
            ],
            "expected_unclassified_fraction": {
                "whole_genome_shotgun_vs_refseq": "70-95%",
                "amplicon_16S_vs_silva": "5-30%",
                "amplicon_ITS_vs_unite": "10-40%",
                "amplicon_rbcL_vs_bold": "20-60%",
            }
        }

        for db_type, db in self._databases.items():
            report["databases"][db_type.value] = {
                "version": db.version,
                "total_sequences": db.total_sequences,
                "unique_taxa": db.unique_taxa,
                "target_loci": [loc.value for loc in db.target_loci],
                "description_summary": db.description[:120] + "...",
            }

        return report

    def validate_unite_sh_assignment(
        self,
        asv_sequence: str,
        similarity_threshold: float = 0.97,
    ) -> List[Tuple[str, str, float]]:
        """
        Validate a fungal ASV against UNITE Species Hypothesis clusters.

        Research §2.1 UNITE SH clustering:
            97% threshold: coarser clusters (morpho-species level)
            99% threshold: finer clusters (cryptic species discrimination)

        Args:
            asv_sequence: Exact ASV nucleotide sequence (ITS1 or ITS2)
            similarity_threshold: 0.97 or 0.99 SH threshold

        Returns:
            List of (SH_identifier, species_name, similarity_score) tuples
            sorted by similarity descending.
        """
        db_type = (ReferenceDatabaseType.UNITE_V10_99
                   if similarity_threshold >= 0.99
                   else ReferenceDatabaseType.UNITE_V10_97)
        db = self._databases.get(db_type)
        if db is None or db.total_sequences == 0:
            return []

        # Simplified similarity scoring (production uses VSEARCH/BLASTn)
        results: List[Tuple[str, str, float]] = []
        query_upper = asv_sequence.upper()

        for entry in db.entries:
            if entry.species_hypothesis:
                ref_upper = entry.sequence.upper()
                # Compute simple overlap score (normalized)
                matches = sum(a == b for a, b in zip(query_upper, ref_upper))
                score = matches / max(len(query_upper), len(ref_upper), 1)
                if score >= similarity_threshold:
                    results.append((
                        entry.species_hypothesis,
                        entry.scientific_name,
                        score,
                    ))

        return sorted(results, key=lambda x: -x[2])
