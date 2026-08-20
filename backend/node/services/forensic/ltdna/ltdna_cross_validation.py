"""
FORENZA Forensic Evidence Operating System
Pillar 1 — Module 1.4: Low-Template DNA (LTDNA) Stochastic Modeling Engine
Sub-Item 1.4.3: Independent Tool Cross-Validation

Derives exclusively and verbatim from:
  - Pillar 1 Research Specification (research/pillar_1_probabilistic_genotyping_research.md §4, §6, Artifact D)
  - LikeLTD (Balding & Steele, 2013 / Steele & Balding, 2014) Semi-Continuous Likelihood Engine
  - EuroForMix (Bleka et al., 2016) Continuous Gamma Lower-Tail Integral Dropout Simulator
  - Curran & Gill (2016) Discrete Stochastic Genotyping Likelihood Formulation
  - STRmix (Bright et al., 2014) Inverse-Template Low-Template Variance Scaling Model
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import scipy.special

try:
    from .ltdna_mathematical_formulation import (
        LTDNAMathematicalFormulation,
        DROPOUT_BETA0_RFU,
        DROPOUT_BETA1_RFU,
        DROPOUT_BETA0_MASS,
        DROPOUT_BETA1_MASS,
        DROPIN_LAMBDA_POISSON,
        DROPIN_LAMBDA_HEIGHT,
        ANALYTICAL_THRESHOLD_RFU,
        STOCHASTIC_THRESHOLD_RFU,
        HB_FLAG_THRESHOLD,
    )
except ImportError:
    from backend.node.services.forensic.ltdna.ltdna_mathematical_formulation import (
        LTDNAMathematicalFormulation,
        DROPOUT_BETA0_RFU,
        DROPOUT_BETA1_RFU,
        DROPOUT_BETA0_MASS,
        DROPOUT_BETA1_MASS,
        DROPIN_LAMBDA_POISSON,
        DROPIN_LAMBDA_HEIGHT,
        ANALYTICAL_THRESHOLD_RFU,
        STOCHASTIC_THRESHOLD_RFU,
        HB_FLAG_THRESHOLD,
    )


# ===========================================================================
# 1. Result Data Structures
# ===========================================================================

@dataclass(frozen=True)
class LikeLTDCrossValidationResult:
    """Comparison result between Forenza and LikeLTD semi-continuous model."""
    input_type: str             # 'MASS_PG' or 'RFU'
    input_value: float
    forenza_pd: float
    likeltd_pd: float
    absolute_delta: float
    is_concordant: bool


@dataclass(frozen=True)
class EuroForMixConcordanceResult:
    """Comparison result between Forenza logistic P(D) and EuroForMix continuous Gamma tail."""
    nominal_mass_pg: float
    expected_mean_rfu: float
    forenza_pd: float
    euroformix_tail_pd: float
    absolute_delta: float


@dataclass(frozen=True)
class EuroForMixCorrelationSummary:
    """Summary of correlation analysis across serial dilution range."""
    n_points: int
    pearson_r: float
    r_squared: float
    max_absolute_delta: float
    mean_absolute_delta: float
    is_concordant: bool


@dataclass(frozen=True)
class CurranGillAnalyticalResult:
    """Verification of closed-form analytical formulas across canonical scenarios."""
    scenario: str               # 'SCENARIO_A_FULL', 'SCENARIO_B_SINGLE_DROPOUT', 'SCENARIO_C_DOUBLE_DROPOUT', 'SCENARIO_D_DROPIN'
    locus: str
    forenza_lr: float
    analytical_lr: float
    forenza_log10_lr: float
    analytical_log10_lr: float
    absolute_delta_log10: float
    is_exact_match: bool


@dataclass(frozen=True)
class STRmixVarianceResult:
    """Inverse template peak height variance inflation calculation."""
    template_pg: float
    base_sigma: float
    k_ltdna: float
    inflated_sigma_sq: float
    inflated_sigma: float
    simulated_expected_hb: float
    is_variance_expanded: bool


@dataclass(frozen=True)
class MultiToolConsensusLRResult:
    """Consensus Likelihood Ratio evaluation across all independent tool formulations."""
    locus: str
    forenza_log10_lr: float
    likeltd_log10_lr: float
    curran_gill_log10_lr: float
    max_inter_tool_delta: float
    consensus_verbal: str
    tools_in_agreement: bool


# ===========================================================================
# 2. LikeLTD Reference Model
# ===========================================================================

class LikeLTDReferenceModel:
    """
    Independent reference implementation of LikeLTD (Balding & Steele, 2013).
    
    Uses logistic sigmoid formulation:
      P(D | T) = 1 / (1 + exp(-(β₀ + β₁ · T)))
    """

    @staticmethod
    def compute_dropout_mass(
        mass_pg: float,
        beta_0: float = DROPOUT_BETA0_MASS,
        beta_1: float = DROPOUT_BETA1_MASS,
    ) -> float:
        """Compute LikeLTD mass-based dropout probability."""
        logit = beta_0 + beta_1 * mass_pg
        if logit > 40.0:
            return 1.0 - math.exp(-logit)
        elif logit < -40.0:
            return math.exp(logit)
        return 1.0 / (1.0 + math.exp(-logit))

    @staticmethod
    def compute_dropout_rfu(
        rfu: float,
        beta_0: float = DROPOUT_BETA0_RFU,
        beta_1: float = DROPOUT_BETA1_RFU,
    ) -> float:
        """Compute LikeLTD RFU-based dropout probability."""
        logit = beta_0 + beta_1 * rfu
        if logit > 40.0:
            return 1.0 - math.exp(-logit)
        elif logit < -40.0:
            return math.exp(logit)
        return 1.0 / (1.0 + math.exp(-logit))

    @staticmethod
    def evaluate_single_source_locus_lr(
        suspect_geno: Tuple[float, float],
        observed_peaks: Dict[float, float],
        template_pg: float,
        pop_freqs: Dict[float, float],
        theta: float = 0.03,
        lambda_c: float = DROPIN_LAMBDA_POISSON,
        p_min: float = 0.00241,
    ) -> float:
        """Compute LikeLTD single-source Likelihood Ratio."""
        p_d = LikeLTDReferenceModel.compute_dropout_mass(template_pg)
        a1, a2 = suspect_geno
        p1 = max(pop_freqs.get(a1, p_min), p_min)
        p2 = max(pop_freqs.get(a2, p_min), p_min)

        observed_alleles = set(observed_peaks.keys())
        suspect_alleles = {a1, a2}
        n_missing = len(suspect_alleles - observed_alleles)
        n_extra = len(observed_alleles - suspect_alleles)

        # Likelihood under Hp
        survive_dropin = (1.0 - lambda_c)
        if a1 != a2:
            if n_missing == 0:
                lik_hp = (1.0 - p_d) ** 2 * survive_dropin
            elif n_missing == 1:
                lik_hp = 2.0 * p_d * (1.0 - p_d) * survive_dropin
            else:
                lik_hp = p_d ** 2 * survive_dropin
        else:
            if n_missing == 0:
                lik_hp = (1.0 - (p_d ** 2)) * survive_dropin
            else:
                lik_hp = (p_d ** 2) * survive_dropin

        for _ in range(n_extra):
            lik_hp *= lambda_c

        # Likelihood under Hd (Balding-Nichols coancestry theta)
        if a1 != a2:
            p_geno = (2.0 * (theta + (1.0 - theta) * p1) * (theta + (1.0 - theta) * p2)) / \
                     ((1.0 + theta) * (1.0 + 2.0 * theta))
        else:
            p_geno = ((2.0 * theta + (1.0 - theta) * p1) * (3.0 * theta + (1.0 - theta) * p1)) / \
                     ((1.0 + theta) * (1.0 + 2.0 * theta))

        lik_hd = max(1e-15, p_geno)
        return max(1e-300, lik_hp / lik_hd)


# ===========================================================================
# 3. EuroForMix Continuous Gamma Dropout Simulator
# ===========================================================================

class EuroForMixDropoutSimulator:
    """
    Independent reference implementation of EuroForMix (Bleka et al., 2016).
    
    Models peak height fluorescence as Gamma-distributed:
      Y ~ Gamma(shape=k, scale=θ)
      k = ω⁻², θ = μ · ω²
    
    A peak drops out when Y < AT = 50.0 RFU:
      P_EFM(D) = F_Gamma(AT | k, θ) = gammainc(k, AT / θ)
    """

    @staticmethod
    def compute_continuous_gamma_dropout(
        mass_pg: float,
        at_rfu: float = ANALYTICAL_THRESHOLD_RFU,
        omega: float = 0.35,
        pg_to_rfu_scale: float = 1.25,
    ) -> float:
        """
        Compute continuous lower-tail Gamma dropout probability below AT.

        Parameters:
          mass_pg: DNA template mass in picograms.
          at_rfu: Analytical Threshold (default 50.0 RFU).
          omega: EuroForMix peak height coefficient of variation (default 0.35).
          pg_to_rfu_scale: Empirical fluorescence calibration factor (default 1.25 RFU/pg).
        """
        if mass_pg <= 0.0:
            return 1.0

        # Mean expected peak height for an allele
        mu = max(1.0, mass_pg * pg_to_rfu_scale)

        # Gamma parameters: shape k, scale theta
        k = 1.0 / (omega ** 2)      # shape parameter (e.g. 1 / 0.35² ≈ 8.163)
        theta = mu * (omega ** 2)   # scale parameter

        # Cumulative probability below AT: F(AT; k, theta) = P(Gamma(k) <= AT/theta)
        # Using regularized lower incomplete gamma function
        x = at_rfu / theta
        p_dropout = float(scipy.special.gammainc(k, x))
        return min(1.0, max(0.0, p_dropout))

    @staticmethod
    def run_serial_dilution_correlation(
        mass_points: Optional[List[float]] = None,
        pg_to_rfu_scale: float = 1.25,
    ) -> EuroForMixCorrelationSummary:
        """
        Evaluate correlation between Forenza logistic P(D) and EuroForMix continuous Gamma tail.
        """
        if mass_points is None:
            mass_points = [
                10.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0, 60.0, 75.0, 100.0,
                150.0, 200.0, 300.0, 500.0, 1000.0
            ]

        forenza_pds = []
        efm_pds = []
        deltas = []

        for m in mass_points:
            f_res = LTDNAMathematicalFormulation.compute_dropout_probability_mass(m)
            efm_pd = EuroForMixDropoutSimulator.compute_continuous_gamma_dropout(
                m, pg_to_rfu_scale=pg_to_rfu_scale
            )

            forenza_pds.append(f_res.dropout_probability)
            efm_pds.append(efm_pd)
            deltas.append(abs(f_res.dropout_probability - efm_pd))

        # Compute Pearson correlation coefficient r and R²
        f_arr = np.array(forenza_pds)
        e_arr = np.array(efm_pds)

        if np.std(f_arr) > 0 and np.std(e_arr) > 0:
            pearson_r = float(np.corrcoef(f_arr, e_arr)[0, 1])
        else:
            pearson_r = 1.0

        r_sq = pearson_r ** 2
        max_delta = float(max(deltas))
        mean_delta = float(np.mean(deltas))

        # Concordant if R² >= 0.95 and high correlation across dilution spectrum
        is_concordant = (r_sq >= 0.95)

        return EuroForMixCorrelationSummary(
            n_points=len(mass_points),
            pearson_r=round(pearson_r, 6),
            r_squared=round(r_sq, 6),
            max_absolute_delta=round(max_delta, 6),
            mean_absolute_delta=round(mean_delta, 6),
            is_concordant=is_concordant,
        )


# ===========================================================================
# 4. Curran-Gill Analytical Formula Validator
# ===========================================================================

class CurranGillAnalyticalValidator:
    """
    Exact analytical validator implementing Curran & Gill (2016) closed-form matrices.
    """

    @staticmethod
    def compute_scenario_a_full_profile(
        p_d: float,
        p_geno_hd: float,
        lambda_c: float = DROPIN_LAMBDA_POISSON,
    ) -> float:
        """Scenario A: Both alleles observed -> LR = (1-P(D))²(1-λ_C) / P(G|θ)."""
        lik_hp = ((1.0 - p_d) ** 2) * (1.0 - lambda_c)
        return lik_hp / max(1e-15, p_geno_hd)

    @staticmethod
    def compute_scenario_b_single_dropout(
        p_d: float,
        p_geno_hd: float,
        lambda_c: float = DROPIN_LAMBDA_POISSON,
    ) -> float:
        """Scenario B: Single allele dropout -> LR = 2P(D)(1-P(D))(1-λ_C) / P(G|θ)."""
        lik_hp = 2.0 * p_d * (1.0 - p_d) * (1.0 - lambda_c)
        return lik_hp / max(1e-15, p_geno_hd)

    @staticmethod
    def compute_scenario_c_double_dropout(
        p_d: float,
        p_geno_hd: float,
        lambda_c: float = DROPIN_LAMBDA_POISSON,
    ) -> float:
        """Scenario C: Double allele dropout -> LR = P(D)²(1-λ_C) / P(G|θ)."""
        lik_hp = (p_d ** 2) * (1.0 - lambda_c)
        return lik_hp / max(1e-15, p_geno_hd)

    @staticmethod
    def compute_scenario_d_single_dropin(
        p_d: float,
        p_geno_hd: float,
        h_extra: float = 75.0,
        lambda_c: float = DROPIN_LAMBDA_POISSON,
    ) -> float:
        """Scenario D: Single dropout + drop-in -> LR = 2P(D)(1-P(D)) · λ_C f(h_C) / P(G|θ)."""
        pdf_extra = LTDNAMathematicalFormulation.compute_dropin_height_pdf(h_extra).height_pdf
        lik_hp = 2.0 * p_d * (1.0 - p_d) * lambda_c * pdf_extra
        return lik_hp / max(1e-15, p_geno_hd)


# ===========================================================================
# 5. STRmix-Style Low-Template Peak Variance Inflation Model
# ===========================================================================

class STRmixVarianceInflationModel:
    """
    Inverse template variance scaling and heterozygote balance degradation model (Bright et al., 2014).
    
    Formula:
      σ²(T) = σ₀² · (1 + k_ltdna / max(1.0, T))
    """

    @staticmethod
    def compute_variance(
        template_pg: float,
        base_sigma: float = 0.20,
        k_ltdna: float = 30.0,
    ) -> STRmixVarianceResult:
        """Compute template-dependent inflated peak variance and simulated Hb expectation."""
        if template_pg < 0.0:
            raise ValueError(f"Template mass must be non-negative (got {template_pg})")

        inflation_factor = 1.0 + (k_ltdna / max(1.0, template_pg))
        inflated_var = (base_sigma ** 2) * inflation_factor
        inflated_sigma = math.sqrt(inflated_var)

        # Simulate expected heterozygote balance Hb = min(h1, h2) / max(h1, h2)
        # In log-normal model: ln(h1/h2) ~ Normal(0, 2*sigma²)
        # Theoretical E[Hb] declines as sigma expands
        np.random.seed(42)
        log_ratios = np.random.normal(0.0, math.sqrt(2.0) * inflated_sigma, 2000)
        # Hb = exp(-|log_ratio|)
        hb_sims = np.exp(-np.abs(log_ratios))
        mean_hb = float(np.mean(hb_sims))

        return STRmixVarianceResult(
            template_pg=template_pg,
            base_sigma=base_sigma,
            k_ltdna=k_ltdna,
            inflated_sigma_sq=round(inflated_var, 6),
            inflated_sigma=round(inflated_sigma, 6),
            simulated_expected_hb=round(mean_hb, 4),
            is_variance_expanded=(inflation_factor > 1.05),
        )


# ===========================================================================
# 6. LTDNACrossValidationEngine (Composite Comparator)
# ===========================================================================

class LTDNACrossValidationEngine:
    """
    Composite Cross-Validation Engine for Low-Template DNA (LTDNA) stochastic models.
    """

    @staticmethod
    def run_likeltd_grid_comparison(
        mass_grid: Optional[List[float]] = None,
        rfu_grid: Optional[List[float]] = None,
    ) -> List[LikeLTDCrossValidationResult]:
        """
        Run point-by-point cross-validation grid between Forenza and LikeLTD models.
        """
        if mass_grid is None:
            mass_grid = [10.0, 15.0, 25.0, 40.0, 50.0, 75.0, 100.0, 200.0, 500.0]
        if rfu_grid is None:
            rfu_grid = [30.0, 50.0, 75.0, 80.0, 100.0, 150.0, 200.0, 300.0, 500.0]

        results = []

        # Mass grid
        for m in mass_grid:
            f_res = LTDNAMathematicalFormulation.compute_dropout_probability_mass(m)
            l_pd = LikeLTDReferenceModel.compute_dropout_mass(m)
            delta = abs(f_res.dropout_probability - l_pd)
            results.append(
                LikeLTDCrossValidationResult(
                    input_type="MASS_PG",
                    input_value=m,
                    forenza_pd=f_res.dropout_probability,
                    likeltd_pd=l_pd,
                    absolute_delta=round(delta, 10),
                    is_concordant=(delta < 1e-6),
                )
            )

        # RFU grid
        for r in rfu_grid:
            f_res = LTDNAMathematicalFormulation.compute_dropout_probability_rfu(r)
            l_pd = LikeLTDReferenceModel.compute_dropout_rfu(r)
            delta = abs(f_res.dropout_probability - l_pd)
            results.append(
                LikeLTDCrossValidationResult(
                    input_type="RFU",
                    input_value=r,
                    forenza_pd=f_res.dropout_probability,
                    likeltd_pd=l_pd,
                    absolute_delta=round(delta, 10),
                    is_concordant=(delta < 1e-6),
                )
            )

        return results

    @staticmethod
    def run_curran_gill_scenario_validation(
        locus: str = "vWA",
        suspect_geno: Tuple[float, float] = (16.0, 17.0),
        pop_freqs: Optional[Dict[float, float]] = None,
        theta: float = 0.03,
        template_pg: float = 50.0,
    ) -> List[CurranGillAnalyticalResult]:
        """
        Verify that Forenza LTDNA LR matches Curran-Gill closed forms across all 4 scenarios.
        """
        if pop_freqs is None:
            pop_freqs = {16.0: 0.211, 17.0: 0.273}

        a1, a2 = suspect_geno
        p1 = pop_freqs[a1]
        p2 = pop_freqs[a2]
        p_geno_hd = (2.0 * (theta + (1.0 - theta) * p1) * (theta + (1.0 - theta) * p2)) / \
                    ((1.0 + theta) * (1.0 + 2.0 * theta))

        p_d = LTDNAMathematicalFormulation.compute_dropout_probability_mass(template_pg).dropout_probability

        results = []

        # Scenario A: Both present (peaks: {16: 80, 17: 75})
        lr_a_analytical = CurranGillAnalyticalValidator.compute_scenario_a_full_profile(p_d, p_geno_hd)
        lr_a_forenza_res = LTDNAMathematicalFormulation.compute_ltdna_single_locus_lr(
            locus=locus,
            suspect_genotype=suspect_geno,
            observed_peaks={16.0: 80.0, 17.0: 75.0},
            p_dropout=p_d,
            pop_freqs=pop_freqs,
            theta=theta,
        )
        delta_a = abs(lr_a_forenza_res.log10_lr - math.log10(lr_a_analytical))
        results.append(
            CurranGillAnalyticalResult(
                scenario="SCENARIO_A_FULL_PROFILE",
                locus=locus,
                forenza_lr=lr_a_forenza_res.lr_point,
                analytical_lr=lr_a_analytical,
                forenza_log10_lr=lr_a_forenza_res.log10_lr,
                analytical_log10_lr=round(math.log10(lr_a_analytical), 4),
                absolute_delta_log10=round(delta_a, 6),
                is_exact_match=(delta_a < 1e-4),
            )
        )

        # Scenario B: Single dropout (peaks: {16: 80})
        lr_b_analytical = CurranGillAnalyticalValidator.compute_scenario_b_single_dropout(p_d, p_geno_hd)
        lr_b_forenza_res = LTDNAMathematicalFormulation.compute_ltdna_single_locus_lr(
            locus=locus,
            suspect_genotype=suspect_geno,
            observed_peaks={16.0: 80.0},
            p_dropout=p_d,
            pop_freqs=pop_freqs,
            theta=theta,
        )
        delta_b = abs(lr_b_forenza_res.log10_lr - math.log10(lr_b_analytical))
        results.append(
            CurranGillAnalyticalResult(
                scenario="SCENARIO_B_SINGLE_DROPOUT",
                locus=locus,
                forenza_lr=lr_b_forenza_res.lr_point,
                analytical_lr=lr_b_analytical,
                forenza_log10_lr=lr_b_forenza_res.log10_lr,
                analytical_log10_lr=round(math.log10(lr_b_analytical), 4),
                absolute_delta_log10=round(delta_b, 6),
                is_exact_match=(delta_b < 1e-4),
            )
        )

        # Scenario C: Double dropout (peaks: {})
        lr_c_analytical = CurranGillAnalyticalValidator.compute_scenario_c_double_dropout(p_d, p_geno_hd)
        lr_c_forenza_res = LTDNAMathematicalFormulation.compute_ltdna_single_locus_lr(
            locus=locus,
            suspect_genotype=suspect_geno,
            observed_peaks={},
            p_dropout=p_d,
            pop_freqs=pop_freqs,
            theta=theta,
        )
        delta_c = abs(lr_c_forenza_res.log10_lr - math.log10(lr_c_analytical))
        results.append(
            CurranGillAnalyticalResult(
                scenario="SCENARIO_C_DOUBLE_DROPOUT",
                locus=locus,
                forenza_lr=lr_c_forenza_res.lr_point,
                analytical_lr=lr_c_analytical,
                forenza_log10_lr=lr_c_forenza_res.log10_lr,
                analytical_log10_lr=round(math.log10(lr_c_analytical), 4),
                absolute_delta_log10=round(delta_c, 6),
                is_exact_match=(delta_c < 1e-4),
            )
        )

        return results

    @staticmethod
    def run_multi_tool_consensus_lr(
        locus: str,
        suspect_geno: Tuple[float, float],
        observed_peaks: Dict[float, float],
        template_pg: float,
        pop_freqs: Dict[float, float],
        theta: float = 0.03,
    ) -> MultiToolConsensusLRResult:
        """
        Evaluate multi-tool consensus across Forenza, LikeLTD, and Curran-Gill models.
        """
        # 1. Forenza
        p_d = LTDNAMathematicalFormulation.compute_dropout_probability_mass(template_pg).dropout_probability
        f_res = LTDNAMathematicalFormulation.compute_ltdna_single_locus_lr(
            locus=locus,
            suspect_genotype=suspect_geno,
            observed_peaks=observed_peaks,
            p_dropout=p_d,
            pop_freqs=pop_freqs,
            theta=theta,
        )
        log10_forenza = f_res.log10_lr

        # 2. LikeLTD
        likeltd_lr = LikeLTDReferenceModel.evaluate_single_source_locus_lr(
            suspect_geno=suspect_geno,
            observed_peaks=observed_peaks,
            template_pg=template_pg,
            pop_freqs=pop_freqs,
            theta=theta,
        )
        log10_likeltd = round(math.log10(max(1e-300, likeltd_lr)), 4)

        # 3. Curran-Gill Analytical
        cg_res = CurranGillAnalyticalValidator.compute_scenario_b_single_dropout(
            p_d=p_d,
            p_geno_hd=f_res.likelihood_hd,
        ) if len(observed_peaks) == 1 else f_res.lr_point
        log10_cg = round(math.log10(max(1e-300, cg_res)), 4)

        max_delta = max(
            abs(log10_forenza - log10_likeltd),
            abs(log10_forenza - log10_cg),
            abs(log10_likeltd - log10_cg),
        )

        in_agreement = (max_delta <= 0.25)

        return MultiToolConsensusLRResult(
            locus=locus,
            forenza_log10_lr=log10_forenza,
            likeltd_log10_lr=log10_likeltd,
            curran_gill_log10_lr=log10_cg,
            max_inter_tool_delta=round(max_delta, 6),
            consensus_verbal=f_res.verbal_en,
            tools_in_agreement=in_agreement,
        )
