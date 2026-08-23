"""
FORENZA Taphonomic Epigenetic Kinetics & Post-Mortem Arrest Engine (Pillar 4 §5).

Enforces the fundamental forensic dichotomy:
  1. DNA Methylation Epigenetic Clocks Measure Age-at-Death (Chronological Donor Age).
  2. DNA Methylation DOES NOT Measure Post-Mortem Interval (PMI).
  3. Enzymatic DNMT arrest occurs rapidly (15-30 min) upon SAM/ATP depletion.
  4. 5mC covalent stability is preserved across 0-120 hours post-mortem.
  5. Hydrolytic deamination kinetics (5mC -> T and C -> U) noise filtering.
"""

import math
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    TaphonomicPMIResult,
)


@dataclass
class TaphonomicStabilityMetrics:
    """Quantitative taphonomic stability parameters for post-mortem specimen."""
    pmi_hours: float
    ambient_temperature_c: float
    enzymatic_arrest_status: str
    five_mc_preservation_fraction: float
    deamination_drift_fraction: float
    epigenetic_clock_reliability: str
    biological_rationale: str
    advisory_warning: str


class TaphonomyEngine:
    """Mathematical engine for post-mortem 5mC stability and taphonomic decay kinetics."""

    # Arrhenius activation energy for 5mC hydrolytic deamination (kJ/mol)
    EA_DEAMINATION: float = 117.0
    R_GAS_CONST: float = 8.314e-3  # kJ/(mol*K)
    K0_PRE_EXPONENTIAL: float = 4.2e12  # day^-1

    @classmethod
    def calculate_deamination_rate(cls, temperature_c: float) -> float:
        """
        Compute temperature-dependent hydrolytic deamination rate k_deam (day^-1)
        via Arrhenius equation: k = k0 * exp(-Ea / (R * T_K)).
        """
        temp_k = max(250.0, min(330.0, temperature_c + 273.15))
        k_deam = cls.K0_PRE_EXPONENTIAL * math.exp(-cls.EA_DEAMINATION / (cls.R_GAS_CONST * temp_k))
        return float(k_deam)

    @classmethod
    def evaluate_post_mortem_epigenetic_stability(
        cls,
        estimated_pmi_hours: float,
        ambient_temperature_c: float = 20.0,
    ) -> TaphonomicStabilityMetrics:
        """
        Evaluate post-mortem 5mC preservation and verify age-at-death validity.
        """
        pmi_h = max(0.0, float(estimated_pmi_hours))
        temp_c = float(ambient_temperature_c)

        # 1. Enzymatic arrest status
        # Somatic death depletes ATP/SAM within 0.5 hours, inactivating DNMT1/DNMT3A/B
        if pmi_h >= 0.5:
            arrest_status = "COMPLETE_ENZYMATIC_ARREST"
        else:
            arrest_status = "EARLY_AGONAL_PHASE"

        # 2. Compute cumulative hydrolytic deamination fraction (5mC -> T)
        pmi_days = pmi_h / 24.0
        k_deam_daily = cls.calculate_deamination_rate(temp_c)
        deam_fraction = 1.0 - math.exp(-k_deam_daily * pmi_days)

        # 3. 5mC chemical integrity preservation index
        # 5mC has a stable covalent bond preserved across 0-120 hours (< 0.05% deamination at 20C)
        five_mc_preservation = max(0.0, 1.0 - deam_fraction)

        # 4. Reliability classification of Epigenetic Age-at-Death
        if pmi_h <= 120.0 and temp_c <= 25.0:
            reliability = "HIGH_CONFIDENCE_AGE_AT_DEATH"
            warning = "Epigenetic clock accurately reflects Age-at-Death. 5mC methylation remains intact."
        elif pmi_h <= 240.0 and temp_c <= 20.0:
            reliability = "MODERATE_CONFIDENCE_AGE_AT_DEATH"
            warning = "Minor taphonomic fragmentation detected; epigenetic age valid with expanded uncertainty."
        else:
            reliability = "ELEVATED_TAPHONOMIC_DEGRADATION"
            warning = "Extended post-mortem interval or elevated temperature may induce deamination drift."

        rationale = (
            f"DNA methylation underwent complete catalytic arrest at somatic death (PMI={pmi_h:.1f}h). "
            f"Preservation fraction of 5mC is {five_mc_preservation * 100.0:.2f}%. "
            "Epigenetic clocks measure the individual's Age-at-Death, NOT post-mortem interval."
        )

        return TaphonomicStabilityMetrics(
            pmi_hours=round(pmi_h, 1),
            ambient_temperature_c=round(temp_c, 1),
            enzymatic_arrest_status=arrest_status,
            five_mc_preservation_fraction=round(five_mc_preservation, 5),
            deamination_drift_fraction=round(deam_fraction, 6),
            epigenetic_clock_reliability=reliability,
            biological_rationale=rationale,
            advisory_warning=warning,
        )

    @classmethod
    def correct_deamination_drift(
        cls,
        observed_betas: Dict[str, float],
        pmi_hours: float,
        temperature_c: float = 20.0,
    ) -> Dict[str, float]:
        """
        Apply noise filter for spontaneous 5mC -> T hydrolytic deamination.
        """
        pmi_days = max(0.0, pmi_hours / 24.0)
        k_deam = cls.calculate_deamination_rate(temperature_c)
        survival_factor = math.exp(-k_deam * pmi_days)

        corrected = {}
        for probe, b_val in observed_betas.items():
            # Correct for small loss of apparent methylation
            corr_b = min(1.0, max(0.0, b_val / max(0.90, survival_factor)))
            corrected[probe] = round(corr_b, 4)
        return corrected
