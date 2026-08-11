"""
Peak Height & Stutter Artifact Model for Continuous Probabilistic Genotyping.
Models quantitative EPG signals using log-normal height variance distributions and
locus-specific n-1 stutter slopes.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, Optional

# Standard locus-specific n-1 stutter ratio slopes (R_l)
DEFAULT_STUTTER_SLOPES: Dict[str, float] = {
    "CSF1PO": 0.065, "FGA": 0.088, "TH01": 0.025, "TPOX": 0.042, "VWA": 0.078,
    "D3S1358": 0.082, "D5S818": 0.068, "D7S820": 0.062, "D8S1179": 0.074, "D13S317": 0.061,
    "D16S539": 0.079, "D18S51": 0.092, "D21S11": 0.085, "D1S1656": 0.095, "D2S1338": 0.089,
    "D10S1248": 0.071, "D12S391": 0.112, "D19S433": 0.076, "D22S1045": 0.058, "AMEL": 0.010
}


@dataclass
class StutterModel:
    """Locus-specific n-1 stutter artifact prediction model."""
    stutter_slopes: Dict[str, float] = field(default_factory=lambda: dict(DEFAULT_STUTTER_SLOPES))

    def predict_stutter_height(self, locus_name: str, parent_height_rfu: float) -> float:
        """Predicts expected n-1 stutter peak height for a given parent allele."""
        slope = self.stutter_slopes.get(locus_name.upper(), 0.07)
        return slope * parent_height_rfu


@dataclass
class PeakHeightModel:
    """
    Log-Normal Peak Height Distribution Model.
    ln(h_observed) ~ N(ln(mu_expected), sigma^2 / mu_expected^gamma)
    """
    sigma: float = 0.35  # Height variance scale parameter
    gamma: float = 0.50  # Heteroscedasticity power parameter
    stutter_model: StutterModel = field(default_factory=StutterModel)

    def log_likelihood(
        self,
        locus_name: str,
        observed_height: float,
        expected_height: float
    ) -> float:
        """Calculates log-likelihood of an observed peak height given expected height."""
        if observed_height <= 0 or expected_height <= 0:
            return -100.0

        variance = (self.sigma ** 2) / (expected_height ** self.gamma)
        variance = max(0.01, variance)

        ln_obs = math.log(observed_height)
        ln_exp = math.log(expected_height)

        residual = ln_obs - ln_exp
        log_pdf = -0.5 * math.log(2 * math.pi * variance) - (residual ** 2) / (2 * variance)
        return log_pdf
