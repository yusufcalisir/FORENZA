"""
Unit Test Suite for FORENZA HIrisPlex-S Reference Standards & Casework Cohorts (Module 3.1).
Validates certified reference standards NA12878, NA19240, Celtic Red Hair, NA18507, and HG002.
"""

import pytest

from node.services.forensic.phenotyping.hirisplex_reference_datasets import (
    HIrisPlexReferenceDatasets,
    HIRISPLEX_GOLDEN_STANDARDS,
)
from node.services.forensic.phenotyping.hirisplex_mathematical_formulation import (
    HIrisPlexMathematicalFormulation,
    EYE_COLOR_MODEL,
    HAIR_COLOR_MODEL,
    SKIN_PHOTOTYPE_MODEL,
)


class TestHIrisPlexReferenceDatasets:
    """Verifies certified multi-omic pigmentation reference standards."""

    def test_five_standards_registered(self):
        assert len(HIRISPLEX_GOLDEN_STANDARDS) == 5
        stds = HIrisPlexReferenceDatasets.list_standards()
        assert len(stds) == 5

    def test_na12878_fair_standard(self):
        std = HIRISPLEX_GOLDEN_STANDARDS["NA12878_CEU_EUROPEAN"]
        eye_res = HIrisPlexMathematicalFormulation.predict_multinomial_trait(
            EYE_COLOR_MODEL, std.genotype_dosages, enable_imputation=False
        )
        assert eye_res.predicted_class == std.expected_eye_class
        assert eye_res.confidence >= std.min_eye_confidence

    def test_na19240_dark_standard(self):
        std = HIRISPLEX_GOLDEN_STANDARDS["NA19240_YRI_AFRICAN"]
        eye_res = HIrisPlexMathematicalFormulation.predict_multinomial_trait(
            EYE_COLOR_MODEL, std.genotype_dosages, enable_imputation=False
        )
        assert eye_res.predicted_class == "Brown"
        assert eye_res.confidence >= std.min_eye_confidence

        hair_res = HIrisPlexMathematicalFormulation.predict_multinomial_trait(
            HAIR_COLOR_MODEL, std.genotype_dosages, enable_imputation=False
        )
        assert hair_res.predicted_class == "Black"

    def test_celtic_red_hair_standard(self):
        std = HIRISPLEX_GOLDEN_STANDARDS["CELTIC_RED_HAIR_STANDARD"]
        hair_res = HIrisPlexMathematicalFormulation.predict_multinomial_trait(
            HAIR_COLOR_MODEL, std.genotype_dosages, enable_imputation=False
        )
        assert hair_res.predicted_class == "Red"
        assert hair_res.confidence >= std.min_hair_confidence
