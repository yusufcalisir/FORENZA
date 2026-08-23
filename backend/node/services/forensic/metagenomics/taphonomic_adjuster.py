"""
FORENZA — Taphonomic Decay & Transfer Dynamic Adjuster (Phase 5.2)
==================================================================

Implements temporal and storage condition-dependent taphonomic shifts
in forensic soil metagenome composition, enabling post-deposit time
adjustment of taxonomic abundance profiles.

Research §4.2 Taphonomic Decay Principles:

    Bacterial Decay Kinetics after Soil Deposition:
        Gram-negative, moisture-sensitive taxa decay faster:
            Pseudomonadota, Bacteroidota → 50% reduction per 30 days desiccation
        Spore-forming taxa are enriched over time:
            Actinomycetota, Bacillus spp. → resistant
        Ratio metric: Actinomycetota:Gammaproteobacteria ratio increases with age.

    Desiccation & Temperature Decay (Research §4.2):
        f_decay(t, T) = exp(-λ × t) where:
            λ = 0.023 day^{-1} at 25°C (Gram-negative fragile taxa)
            λ = 0.007 day^{-1} at 4°C  (cold storage)
            λ = 0.002 day^{-1} at -20°C (frozen)
            Actinomycetota: λ ≈ 0.001 day^{-1} (highly resistant)

    Human Carrier Skin Microbiome Contamination Filter (Research §4.2):
        Subtract Cutibacterium acnes, Staphylococcus epidermidis,
        Corynebacterium spp. BEFORE taphonomic adjustment.
        (Handled upstream by DarkMatterFilter; referenced here for completeness.)

    Storage Condition Adjustment Matrix:
        The following weighting factors apply to susceptible taxa:
            Desiccated (25°C):   w = exp(-0.023 × t)
            Refrigerated (4°C):  w = exp(-0.007 × t)
            Frozen (-20°C):      w = exp(-0.002 × t)
            Actinomycetota:      w = exp(-0.001 × t) (all conditions)
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, FrozenSet, List, Optional, Set

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# §1 STORAGE CONDITIONS & DECAY CONSTANTS (Research §4.2)
# ═══════════════════════════════════════════════════════════════════════════════

class StorageCondition(str, Enum):
    """Storage condition categories for taphonomic decay adjustment."""
    DESICCATED_25C = "DESICCATED_25C"       # Air-dried at 25°C
    REFRIGERATED_4C = "REFRIGERATED_4C"     # 4°C cold storage
    FROZEN_MINUS20C = "FROZEN_MINUS20C"     # -20°C frozen
    AMBIENT_VARIABLE = "AMBIENT_VARIABLE"   # Uncontrolled ambient (crime scene)


# Decay rate constants λ (day^{-1}) for fragile Gram-negative taxa (Research §4.2)
_GRAM_NEG_DECAY_RATES: Dict[StorageCondition, float] = {
    StorageCondition.DESICCATED_25C: 0.023,
    StorageCondition.REFRIGERATED_4C: 0.007,
    StorageCondition.FROZEN_MINUS20C: 0.002,
    StorageCondition.AMBIENT_VARIABLE: 0.015,  # midpoint estimate
}

# Decay rate constants for resistant Actinomycetota & spore-forming Bacillus
_RESISTANT_DECAY_RATE: float = 0.001  # day^{-1} (all conditions)

# TaxIDs of susceptible (fragile Gram-negative) phyla at genus level
# Represented here by representative phylum-level taxids
FRAGILE_GRAMNEG_PHYLUM_TAXIDS: FrozenSet[int] = frozenset([
    1224,   # Pseudomonadota (Proteobacteria)
    976,    # Bacteroidota (Bacteroidetes)
    203691, # Spirochaetota (Spirochaetes) — very fragile
    29547,  # Campylobacterota
    74152,  # Aquificota
])

# TaxIDs of resistant (spore-forming) phyla
RESISTANT_PHYLUM_TAXIDS: FrozenSet[int] = frozenset([
    201174, # Actinomycetota (Actinobacteria)
    1239,   # Bacillota (Firmicutes, includes Bacillus spp.)
    203682, # Chloroflexota (highly resistant)
])

# Human skin contaminants (identical to dark_matter_filter.py — referenced here for completeness)
SKIN_CONTAMINANT_TAXIDS: FrozenSet[int] = frozenset([
    1743,   # Cutibacterium acnes
    1282,   # Staphylococcus epidermidis
    1717,   # Corynebacterium (genus)
])


# ═══════════════════════════════════════════════════════════════════════════════
# §2 TAPHONOMIC DECAY COMPUTER
# ═══════════════════════════════════════════════════════════════════════════════

def compute_taphonomic_weight(
    taxid: int,
    days_stored: float,
    condition: StorageCondition,
    fragile_phylum_taxids: Optional[FrozenSet[int]] = None,
    resistant_phylum_taxids: Optional[FrozenSet[int]] = None,
) -> float:
    """
    Compute the taphonomic decay weight for a taxon given storage conditions.

    Research §4.2 Decay Function:
        w(t) = exp(-λ × t)
        where:
            λ = decay rate (day^{-1}) from research constants
            t = days_stored

    Args:
        taxid: NCBI TaxID of the target organism
        days_stored: Number of days since sample collection
        condition: Storage condition (desiccated, refrigerated, frozen)
        fragile_phylum_taxids: Set of fragile phylum taxids (default: built-in)
        resistant_phylum_taxids: Set of resistant phylum taxids (default: built-in)

    Returns:
        Weight w ∈ (0, 1]: 1.0 = no decay, approaches 0 = fully decayed
    """
    if fragile_phylum_taxids is None:
        fragile_phylum_taxids = FRAGILE_GRAMNEG_PHYLUM_TAXIDS
    if resistant_phylum_taxids is None:
        resistant_phylum_taxids = RESISTANT_PHYLUM_TAXIDS

    if taxid in fragile_phylum_taxids:
        lambda_val = _GRAM_NEG_DECAY_RATES.get(condition, 0.015)
    elif taxid in resistant_phylum_taxids:
        lambda_val = _RESISTANT_DECAY_RATE
    else:
        # Unknown taxon: use midpoint decay rate
        lambda_val = (
            _GRAM_NEG_DECAY_RATES.get(condition, 0.015) + _RESISTANT_DECAY_RATE
        ) / 2.0

    weight = math.exp(-lambda_val * days_stored)
    return max(weight, 1e-6)  # minimum non-zero weight


# ═══════════════════════════════════════════════════════════════════════════════
# §3 TAPHONOMIC ADJUSTER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TaphonomicAdjustmentReport:
    """
    Report from a taphonomic adjustment operation.

    Documents all weight adjustments applied and the resulting
    abundance vector shift.
    """
    sample_id: str
    days_stored: float
    storage_condition: StorageCondition
    taxid_weights: Dict[int, float]           # taxid → applied taphonomic weight
    original_abundance: Dict[int, float]
    adjusted_abundance: Dict[int, float]
    actinomycetota_ratio_original: float      # Resistant:Fragile ratio before adjustment
    actinomycetota_ratio_adjusted: float      # Resistant:Fragile ratio after adjustment
    notes: str = ""


class TaphonomicAdjuster:
    """
    Forensic Taphonomic Decay & Transfer Dynamic Adjuster.

    Adjusts taxonomic abundance vectors for time-dependent post-deposit
    decay of fragile Gram-negative taxa relative to resistant spore-formers.

    This adjuster is applied AFTER dark matter decontamination and BEFORE
    Aitchison distance computation for LR scoring.

    Research §4.2 Note on Forensic Interpretation:
        A high Actinomycetota:Pseudomonadota ratio in a questioned trace
        relative to a fresh crime scene reference sample may indicate either:
            1. The trace was deposited weeks/months before collection, OR
            2. The trace originated from a different (drier/older) environment.
        Both interpretations must be presented to the trier of fact.
    """

    def __init__(
        self,
        fragile_phylum_taxids: Optional[FrozenSet[int]] = None,
        resistant_phylum_taxids: Optional[FrozenSet[int]] = None,
    ) -> None:
        self.fragile_phylum_taxids = fragile_phylum_taxids or FRAGILE_GRAMNEG_PHYLUM_TAXIDS
        self.resistant_phylum_taxids = resistant_phylum_taxids or RESISTANT_PHYLUM_TAXIDS

    def adjust_abundance(
        self,
        abundance_vector: Dict[int, float],
        days_stored: float,
        condition: StorageCondition,
        sample_id: str = "UNKNOWN_SAMPLE",
    ) -> TaphonomicAdjustmentReport:
        """
        Apply taphonomic decay weights to an abundance vector.

        Steps:
            1. Compute w_i = exp(-λ_i × t) for each taxon
            2. Weight-scale abundance: x_i_adj = x_i × w_i
            3. Renormalize to simplex: x_i_adj = x_i_adj / Σ x_j_adj

        Args:
            abundance_vector: taxid → relative abundance (sum = 1.0)
            days_stored: Days since sample collection
            condition: Storage condition
            sample_id: Sample identifier

        Returns:
            TaphonomicAdjustmentReport with adjusted abundance vector.
        """
        weights: Dict[int, float] = {}
        weighted: Dict[int, float] = {}

        for taxid, frac in abundance_vector.items():
            w = compute_taphonomic_weight(
                taxid=taxid,
                days_stored=days_stored,
                condition=condition,
                fragile_phylum_taxids=self.fragile_phylum_taxids,
                resistant_phylum_taxids=self.resistant_phylum_taxids,
            )
            weights[taxid] = w
            weighted[taxid] = frac * w

        # Renormalize
        total_weighted = sum(weighted.values())
        if total_weighted > 0:
            adjusted = {tid: w / total_weighted for tid, w in weighted.items()}
        else:
            adjusted = {tid: 1.0 / len(weighted) for tid in weighted} if weighted else {}

        # Compute Actinomycetota:Pseudomonadota ratios
        def _compute_ratio(vec: Dict[int, float]) -> float:
            actino = sum(v for tid, v in vec.items() if tid in self.resistant_phylum_taxids)
            fragile = sum(v for tid, v in vec.items() if tid in self.fragile_phylum_taxids)
            return actino / fragile if fragile > 0 else float("inf")

        ratio_original = _compute_ratio(abundance_vector)
        ratio_adjusted = _compute_ratio(adjusted)

        report = TaphonomicAdjustmentReport(
            sample_id=sample_id,
            days_stored=days_stored,
            storage_condition=condition,
            taxid_weights=weights,
            original_abundance=abundance_vector,
            adjusted_abundance=adjusted,
            actinomycetota_ratio_original=round(ratio_original, 4),
            actinomycetota_ratio_adjusted=round(ratio_adjusted, 4),
            notes=(
                f"Taphonomic adjustment: {days_stored} days, {condition.value}. "
                f"Actinomycetota:Fragile ratio changed "
                f"from {ratio_original:.3f} to {ratio_adjusted:.3f}. "
                f"NOTE: Elevated Actinomycetota:Pseudomonadota ratio may reflect "
                f"either (a) post-deposit aging or (b) inherently dry/resistant environment. "
                f"Both hypotheses must be evaluated for the trier of fact."
            )
        )

        logger.info(
            f"[TaphonomicAdjuster] {sample_id}: "
            f"{days_stored}d at {condition.value}, "
            f"Actino:Fragile ratio {ratio_original:.3f}→{ratio_adjusted:.3f}"
        )

        return report
