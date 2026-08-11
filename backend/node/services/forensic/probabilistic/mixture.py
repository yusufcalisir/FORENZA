"""
2-Person and 3-Person DNA Mixture Deconvolution Engine.
Deconvolutes complex multi-contributor EPG profiles into candidate genotype pairs
and estimates mixture proportions (Mx).
"""

from dataclasses import dataclass, field
import math
from typing import Dict, List, Optional, Set, Tuple
from .peak_model import PeakHeightModel
from ..models import STRGenotype, STRProfile, SampleType


@dataclass
class MixtureContributor:
    """Represents a contributor in a mixture with estimated mixture ratio (Mx)."""
    contributor_id: str
    mixture_ratio: float  # e.g., 0.70 for major, 0.30 for minor
    profile: Optional[STRProfile] = None


@dataclass
class DeconvolutedGenotypePair:
    """A candidate genotype combination for contributors at a single locus with posterior probability."""
    major_genotype: Tuple[float, float]
    minor_genotype: Tuple[float, float]
    posterior_probability: float
    log_likelihood: float


class MixtureDeconvolutionEngine:
    """Performs semi-continuous and continuous deconvolution of 2-person & 3-person mixtures."""

    def __init__(self, peak_model: Optional[PeakHeightModel] = None):
        self.peak_model = peak_model or PeakHeightModel()

    def deconvolute_2person_locus(
        self,
        locus_name: str,
        observed_alleles_with_heights: Dict[float, float],
        major_ratio: float = 0.70
    ) -> List[DeconvolutedGenotypePair]:
        """
        Deconvolutes a 2-person mixture at a single locus.
        Evaluates candidate major/minor genotype combinations.
        """
        minor_ratio = 1.0 - major_ratio
        alleles = list(observed_alleles_with_heights.keys())
        total_rfu = sum(observed_alleles_with_heights.values())

        if not alleles:
            return []

        # Generate candidate genotype pairs from observed alleles
        candidate_pairs: List[Tuple[Tuple[float, float], Tuple[float, float]]] = []
        for i in range(len(alleles)):
            for j in range(i, len(alleles)):
                g_maj = (alleles[i], alleles[j])
                for m1 in range(len(alleles)):
                    for m2 in range(m1, len(alleles)):
                        g_min = (alleles[m1], alleles[m2])
                        # Candidate must cover all observed alleles
                        covered = set(g_maj) | set(g_min)
                        if covered == set(alleles):
                            candidate_pairs.append((g_maj, g_min))

        scored_candidates: List[DeconvolutedGenotypePair] = []
        log_likelihoods: List[float] = []

        for g_maj, g_min in candidate_pairs:
            # Predict expected allele heights
            exp_heights: Dict[float, float] = {a: 0.0 for a in alleles}
            for a in g_maj:
                exp_heights[a] += (total_rfu * major_ratio / 2.0)
            for a in g_min:
                exp_heights[a] += (total_rfu * minor_ratio / 2.0)

            # Sum log-likelihood across alleles
            ll = 0.0
            for a, obs_h in observed_alleles_with_heights.items():
                exp_h = exp_heights[a]
                ll += self.peak_model.log_likelihood(locus_name, obs_h, exp_h)

            log_likelihoods.append(ll)

        # Normalize posterior probabilities using log-sum-exp
        if not log_likelihoods:
            return []

        max_ll = max(log_likelihoods)
        unnorm_probs = [math.exp(ll - max_ll) for ll in log_likelihoods]
        total_p = sum(unnorm_probs)

        for (g_maj, g_min), ll, p in zip(candidate_pairs, log_likelihoods, unnorm_probs):
            norm_p = p / total_p if total_p > 0 else 1.0 / len(candidate_pairs)
            scored_candidates.append(
                DeconvolutedGenotypePair(
                    major_genotype=g_maj,
                    minor_genotype=g_min,
                    posterior_probability=norm_p,
                    log_likelihood=ll
                )
            )

        # Sort by posterior probability descending
        scored_candidates.sort(key=lambda x: x.posterior_probability, reverse=True)
        return scored_candidates
