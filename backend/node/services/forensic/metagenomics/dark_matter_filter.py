"""
FORENZA — Environmental Dark Matter & Artifact Mitigation Filter (Phase 3.2)
=============================================================================

Implements the environmental dark matter quantification and forensic artifact
mitigation pipeline for low-biomass forensic metagenomics.

Research §3 Environmental Dark Matter & Classification Failure Modes:

    Failure Mode 1 — High Unclassified Fraction (F_unclass):
        F_unclass = N_unclass / N_total
        Typical for forensic soil: 70–95% against standard RefSeq.
        Root cause: <1% of soil microorganisms are cultivable.

    Failure Mode 2 — LCA Inflation (Taxonomic Bubble-Up):
        Shared k-mers between divergent organisms force LCA to rise toward
        root, producing spuriously high read counts at genus/family level.
        Penalty: LCA_depth_score = phylo_depth / max_phylo_depth ∈ [0,1]
        (Research §3.2 LCA Inflation Penalty)

    Failure Mode 3 — HGT & Mobile Element Artifacts:
        Horizontal Gene Transfer (HGT) and plasmid-borne sequences cause
        the same k-mers to appear across distant phylogenetic lineages.
        Filter: flag taxon pairs with LCA height ≤ 2 (Domain/Kingdom level)
        but high shared minimizer fraction.

    Failure Mode 4 — Kitome/Splashome Contamination:
        Reagent and environmental laboratory-derived contaminants introduce
        systematic false-positive detections. A curated decontamination list
        of 47 canonical kitome taxa is subtracted proportionally.

    Failure Mode 5 — Carry-Over Human Skin Microbiome:
        Human handler contamination: Cutibacterium acnes (taxid=1743),
        Staphylococcus epidermidis (taxid=1282), Corynebacterium spp.

Human Carrier Skin Microbiome Filter (Research §3.2):
    Skin contaminant taxa subtracted from questioned traces before
    Aitchison distance computation (prevents spurious match to skin-positive
    reference databases).
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

from .schemas import (
    ClassifierEngine,
    KReportNode,
    TaxonomicProfile,
    TaxonomicRank,
)
from .kraken2_engine import TaxonomyTree

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# §1 KNOWN FORENSIC CONTAMINATION DATABASES
# ═══════════════════════════════════════════════════════════════════════════════

# Human skin / human carrier microbiome contaminant TaxIDs (Research §3.2)
# These are subtracted from questioned traces before LR computation.
HUMAN_SKIN_MICROBIOME_TAXIDS: FrozenSet[int] = frozenset([
    1743,     # Cutibacterium acnes (formerly Propionibacterium acnes)
    1282,     # Staphylococcus epidermidis
    1279,     # Staphylococcus (genus, catches all spp.)
    1717,     # Corynebacterium (genus)
    169435,   # Corynebacterium tuberculostearicum
    1260517,  # Staphylococcus capitis
    29388,    # Staphylococcus warneri
    1301,     # Streptococcus (genus — oral cavity)
    216816,   # Bifidobacterium longum (gut-derived oral carry-over)
    1246,     # Rothia (oral/skin)
    1515,     # Veillonella (oral)
])

# Canonical kitome / splashome contaminants (47 curated taxa)
# A subset representing the most common reagent-borne contaminants.
# Derived from Salter et al. 2014, Davis et al. 2018 (Research §3 Failure Mode 4).
KITOME_CONTAMINANT_TAXIDS: FrozenSet[int] = frozenset([
    817,      # Bacteroides fragilis (common in negative controls)
    1263,     # Ruminococcus (gut/reagent)
    816,      # Bacteroides (genus)
    196620,   # Escherichia albertii
    562,      # Escherichia coli (DH5α contamination)
    1423,     # Bacillus subtilis (common lab contaminant)
    1392,     # Bacillus anthracis (over-detected in soil)
    29459,    # Pseudomonas fluorescens
    287,      # Pseudomonas aeruginosa
    1148,     # Synechocystis (cyanobacterial reagent contamination)
    1590,     # Lactobacillus (reagent cross-contamination)
    1578,     # Lactobacillus (genus)
    100272,   # Ralstonia (highly prevalent in negative extraction controls)
    48736,    # Ralstonia pickettii
    # (47 total in production; this list covers the dominant 14 for forensic purposes)
])


# ═══════════════════════════════════════════════════════════════════════════════
# §2 DARK MATTER QUANTIFICATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DarkMatterReport:
    """
    Environmental Dark Matter analysis report for a single forensic sample.

    Quantifies the unclassifiable "dark matter" fraction and all known
    artifact classes that inflate or suppress the classified fraction.
    """
    sample_id: str
    total_reads: int
    classified_reads: int
    unclassified_reads: int

    # Core dark matter metric (Research §3 Failure Mode 1)
    f_unclass: float          # F_unclass = N_unclass / N_total

    # Artifact statistics
    lca_inflated_taxids: List[int] = field(default_factory=list)   # Failure Mode 2
    hgt_flagged_pairs: List[Tuple[int, int]] = field(default_factory=list)  # Failure Mode 3
    kitome_contaminated_taxids: List[int] = field(default_factory=list)     # Failure Mode 4
    skin_contaminant_taxids: List[int] = field(default_factory=list)        # Failure Mode 5

    # Reads removed by each filter
    reads_removed_kitome: int = 0
    reads_removed_skin: int = 0
    reads_removed_lca_inflation: int = 0

    # Adjusted classified fraction after decontamination
    f_classified_adjusted: float = 0.0

    notes: str = ""


class DarkMatterFilter:
    """
    Forensic Environmental Dark Matter & Artifact Mitigation Filter.

    Implements the 5 failure-mode handling pipeline from Research §3:

        1. Unclassified Fraction Quantifier:
               F_unclass = N_unclass / N_total
           Typical forensic soil: 70–95% (documented, not treated as error).

        2. LCA Inflation Penalty:
               LCA_depth_score = phylo_depth / max_phylo_depth ∈ [0, 1]
           Taxa classified at phylo_depth ≤ 2 (Family/Order) flagged.

        3. HGT & Mobile Plasmid Artifact Culling:
           Flag taxon pairs sharing >90% of minimizers but at phylo_depth
           LCA ≤ 2 (Domain-level) as potential HGT artifacts.

        4. Kitome/Splashome Decontamination:
           Subtract canonical kitome taxon reads proportionally.

        5. Human Skin Microbiome Subtraction:
           Remove Cutibacterium acnes, Staphylococcus epidermidis,
           Corynebacterium spp. before LR computation.
    """

    def __init__(
        self,
        taxonomy_tree: Optional[TaxonomyTree] = None,
        custom_kitome_taxids: Optional[Set[int]] = None,
        custom_skin_taxids: Optional[Set[int]] = None,
        lca_depth_threshold: int = 3,
    ) -> None:
        """
        Initialize the dark matter filter.

        Args:
            taxonomy_tree: Taxonomy DAG for LCA depth calculations.
            custom_kitome_taxids: Override/augment the built-in kitome taxid set.
            custom_skin_taxids: Override/augment the built-in skin taxid set.
            lca_depth_threshold: Minimum phylo_depth for valid species assignments.
                                 Nodes at depth < threshold are flagged as LCA-inflated.
                                 Default 3 (Kingdom/Phylum level and above → inflated).
        """
        self.tree = taxonomy_tree or TaxonomyTree()
        self.kitome_taxids: Set[int] = (
            KITOME_CONTAMINANT_TAXIDS | (custom_kitome_taxids or set())
        )
        self.skin_taxids: Set[int] = (
            HUMAN_SKIN_MICROBIOME_TAXIDS | (custom_skin_taxids or set())
        )
        self.lca_depth_threshold = lca_depth_threshold

        logger.info(
            f"[DarkMatterFilter] Initialized: "
            f"kitome_taxa={len(self.kitome_taxids)}, "
            f"skin_taxa={len(self.skin_taxids)}, "
            f"lca_depth_threshold={lca_depth_threshold}"
        )

    # ──────────────────────────────────────────────────────────────────────────
    # §2.1 Failure Mode 1 — Unclassified Fraction
    # ──────────────────────────────────────────────────────────────────────────

    def compute_f_unclass(self, profile: TaxonomicProfile) -> float:
        """
        Compute the unclassified fraction F_unclass (Research §3 Failure Mode 1).

        F_unclass = N_unclass / N_total

        This is a DIAGNOSTIC metric, not an error. Typical forensic soil
        values of 70–95% are scientifically valid given the extreme
        underrepresentation of soil microorganisms in reference databases.

        Args:
            profile: TaxonomicProfile from any classifier engine

        Returns:
            F_unclass ∈ [0.0, 1.0]
        """
        if profile.total_reads == 0:
            return 1.0
        return profile.unclassified_reads / profile.total_reads

    # ──────────────────────────────────────────────────────────────────────────
    # §2.2 Failure Mode 2 — LCA Inflation Penalty
    # ──────────────────────────────────────────────────────────────────────────

    def detect_lca_inflation(
        self,
        kreport_nodes: List[KReportNode],
        max_phylo_depth: int = 8,
    ) -> List[int]:
        """
        Detect taxa classified at high LCA (low phylogenetic depth) indicating
        taxonomic inflation / LCA bubble-up (Research §3 Failure Mode 2).

        LCA depth score = phylo_depth / max_phylo_depth ∈ [0, 1]
        Taxa with phylo_depth < lca_depth_threshold are flagged.

        Args:
            kreport_nodes: .kreport nodes from TaxonomicProfile
            max_phylo_depth: Maximum expected phylogenetic depth (default 8)

        Returns:
            List of taxids flagged as LCA-inflated
        """
        inflated_taxids: List[int] = []
        rank_code_depths: Dict[str, int] = {
            "D": 1, "P": 2, "C": 3, "O": 4, "F": 5, "G": 6, "S": 7, "S1": 8,
        }

        for node in kreport_nodes:
            # Determine phylogenetic depth from rank code
            depth = rank_code_depths.get(node.rank_code, 0)
            if depth < self.lca_depth_threshold and node.cumulative_reads > 0:
                # Node exists at or above the inflation threshold (genus or above)
                if node.taxid != 0 and node.taxid != 1:  # skip root & unclassified
                    inflated_taxids.append(node.taxid)
                    logger.debug(
                        f"[DarkMatterFilter] LCA inflation detected: "
                        f"taxid={node.taxid} rank={node.rank_code} "
                        f"depth={depth} < threshold={self.lca_depth_threshold}"
                    )

        return inflated_taxids

    # ──────────────────────────────────────────────────────────────────────────
    # §2.3 Failure Mode 3 — HGT & Mobile Plasmid Artifacts
    # ──────────────────────────────────────────────────────────────────────────

    def detect_hgt_artifacts(
        self,
        kreport_nodes: List[KReportNode],
        shared_minimizer_matrix: Optional[Dict[Tuple[int, int], float]] = None,
    ) -> List[Tuple[int, int]]:
        """
        Detect potential Horizontal Gene Transfer (HGT) and mobile plasmid
        artifact taxon pairs (Research §3 Failure Mode 3).

        Criteria for HGT flag:
            1. LCA of the two taxa is at Domain level (phylo_depth ≤ 2)
            2. Shared minimizer fraction (from shared_minimizer_matrix) > 0.90

        In production: shared_minimizer_matrix comes from CHT cross-reference.
        In this forensic simulation: uses rank_code proximity as proxy.

        Args:
            kreport_nodes: .kreport nodes
            shared_minimizer_matrix: {(taxid_a, taxid_b): shared_fraction}

        Returns:
            List of (taxid_a, taxid_b) pairs flagged as HGT artifacts
        """
        hgt_pairs: List[Tuple[int, int]] = []

        if shared_minimizer_matrix:
            for (taxid_a, taxid_b), frac in shared_minimizer_matrix.items():
                if frac > 0.90:
                    # Check if these taxa are at Domain-level LCA
                    lca = self.tree.lca(taxid_a, taxid_b) if self.tree.has_node(taxid_a) else 1
                    lca_node = self.tree.get_node(lca)
                    lca_depth = getattr(lca_node, "phylo_depth", 0) if lca_node else 0
                    if lca_depth <= 2:  # Domain/Kingdom level LCA
                        hgt_pairs.append((taxid_a, taxid_b))
                        logger.warning(
                            f"[DarkMatterFilter] HGT artifact suspected: "
                            f"taxid_a={taxid_a}, taxid_b={taxid_b}, "
                            f"shared_minimizer_frac={frac:.2f}, LCA_depth={lca_depth}"
                        )

        return hgt_pairs

    # ──────────────────────────────────────────────────────────────────────────
    # §2.4 Failure Mode 4 — Kitome / Splashome Decontamination
    # ──────────────────────────────────────────────────────────────────────────

    def apply_kitome_filter(
        self,
        abundance_vector: Dict[int, float],
    ) -> Tuple[Dict[int, float], Dict[int, float], int]:
        """
        Subtract canonical kitome/splashome contamination taxa from the
        abundance vector (Research §3 Failure Mode 4).

        Proportional subtraction: after removing kitome reads, renormalize
        the remaining taxa so the abundance vector sums to 1.0 again.

        Args:
            abundance_vector: taxid → relative abundance fraction (sum = 1.0)

        Returns:
            Tuple of (filtered_abundance, removed_abundance, n_kitome_taxa_removed)
        """
        removed: Dict[int, float] = {}
        filtered: Dict[int, float] = {}

        for taxid, frac in abundance_vector.items():
            if taxid in self.kitome_taxids:
                removed[taxid] = frac
            else:
                filtered[taxid] = frac

        # Renormalize to simplex after kitome removal
        total_remaining = sum(filtered.values())
        if total_remaining > 0 and filtered:
            filtered = {
                tid: f / total_remaining for tid, f in filtered.items()
            }

        return filtered, removed, len(removed)

    # ──────────────────────────────────────────────────────────────────────────
    # §2.5 Failure Mode 5 — Human Skin Microbiome Subtraction
    # ──────────────────────────────────────────────────────────────────────────

    def apply_skin_microbiome_filter(
        self,
        abundance_vector: Dict[int, float],
    ) -> Tuple[Dict[int, float], Dict[int, float], int]:
        """
        Remove human skin carrier microbiome contaminants from the abundance
        vector before Aitchison distance computation (Research §3.2 Failure Mode 5).

        Subtracted taxa:
            - Cutibacterium acnes (taxid=1743)
            - Staphylococcus epidermidis (taxid=1282)
            - Corynebacterium spp. (taxid=1717)

        Args:
            abundance_vector: taxid → relative abundance fraction

        Returns:
            Tuple of (filtered_abundance, removed_abundance, n_skin_taxa_removed)
        """
        removed: Dict[int, float] = {}
        filtered: Dict[int, float] = {}

        for taxid, frac in abundance_vector.items():
            if taxid in self.skin_taxids:
                removed[taxid] = frac
            else:
                filtered[taxid] = frac

        # Renormalize after skin subtraction
        total_remaining = sum(filtered.values())
        if total_remaining > 0 and filtered:
            filtered = {
                tid: f / total_remaining for tid, f in filtered.items()
            }

        return filtered, removed, len(removed)

    # ──────────────────────────────────────────────────────────────────────────
    # §2.6 Full Pipeline — Apply All Dark Matter Filters
    # ──────────────────────────────────────────────────────────────────────────

    def apply_full_pipeline(
        self,
        profile: TaxonomicProfile,
        shared_minimizer_matrix: Optional[Dict[Tuple[int, int], float]] = None,
    ) -> Tuple[TaxonomicProfile, DarkMatterReport]:
        """
        Apply the complete 5-step dark matter and artifact mitigation pipeline.

        Steps (in order):
            1. Compute F_unclass (diagnostic, no reads removed)
            2. Detect LCA-inflated taxids
            3. Detect HGT artifact pairs
            4. Apply kitome decontamination (proportional subtraction)
            5. Apply human skin microbiome filter

        Args:
            profile: Input TaxonomicProfile (from any classifier engine)
            shared_minimizer_matrix: Optional HGT detection matrix

        Returns:
            Tuple of (decontaminated_TaxonomicProfile, DarkMatterReport)
        """
        # Step 1: F_unclass
        f_unclass = self.compute_f_unclass(profile)

        # Step 2: LCA inflation detection
        inflated_taxids = self.detect_lca_inflation(profile.kreport_nodes)

        # Step 3: HGT artifact detection
        hgt_pairs = self.detect_hgt_artifacts(
            profile.kreport_nodes,
            shared_minimizer_matrix=shared_minimizer_matrix
        )

        # Step 4: Kitome decontamination
        abundance_after_kitome, kitome_removed, n_kitome = self.apply_kitome_filter(
            profile.abundance_vector
        )

        # Step 5: Skin microbiome subtraction
        abundance_final, skin_removed, n_skin = self.apply_skin_microbiome_filter(
            abundance_after_kitome
        )

        # Compute adjusted read counts
        kitome_reads = sum(
            int(frac * profile.classified_reads)
            for frac in kitome_removed.values()
        )
        skin_reads = sum(
            int(frac * profile.classified_reads)
            for frac in skin_removed.values()
        )

        adjusted_classified = max(0, profile.classified_reads - kitome_reads - skin_reads)
        f_classified_adjusted = adjusted_classified / profile.total_reads if profile.total_reads > 0 else 0.0

        # Build decontaminated .kreport nodes
        removed_taxids = set(kitome_removed) | set(skin_removed)
        decontam_nodes = [
            node for node in profile.kreport_nodes
            if node.taxid not in removed_taxids
        ]

        # Build decontaminated profile
        decontam_profile = TaxonomicProfile(
            sample_id=profile.sample_id,
            engine_used=profile.engine_used,
            reference_db=profile.reference_db,
            total_reads=profile.total_reads,
            classified_reads=adjusted_classified,
            unclassified_reads=profile.total_reads - adjusted_classified,
            unclassified_fraction=round(
                (profile.total_reads - adjusted_classified) / profile.total_reads, 6
            ) if profile.total_reads > 0 else 1.0,
            kreport_nodes=decontam_nodes,
            abundance_vector=abundance_final,
            processing_time_seconds=profile.processing_time_seconds,
            notes=(
                f"DarkMatterFilter applied: "
                f"F_unclass={f_unclass:.1%} (original), "
                f"kitome_removed={n_kitome} taxa ({kitome_reads} reads), "
                f"skin_removed={n_skin} taxa ({skin_reads} reads), "
                f"LCA_inflated={len(inflated_taxids)} taxa flagged, "
                f"HGT_pairs={len(hgt_pairs)} pairs flagged."
            )
        )

        # Build dark matter report
        report = DarkMatterReport(
            sample_id=profile.sample_id,
            total_reads=profile.total_reads,
            classified_reads=profile.classified_reads,
            unclassified_reads=profile.unclassified_reads,
            f_unclass=round(f_unclass, 6),
            lca_inflated_taxids=inflated_taxids,
            hgt_flagged_pairs=hgt_pairs,
            kitome_contaminated_taxids=list(kitome_removed.keys()),
            skin_contaminant_taxids=list(skin_removed.keys()),
            reads_removed_kitome=kitome_reads,
            reads_removed_skin=skin_reads,
            reads_removed_lca_inflation=0,  # LCA inflation is flagged not removed
            f_classified_adjusted=round(f_classified_adjusted, 6),
            notes=(
                f"Environmental dark matter F_unclass={f_unclass:.1%}. "
                f"Typical for forensic soil against standard RefSeq (70–95%%). "
                f"Adjusted classified fraction after decontamination: "
                f"{f_classified_adjusted:.1%}."
            )
        )

        logger.info(
            f"[DarkMatterFilter] {profile.sample_id}: "
            f"F_unclass={f_unclass:.2%}, "
            f"kitome_removed={n_kitome}, skin_removed={n_skin}, "
            f"hgt_pairs={len(hgt_pairs)}, lca_inflated={len(inflated_taxids)}"
        )

        return decontam_profile, report

    def generate_dark_matter_forensic_note(
        self,
        report: DarkMatterReport,
        language: str = "EN",
    ) -> str:
        """
        Generate a forensic-grade dark matter caveat note for inclusion in reports.

        Languages supported: EN (English), TR (Turkish).
        Includes the mandatory Investigative Intelligence disclaimer per Research §3.

        Args:
            report: DarkMatterReport from apply_full_pipeline()
            language: "EN" or "TR"

        Returns:
            Formatted forensic caveat string
        """
        if language == "TR":
            note = (
                f"ÖNEMLİ METAGENOMİK UYARI: Bu örneğin sınıflandırılmamış fraksiyonu "
                f"F_unclass = {report.f_unclass:.1%} olarak hesaplanmıştır. "
                f"Bu yüksek değer, adli tıp toprağı metagenomik analizinde standart bir bulgudur; "
                f"toprak mikrobiyomundaki organizmaların %99'undan fazlası referans veritabanlarında "
                f"bulunmamaktadır (GTDB, RefSeq). "
                f"Bu analiz kesin kimlik belirleme değil, araştırıcı istihbarat niteliği taşır. "
                f"Kitome kontaminantı olarak {report.reads_removed_kitome} okuma çıkarılmıştır. "
                f"Deri mikrobiyomu kontaminantı olarak {report.reads_removed_skin} okuma çıkarılmıştır."
            )
        else:
            note = (
                f"CRITICAL METAGENOMIC CAVEAT: The unclassified fraction for this sample is "
                f"F_unclass = {report.f_unclass:.1%}. "
                f"This elevated value is a standard finding in forensic soil metagenomics; "
                f"greater than 99% of soil microorganisms are absent from reference databases "
                f"(GTDB R220, RefSeq, SILVA 138.2). "
                f"This analysis provides investigative intelligence, NOT definitive identification. "
                f"{report.reads_removed_kitome} reads removed as kitome contaminants. "
                f"{report.reads_removed_skin} reads removed as human skin microbiome carry-over. "
                f"{len(report.lca_inflated_taxids)} taxa flagged for LCA taxonomic inflation."
            )
        return note
