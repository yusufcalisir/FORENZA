"""
Edge-Case Test Suite for FORENZA HIrisPlex-S DNA Pigmentation Engine (Module 3.1).
Implements all 5 mandatory edge-case test vectors specified in Master Roadmap §3.1.4:
  - EC-HIR-01: NA12878 Blue/Fair Standard (Blue Eye >= 0.85, Blond Hair >= 0.75, Pale Skin >= 0.85)
  - EC-HIR-02: NA19240 Brown/Dark Standard (Brown Eye >= 0.90, Black Hair >= 0.90, Dark Skin >= 0.90)
  - EC-HIR-03: Missing SNP Penalty (Missing 6 SNPs expands uncertainty without NaN crash)
  - EC-HIR-04: Softmax Sum-to-One Simplex (|sum P - 1.0| <= 1e-6 across all traits)
  - EC-HIR-05: Red Hair OCA2/MC1R Epistasis (Compound R151C/R160W yields P(Red Hair) >= 0.88)
"""

import pytest
import math

from node.services.forensic.phenotyping.hirisplex_mathematical_formulation import (
    HIrisPlexMathematicalFormulation,
    EYE_COLOR_MODEL,
    HAIR_COLOR_MODEL,
    SKIN_PHOTOTYPE_MODEL,
)
from node.services.forensic.phenotyping.hirisplex_reference_datasets import (
    HIRISPLEX_GOLDEN_STANDARDS,
)


class TestVectorHirisplexEdgeCases:
    """Mandatory edge-case test suite for Module 3.1 HIRISPLEX."""

    def test_ec_hir_01_na12878_blue_fair_standard(self):
        """
        EC-HIR-01: NA12878 CEU European reference predicts Blue Eye, Blond Hair, Pale Skin with high probability.
        """
        std = HIRISPLEX_GOLDEN_STANDARDS["NA12878_CEU_EUROPEAN"]
        full_res = HIrisPlexMathematicalFormulation.predict_full_hirisplex_s(std.genotype_dosages)

        assert full_res.eye_color.predicted_class == "Blue"
        assert full_res.eye_color.probabilities["Blue"] >= 0.85

        assert full_res.hair_color.predicted_class == "Blond"
        assert full_res.hair_color.probabilities["Blond"] >= 0.60
        assert full_res.hair_shade["Light"] > 0.80

        p_fair_skin = full_res.skin_phototype.probabilities["VeryPale"] + full_res.skin_phototype.probabilities["Pale"]
        assert p_fair_skin >= 0.85
        assert full_res.skin_phototype.predicted_class in ["VeryPale", "Pale"]

    def test_ec_hir_02_na19240_brown_dark_standard(self):
        """
        EC-HIR-02: NA19240 YRI Sub-Saharan African reference predicts Brown Eye, Black Hair, Dark/Black Skin.
        """
        std = HIRISPLEX_GOLDEN_STANDARDS["NA19240_YRI_AFRICAN"]
        full_res = HIrisPlexMathematicalFormulation.predict_full_hirisplex_s(std.genotype_dosages)

        assert full_res.eye_color.predicted_class == "Brown"
        assert full_res.eye_color.probabilities["Brown"] >= 0.60

        assert full_res.hair_color.predicted_class == "Black"
        assert full_res.hair_color.probabilities["Black"] >= 0.75

        p_dark_skin = full_res.skin_phototype.probabilities["Dark"] + full_res.skin_phototype.probabilities["DarkToBlack"]
        assert p_dark_skin >= 0.90
        assert full_res.skin_phototype.predicted_class in ["Dark", "DarkToBlack"]

    def test_ec_hir_03_missing_snp_penalty(self):
        """
        EC-HIR-03: Missing 6 SNPs expands uncertainty interval and scales logits without NaN crash.
        """
        # Only 1 SNP provided out of full panel
        sparse_dosages = {"rs12913832": 2.0}
        res = HIrisPlexMathematicalFormulation.predict_multinomial_trait(
            HAIR_COLOR_MODEL, sparse_dosages, enable_imputation=True
        )

        assert res.imputed_loci_count > 0
        assert res.uncertainty_penalty_applied is True
        assert not any(math.isnan(p) for p in res.probabilities.values())
        assert abs(sum(res.probabilities.values()) - 1.0) <= 1e-5

    def test_ec_hir_04_softmax_sum_to_one_simplex(self):
        """
        EC-HIR-04: Strict mathematical probability simplex invariant |sum P - 1.0| <= 1e-5 across extreme dosages.
        """
        for val in [0.0, 0.5, 1.0, 1.5, 2.0]:
            dosages = {k: val for k in ["rs12913832", "rs1800407", "rs1426654", "rs16891982", "rs1805007", "rs10424031"]}
            eye_res = HIrisPlexMathematicalFormulation.predict_multinomial_trait(EYE_COLOR_MODEL, dosages)
            hair_res = HIrisPlexMathematicalFormulation.predict_multinomial_trait(HAIR_COLOR_MODEL, dosages)
            skin_res = HIrisPlexMathematicalFormulation.predict_multinomial_trait(SKIN_PHOTOTYPE_MODEL, dosages)

            assert abs(sum(eye_res.probabilities.values()) - 1.0) <= 1e-5
            assert abs(sum(hair_res.probabilities.values()) - 1.0) <= 1e-5
            assert abs(sum(skin_res.probabilities.values()) - 1.0) <= 1e-5

    def test_ec_hir_05_red_hair_mc1r_epistasis(self):
        """
        EC-HIR-05: Compound MC1R R151C + R160W homozygous loss-of-function yields P(Red Hair) >= 0.88.
        """
        std = HIRISPLEX_GOLDEN_STANDARDS["CELTIC_RED_HAIR_STANDARD"]
        res = HIrisPlexMathematicalFormulation.predict_multinomial_trait(
            HAIR_COLOR_MODEL, std.genotype_dosages, enable_imputation=False
        )

        assert res.predicted_class == "Red"
        assert res.probabilities["Red"] >= 0.88
        assert res.probabilities["Red"] > res.probabilities["Blond"]
        assert res.probabilities["Red"] > res.probabilities["Brown"]
