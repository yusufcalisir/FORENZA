"""
FORENZA Forensic Toxicology Engine & Quantitative Measurement Uncertainty Calculator.
Evaluates drug and metabolite concentrations across sample matrices (Blood, Urine, Vitreous Humor, Hair).
Maps concentrations to toxicological reference ranges (THERAPEUTIC, TOXIC, FATAL_LETHAL).
Calculates ISO/IEC 17025 expanded measurement uncertainty:
  U_95% = k * u_c = 2 * sqrt(u_cal^2 + u_rep^2 + u_matrix^2)

References:
  Baselt RC (2020) Disposition of Toxic Drugs and Chemicals in Man.
  SOFT/AAFS Forensic Toxicology Laboratory Guidelines (2021).
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class ToxicologicalAnalyte:
    analyte_name: str                  # e.g. 'Ethanol', 'Morphine', 'Fentanyl', 'Cocaine', 'Benzoylecgonine'
    matrix_type: str                   # 'WHOLE_BLOOD', 'URINE', 'VITREOUS_HUMOR', 'HAIR', 'LIVER_TISSUE'
    measured_concentration: float      # Measured value (mg/L or ng/mL)
    unit: str                          # 'mg/L', 'g/dL', 'ng/mL'
    u_cal_rel: float = 0.03            # Relative calibration uncertainty (3%)
    u_rep_rel: float = 0.04            # Relative repeatability uncertainty (4%)
    u_matrix_rel: float = 0.02         # Relative matrix effect uncertainty (2%)


@dataclass
class AnalyteQuantitativeReport:
    analyte_name: str
    matrix_type: str
    measured_concentration: float
    expanded_uncertainty_95: float    # U_95% = k * u_c (k=2)
    concentration_formatted: str       # e.g. '0.85 ± 0.09 mg/L'
    toxicological_classification: str # 'THERAPEUTIC', 'TOXIC', 'FATAL_LETHAL'
    reference_range_description: str


@dataclass
class ToxicologyScreenResult:
    sample_id: str
    analyte_reports: List[AnalyteQuantitativeReport]
    toxicology_summary: str


# Reference Toxicological Thresholds (mg/L in blood)
TOXICOLOGICAL_DB = {
    "Morphine": {"therapeutic": 0.08, "toxic": 0.20, "fatal": 0.50},
    "Fentanyl": {"therapeutic": 0.003, "toxic": 0.010, "fatal": 0.020},
    "Cocaine": {"therapeutic": 0.10, "toxic": 0.50, "fatal": 1.00},
    "Ethanol": {"therapeutic": 0.00, "toxic": 1.50, "fatal": 3.50}, # g/L
}


class ForensicToxicologyEngine:
    """
    Classifies quantitative toxicology screening results with ISO 17025 expanded measurement uncertainty.
    """

    def screen_analytes(self, sample_id: str, analytes: List[ToxicologicalAnalyte]) -> ToxicologyScreenResult:
        reports: List[AnalyteQuantitativeReport] = []

        for a in analytes:
            c = a.measured_concentration

            # Expanded Uncertainty U = 2 * c * sqrt(u_cal^2 + u_rep^2 + u_matrix^2)
            u_combined_rel = math.sqrt(a.u_cal_rel**2 + a.u_rep_rel**2 + a.u_matrix_rel**2)
            u_expanded = round(2.0 * c * u_combined_rel, 4)
            formatted = f"{c:.2f} ± {u_expanded:.2f} {a.unit}"

            ref = TOXICOLOGICAL_DB.get(a.analyte_name, {"therapeutic": 0.1, "toxic": 0.5, "fatal": 1.0})

            if c >= ref["fatal"]:
                cls = "FATAL_LETHAL"
                desc = f"Concentration exceeds lethal threshold ({ref['fatal']} {a.unit}). High risk of acute toxicity."
            elif c >= ref["toxic"]:
                cls = "TOXIC"
                desc = f"Concentration falls within toxic range ({ref['toxic']} to {ref['fatal']} {a.unit})."
            else:
                cls = "THERAPEUTIC"
                desc = f"Concentration falls within therapeutic or sub-toxic window (< {ref['toxic']} {a.unit})."

            reports.append(AnalyteQuantitativeReport(
                analyte_name=a.analyte_name,
                matrix_type=a.matrix_type,
                measured_concentration=c,
                expanded_uncertainty_95=u_expanded,
                concentration_formatted=formatted,
                toxicological_classification=cls,
                reference_range_description=desc
            ))

        summary = f"Toxicology Screening Complete for {sample_id}: Analyzed {len(analytes)} analytes with ISO 17025 U_95% uncertainty."

        return ToxicologyScreenResult(
            sample_id=sample_id,
            analyte_reports=reports,
            toxicology_summary=summary
        )
