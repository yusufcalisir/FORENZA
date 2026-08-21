"""
Mathematical Formulation Tests for FORENZA MC1R Epistasis & UV Sensitivity (Module 3.5).

Verifies verbatim constants from Pillar 3 Research §5:
  - §5.1 MC1R 'R' high-risk variant weights (D84E=2.50, R142H=2.40, R151C=2.85, R160W=2.75, D294H=2.60)
  - §5.1 MC1R 'r' low-risk variant weights (V60L=1.10, V92M=0.85, R163Q=0.75)
  - §5.2 Freckling logistic constants (intercept=-2.50, W_coeff=1.35, ASIP=0.85, BNC2=0.65)
  - §5.2 Freckling intensity thresholds (≥75 DENSE, ≥45 MODERATE, ≥20 MILD, <20 MINIMAL)
  - §5.2 MED diplotype mapping (R/R < 20, R/r|R/wt 20-35, r/r|r/wt 35-50, wt/wt > 50)
"""

import math
import pytest

from backend.node.services.forensic.phenotyping.mc1r_mathematical_formulation import (
    MC1RMathematicalFormulation,
    MC1R_R_WEIGHTS,
    MC1R_r_WEIGHTS,
    MODIFIER_WEIGHTS,
    FRECKLING_INTERCEPT,
    FRECKLING_W_MC1R_COEFF,
    FRECKLING_ASIP_COEFF,
    FRECKLING_BNC2_COEFF,
    FRECKLING_DENSE_THRESHOLD,
    FRECKLING_MODERATE_THRESHOLD,
    FRECKLING_MILD_THRESHOLD,
    MED_R_R_CATEGORY,
    MED_R_HET_CATEGORY,
    MED_r_HOM_CATEGORY,
    MED_WT_CATEGORY,
)


class TestMC1RLociRegistry:
    """Verifies the loci registry constants."""

    def test_r_variant_count(self):
        assert len(MC1R_R_WEIGHTS) == 5

    def test_r_variant_rsids(self):
        assert "rs1805006" in MC1R_R_WEIGHTS   # D84E
        assert "rs75570604" in MC1R_R_WEIGHTS  # R142H
        assert "rs1805007" in MC1R_R_WEIGHTS   # R151C
        assert "rs1805008" in MC1R_R_WEIGHTS   # R160W
        assert "rs1805009" in MC1R_R_WEIGHTS   # D294H

    def test_r_variant_weights_exact(self):
        assert MC1R_R_WEIGHTS["rs1805006"]["weight"] == pytest.approx(2.50, abs=1e-9)   # D84E
        assert MC1R_R_WEIGHTS["rs75570604"]["weight"] == pytest.approx(2.40, abs=1e-9)  # R142H
        assert MC1R_R_WEIGHTS["rs1805007"]["weight"] == pytest.approx(2.85, abs=1e-9)   # R151C (highest)
        assert MC1R_R_WEIGHTS["rs1805008"]["weight"] == pytest.approx(2.75, abs=1e-9)   # R160W
        assert MC1R_R_WEIGHTS["rs1805009"]["weight"] == pytest.approx(2.60, abs=1e-9)   # D294H

    def test_r_low_variant_count(self):
        assert len(MC1R_r_WEIGHTS) == 3

    def test_r_low_variant_weights_exact(self):
        assert MC1R_r_WEIGHTS["rs1805005"]["weight"] == pytest.approx(1.10, abs=1e-9)  # V60L
        assert MC1R_r_WEIGHTS["rs2228479"]["weight"] == pytest.approx(0.85, abs=1e-9)  # V92M
        assert MC1R_r_WEIGHTS["rs885479"]["weight"] == pytest.approx(0.75, abs=1e-9)   # R163Q

    def test_modifier_weights(self):
        assert MODIFIER_WEIGHTS["rs1015362"]["weight"] == pytest.approx(0.85, abs=1e-9)  # ASIP
        assert MODIFIER_WEIGHTS["rs10756819"]["weight"] == pytest.approx(0.65, abs=1e-9)  # BNC2


class TestFrecklingConstants:
    """Verifies freckling logistic model constants."""

    def test_intercept(self):
        assert FRECKLING_INTERCEPT == pytest.approx(-2.50, abs=1e-9)

    def test_w_mc1r_coefficient(self):
        assert FRECKLING_W_MC1R_COEFF == pytest.approx(1.35, abs=1e-9)

    def test_asip_coefficient(self):
        assert FRECKLING_ASIP_COEFF == pytest.approx(0.85, abs=1e-9)

    def test_bnc2_coefficient(self):
        assert FRECKLING_BNC2_COEFF == pytest.approx(0.65, abs=1e-9)

    def test_intensity_thresholds(self):
        assert FRECKLING_DENSE_THRESHOLD == 75.0
        assert FRECKLING_MODERATE_THRESHOLD == 45.0
        assert FRECKLING_MILD_THRESHOLD == 20.0


class TestMC1RLossWeightFormula:
    """Verifies W_MC1R = Σ w_i * X_i for various genotype configurations."""

    def test_zero_weight_all_reference(self):
        w, n_R, n_r, _ = MC1RMathematicalFormulation.compute_mc1r_loss_weight({})
        assert w == pytest.approx(0.0, abs=1e-9)
        assert n_R == 0
        assert n_r == 0

    def test_r151c_het_weight(self):
        w, n_R, _, _ = MC1RMathematicalFormulation.compute_mc1r_loss_weight({"rs1805007": 1})
        assert w == pytest.approx(2.85, abs=1e-6)
        assert n_R == 1

    def test_r151c_hom_weight(self):
        w, n_R, _, _ = MC1RMathematicalFormulation.compute_mc1r_loss_weight({"rs1805007": 2})
        assert w == pytest.approx(5.70, abs=1e-6)
        assert n_R == 2

    def test_r160w_het_weight(self):
        w, n_R, _, _ = MC1RMathematicalFormulation.compute_mc1r_loss_weight({"rs1805008": 1})
        assert w == pytest.approx(2.75, abs=1e-6)

    def test_d294h_het_weight(self):
        w, n_R, _, _ = MC1RMathematicalFormulation.compute_mc1r_loss_weight({"rs1805009": 1})
        assert w == pytest.approx(2.60, abs=1e-6)

    def test_v60l_het_weight(self):
        w, _, n_r, _ = MC1RMathematicalFormulation.compute_mc1r_loss_weight({"rs1805005": 1})
        assert w == pytest.approx(1.10, abs=1e-6)
        assert n_r == 1

    def test_compound_r_r_weight(self):
        """R151C(1) + V60L(1) = 2.85 + 1.10 = 3.95."""
        w, n_R, n_r, _ = MC1RMathematicalFormulation.compute_mc1r_loss_weight({"rs1805007": 1, "rs1805005": 1})
        assert w == pytest.approx(3.95, abs=1e-6)
        assert n_R == 1
        assert n_r == 1

    def test_weight_additivity_multiple_loci(self):
        """Two R-variants should add their weights independently."""
        w_r1, _, _, _ = MC1RMathematicalFormulation.compute_mc1r_loss_weight({"rs1805007": 1})
        w_r2, _, _, _ = MC1RMathematicalFormulation.compute_mc1r_loss_weight({"rs1805008": 1})
        w_combined, _, _, _ = MC1RMathematicalFormulation.compute_mc1r_loss_weight({"rs1805007": 1, "rs1805008": 1})
        assert abs(w_combined - (w_r1 + w_r2)) < 1e-6


class TestDiplotypeClassification:
    """Verifies MC1R diplotype classification rules."""

    def test_wildtype(self):
        d, c = MC1RMathematicalFormulation.classify_diplotype(0, 0)
        assert d == "wt/wt"
        assert c == "WILD_TYPE"

    def test_r_wt(self):
        d, c = MC1RMathematicalFormulation.classify_diplotype(1, 0)
        assert d == "R/wt"
        assert c == "MODERATE_LOSS"

    def test_r_r(self):
        d, c = MC1RMathematicalFormulation.classify_diplotype(2, 0)
        assert d == "R/R"
        assert c == "SEVERE_LOSS"

    def test_r_r_compound(self):
        d, c = MC1RMathematicalFormulation.classify_diplotype(1, 1)
        assert d == "R/r"
        assert c == "MODERATE_LOSS"

    def test_r_r_hom(self):
        d, c = MC1RMathematicalFormulation.classify_diplotype(0, 2)
        assert d == "r/r"
        assert c == "MILD_LOSS"

    def test_r_wt_low(self):
        d, c = MC1RMathematicalFormulation.classify_diplotype(0, 1)
        assert d == "r/wt"
        assert c == "MILD_LOSS"

    def test_three_r_alleles(self):
        """n_R >= 2 always yields R/R regardless of count."""
        d, c = MC1RMathematicalFormulation.classify_diplotype(3, 0)
        assert d == "R/R"
        assert c == "SEVERE_LOSS"


class TestFrecklingScoreFormula:
    """Verifies F_score = 100/(1+exp(-logit)) with exact analytical values."""

    def test_wildtype_baseline_7_59(self):
        f, logit = MC1RMathematicalFormulation.compute_freckling_score(0.0, 0.0, 0.0)
        expected = 100.0 / (1.0 + math.exp(2.5))
        assert f == pytest.approx(expected, abs=0.01)
        assert logit == pytest.approx(-2.50, abs=1e-6)

    def test_r151c_hom_5_70_f_score(self):
        """R/R (W=5.70): logit = -2.5 + 1.35*5.70 = 5.195 → F ≈ 99.45%."""
        f, logit = MC1RMathematicalFormulation.compute_freckling_score(5.70, 0.0, 0.0)
        assert logit == pytest.approx(5.195, abs=1e-3)
        assert f >= 99.0

    def test_compound_r_r_3_95(self):
        """R/r (W=3.95): logit = -2.5 + 1.35*3.95 = 2.8325 → F ≈ 94.44%."""
        f, _ = MC1RMathematicalFormulation.compute_freckling_score(3.95, 0.0, 0.0)
        assert f == pytest.approx(94.44, abs=0.2)

    def test_asip_bnc2_boost(self):
        """ASIP=2, BNC2=2, W=0: logit=0.50 → F ≈ 62.25%."""
        f, logit = MC1RMathematicalFormulation.compute_freckling_score(0.0, 2.0, 2.0)
        assert logit == pytest.approx(0.50, abs=1e-6)
        assert f == pytest.approx(62.25, abs=0.1)

    def test_f_score_bounded(self):
        """F_score always in [0.0, 100.0] for any inputs."""
        for w in [0.0, 2.85, 5.70, 10.0]:
            for xa in [0, 1, 2]:
                for xb in [0, 1, 2]:
                    f, _ = MC1RMathematicalFormulation.compute_freckling_score(float(w), float(xa), float(xb))
                    assert 0.0 <= f <= 100.0


class TestFrecklingIntensityClassification:
    """Verifies 4-tier intensity thresholds."""

    def test_minimal_below_20(self):
        assert "MINIMAL" in MC1RMathematicalFormulation.classify_freckling_intensity(7.59)
        assert "MINIMAL" in MC1RMathematicalFormulation.classify_freckling_intensity(19.99)

    def test_mild_between_20_and_45(self):
        assert "MILD" in MC1RMathematicalFormulation.classify_freckling_intensity(20.0)
        assert "MILD" in MC1RMathematicalFormulation.classify_freckling_intensity(44.99)

    def test_moderate_between_45_and_75(self):
        assert "MODERATE" in MC1RMathematicalFormulation.classify_freckling_intensity(45.0)
        assert "MODERATE" in MC1RMathematicalFormulation.classify_freckling_intensity(74.99)

    def test_dense_at_75_and_above(self):
        assert "DENSE" in MC1RMathematicalFormulation.classify_freckling_intensity(75.0)
        assert "DENSE" in MC1RMathematicalFormulation.classify_freckling_intensity(99.45)
        assert "DENSE" in MC1RMathematicalFormulation.classify_freckling_intensity(100.0)


class TestMEDDiplotypMapping:
    """Verifies UV/MED diplotype mapping per Research §5.2."""

    def test_rr_med_below_20(self):
        med, tan, _ = MC1RMathematicalFormulation.compute_uv_sensitivity("R/R")
        assert "< 20" in med
        assert tan == "NEVER_TANS_ALWAYS_BURNS"

    def test_r_r_med_20_35(self):
        med, tan, _ = MC1RMathematicalFormulation.compute_uv_sensitivity("R/r")
        assert "20 - 35" in med
        assert tan == "RARE_TAN_FREQUENT_BURN"

    def test_r_wt_med_20_35(self):
        med, tan, _ = MC1RMathematicalFormulation.compute_uv_sensitivity("R/wt")
        assert "20 - 35" in med
        assert tan == "RARE_TAN_FREQUENT_BURN"

    def test_rr_lower_med_35_50(self):
        med, tan, _ = MC1RMathematicalFormulation.compute_uv_sensitivity("r/r")
        assert "35 - 50" in med
        assert tan == "MILD_TAN_OCCASIONAL_BURN"

    def test_r_wt_lower_med_35_50(self):
        med, tan, _ = MC1RMathematicalFormulation.compute_uv_sensitivity("r/wt")
        assert "35 - 50" in med
        assert tan == "MILD_TAN_OCCASIONAL_BURN"

    def test_wtwt_med_above_50(self):
        med, tan, _ = MC1RMathematicalFormulation.compute_uv_sensitivity("wt/wt")
        assert "> 50" in med
        assert tan == "NORMAL_TAN_RARE_BURN"


class TestFullPipelineFormulation:
    """Verifies combined end-to-end pipeline methods."""

    def test_run_mc1r_formulation_wildtype(self):
        res = MC1RMathematicalFormulation.run_mc1r_formulation({})
        assert res.diplotype == "wt/wt"
        assert res.functional_classification == "WILD_TYPE"
        assert res.total_mc1r_loss_weight == pytest.approx(0.0, abs=1e-9)
        assert res.max_possible_weight == pytest.approx(5.70, abs=0.01)

    def test_run_mc1r_formulation_r_hom(self):
        res = MC1RMathematicalFormulation.run_mc1r_formulation({"rs1805007": 2})
        assert res.diplotype == "R/R"
        assert res.r_high_risk_alleles_count == 2
        assert res.total_mc1r_loss_weight == pytest.approx(5.70, abs=1e-3)

    def test_run_freckling_formulation_wildtype(self):
        res = MC1RMathematicalFormulation.run_freckling_formulation({}, 0.0)
        assert res.freckling_score_pct == pytest.approx(7.59, abs=0.1)
        assert "MINIMAL" in res.freckling_intensity

    def test_run_uv_formulation_rr(self):
        res = MC1RMathematicalFormulation.run_uv_formulation("R/R")
        assert "< 20" in res.minimal_erythema_dose_category
        assert res.tanning_capacity == "NEVER_TANS_ALWAYS_BURNS"
