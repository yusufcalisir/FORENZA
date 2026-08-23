"""
FORENZA — Bracken Bayesian Abundance Re-estimation Engine (Phase 2.2)
======================================================================

Implements the Bracken (Bayesian Reestimation of Abundance after Classification
with KrakEN) species-level re-estimation pipeline.

Problem addressed (Research §1.4):
    Kraken 2 does not generate accurate species-level abundance profiles because
    sequence homology forces non-unique k-mers to be classified at genus/family/
    higher LCA nodes. Bracken probabilistically redistributes these reads to
    species-level leaves.

Mathematical formulation (Research §1.4 Bracken Mathematical Model):

    Precomputed (offline, bracken-build):
        P(G_j | S_i) = P(a read from S_i is classified by Kraken2 at node G_j)

    Bayesian posterior (Bayes' theorem):
        P(S_i | G_j) = P(G_j | S_i) * P(S_i) / Σ_k P(G_j | S_k) * P(S_k)

    Read re-assignment:
        N_hat_{S_i ← G_j} = N_j × P(S_i | G_j)

    Convergence criterion:
        |ΔP| < 1e-6  (iterative update until species priors stabilize)

    Simplex invariant (AGENTS.md):
        |Σ A_i - 1.0| ≤ 1e-6
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
# §1 BRACKEN DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

# Convergence threshold for Bracken iterative update (Research §1.4)
BRACKEN_CONVERGENCE_THRESHOLD: float = 1e-6
BRACKEN_MAX_ITERATIONS: int = 1000


@dataclass
class BrackenSpeciesEntry:
    """
    Bracken species-level re-estimation entry for a single species S_i.

    The conditional probability matrix P(G_j | S_i) is precomputed by
    bracken-build via read simulation and Kraken 2 re-classification.
    """
    taxid: int
    species_name: str
    prior: float = 0.0          # P(S_i): current prior abundance estimate
    reassigned_reads: float = 0.0  # N_hat_{S_i}: total reassigned read count
    # Nested dict: {parent_taxid: P(G_j | S_i)} for read redistribution
    conditional_probs: Dict[int, float] = field(default_factory=dict)


@dataclass
class BrackenAncestorNode:
    """
    Higher-level (genus/family/order) node from which reads are redistributed.

    N_j: reads classified to this ancestor node by Kraken 2.
    candidate_species: TaxIDs of species in this node's subtree with reads ≥ threshold.
    """
    taxid: int
    node_name: str
    classified_reads: int = 0   # N_j from Kraken 2 classification
    candidate_species: List[int] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# §2 BRACKEN ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class BrackenEngine:
    """
    Forensic Bracken Bayesian Read Re-estimation Engine.

    Redistributes reads assigned to higher LCA nodes (genus, family) back
    to species-level leaves using Bayesian probability inference.

    Usage:
        1. Input: Kraken 2 TaxonomicProfile (.kreport nodes)
        2. Load precomputed P(G_j | S_i) matrix (from bracken-build)
        3. Run iterative Bayesian update until |ΔP| < 1e-6
        4. Output: Species-level TaxonomicProfile with reassigned read counts

    Research §1.4: Convergence |ΔP| < 1e-6 across all species priors.
    """

    def __init__(
        self,
        config: Optional[ClassifierConfig] = None,
        convergence_threshold: float = BRACKEN_CONVERGENCE_THRESHOLD,
    ) -> None:
        self.config = config or ClassifierConfig(engine=ClassifierEngine.BRACKEN)
        self.convergence_threshold = convergence_threshold

        # P_matrix[species_taxid][ancestor_taxid] = P(G_j | S_i)
        self._p_matrix: Dict[int, Dict[int, float]] = {}
        # Species registry
        self._species: Dict[int, BrackenSpeciesEntry] = {}
        # Ancestor nodes
        self._ancestors: Dict[int, BrackenAncestorNode] = {}

        logger.info(
            f"[BrackenEngine] Initialized with convergence_threshold={convergence_threshold}"
        )

    def load_probability_matrix(
        self,
        p_matrix: Dict[int, Dict[int, float]]
    ) -> None:
        """
        Load the precomputed conditional probability matrix P(G_j | S_i).

        This matrix is produced offline by bracken-build via:
            - Simulating reads of length l from each reference genome S_i
            - Classifying simulated reads with Kraken 2
            - Recording fraction of reads landing at each ancestor node G_j

        Args:
            p_matrix: {species_taxid: {ancestor_taxid: P(G_j|S_i)}}
        """
        self._p_matrix = p_matrix
        logger.info(f"[BrackenEngine] Loaded P(G|S) matrix for {len(p_matrix)} species")

    def register_species(
        self,
        taxid: int,
        species_name: str,
        initial_reads: int = 0,
    ) -> None:
        """Register a species S_i with its conditional probability data."""
        entry = BrackenSpeciesEntry(
            taxid=taxid,
            species_name=species_name,
            conditional_probs=self._p_matrix.get(taxid, {}),
        )
        if initial_reads > 0:
            entry.reassigned_reads = float(initial_reads)
        self._species[taxid] = entry

    def ingest_kraken_profile(
        self,
        profile: TaxonomicProfile,
        min_threshold: int = 10,
    ) -> None:
        """
        Ingest a Kraken 2 TaxonomicProfile as Bracken input.

        Extracts:
            - Ancestor nodes G_j: nodes with reads not at species level
            - Direct species reads: species-level read counts as initial priors

        Args:
            profile: Output TaxonomicProfile from Kraken2Engine
            min_threshold: Minimum read count t for species inclusion (Research §1.4)
        """
        total = profile.total_reads
        if total == 0:
            return

        for node in profile.kreport_nodes:
            if node.rank_code in ("S", "S1", "t", "SGB"):
                # Species-level node → seed as candidate with initial reads
                if node.direct_reads >= min_threshold:
                    if node.taxid not in self._species:
                        self.register_species(
                            taxid=node.taxid,
                            species_name=node.name.strip(),
                            initial_reads=node.direct_reads,
                        )
                    else:
                        self._species[node.taxid].reassigned_reads += node.direct_reads
            else:
                # Higher-level ancestor node G_j with reads to redistribute
                if node.cumulative_reads > 0:
                    self._ancestors[node.taxid] = BrackenAncestorNode(
                        taxid=node.taxid,
                        node_name=node.name.strip(),
                        classified_reads=node.direct_reads,
                    )

        # Link candidate species to ancestor nodes
        for sp_taxid, sp_entry in self._species.items():
            for ancestor_taxid in sp_entry.conditional_probs:
                if ancestor_taxid in self._ancestors:
                    anc = self._ancestors[ancestor_taxid]
                    if sp_taxid not in anc.candidate_species:
                        anc.candidate_species.append(sp_taxid)

    def _initialize_priors(self) -> None:
        """
        Initialize P(S_i) uniform priors (equal probability for all species).
        
        Prior = 1 / n_species before any information is incorporated.
        """
        n = len(self._species)
        if n == 0:
            return
        uniform_prior = 1.0 / n
        for sp in self._species.values():
            sp.prior = uniform_prior

    def run_em_iteration(self) -> float:
        """
        Execute one EM iteration of Bracken re-estimation.

        For each ancestor G_j with N_j reads:
            1. Compute posterior: P(S_i|G_j) = P(G_j|S_i)*P(S_i) / Σ_k P(G_j|S_k)*P(S_k)
            2. Assign: N_hat_{S_i←G_j} = N_j × P(S_i|G_j)

        Then update priors from new read assignment totals.

        Returns:
            Maximum absolute prior change across all species (for convergence check).
        """
        # Step 1: For each ancestor node, redistribute reads to candidate species
        new_reads: Dict[int, float] = {sp_taxid: 0.0 for sp_taxid in self._species}

        # Carry forward direct species reads (already at species level)
        for sp_taxid, sp in self._species.items():
            # Direct reads at species node not redistributed (already species-level)
            direct = 0.0
            for anc_taxid, anc in self._ancestors.items():
                if anc.classified_reads > 0 and sp_taxid in anc.candidate_species:
                    # Compute denominator: Σ_k P(G_j|S_k) * P(S_k)
                    denominator = 0.0
                    for candidate_taxid in anc.candidate_species:
                        candidate_sp = self._species.get(candidate_taxid)
                        if candidate_sp is None:
                            continue
                        p_gj_given_sk = candidate_sp.conditional_probs.get(anc_taxid, 0.0)
                        denominator += p_gj_given_sk * candidate_sp.prior

                    if denominator > 0.0:
                        # P(S_i | G_j) = P(G_j | S_i) * P(S_i) / denominator
                        p_gj_given_si = sp.conditional_probs.get(anc_taxid, 0.0)
                        posterior = (p_gj_given_si * sp.prior) / denominator
                        # N_hat_{S_i ← G_j} = N_j × P(S_i | G_j)
                        new_reads[sp_taxid] += anc.classified_reads * posterior

            # Add original direct reads at this species level
            new_reads[sp_taxid] += sp.reassigned_reads if sp.reassigned_reads > 0 else direct

        # Step 2: Update priors from new read totals
        total_new_reads = sum(new_reads.values())
        max_delta = 0.0

        for sp_taxid, sp in self._species.items():
            new_count = new_reads.get(sp_taxid, 0.0)
            new_prior = new_count / total_new_reads if total_new_reads > 0 else 0.0
            delta = abs(new_prior - sp.prior)
            max_delta = max(max_delta, delta)
            sp.prior = new_prior
            sp.reassigned_reads = new_count

        return max_delta

    def reestimate(
        self,
        kraken_profile: TaxonomicProfile,
        sample_id: str = "UNKNOWN_SAMPLE",
        min_threshold: int = 10,
    ) -> TaxonomicProfile:
        """
        Full Bracken re-estimation pipeline.

        Steps:
            1. Ingest Kraken 2 profile
            2. Initialize uniform priors
            3. Run EM iterations until |ΔP| < 1e-6 (max 1000 iterations)
            4. Generate species-level TaxonomicProfile

        Convergence criterion (Research §1.4):
            |ΔP| < 1e-6 across all species priors

        Args:
            kraken_profile: Raw Kraken 2 output TaxonomicProfile
            sample_id: Case/sample identifier
            min_threshold: Minimum reads for species inclusion (default 10)

        Returns:
            Species-level TaxonomicProfile with Bayesian reassigned counts.

        Raises:
            ValueError: If simplex invariant |Σ A_i - 1.0| > 1e-6 after normalization.
        """
        import time
        t0 = time.perf_counter()

        # Ingest the Kraken 2 profile
        self.ingest_kraken_profile(kraken_profile, min_threshold=min_threshold)

        if not self._species:
            # No species detected above threshold → return unmodified profile
            return TaxonomicProfile(
                sample_id=sample_id,
                engine_used=ClassifierEngine.BRACKEN,
                reference_db=kraken_profile.reference_db,
                total_reads=kraken_profile.total_reads,
                classified_reads=0,
                unclassified_reads=kraken_profile.total_reads,
                unclassified_fraction=1.0,
                kreport_nodes=[],
                abundance_vector={},
                processing_time_seconds=round(time.perf_counter() - t0, 4),
                notes=f"Bracken: No species above threshold t={min_threshold}."
            )

        # Initialize uniform priors
        self._initialize_priors()

        # Iterative EM until convergence
        n_iterations = 0
        converged = False
        for i in range(BRACKEN_MAX_ITERATIONS):
            delta = self.run_em_iteration()
            n_iterations = i + 1
            if delta < self.convergence_threshold:
                converged = True
                break

        # Build output profile
        total_reassigned = sum(sp.reassigned_reads for sp in self._species.values())
        total_reads = kraken_profile.total_reads

        kreport_nodes: List[KReportNode] = []
        abundance_vector: Dict[int, float] = {}

        for sp_taxid, sp in sorted(
            self._species.items(),
            key=lambda x: -x[1].reassigned_reads
        ):
            pct = (sp.reassigned_reads / total_reads * 100.0) if total_reads > 0 else 0.0
            abundance_frac = sp.reassigned_reads / total_reassigned if total_reassigned > 0 else 0.0

            kreport_nodes.append(KReportNode(
                pct_total=round(pct, 4),
                cumulative_reads=int(sp.reassigned_reads),
                direct_reads=int(sp.reassigned_reads),
                rank_code="S",
                taxid=sp_taxid,
                name=sp.species_name,
            ))
            abundance_vector[sp_taxid] = abundance_frac

        # Simplex invariant check: |Σ A_i - 1.0| ≤ 1e-6 (AGENTS.md)
        sigma = sum(abundance_vector.values())
        if abundance_vector and abs(sigma - 1.0) > 1e-6:
            raise ValueError(
                f"Bracken simplex invariant VIOLATED: |Σ A_i - 1.0| = "
                f"{abs(sigma - 1.0):.2e} > 1e-6. "
                f"Check read re-assignment normalization."
            )

        classified_reads = int(total_reassigned)
        unclassified_reads = max(0, total_reads - classified_reads)
        unclass_fraction = unclassified_reads / total_reads if total_reads > 0 else 0.0

        profile = TaxonomicProfile(
            sample_id=sample_id,
            engine_used=ClassifierEngine.BRACKEN,
            reference_db=kraken_profile.reference_db,
            total_reads=total_reads,
            classified_reads=classified_reads,
            unclassified_reads=unclassified_reads,
            unclassified_fraction=round(unclass_fraction, 6),
            kreport_nodes=kreport_nodes,
            abundance_vector=abundance_vector,
            processing_time_seconds=round(time.perf_counter() - t0, 4),
            notes=(
                f"Bracken: {len(self._species)} species, "
                f"{n_iterations} EM iterations, "
                f"converged={converged} "
                f"(threshold |ΔP|<{self.convergence_threshold}). "
                f"Simplex invariant: |Σ A_i - 1.0| = {abs(sigma - 1.0):.2e}."
            )
        )

        logger.info(
            f"[BrackenEngine] {sample_id}: {len(self._species)} species, "
            f"converged={converged} after {n_iterations} iterations"
        )
        return profile

    def reassign_reads(
        self,
        genus_level_reads: Dict[int, int],
        assignment_probability_matrix: Dict[int, Dict[int, float]],
    ) -> Dict[int, float]:
        """
        Direct read re-assignment from genus-level counts to species-level counts
        using a pre-computed probability matrix P(S_i | G_j).

        Research §1.4 — Bracken Bayesian EM re-assignment:
            C(S_i) = Σ_j [ C(G_j) × P(S_i | G_j) ]

        Args:
            genus_level_reads:
                Dict mapping genus TaxID → raw read count from Kraken 2.
            assignment_probability_matrix:
                Dict mapping genus TaxID → {species TaxID → probability}.
                Each inner dict must sum to 1.0 (probability simplex).

        Returns:
            Dict mapping species TaxID → reassigned read count (float, may be fractional).
            The sum of all values equals the sum of genus_level_reads.

        Raises:
            ValueError: If any probability row does not sum to 1.0 ± 1e-6.
        """
        # Validate each probability row
        for genus_taxid, probs in assignment_probability_matrix.items():
            row_sum = sum(probs.values())
            if abs(row_sum - 1.0) > 1e-6:
                raise ValueError(
                    f"Probability row for genus {genus_taxid} sums to {row_sum:.8f}, "
                    f"not 1.0. Simplex invariant violated (|Σ - 1.0| = {abs(row_sum - 1.0):.2e})."
                )

        species_counts: Dict[int, float] = {}
        for genus_taxid, read_count in genus_level_reads.items():
            if genus_taxid not in assignment_probability_matrix:
                # No assignment info → assign all reads to genus itself
                species_counts[genus_taxid] = species_counts.get(genus_taxid, 0.0) + read_count
                continue
            for species_taxid, prob in assignment_probability_matrix[genus_taxid].items():
                species_counts[species_taxid] = (
                    species_counts.get(species_taxid, 0.0) + read_count * prob
                )

        return species_counts

