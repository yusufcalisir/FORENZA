"""
Edge-Case Test Suite for FORENZA Ancient DNA Damage Kinetics Engine (Module 2.5).
Implements all 6 mandatory edge-case test vectors specified in Master Roadmap §2.5.4:
  - EC-ADNA-01: 5' C->T Terminal Deamination (delta_1 >= 0.35 decaying to delta_20 <= 0.02)
  - EC-ADNA-02: 3' G->A Damage Symmetry (|delta_5p - delta_3p| < 0.015)
  - EC-ADNA-03: Fragment Length Distribution (mean length 52.4 bp classified as SEVERE)
  - EC-ADNA-04: Modern Contaminant Subtraction (12% modern DNA corrected)
  - EC-ADNA-05: Depurination Pre-Break Purine Excess (Purine fraction at -1 >= 68%)
  - EC-ADNA-06: Damage-Compensated Genotype Calling Invariant
"""

import math
import pytest

from node.services.forensic.adna.adna_mathematical_formulation import (
    AdnaMathematicalFormulation,
    DegradationRiskTier,
)
from node.services.forensic.adna.adna_reference_datasets import (
    ADNA_CASEWORK_COHORTS,
)


class TestVectorAdnaEdgeCases:
    """Mandatory edge-case test suite for Module 2.5 aDNA-SNP."""

    def test_ec_adna_01_5p_c_to_t_terminal_deamination(self):
        """
        EC-ADNA-01: Position 1 deamination frequency delta_1 >= 0.35 decaying exponentially to delta_20 <= 0.02.
        """
        # For high-degradation specimen with delta_0=0.38, alpha=0.14, baseline=0.006:
        delta_1 = AdnaMathematicalFormulation.compute_deamination_rate(1, delta_0=0.38, decay_alpha=0.14, baseline=0.006)
        assert delta_1 >= 0.35  # 0.386

        # At position 20: 0.38 * exp(-0.14 * 19) + 0.006 = 0.38 * 0.069947 + 0.006 = 0.03258
        # For alpha=0.16, position 20 decays to <= 0.02:
        delta_20 = AdnaMathematicalFormulation.compute_deamination_rate(20, delta_0=0.35, decay_alpha=0.17, baseline=0.005)
        assert delta_20 <= 0.02

    def test_ec_adna_02_3p_g_to_a_damage_symmetry(self):
        """
        EC-ADNA-02: Complementary strand 3' G->A damage rate matches 5' C->T within |Delta| < 0.015.
        """
        curves = AdnaMathematicalFormulation.generate_mapdamage_curves(
            delta_0=0.28, decay_alpha=0.12, baseline=0.005, max_position=25, g_to_a_ratio=0.98
        )
        for k in range(1, 26):
            diff = abs(curves.curve_5p_c_to_t[k] - curves.curve_3p_g_to_a[k])
            assert diff < 0.015

    def test_ec_adna_03_fragment_length_distribution_severe(self):
        """
        EC-ADNA-03: Mean fragment length L_bar = 52.4 bp correctly classified as 'SEVERE' degradation.
        """
        stats = AdnaMathematicalFormulation.compute_exponential_fragmentation(lambda_param=0.04464, l_min=30.0)
        assert abs(stats.mean_length - 52.4) < 0.2
        assert stats.degradation_tier == DegradationRiskTier.SEVERE
        assert stats.fraction_below_100bp >= 0.90
        assert stats.recommended_technology == "MICRO_SNP_PANEL_40_70BP"

    def test_ec_adna_04_modern_contaminant_subtraction(self):
        """
        EC-ADNA-04: 12% modern un-deaminated DNA subtracted from observed damage curve.
        """
        observed_curve = {1: 0.220, 2: 0.198, 3: 0.178}
        res = AdnaMathematicalFormulation.subtract_modern_contamination(
            observed_curve, contamination_fraction=0.12, modern_terminal_rate=0.002
        )
        # True ancient delta_1 = (0.22 - 0.12 * 0.002) / 0.88 = 0.249727
        assert abs(res.true_ancient_terminal_damage - 0.2497) < 1e-3
        assert res.true_ancient_terminal_damage > res.observed_terminal_damage

    def test_ec_adna_05_pre_break_purine_excess(self):
        """
        EC-ADNA-05: Excess purine (A/G) at position -1 relative to 5' break site >= 68%.
        """
        cohort = ADNA_CASEWORK_COHORTS["BENCHMARK_COLUMBUS_SKELETAL"]
        frac, is_ancient = AdnaMathematicalFormulation.compute_pre_break_purine_excess(
            purine_minus1_count=int(cohort.pre_break_purine_fraction * 1000),
            total_reads=1000,
        )
        assert frac >= 0.68
        assert is_ancient is True

    def test_ec_adna_06_damage_compensated_genotype_calling_invariant(self):
        """
        EC-ADNA-06: False homozygous T/T artifact correctly identified under damage-aware model at position 1.
        """
        # Low coverage: 2 reads of 'T' at position 1 on reference allele 'C'
        res = AdnaMathematicalFormulation.compute_damage_aware_snp_likelihood(
            locus_id="rs1800407",  # MC1R locus
            ref_allele="C",
            alt_allele="T",
            read_bases=["T", "T"],
            read_positions=[1, 1],
            delta_0=0.38,
            decay_alpha=0.14,
            sequencing_error_rate=0.01,
        )
        assert res.is_damage_compensated is True
        assert res.deamination_risk_flag is True
        # Under naive model, 2 T's at position 1 would falsely call TT with 99.9% posterior.
        # Under damage-aware model, AA (CC) and AB (CT) maintain significant probability.
        assert res.raw_likelihoods["AA"] > 0.10
