"""
Unit Tests for FORENZA BGA-55 Independent Tool Cross-Validation Engine (Module 3.2).
"""

import pytest
from node.services.forensic.phenotyping.bga_cross_validation import (
    BGACrossValidationEngine,
)


class TestBGACrossValidation:
    """Verifies concordance against FROG-kb, STRUCTURE 2.3.4, and reporting shields."""

    def test_frog_kb_eur_concordance(self):
        res = BGACrossValidationEngine.cross_validate_frog_kb_na12878_eur()
        assert res.is_concordant is True
        assert res.computed_proportion >= 0.95
        assert res.absolute_residual <= 0.05

    def test_structure_afr_concordance(self):
        res = BGACrossValidationEngine.cross_validate_structure_na19240_afr()
        assert res.is_concordant is True
        assert res.computed_proportion >= 0.98
        assert res.absolute_residual <= 0.02

    def test_structure_eas_concordance(self):
        res = BGACrossValidationEngine.cross_validate_structure_na18507_eas()
        assert res.is_concordant is True
        assert res.computed_proportion >= 0.95
        assert res.absolute_residual <= 0.05

    def test_bga_reporting_shield(self):
        shield = BGACrossValidationEngine.get_bga_reporting_shield()
        assert shield["has_bga_disclaimer"] is True
        assert shield["prosecutors_fallacy_shield_active"] is True
        assert "ENFSI" in shield["disclaimer_text_en"]
        assert "ENFSI" in shield["disclaimer_text_tr"]
