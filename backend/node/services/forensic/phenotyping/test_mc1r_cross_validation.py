"""
Cross-Validation Tests for FORENZA MC1R Epistasis & UV Sensitivity (Module 3.5).

Verifies concordance with:
  - Sulem et al. (2007) — R-variant weight fidelity
  - Valverde (1995) / Sulem (2007) — Freckling formula checkpoints
  - Sulem et al. (2008) — ASIP/BNC2 epistatic modifier independence
  - 5 Certified Reference Standards
"""

import pytest

from backend.node.services.forensic.phenotyping.mc1r_cross_validation import MC1RCrossValidation


class TestCVMC1R01VariantWeightFidelity:
    """CV-MC1R-01: All R and r variant weights verified (Sulem 2007)."""

    def test_all_concordant(self):
        result = MC1RCrossValidation.validate_r_variant_weight_fidelity()
        assert result["all_concordant"] is True

    def test_eight_variants_checked(self):
        result = MC1RCrossValidation.validate_r_variant_weight_fidelity()
        assert len(result["results"]) == 8  # 5 R + 3 r

    def test_all_individual_weights_pass(self):
        result = MC1RCrossValidation.validate_r_variant_weight_fidelity()
        for r in result["results"]:
            assert r["passed"] is True, (
                f"{r['rsid']} ({r['name']}) weight failed: "
                f"expected={r['published_weight']}, computed={r['computed_weight']}, Δ={r['delta']}"
            )


class TestCVMC1R02FrecklingFormulaConcordance:
    """CV-MC1R-02: Freckling formula at key analytical checkpoints (Valverde 1995 / Sulem 2007)."""

    def test_all_concordant(self):
        result = MC1RCrossValidation.validate_freckling_formula_concordance()
        assert result["all_concordant"] is True

    def test_four_checkpoints(self):
        result = MC1RCrossValidation.validate_freckling_formula_concordance()
        assert len(result["formula_checkpoints"]) == 4

    def test_all_checkpoints_pass(self):
        result = MC1RCrossValidation.validate_freckling_formula_concordance()
        for cp in result["formula_checkpoints"]:
            assert cp["passed"] is True, (
                f"Checkpoint '{cp['checkpoint']}' failed: "
                f"analytical={cp['analytical_f_score']}, computed={cp['computed_f_score']}, "
                f"Δ={cp['delta_pct']}"
            )

    def test_constants_exact(self):
        result = MC1RCrossValidation.validate_freckling_formula_concordance()
        for c in result["constant_fidelity"]:
            assert c["passed"] is True, (
                f"Constant '{c['name']}' failed: computed={c['computed']}, expected={c['expected']}"
            )


class TestCVMC1R03ASIPBNCIndependence:
    """CV-MC1R-03: ASIP/BNC2 epistatic modifier independence (Sulem 2008)."""

    def test_all_concordant(self):
        result = MC1RCrossValidation.validate_asip_bnc2_independence()
        assert result["all_concordant"] is True

    def test_two_locus_deltas_correct(self):
        result = MC1RCrossValidation.validate_asip_bnc2_independence()
        for r in result["locus_results"]:
            assert r["passed"] is True, (
                f"{r['rsid']} ({r['gene']}) logit delta failed: "
                f"expected={r['expected_delta_logit']}, actual={r['actual_delta_logit']}"
            )

    def test_combined_asip2_bnc2_2_f_score(self):
        result = MC1RCrossValidation.validate_asip_bnc2_independence()
        combined = result["combined_asip2_bnc2_2"]
        assert combined["passed"] is True, (
            f"Combined ASIP=2 BNC2=2 F_score={combined['f_score']}, "
            f"expected={combined['expected_f_score']}, Δ={combined['delta_pct']}"
        )


class TestCVMC1R04ReferenceStandards:
    """CV-MC1R-04: All 5 certified reference standards concordant."""

    def test_all_concordant(self):
        result = MC1RCrossValidation.validate_reference_standards()
        assert result["all_concordant"] is True

    def test_five_standards_validated(self):
        result = MC1RCrossValidation.validate_reference_standards()
        assert result["standards_count"] == 5

    def test_each_standard_passes(self):
        result = MC1RCrossValidation.validate_reference_standards()
        for r in result["results"]:
            assert r["passed"] is True, (
                f"Standard {r['standard_id']} ({r['sample_name']}) failed: "
                f"dipl={r['diplotype_ok']}, w={r['w_mc1r_ok']}, "
                f"f_score={r['f_score_ok']}, med={r['med_ok']}, intensity={r['intensity_ok']}"
            )


class TestMC1RForensicReportingShield:
    """Verifies ENFSI evaluative reporting shield contents."""

    def test_shield_has_required_keys(self):
        shield = MC1RCrossValidation.get_forensic_reporting_shield()
        assert "prosecutors_fallacy_shield" in shield
        assert "enfsi_reporting_statement_en" in shield
        assert "enfsi_reporting_statement_tr" in shield
        assert "validation_status" in shield

    def test_validation_status_verified(self):
        shield = MC1RCrossValidation.get_forensic_reporting_shield()
        assert shield["validation_status"] == "VERIFIED"

    def test_shield_mentions_key_concepts(self):
        shield = MC1RCrossValidation.get_forensic_reporting_shield()
        text = shield["prosecutors_fallacy_shield"]
        assert "probabilistic" in text.lower()
        assert "MUST NOT" in text
        assert "MC1R" in text
