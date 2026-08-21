"""
Unit Test Suite for FORENZA HIrisPlex-S Cross-Validation Engine (Module 3.1).
Validates concordance against Erasmus MC HIrisPlex-S webtool and VISAGE standards.
"""

import pytest

from node.services.forensic.phenotyping.hirisplex_cross_validation import (
    HIrisPlexCrossValidationEngine,
)


class TestHIrisPlexCrossValidation:
    """Verifies external tool cross-validation concordance."""

    def test_erasmus_mc_irisplex_concordance(self):
        res = HIrisPlexCrossValidationEngine.cross_validate_erasmus_mc_irisplex()
        assert res.is_concordant is True
        assert res.absolute_residual < 0.05

    def test_red_hair_mc1r_concordance(self):
        res = HIrisPlexCrossValidationEngine.cross_validate_red_hair_mc1r()
        assert res.is_concordant is True
        assert res.computed_probability >= 0.88

    def test_visage_skin_phototype_concordance(self):
        res = HIrisPlexCrossValidationEngine.cross_validate_visage_skin_phototype()
        assert res.is_concordant is True
        assert res.computed_probability >= 0.90

    def test_visage_enfsi_reporting_shield(self):
        shield = HIrisPlexCrossValidationEngine.get_visage_enfsi_reporting_shield()
        assert shield["has_phenotype_disclaimer"] is True
        assert shield["prosecutors_fallacy_shield_active"] is True
        assert "VISAGE" in shield["disclaimer_text_en"]
        assert "VISAGE" in shield["disclaimer_text_tr"]
