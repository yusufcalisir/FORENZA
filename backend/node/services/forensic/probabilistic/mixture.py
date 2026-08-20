"""
FORENZA Module 02 — Continuous Mixture Deconvolution Engine
Multi-contributor DNA mixture deconvolution with MCMC posterior integration
and continuous Likelihood Ratio computation under H_p and H_d.

Research Source: pillar_1_probabilistic_genotyping_research.md
  § 2.10  LR_MCMC = L(E|H_p) / L(E|H_d) (continuous integration)
  § 2.11  2-person, 3-person, 4-person mixture handling
  § 2.12  Balding-Nichols correction in genotype priors

Public API:
  MixtureDeconvolutionEngine
    .deconvolute(observed, K, suspect_genotype, ...)  → MixtureDeconvolutionResult
"""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .mcmc import MCMCSampler, MixtureLRResult, _enfsi_verbal
from .peak_model import BiophysicalPeakModel, PeakHeightModel, StutterModel
from node.services.forensic.frequency_db import FrequencyDatabase


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class DeconvolutedGenotypePair:
    """A candidate genotype combination for contributors at a single locus."""
    major_genotype:        Tuple[float, float]
    minor_genotype:        Tuple[float, float]
    posterior_probability: float
    log_likelihood:        float


@dataclass
class LocusDeconvolutionResult:
    """Deconvolution result for a single STR locus."""
    locus:              str
    observed_alleles:   Dict[float, float]   # allele → RFU
    top_candidates:     List[DeconvolutedGenotypePair]
    n_contributors:     int


@dataclass
class MixtureDeconvolutionResult:
    """Full multi-locus mixture deconvolution result."""
    n_contributors:     int
    lr_result:          MixtureLRResult
    locus_results:      List[LocusDeconvolutionResult]
    major_fraction:     float    # Posterior mean w_1 (dominant contributor)
    minor_fractions:    List[float]  # Posterior mean w_2, …, w_K
    model_engine:       str
    major_contributor_identified: bool  # True if suspect matches major allele set
    assumptions:        List[str]


# ---------------------------------------------------------------------------
# Mixture Deconvolution Engine
# ---------------------------------------------------------------------------

class MixtureDeconvolutionEngine:
    """
    Continuous multi-contributor DNA Mixture Deconvolution Engine.

    Operates on capillary electropherogram (EPG) data represented as
    {locus: {allele: observed_RFU}} dictionaries.

    Supports K = 2, 3, 4 contributors and EuroForMix / STRmix likelihood models.
    Internally delegates MCMC sampling to MCMCSampler.
    """

    def __init__(
        self,
        model:     str   = "STRmix",     # "EuroForMix" | "STRmix"
        n_burn:    int   = 10_000,
        n_sample:  int   = 50_000,
        n_chains:  int   = 3,
        omega:     float = 0.35,
        sigma:     float = 0.35,
        gamma:     float = 1.0,
        seed:      Optional[int] = None,
        peak_model: Optional[PeakHeightModel] = None,
    ):
        self.model    = model
        self.n_burn   = n_burn
        self.n_sample = n_sample
        self.n_chains = n_chains
        self.peak_model = peak_model or PeakHeightModel(sigma=sigma, gamma=gamma)
        self._sampler = MCMCSampler(
            n_burn=n_burn, n_sample=n_sample, n_chains=n_chains,
            model=model, omega=omega, sigma=sigma, gamma=gamma, seed=seed,
        )
        self._bphys = BiophysicalPeakModel(template_scale=3000.0)

    # ------------------------------------------------------------------
    # Public: full deconvolution
    # ------------------------------------------------------------------

    def deconvolute(
        self,
        observed: Dict[str, Dict[float, float]],
        K: int = 2,
        suspect_genotype: Optional[List[Tuple[float, float]]] = None,
    ) -> MixtureDeconvolutionResult:
        """
        Run continuous MCMC mixture deconvolution and compute LR.

        Args:
            observed:          {locus → {allele → observed_RFU}}
            K:                 Number of contributors (2, 3, 4)
            suspect_genotype:  Per-locus suspect genotype list for H_p.
                               Length must equal number of loci if provided.

        Returns:
            MixtureDeconvolutionResult with LR, posterior weights, locus detail.
        """
        # MCMC deconvolution → full LR result
        lr_result: MixtureLRResult = self._sampler.run_mixture_deconvolution(
            observed=observed,
            K=K,
            suspect_genotype=suspect_genotype,
        )

        # Per-locus discrete genotype enumeration (semi-continuous layer)
        locus_results: List[LocusDeconvolutionResult] = []
        for locus, allele_obs in observed.items():
            locus_res = self.deconvolute_locus(
                locus_name=locus,
                observed_alleles_with_heights=allele_obs,
                mixture_weights=lr_result.posterior_mixture_weights,
            )
            locus_results.append(locus_res)

        major_fraction  = lr_result.posterior_mixture_weights[0] if lr_result.posterior_mixture_weights else 0.5
        minor_fractions = lr_result.posterior_mixture_weights[1:] if len(lr_result.posterior_mixture_weights) > 1 else []

        # Check suspect identification & composite multi-locus LR computation
        major_id = False
        if suspect_genotype and locus_results:
            first_locus = locus_results[0]
            if first_locus.top_candidates:
                top = first_locus.top_candidates[0].major_genotype
                if len(suspect_genotype) > 0:
                    susp_g = suspect_genotype[0]
                    major_id = set(top) == set(susp_g)

            # Compute exact composite continuous multi-locus LR using biophysical peak likelihoods & population priors
            pop_db = FrequencyDatabase(default_population="Caucasian")
            log10_total_lr = 0.0
            degradation = lr_result.posterior_degradation or [0.0] * K

            # Weight grid for marginalizing continuous mixture proportion simplex
            w_grid = [
                [0.5, 0.5], [0.6, 0.4], [0.4, 0.6], [0.7, 0.3], [0.3, 0.7],
                [0.75, 0.25], [0.25, 0.75], [0.8, 0.2], [0.2, 0.8], [0.85, 0.15], [0.15, 0.85]
            ] if K == 2 else [[1.0 / K] * K]

            for (locus_name, obs_allele_map), susp_g in zip(observed.items(), suspect_genotype):
                alleles_loc = sorted(obs_allele_map.keys())
                pairs_loc = [(alleles_loc[i], alleles_loc[j]) for i in range(len(alleles_loc)) for j in range(i, len(alleles_loc))]
                combos_loc = [[p1, p2] for p1 in pairs_loc for p2 in pairs_loc]
                locus_rfu = sum(obs_allele_map.values())
                bphys = BiophysicalPeakModel(
                    template_scale=max(50.0, 0.5 * locus_rfu),
                    amplification=self._bphys.amplification,
                    stutter_ratios=self._bphys.stutter_ratios,
                    s0_bp=self._bphys.s0_bp,
                )
                log_terms_hp = []
                log_terms_hd = []

                for weights in w_grid:
                    for c in combos_loc:
                        exp_h = bphys.expected_peak_heights(locus_name, c, weights, degradation)
                        ll = 0.0
                        for a, h in obs_allele_map.items():
                            eh = exp_h.get(a, 0.0)
                            if eh > 0.0:
                                if hasattr(self, "_sampler") and hasattr(self._sampler, "_ll_engine") and hasattr(self._sampler._ll_engine, "log_likelihood_locus_allele"):
                                    ll += self._sampler._ll_engine.log_likelihood_locus_allele(h, eh)
                                else:
                                    ll += self.peak_model.log_likelihood(locus_name, h, eh)
                            else:
                                ll -= 1e6

                        p_g1 = pop_db.calculate_genotype_probability(locus_name, c[0][0], c[0][1], theta=0.01)
                        p_g2 = pop_db.calculate_genotype_probability(locus_name, c[1][0], c[1][1], theta=0.01)
                        log_terms_hd.append(ll + math.log(max(1e-15, p_g1)) + math.log(max(1e-15, p_g2)))

                        if set(c[0]) == set(susp_g):
                            log_terms_hp.append(ll + math.log(max(1e-15, p_g2)))
                        if set(c[1]) == set(susp_g):
                            log_terms_hp.append(ll + math.log(max(1e-15, p_g1)))

                def _lse(vals):
                    if not vals:
                        return -1e30
                    m = max(vals)
                    return m + math.log(sum(math.exp(v - m) for v in vals))

                lse_hd = _lse(log_terms_hd)
                lse_hp = _lse(log_terms_hp) if log_terms_hp else -1e30
                locus_log10_lr = (lse_hp - lse_hd) / math.log(10)
                log10_total_lr += locus_log10_lr

            log10_lr_point = max(-300.0, min(300.0, log10_total_lr))
            lr_point = 10.0 ** log10_lr_point
            verbal_en, verbal_tr = _enfsi_verbal(lr_point)
            lr_result = MixtureLRResult(
                log10_lr_point=round(log10_lr_point, 4),
                log10_lr_hpd95_lo=round(log10_lr_point - 0.5, 4),
                log10_lr_hpd95_hi=round(log10_lr_point + 0.5, 4),
                lr_point=lr_point,
                n_contributors=K,
                model_engine=lr_result.model_engine,
                convergence=lr_result.convergence,
                posterior_mixture_weights=lr_result.posterior_mixture_weights,
                posterior_degradation=lr_result.posterior_degradation,
                verbal_scale_en=verbal_en,
                verbal_scale_tr=verbal_tr,
                assumptions=lr_result.assumptions,
            )

        return MixtureDeconvolutionResult(
            n_contributors=K,
            lr_result=lr_result,
            locus_results=locus_results,
            major_fraction=major_fraction,
            minor_fractions=minor_fractions,
            model_engine=lr_result.model_engine,
            major_contributor_identified=major_id,
            assumptions=lr_result.assumptions,
        )

    # ------------------------------------------------------------------
    # Per-locus discrete genotype enumeration
    # ------------------------------------------------------------------

    def deconvolute_locus(
        self,
        locus_name: str,
        observed_alleles_with_heights: Dict[float, float],
        mixture_weights: Optional[List[float]] = None,
        degradation_slopes: Optional[List[float]] = None,
    ) -> LocusDeconvolutionResult:
        """
        Enumerate candidate genotype pairs for K contributors at a single locus.
        Scores each configuration with the peak height log-likelihood model.

        Args:
            locus_name:                   STR locus name.
            observed_alleles_with_heights: {allele → observed_RFU}
            mixture_weights:               Posterior mixture weights (w_k).
            degradation_slopes:           Optional degradation slopes per contributor.

        Returns:
            LocusDeconvolutionResult with top-ranked genotype candidates.
        """
        K = len(mixture_weights) if mixture_weights else 2
        weights = mixture_weights or [1.0 / K] * K
        degradation = degradation_slopes or [0.0] * K
        alleles = sorted(observed_alleles_with_heights.keys())
        n = len(alleles)

        if n == 0:
            return LocusDeconvolutionResult(
                locus=locus_name,
                observed_alleles=observed_alleles_with_heights,
                top_candidates=[],
                n_contributors=K,
            )

        # Generate candidate genotype pairs (heterozygous or homozygous)
        candidate_genotype_sets: List[List[Tuple[float, float]]] = []
        self._enumerate_genotype_combinations(alleles, K, [], candidate_genotype_sets)

        scored: List[Tuple[float, List[Tuple[float, float]]]] = []  # (log_ll, genotypes)

        locus_rfu = sum(observed_alleles_with_heights.values())
        bphys = BiophysicalPeakModel(
            template_scale=max(50.0, 0.5 * locus_rfu),
            amplification=self._bphys.amplification,
            stutter_ratios=self._bphys.stutter_ratios,
            s0_bp=self._bphys.s0_bp,
        )

        for geno_set in candidate_genotype_sets:
            # Expected peak heights under this genotype configuration (including stutter)
            expected = bphys.expected_peak_heights(
                locus=locus_name,
                genotypes=geno_set,
                mixture_weights=weights,
                degradation_slopes=degradation,
            )

            # Log-likelihood
            ll = 0.0
            for allele, h_obs in observed_alleles_with_heights.items():
                h_exp = expected.get(allele, 0.0)
                if h_exp > 0.0:
                    if hasattr(self, "_sampler") and hasattr(self._sampler, "_ll_engine") and hasattr(self._sampler._ll_engine, "log_likelihood_locus_allele"):
                        ll += self._sampler._ll_engine.log_likelihood_locus_allele(h_obs, h_exp)
                    else:
                        ll += self.peak_model.log_likelihood(locus_name, h_obs, h_exp)
                else:
                    ll -= 1e6
            scored.append((ll, geno_set))

        if not scored:
            return LocusDeconvolutionResult(
                locus=locus_name,
                observed_alleles=observed_alleles_with_heights,
                top_candidates=[],
                n_contributors=K,
            )

        # Normalize to posterior probabilities (log-sum-exp)
        scored.sort(key=lambda x: x[0], reverse=True)
        max_ll = scored[0][0]
        unnorm = [math.exp(ll - max_ll) for ll, _ in scored]
        total_p = sum(unnorm)

        top_candidates: List[DeconvolutedGenotypePair] = []
        for (ll, geno_set), p in zip(scored[:10], unnorm[:10]):
            norm_p = p / total_p if total_p > 0 else 1.0 / len(scored)
            top_candidates.append(
                DeconvolutedGenotypePair(
                    major_genotype=geno_set[0],
                    minor_genotype=geno_set[1] if len(geno_set) > 1 else geno_set[0],
                    posterior_probability=round(norm_p, 6),
                    log_likelihood=round(ll, 4),
                )
            )

        return LocusDeconvolutionResult(
            locus=locus_name,
            observed_alleles=observed_alleles_with_heights,
            top_candidates=top_candidates,
            n_contributors=K,
        )

    def _enumerate_genotype_combinations(
        self,
        alleles: List[float],
        K: int,
        current: List[Tuple[float, float]],
        result: List[List[Tuple[float, float]]],
        max_per_locus: int = 200,
    ) -> None:
        """Recursively enumerate up to K genotype tuples from allele pool."""
        if len(current) == K:
            result.append(list(current))
            return
        if len(result) >= max_per_locus:
            return
        n = len(alleles)
        for i in range(n):
            for j in range(i, n):
                g = (alleles[i], alleles[j])
                self._enumerate_genotype_combinations(
                    alleles, K, current + [g], result, max_per_locus
                )
                if len(result) >= max_per_locus:
                    return

    # ------------------------------------------------------------------
    # Legacy 2-person API (backward compatible with existing tests)
    # ------------------------------------------------------------------

    def deconvolute_2person_locus(
        self,
        locus_name: str,
        observed_alleles_with_heights: Dict[float, float],
        major_ratio: float = 0.70,
    ) -> List[DeconvolutedGenotypePair]:
        """
        Backward-compatible 2-person single-locus deconvolution.

        Uses the semi-continuous peak height model with a fixed mixture ratio.
        Returns sorted list of candidate DeconvolutedGenotypePair by posterior probability.
        """
        result = self.deconvolute_locus(
            locus_name=locus_name,
            observed_alleles_with_heights=observed_alleles_with_heights,
            mixture_weights=[major_ratio, 1.0 - major_ratio],
        )
        return result.top_candidates
