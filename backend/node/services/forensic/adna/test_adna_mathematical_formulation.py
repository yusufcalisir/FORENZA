"""
Unit Test Suite for FORENZA Ancient DNA Mathematical Formulation Engine (Module 2.5).
Validates Briggs deamination decay, fragment length distributions, damage-aware SNP likelihood,
multi-SNP cumulative LR, modern contaminant subtraction, and pre-break purine excess.
"""

import pytest
import math

from node.services.forensic.adna.adna_mathematical_formulation import (
    AdnaMathematicalFormulation,
    DegradationRiskTier,
)


class TestDeaminationKinetics:
    """Verifies Briggs deamination curve calculations."""

    def test_position_1_terminal_deamination(self):
        # Position 1: delta_1 = delta_0 * exp(0) + baseline = delta_0 + baseline
        rate = AdnaMathematicalFormulation.compute_deamination_rate(1, delta_0=0.35, decay_alpha=0.10, baseline=0.005)
        assert abs(rate - 0.355) < 1e-6

    def test_exponential_decay_interior(self):
        # Position 20: delta_20 = 0.35 * exp(-0.10 * 19) + 0.005 = 0.35 * 0.1495686 + 0.005 = 0.057349
        rate = AdnaMathematicalFormulation.compute_deamination_rate(20, delta_0=0.35, decay_alpha=0.10, baseline=0.005)
        assert abs(rate - 0.057349) < 1e-4

    def test_full_curves_generation(self):
        res = AdnaMathematicalFormulation.generate_mapdamage_curves(
            delta_0=0.25, decay_alpha=0.12, baseline=0.005, max_position=25
        )
        assert len(res.curve_5p_c_to_t) == 25
        assert len(res.curve_3p_g_to_a) == 25
        assert res.curve_5p_c_to_t[1] > res.curve_5p_c_to_t[10] > res.curve_5p_c_to_t[25]


class TestFragmentationDistribution:
    """Verifies fragment length distribution calculations."""

    def test_severe_fragmentation_stats(self):
        # lambda = 0.0446, L_min = 30 -> mean length = 1/0.0446 + 30 ≈ 52.42 bp
        stats = AdnaMathematicalFormulation.compute_exponential_fragmentation(lambda_param=0.0446, l_min=30.0)
        assert abs(stats.mean_length - 52.42) < 0.1
        assert stats.degradation_tier == DegradationRiskTier.SEVERE
        assert stats.recommended_technology == "MICRO_SNP_PANEL_40_70BP"
        assert stats.fraction_below_100bp > 0.90

    def test_pristine_fragmentation_stats(self):
        # lambda = 0.0031, L_min = 30 -> mean length = 1/0.0031 + 30 ≈ 352.58 bp
        stats = AdnaMathematicalFormulation.compute_exponential_fragmentation(lambda_param=0.0031, l_min=30.0)
        assert stats.mean_length > 300.0
        assert stats.degradation_tier == DegradationRiskTier.PRISTINE


class TestDamageAwareSNPLikelihood:
    """Verifies low-coverage damage-compensated SNP calling."""

    def test_terminal_t_on_ref_c_compensated(self):
        # 3 reads of 'T' observed at position 1 (terminal 5' end) where reference is 'C'
        # With high delta_0 = 0.40, damage compensation should recognize this as potential C/C + damage
        res = AdnaMathematicalFormulation.compute_damage_aware_snp_likelihood(
            locus_id="rs12345",
            ref_allele="C",
            alt_allele="T",
            read_bases=["T", "T", "T"],
            read_positions=[1, 1, 1],
            delta_0=0.40,
            decay_alpha=0.10,
        )
        assert res.is_damage_compensated is True
        assert res.deamination_risk_flag is True
        assert res.raw_likelihoods["AA"] > 0.0

    def test_interior_t_calls_true_variant(self):
        # 5 reads of 'T' observed deep in the fragment (position 35) where delta_k ≈ 0
        res = AdnaMathematicalFormulation.compute_damage_aware_snp_likelihood(
            locus_id="rs99999",
            ref_allele="C",
            alt_allele="T",
            read_bases=["T", "T", "T", "T", "T"],
            read_positions=[35, 40, 42, 38, 45],
            delta_0=0.40,
            decay_alpha=0.10,
        )
        assert res.called_genotype == "BB"
        assert res.posterior_probabilities["BB"] > 0.90


class TestContaminationAndPurineExcess:
    """Verifies modern contaminant subtraction and pre-break purine statistics."""

    def test_contamination_subtraction(self):
        obs = {1: 0.22, 2: 0.18}
        res = AdnaMathematicalFormulation.subtract_modern_contamination(
            obs, contamination_fraction=0.12, modern_terminal_rate=0.002
        )
        # True ancient delta_1 = (0.22 - 0.12*0.002)/0.88 ≈ 0.2497
        assert abs(res.true_ancient_terminal_damage - 0.2497) < 1e-3
        assert res.true_ancient_terminal_damage > res.observed_terminal_damage

    def test_pre_break_purine_excess(self):
        frac, is_anc = AdnaMathematicalFormulation.compute_pre_break_purine_excess(720, 1000)
        assert frac == 0.72
        assert is_anc is True

        frac_modern, is_anc_modern = AdnaMathematicalFormulation.compute_pre_break_purine_excess(500, 1000)
        assert frac_modern == 0.50
        assert is_anc_modern is False
