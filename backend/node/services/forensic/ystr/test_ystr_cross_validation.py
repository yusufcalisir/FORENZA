"""
Unit Test Suite for Y-STR 27-Locus (Yfiler Plus) Independent Tool Cross-Validation.
Sub-Item 2.1.3: Independent Tool Cross-Validation

Tests:
  - YHRD Clopper-Pearson 95% upper bound concordance (|delta| < 10^-6) across 10 configurations
  - Ballantyne & Kayser (2012) RM Y-STR mutation rate and differentiation power
  - ISFG (2020) patrilineal evaluative reporting disclaimer and Prosecutor's Fallacy shield
"""

import pytest

from node.services.forensic.ystr.ystr_cross_validation import (
    YStrCrossValidationEngine,
    YHRD_CANONICAL_TABLE,
    YhrdConcordanceCheckResult,
    RmDifferentiationPowerResult,
    IsfgReportingScaleCheckResult,
)


class TestYhrdOnlineEngineConcordance:
    """Verifies YHRD Clopper-Pearson 95% upper bound calculations against published tables."""

    def test_all_ten_yhrd_configurations_concordant(self):
        results = YStrCrossValidationEngine.validate_yhrd_concordance(tolerance=1e-6)
        assert len(results) == 10
        for r in results:
            assert r.is_concordant is True, (
                f"YHRD discordance for N={r.database_size_n}, k={r.observed_matches_k}: "
                f"computed={r.computed_upper_p}, expected={r.canonical_yhrd_upper_p}, delta={r.absolute_delta}"
            )
            assert r.absolute_delta < 1e-6

    def test_zero_match_upper_bound_n38500(self):
        results = { (r.database_size_n, r.observed_matches_k): r for r in YStrCrossValidationEngine.validate_yhrd_concordance() }
        r = results[(38500, 0)]
        assert abs(r.computed_upper_p - 7.7806180e-05) < 1e-8
        assert "1 in 12,852" in r.equivalent_ratio_str

    def test_zero_match_upper_bound_n385000(self):
        results = { (r.database_size_n, r.observed_matches_k): r for r in YStrCrossValidationEngine.validate_yhrd_concordance() }
        r = results[(385000, 0)]
        assert abs(r.computed_upper_p - 7.7810723e-06) < 1e-10
        assert "1 in 128,517" in r.equivalent_ratio_str

    def test_ten_matches_upper_bound_n38500(self):
        results = { (r.database_size_n, r.observed_matches_k): r for r in YStrCrossValidationEngine.validate_yhrd_concordance() }
        r = results[(38500, 10)]
        assert abs(r.computed_upper_p - 4.7761954e-04) < 1e-7


class TestRmYStrDifferentiationPower:
    """Verifies Ballantyne & Kayser (2012) Rapidly Mutating Y-STR differentiation model."""

    def test_rm_differentiation_statistics(self):
        res = YStrCrossValidationEngine.evaluate_rm_differentiation_power()
        assert res.n_total_loci == 25
        assert res.n_rm_loci == 6  # 6 systems (7 markers including DYF387S1a/b)
        assert res.n_standard_loci == 19

        # Father-son mutation probability across all 27 loci is ~13.8%
        assert 0.12 <= res.father_son_mut_prob_all_loci <= 0.16

        # Standard loci alone provide only ~4.6% mutation probability
        assert 0.03 <= res.father_son_mut_prob_standard_only <= 0.06

        # 7 RM loci alone provide ~9.7% mutation probability
        assert 0.08 <= res.father_son_mut_prob_rm_only <= 0.12

        # Grandfather-grandson (2 meioses) mutation probability is ~25.7%
        assert 0.22 <= res.grandfather_grandson_mut_prob <= 0.30

        # Differentiation boost factor is ~3.02x
        assert res.differentiation_boost_factor >= 2.8


class TestIsfgEvaluativeReportingShield:
    """Verifies ISFG (2020) patrilineal lineage reporting disclaimer and Prosecutor's Fallacy shield."""

    def test_patrilineal_disclaimer_present(self):
        shield = YStrCrossValidationEngine.get_isfg_patrilineal_disclaimer()
        assert shield.has_patrilineal_disclaimer is True
        assert shield.prosecutors_fallacy_shield_active is True
        assert "MANDATORY ISFG (2020) PATRILINEAL DISCLAIMER" in shield.disclaimer_text_en
        assert "patrilineally related male relatives" in shield.disclaimer_text_en
        assert "ZORUNLU ISFG (2020) BABA SOYU ADLİ UYARI BİLDİRİMİ" in shield.disclaimer_text_tr
        assert "aynı ortak baba soyunu paylaşan" in shield.disclaimer_text_tr
