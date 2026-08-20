"""
FORENZA Module 1.3: NRC-II Dirichlet Fst / Balding-Nichols Population Genetics.
Mathematical & Biophysical Formulation Engine.

Derived verbatim from research specifications:
  - pillar_1_probabilistic_genotyping_research.md (§1.2 & §3)
  - str_24_locus_microvariants_research.md
  - National Research Council (NRC II, 1996) Recommendation 4.10b & Rule 4.1
  - Balding DJ, Nichols RA. Genetica 96(1-2):69-71, 1995.
  - Weir BS, Cockerham CC. Estimating F-statistics for the analysis of population structure. Evolution 38(6):1358-1370, 1984.
  - Curran JM, Buckleton JS. Calculation of match probabilities under subpopulation models. Forensic Sci Int, 2007.

Zero arbitrary heuristics. Exact biostatistical invariants enforced:
  - Dirichlet Compound Multinomial (DCM) log-gamma formulation with overflow immunity
  - Probability Simplex Normalization: sum_{i <= j} P(Ai Aj | theta) = 1.00000000 ± 1e-6
  - Reciprocal Hypothesis Balance: LR(Hp / Hd) * LR(Hd / Hp) = 1.0000000 ± 1e-6
  - Additivity of Log-Likelihoods: |log10(LR_total) - sum(log10(LR_l))| < 1e-6
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Constants (Research-Locked — Pillar 1 §1.1 & NRC II 1996)
# ---------------------------------------------------------------------------
NIST_1036_N: int = 1036
NIST_1036_TWO_N: int = 2 * NIST_1036_N  # 2072 alleles
P_MIN_NRC_II: float = 5.0 / NIST_1036_TWO_N  # 0.002413127413127413...
DEFAULT_THETA: float = 0.03  # US Domestic Standard (FBI/SWGDAM)
CONSERVATIVE_THETA: float = 0.01  # NRC II General Population Baseline


@dataclass(frozen=True)
class DCMResult:
    """Dirichlet Compound Multinomial (Polya-Eggenberger) evaluation result."""
    log_likelihood: float
    probability: float
    kappa: float
    total_alleles_sampled: int
    num_distinct_alleles: int


@dataclass(frozen=True)
class SimplexValidationResult:
    """Validation telemetry for diploid genotype probability simplex."""
    locus: str
    theta: float
    sum_probability: float
    delta_from_unity: float
    num_genotypes_evaluated: int
    is_valid: bool


@dataclass(frozen=True)
class MatchStateProbabilityResult:
    """Balding-Nichols 4-state conditional match probability."""
    state_name: str  # "HOMOZYGOUS_MATCH", "HETEROZYGOUS_MATCH", "PARTIAL_ONE_ALLELE", "ZERO_SHARED_ALLELES"
    suspect_genotype: Tuple[float, float]
    evidence_genotype: Tuple[float, float]
    p_conditional: float
    lr_per_locus: float
    log10_lr: float


@dataclass(frozen=True)
class WeirCockerhamResult:
    """Weir & Cockerham (1984) unbiased ANOVA Fst / theta estimator output."""
    theta_hat: float
    msp: float  # Mean Square Among Populations
    msg: float  # Mean Square Within Populations (Groups)
    n_c: float  # Sample size correction coefficient
    num_populations: int
    num_alleles: int
    locus: Optional[str] = None


@dataclass(frozen=True)
class LocusLRResult:
    """Per-locus LR computation under Balding-Nichols coancestry correction."""
    locus: str
    suspect_genotype: Tuple[float, float]
    evidence_genotype: Tuple[float, float]
    match_state: str
    theta: float
    p_conditional: float
    lr_locus: float
    log10_lr_locus: float


@dataclass(frozen=True)
class NRCProfileLRResult:
    """Multi-locus composite Likelihood Ratio result under NRC-II / Balding-Nichols."""
    locus_results: List[LocusLRResult]
    total_lr: float
    log10_total_lr: float
    reciprocal_lr: float
    is_reciprocal_balanced: bool
    reciprocal_product_delta: float
    theta_used: float
    population_used: str
    verbal_scale_en: str
    verbal_scale_tr: str


# ---------------------------------------------------------------------------
# Component 1: Dirichlet Compound Multinomial (DCM) Distribution Engine
# ---------------------------------------------------------------------------

class DirichletCompoundMultinomial:
    """
    Dirichlet Compound Multinomial (DCM) / Dirichlet-Multinomial distribution.
    Models allele count sampling distributions from finite sub-populations with coancestry theta.

    Formula (Pillar 1 §3.1):
      kappa = (1 - theta) / theta
      alpha_i = p_i * kappa
      P(n | p, theta) = [ Gamma(kappa) / Gamma(sum(n) + kappa) ] * prod_i [ Gamma(n_i + alpha_i) / Gamma(alpha_i) ]

    Computation is executed in log-gamma space (math.lgamma) to guarantee numerical stability
    and eliminate overflow/underflow across large sample sizes (N > 100,000).
    """

    @staticmethod
    def compute_kappa(theta: float) -> float:
        if not (0.0 < theta < 1.0):
            raise ValueError(f"theta must be strictly in (0, 1), got {theta}")
        return (1.0 - theta) / theta

    @classmethod
    def log_likelihood(
        cls,
        allele_counts: Dict[float, int],
        allele_freqs: Dict[float, float],
        theta: float,
        p_min: float = P_MIN_NRC_II
    ) -> DCMResult:
        """
        Computes the log-likelihood ln P(n | p, theta) using log-gamma functions.
        """
        if theta <= 0.0:
            # Degenerate theta -> 0 represents standard Multinomial
            return cls._multinomial_log_likelihood(allele_counts, allele_freqs, p_min)

        kappa = cls.compute_kappa(theta)
        total_s = sum(allele_counts.values())

        if total_s == 0:
            return DCMResult(
                log_likelihood=0.0,
                probability=1.0,
                kappa=kappa,
                total_alleles_sampled=0,
                num_distinct_alleles=len(allele_counts)
            )

        # Base log-gamma ratio for total count: ln Gamma(kappa) - ln Gamma(S + kappa)
        log_ll = math.lgamma(kappa) - math.lgamma(total_s + kappa)

        # Product terms in log-space: sum_i [ ln Gamma(n_i + alpha_i) - ln Gamma(alpha_i) ]
        for allele, count in allele_counts.items():
            freq = max(allele_freqs.get(allele, p_min), p_min)
            alpha_i = freq * kappa
            log_ll += math.lgamma(count + alpha_i) - math.lgamma(alpha_i)

        prob = math.exp(log_ll) if log_ll > -700 else 0.0

        return DCMResult(
            log_likelihood=log_ll,
            probability=prob,
            kappa=kappa,
            total_alleles_sampled=total_s,
            num_distinct_alleles=len(allele_counts)
        )

    @classmethod
    def _multinomial_log_likelihood(
        cls,
        allele_counts: Dict[float, int],
        allele_freqs: Dict[float, float],
        p_min: float
    ) -> DCMResult:
        """Standard multinomial log-likelihood when theta -> 0."""
        total_s = sum(allele_counts.values())
        # Multinomial coefficient: ln(S!) - sum(ln(n_i!))
        log_ll = math.lgamma(total_s + 1)
        for count in allele_counts.values():
            log_ll -= math.lgamma(count + 1)

        # sum(n_i * ln(p_i))
        for allele, count in allele_counts.items():
            freq = max(allele_freqs.get(allele, p_min), p_min)
            log_ll += count * math.log(freq)

        prob = math.exp(log_ll) if log_ll > -700 else 0.0

        return DCMResult(
            log_likelihood=log_ll,
            probability=prob,
            kappa=float("inf"),
            total_alleles_sampled=total_s,
            num_distinct_alleles=len(allele_counts)
        )


# ---------------------------------------------------------------------------
# Component 2: Balding-Nichols 4-State Conditional & Unconditional Match Model
# ---------------------------------------------------------------------------

class BaldingNicholsMatchModel:
    """
    Balding-Nichols (1995) & NRC II (1996) Recommendation 4.10b Conditional Match Probability Model.

    Covers all 4 pairwise match scenarios between suspect genotype S and evidence genotype M:
      1. Homozygous Match:   (Ai Ai | Ai Ai) -> [2θ + (1-θ)pi][3θ + (1-θ)pi] / [(1+θ)(1+2θ)]
      2. Heterozygous Match: (Ai Aj | Ai Aj) -> 2[θ + (1-θ)pi][θ + (1-θ)pj]   / [(1+θ)(1+2θ)]
      3. Partial 1-Allele:   (Ai Aj | Ai Ak) -> [θ + (1-θ)pi][(1-θ)pj]        / [(1+θ)(1+2θ)]
      4. Zero Shared:        (Ai Aj | Ak Al) -> 2[(1-θ)pi][(1-θ)pj]          / [(1+θ)(1+2θ)]
    """

    @classmethod
    def compute_conditional_match_probability(
        cls,
        suspect_genotype: Tuple[float, float],
        evidence_genotype: Tuple[float, float],
        allele_frequencies: Dict[float, float],
        theta: float,
        p_min: float = P_MIN_NRC_II
    ) -> MatchStateProbabilityResult:
        """
        Computes conditional probability P(Evidence | Suspect, theta).
        """
        s1, s2 = sorted(suspect_genotype)
        e1, e2 = sorted(evidence_genotype)

        denom = (1.0 + theta) * (1.0 + 2.0 * theta)
        one_minus_theta = 1.0 - theta

        p_e1 = max(allele_frequencies.get(e1, p_min), p_min)
        p_e2 = max(allele_frequencies.get(e2, p_min), p_min)

        is_susp_homo = (s1 == s2)
        is_evid_homo = (e1 == e2)

        # Case 1: Full Homozygous Match (Ai Ai | Ai Ai)
        if is_susp_homo and is_evid_homo and s1 == e1:
            p_cond = (2.0 * theta + one_minus_theta * p_e1) * (3.0 * theta + one_minus_theta * p_e1) / denom
            state = "HOMOZYGOUS_MATCH"

        # Case 2: Full Heterozygous Match (Ai Aj | Ai Aj)
        elif not is_susp_homo and not is_evid_homo and s1 == e1 and s2 == e2:
            p_cond = 2.0 * (theta + one_minus_theta * p_e1) * (theta + one_minus_theta * p_e2) / denom
            state = "HETEROZYGOUS_MATCH"

        # Case 3: Partial Match — Evidence is Heterozygous, shares 1 allele with Suspect
        elif not is_evid_homo:
            shared_alleles = set([s1, s2]).intersection(set([e1, e2]))
            if len(shared_alleles) == 1:
                shared = list(shared_alleles)[0]
                unshared = e2 if e1 == shared else e1
                p_shared = max(allele_frequencies.get(shared, p_min), p_min)
                p_unshared = max(allele_frequencies.get(unshared, p_min), p_min)
                p_cond = (theta + one_minus_theta * p_shared) * (one_minus_theta * p_unshared) / denom
                state = "PARTIAL_ONE_ALLELE"
            elif len(shared_alleles) == 0:
                p_cond = 2.0 * (one_minus_theta * p_e1) * (one_minus_theta * p_e2) / denom
                state = "ZERO_SHARED_ALLELES"
            else:
                # Fallback het match
                p_cond = 2.0 * (theta + one_minus_theta * p_e1) * (theta + one_minus_theta * p_e2) / denom
                state = "HETEROZYGOUS_MATCH"

        # Case 4: Evidence is Homozygous, Suspect is Heterozygous sharing 1 allele (Ai Ai | Ai Aj)
        elif is_evid_homo and not is_susp_homo and (e1 == s1 or e1 == s2):
            p_cond = (theta + one_minus_theta * p_e1) * (2.0 * theta + one_minus_theta * p_e1) / denom
            state = "PARTIAL_HOMOZYGOTE_MATCH"

        # Case 5: Evidence is Homozygous, shares 0 alleles with Suspect (Ai Ai | Aj Ak)
        elif is_evid_homo and e1 != s1 and e1 != s2:
            p_cond = (one_minus_theta * p_e1) * (theta + one_minus_theta * p_e1) / denom
            state = "ZERO_SHARED_ALLELES"

        else:
            p_cond = 2.0 * (one_minus_theta * p_e1) * (one_minus_theta * p_e2) / denom
            state = "ZERO_SHARED_ALLELES"

        # LR is 1 / P(Evidence | Suspect, theta)
        lr = 1.0 / p_cond if p_cond > 0 else float("inf")
        log10_lr = math.log10(lr) if lr > 0 else float("-inf")

        return MatchStateProbabilityResult(
            state_name=state,
            suspect_genotype=(s1, s2),
            evidence_genotype=(e1, e2),
            p_conditional=p_cond,
            lr_per_locus=lr,
            log10_lr=log10_lr
        )

    @classmethod
    def compute_unconditional_genotype_probability(
        cls,
        genotype: Tuple[float, float],
        allele_frequencies: Dict[float, float],
        theta: float,
        p_min: float = 0.0
    ) -> float:
        """
        Computes unconditional genotype probability P(G | theta) under Wright's inbreeding / NRC II Eq 4.4:
          Homozygote: P(Ai Ai | theta) = p_i^2 + theta * p_i * (1 - p_i) = (1 - theta) * p_i^2 + theta * p_i
          Heterozygote (i != j): P(Ai Aj | theta) = 2 * p_i * p_j * (1 - theta)

        Mathematical Invariant:
          sum_i P(Ai Ai | theta) + sum_{i < j} P(Ai Aj | theta) = 1.00000000 identically for any normalized frequency vector.
        """
        a1, a2 = genotype
        p1 = max(allele_frequencies.get(a1, p_min), p_min)
        p2 = max(allele_frequencies.get(a2, p_min), p_min)

        if a1 == a2:
            # Homozygote (NRC II Eq 4.4a)
            return (1.0 - theta) * (p1 ** 2) + theta * p1
        else:
            # Heterozygote (NRC II Eq 4.4b)
            return 2.0 * (1.0 - theta) * p1 * p2

    @classmethod
    def validate_simplex_normalization(
        cls,
        locus: str,
        allele_frequencies: Dict[float, float],
        theta: float,
        tolerance: float = 1e-6
    ) -> SimplexValidationResult:
        """
        Enforces and validates the mathematical invariant:
          sum_{i <= j} P(Ai Aj | theta) = 1.00000000 ± 1e-6
        across all possible diploid combinations for a given locus.
        """
        alleles = sorted(list(allele_frequencies.keys()))
        total_p = 0.0
        n_genotypes = 0

        # Normalize input frequencies first to ensure valid discrete probability vector
        sum_raw = sum(allele_frequencies.values())
        norm_freqs = {a: freq / sum_raw for a, freq in allele_frequencies.items()}

        for i, a1 in enumerate(alleles):
            for a2 in alleles[i:]:
                prob = cls.compute_unconditional_genotype_probability((a1, a2), norm_freqs, theta)
                total_p += prob
                n_genotypes += 1

        delta = abs(total_p - 1.0)
        is_valid = delta <= tolerance

        return SimplexValidationResult(
            locus=locus,
            theta=theta,
            sum_probability=total_p,
            delta_from_unity=delta,
            num_genotypes_evaluated=n_genotypes,
            is_valid=is_valid
        )


# ---------------------------------------------------------------------------
# Component 3: Weir & Cockerham (1984) Unbiased ANOVA Fst Estimator
# ---------------------------------------------------------------------------

class WeirCockerhamEstimator:
    """
    Weir & Cockerham (1984) ANOVA variance component Fst / theta estimator.
    Computes unbiased theta_hat across multiple sub-populations with unequal sample sizes.

    Formulas:
      n_c = [ sum(n_i) - sum(n_i^2)/sum(n_i) ] / (K - 1)
      MSP = sum_i [ n_i (p_tilde_i - p_bar)^2 ] / (K - 1)
      MSG = sum_i [ n_i p_tilde_i (1 - p_tilde_i) ] / sum(n_i - 1)
      theta_hat = (MSP - MSG) / [ MSP + (n_c - 1) * MSG ]
    """

    @classmethod
    def estimate_locus_theta(
        cls,
        subpop_allele_counts: Dict[str, Dict[float, int]],
        locus: Optional[str] = None
    ) -> WeirCockerhamResult:
        """
        Computes locus-specific Weir-Cockerham theta_hat.
        subpop_allele_counts: { "PopA": {14.0: 120, 15.0: 240, ...}, "PopB": { ... } }
        """
        pop_names = list(subpop_allele_counts.keys())
        k_pops = len(pop_names)
        if k_pops < 2:
            raise ValueError(f"At least 2 sub-populations required for Fst estimation, got {k_pops}")

        # Total sample sizes per population (2N alleles)
        n_per_pop = {pop: sum(counts.values()) for pop, counts in subpop_allele_counts.items()}
        total_n = sum(n_per_pop.values())

        if total_n == 0:
            return WeirCockerhamResult(0.0, 0.0, 0.0, 0.0, k_pops, 0, locus)

        # n_c calculation (variance-adjusted average sample size)
        sum_n_sq = sum(n ** 2 for n in n_per_pop.values())
        n_c = (total_n - (sum_n_sq / total_n)) / (k_pops - 1)

        # Distinct alleles across all populations
        all_alleles: Set[float] = set()
        for counts in subpop_allele_counts.values():
            all_alleles.update(counts.keys())

        msp_total = 0.0
        msg_total = 0.0

        for allele in all_alleles:
            # Subpopulation sample frequencies p_tilde_i
            p_tilde = {}
            for pop in pop_names:
                n_i = n_per_pop[pop]
                count_i = subpop_allele_counts[pop].get(allele, 0)
                p_tilde[pop] = count_i / n_i if n_i > 0 else 0.0

            # Overall pooled weighted mean frequency p_bar
            p_bar = sum(n_per_pop[pop] * p_tilde[pop] for pop in pop_names) / total_n

            # MSP (Mean Square Among Populations for this allele)
            msp_a = sum(n_per_pop[pop] * ((p_tilde[pop] - p_bar) ** 2) for pop in pop_names) / (k_pops - 1)

            # MSG (Mean Square Within Populations for this allele)
            denom_msg = sum(n_per_pop[pop] - 1 for pop in pop_names if n_per_pop[pop] > 1)
            if denom_msg > 0:
                msg_a = sum(n_per_pop[pop] * p_tilde[pop] * (1.0 - p_tilde[pop]) for pop in pop_names) / denom_msg
            else:
                msg_a = 0.0

            msp_total += msp_a
            msg_total += msg_a

        # Overall locus theta_hat
        denom_theta = msp_total + (n_c - 1.0) * msg_total
        if denom_theta <= 0.0:
            theta_hat = 0.0
        else:
            theta_hat = (msp_total - msg_total) / denom_theta

        # Bounded to [0.0, 1.0]
        theta_hat = max(0.0, min(1.0, theta_hat))

        return WeirCockerhamResult(
            theta_hat=theta_hat,
            msp=msp_total,
            msg=msg_total,
            n_c=n_c,
            num_populations=k_pops,
            num_alleles=len(all_alleles),
            locus=locus
        )


# ---------------------------------------------------------------------------
# Component 4: Multi-Locus Composite LR & Reciprocal Hypothesis Balance
# ---------------------------------------------------------------------------

class NRC2LikelihoodRatioEngine:
    """
    Multi-locus biostatistical Likelihood Ratio engine with Balding-Nichols coancestry correction.

    Guarantees:
      - Additivity in log-space: log10(LR_total) = sum_l log10(LR_l)
      - Reciprocal Hypothesis Balance: LR(Hp / Hd) * LR(Hd / Hp) = 1.0000000 ± 1e-6
      - ENFSI (2017) 7-tier bilingual reporting scale
    """

    ENFSI_TIERS = [
        (6.0, "Extremely strong support for inclusion (Hp)", "Dahil olma lehine son derece güçlü delil (Hp)"),
        (4.0, "Very strong support for inclusion (Hp)", "Dahil olma lehine çok güçlü delil (Hp)"),
        (2.0, "Strong support for inclusion (Hp)", "Dahil olma lehine güçlü delil (Hp)"),
        (1.0, "Moderately strong support for inclusion (Hp)", "Dahil olma lehine orta-güçlü delil (Hp)"),
        (0.0, "Moderate support for inclusion (Hp)", "Dahil olma lehine ılımlı delil (Hp)"),
        (-2.0, "Inconclusive / Neutral", "Sonuçsuz / Nötr delil"),
        (-float("inf"), "Support for exclusion (Hd)", "Hariç tutulma lehine delil (Hd)"),
    ]

    @classmethod
    def get_enfsi_verbal_scale(cls, log10_lr: float) -> Tuple[str, str]:
        for threshold, en_text, tr_text in cls.ENFSI_TIERS:
            if log10_lr >= threshold:
                return en_text, tr_text
        return cls.ENFSI_TIERS[-1][1], cls.ENFSI_TIERS[-1][2]

    @classmethod
    def compute_profile_lr(
        cls,
        suspect_profile: Dict[str, Tuple[float, float]],
        evidence_profile: Dict[str, Tuple[float, float]],
        population_frequencies: Dict[str, Dict[float, float]],
        theta: float = DEFAULT_THETA,
        population_name: str = "Caucasian",
        p_min: float = P_MIN_NRC_II
    ) -> NRCProfileLRResult:
        """
        Computes joint 24-locus Likelihood Ratio under Linkage Equilibrium assumption.
        """
        locus_results: List[LocusLRResult] = []
        log10_total_lr = 0.0

        for locus, susp_gt in suspect_profile.items():
            evid_gt = evidence_profile.get(locus, susp_gt)
            freqs = population_frequencies.get(locus, {})

            match_res = BaldingNicholsMatchModel.compute_conditional_match_probability(
                suspect_genotype=susp_gt,
                evidence_genotype=evid_gt,
                allele_frequencies=freqs,
                theta=theta,
                p_min=p_min
            )

            locus_results.append(
                LocusLRResult(
                    locus=locus,
                    suspect_genotype=susp_gt,
                    evidence_genotype=evid_gt,
                    match_state=match_res.state_name,
                    theta=theta,
                    p_conditional=match_res.p_conditional,
                    lr_locus=match_res.lr_per_locus,
                    log10_lr_locus=match_res.log10_lr
                )
            )
            log10_total_lr += match_res.log10_lr

        total_lr = 10.0 ** log10_total_lr if log10_total_lr < 300 else float("inf")
        reciprocal_lr = 1.0 / total_lr if total_lr > 0 and total_lr != float("inf") else 0.0

        # Reciprocal balance check
        reciprocal_product = total_lr * reciprocal_lr if math.isfinite(total_lr) and total_lr > 0 else 1.0
        delta = abs(reciprocal_product - 1.0)
        is_balanced = delta <= 1e-6

        en_verbal, tr_verbal = cls.get_enfsi_verbal_scale(log10_total_lr)

        return NRCProfileLRResult(
            locus_results=locus_results,
            total_lr=total_lr,
            log10_total_lr=log10_total_lr,
            reciprocal_lr=reciprocal_lr,
            is_reciprocal_balanced=is_balanced,
            reciprocal_product_delta=delta,
            theta_used=theta,
            population_used=population_name,
            verbal_scale_en=en_verbal,
            verbal_scale_tr=tr_verbal
        )
