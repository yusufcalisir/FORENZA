"""
Metropolis-Hastings MCMC Sampling Engine & Tippett Plot Calibration.
Samples continuous parameter distributions and computes Tippett plot calibration metrics.
"""

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class MCMCSample:
    """A single MCMC sample iteration state."""
    iteration: int
    major_ratio: float
    sigma: float
    log_likelihood: float


class MCMCSampler:
    """Metropolis-Hastings MCMC algorithm for continuous mixture parameter estimation."""

    def __init__(self, n_iterations: int = 1000, burn_in: int = 200):
        self.n_iterations = n_iterations
        self.burn_in = burn_in

    def sample_mixture_ratio(
        self,
        initial_ratio: float = 0.50,
        proposal_std: float = 0.05
    ) -> List[MCMCSample]:
        """Samples mixture ratio distribution using Metropolis-Hastings iterations."""
        current_ratio = initial_ratio
        current_sigma = 0.35
        samples: List[MCMCSample] = []

        # Synthetic log-likelihood function for MCMC sampling
        def eval_log_likelihood(ratio: float, sigma: float) -> float:
            # Target true ratio assumed around 0.70 with gaussian log-likelihood peak
            diff = ratio - 0.70
            return -0.5 * ((diff / 0.10) ** 2) - math.log(sigma)

        current_ll = eval_log_likelihood(current_ratio, current_sigma)

        for i in range(self.n_iterations):
            # Propose candidate parameter
            proposed_ratio = current_ratio + random.gauss(0, proposal_std)
            proposed_ratio = max(0.05, min(0.95, proposed_ratio))

            proposed_ll = eval_log_likelihood(proposed_ratio, current_sigma)
            log_alpha = proposed_ll - current_ll

            # Accept/reject step
            if math.log(random.random()) < log_alpha:
                current_ratio = proposed_ratio
                current_ll = proposed_ll

            if i >= self.burn_in:
                samples.append(
                    MCMCSample(
                        iteration=i,
                        major_ratio=current_ratio,
                        sigma=current_sigma,
                        log_likelihood=current_ll
                    )
                )

        return samples


class CalibrationEngine:
    """Generates Tippett plot calibration data for validation assessment."""

    @staticmethod
    def generate_tippett_curve(
        donor_lrs: List[float],
        nondonor_lrs: List[float]
    ) -> Dict[str, List[Tuple[float, float]]]:
        """
        Calculates cumulative log10(LR) distributions for Tippett calibration plots.
        - True Donor curve: P(log10(LR) >= x | H1 is true)
        - Non-Donor curve: P(log10(LR) >= x | H2 is true)
        """
        sorted_donor = sorted([math.log10(max(1e-10, lr)) for lr in donor_lrs])
        sorted_nondonor = sorted([math.log10(max(1e-10, lr)) for lr in nondonor_lrs])

        n_donor = len(sorted_donor)
        n_nondonor = len(sorted_nondonor)

        donor_curve: List[Tuple[float, float]] = []
        for i, val in enumerate(sorted_donor):
            prob_greater_equal = (n_donor - i) / n_donor
            donor_curve.append((val, prob_greater_equal))

        nondonor_curve: List[Tuple[float, float]] = []
        for i, val in enumerate(sorted_nondonor):
            prob_greater_equal = (n_nondonor - i) / n_nondonor
            nondonor_curve.append((val, prob_greater_equal))

        return {
            "true_donor_curve": donor_curve,
            "non_donor_curve": nondonor_curve
        }
