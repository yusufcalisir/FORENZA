"""
FORENZA Forensic Serology & Blood Group Antigen Engine.
Evaluates classical blood group systems (ABO, Rh, Kell, Duffy) and Lewis antigen Secretor status (Se/se).

References:
  Gaensslen RE (1983) Sourcebook in Forensic Serology, Immunology, and Biochemistry.
  ISBT (2021) Table of blood group systems and antigen frequencies.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# Standard European Population Blood Group Phenotype Frequencies
ANTIGEN_FREQUENCIES = {
    "ABO": {
        "O": 0.45,
        "A": 0.40,
        "B": 0.11,
        "AB": 0.04,
    },
    "Rh": {
        "D+": 0.85,
        "D-": 0.15,
    },
    "Kell": {
        "K+": 0.09,
        "K-": 0.91,
    },
    "Duffy": {
        "Fya+": 0.66,
        "Fyb+": 0.83,
    },
    "Lewis": {
        "Lea-b+": 0.72, # Secretor (Se)
        "Lea+b-": 0.22, # Non-secretor (se)
        "Lea-b-": 0.06, # Secretor/Non-secretor variant
    }
}


@dataclass
class SerologicalPhenotypeData:
    sample_id: str
    abo_group: str                      # 'A', 'B', 'AB', 'O'
    rh_factor: str                      # 'D+', 'D-'
    kell_status: Optional[str] = "K-"   # 'K+', 'K-'
    lewis_phenotype: Optional[str] = "Lea-b+" # 'Lea-b+', 'Lea+b-', 'Lea-b-'


@dataclass
class SerologicalEvaluationResult:
    sample_id: str
    abo_group: str
    rh_factor: str
    secretor_status: str               # 'SECRETOR', 'NON_SECRETOR'
    combined_serology_frequency: float # Combined population phenotype frequency
    serology_likelihood_ratio: float   # LR_serology = 1 / frequency
    serology_summary: str


class ForensicSerologyEngine:
    """
    Evaluates classical serological antigen profiles and secretor phenotypes.
    """

    def evaluate_phenotype(self, sample: SerologicalPhenotypeData) -> SerologicalEvaluationResult:
        f_abo = ANTIGEN_FREQUENCIES["ABO"].get(sample.abo_group.upper(), 0.45)
        f_rh = ANTIGEN_FREQUENCIES["Rh"].get(sample.rh_factor.upper(), 0.85)
        f_kell = ANTIGEN_FREQUENCIES["Kell"].get(sample.kell_status, 0.91) if sample.kell_status else 1.0

        f_comb = round(f_abo * f_rh * f_kell, 4)
        lr_serology = round(1.0 / max(1e-6, f_comb), 2)

        # Secretor status from Lewis phenotype
        if sample.lewis_phenotype == "Lea-b+":
            secretor = "SECRETOR"
        elif sample.lewis_phenotype == "Lea+b-":
            secretor = "NON_SECRETOR"
        else:
            secretor = "SECRETOR_VARIANT"

        summary = (
            f"Serological Evaluation for {sample.sample_id}: "
            f"Group {sample.abo_group} {sample.rh_factor} ({secretor}). "
            f"Population Frequency = {f_comb*100:.2f}%, LR_serology = {lr_serology}."
        )

        return SerologicalEvaluationResult(
            sample_id=sample.sample_id,
            abo_group=sample.abo_group.upper(),
            rh_factor=sample.rh_factor.upper(),
            secretor_status=secretor,
            combined_serology_frequency=f_comb,
            serology_likelihood_ratio=lr_serology,
            serology_summary=summary
        )
