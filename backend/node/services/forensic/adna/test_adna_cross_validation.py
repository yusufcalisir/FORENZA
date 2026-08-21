"""
Unit Test Suite for FORENZA Ancient DNA Cross-Validation Engine (Module 2.5).
Validates concordance against mapDamage 2.0, Columbus historical series, and ISFG (2021).
"""

import pytest

from node.services.forensic.adna.adna_cross_validation import (
    AdnaCrossValidationEngine,
)


class TestAdnaCrossValidation:
    """Verifies external tool cross-validation concordance."""

    def test_mapdamage_deamination_curve_concordance(self):
        res = AdnaCrossValidationEngine.cross_validate_mapdamage_deamination_curve()
        assert res.is_concordant is True
        assert res.relative_residual < 1e-4

    def test_columbus_fragmentation_concordance(self):
        res = AdnaCrossValidationEngine.cross_validate_columbus_fragmentation()
        assert res.is_concordant is True
        assert res.relative_residual < 0.01

    def test_contaminant_subtraction_concordance(self):
        res = AdnaCrossValidationEngine.cross_validate_contaminant_subtraction()
        assert res.is_concordant is True
        assert res.relative_residual < 1e-4

    def test_isfg_paleogenomics_shield(self):
        shield = AdnaCrossValidationEngine.get_isfg_paleogenomics_reporting_shield()
        assert shield["has_adna_disclaimer"] is True
        assert shield["prosecutors_fallacy_shield_active"] is True
        assert "ISFG" in shield["disclaimer_text_en"]
        assert "ISFG" in shield["disclaimer_text_tr"]
