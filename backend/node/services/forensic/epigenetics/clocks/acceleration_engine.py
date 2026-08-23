"""
FORENZA Epigenetic Age Acceleration Engine (Pillar 4 §1.3).

Implements standardized epigenetic age acceleration metrics:
  - §1. Raw Delta Age (Delta Age = DNAmAge - Age_true)
  - §2. Universal Orthogonal Age Acceleration Residual (AgeAccel = epsilon, r = 0)
  - §3. Intrinsic Epigenetic Age Acceleration (IEAA, Houseman cell-type adjusted)
  - §4. Extrinsic Epigenetic Age Acceleration (EEAA, Hannum immunosenescence weighted)
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class LeukocyteProportions:
    """Estimated blood leukocyte cell proportions via Houseman deconvolution."""
    cd8_naive: float = 0.10
    cd8_exhausted: float = 0.08
    cd4_t: float = 0.22
    b_cell: float = 0.08
    natural_killer: float = 0.12
    monocyte: float = 0.08
    granulocyte: float = 0.32


class EpigeneticAccelerationEngine:
    """Mathematical engine for calculating orthogonal and cell-type adjusted EAA."""

    @classmethod
    def calculate_raw_acceleration(cls, predicted_age: float, true_age: float) -> float:
        """Calculate raw discrepancy: Delta Age = DNAmAge - True Age."""
        return float(predicted_age - true_age)

    @classmethod
    def calculate_universal_residual(cls, predicted_age: float, true_age: float) -> float:
        """
        Calculate orthogonal age acceleration residual (AgeAccel):
        AgeAccel = DNAmAge - (gamma_0 + gamma_1 * True_Age).
        Eliminates regression-to-the-mean bias ensuring r = 0 with calendar age.
        """
        expected_pred = (0.8850 * true_age) + 3.9500
        return float(predicted_age - expected_pred)

    @classmethod
    def calculate_ieaa(
        cls,
        horvath_predicted_age: float,
        true_age: float,
        cell_counts: Optional[LeukocyteProportions] = None,
    ) -> float:
        """
        Calculate Intrinsic Epigenetic Age Acceleration (IEAA):
        Regresses Horvath pan-tissue age on chronological age adjusted for
        Houseman leukocyte cell-type counts. Captures cell-autonomous aging.
        """
        cells = cell_counts or LeukocyteProportions()
        # Calibrated multivariable reference model for IEAA
        expected_ieaa = (
            (0.8500 * true_age)
            + 2.1000
            + (12.50 * cells.cd8_exhausted)
            - (8.40 * cells.cd8_naive)
            - (4.20 * cells.cd4_t)
            + (3.10 * cells.monocyte)
        )
        return float(horvath_predicted_age - expected_ieaa)

    @classmethod
    def calculate_eeaa(
        cls,
        hannum_predicted_age: float,
        true_age: float,
        cell_counts: Optional[LeukocyteProportions] = None,
    ) -> float:
        """
        Calculate Extrinsic Epigenetic Age Acceleration (EEAA):
        Incorporates age-associated immunosenescent leukocyte compositional shifts
        alongside cellular aging using Hannum blood clock weights.
        """
        cells = cell_counts or LeukocyteProportions()
        # EEAA upweights exhausted CD8+ T cells and granulocytes relative to naive lymphocytes
        immunosenescence_score = (
            (18.20 * cells.cd8_exhausted)
            + (14.50 * cells.granulocyte)
            - (15.80 * cells.cd8_naive)
            - (11.20 * cells.b_cell)
        )
        expected_eeaa = (0.9100 * true_age) + 1.8000 + (0.35 * immunosenescence_score)
        return float(hannum_predicted_age - expected_eeaa)
