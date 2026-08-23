"""
FORENZA — Bayesian Microbial Source Tracking Engine (Phase 4.3)
===============================================================

Implements the Fast Expectation-Maximization for Microbial Source Tracking
(FEAST) algorithm for forensic soil provenance attribution.

Research §3.4 Bayesian Source Tracking:

    Model:
        Questioned exhibit (sink) = mixture of k candidate source environments
        plus an unknown residual component (to capture dark matter).

        E[sink] = Σ_{s=1}^{k} α_s × source_s + α_unknown × unknown_residual

    FEAST EM Algorithm:
        π_si = mixing proportions (prior: uniform 1/k for each source s)
        E-step: E[z_{ij} | x_j, π] = π_si × λ_{sj} / Σ_t π_ti × λ_{tj}
        where λ_{sj} = source_s[taxon_j] (relative abundance of taxon j in source s)
        M-step: π_si = (1/n) Σ_j E[z_{ij}]
        Convergence: Σ |Δπ| < 1e-6

    Unknown residual:
        ρ_unknown = proportion of sink taxa not explained by any known source.
        Implemented as a uniform source distribution (1/D for all D taxa).

    FEAST Reference:
        Shenhav et al. 2019, Nature Methods.
        (Research §3.4 FEAST microbial source tracking)

    Forensic application:
        - Questioned footwear soil → candidate crime scene environments
        - LR framing: P(sink composition | source_Hp) / P(sink composition | source_Hd)
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# §1 FEAST DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

# FEAST convergence threshold (Research §3.4)
FEAST_CONVERGENCE_THRESHOLD: float = 1e-6
FEAST_MAX_ITERATIONS: int = 1000


@dataclass
class SourceEnvironment:
    """
    A candidate geographic source environment for FEAST source tracking.

    The relative_abundance dict represents P(taxon | source) — the expected
    relative abundance of each taxon in this source environment.
    """
    source_id: str
    description: str
    relative_abundance: Dict[int, float]  # taxid → P(taxon | source)

    def normalize(self) -> None:
        """Ensure relative_abundance sums to 1.0."""
        total = sum(self.relative_abundance.values())
        if total > 0:
            self.relative_abundance = {
                tid: frac / total for tid, frac in self.relative_abundance.items()
            }


@dataclass
class FEASTResult:
    """
    FEAST source tracking result for a single questioned sink sample.
    """
    sink_id: str
    source_proportions: Dict[str, float]   # source_id → mixing proportion α_s
    unknown_proportion: float              # α_unknown (unexplained fraction)
    n_iterations: int
    converged: bool
    convergence_delta: float               # Final |Δπ| at termination
    notes: str = ""


# ═══════════════════════════════════════════════════════════════════════════════
# §2 FEAST ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class FEASTEngine:
    """
    Forensic FEAST Bayesian Microbial Source Tracking Engine.

    Implements the Fast Expectation-Maximization for Microbial Source Tracking
    algorithm (Research §3.4, Shenhav et al. 2019).

    Questioned exhibit (sink) is modeled as a mixture of:
        - k candidate source environments (registered crime scene samples)
        - 1 unknown residual (dark matter / novel environment)

    The mixing proportions α_s give the fraction of the sink microbiome
    attributable to each candidate source.

    Forensic interpretation:
        α_crime_scene > 0.5 → strong support for Hp (originated at crime scene)
        α_unknown > 0.8 → insufficient source coverage to conclude
    """

    def __init__(
        self,
        convergence_threshold: float = FEAST_CONVERGENCE_THRESHOLD,
        max_iterations: int = FEAST_MAX_ITERATIONS,
        seed: int = 42,
    ) -> None:
        self.convergence_threshold = convergence_threshold
        self.max_iterations = max_iterations
        self._sources: Dict[str, SourceEnvironment] = {}

        import random
        self._rng = random.Random(seed)

        logger.info(
            f"[FEASTEngine] Initialized with convergence={convergence_threshold}, "
            f"max_iter={max_iterations}"
        )

    def register_source(self, source: SourceEnvironment) -> None:
        """Register a candidate source environment."""
        source.normalize()
        self._sources[source.source_id] = source
        logger.debug(
            f"[FEASTEngine] Registered source '{source.source_id}' "
            f"with {len(source.relative_abundance)} taxa"
        )

    def _build_unknown_source(self, all_taxids: List[int]) -> Dict[int, float]:
        """
        Build the uniform unknown residual source distribution.

        The unknown source represents taxa not covered by any known source.
        Each taxon has equal probability 1/D (Research §3.4 unknown residual).
        """
        D = len(all_taxids)
        if D == 0:
            return {}
        return {taxid: 1.0 / D for taxid in all_taxids}

    def track_sources(
        self,
        sink_abundance: Dict[int, float],
        sink_id: str = "QUESTIONED_TRACE",
    ) -> FEASTResult:
        """
        Run FEAST EM to estimate mixing proportions from sink to sources.

        Algorithm:
            Initialize: π_s = 1/(k+1) for all k sources + 1 unknown
            E-step:
                responsibility r_{sj} = π_s × λ_{sj} / Σ_t π_t × λ_{tj}
                where λ_{sj} = source_s.relative_abundance.get(j, ε)
            M-step:
                π_s = (1/D_observed) × Σ_j r_{sj} × sink[j]
            Convergence: Σ_s |Δπ_s| < 1e-6

        Args:
            sink_abundance: Questioned sink relative abundance {taxid: fraction}
            sink_id: Sample identifier for the questioned exhibit

        Returns:
            FEASTResult with mixing proportions per source and unknown fraction.
        """
        sources = self._sources
        if not sources:
            return FEASTResult(
                sink_id=sink_id,
                source_proportions={},
                unknown_proportion=1.0,
                n_iterations=0,
                converged=False,
                convergence_delta=float("inf"),
                notes="No sources registered. All attribution to unknown."
            )

        # Collect all taxa observed in sink or any source
        all_taxids = list(set(sink_abundance) | set(
            taxid for src in sources.values()
            for taxid in src.relative_abundance
        ))
        D = len(all_taxids)
        n_sources = len(sources)
        source_ids = list(sources.keys()) + ["_UNKNOWN_"]

        # Build source emission matrix: λ[source_id][taxid] = P(taxon | source)
        epsilon = 1.0 / (D * 1000)  # background for taxa absent from source
        unknown_dist = self._build_unknown_source(all_taxids)

        lambda_matrix: Dict[str, Dict[int, float]] = {}
        for sid in sources:
            src_abd = sources[sid].relative_abundance
            total = sum(src_abd.values())
            if total <= 0:
                total = 1.0
            lambda_matrix[sid] = {
                taxid: src_abd.get(taxid, epsilon) / total
                for taxid in all_taxids
            }
        lambda_matrix["_UNKNOWN_"] = unknown_dist

        # Initialize uniform mixing proportions
        pi: Dict[str, float] = {sid: 1.0 / len(source_ids) for sid in source_ids}

        n_iterations = 0
        converged = False
        final_delta = float("inf")

        # Normalize sink to use as observation weights
        sink_total = sum(sink_abundance.values())
        sink_norm = {
            taxid: frac / sink_total for taxid, frac in sink_abundance.items()
        } if sink_total > 0 else {taxid: 1.0 / D for taxid in all_taxids}

        for iteration in range(self.max_iterations):
            # E-step: compute responsibilities r_{sj}
            responsibilities: Dict[str, Dict[int, float]] = {sid: {} for sid in source_ids}

            for taxid in all_taxids:
                sink_weight = sink_norm.get(taxid, epsilon)
                if sink_weight <= 0:
                    continue

                # Denominator: Σ_t π_t × λ_{tj}
                denominator = sum(
                    pi[sid] * lambda_matrix[sid].get(taxid, epsilon)
                    for sid in source_ids
                )

                if denominator <= 0:
                    continue

                for sid in source_ids:
                    r = (pi[sid] * lambda_matrix[sid].get(taxid, epsilon)) / denominator
                    responsibilities[sid][taxid] = r * sink_weight

            # M-step: update mixing proportions
            new_pi: Dict[str, float] = {}
            for sid in source_ids:
                new_pi[sid] = sum(responsibilities[sid].values())

            # Normalize pi to sum to 1
            pi_total = sum(new_pi.values())
            if pi_total > 0:
                new_pi = {sid: v / pi_total for sid, v in new_pi.items()}

            # Convergence check
            delta = sum(abs(new_pi.get(sid, 0.0) - pi.get(sid, 0.0)) for sid in source_ids)
            pi = new_pi
            n_iterations = iteration + 1
            final_delta = delta

            if delta < self.convergence_threshold:
                converged = True
                break

        # Extract results
        source_proportions = {
            sid: round(pi.get(sid, 0.0), 6)
            for sid in list(sources.keys())
        }
        unknown_proportion = round(pi.get("_UNKNOWN_", 0.0), 6)

        result = FEASTResult(
            sink_id=sink_id,
            source_proportions=source_proportions,
            unknown_proportion=unknown_proportion,
            n_iterations=n_iterations,
            converged=converged,
            convergence_delta=round(final_delta, 10),
            notes=(
                f"FEAST EM: {n_iterations} iterations, "
                f"converged={converged} (threshold={self.convergence_threshold}). "
                f"Unknown residual α_unknown={unknown_proportion:.3f} "
                f"({'HIGH — insufficient source coverage' if unknown_proportion > 0.8 else 'acceptable'}). "
                f"Sources: {list(source_proportions.keys())}."
            )
        )

        logger.info(
            f"[FEASTEngine] {sink_id}: "
            f"converged={converged} after {n_iterations} iter, "
            f"unknown={unknown_proportion:.3f}, "
            f"sources={source_proportions}"
        )

        return result

    def compute_source_lr(
        self,
        feast_result: FEASTResult,
        hp_source_id: str,
        hd_source_id: Optional[str] = None,
    ) -> Tuple[float, str]:
        """
        Compute a source-proportion-based Likelihood Ratio.

        Research §3.4 → §5.1 Bridge:
            LR = α_Hp / α_Hd
            where α_Hp = mixing proportion for the prosecution source (crime scene)
                  α_Hd = mixing proportion for the defence source (alternative location)

        If hd_source_id is None, Hd is represented by the unknown residual.

        Args:
            feast_result: FEAST mixing proportion result
            hp_source_id: Prosecution hypothesis source ID
            hd_source_id: Defence hypothesis source ID (or None → unknown)

        Returns:
            Tuple of (log10_LR, verbal_description)
        """
        alpha_hp = feast_result.source_proportions.get(hp_source_id, 0.0)

        if hd_source_id:
            alpha_hd = feast_result.source_proportions.get(hd_source_id, 0.0)
        else:
            alpha_hd = feast_result.unknown_proportion

        # Guard against division by zero
        if alpha_hd <= 0.0:
            alpha_hd = 1e-6  # small background for numerical stability

        if alpha_hp <= 0.0:
            return float("-inf"), "FEAST LR: Virtually no support for Hp source."

        lr = alpha_hp / alpha_hd
        log10_lr = math.log10(lr)

        return log10_lr, (
            f"FEAST Source Proportion LR: "
            f"α_Hp({hp_source_id})={alpha_hp:.4f}, "
            f"α_Hd={'unknown' if hd_source_id is None else hd_source_id}={alpha_hd:.4f}, "
            f"LR = {lr:.2e} (log10 LR = {log10_lr:.2f})."
        )
