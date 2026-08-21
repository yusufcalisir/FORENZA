"""
Unit tests for Craniofacial Independent Tool Cross-Validation (Module 3.3).
"""

import pytest
from backend.node.services.forensic.phenotyping.cranio_cross_validation import (
    CraniofacialCrossValidation,
)


def test_cross_validate_procrustes_alignment():
    res = CraniofacialCrossValidation.cross_validate_procrustes_alignment(
        "NA12878_CEU_EUROPEAN", "NA19240_YRI_AFRICAN"
    )

    assert res["is_concordant"] is True
    assert res["cs1_residual"] < 1e-4
    assert res["cs2_residual"] < 1e-4
    assert res["det_residual"] < 1e-5
    assert res["rmsd_mm"] > 0.0


def test_evaluative_reporting_shield_contents():
    shield = CraniofacialCrossValidation.get_evaluative_reporting_shield()

    assert "ENFSI" in shield["legal_framework"]
    assert "PROSECUTOR'S FALLACY WARNING" in shield["prosecutors_fallacy_shield"]
    assert "ISO/IEC 17025:2017" in shield["validation_authority"]
