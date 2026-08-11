"""
FORENZA Insect Ecological Succession Auditor.
Models ecological arthropod succession waves on decomposing human remains across 4 major decomposition phases:
  - Fresh Stage Wave (Calliphoridae blowflies, Muscidae)
  - Bloated Stage Wave (Silphidae carrion beetles, Histeridae predators)
  - Active Decay Wave (Piophilidae skipper flies, Staphylinidae rove beetles)
  - Advanced / Dry Decay Wave (Dermestidae skin beetles, Tineidae moths)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class ArthropodOccurrence:
    family_name: str                   # 'Calliphoridae', 'Silphidae', 'Dermestidae'
    species_observed: str              # e.g. 'Calliphora vicina'
    abundance_score: str               # 'HIGH', 'MODERATE', 'SCARCE'


@dataclass
class SuccessionAuditReport:
    sample_id: str
    inferred_decomposition_stage: str  # 'FRESH_STAGE', 'BLOATED_STAGE', 'ACTIVE_DECAY', 'DRY_DECAY'
    typical_timeframe_days: str        # e.g. '1 - 3 days'
    observed_families: List[str]
    succession_summary: str


class InsectSuccessionAuditor:
    """
    Audits arthropod community composition to infer decomposition state.
    """

    def audit_succession_wave(self, sample_id: str, occurrences: List[ArthropodOccurrence]) -> SuccessionAuditReport:
        families = [o.family_name.capitalize() for o in occurrences]
        fam_set = set(families)

        if "Dermestidae" in fam_set or "Tineidae" in fam_set:
            stage = "ADVANCED_DRY_DECAY"
            timeframe = "25 - 50+ days"
        elif "Piophilidae" in fam_set or "Staphylinidae" in fam_set:
            stage = "ACTIVE_DECAY"
            timeframe = "8 - 20 days"
        elif "Silphidae" in fam_set or "Histeridae" in fam_set:
            stage = "BLOATED_STAGE"
            timeframe = "3 - 7 days"
        else:
            stage = "FRESH_STAGE"
            timeframe = "1 - 3 days"

        summary = f"Arthropod Succession Audit for {sample_id}: Inferred {stage} ({timeframe}) from {len(families)} observed families."

        return SuccessionAuditReport(
            sample_id=sample_id,
            inferred_decomposition_stage=stage,
            typical_timeframe_days=timeframe,
            observed_families=families,
            succession_summary=summary
        )
