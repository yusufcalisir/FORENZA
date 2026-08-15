"""
FORENZA Touch DNA & Low-Template (LTDNA) Stochastic Modeling Engine — Module 04.

Implements verbatim from Pillar 1 Research §4 (LTDNA Stochastic Phenomenon Modeling):
  - §4.1 Logistic Allele Dropout Model P(D|x): RFU-based (β₀=+2.50, β₁=-0.025)
          and DNA mass-based (β₀=+3.20, β₁=-0.080) sigmoid calibration curves.
  - §4.2 Poisson Allele Drop-in Model P(C=k): λ_C=0.020 per locus.
          Exponential Drop-in Peak Height PDF: λ_h=0.015, AT=50.0 RFU.
  - §4.2 Heterozygote Balance (H_b): H_b = min(h1,h2)/max(h1,h2); stochastic flag if
          H_b < 0.60 or h_min < ST=150 RFU or any peak < AT=50 RFU.
  - Curran-Gill Stochastic Single-Source LTDNA LR across 4 allele-state scenarios
          (both present, single dropout, both dropout, drop-in).
  - Substrate Recovery Efficiency Matrix (SMOOTH_NON_POROUS 0.60,
          TEXTURED_NON_POROUS 0.40, POROUS_FABRIC 0.20, ROUGH_WOOD 0.15).

Golden Benchmark Vector:
  VECTOR_03 (LTDNA Dropout Case): vWA locus, suspect (16, 17), observed 16@80 RFU,
  17 dropped, P(D) stochastic penalty active → log10(LR) = 1.22 ± 0.20.

References:
  NRC II (1996) National Research Council Report on DNA Evidence.
  Curran JM, Gill P (2016) Stochastic Genotyping for LTDNA. FSI Genetics.
  SWGDAM (2020) Guidelines for Autosomal STR Probabilistic Genotyping.
  Gill P (2001) Application of Low Copy Number DNA Profiling. FSI.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ── Research-Calibrated Constants (Verbatim §4) ───────────────────────────────

# §4.1 Logistic Dropout Model — RFU-based calibration
DROPOUT_BETA0_RFU: float = 2.50
DROPOUT_BETA1_RFU: float = -0.025   # per RFU unit

# §4.1 Logistic Dropout Model — DNA Mass-based calibration
DROPOUT_BETA0_MASS: float = 3.20
DROPOUT_BETA1_MASS: float = -0.080  # per picogram

# §4.2 Poisson Drop-in count rate per locus
DROPIN_LAMBDA_POISSON: float = 0.020

# §4.2 Exponential drop-in peak height decay parameter
DROPIN_LAMBDA_HEIGHT: float = 0.015  # per RFU

# Analytical Threshold (peaks below are masked artefacts)
ANALYTICAL_THRESHOLD_RFU: float = 50.0

# Stochastic Threshold (peaks below trigger stochastic flag)
STOCHASTIC_THRESHOLD_RFU: float = 150.0

# Heterozygote balance flag threshold
HB_FLAG_THRESHOLD: float = 0.60


# ── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class DropoutModelResult:
    """Logistic allele dropout probability result."""
    input_value: float
    model_type: str          # 'RFU' or 'MASS_PG'
    beta_0: float
    beta_1: float
    logit_value: float       # β₀ + β₁·x
    dropout_probability: float  # P(D|x) = 1 / (1 + exp(-(β₀ + β₁·x)))
    critical_threshold: float
    is_below_critical: bool


@dataclass
class DropinModelResult:
    """Poisson drop-in count and exponential height density result."""
    k: int
    lambda_c: float
    poisson_probability: float       # P(C=k) = (λ^k * e^-λ) / k!
    h_c: Optional[float]
    lambda_h: float
    at_rfu: float
    height_density: Optional[float]  # f(h_c) = λ_h * exp(-λ_h * (h_c - AT))
    is_above_at: Optional[bool]


@dataclass
class HeterozygoteBalanceResult:
    """Heterozygote balance evaluation and stochastic flag assessment."""
    h1: float
    h2: float
    h_min: float
    h_max: float
    h_balance: float              # H_b = h_min / h_max
    at_threshold: float
    st_threshold: float
    hb_threshold: float
    imbalance_flag: bool          # H_b < 0.60
    stochastic_threshold_flag: bool  # h_min < ST = 150 RFU
    at_flag: bool                 # any peak < AT = 50 RFU
    stochastic_flag_active: bool  # any of the 3 conditions
    interpretation: str


@dataclass
class StochasticLRResult:
    """Curran-Gill stochastic single-source LTDNA Likelihood Ratio."""
    locus: str
    suspect_genotype: Tuple[float, float]
    observed_peaks: Dict[float, float]
    p_dropout: float
    p_dropin: float
    # Allele state probabilities
    prob_both_present: float
    prob_single_dropout: float
    prob_both_dropout: float
    prob_dropin_contribution: float
    # Denominator (population genotype probability)
    pop_genotype_prob: float
    # Final LR and log10(LR)
    likelihood_numerator: float
    match_probability: float
    log10_lr: float
    interpretation: str


@dataclass
class SubstrateEfficiencyResult:
    substrate_type: str
    efficiency_factor: float
    input_mass_pg: float
    recovered_mass_pg: float


@dataclass
class StochasticDropoutModel:
    recovered_mass_pg: float
    dropout_probability_pd: float
    dropin_probability_pc: float
    peak_imbalance_ratio: float


@dataclass
class TouchDnaAnalysisResult:
    sample_id: str
    substrate: SubstrateEfficiencyResult
    stochastic_model: StochasticDropoutModel
    is_low_template: bool
    ltdna_summary: str


# ── Touch DNA & LTDNA Engine ─────────────────────────────────────────────────

class TouchDnaEngine:
    """
    Full FORENZA Touch DNA & LTDNA Stochastic Modeling Engine (Module 04).

    All formulas implemented verbatim from Pillar 1 Research §4:
      P(D|x) = 1 / (1 + exp(-(β₀ + β₁·x)))   [Logistic Dropout]
      P(C=k) = (λ_C^k * e^{-λ_C}) / k!          [Poisson Drop-in]
      f(h_c) = λ_h * exp(-λ_h * (h_c - AT))     [Drop-in Height PDF]
      H_b = min(h1, h2) / max(h1, h2)            [Heterozygote Balance]
    """

    SUBSTRATE_EFFICIENCIES = {
        "SMOOTH_NON_POROUS":   0.60,
        "TEXTURED_NON_POROUS": 0.40,
        "POROUS_FABRIC":       0.20,
        "ROUGH_WOOD":          0.15,
    }

    # ── §4.1 Logistic Dropout P(D) ────────────────────────────────────────

    def compute_rfu_dropout_probability(
        self,
        rfu: float,
        beta_0: float = DROPOUT_BETA0_RFU,
        beta_1: float = DROPOUT_BETA1_RFU,
    ) -> DropoutModelResult:
        """
        Logistic allele dropout probability from peak height RFU.

        P(D|RFU) = 1 / (1 + exp(-(β₀ + β₁·RFU)))
        β₀ = +2.50, β₁ = -0.025 RFU⁻¹   (Research §4.1 RFU-based calibration)
        """
        logit = beta_0 + beta_1 * rfu
        p_dropout = 1.0 / (1.0 + math.exp(-logit))
        # Critical threshold: P(D) < 1% → logit = log(0.01/0.99) → x > (β₀ - log(0.01/0.99)) / |β₁|
        p_critical_rfu = (beta_0 - math.log(0.01 / 0.99)) / abs(beta_1)
        return DropoutModelResult(
            input_value=rfu,
            model_type="RFU",
            beta_0=beta_0,
            beta_1=beta_1,
            logit_value=round(logit, 8),
            dropout_probability=round(p_dropout, 6),
            critical_threshold=round(p_critical_rfu, 2),
            is_below_critical=(rfu < p_critical_rfu),
        )

    def compute_mass_dropout_probability(
        self,
        mass_pg: float,
        beta_0: float = DROPOUT_BETA0_MASS,
        beta_1: float = DROPOUT_BETA1_MASS,
    ) -> DropoutModelResult:
        """
        Logistic allele dropout probability from recovered DNA mass (picograms).

        P(D|pg) = 1 / (1 + exp(-(β₀ + β₁·mass_pg)))
        β₀ = +3.20, β₁ = -0.080 pg⁻¹   (Research §4.1 Mass-based calibration)
        """
        logit = beta_0 + beta_1 * mass_pg
        p_dropout = 1.0 / (1.0 + math.exp(-logit))
        p_critical_pg = (beta_0 - math.log(0.01 / 0.99)) / abs(beta_1)
        return DropoutModelResult(
            input_value=mass_pg,
            model_type="MASS_PG",
            beta_0=beta_0,
            beta_1=beta_1,
            logit_value=round(logit, 8),
            dropout_probability=round(p_dropout, 6),
            critical_threshold=round(p_critical_pg, 2),
            is_below_critical=(mass_pg < p_critical_pg),
        )

    # ── §4.2 Poisson Drop-in P(C) ─────────────────────────────────────────

    def compute_dropin_poisson_probability(
        self,
        k: int,
        lambda_c: float = DROPIN_LAMBDA_POISSON,
    ) -> DropinModelResult:
        """
        Poisson drop-in allele count probability.

        P(C=k) = (λ_C^k * e^{-λ_C}) / k!   λ_C = 0.020 per locus (Research §4.2)
        """
        factorial_k = math.factorial(k)
        p_dropin = (lambda_c ** k * math.exp(-lambda_c)) / factorial_k
        return DropinModelResult(
            k=k,
            lambda_c=lambda_c,
            poisson_probability=round(p_dropin, 8),
            h_c=None,
            lambda_h=DROPIN_LAMBDA_HEIGHT,
            at_rfu=ANALYTICAL_THRESHOLD_RFU,
            height_density=None,
            is_above_at=None,
        )

    def compute_dropin_height_density(
        self,
        h_c: float,
        at: float = ANALYTICAL_THRESHOLD_RFU,
        lambda_h: float = DROPIN_LAMBDA_HEIGHT,
    ) -> DropinModelResult:
        """
        Exponential drop-in peak height PDF for artefact peaks above AT.

        f(h_c) = λ_h * exp(-λ_h * (h_c - AT))   h_c ≥ AT = 50 RFU (Research §4.2)
        λ_h = 0.015 per RFU.
        """
        if h_c < at:
            density = 0.0
            above_at = False
        else:
            density = lambda_h * math.exp(-lambda_h * (h_c - at))
            above_at = True
        return DropinModelResult(
            k=0,
            lambda_c=DROPIN_LAMBDA_POISSON,
            poisson_probability=math.exp(-DROPIN_LAMBDA_POISSON),
            h_c=h_c,
            lambda_h=lambda_h,
            at_rfu=at,
            height_density=round(density, 8),
            is_above_at=above_at,
        )

    # ── §4.2 Heterozygote Balance H_b ─────────────────────────────────────

    def evaluate_heterozygote_balance(
        self,
        h1: float,
        h2: float,
        hb_threshold: float = HB_FLAG_THRESHOLD,
        st_threshold: float = STOCHASTIC_THRESHOLD_RFU,
        at_threshold: float = ANALYTICAL_THRESHOLD_RFU,
    ) -> HeterozygoteBalanceResult:
        """
        Evaluates heterozygote peak balance and stochastic quality flags.

        H_b = min(h1, h2) / max(h1, h2)   (Research §4.2)
        Stochastic flag ACTIVE if:
          - H_b < 0.60       (severe imbalance)
          - h_min < 150 RFU  (Stochastic Threshold ST)
          - any peak < 50 RFU (Analytical Threshold AT)
        """
        if max(h1, h2) == 0:
            raise ValueError("Peak heights cannot both be zero.")

        h_min = min(h1, h2)
        h_max = max(h1, h2)
        h_balance = h_min / h_max

        imbalance_flag = h_balance < hb_threshold
        st_flag = h_min < st_threshold
        at_flag = (h1 < at_threshold) or (h2 < at_threshold)
        stochastic_active = imbalance_flag or st_flag or at_flag

        if stochastic_active:
            flags = []
            if imbalance_flag:
                flags.append(f"Hb={h_balance:.3f}<{hb_threshold}")
            if st_flag:
                flags.append(f"h_min={h_min:.0f}<ST={st_threshold:.0f}RFU")
            if at_flag:
                flags.append(f"Peak<AT={at_threshold:.0f}RFU")
            interpretation = f"STOCHASTIC FLAGS ACTIVE: {', '.join(flags)}"
        else:
            interpretation = (
                f"BALANCED: Hb={h_balance:.3f}>={hb_threshold}, "
                f"h_min={h_min:.0f}>={st_threshold:.0f}RFU"
            )

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
            interpretation=interpretation,
        )

    # ── Curran-Gill Stochastic LTDNA LR ──────────────────────────────────

    def calculate_stochastic_ltdna_lr(
        self,
        locus: str,
        suspect_genotype: Tuple[float, float],
        observed_peaks: Dict[float, float],
        p_dropout: float,
        p_dropin: float,
        locus_freqs: Dict[float, float],
        theta: float = 0.03,
        p_min: float = 0.00241,
    ) -> StochasticLRResult:
        """
        Curran-Gill Stochastic Single-Source LTDNA Likelihood Ratio.

        Evaluates the 4 allele-state scenarios for a low-template locus:
          1. Both alleles present:   (1 - P(D))^2
          2. Single allele dropout:  2 * P(D) * (1 - P(D))
          3. Both alleles dropped:   P(D)^2
          4. Drop-in contribution:   P(C=1) * f(h_c)

        Evidence likelihood P(E | Hp) computed from observed peak configuration,
        denominator P(E | Hd) from Balding-Nichols θ-corrected population freq.
        """
        a1, a2 = suspect_genotype
        p1 = max(locus_freqs.get(a1, p_min), p_min)
        p2 = max(locus_freqs.get(a2, p_min), p_min)

        # Compute allele-state probabilities
        prob_both_present = (1.0 - p_dropout) ** 2
        prob_single_dropout = 2.0 * p_dropout * (1.0 - p_dropout)
        prob_both_dropout = p_dropout ** 2
        prob_dropin = p_dropin

        # Determine observed configuration
        observed_alleles = set(observed_peaks.keys())
        suspect_alleles = {a1, a2}
        n_observed_in_suspect = len(observed_alleles & suspect_alleles)
        n_missing = len(suspect_alleles - observed_alleles)

        # Likelihood under Hp (suspect is contributor)
        if n_missing == 0:
            # Both alleles observed → both present scenario
            likelihood_hp = prob_both_present
        elif n_missing == 1:
            # One allele dropped → single dropout scenario
            likelihood_hp = prob_single_dropout
        else:
            # Both dropped out
            likelihood_hp = prob_both_dropout

        # Penalise extra peaks (possible drop-in) in observed not in suspect
        n_extra = len(observed_alleles - suspect_alleles)
        for _ in range(n_extra):
            likelihood_hp *= prob_dropin

        # Population genotype probability denominator (Balding-Nichols θ-correction)
        if a1 == a2:
            # Homozygous
            pop_prob = ((2 * theta + (1 - theta) * p1) *
                        (3 * theta + (1 - theta) * p1)) / ((1 + theta) * (1 + 2 * theta))
        else:
            # Heterozygous
            pop_prob = (2 * (theta + (1 - theta) * p1) *
                        (theta + (1 - theta) * p2)) / ((1 + theta) * (1 + 2 * theta))

        # Clamp log10 LR to [-300, 300]
        if likelihood_hp <= 0 or pop_prob <= 0:
            log10_lr = -300.0
        else:
            raw_lr = likelihood_hp / pop_prob
            log10_lr = max(-300.0, min(300.0, math.log10(raw_lr)))

        if log10_lr >= 3:
            interp = "Strong stochastic support for contributor hypothesis."
        elif log10_lr >= 1:
            interp = "Moderate stochastic support for contributor hypothesis."
        elif log10_lr > 0:
            interp = "Weak stochastic support for contributor hypothesis."
        elif log10_lr == 0:
            interp = "Neutral — no stochastic discriminating power."
        else:
            interp = "Support for exclusion hypothesis."

        return StochasticLRResult(
            locus=locus,
            suspect_genotype=suspect_genotype,
            observed_peaks=observed_peaks,
            p_dropout=round(p_dropout, 6),
            p_dropin=round(p_dropin, 6),
            prob_both_present=round(prob_both_present, 8),
            prob_single_dropout=round(prob_single_dropout, 8),
            prob_both_dropout=round(prob_both_dropout, 8),
            prob_dropin_contribution=round(prob_dropin, 8),
            pop_genotype_prob=round(pop_prob, 8),
            likelihood_numerator=round(likelihood_hp, 8),
            match_probability=round(pop_prob, 8),
            log10_lr=round(log10_lr, 6),
            interpretation=interp,
        )

    # ── Substrate Recovery & Full LTDNA Analysis ──────────────────────────

    def analyze_ltdna(
        self,
        sample_id: str,
        substrate_type: str,
        input_mass_pg: float,
        lambda_dropout: float = 0.05,
    ) -> TouchDnaAnalysisResult:
        """
        Full LTDNA substrate recovery and stochastic dropout analysis.

        Uses the research-calibrated logistic mass-based dropout model
        to compute P(D) from the recovered DNA mass after substrate efficiency
        correction.
        """
        if input_mass_pg <= 0:
            raise ValueError("Input DNA mass must be greater than zero.")

        sub_key = substrate_type.upper()
        eff = self.SUBSTRATE_EFFICIENCIES.get(sub_key, 0.30)
        recovered_mass = round(input_mass_pg * eff, 2)

        # Use research-calibrated mass-based logistic dropout model
        mass_result = self.compute_mass_dropout_probability(recovered_mass)
        pd = mass_result.dropout_probability

        # P(C) = P(C=1) from Poisson with λ_C = 0.020
        pc = round(
            (DROPIN_LAMBDA_POISSON ** 1 * math.exp(-DROPIN_LAMBDA_POISSON)) / 1, 4
        )

        # Peak height imbalance approximation from P(D)
        imbalance = round(max(0.20, 1.0 - 0.80 * pd), 4)

        sub_res = SubstrateEfficiencyResult(
            substrate_type=sub_key,
            efficiency_factor=eff,
            input_mass_pg=input_mass_pg,
            recovered_mass_pg=recovered_mass,
        )

        stoch_res = StochasticDropoutModel(
            recovered_mass_pg=recovered_mass,
            dropout_probability_pd=pd,
            dropin_probability_pc=pc,
            peak_imbalance_ratio=imbalance,
        )

        is_ltdna = recovered_mass < 100.0

        summary = (
            f"Touch DNA Analysis for {sample_id} ({sub_key}): "
            f"Recovered Mass = {recovered_mass} pg (Efficiency={eff*100:.0f}%). "
            f"Logistic Stochastic Dropout P(D) = {pd:.2%} "
            f"[Mass Model: β₀={DROPOUT_BETA0_MASS}, β₁={DROPOUT_BETA1_MASS}]. "
            f"Poisson Drop-in P(C=1) = {pc:.4f}. "
            f"Classification: {'LOW-TEMPLATE DNA (LTDNA)' if is_ltdna else 'STANDARD TEMPLATE DNA'}."
        )

        return TouchDnaAnalysisResult(
            sample_id=sample_id,
            substrate=sub_res,
            stochastic_model=stoch_res,
            is_low_template=is_ltdna,
            ltdna_summary=summary,
        )
