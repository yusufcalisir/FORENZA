"""
Reference Dataset Tests for FORENZA MC1R Epistasis & UV Sensitivity (Module 3.5).

Tests all 5 certified reference standards against expected outputs.
"""

import pytest

from backend.node.services.forensic.phenotyping.mc1r_mathematical_formulation import (
    MC1RMathematicalFormulation,
)
from backend.node.services.forensic.phenotyping.mc1r_reference_datasets import FRECKLING_STANDARDS


class TestMC1RStandardsRegistry:
    """Verifies registry completeness."""

    def test_five_standards_registered(self):
        assert len(FRECKLING_STANDARDS) == 5

    def test_all_required_keys_present(self):
        required = {
            "WT_BASELINE",
            "R151C_HOM_RED",
            "R151C_V60L_COMPOUND",
            "V60L_HOM_MILD",
            "ASIP_BNC2_EPISTATIC",
        }
        assert set(FRECKLING_STANDARDS.keys()) == required

    def test_standard_ids_unique(self):
        ids = [s.standard_id for s in FRECKLING_STANDARDS.values()]
        assert len(ids) == len(set(ids))


class TestStd01WildTypeBaseline:
    """STD-MC1R-01: Wild-type baseline — VECTOR_15_FRECKLE_A."""

    def test_diplotype_wildtype(self):
        std = FRECKLING_STANDARDS["WT_BASELINE"]
        res = MC1RMathematicalFormulation.run_mc1r_formulation(std.snp_dosages)
        assert res.diplotype == "wt/wt"
        assert res.functional_classification == "WILD_TYPE"

    def test_w_zero(self):
        std = FRECKLING_STANDARDS["WT_BASELINE"]
        res = MC1RMathematicalFormulation.run_mc1r_formulation(std.snp_dosages)
        assert res.total_mc1r_loss_weight == pytest.approx(0.0, abs=1e-9)

    def test_f_score_7_59(self):
        std = FRECKLING_STANDARDS["WT_BASELINE"]
        mc1r = MC1RMathematicalFormulation.run_mc1r_formulation(std.snp_dosages)
        freckle = MC1RMathematicalFormulation.run_freckling_formulation(std.snp_dosages, mc1r.total_mc1r_loss_weight)
        assert freckle.freckling_score_pct == pytest.approx(7.59, abs=0.1)

    def test_med_above_50(self):
        std = FRECKLING_STANDARDS["WT_BASELINE"]
        mc1r = MC1RMathematicalFormulation.run_mc1r_formulation(std.snp_dosages)
        uv = MC1RMathematicalFormulation.run_uv_formulation(mc1r.diplotype)
        assert "> 50" in uv.minimal_erythema_dose_category
        assert uv.tanning_capacity == "NORMAL_TAN_RARE_BURN"


class TestStd02R151CHom:
    """STD-MC1R-02: R151C homozygous red hair — VECTOR_15_FRECKLE_B."""

    def test_diplotype_rr(self):
        std = FRECKLING_STANDARDS["R151C_HOM_RED"]
        res = MC1RMathematicalFormulation.run_mc1r_formulation(std.snp_dosages)
        assert res.diplotype == "R/R"
        assert res.functional_classification == "SEVERE_LOSS"

    def test_w_5_70(self):
        std = FRECKLING_STANDARDS["R151C_HOM_RED"]
        res = MC1RMathematicalFormulation.run_mc1r_formulation(std.snp_dosages)
        assert res.total_mc1r_loss_weight == pytest.approx(5.70, abs=1e-3)

    def test_f_score_above_99(self):
        std = FRECKLING_STANDARDS["R151C_HOM_RED"]
        mc1r = MC1RMathematicalFormulation.run_mc1r_formulation(std.snp_dosages)
        freckle = MC1RMathematicalFormulation.run_freckling_formulation(std.snp_dosages, mc1r.total_mc1r_loss_weight)
        assert freckle.freckling_score_pct >= 99.0

    def test_med_below_20(self):
        std = FRECKLING_STANDARDS["R151C_HOM_RED"]
        mc1r = MC1RMathematicalFormulation.run_mc1r_formulation(std.snp_dosages)
        uv = MC1RMathematicalFormulation.run_uv_formulation(mc1r.diplotype)
        assert "< 20" in uv.minimal_erythema_dose_category
        assert uv.tanning_capacity == "NEVER_TANS_ALWAYS_BURNS"


class TestStd03CompoundHet:
    """STD-MC1R-03: R151C + V60L compound het — VECTOR_15_FRECKLE_C."""

    def test_diplotype_r_r(self):
        std = FRECKLING_STANDARDS["R151C_V60L_COMPOUND"]
        res = MC1RMathematicalFormulation.run_mc1r_formulation(std.snp_dosages)
        assert res.diplotype == "R/r"
        assert res.functional_classification == "MODERATE_LOSS"

    def test_w_3_95(self):
        std = FRECKLING_STANDARDS["R151C_V60L_COMPOUND"]
        res = MC1RMathematicalFormulation.run_mc1r_formulation(std.snp_dosages)
        assert res.total_mc1r_loss_weight == pytest.approx(3.95, abs=1e-3)

    def test_f_score_94_44(self):
        std = FRECKLING_STANDARDS["R151C_V60L_COMPOUND"]
        mc1r = MC1RMathematicalFormulation.run_mc1r_formulation(std.snp_dosages)
        freckle = MC1RMathematicalFormulation.run_freckling_formulation(std.snp_dosages, mc1r.total_mc1r_loss_weight)
        assert freckle.freckling_score_pct == pytest.approx(94.44, abs=0.2)

    def test_med_20_35(self):
        std = FRECKLING_STANDARDS["R151C_V60L_COMPOUND"]
        mc1r = MC1RMathematicalFormulation.run_mc1r_formulation(std.snp_dosages)
        uv = MC1RMathematicalFormulation.run_uv_formulation(mc1r.diplotype)
        assert "20 - 35" in uv.minimal_erythema_dose_category


class TestStd04V60LHom:
    """STD-MC1R-04: V60L homozygous (r/r) — VECTOR_15_FRECKLE_D."""

    def test_diplotype_rr_lower(self):
        std = FRECKLING_STANDARDS["V60L_HOM_MILD"]
        res = MC1RMathematicalFormulation.run_mc1r_formulation(std.snp_dosages)
        assert res.diplotype == "r/r"
        assert res.functional_classification == "MILD_LOSS"

    def test_w_2_20(self):
        std = FRECKLING_STANDARDS["V60L_HOM_MILD"]
        res = MC1RMathematicalFormulation.run_mc1r_formulation(std.snp_dosages)
        assert res.total_mc1r_loss_weight == pytest.approx(2.20, abs=1e-3)

    def test_f_score_61_54(self):
        std = FRECKLING_STANDARDS["V60L_HOM_MILD"]
        mc1r = MC1RMathematicalFormulation.run_mc1r_formulation(std.snp_dosages)
        freckle = MC1RMathematicalFormulation.run_freckling_formulation(std.snp_dosages, mc1r.total_mc1r_loss_weight)
        assert freckle.freckling_score_pct == pytest.approx(61.54, abs=0.2)


class TestStd05ASIPBNCEpistatic:
    """STD-MC1R-05: ASIP+BNC2 pure epistatic boost — VECTOR_15_FRECKLE_F."""

    def test_diplotype_still_wildtype(self):
        std = FRECKLING_STANDARDS["ASIP_BNC2_EPISTATIC"]
        res = MC1RMathematicalFormulation.run_mc1r_formulation(std.snp_dosages)
        assert res.diplotype == "wt/wt"
        assert res.total_mc1r_loss_weight == pytest.approx(0.0, abs=1e-9)

    def test_f_score_62_25(self):
        std = FRECKLING_STANDARDS["ASIP_BNC2_EPISTATIC"]
        mc1r = MC1RMathematicalFormulation.run_mc1r_formulation(std.snp_dosages)
        freckle = MC1RMathematicalFormulation.run_freckling_formulation(std.snp_dosages, mc1r.total_mc1r_loss_weight)
        assert freckle.freckling_score_pct == pytest.approx(62.25, abs=0.1)

    def test_med_still_above_50(self):
        """wt/wt diplotype must still yield MED > 50 mJ/cm² regardless of modifier loci."""
        std = FRECKLING_STANDARDS["ASIP_BNC2_EPISTATIC"]
        mc1r = MC1RMathematicalFormulation.run_mc1r_formulation(std.snp_dosages)
        uv = MC1RMathematicalFormulation.run_uv_formulation(mc1r.diplotype)
        assert "> 50" in uv.minimal_erythema_dose_category
