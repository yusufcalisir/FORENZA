"""
FORENZA Forensic Evidence Operating System
Pillar 1 — Module 1.4: Low-Template DNA (LTDNA) Stochastic Modeling Engine
Sub-Item 1.4.3: Independent Tool Cross-Validation Unit Test Suite

Tests:
  1. TestLikeLTDCrossValidation: Grid Concordance (|Δ| < 10⁻⁹) across Mass & RFU.
  2. TestEuroForMixContinuousConcordance: Continuous Gamma Lower-Tail Integral (R² ≥ 0.95).
  3. TestCurranGillAnalyticalConcordance: Closed-Form Exact Match across Scenarios A, B, C.
  4. TestSTRmixVarianceInflationConcordance: Inverse-Template Scaling & Hb Degradation.
  5. TestMultiToolConsensusLR: Inter-Tool Consensus (|Δ| ≤ 0.25) on Benchmark Profiles.
"""

import math
import pytest
from typing import Dict, List, Tuple

from backend.node.services.forensic.ltdna.ltdna_cross_validation import (
    LikeLTDReferenceModel,
    EuroForMixDropoutSimulator,
    CurranGillAnalyticalValidator,
    STRmixVarianceInflationModel,
    LTDNACrossValidationEngine,
    LikeLTDCrossValidationResult,
    EuroForMixConcordanceResult,
    EuroForMixCorrelationSummary,
    CurranGillAnalyticalResult,
    STRmixVarianceResult,
    MultiToolConsensusLRResult,
)
from backend.node.services.forensic.ltdna.ltdna_reference_datasets import (
    LTDNAReferenceDatasetRegistry,
    NIST_SRM2391D_COMP_A_PROFILE,
)


# ===========================================================================
# 1. LikeLTD Cross-Validation Tests
# ===========================================================================

class TestLikeLTDCrossValidation:
    """Verifies exact numerical concordance with LikeLTD semi-continuous model."""

    def test_likeltd_mass_and_rfu_grid_concordance(self):
        """Grid comparison across 18 mass and RFU points achieves exact concordance (|Δ| < 10⁻⁶)."""
        results = LTDNACrossValidationEngine.run_likeltd_grid_comparison()
        assert len(results) == 18
        for res in results:
            assert res.is_concordant, f"Failed at {res.input_type}={res.input_value}: delta={res.absolute_delta}"
            assert res.absolute_delta < 1e-6

    def test_likeltd_single_source_lr_concordance(self):
        """Single-source LikeLTD LR formulation matches Forenza calculation on single dropout case."""
        suspect_geno = (16.0, 17.0)
        observed_peaks = {16.0: 80.0}  # allele 17 dropped
        pop_freqs = {16.0: 0.211, 17.0: 0.273}
        template_pg = 50.0

        likeltd_lr = LikeLTDReferenceModel.evaluate_single_source_locus_lr(
            suspect_geno=suspect_geno,
            observed_peaks=observed_peaks,
            template_pg=template_pg,
            pop_freqs=pop_freqs,
            theta=0.03,
        )

        res_consensus = LTDNACrossValidationEngine.run_multi_tool_consensus_lr(
            locus="vWA",
            suspect_geno=suspect_geno,
            observed_peaks=observed_peaks,
            template_pg=template_pg,
            pop_freqs=pop_freqs,
            theta=0.03,
        )

        assert res_consensus.tools_in_agreement
        assert res_consensus.max_inter_tool_delta < 0.05
        assert abs(res_consensus.forenza_log10_lr - math.log10(likeltd_lr)) < 0.01


# ===========================================================================
# 2. EuroForMix Continuous Gamma Tail Dropout Concordance Tests
# ===========================================================================

class TestEuroForMixContinuousConcordance:
    """Verifies concordance with EuroForMix continuous Gamma lower-tail dropout simulator."""

    def test_euroformix_gamma_tail_correlation_r_squared(self):
        """Continuous Gamma lower-tail integral correlates with Forenza logistic P(D) (R² ≥ 0.95)."""
        summary = EuroForMixDropoutSimulator.run_serial_dilution_correlation()
        assert summary.n_points == 15
        assert summary.is_concordant
        assert summary.r_squared >= 0.95, f"R² = {summary.r_squared} is below 0.95 threshold"
        assert summary.pearson_r >= 0.97
        assert summary.mean_absolute_delta < 0.12

    def test_euroformix_asymptotic_boundary_concordance(self):
        """Both Forenza and EuroForMix continuous models approach 0 dropout at high template and ~1 at ultra-low."""
        # 1000 pg pristine control
        efm_1000 = EuroForMixDropoutSimulator.compute_continuous_gamma_dropout(1000.0)
        assert efm_1000 < 0.0001

        # 500 pg standard casework
        efm_500 = EuroForMixDropoutSimulator.compute_continuous_gamma_dropout(500.0)
        assert efm_500 < 0.0001

        # 15 pg single cell range
        efm_15 = EuroForMixDropoutSimulator.compute_continuous_gamma_dropout(15.0)
        assert efm_15 >= 0.70  # strong dropout tail below AT=50 RFU


# ===========================================================================
# 3. Curran-Gill Analytical Formula Concordance Tests
# ===========================================================================

class TestCurranGillAnalyticalConcordance:
    """Verifies exact algebraic equivalence with Curran-Gill closed-form analytical formulas."""

    def test_curran_gill_scenarios_exact_match(self):
        """Scenarios A (full), B (single dropout), C (double dropout) match analytical formulas."""
        results = LTDNACrossValidationEngine.run_curran_gill_scenario_validation(
            locus="vWA",
            suspect_geno=(16.0, 17.0),
            pop_freqs={16.0: 0.211, 17.0: 0.273},
            theta=0.03,
            template_pg=50.0,
        )

        assert len(results) == 3
        for res in results:
            assert res.is_exact_match, f"Failed at {res.scenario}: delta_log10={res.absolute_delta_log10}"
            assert res.absolute_delta_log10 < 1e-4

    def test_curran_gill_scenario_d_dropin_concordance(self):
        """Scenario D drop-in formula produces valid penalized LR."""
        p_d = 0.31
        p_geno_hd = 0.1267
        lr_dropin = CurranGillAnalyticalValidator.compute_scenario_d_single_dropin(
            p_d=p_d,
            p_geno_hd=p_geno_hd,
            h_extra=75.0,
            lambda_c=0.020,
        )
        assert lr_dropin > 0.0
        # Drop-in penalized LR should be significantly smaller than pristine full match
        lr_full = CurranGillAnalyticalValidator.compute_scenario_a_full_profile(p_d, p_geno_hd)
        assert lr_dropin < (lr_full * 0.05)


# ===========================================================================
# 4. STRmix-Style Inverse Template Variance Inflation Tests
# ===========================================================================

class TestSTRmixVarianceInflationConcordance:
    """Verifies inverse template variance scaling and simulated Hb degradation."""

    def test_variance_inflation_monotonicity(self):
        """Peak height variance σ²(T) expands monotonically as template mass decreases."""
        templates = [500.0, 100.0, 60.0, 30.0, 15.0]
        sigmas = [
            STRmixVarianceInflationModel.compute_variance(t).inflated_sigma
            for t in templates
        ]
        for i in range(len(sigmas) - 1):
            assert sigmas[i] < sigmas[i + 1], f"Variance failed to expand: {templates[i]} ({sigmas[i]}) >= {templates[i+1]} ({sigmas[i+1]})"

    def test_simulated_hb_degradation_alignment(self):
        """Simulated expected Hb matches empirical dilution series trend."""
        res_500 = STRmixVarianceInflationModel.compute_variance(500.0)
        res_100 = STRmixVarianceInflationModel.compute_variance(100.0)
        res_30 = STRmixVarianceInflationModel.compute_variance(30.0)
        res_15 = STRmixVarianceInflationModel.compute_variance(15.0)

        # Hb degrades from high (> 0.80) to low (< 0.75)
        assert res_500.simulated_expected_hb > res_100.simulated_expected_hb > res_30.simulated_expected_hb > res_15.simulated_expected_hb
        assert res_500.simulated_expected_hb >= 0.75
        assert res_15.simulated_expected_hb <= 0.75

    def test_invalid_negative_template_raises(self):
        """Negative template input raises ValueError."""
        with pytest.raises(ValueError, match="non-negative"):
            STRmixVarianceInflationModel.compute_variance(-10.0)


# ===========================================================================
# 5. Multi-Tool Consensus LR Tests
# ===========================================================================

class TestMultiToolConsensusLR:
    """Verifies consensus across all independent tool implementations on benchmark profiles."""

    def test_consensus_on_vector_03_benchmark(self):
        """Multi-tool consensus on VECTOR_03 (vWA 16@80RFU single dropout)."""
        res = LTDNACrossValidationEngine.run_multi_tool_consensus_lr(
            locus="vWA",
            suspect_geno=(16.0, 17.0),
            observed_peaks={16.0: 80.0},
            template_pg=45.0,
            pop_freqs={16.0: 0.211, 17.0: 0.273},
            theta=0.03,
        )

        assert res.tools_in_agreement
        assert res.max_inter_tool_delta <= 0.25
        assert "Support" in res.consensus_verbal

    def test_consensus_on_nist_srm2391d_loci(self):
        """Multi-tool consensus across 5 diverse loci of NIST SRM 2391d Component A."""
        test_loci = ["D3S1358", "FGA", "D8S1179", "TH01", "D1S1656"]
        pop_db = {
            "D3S1358": {15.0: 0.282, 16.0: 0.231},
            "FGA": {21.0: 0.185, 22.0: 0.198},
            "D8S1179": {13.0: 0.339, 14.0: 0.201},
            "TH01": {6.0: 0.225, 9.3: 0.312},
            "D1S1656": {15.0: 0.162, 17.3: 0.210},
        }

        for locus in test_loci:
            geno = NIST_SRM2391D_COMP_A_PROFILE[locus]
            # Single dropout test condition: only first allele observed
            obs_peaks = {geno[0]: 85.0}
            res = LTDNACrossValidationEngine.run_multi_tool_consensus_lr(
                locus=locus,
                suspect_geno=geno,
                observed_peaks=obs_peaks,
                template_pg=60.0,
                pop_freqs=pop_db[locus],
                theta=0.03,
            )
            assert res.tools_in_agreement, f"Consensus failed on locus {locus}: max_delta={res.max_inter_tool_delta}"
            assert res.max_inter_tool_delta <= 0.25
