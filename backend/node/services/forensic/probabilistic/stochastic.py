"""
Stochastic Dropout & Drop-in Models for Low-Template DNA Analysis.
Implements logistic dropout curves and Poisson/exponential drop-in models.
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class DropoutModel:
    """
    Logistic Dropout Probability Model.
    P(D | x) = 1 / (1 + exp(beta0 + beta1 * x))
    where x is DNA concentration or average peak height (RFU).
    """
    beta0: float = -3.5  # Baseline intercept parameter
    beta1: float = 0.015  # RFU scale coefficient

    def calculate_dropout_probability(self, peak_height_rfu: float) -> float:
        """Calculates probability of allele dropout P(D) given peak height RFU."""
        if peak_height_rfu <= 0:
            return 0.999
        exponent = self.beta0 + (self.beta1 * peak_height_rfu)
        # Bounded sigmoid to avoid overflow
        exponent = max(-20.0, min(20.0, exponent))
        p_d = 1.0 / (1.0 + math.exp(exponent))
        return min(0.999, max(0.001, p_d))


@dataclass
class DropInModel:
    """
    Poisson & Exponential Drop-in Contamination Model.
    - Drop-in count follows Poisson(lambda_c)
    - Drop-in height above Analytical Threshold (AT) follows Exponential(lambda_h)
    """
    lambda_c: float = 0.05  # Average drop-in events per locus
    lambda_h: float = 0.02  # Exponential scale parameter for height
    analytical_threshold: float = 50.0  # RFU cutoff

    def count_probability(self, k_events: int) -> float:
        """Calculates Poisson probability of observing k drop-in events at a locus."""
        if k_events < 0:
            return 0.0
        return (self.lambda_c ** k_events) * math.exp(-self.lambda_c) / math.factorial(k_events)

    def height_density(self, height_rfu: float) -> float:
        """Calculates probability density of observing a drop-in peak of height_rfu."""
        if height_rfu < self.analytical_threshold:
            return 0.0
        delta = height_rfu - self.analytical_threshold
        return self.lambda_h * math.exp(-self.lambda_h * delta)


class StochasticModel:
    """Combined stochastic model evaluator for a locus."""

    def __init__(
        self,
        dropout_model: DropoutModel = DropoutModel(),
        dropin_model: DropInModel = DropInModel()
    ):
        self.dropout = dropout_model
        self.dropin = dropin_model

    def evaluate_allele_stochasticity(self, peak_height_rfu: float) -> Dict[str, float]:
        """Returns stochastic metrics for an observed allele."""
        p_d = self.dropout.calculate_dropout_probability(peak_height_rfu)
        p_c_1 = self.dropin.count_probability(1)
        h_density = self.dropin.height_density(peak_height_rfu)
        return {
            "dropout_probability": p_d,
            "dropin_count_probability": p_c_1,
            "dropin_height_density": h_density,
            "is_low_template": 1.0 if peak_height_rfu < 150.0 else 0.0
        }
