"""
Unit Tests for FORENZA X-STR Cross-Validation Engine (Module 2.2).
Validates concordance against Familias 3, VECTOR_P2_02, and ISFG guidelines.
"""

import pytest

from node.services.forensic.xstr.xstr_cross_validation import (
    XStrCrossValidationEngine,
)


class TestXStrCrossValidation:
    """Verifies cross-validation tests."""

    def test_vector_p2_02_concordance(self):
        res = XStrCrossValidationEngine.cross_validate_vector_p2_02()
        assert res.is_concordant is True
        assert res.computed_ki > 100000.0
        assert "VECTOR_P2_02" in res.benchmark_name

    def test_familias3_single_locus_recombination_concordance(self):
        res = XStrCrossValidationEngine.cross_validate_familias3_linkage_formula()
        assert res.is_concordant is True
        assert abs(res.computed_ki - 4.92) < 1e-4

    def test_isfg_reporting_shield_content(self):
        shield = XStrCrossValidationEngine.get_isfg_xstr_reporting_shield()
        assert shield["has_patrilineal_disclaimer"] is True
        assert shield["prosecutors_fallacy_shield_active"] is True
        assert "ISFG" in shield["disclaimer_text_en"]
        assert "ISFG" in shield["disclaimer_text_tr"]
