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
  17 dropped, P(D) stochastic penalty active → log10(LR) = 0.5604 (support).

References:
  NRC II (1996) National Research Council Report on DNA Evidence.
  Curran JM, Gill P (2016) Stochastic Genotyping for LTDNA. FSI Genetics.
  SWGDAM (2020) Guidelines for Autosomal STR Probabilistic Genotyping.
  Gill P (2001) Application of Low Copy Number DNA Profiling. FSI.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any

try:
    from node.services.forensic.ltdna.ltdna_mathematical_formulation import (
        LTDNAMathematicalFormulation,
        DROPOUT_BETA0_RFU,
        DROPOUT_BETA1_RFU,
        DROPOUT_BETA0_MASS,
        DROPOUT_BETA1_MASS,
        DROPOUT_BETAS_BP,
        DROPIN_LAMBDA_POISSON,
        DROPIN_LAMBDA_HEIGHT,
        ANALYTICAL_THRESHOLD_RFU,
        STOCHASTIC_THRESHOLD_RFU,
        HB_FLAG_THRESHOLD,
        DropoutModelResult as CoreDropoutResult,
        DropinPoissonResult as CoreDropinPoissonResult,
        DropinHeightDensityResult as CoreDropinHeightResult,
        HeterozygoteBalanceResult as CoreHbResult,
        LTDNALocusLRResult,
        LTDNAMultiLocusResult,
    )
    from node.services.forensic.ltdna.ltdna_reference_datasets import (
        LTDNAReferenceDatasetRegistry,
        LCNDilutionTier,
        SubstrateRecoverySpec,
        SubstrateRecoveryResult,
        TouchBenchmarkVector,
        NIST_SRM2391D_COMP_A_PROFILE,
    )
except ImportError:
    from backend.node.services.forensic.ltdna.ltdna_mathematical_formulation import (
        LTDNAMathematicalFormulation,
        DROPOUT_BETA0_RFU,
        DROPOUT_BETA1_RFU,
        DROPOUT_BETA0_MASS,
        DROPOUT_BETA1_MASS,
        DROPOUT_BETAS_BP,
        DROPIN_LAMBDA_POISSON,
        DROPIN_LAMBDA_HEIGHT,
        ANALYTICAL_THRESHOLD_RFU,
        STOCHASTIC_THRESHOLD_RFU,
        HB_FLAG_THRESHOLD,
        DropoutModelResult as CoreDropoutResult,
        DropinPoissonResult as CoreDropinPoissonResult,
        DropinHeightDensityResult as CoreDropinHeightResult,
        HeterozygoteBalanceResult as CoreHbResult,
        LTDNALocusLRResult,
        LTDNAMultiLocusResult,
    )
    from backend.node.services.forensic.ltdna.ltdna_reference_datasets import (
        LTDNAReferenceDatasetRegistry,
        LCNDilutionTier,
        SubstrateRecoverySpec,
        SubstrateRecoveryResult,
        TouchBenchmarkVector,
        NIST_SRM2391D_COMP_A_PROFILE,
    )


# ── Backward-Compatible Data Classes ─────────────────────────────────────────

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

    All biocomputational models derive directly from LTDNAMathematicalFormulation
    and LTDNAReferenceDatasetRegistry.
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
        """
        core = LTDNAMathematicalFormulation.compute_dropout_probability_rfu(
            rfu=rfu, beta_0=beta_0, beta_1=beta_1
        )
        return DropoutModelResult(
            input_value=core.input_value,
            model_type=core.model_type,
            beta_0=core.beta_0,
            beta_1=core.beta_1,
            logit_value=core.logit_value,
            dropout_probability=core.dropout_probability,
            critical_threshold=core.critical_threshold_1pct,
            is_below_critical=core.is_below_critical,
        )

    def compute_mass_dropout_probability(
        self,
        mass_pg: float,
        amplicon_bp: Optional[float] = None,
        beta_0: float = DROPOUT_BETA0_MASS,
        beta_1: float = DROPOUT_BETA1_MASS,
    ) -> DropoutModelResult:
        """
        Logistic allele dropout probability from recovered DNA mass (picograms).
        """
        if amplicon_bp is not None:
            core = LTDNAMathematicalFormulation.compute_dropout_probability_fragment(
                mass_pg=mass_pg,
                fragment_length_bp=amplicon_bp,
                beta_0=beta_0,
                beta_1=beta_1,
            )
        else:
            core = LTDNAMathematicalFormulation.compute_dropout_probability_mass(
                mass_pg=mass_pg,
                beta_0=beta_0,
                beta_1=beta_1,
            )
        return DropoutModelResult(
            input_value=core.input_value,
            model_type=core.model_type,
            beta_0=core.beta_0,
            beta_1=core.beta_1,
            logit_value=core.logit_value,
            dropout_probability=core.dropout_probability,
            critical_threshold=core.critical_threshold_1pct,
            is_below_critical=core.is_below_critical,
        )

    # ── §4.2 Poisson Drop-in P(C) ─────────────────────────────────────────

    def compute_dropin_poisson_probability(
        self,
        k: int,
        lambda_c: float = DROPIN_LAMBDA_POISSON,
    ) -> DropinModelResult:
        """
        Poisson drop-in allele count probability.
        """
        core = LTDNAMathematicalFormulation.compute_dropin_poisson_pmf(
            k=k, lambda_c=lambda_c
        )
        return DropinModelResult(
            k=core.k,
            lambda_c=core.lambda_c,
            poisson_probability=core.poisson_pmf,
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
        """
        core = LTDNAMathematicalFormulation.compute_dropin_height_pdf(
            h_c=h_c, at=at, lambda_h=lambda_h
        )
        return DropinModelResult(
            k=0,
            lambda_c=DROPIN_LAMBDA_POISSON,
            poisson_probability=math.exp(-DROPIN_LAMBDA_POISSON),
            h_c=core.h_c,
            lambda_h=core.lambda_h,
            at_rfu=core.at_rfu,
            height_density=core.height_pdf,
            is_above_at=core.is_above_at,
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
        """
        core = LTDNAMathematicalFormulation.evaluate_heterozygote_balance(
            h1=h1,
            h2=h2,
            hb_threshold=hb_threshold,
            st_threshold=st_threshold,
            at_threshold=at_threshold,
        )
        return HeterozygoteBalanceResult(
            h1=core.h1,
            h2=core.h2,
            h_min=core.h_min,
            h_max=core.h_max,
            h_balance=core.h_balance,
            at_threshold=core.at_threshold,
            st_threshold=core.st_threshold,
            hb_threshold=core.hb_threshold,
            imbalance_flag=core.imbalance_flag,
            stochastic_threshold_flag=core.stochastic_threshold_flag,
            at_flag=core.at_flag,
            stochastic_flag_active=core.stochastic_flag_active,
            interpretation=core.interpretation,
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
        """
        core_lr = LTDNAMathematicalFormulation.compute_ltdna_single_locus_lr(
            locus=locus,
            suspect_genotype=suspect_genotype,
            observed_peaks=observed_peaks,
            p_dropout=p_dropout,
            pop_freqs=locus_freqs,
            theta=theta,
            lambda_c=p_dropin,
            p_min=p_min,
        )

        prob_both_present = (1.0 - p_dropout) ** 2
        prob_single_dropout = 2.0 * p_dropout * (1.0 - p_dropout)
        prob_both_dropout = p_dropout ** 2

        return StochasticLRResult(
            locus=core_lr.locus,
            suspect_genotype=core_lr.suspect_genotype,
            observed_peaks=observed_peaks,
            p_dropout=p_dropout,
            p_dropin=p_dropin,
            prob_both_present=round(prob_both_present, 6),
            prob_single_dropout=round(prob_single_dropout, 6),
            prob_both_dropout=round(prob_both_dropout, 6),
            prob_dropin_contribution=round(p_dropin, 6),
            pop_genotype_prob=round(core_lr.likelihood_hd, 6),
            likelihood_numerator=round(core_lr.likelihood_hp, 6),
            match_probability=round(core_lr.likelihood_hd, 6),
            log10_lr=round(core_lr.log10_lr, 4),
            interpretation=core_lr.verbal_en,
        )

    # ── Multi-Locus LTDNA Profile LR ──────────────────────────────────────

    def calculate_multi_locus_ltdna_lr(
        self,
        suspect_profile: Dict[str, Tuple[float, float]],
        observed_profile: Dict[str, Dict[float, float]],
        template_pg: float,
        population_db: Optional[Dict[str, Dict[float, float]]] = None,
        theta: float = 0.03,
    ) -> LTDNAMultiLocusResult:
        """
        Computes composite multi-locus profile stochastic Likelihood Ratio.
        """
        if population_db is None:
            population_db = {
                "vWA": {16.0: 0.211, 17.0: 0.273, 18.0: 0.150},
                "D3S1358": {15.0: 0.282, 16.0: 0.231, 14.0: 0.120},
                "FGA": {21.0: 0.185, 22.0: 0.198},
                "D8S1179": {13.0: 0.339, 14.0: 0.201},
                "TH01": {6.0: 0.225, 9.3: 0.312},
                "D1S1656": {15.0: 0.162, 17.3: 0.210},
            }
        return LTDNAMathematicalFormulation.compute_multi_locus_ltdna_lr(
            suspect_profile=suspect_profile,
            observed_profile=observed_profile,
            template_pg=template_pg,
            pop_freqs_db=population_db,
            theta=theta,
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
        Comprehensive Touch DNA analysis simulating recovery and stochastic modeling.
        """
        recovery = LTDNAReferenceDatasetRegistry.simulate_substrate_recovery(
            initial_mass_pg=input_mass_pg,
            substrate_id=substrate_type,
        )

        p_dropout_res = LTDNAMathematicalFormulation.compute_dropout_probability_mass(
            recovery.recovered_mass_pg
        )
        p_dropin_res = LTDNAMathematicalFormulation.compute_dropin_poisson_pmf(
            k=1, lambda_c=DROPIN_LAMBDA_POISSON
        )

        is_ltdna = recovery.recovered_mass_pg < 100.0

        # Simulated peak imbalance based on mass
        if recovery.recovered_mass_pg >= 500.0:
            peak_imbalance = 0.88
        elif recovery.recovered_mass_pg >= 100.0:
            peak_imbalance = 0.74
        elif recovery.recovered_mass_pg >= 60.0:
            peak_imbalance = 0.62
        elif recovery.recovered_mass_pg >= 30.0:
            peak_imbalance = 0.48
        else:
            peak_imbalance = 0.35

        summary = (
            f"Touch DNA Sample '{sample_id}' recovered {recovery.recovered_mass_pg:.1f} pg "
            f"from {recovery.substrate_id} (efficiency {recovery.recovery_efficiency*100:.0f}%). "
            f"P(D)={p_dropout_res.dropout_probability*100:.1f}%, P(C)={p_dropin_res.poisson_pmf*100:.2f}%. "
            f"Zone: {'LOW-TEMPLATE STOCHASTIC' if is_ltdna else 'STANDARD CASEREGIME'}."
        )

        return TouchDnaAnalysisResult(
            sample_id=sample_id,
            substrate=SubstrateEfficiencyResult(
                substrate_type=recovery.substrate_id,
                efficiency_factor=recovery.recovery_efficiency,
                input_mass_pg=recovery.initial_mass_pg,
                recovered_mass_pg=recovery.recovered_mass_pg,
            ),
            stochastic_model=StochasticDropoutModel(
                recovered_mass_pg=recovery.recovered_mass_pg,
                dropout_probability_pd=p_dropout_res.dropout_probability,
                dropin_probability_pc=p_dropin_res.poisson_pmf,
                peak_imbalance_ratio=peak_imbalance,
            ),
            is_low_template=is_ltdna,
            ltdna_summary=summary,
        )
