"""
FORENZA Forensic Anthropology Biological Profile Estimator.
Estimates biological profile attributes from skeletal morphometrics:
  - Sex Estimation (Pelvic subpubic angle & Greater Sciatic Notch score)
  - Age Estimation (Suchey-Brooks pubic symphysis phase mapping)
  - Stature Estimation (Trotter-Gleser linear regression equations)
  - Population Affinity (Craniometric discriminant analysis)

Reference:
  Trotter & Gleser (1958) Stature Estimation; Suchey & Brooks (1990) Age Estimation Standards.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class MorphometricMeasurements:
    femur_length_mm: Optional[float] = None        # Maximum length of femur in mm
    tibia_length_mm: Optional[float] = None        # Maximum length of tibia in mm
    pelvic_notch_score: Optional[int] = None       # Greater sciatic notch score (1=Female to 5=Male)
    subpubic_angle_deg: Optional[float] = None      # Subpubic angle (>90 deg = Female, <70 deg = Male)
    pubic_symphysis_phase: Optional[int] = None    # Suchey-Brooks phase (1 to 6)
    cranial_breadth_mm: Optional[float] = None     # Maximum cranial breadth (XCB) in mm
    cranial_length_mm: Optional[float] = None      # Maximum cranial length (GOL) in mm


@dataclass
class BiologicalProfileResult:
    estimated_sex: str                             # 'FEMALE', 'MALE', 'INDETERMINATE'
    sex_confidence: float
    estimated_age_range: str                       # e.g. '18 - 24 years'
    estimated_stature_cm: float                    # Point estimate of stature in cm
    stature_margin_error_cm: float                 # 95% prediction interval error (e.g. +/- 3.27 cm)
    stature_range_formatted: str
    population_affinity: str                       # 'European Affinity', 'African Affinity', 'Asian Affinity'
    anthropology_summary: str


class AnthropologyProfileEstimator:
    """
    Computes biological profile estimates from osteological measurements.
    """

    def estimate_biological_profile(self, measurements: MorphometricMeasurements) -> BiologicalProfileResult:
        # 1. Sex Estimation
        if measurements.subpubic_angle_deg is not None:
            if measurements.subpubic_angle_deg > 85.0:
                sex = "FEMALE"
                sex_conf = 0.92
            elif measurements.subpubic_angle_deg < 75.0:
                sex = "MALE"
                sex_conf = 0.94
            else:
                sex = "INDETERMINATE"
                sex_conf = 0.50
        elif measurements.pelvic_notch_score is not None:
            if measurements.pelvic_notch_score <= 2:
                sex = "FEMALE"
                sex_conf = 0.85
            elif measurements.pelvic_notch_score >= 4:
                sex = "MALE"
                sex_conf = 0.88
            else:
                sex = "INDETERMINATE"
                sex_conf = 0.50
        else:
            sex = "INDETERMINATE"
            sex_conf = 0.50

        # 2. Age Estimation (Suchey-Brooks Pubic Symphysis Phases)
        phase = measurements.pubic_symphysis_phase or 3
        age_ranges = {
            1: "15 - 19 years",
            2: "20 - 24 years",
            3: "25 - 34 years",
            4: "35 - 45 years",
            5: "46 - 59 years",
            6: "60+ years"
        }
        age_range = age_ranges.get(phase, "25 - 34 years")

        # 3. Stature Estimation (Trotter & Gleser Regression for Femur/Tibia)
        # Stature (cm) = 2.38 * Femur_Length (cm) + 61.41 +/- 3.27 cm (White Males/Females baseline)
        if measurements.femur_length_mm is not None:
            femur_cm = measurements.femur_length_mm / 10.0
            stature_est = round(2.38 * femur_cm + 61.41, 1)
            error_cm = 3.27
        elif measurements.tibia_length_mm is not None:
            tibia_cm = measurements.tibia_length_mm / 10.0
            stature_est = round(2.52 * tibia_cm + 78.62, 1)
            error_cm = 3.37
        else:
            stature_est = 172.5
            error_cm = 4.0

        stature_range = f"{round(stature_est - error_cm, 1)} - {round(stature_est + error_cm, 1)} cm"

        # 4. Population Affinity Estimation (Craniometric Index)
        if measurements.cranial_length_mm and measurements.cranial_breadth_mm:
            cranial_index = (measurements.cranial_breadth_mm / measurements.cranial_length_mm) * 100.0
            if cranial_index < 75.0:
                affinity = "African / Dolichocephalic Affinity"
            elif cranial_index <= 80.0:
                affinity = "European / Mesocephalic Affinity"
            else:
                affinity = "Asian / Brachycephalic Affinity"
        else:
            affinity = "European Affinity (Baseline)"

        summary = f"Biological Profile Complete: Estimated Sex={sex} (conf={int(sex_conf*100)}%), Age={age_range}, Stature={stature_est} cm ({stature_range}), Affinity={affinity}."

        return BiologicalProfileResult(
            estimated_sex=sex,
            sex_confidence=sex_conf,
            estimated_age_range=age_range,
            estimated_stature_cm=stature_est,
            stature_margin_error_cm=error_cm,
            stature_range_formatted=stature_range,
            population_affinity=affinity,
            anthropology_summary=summary
        )
