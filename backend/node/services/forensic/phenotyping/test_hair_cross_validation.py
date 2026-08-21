"""
Cross-Validation Tests for FORENZA Hair Morphology & Balding PRS (Module 3.4).

Verifies concordance with:
  - Medland et al. (2009) EDAR fiber area cross-check
  - Adhikari et al. (2016) TCHH/WNT10A curl additivity cross-check
  - Li et al. (2022) AGA PRS weight fidelity cross-check
"""

import pytest

from backend.node.services.forensic.phenotyping.hair_cross_validation import (
    HairCrossValidation,
)


class TestCVHair01EDARAreaConcordance:
    """CV-HAIR-01: EDAR Val370Ala fiber area cross-validation (Medland 2009)."""

    def test_all_concordant(self):
        result = HairCrossValidation.validate_edar_area_concordance()
        assert result["all_concordant"] is True

    def test_three_dosage_levels(self):
        result = HairCrossValidation.validate_edar_area_concordance()
        assert len(result["results"]) == 3

    def test_individual_results_pass(self):
        result = HairCrossValidation.validate_edar_area_concordance()
        for r in result["results"]:
            assert r["passed"] is True, (
                f"EDAR={r['edar_dosage']} area concordance failed: "
                f"computed={r['computed_area_um2']}, expected={r['expected_area_um2']}, Δ={r['delta_um2']}"
            )


class TestCVHair02CurlAdditivity:
    """CV-HAIR-02: TCHH/WNT10A/EDAR curl additivity (Adhikari 2016)."""

    def test_all_concordant(self):
        result = HairCrossValidation.validate_curl_independence_additivity()
        assert result["all_concordant"] is True

    def test_six_locus_delta_checks(self):
        result = HairCrossValidation.validate_curl_independence_additivity()
        assert len(result["results"]) == 6  # TCHH×2 + WNT10A×2 + EDAR×2

    def test_all_locus_deltas_below_tolerance(self):
        result = HairCrossValidation.validate_curl_independence_additivity()
        for r in result["results"]:
            assert r["passed"] is True, (
                f"{r['locus']} dose={r['dosage']} failed: "
                f"expected_delta={r['expected_delta']}, actual_delta={r['actual_delta']}, Δ_err={r['delta_error']}"
            )


class TestCVHair03PRSWeightFidelity:
    """CV-HAIR-03: PRS weight fidelity (Li et al. 2022 PLOS Genetics)."""

    def test_all_concordant(self):
        result = HairCrossValidation.validate_prs_weight_fidelity()
        assert result["all_concordant"] is True

    def test_four_locus_weights_correct(self):
        result = HairCrossValidation.validate_prs_weight_fidelity()
        for r in result["locus_results"]:
            assert r["passed"] is True, (
                f"{r['rsid']} ({r['gene']}) weight failed: "
                f"expected={r['published_weight']}, computed={r['computed_prs_het1']}, Δ={r['delta_w']}"
            )

    def test_max_prs_4_740(self):
        result = HairCrossValidation.validate_prs_weight_fidelity()
        assert result["max_prs_passed"] is True
        assert result["max_prs_computed"] == pytest.approx(4.740, abs=1e-6)

    def test_hamilton_norwood_thresholds_correct(self):
        result = HairCrossValidation.validate_prs_weight_fidelity()
        for t in result["hamilton_norwood_thresholds"]:
            assert t["passed"] is True, (
                f"HN threshold {t['threshold']} failed: "
                f"computed={t['computed']}, expected={t['expected']}"
            )


class TestCVHair04ReferenceStandards:
    """CV-HAIR-04: All 5 certified reference standards concordant."""

    def test_all_concordant(self):
        result = HairCrossValidation.validate_reference_standards()
        assert result["all_concordant"] is True

    def test_five_standards_validated(self):
        result = HairCrossValidation.validate_reference_standards()
        assert result["standards_count"] == 5

    def test_each_standard_passes(self):
        result = HairCrossValidation.validate_reference_standards()
        for r in result["results"]:
            assert r["passed"] is True, (
                f"Standard {r['standard_id']} ({r['sample_name']}) failed: "
                f"curl_ok={r['curl_index_ok']}, area_ok={r['fiber_area_ok']}, "
                f"prs_ok={r['prs_ok']}, grade_ok={r['grade_ok']}"
            )


class TestForensicReportingShield:
    """Verifies ENFSI (2017) evaluative reporting shield contents."""

    def test_shield_has_required_keys(self):
        shield = HairCrossValidation.get_forensic_reporting_shield()
        assert "prosecutors_fallacy_shield" in shield
        assert "enfsi_reporting_statement_en" in shield
        assert "enfsi_reporting_statement_tr" in shield
        assert "validation_status" in shield

    def test_validation_status_verified(self):
        shield = HairCrossValidation.get_forensic_reporting_shield()
        assert shield["validation_status"] == "VERIFIED"

    def test_shield_mentions_key_concepts(self):
        shield = HairCrossValidation.get_forensic_reporting_shield()
        text = shield["prosecutors_fallacy_shield"]
        assert "probabilistic" in text.lower()
        assert "Hamilton-Norwood" in text
        assert "MUST NOT" in text
