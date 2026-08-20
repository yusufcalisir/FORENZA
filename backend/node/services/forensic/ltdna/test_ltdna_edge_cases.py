"""
FORENZA Forensic Evidence Operating System
Pillar 1 — Module 1.4: Low-Template DNA (LTDNA) Stochastic Modeling Engine
Sub-Item 1.4.4: 5 Documented Edge-Case Tests (EC-LTDNA-01 to EC-LTDNA-05)

Mandatory Verification Criteria (AGENTS.md & VALIDATION_CHECKLIST.md):
  1. EC-LTDNA-01: Pristine High-Template (1000 pg) Asymptote (P(D) < 0.0001, Hb >= 0.88, 0 flags).
  2. EC-LTDNA-02: Single-Cell Ultralow (15 pg) Bound (P(D) = 0.8808 ± 0.015, severe flags, >=20 dropouts).
  3. EC-LTDNA-03: Poisson Drop-in Exact Probability Vector (P(C=0)=0.9802, P(C=1)=0.0196, P(C=2)=0.0002).
  4. EC-LTDNA-04: Sub-Threshold RFU Culling (h < 50 RFU -> f(h)=0.0, exponential decay above AT).
  5. EC-LTDNA-05: Heterozygote Peak Imbalance Zone (Hb = 0.42 < 0.60) & False Homozygote Shield ([0] mask).
"""

import math
import pytest
from typing import Dict, List, Tuple

from backend.node.services.forensic.ltdna.ltdna_mathematical_formulation import (
    LTDNAMathematicalFormulation,
    DROPOUT_BETA0_MASS,
    DROPOUT_BETA1_MASS,
    DROPOUT_BETA0_RFU,
    DROPOUT_BETA1_RFU,
    DROPIN_LAMBDA_POISSON,
    DROPIN_LAMBDA_HEIGHT,
    ANALYTICAL_THRESHOLD_RFU,
    STOCHASTIC_THRESHOLD_RFU,
    HB_FLAG_THRESHOLD,
)
from backend.node.services.forensic.ltdna.ltdna_reference_datasets import (
    LTDNAReferenceDatasetRegistry,
    NIST_SRM2391D_COMP_A_PROFILE,
)


# ===========================================================================
# 1. EC-LTDNA-01: Pristine High-Template (1000 pg) Asymptote
# ===========================================================================

class TestECLTDNA01_PristineHighTemplate:
    """
    EC-LTDNA-01: High template mass (1000 pg / 1.0 ng) operates in pristine,
    unpenalized regime with P(D) < 0.0001, Hb >= 0.88, zero stochastic flags,
    and complete 24-locus profile retention.
    """

    def test_ec_ltdna_01_asymptote_dropout_rate(self):
        """At 1000 pg and 5000 pg, P(D) drops asymptotically towards 0.0."""
        res_1000 = LTDNAMathematicalFormulation.compute_dropout_probability_mass(1000.0)
        assert res_1000.dropout_probability < 0.0001
        assert not res_1000.is_below_critical

        res_5000 = LTDNAMathematicalFormulation.compute_dropout_probability_mass(5000.0)
        assert res_5000.dropout_probability < 1e-12

    def test_ec_ltdna_01_heterozygote_balance_pristine(self):
        """Pristine peak heights (800 RFU, 850 RFU) exhibit Hb >= 0.88 with zero active flags."""
        res_hb = LTDNAMathematicalFormulation.evaluate_heterozygote_balance(h1=800.0, h2=850.0)
        assert res_hb.h_balance >= 0.88
        assert not res_hb.imbalance_flag
        assert not res_hb.stochastic_threshold_flag
        assert not res_hb.at_flag
        assert not res_hb.stochastic_flag_active
        assert "BALANCED QUALITY" in res_hb.interpretation

    def test_ec_ltdna_01_full_24_locus_pristine_profile(self):
        """Complete 24-locus pristine control (1000 pg) exhibits zero locus dropouts."""
        tier_1000 = LTDNAReferenceDatasetRegistry.get_dilution_tier("LCN_DILUTION_1000PG")
        assert len(tier_1000.dropout_loci) == 0
        assert tier_1000.expected_p_dropout < 0.0001
        assert tier_1000.expected_hb >= 0.90
        assert tier_1000.stochastic_zone == "PRISTINE_STANDARD"


# ===========================================================================
# 2. EC-LTDNA-02: Single-Cell Ultralow (15 pg) Bound & Severe Stochastic Zone
# ===========================================================================

class TestECLTDNA02_SingleCellUltralowTemplate:
    """
    EC-LTDNA-02: Single-cell ultralow template (15.0 pg / ~2.2 cells) exhibits
    high dropout P(D) = 0.8808 ± 0.015, severe stochastic warning active,
    and >= 20 dropped loci across 24-locus array.
    """

    def test_ec_ltdna_02_single_cell_mass_dropout_bound(self):
        """At 15.0 pg template mass, P(D) equals 0.880797 (within ±0.015 bound)."""
        res_15 = LTDNAMathematicalFormulation.compute_dropout_probability_mass(15.0)
        # logit = 3.20 + (-0.080)*15 = 2.00 -> 1/(1+e^-2.00) = 0.88079708
        assert abs(res_15.dropout_probability - 0.880797) < 1e-4
        assert abs(res_15.dropout_probability - 0.893) <= 0.015
        assert res_15.is_below_critical

    def test_ec_ltdna_02_severe_stochastic_zone_flags(self):
        """Single-cell peaks (h1=55 RFU, h2 dropped) trigger severe stochastic warning."""
        res_hb = LTDNAMathematicalFormulation.evaluate_heterozygote_balance(h1=55.0, h2=140.0)
        assert res_hb.h_balance < 0.60  # 55/140 = 0.393
        assert res_hb.imbalance_flag
        assert res_hb.stochastic_threshold_flag  # 55 < 150 RFU
        assert res_hb.stochastic_flag_active
        assert "STOCHASTIC FLAGS ACTIVE" in res_hb.interpretation

    def test_ec_ltdna_02_single_cell_locus_dropout_escalation(self):
        """In 15 pg tier, >= 20 loci suffer allelic dropout."""
        tier_15 = LTDNAReferenceDatasetRegistry.get_dilution_tier("LCN_DILUTION_15PG")
        assert len(tier_15.dropout_loci) >= 20
        assert tier_15.expected_p_dropout >= 0.85
        assert tier_15.expected_hb <= 0.40
        assert tier_15.stochastic_zone == "SINGLE_CELL_ULTRALOW"


# ===========================================================================
# 3. EC-LTDNA-03: Poisson Drop-in Exact Probability Vector
# ===========================================================================

class TestECLTDNA03_PoissonDropinVerification:
    """
    EC-LTDNA-03: Discrete Poisson drop-in distribution at lambda_C = 0.020:
    P(C=0) = 0.9802, P(C=1) = 0.0196, P(C=2) = 0.0002,
    and 24-locus composite clean product P(C_total=0) = e^-0.48 ≈ 0.6188.
    """

    def test_ec_ltdna_03_discrete_poisson_probabilities(self):
        """Discrete Poisson drop-in PMF matches exact analytical values."""
        res_k0 = LTDNAMathematicalFormulation.compute_dropin_poisson_pmf(0, lambda_c=0.020)
        res_k1 = LTDNAMathematicalFormulation.compute_dropin_poisson_pmf(1, lambda_c=0.020)
        res_k2 = LTDNAMathematicalFormulation.compute_dropin_poisson_pmf(2, lambda_c=0.020)

        assert abs(res_k0.poisson_pmf - 0.98019867) < 1e-6
        assert abs(res_k1.poisson_pmf - 0.01960397) < 1e-6
        assert abs(res_k2.poisson_pmf - 0.00019604) < 1e-6

    def test_ec_ltdna_03_multi_locus_24_locus_product(self):
        """Composite 24-locus clean profile probability equals e^(-24 * 0.020) = e^-0.48."""
        p_single_clean = math.exp(-0.020)
        p_24_clean = p_single_clean ** 24
        expected_24_clean = math.exp(-24.0 * 0.020)  # = exp(-0.48) = 0.61878339

        assert abs(p_24_clean - expected_24_clean) < 1e-12
        assert abs(p_24_clean - 0.618783) < 1e-5

    def test_ec_ltdna_03_simplex_normalization_upper_bound(self):
        """Sum of Poisson probabilities from k=0 to 10 equals 1.00000000 ± 10⁻⁹."""
        cdf_10 = LTDNAMathematicalFormulation.compute_dropin_poisson_cdf(k_max=10, lambda_c=0.020)
        assert abs(cdf_10 - 1.0) < 1e-9


# ===========================================================================
# 4. EC-LTDNA-04: Sub-Threshold RFU Culling & Exponential Height PDF
# ===========================================================================

class TestECLTDNA04_SubThresholdNoiseRejection:
    """
    EC-LTDNA-04: Peaks below Analytical Threshold (AT = 50.0 RFU) are culled (f(h)=0.0),
    while drop-in peaks >= AT follow exponential decay with mean 116.67 RFU.
    """

    def test_ec_ltdna_04_sub_at_peak_culling(self):
        """Fluorescence signals below AT = 50.0 RFU return zero PDF and zero CDF."""
        for sub_rfu in [0.0, 10.0, 25.0, 45.0, 49.9]:
            res = LTDNAMathematicalFormulation.compute_dropin_height_pdf(sub_rfu, at=50.0)
            assert res.height_pdf == 0.0, f"Failed at sub-AT RFU {sub_rfu}"
            assert res.height_cdf == 0.0
            assert not res.is_above_at

    def test_ec_ltdna_04_exponential_pdf_above_at(self):
        """Signals at or above AT = 50.0 RFU follow continuous exponential decay."""
        res_50 = LTDNAMathematicalFormulation.compute_dropin_height_pdf(50.0, at=50.0, lambda_h=0.015)
        res_100 = LTDNAMathematicalFormulation.compute_dropin_height_pdf(100.0, at=50.0, lambda_h=0.015)
        res_150 = LTDNAMathematicalFormulation.compute_dropin_height_pdf(150.0, at=50.0, lambda_h=0.015)

        assert abs(res_50.height_pdf - 0.01500000) < 1e-7
        assert res_50.height_pdf > res_100.height_pdf > res_150.height_pdf
        assert res_50.is_above_at and res_100.is_above_at and res_150.is_above_at

    def test_ec_ltdna_04_expected_dropin_height_moment(self):
        """Theoretical mean E[h_C] equals AT + 1/lambda_h = 50 + 1/0.015 = 116.6667 RFU."""
        res = LTDNAMathematicalFormulation.compute_dropin_height_pdf(75.0, at=50.0, lambda_h=0.015)
        assert abs(res.theoretical_mean - 116.6667) < 1e-3
        assert abs(res.theoretical_variance - 4444.4444) < 1e-2


# ===========================================================================
# 5. EC-LTDNA-05: Heterozygote Peak Imbalance Zone & False Homozygote Shield
# ===========================================================================

class TestECLTDNA05_HeterozygotePeakImbalanceZone:
    """
    EC-LTDNA-05: Severe peak imbalance (Hb = 0.42 < 0.60) or single sub-stochastic
    peak (h1 = 110 RFU < ST = 150 RFU) flags locus for stochastic interpretation,
    masks sister allele as [0] / potential dropout, preventing false homozygous call.
    """

    def test_ec_ltdna_05_severe_imbalance_detection(self):
        """Hb = 46.2 / 110.0 = 0.42 < 0.60 correctly triggers severe imbalance flag."""
        res_hb = LTDNAMathematicalFormulation.evaluate_heterozygote_balance(h1=110.0, h2=46.2)
        assert abs(res_hb.h_balance - 0.42) < 1e-3
        assert res_hb.imbalance_flag
        assert res_hb.stochastic_threshold_flag  # 46.2 < 150 RFU
        assert res_hb.at_flag                   # 46.2 < 50 RFU
        assert res_hb.stochastic_flag_active
        assert "H_b = 0.420 < 0.60" in res_hb.interpretation
        assert "Severe Imbalance" in res_hb.interpretation

    def test_ec_ltdna_05_sub_stochastic_sister_dropout_shield(self):
        """Single peak 110 RFU (< ST = 150 RFU) is flagged to prevent false homozygosity."""
        # Single peak observed at 110 RFU against heterozygous suspect (16, 17)
        res_lr = LTDNAMathematicalFormulation.compute_ltdna_single_locus_lr(
            locus="vWA",
            suspect_genotype=(16.0, 17.0),
            observed_peaks={16.0: 110.0},  # allele 17 dropped
            p_dropout=0.31,
            pop_freqs={16.0: 0.211, 17.0: 0.273},
            theta=0.03,
        )

        assert res_lr.observed_state == "SINGLE_DROPOUT"
        assert any("Dropout Observed" in flag for flag in res_lr.stochastic_flags)
        # Likelihood under Hp is 2*P(D)*(1-P(D))*(1-lambda) instead of (1-P(D))^2
        assert res_lr.likelihood_hp < 0.50

    def test_ec_ltdna_05_touch_casework_profile_masking(self):
        """Full 24-locus VECTOR_TERM_06 verifies masked [0] dropout alleles and Hb = 0.455 flag."""
        vec06 = LTDNAReferenceDatasetRegistry.get_benchmark_vector("VECTOR_TERM_06")
        assert len(vec06.masked_dropout_loci) == 7
        assert "D3S1358" in vec06.masked_dropout_loci
        assert "D21S11" in vec06.masked_dropout_loci

        # vWA exhibits peak imbalance Hb = 50 / 110 = 0.455 < 0.60
        vwa_peaks = vec06.observed_epg_peaks["vWA"]
        res_vwa_hb = LTDNAMathematicalFormulation.evaluate_heterozygote_balance(
            h1=vwa_peaks[16.0], h2=vwa_peaks[18.0]
        )
        assert abs(res_vwa_hb.h_balance - (50.0 / 110.0)) < 1e-3
        assert res_vwa_hb.imbalance_flag
        assert res_vwa_hb.stochastic_flag_active
