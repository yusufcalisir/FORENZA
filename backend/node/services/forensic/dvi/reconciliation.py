"""
FORENZA Interpol Disaster Victim Identification (DVI) Reconciliation Engine.
Performs N x M cross-comparison matrix evaluation between Ante-Mortem (AM) family reference profiles
and Post-Mortem (PM) disaster victim human remain profiles.

Reference:
  Interpol Disaster Victim Identification (DVI) Forensic DNA Reconciliation Protocol (2018).
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from node.services.forensic.models import STRGenotype, STRProfile
from node.services.forensic.kinship_engine import KinshipEngine, KinshipRelationship


@dataclass
class DviPairwiseComparison:
    am_profile_id: str                 # Ante-Mortem reference (e.g. AM-FAMILY-101)
    pm_profile_id: str                 # Post-Mortem human remain (e.g. PM-REMAIN-502)
    relationship_hypothesis: str       # 'DIRECT_REFERENCE', 'PARENT_CHILD', 'SIBLING'
    lr: float
    log10_lr: float
    identification_status: str        # 'CONFIRMED_MATCH', 'PROBABLE_MATCH', 'EXCLUDED', 'INCONCLUSIVE'


@dataclass
class DviReconciliationReport:
    disaster_event_id: str
    total_am_profiles: int
    total_pm_profiles: int
    confirmed_identifications_count: int
    reconciliation_matrix: List[DviPairwiseComparison]
    dvi_summary: str


class DviReconciliationEngine:
    """
    Computes Interpol DVI cross-reconciliation matrix comparing AM family references vs PM victim remains.
    """

    def __init__(self, kinship_engine: Optional[KinshipEngine] = None):
        self.kinship_engine = kinship_engine or KinshipEngine()

    def reconcile_am_pm_profiles(
        self,
        disaster_event_id: str,
        am_profiles: List[STRProfile],
        pm_profiles: List[STRProfile]
    ) -> DviReconciliationReport:
        """Runs N x M cross-comparison matrix across AM family references and PM victim remains."""
        matrix: List[DviPairwiseComparison] = []
        confirmed_count = 0

        for am in am_profiles:
            for pm in pm_profiles:
                # 1. Evaluate Kinship (Parent-Child hypothesis)
                res = self.kinship_engine.compute_kinship_index(am, pm, KinshipRelationship.PARENT_CHILD)
                lr = max(1e-9, res.value)
                log_lr = round(math.log10(lr), 4)

                if log_lr >= 4.0:
                    status = "CONFIRMED_IDENTIFICATION"
                    confirmed_count += 1
                elif log_lr >= 1.0:
                    status = "PROBABLE_IDENTIFICATION"
                    confirmed_count += 1
                elif log_lr <= -1.0:
                    status = "EXCLUDED"
                else:
                    status = "INCONCLUSIVE"

                matrix.append(DviPairwiseComparison(
                    am_profile_id=am.profile_id,
                    pm_profile_id=pm.profile_id,
                    relationship_hypothesis="PARENT_CHILD",
                    lr=round(lr, 2),
                    log10_lr=log_lr,
                    identification_status=status
                ))

        return DviReconciliationReport(
            disaster_event_id=disaster_event_id,
            total_am_profiles=len(am_profiles),
            total_pm_profiles=len(pm_profiles),
            confirmed_identifications_count=confirmed_count,
            reconciliation_matrix=matrix,
            dvi_summary=f"DVI Reconciliation complete: {confirmed_count} confirmed identifications out of {len(am_profiles) * len(pm_profiles)} evaluated AM/PM pairs."
        )
