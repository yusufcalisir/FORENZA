"""
Unit Test Suite for FORENZA mtDNA Cross-Validation Engine (Module 2.3).
Validates concordance against EMPOP SAM 2, HaploSearch, and ISFG guidelines.
"""

import pytest

from node.services.forensic.mtdna.mtdna_cross_validation import (
    MtDnaCrossValidationEngine,
)


class TestMtDnaCrossValidation:
    """Verifies external tool cross-validation concordance."""

    def test_lineage_a_concordance(self):
        res = MtDnaCrossValidationEngine.cross_validate_lineage_a()
        assert res.is_concordant is True
        assert res.computed_value > 25.0

    def test_lineage_b_concordance(self):
        res = MtDnaCrossValidationEngine.cross_validate_lineage_b()
        assert res.is_concordant is True
        assert res.computed_value > 1500.0

    def test_empop_k0_bound_concordance(self):
        res = MtDnaCrossValidationEngine.cross_validate_empop_k0_bound()
        assert res.is_concordant is True
        assert res.relative_residual < 1e-4

    def test_isfg_reporting_shield(self):
        shield = MtDnaCrossValidationEngine.get_isfg_mtdna_reporting_shield()
        assert shield["has_matrilineal_disclaimer"] is True
        assert shield["prosecutors_fallacy_shield_active"] is True
        assert "ISFG" in shield["disclaimer_text_en"]
        assert "ISFG" in shield["disclaimer_text_tr"]
