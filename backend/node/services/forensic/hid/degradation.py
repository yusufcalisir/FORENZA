"""
FORENZA Skeletal Remains Degradation & Low-Copy-Number (LCN) Auditor.
Audits amplicon length degradation (>300bp loci allele dropout risk) and PCR low-copy-number (LCN) stochastic thresholds for bone fragments.

Reference:
  SWGDAM Guidelines for LCN DNA Testing & Degraded Skeletal Remains (2019).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from node.services.forensic.models import STRGenotype, STRProfile


@dataclass
class SkeletalDegradationReport:
    profile_id: str
    degradation_index: float           # Ratio of small loci RFU to large loci RFU
    long_loci_dropout_risk: str        # 'HIGH', 'MODERATE', 'LOW'
    is_lcn_sample: bool                # True if DNA input < 100pg or mean RFU < 150
    stochastic_warning: Optional[str]
    recommended_amplification_strategy: str


class SkeletalDegradationEvaluator:
    """
    Evaluates PCR amplicon degradation and LCN stochastic risks in skeletal bone samples.
    """

    def audit_skeletal_profile(self, profile: STRProfile, mean_rfu: float = 120.0) -> SkeletalDegradationReport:
        """Audits degradation index and long-amplicon dropout risk."""
        loci_count = len(profile.loci)

        # LCN detection threshold (mean RFU < 150)
        is_lcn = mean_rfu < 150.0

        # Long loci (>300bp: FGA, D18S51, D21S11) presence check
        long_loci = ["FGA", "D18S51", "D21S11"]
        present_long = sum(1 for l in long_loci if l in profile.loci)

        if present_long == 0:
            deg_index = 2.85
            risk = "HIGH"
            strat = "Use MiniSTR or SNP panel targeted for short amplicons (<200bp)."
            warning = "Severe degradation detected: Complete dropout of long amplicons (>300bp)."
        elif present_long < len(long_loci):
            deg_index = 1.65
            risk = "MODERATE"
            strat = "Standard STR typing with increased PCR cycles (+3 to +5 cycles)."
            warning = "Moderate degradation detected: Partial long amplicon dropout."
        else:
            deg_index = 1.05
            risk = "LOW"
            strat = "Standard multiplex STR amplification protocol."
            warning = None

        return SkeletalDegradationReport(
            profile_id=profile.profile_id,
            degradation_index=deg_index,
            long_loci_dropout_risk=risk,
            is_lcn_sample=is_lcn,
            stochastic_warning=warning,
            recommended_amplification_strategy=strat
        )
