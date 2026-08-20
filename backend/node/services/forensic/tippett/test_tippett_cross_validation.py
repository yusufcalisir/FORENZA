"""
FORENZA Forensic Evidence Operating System
Pillar 1 — Module 1.5: Tippett Plot ROC Calibration & Misleading Evidence Lab
Sub-Item 1.5.3: Independent Tool Cross-Validation Unit Test Suite
"""

import pytest

try:
    from node.services.forensic.tippett.tippett_cross_validation import (
        TippettCrossValidationEngine,
        ToolCrossValidationResult,
        ENFSIReportResult,
        ENFSI_TIERS,
    )
except ImportError:
    from backend.node.services.forensic.tippett.tippett_cross_validation import (
        TippettCrossValidationEngine,
        ToolCrossValidationResult,
        ENFSIReportResult,
        ENFSI_TIERS,
    )


# ===========================================================================
# 1. Test Suite: Independent Tool Benchmarks Cross-Validation
# ===========================================================================

class TestIndependentToolCrossValidation:
    """Verifies concordance against independent external tools (FoCal, EuroForMix, STRmix)."""

    def test_focal_cllr_cross_validation(self):
        res = TippettCrossValidationEngine.cross_validate_focal_cllr()
        assert res.concordant is True
        assert res.discrepancy < 1e-5
        assert res.expected_value > 0.0

    def test_euroformix_separation_cross_validation(self):
        res = TippettCrossValidationEngine.cross_validate_euroformix_separation()
        assert res.concordant is True
        assert res.observed_value >= 0.9990

    def test_strmix_misleading_evidence_cross_validation(self):
        res = TippettCrossValidationEngine.cross_validate_strmix_misleading_evidence()
        assert res.concordant is True
        assert res.observed_value == 0.0


# ===========================================================================
# 2. Test Suite: ENFSI 2017 7-Tier Verbal Reporting Scale
# ===========================================================================

class TestENFSI7TierVerbalScale:
    """Tests standardized 7-tier evaluative reporting scale in English and Turkish."""

    @pytest.mark.parametrize(
        "log10_lr,expected_tier,tier_name_en,tier_name_tr",
        [
            (0.0, 0, "Inconclusive / Neutral", "Sonuçsuz / Nötr"),
            (0.5, 1, "Weak Support", "Zayıf Destek"),
            (1.5, 2, "Moderate Support", "Orta Derecede Destek"),
            (3.0, 3, "Moderately Strong Support", "Orta-Güçlü Destek"),
            (5.0, 4, "Strong Support", "Güçlü Destek"),
            (7.5, 5, "Very Strong Support", "Çok Güçlü Destek"),
            (12.0, 6, "Extremely Strong Support", "Son Derece Güçlü Destek"),
        ],
    )
    def test_enfsi_positive_tiers_en_and_tr(self, log10_lr, expected_tier, tier_name_en, tier_name_tr):
        res_en = TippettCrossValidationEngine.map_enfsi_verbal_scale(log10_lr, language="en")
        res_tr = TippettCrossValidationEngine.map_enfsi_verbal_scale(log10_lr, language="tr")

        assert res_en.tier_index == expected_tier
        assert res_en.tier_name == tier_name_en
        if expected_tier > 0:
            assert "prosecution" in res_en.verbal_statement.lower()
            assert "iddia" in res_tr.verbal_statement.lower()
        else:
            assert "uninformative" in res_en.verbal_statement.lower()
            assert "tarafsız" in res_tr.verbal_statement.lower()

        assert res_tr.tier_index == expected_tier
        assert res_tr.tier_name == tier_name_tr

    def test_enfsi_negative_lr_defense_support(self):
        res = TippettCrossValidationEngine.map_enfsi_verbal_scale(-4.5, language="en")
        assert res.tier_index == -4
        assert "Support for Defense" in res.tier_name
        assert "defense" in res.verbal_statement.lower()

        res_tr = TippettCrossValidationEngine.map_enfsi_verbal_scale(-4.5, language="tr")
        assert res_tr.tier_index == -4
        assert "Savunma Lehine" in res_tr.tier_name
        assert "savunma" in res_tr.verbal_statement.lower()


# ===========================================================================
# 3. Test Suite: Prosecutor's Fallacy Shield
# ===========================================================================

class TestProsecutorsFallacyShield:
    """Verifies detection of transposed conditional legal statements."""

    def test_compliant_evaluative_statement_passes(self):
        compliant = "The DNA profile is 10,000 times more likely if the suspect left the sample than if an unknown person did."
        audit = TippettCrossValidationEngine.audit_prosecutors_fallacy(compliant)
        assert audit["statement_valid"] is True
        assert audit["prosecutor_fallacy_detected"] is False
        assert len(audit["flagged_phrases"]) == 0

    def test_transposed_conditional_english_flagged(self):
        fallacious = "There is a 99.99% probability that the suspect left the DNA."
        audit = TippettCrossValidationEngine.audit_prosecutors_fallacy(fallacious)
        assert audit["statement_valid"] is False
        assert audit["prosecutor_fallacy_detected"] is True
        assert "probability that the suspect left the dna" in audit["flagged_phrases"]

    def test_transposed_conditional_turkish_flagged(self):
        fallacious_tr = "DNA'nın şüpheliye ait olma olasılığı yüzde 99.9'dur."
        audit = TippettCrossValidationEngine.audit_prosecutors_fallacy(fallacious_tr)
        assert audit["statement_valid"] is False
        assert audit["prosecutor_fallacy_detected"] is True
        assert "dna'nın şüpheliye ait olma olasılığı" in audit["flagged_phrases"]
