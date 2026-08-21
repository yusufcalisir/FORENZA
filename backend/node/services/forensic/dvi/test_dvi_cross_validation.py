"""
Unit Test Suite for FORENZA DVI Cross-Validation Engine (Module 2.4).
Validates concordance against Familias 3 DVI Module, Interpol DVI Standards, and ENFSI (2017).
"""

import pytest

from node.services.forensic.dvi.dvi_cross_validation import (
    DviCrossValidationEngine,
)


class TestDviCrossValidation:
    """Verifies external tool cross-validation concordance."""

    def test_vector_p2_03_concordance(self):
        res = DviCrossValidationEngine.cross_validate_vector_p2_03()
        assert res.is_concordant is True
        assert abs(res.computed_value - 2.6e11) < 1e5

    def test_bayesian_prior_updating_concordance(self):
        res = DviCrossValidationEngine.cross_validate_bayesian_prior_updating()
        assert res.is_concordant is True
        assert res.computed_value > 0.999999

    def test_interpol_reporting_shield(self):
        shield = DviCrossValidationEngine.get_interpol_dvi_reporting_shield()
        assert shield["has_dvi_disclaimer"] is True
        assert shield["prosecutors_fallacy_shield_active"] is True
        assert "Interpol" in shield["disclaimer_text_en"]
        assert "İnterpol" in shield["disclaimer_text_tr"]
