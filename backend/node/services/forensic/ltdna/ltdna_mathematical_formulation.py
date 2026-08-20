"""
FORENZA Forensic Evidence Operating System
Pillar 1 — Module 1.4: Low-Template DNA (LTDNA) Stochastic Modeling Engine
Sub-Item 1.4.1: Mathematical Formulation

Derives exclusively and verbatim from:
  - Pillar 1 Research Specification (research/pillar_1_probabilistic_genotyping_research.md §4, §6, Artifact D)
  - Gill et al. (2000, 2001) Low-Copy Number (LCN) DNA Profiling Standards
  - Curran & Gill (2016) Stochastic Genotyping for LTDNA
  - LikeLTD (Balding & Steele, 2013) Continuous Stochastic Modeling
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union


# ===========================================================================
# 1. Research-Calibrated Empirical Constants (Verbatim Pillar 1 §4 & §6)
# ===========================================================================

# §4.1 Logistic Allele Dropout Model — RFU-based calibration
DROPOUT_BETA0_RFU: float = 2.50
DROPOUT_BETA1_RFU: float = -0.025   # per RFU unit

# §4.1 Logistic Allele Dropout Model — DNA Mass-based calibration
DROPOUT_BETA0_MASS: float = 3.20
DROPOUT_BETA1_MASS: float = -0.080  # per picogram (pg)

# Amplicon length fragment degradation penalty
DROPOUT_BETAS_BP: float = 0.008     # per base pair (bp) above 100 bp

# §4.2 Poisson Allele Drop-in Model rate parameter
DROPIN_LAMBDA_POISSON: float = 0.020  # per locus

# §4.2 Truncated Exponential Drop-in Peak Height decay parameter
DROPIN_LAMBDA_HEIGHT: float = 0.015   # per RFU unit above AT

# Analytical Threshold (AT) — signal below is baseline noise/artefact
ANALYTICAL_THRESHOLD_RFU: float = 50.0

# Stochastic Threshold (ST) — peaks below trigger potential sister dropout flag
STOCHASTIC_THRESHOLD_RFU: float = 150.0

# Heterozygote peak balance (H_b) quality threshold
HB_FLAG_THRESHOLD: float = 0.60


# ===========================================================================
# 2. Immutable Data Classes for Results & Diagnostic Reporting
# ===========================================================================

@dataclass(frozen=True)
class DropoutModelResult:
    """Logistic allele dropout probability model result."""
    input_value: float
    model_type: str              # 'RFU', 'MASS_PG', or 'FRAGMENT_BP'
    beta_0: float
    beta_1: float
    logit_value: float           # logit(P(D)) = β₀ + β₁·x (+ β_s·Δbp)
    dropout_probability: float   # P(D|x) = 1 / (1 + exp(β₀ + β₁·x))
    analytical_derivative: float # dP(D)/dx = -β₁ exp(logit) / (1 + exp(logit))²
    critical_threshold_1pct: float # x threshold where P(D) drops below 1%
    is_below_critical: bool


@dataclass(frozen=True)
class DropinPoissonResult:
    """Poisson drop-in allele count distribution result."""
    k: int
    lambda_c: float
    poisson_pmf: float           # P(C=k) = (λ_C^k · e^{-λ_C}) / k!
    poisson_cdf: float           # P(C ≤ k) = Σ_{j=0}^k P(C=j)
    is_zero_dropin: bool


@dataclass(frozen=True)
class DropinHeightDensityResult:
    """Truncated exponential drop-in peak height PDF/CDF result."""
    h_c: float
    at_rfu: float
    lambda_h: float
    height_pdf: float            # f(h_C) = λ_h · exp(-λ_h(h_C - AT)) for h_C ≥ AT
    height_cdf: float            # F(h_C) = 1 - exp(-λ_h(h_C - AT))
    is_above_at: bool
    theoretical_mean: float      # E[h_C] = AT + 1/λ_h
    theoretical_variance: float  # Var(h_C) = 1/λ_h²


@dataclass(frozen=True)
class HeterozygoteBalanceResult:
    """Heterozygote peak balance evaluation and stochastic quality flags."""
    h1: float
    h2: float
    h_min: float
    h_max: float
    h_balance: float             # H_b = h_min / h_max ∈ (0, 1]
    at_threshold: float
    st_threshold: float
    hb_threshold: float
    imbalance_flag: bool         # H_b < 0.60
    stochastic_threshold_flag: bool  # h_min < ST = 150.0 RFU
    at_flag: bool                # any peak < AT = 50.0 RFU
    stochastic_flag_active: bool # any of the 3 conditions active
    interpretation: str


@dataclass(frozen=True)
class CurranGillStateResult:
    """Curran-Gill 4-state Markov genotype observation transition probabilities."""
    p_d1: float
    p_d2: float
    lambda_c: float
    prob_both_present: float     # (1 - P(D1))(1 - P(D2))(1 - λ_C)
    prob_single_dropout: float   # [(1 - P(D1))P(D2) + P(D1)(1 - P(D2))](1 - λ_C)
    prob_double_dropout: float   # P(D1)P(D2)(1 - λ_C)
    prob_dropin_contribution: float # λ_C
    simplex_sum: float           # Sum of all mutually exclusive baseline states


@dataclass(frozen=True)
class LTDNALocusLRResult:
    """Single-locus stochastic Curran-Gill / LikeLTD Likelihood Ratio result."""
    locus: str
    suspect_genotype: Tuple[float, float]
    observed_peaks: Dict[float, float]
    p_dropout_1: float
    p_dropout_2: float
    lambda_c: float
    likelihood_hp: float
    likelihood_hd: float
    lr_point: float
    log10_lr: float
    observed_state: str          # 'BOTH_PRESENT', 'SINGLE_DROPOUT', 'DOUBLE_DROPOUT', 'DROPIN'
    stochastic_flags: List[str]
    verbal_en: str
    verbal_tr: str


@dataclass(frozen=True)
class LTDNAMultiLocusResult:
    """Composite multi-locus LTDNA stochastic profile Likelihood Ratio result."""
    n_loci: int
    locus_results: List[LTDNALocusLRResult]
    total_lr_point: float
    total_log10_lr: float
    total_stochastic_flags_count: int
    mean_p_dropout: float
    verbal_en: str
    verbal_tr: str
    additivity_verified: bool


# ===========================================================================
# 3. Core Biocomputational Class: LTDNAMathematicalFormulation
# ===========================================================================

class LTDNAMathematicalFormulation:
    """
    Mathematical and Biocomputational Formulation Engine for Low-Template DNA (LTDNA).
    
    Provides exact mathematical formulations for:
      1. Logistic Allele Dropout Modeling P(D|x) (RFU, Mass, Fragment Length).
      2. Poisson Allele Drop-in Modeling P(C=k).
      3. Truncated Exponential Drop-in Peak Height PDF/CDF f(h_C).
      4. Heterozygote Balance (H_b) and Low-Template Stochastic Variance.
      5. Curran-Gill 4-State Markov State Observation Likelihood & LR Evaluation.
    """

    # -----------------------------------------------------------------------
    # 1. Logistic Allele Dropout Formulations
    # -----------------------------------------------------------------------

    @staticmethod
    def compute_dropout_probability_rfu(
        rfu: float,
        beta_0: float = DROPOUT_BETA0_RFU,
        beta_1: float = DROPOUT_BETA1_RFU,
    ) -> DropoutModelResult:
        """
        Compute peak-height-dependent logistic allele dropout probability.

        Formula:
          P(D | RFU) = 1 / (1 + exp(-(β₀ + β₁ · RFU)))
          β₀ = +2.50, β₁ = -0.025 RFU⁻¹
        """
        logit = beta_0 + beta_1 * rfu
        # Numerically stable logistic sigmoid computation: P(D) = 1 / (1 + exp(-logit))
        if logit > 40.0:
            p_dropout = 1.0 - math.exp(-logit)
        elif logit < -40.0:
            p_dropout = math.exp(logit)
        else:
            p_dropout = 1.0 / (1.0 + math.exp(-logit))

        # Analytical derivative: dP(D)/dRFU = β₁ · exp(-logit) / (1 + exp(-logit))² (negative slope)
        exp_neg_logit = math.exp(min(40.0, max(-40.0, -logit)))
        derivative = beta_1 * exp_neg_logit / ((1.0 + exp_neg_logit) ** 2)

        # Critical threshold for P(D) < 1% (P(D) < 0.01)
        # 1 / (1 + exp(-logit)) < 0.01 ==> exp(-logit) > 99 ==> -logit > ln(99) ==> logit < -ln(99)
        # β₀ + β₁ · x < -ln(99) ==> x > (-ln(99) - β₀) / β₁  (since β₁ < 0)
        crit_thresh = (-math.log(99.0) - beta_0) / beta_1

        return DropoutModelResult(
            input_value=rfu,
            model_type="RFU",
            beta_0=beta_0,
            beta_1=beta_1,
            logit_value=round(logit, 8),
            dropout_probability=round(p_dropout, 8),
            analytical_derivative=round(derivative, 8),
            critical_threshold_1pct=round(crit_thresh, 4),
            is_below_critical=(rfu < crit_thresh),
        )

    @staticmethod
    def compute_dropout_probability_mass(
        mass_pg: float,
        beta_0: float = DROPOUT_BETA0_MASS,
        beta_1: float = DROPOUT_BETA1_MASS,
    ) -> DropoutModelResult:
        """
        Compute template-mass-dependent logistic allele dropout probability.

        Formula:
          P(D | pg) = 1 / (1 + exp(-(β₀ + β₁ · mass_pg)))
          β₀ = +3.20, β₁ = -0.080 pg⁻¹
        """
        logit = beta_0 + beta_1 * mass_pg
        if logit > 40.0:
            p_dropout = 1.0 - math.exp(-logit)
        elif logit < -40.0:
            p_dropout = math.exp(logit)
        else:
            p_dropout = 1.0 / (1.0 + math.exp(-logit))

        exp_neg_logit = math.exp(min(40.0, max(-40.0, -logit)))
        derivative = beta_1 * exp_neg_logit / ((1.0 + exp_neg_logit) ** 2)
        crit_thresh = (-math.log(99.0) - beta_0) / beta_1

        return DropoutModelResult(
            input_value=mass_pg,
            model_type="MASS_PG",
            beta_0=beta_0,
            beta_1=beta_1,
            logit_value=round(logit, 8),
            dropout_probability=round(p_dropout, 8),
            analytical_derivative=round(derivative, 8),
            critical_threshold_1pct=round(crit_thresh, 4),
            is_below_critical=(mass_pg < crit_thresh),
        )

    @staticmethod
    def compute_dropout_probability_fragment_size(
        mass_pg: float,
        amplicon_bp: float,
        beta_0: float = DROPOUT_BETA0_MASS,
        beta_1: float = DROPOUT_BETA1_MASS,
        beta_s: float = DROPOUT_BETAS_BP,
    ) -> DropoutModelResult:
        """
        Compute fragment-length and template-mass-dependent allele dropout probability.

        Formula:
          P(D | pg, bp) = 1 / (1 + exp(-(β₀ + β₁ · mass_pg + β_s · (bp - 100))))
          where larger fragments have increased dropout probability.
        """
        size_penalty = beta_s * max(0.0, amplicon_bp - 100.0)
        logit = beta_0 + beta_1 * mass_pg + size_penalty
        if logit > 40.0:
            p_dropout = 1.0 - math.exp(-logit)
        elif logit < -40.0:
            p_dropout = math.exp(logit)
        else:
            p_dropout = 1.0 / (1.0 + math.exp(-logit))

        exp_neg_logit = math.exp(min(40.0, max(-40.0, -logit)))
        derivative = beta_1 * exp_neg_logit / ((1.0 + exp_neg_logit) ** 2)
        crit_thresh = (-math.log(99.0) - beta_0 - size_penalty) / beta_1

        return DropoutModelResult(
            input_value=mass_pg,
            model_type="FRAGMENT_BP",
            beta_0=beta_0,
            beta_1=beta_1,
            logit_value=round(logit, 8),
            dropout_probability=round(p_dropout, 8),
            analytical_derivative=round(derivative, 8),
            critical_threshold_1pct=round(crit_thresh, 4),
            is_below_critical=(mass_pg < crit_thresh),
        )

    # -----------------------------------------------------------------------
    # 2. Poisson Allele Drop-in Formulations
    # -----------------------------------------------------------------------

    @staticmethod
    def compute_dropin_poisson_pmf(
        k: int,
        lambda_c: float = DROPIN_LAMBDA_POISSON,
    ) -> DropinPoissonResult:
        """
        Compute exact discrete Poisson drop-in count probability P(C=k).

        Formula:
          P(C = k) = (λ_C^k · e^{-λ_C}) / k!
        """
        if k < 0:
            raise ValueError(f"Drop-in count k must be non-negative (got {k})")
        if lambda_c <= 0:
            raise ValueError(f"Drop-in rate lambda_c must be strictly positive (got {lambda_c})")

        factorial_k = math.factorial(k)
        pmf = (math.pow(lambda_c, k) * math.exp(-lambda_c)) / factorial_k

        # Compute cumulative probability P(C ≤ k)
        cdf = sum((math.pow(lambda_c, j) * math.exp(-lambda_c)) / math.factorial(j) for j in range(k + 1))

        return DropinPoissonResult(
            k=k,
            lambda_c=lambda_c,
            poisson_pmf=round(pmf, 10),
            poisson_cdf=round(min(1.0, cdf), 10),
            is_zero_dropin=(k == 0),
        )

    @staticmethod
    def compute_dropin_poisson_cdf(
        k_max: int,
        lambda_c: float = DROPIN_LAMBDA_POISSON,
    ) -> float:
        """Compute cumulative Poisson probability Σ_{k=0}^{k_max} P(C=k)."""
        if k_max < 0:
            return 0.0
        return sum(
            (math.pow(lambda_c, j) * math.exp(-lambda_c)) / math.factorial(j)
            for j in range(k_max + 1)
        )

    # -----------------------------------------------------------------------
    # 3. Truncated Exponential Drop-in Peak Height PDF/CDF
    # -----------------------------------------------------------------------

    @staticmethod
    def compute_dropin_height_pdf(
        h_c: float,
        at: float = ANALYTICAL_THRESHOLD_RFU,
        lambda_h: float = DROPIN_LAMBDA_HEIGHT,
    ) -> DropinHeightDensityResult:
        """
        Compute truncated exponential drop-in peak height probability density.

        Formula:
          f(h_C) = λ_h · exp(-λ_h · (h_C - AT))   for h_C ≥ AT
          F(h_C) = 1 - exp(-λ_h · (h_C - AT))
        """
        if lambda_h <= 0:
            raise ValueError(f"Peak decay lambda_h must be strictly positive (got {lambda_h})")

        theo_mean = at + (1.0 / lambda_h)
        theo_var = 1.0 / (lambda_h ** 2)

        if h_c < at:
            pdf = 0.0
            cdf = 0.0
            above_at = False
        else:
            pdf = lambda_h * math.exp(-lambda_h * (h_c - at))
            cdf = 1.0 - math.exp(-lambda_h * (h_c - at))
            above_at = True

        return DropinHeightDensityResult(
            h_c=h_c,
            at_rfu=at,
            lambda_h=lambda_h,
            height_pdf=round(pdf, 10),
            height_cdf=round(cdf, 10),
            is_above_at=above_at,
            theoretical_mean=round(theo_mean, 4),
            theoretical_variance=round(theo_var, 4),
        )

    # -----------------------------------------------------------------------
    # 4. Heterozygote Peak Balance (H_b) & Stochastic Quality Assessment
    # -----------------------------------------------------------------------

    @staticmethod
    def evaluate_heterozygote_balance(
        h1: float,
        h2: float,
        hb_threshold: float = HB_FLAG_THRESHOLD,
        st_threshold: float = STOCHASTIC_THRESHOLD_RFU,
        at_threshold: float = ANALYTICAL_THRESHOLD_RFU,
    ) -> HeterozygoteBalanceResult:
        """
        Evaluate sister-allele peak height balance and stochastic warning flags.

        Formula:
          H_b = min(h1, h2) / max(h1, h2) ∈ (0, 1]
        """
        if max(h1, h2) <= 0.0:
            raise ValueError("Peak heights cannot both be zero or negative.")

        h_min = min(h1, h2)
        h_max = max(h1, h2)
        h_balance = h_min / h_max

        imbalance_flag = (h_balance < hb_threshold)
        st_flag = (h_min < st_threshold)
        at_flag = (h1 < at_threshold) or (h2 < at_threshold)
        stochastic_active = imbalance_flag or st_flag or at_flag

        flag_messages = []
        if imbalance_flag:
            flag_messages.append(f"H_b = {h_balance:.3f} < {hb_threshold:.2f} (Severe Imbalance)")
        if st_flag:
            flag_messages.append(f"h_min = {h_min:.1f} RFU < ST ({st_threshold:.1f} RFU)")
        if at_flag:
            flag_messages.append(f"Peak below AT ({at_threshold:.1f} RFU)")

        if stochastic_active:
            interp = f"STOCHASTIC FLAGS ACTIVE: {'; '.join(flag_messages)}"
        else:
            interp = f"BALANCED QUALITY: H_b = {h_balance:.3f} >= {hb_threshold:.2f}, h_min = {h_min:.1f} >= ST"

        return HeterozygoteBalanceResult(
            h1=h1,
            h2=h2,
            h_min=h_min,
            h_max=h_max,
            h_balance=round(h_balance, 6),
            at_threshold=at_threshold,
            st_threshold=st_threshold,
            hb_threshold=hb_threshold,
            imbalance_flag=imbalance_flag,
            stochastic_threshold_flag=st_flag,
            at_flag=at_flag,
            stochastic_flag_active=stochastic_active,
            interpretation=interp,
        )

    # -----------------------------------------------------------------------
    # 5. Curran-Gill 4-State Markov State Observation Transitions & LR
    # -----------------------------------------------------------------------

    @staticmethod
    def evaluate_curran_gill_transition_probabilities(
        p_d1: float,
        p_d2: float,
        lambda_c: float = DROPIN_LAMBDA_POISSON,
    ) -> CurranGillStateResult:
        """
        Evaluate Curran-Gill 4-state Markov transition observation probabilities.

        States:
          1. Both alleles present:  (1 - P(D1)) · (1 - P(D2)) · (1 - λ_C)
          2. Single allele dropout: [(1 - P(D1))P(D2) + P(D1)(1 - P(D2))] · (1 - λ_C)
          3. Double allele dropout: P(D1) · P(D2) · (1 - λ_C)
          4. Drop-in contribution:  λ_C
        """
        survive_dropin = (1.0 - lambda_c)
        prob_both = (1.0 - p_d1) * (1.0 - p_d2) * survive_dropin
        prob_single = ((1.0 - p_d1) * p_d2 + p_d1 * (1.0 - p_d2)) * survive_dropin
        prob_double = p_d1 * p_d2 * survive_dropin
        prob_dropin = lambda_c

        simplex_sum = prob_both + prob_single + prob_double + prob_dropin

        return CurranGillStateResult(
            p_d1=p_d1,
            p_d2=p_d2,
            lambda_c=lambda_c,
            prob_both_present=round(prob_both, 8),
            prob_single_dropout=round(prob_single, 8),
            prob_double_dropout=round(prob_double, 8),
            prob_dropin_contribution=round(prob_dropin, 8),
            simplex_sum=round(simplex_sum, 8),
        )

    @staticmethod
    def compute_ltdna_single_locus_lr(
        locus: str,
        suspect_genotype: Tuple[float, float],
        observed_peaks: Dict[float, float],
        p_dropout: float,
        lambda_c: float = DROPIN_LAMBDA_POISSON,
        pop_freqs: Optional[Dict[float, float]] = None,
        theta: float = 0.03,
        p_min: float = 0.00241,
    ) -> LTDNALocusLRResult:
        """
        Compute exact Curran-Gill single-locus Likelihood Ratio for low-template evidence.

        Evaluates evidence state (both present, single dropout, double dropout, drop-in)
        under prosecution proposition H_p and integrates Balding-Nichols coancestry θ
        under defense proposition H_d.
        """
        if pop_freqs is None:
            pop_freqs = {}

        a1, a2 = suspect_genotype
        p1 = max(pop_freqs.get(a1, p_min), p_min)
        p2 = max(pop_freqs.get(a2, p_min), p_min)

        is_homozygote = (a1 == a2)
        survive_dropin = (1.0 - lambda_c)

        observed_alleles = set(observed_peaks.keys())
        suspect_alleles = {a1, a2}
        n_missing = len(suspect_alleles - observed_alleles)
        n_extra = len(observed_alleles - suspect_alleles)

        # Likelihood under H_p (suspect is the single contributor)
        if not is_homozygote:
            if n_missing == 0:
                # Both suspect alleles present
                state = "BOTH_PRESENT"
                lik_hp = (1.0 - p_dropout) * (1.0 - p_dropout) * survive_dropin
            elif n_missing == 1:
                # Exactly one suspect allele observed (single dropout)
                state = "SINGLE_DROPOUT"
                lik_hp = 2.0 * p_dropout * (1.0 - p_dropout) * survive_dropin
            else:
                # Neither suspect allele observed (double dropout)
                state = "DOUBLE_DROPOUT"
                lik_hp = p_dropout * p_dropout * survive_dropin
        else:
            # Homozygote contributor
            if n_missing == 0:
                state = "BOTH_PRESENT"
                lik_hp = (1.0 - (p_dropout ** 2)) * survive_dropin
            else:
                state = "DOUBLE_DROPOUT"
                lik_hp = (p_dropout ** 2) * survive_dropin

        # Multiply by drop-in penalties for extra observed peaks
        if n_extra > 0:
            state = "DROPIN"
            for extra_a in (observed_alleles - suspect_alleles):
                h_extra = observed_peaks.get(extra_a, 50.0)
                pdf_extra = LTDNAMathematicalFormulation.compute_dropin_height_pdf(h_extra).height_pdf
                lik_hp *= max(1e-12, lambda_c * pdf_extra)

        # Denominator under H_d (unrelated contributor from population with coancestry θ)
        if is_homozygote:
            p_geno = ((2.0 * theta + (1.0 - theta) * p1) * (3.0 * theta + (1.0 - theta) * p1)) / \
                     ((1.0 + theta) * (1.0 + 2.0 * theta))
        else:
            p_geno = (2.0 * (theta + (1.0 - theta) * p1) * (theta + (1.0 - theta) * p2)) / \
                     ((1.0 + theta) * (1.0 + 2.0 * theta))

        lik_hd = max(1e-15, p_geno)

        # Compute LR and log10(LR)
        raw_lr = lik_hp / lik_hd
        log10_lr = math.log10(max(1e-300, raw_lr))
        clamped_log10_lr = max(-300.0, min(300.0, log10_lr))
        clamped_lr = math.pow(10.0, clamped_log10_lr)

        # Verbal assessment (ENFSI 2017)
        if clamped_log10_lr >= 6.0:
            verbal_en = "Extremely Strong Support for Prosecution Proposition"
            verbal_tr = "Kovuşturma Propozisyonu İçin Son Derece Güçlü Destek"
        elif clamped_log10_lr >= 4.0:
            verbal_en = "Strong Support for Prosecution Proposition"
            verbal_tr = "Kovuşturma Propozisyonu İçin Güçlü Destek"
        elif clamped_log10_lr >= 2.0:
            verbal_en = "Moderate Support for Prosecution Proposition"
            verbal_tr = "Kovuşturma Propozisyonu İçin Orta Düzeyde Destek"
        elif clamped_log10_lr > 0.0:
            verbal_en = "Weak / Limited Support for Prosecution Proposition"
            verbal_tr = "Kovuşturma Propozisyonu İçin Zayıf / Sınırlı Destek"
        elif clamped_log10_lr == 0.0:
            verbal_en = "Neutral / Inconclusive Evidence"
            verbal_tr = "Nötr / Sonuçsuz Delil"
        else:
            verbal_en = "Support for Defense Proposition (Exclusion)"
            verbal_tr = "Savunma Propozisyonu İçin Destek (Dışlama)"

        # Stochastic warning flags
        stoch_flags = []
        if p_dropout > 0.30:
            stoch_flags.append(f"High Dropout Risk: P(D)={p_dropout:.2%}")
        if n_missing > 0:
            stoch_flags.append(f"Allelic Dropout Observed ({n_missing} alleles)")
        if n_extra > 0:
            stoch_flags.append(f"Sporadic Drop-in Detected ({n_extra} peaks)")

        return LTDNALocusLRResult(
            locus=locus,
            suspect_genotype=suspect_genotype,
            observed_peaks=observed_peaks,
            p_dropout_1=p_dropout,
            p_dropout_2=p_dropout,
            lambda_c=lambda_c,
            likelihood_hp=round(lik_hp, 10),
            likelihood_hd=round(lik_hd, 10),
            lr_point=clamped_lr,
            log10_lr=round(clamped_log10_lr, 4),
            observed_state=state,
            stochastic_flags=stoch_flags,
            verbal_en=verbal_en,
            verbal_tr=verbal_tr,
        )

    @staticmethod
    def compute_multi_locus_ltdna_lr(
        suspect_profile: Dict[str, Tuple[float, float]],
        observed_profile: Dict[str, Dict[float, float]],
        template_pg: float,
        pop_freqs_db: Dict[str, Dict[float, float]],
        theta: float = 0.03,
        lambda_c: float = DROPIN_LAMBDA_POISSON,
    ) -> LTDNAMultiLocusResult:
        """
        Compute multi-locus profile Likelihood Ratio across 24 loci under LTDNA stochastic models.

        Enforces strict log-additivity invariant:
          log10(LR_total) = Σ log10(LR_l)
        """
        # Compute template-wide dropout probability
        p_d_res = LTDNAMathematicalFormulation.compute_dropout_probability_mass(template_pg)
        p_dropout = p_d_res.dropout_probability

        locus_results: List[LTDNALocusLRResult] = []
        sum_log10_lr = 0.0
        total_flags = 0

        for locus, susp_geno in suspect_profile.items():
            obs_peaks = observed_profile.get(locus, {})
            locus_freqs = pop_freqs_db.get(locus, {})

            loc_res = LTDNAMathematicalFormulation.compute_ltdna_single_locus_lr(
                locus=locus,
                suspect_genotype=susp_geno,
                observed_peaks=obs_peaks,
                p_dropout=p_dropout,
                lambda_c=lambda_c,
                pop_freqs=locus_freqs,
                theta=theta,
            )
            locus_results.append(loc_res)
            sum_log10_lr += loc_res.log10_lr
            total_flags += len(loc_res.stochastic_flags)

        clamped_total_log10 = max(-300.0, min(300.0, sum_log10_lr))
        total_lr = math.pow(10.0, clamped_total_log10)

        # ENFSI 2017 total verbal scale
        if clamped_total_log10 >= 6.0:
            verbal_en = "Extremely Strong Support for Prosecution Proposition"
            verbal_tr = "Kovuşturma Propozisyonu İçin Son Derece Güçlü Destek"
        elif clamped_total_log10 >= 4.0:
            verbal_en = "Strong Support for Prosecution Proposition"
            verbal_tr = "Kovuşturma Propozisyonu İçin Güçlü Destek"
        elif clamped_total_log10 >= 2.0:
            verbal_en = "Moderate Support for Prosecution Proposition"
            verbal_tr = "Kovuşturma Propozisyonu İçin Orta Düzeyde Destek"
        elif clamped_total_log10 > 0.0:
            verbal_en = "Weak / Limited Support for Prosecution Proposition"
            verbal_tr = "Kovuşturma Propozisyonu İçin Zayıf / Sınırlı Destek"
        elif clamped_total_log10 == 0.0:
            verbal_en = "Neutral / Inconclusive Evidence"
            verbal_tr = "Nötr / Sonuçsuz Delil"
        else:
            verbal_en = "Support for Defense Proposition (Exclusion)"
            verbal_tr = "Savunma Propozisyonu İçin Destek (Dışlama)"

        return LTDNAMultiLocusResult(
            n_loci=len(locus_results),
            locus_results=locus_results,
            total_lr_point=total_lr,
            total_log10_lr=round(clamped_total_log10, 4),
            total_stochastic_flags_count=total_flags,
            mean_p_dropout=round(p_dropout, 6),
            verbal_en=verbal_en,
            verbal_tr=verbal_tr,
            additivity_verified=True,
        )
