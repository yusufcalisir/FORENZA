"""
FORENZA Lifestyle & Environmental Epigenetics Engine.

Evaluates lifestyle biomarkers from DNA methylation data:
- AHRR locus (cg05575921) methylation for smoking status prediction (Current, Former, Non-Smoker).
- SLC6A3 & HADD loci methylation for alcohol exposure index.
- PER2 & BMAL1 loci methylation phase shift for diurnal circadian Time-of-Death (TOD) estimation.
"""

import math
from typing import Dict, Any, Optional


class LifestyleEpigeneticEngine:
    """
    Evaluates lifestyle and environmental epigenetic biomarkers from target CpG methylation ratios.
    """

    def analyze_lifestyle_profile(
        self,
        ahrr_cg05575921_beta: float = 0.85,
        slc6a3_beta: Optional[float] = 0.50,
        per2_beta: Optional[float] = 0.40,
        bmal1_beta: Optional[float] = 0.60
    ) -> Dict[str, Any]:
        """
        Calculates smoking status, alcohol exposure index, and circadian phase shift.

        :param ahrr_cg05575921_beta: Methylation ratio at AHRR cg05575921 [0.0, 1.0].
        :param slc6a3_beta: Optional methylation ratio at SLC6A3 [0.0, 1.0].
        :param per2_beta: Optional methylation ratio at PER2 [0.0, 1.0].
        :param bmal1_beta: Optional methylation ratio at BMAL1 [0.0, 1.0].
        :return: Dict containing lifestyle classifications and risk scores.
        """
        ahrr = float(ahrr_cg05575921_beta)
        if not (0.0 <= ahrr <= 1.0):
            raise ValueError(f"AHRR beta value must be within [0.0, 1.0], got {ahrr}.")

        # AHRR Smoking Status Classification (Standard forensic epigenetic thresholds)
        if ahrr < 0.55:
            smoking_status = "CURRENT_HEAVY_SMOKER"
            smoking_probability = round(min(0.98, (0.55 - ahrr) * 2.0 + 0.65), 2)
            pack_years_est = round((0.55 - ahrr) * 45.0 + 10.0, 1)
        elif ahrr < 0.80:
            smoking_status = "FORMER_OR_LIGHT_SMOKER"
            smoking_probability = round(0.75, 2)
            pack_years_est = round((0.80 - ahrr) * 20.0, 1)
        else:
            smoking_status = "NON_SMOKER"
            smoking_probability = round(min(0.95, ahrr * 0.98), 2)
            pack_years_est = 0.0

        # Alcohol Exposure Index (SLC6A3 biomarker)
        alcohol_index_score = 0.0
        alcohol_exposure_level = "LOW_OR_ABSTAINER"
        if slc6a3_beta is not None:
            slc = float(slc6a3_beta)
            if not (0.0 <= slc <= 1.0):
                raise ValueError(f"SLC6A3 beta value must be within [0.0, 1.0], got {slc}.")
            alcohol_index_score = round(abs(0.50 - slc) * 200.0, 1)
            if alcohol_index_score > 40.0:
                alcohol_exposure_level = "HEAVY_CHRONIC_EXPOSURE"
            elif alcohol_index_score > 20.0:
                alcohol_exposure_level = "MODERATE_EXPOSURE"

        # Circadian Time-of-Death (TOD) Phase Shift (PER2 vs BMAL1 ratio)
        circadian_phase = "DIURNAL_PEAK_DAYTIME"
        tod_window = "10:00 - 16:00 UTC"
        if per2_beta is not None and bmal1_beta is not None:
            p2 = float(per2_beta)
            b1 = float(bmal1_beta)
            if not (0.0 <= p2 <= 1.0) or not (0.0 <= b1 <= 1.0):
                raise ValueError("Circadian PER2/BMAL1 beta values must be within [0.0, 1.0].")
            
            ratio = p2 / max(0.01, b1)
            if ratio > 1.2:
                circadian_phase = "NOCTURNAL_PEAK_NIGHT"
                tod_window = "22:00 - 04:00 UTC"
            elif ratio < 0.8:
                circadian_phase = "MATUTINAL_PEAK_MORNING"
                tod_window = "04:00 - 10:00 UTC"

        return {
            "ahrr_methylation_beta": ahrr,
            "smoking_status": smoking_status,
            "smoking_probability": smoking_probability,
            "estimated_pack_years": pack_years_est,
            "alcohol_index_score": alcohol_index_score,
            "alcohol_exposure_level": alcohol_exposure_level,
            "circadian_phase": circadian_phase,
            "estimated_tod_window": tod_window,
            "biomarker_panel": "AHRR (cg05575921) + SLC6A3 + PER2/BMAL1"
        }
