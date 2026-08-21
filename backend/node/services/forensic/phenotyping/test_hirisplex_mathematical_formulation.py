"""
Unit Test Suite for FORENZA HIrisPlex-S Mathematical Formulation Engine (Module 3.1).
Validates MLR Softmax evaluation, Sum-to-One Simplex Invariant, Hair Shade, Hair Morphology,
and Missing SNP Uncertainty Scaling.
"""

import pytest
import math

from node.services.forensic.phenotyping.hirisplex_mathematical_formulation import (
    HIrisPlexMathematicalFormulation,
    EYE_COLOR_MODEL,
    HAIR_COLOR_MODEL,
    SKIN_PHOTOTYPE_MODEL,
)


class TestHIrisPlexFormulation:
    """Verifies pure mathematical operations of HIrisPlex-S."""

    def test_sum_to_one_simplex_invariant(self):
        # Test across various dosage permutations
        for val in [0.0, 1.0, 2.0]:
            dosages = {
                "rs12913832": val,
                "rs1800407": val,
                "rs1426654": val,
                "rs16891982": val,
                "rs1805007": val,
                "rs10424031": val,
            }
            eye_res = HIrisPlexMathematicalFormulation.predict_multinomial_trait(EYE_COLOR_MODEL, dosages)
            hair_res = HIrisPlexMathematicalFormulation.predict_multinomial_trait(HAIR_COLOR_MODEL, dosages)
            skin_res = HIrisPlexMathematicalFormulation.predict_multinomial_trait(SKIN_PHOTOTYPE_MODEL, dosages)

            assert abs(sum(eye_res.probabilities.values()) - 1.0) <= 1e-5
            assert abs(sum(hair_res.probabilities.values()) - 1.0) <= 1e-5
            assert abs(sum(skin_res.probabilities.values()) - 1.0) <= 1e-5
            assert eye_res.is_simplex_valid is True

    def test_hair_shade_prediction(self):
        # Homozygous light alleles: rs12913832: 2, rs16891982: 2
        light_dosages = {"rs12913832": 2.0, "rs16891982": 2.0}
        shade_res = HIrisPlexMathematicalFormulation.predict_hair_shade(light_dosages)
        assert shade_res["Light"] > shade_res["Dark"]
        assert abs((shade_res["Light"] + shade_res["Dark"]) - 1.0) <= 1e-4

    def test_hair_morphology_prediction(self):
        # East Asian EDAR 370Ala G/G
        asian_dosages = {"rs3827760": 2.0, "rs11803731": 0.0}
        morph_res = HIrisPlexMathematicalFormulation.predict_hair_morphology(asian_dosages)
        assert morph_res.predicted_class == "Straight"
        assert morph_res.probabilities["Straight"] > 0.85

        # African TCHH A/A
        african_dosages = {"rs3827760": 0.0, "rs11803731": 2.0}
        morph_african = HIrisPlexMathematicalFormulation.predict_hair_morphology(african_dosages)
        assert morph_african.predicted_class == "Curly_Coily"
        assert morph_african.probabilities["Curly_Coily"] > 0.70

    def test_missing_snp_imputation_and_penalty(self):
        # Profile with only 1 SNP provided
        partial_dosages = {"rs12913832": 2.0}
        res_imputed = HIrisPlexMathematicalFormulation.predict_multinomial_trait(
            EYE_COLOR_MODEL, partial_dosages, enable_imputation=True
        )
        assert res_imputed.imputed_loci_count == 5
        assert res_imputed.uncertainty_penalty_applied is True
        assert abs(sum(res_imputed.probabilities.values()) - 1.0) <= 1e-6

    def test_full_hirisplex_s_pipeline(self):
        dosages = {"rs12913832": 2.0, "rs16891982": 2.0, "rs1426654": 2.0}
        full_res = HIrisPlexMathematicalFormulation.predict_full_hirisplex_s(dosages)
        assert full_res.eye_color.predicted_class == "Blue"
        assert full_res.global_confidence_score > 0.50
        assert "ENFSI" in full_res.prosecutors_fallacy_shield
