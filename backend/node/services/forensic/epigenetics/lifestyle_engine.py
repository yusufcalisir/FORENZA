"""
FORENZA Environmental Epigenetics & Lifestyle Biomarkers Engine — Module 18.

Implements verbatim from Pillar 4 Research §3 & §6:
  - §3.1 Quantitative Cigarette Smoking Biomarker Model (AHRR cg05575921, F2RL3 cg03636183, ALPPL2 cg01940273 & Pack-Years)
  - §3.2 Epigenetic Body Mass Index (BMI) Model (ABCG1 cg06500161, CPT1A cg00574958, SREBF1 cg11024682)
  - Alcohol Exposure Index (SLC6A3) & Circadian Diurnal Time-of-Deposition (PER2 / BMAL1)
  - Biological Age Acceleration (Delta Age)
"""

import math
from dataclasses import dataclass
from typing import Dict, Any, Optional, Union


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class SmokingProfile:
    ahrr_beta: float
    f2rl3_beta: float
    alppl2_beta: float
    smoking_score: float
    smoking_status: str
    smoking_probability: float
    estimated_pack_years: float


@dataclass
class EpigeneticBmiProfile:
    abcg1_beta: float
    cpt1a_beta: float
    srebf1_beta: float
    estimated_bmi: float
    bmi_category: str


@dataclass
class LifestyleComprehensiveResult:
    smoking: SmokingProfile
    bmi: EpigeneticBmiProfile
    alcohol_index_score: float
    alcohol_exposure_level: str
    circadian_phase: str
    estimated_tod_window: str
    age_acceleration_delta: Optional[float]
    aging_status: str
    biomarker_panel: str
    prosecutors_fallacy_shield: str


# ── Engine ─────────────────────────────────────────────────────────────────────

class LifestyleEpigeneticEngine:
    """
    FORENZA Forensic Environmental Epigenetics & Lifestyle Biomarkers Engine.

    Derives verbatim from Pillar 4 Research §3.
    """

    # Baseline defaults for never-smokers and normal BMI subjects (Research §3 & §6)
    DEFAULT_F2RL3_BETA = 0.82
    DEFAULT_ALPPL2_BETA = 0.84
    DEFAULT_ABCG1_BETA = 0.35
    DEFAULT_CPT1A_BETA = 0.45
    DEFAULT_SREBF1_BETA = 0.30

    def analyze_lifestyle_profile(
        self,
        ahrr_cg05575921_beta: float = 0.85,
        f2rl3_beta: Optional[float] = None,
        alppl2_beta: Optional[float] = None,
        abcg1_beta: Optional[float] = None,
        cpt1a_beta: Optional[float] = None,
        srebf1_beta: Optional[float] = None,
        slc6a3_beta: Optional[float] = 0.50,
        per2_beta: Optional[float] = 0.40,
        bmal1_beta: Optional[float] = 0.60,
        chronological_age: Optional[float] = None,
        estimated_dnam_age: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Calculates quantitative smoking score, pack-years, epigenetic BMI,
        alcohol exposure index, circadian TOD window, and age acceleration delta.
        """
        # Validate AHRR
        ahrr = float(ahrr_cg05575921_beta)
        if not (0.0 <= ahrr <= 1.0):
            raise ValueError(f"AHRR cg05575921 beta value must be within [0.0, 1.0], got {ahrr}.")

        # Fill multi-marker smoking defaults
        f2rl3 = float(f2rl3_beta) if f2rl3_beta is not None else self.DEFAULT_F2RL3_BETA
        alppl2 = float(alppl2_beta) if alppl2_beta is not None else self.DEFAULT_ALPPL2_BETA

        for locus_name, val in [("F2RL3", f2rl3), ("ALPPL2", alppl2)]:
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"{locus_name} beta value must be within [0.0, 1.0], got {val}.")

        # ── 1. Quantitative Cigarette Smoking Biomarker Model (Research §3.1) ──
        # Score_smoke = 10.50 - 9.80*AHRR - 2.50*F2RL3 - 1.80*ALPPL2
        smoking_score = 10.50 - 9.80 * ahrr - 2.50 * f2rl3 - 1.80 * alppl2
        smoking_score_rounded = round(smoking_score, 2)

        # Pack-Years = max(0.0, (0.85 - beta_AHRR) / 0.012)
        pack_years_est = max(0.0, round((0.85 - ahrr) / 0.012, 1))

        if ahrr < 0.55 or smoking_score > 4.50:
            smoking_status = "CURRENT_HEAVY_SMOKER"
            smoking_probability = round(min(0.99, max(0.85, 0.75 + max(0.0, smoking_score - 4.50) * 0.12)), 2)
        elif ahrr < 0.80 or smoking_score >= 1.50:
            smoking_status = "FORMER_OR_LIGHT_SMOKER"
            smoking_probability = 0.75
        else:
            smoking_status = "NON_SMOKER"
            smoking_probability = round(min(0.95, max(0.05, ahrr * 0.98)), 2)
            pack_years_est = 0.0


        # ── 2. Epigenetic Body Mass Index (BMI) Model (Research §3.2) ──
        # BMI = 24.50 + 18.20*ABCG1 - 22.40*CPT1A + 12.10*SREBF1
        abcg1 = float(abcg1_beta) if abcg1_beta is not None else self.DEFAULT_ABCG1_BETA
        cpt1a = float(cpt1a_beta) if cpt1a_beta is not None else self.DEFAULT_CPT1A_BETA
        srebf1 = float(srebf1_beta) if srebf1_beta is not None else self.DEFAULT_SREBF1_BETA

        for locus_name, val in [("ABCG1", abcg1), ("CPT1A", cpt1a), ("SREBF1", srebf1)]:
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"{locus_name} beta value must be within [0.0, 1.0], got {val}.")

        estimated_bmi = round(24.50 + 18.20 * abcg1 - 22.40 * cpt1a + 12.10 * srebf1, 1)

        if estimated_bmi < 18.5:
            bmi_category = "UNDERWEIGHT"
        elif estimated_bmi < 25.0:
            bmi_category = "NORMAL_WEIGHT"
        elif estimated_bmi < 30.0:
            bmi_category = "OVERWEIGHT"
        elif estimated_bmi < 35.0:
            bmi_category = "OBESITY_CLASS_1"
        else:
            bmi_category = "OBESITY_CLASS_2_PLUS"

        # ── 3. Alcohol Exposure Index (SLC6A3 Biomarker) ──
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

        # ── 4. Circadian Time-of-Deposition (TOD) Phase Shift (PER2 vs BMAL1) ──
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

        # ── 5. Epigenetic Age Acceleration (Delta Age) (Research §3.2) ──
        age_acceleration_delta: Optional[float] = None
        aging_status = "NORMAL_AGING"
        if chronological_age is not None and estimated_dnam_age is not None:
            age_acceleration_delta = round(float(estimated_dnam_age) - float(chronological_age), 1)
            if age_acceleration_delta > 5.0:
                aging_status = "ACCELERATED_BIOLOGICAL_AGING"
            elif age_acceleration_delta < -5.0:
                aging_status = "DECELERATED_BIOLOGICAL_AGING"

        shield_statement = (
            "IMPORTANT (Lifestyle & Environmental Epigenetics Legal Shield): Epigenetic biomarkers reflect physiological "
            "exposure signatures (AHRR tobacco smoke, ABCG1/CPT1A metabolic BMI, SLC6A3 alcohol, and PER2/BMAL1 circadian rhythm). "
            "These models provide probabilistic lifestyle inferences and must NOT be used as medical diagnoses."
        )

        return {
            "ahrr_methylation_beta": ahrr,
            "f2rl3_methylation_beta": f2rl3,
            "alppl2_methylation_beta": alppl2,
            "smoking_score": smoking_score_rounded,
            "smoking_status": smoking_status,
            "smoking_probability": smoking_probability,
            "estimated_pack_years": pack_years_est,
            "abcg1_methylation_beta": abcg1,
            "cpt1a_methylation_beta": cpt1a,
            "srebf1_methylation_beta": srebf1,
            "estimated_bmi": estimated_bmi,
            "bmi_category": bmi_category,
            "alcohol_index_score": alcohol_index_score,
            "alcohol_exposure_level": alcohol_exposure_level,
            "circadian_phase": circadian_phase,
            "estimated_tod_window": tod_window,
            "age_acceleration_delta": age_acceleration_delta,
            "aging_status": aging_status,
            "biomarker_panel": "AHRR (cg05575921) + F2RL3 + ALPPL2 + ABCG1 + CPT1A + SREBF1 + SLC6A3 + PER2/BMAL1",
            "prosecutors_fallacy_shield": shield_statement,
        }
