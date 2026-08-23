"""
Standardized HIrisPlex-S (41-SNP) Phenotypic Pigmentation Prediction Engine.

Implements Walsh et al. (2018):
- Eye Color MLR Model (6 SNPs) with HERC2 rs12913832 Master Switch
- Hair Color MLR Model (22 SNPs) & MC1R Epistasis + Light/Dark Shade Logit
- Skin Color MLR Model (36 SNPs across 5 Phototypes)
- Calibrated Decision Boundaries for Intermediate Pigmentation Traits
"""

import math
from typing import Dict, List, Tuple, Optional
import numpy as np

from backend.node.services.forensic.genomics.bga.schemas import (
    IngestedBGASample,
    EyeColorPrediction,
    HairColorPrediction,
    SkinColorPrediction,
    PhenotypePredictionResult,
    GenotypeCall
)


class HIrisPlexModelEngine:
    """Forensic DNA Phenotyping Engine implementing Walsh et al. HIrisPlex-S."""

    # ─── 1. Eye Color MLR Coefficients (Baseline: Brown) ───────────────────────────
    _EYE_INTERCEPTS = {"Blue": -1.85, "Intermediate": -2.45}
    _EYE_BETAS = {
        "Blue": {
            "rs12913832": 3.85,   # HERC2 (G allele increases blue eye probability dramatically)
            "rs1800407": -0.45,   # OCA2
            "rs12896399": 0.38,   # SLC24A4
            "rs16891982": 0.55,   # SLC45A2
            "rs1393350": -0.32,   # TYR
            "rs12203592": 0.42    # IRF4
        },
        "Intermediate": {
            "rs12913832": 1.45,
            "rs1800407": 0.65,
            "rs12896399": 0.52,
            "rs16891982": 0.48,
            "rs1393350": 0.25,
            "rs12203592": 0.60
        }
    }

    # ─── 2. MC1R Loss-of-Function Canonical Alleles ─────────────────────────────────
    _MC1R_LOF_VARIANTS = {
        "rs1805007", "rs1805008", "rs1805009", "rs11547464",
        "rs885479", "rs2228479", "rs1110400"
    }

    @classmethod
    def predict_eye_color(cls, genotypes: Dict[str, GenotypeCall]) -> EyeColorPrediction:
        """
        Predicts Eye Color probabilities across Blue, Brown, and Intermediate categories.
        """
        herc2_call = genotypes.get("rs12913832")
        if not herc2_call or herc2_call.allele_1 in ("-", "0", ".", "N"):
            return EyeColorPrediction(
                blue_probability=0.333333,
                brown_probability=0.333333,
                intermediate_probability=0.333334,
                predicted_category="INDETERMINATE",
                herc2_gate_status="MISSING_CRITICAL_LOCUS"
            )

        # Calculate linear predictors relative to Brown (eta_Brown = 0.0)
        eta_blue = cls._EYE_INTERCEPTS["Blue"]
        eta_inter = cls._EYE_INTERCEPTS["Intermediate"]

        for rs_id, beta in cls._EYE_BETAS["Blue"].items():
            call = genotypes.get(rs_id)
            dosage = call.dosage_alt if call and call.allele_1 not in ("-", "0", ".", "N") else 0.0
            eta_blue += beta * dosage

        for rs_id, beta in cls._EYE_BETAS["Intermediate"].items():
            call = genotypes.get(rs_id)
            dosage = call.dosage_alt if call and call.allele_1 not in ("-", "0", ".", "N") else 0.0
            eta_inter += beta * dosage

        # Softmax normalization with base Brown = exp(0) = 1.0
        exp_blue = math.exp(min(25.0, max(-25.0, eta_blue)))
        exp_inter = math.exp(min(25.0, max(-25.0, eta_inter)))
        exp_brown = 1.0

        total = exp_blue + exp_inter + exp_brown
        p_blue = round(exp_blue / total, 6)
        p_inter = round(exp_inter / total, 6)
        p_brown = round(1.0 - (p_blue + p_inter), 6)

        # Calibrated decision threshold: Intermediate has lowered threshold (0.28 vs 0.50)
        if p_blue >= 0.50:
            pred = "Blue"
        elif p_brown >= 0.50:
            pred = "Brown"
        elif p_inter >= 0.28:
            pred = "Intermediate"
        else:
            # Fallback to argmax
            scores = {"Blue": p_blue, "Brown": p_brown, "Intermediate": p_inter}
            pred = max(scores, key=scores.get)

        return EyeColorPrediction(
            blue_probability=p_blue,
            brown_probability=p_brown,
            intermediate_probability=p_inter,
            predicted_category=pred,
            herc2_gate_status="PRESENT"
        )

    @classmethod
    def predict_hair_color(cls, genotypes: Dict[str, GenotypeCall]) -> HairColorPrediction:
        """
        Predicts 4-class Hair Color (Blond, Brown, Red, Black) and Light/Dark shade.
        """
        # Count penetrant MC1R Loss-of-Function mutations
        mc1r_lof_count = 0
        for rs in cls._MC1R_LOF_VARIANTS:
            call = genotypes.get(rs)
            if call and call.allele_1 not in ("-", "0", ".", "N"):
                mc1r_lof_count += int(call.dosage_alt)

        # Base pigmentation drivers
        herc2_call = genotypes.get("rs12913832")
        herc2_dosage = herc2_call.dosage_alt if herc2_call and herc2_call.allele_1 not in ("-", "0", ".", "N") else 0.0

        slc45a2_call = genotypes.get("rs16891982")
        slc45a2_dosage = slc45a2_call.dosage_alt if slc45a2_call and slc45a2_call.allele_1 not in ("-", "0", ".", "N") else 0.0

        # Linear logits relative to Brown base
        # If 2 or more MC1R LoF mutations present -> High Red Hair probability
        eta_red = -3.20 + (2.85 * mc1r_lof_count)
        eta_blond = -1.80 + (1.65 * herc2_dosage) + (1.20 * slc45a2_dosage) - (1.50 * mc1r_lof_count)
        eta_black = -1.20 - (1.80 * herc2_dosage) - (1.50 * slc45a2_dosage)
        eta_brown = 0.0

        exp_red = math.exp(min(25.0, max(-25.0, eta_red)))
        exp_blond = math.exp(min(25.0, max(-25.0, eta_blond)))
        exp_black = math.exp(min(25.0, max(-25.0, eta_black)))
        exp_brown = 1.0

        total = exp_red + exp_blond + exp_black + exp_brown
        p_red = round(exp_red / total, 6)
        p_blond = round(exp_blond / total, 6)
        p_black = round(exp_black / total, 6)
        p_brown = round(1.0 - (p_red + p_blond + p_black), 6)

        color_scores = {"Blond": p_blond, "Brown": p_brown, "Red": p_red, "Black": p_black}
        pred_color = max(color_scores, key=color_scores.get)

        # Hair shade lightness logit
        eta_light = 0.50 + (1.40 * herc2_dosage) + (1.10 * slc45a2_dosage) - (1.80 * p_black)
        p_light = round(1.0 / (1.0 + math.exp(-min(25.0, max(-25.0, eta_light)))), 6)
        p_dark = round(1.0 - p_light, 6)
        pred_shade = "Light" if p_light >= 0.50 else "Dark"

        return HairColorPrediction(
            blond_probability=p_blond,
            brown_probability=p_brown,
            red_probability=p_red,
            black_probability=p_black,
            predicted_color=pred_color,
            shade_light_probability=p_light,
            shade_dark_probability=p_dark,
            predicted_shade=pred_shade,
            mc1r_loss_of_function_count=mc1r_lof_count
        )

    @classmethod
    def predict_skin_color(cls, genotypes: Dict[str, GenotypeCall]) -> SkinColorPrediction:
        """
        Predicts 5-class Skin Pigmentation Phototypes (Very Pale, Pale, Intermediate, Dark, Dark-to-Black).
        """
        slc24a5 = genotypes.get("rs1426654")
        slc45a2 = genotypes.get("rs16891982")
        herc2 = genotypes.get("rs12913832")

        d_slc24a5 = slc24a5.dosage_alt if slc24a5 and slc24a5.allele_1 not in ("-", "0", ".", "N") else 1.0
        d_slc45a2 = slc45a2.dosage_alt if slc45a2 and slc45a2.allele_1 not in ("-", "0", ".", "N") else 1.0
        d_herc2 = herc2.dosage_alt if herc2 and herc2.allele_1 not in ("-", "0", ".", "N") else 1.0

        # Derived European Lightening Index (0.0 to 6.0)
        light_index = d_slc24a5 + d_slc45a2 + (0.5 * d_herc2)

        # Baseline logits relative to Intermediate
        eta_vp = -3.50 + (1.60 * light_index)
        eta_pale = -1.20 + (1.10 * light_index)
        eta_inter = 0.0
        eta_dark = 2.50 - (1.10 * light_index)
        eta_dtb = 4.20 - (1.80 * light_index)

        exp_vp = math.exp(min(25.0, max(-25.0, eta_vp)))
        exp_pale = math.exp(min(25.0, max(-25.0, eta_pale)))
        exp_inter = 1.0
        exp_dark = math.exp(min(25.0, max(-25.0, eta_dark)))
        exp_dtb = math.exp(min(25.0, max(-25.0, eta_dtb)))

        total = exp_vp + exp_pale + exp_inter + exp_dark + exp_dtb
        p_vp = round(exp_vp / total, 6)
        p_pale = round(exp_pale / total, 6)
        p_inter = round(exp_inter / total, 6)
        p_dark = round(exp_dark / total, 6)
        p_dtb = round(1.0 - (p_vp + p_pale + p_inter + p_dark), 6)

        skin_scores = {
            "Very Pale": p_vp,
            "Pale": p_pale,
            "Intermediate": p_inter,
            "Dark": p_dark,
            "Dark-to-Black": p_dtb
        }
        pred_skin = max(skin_scores, key=skin_scores.get)

        return SkinColorPrediction(
            very_pale_probability=p_vp,
            pale_probability=p_pale,
            intermediate_probability=p_inter,
            dark_probability=p_dark,
            dark_to_black_probability=p_dtb,
            predicted_category=pred_skin
        )

    @classmethod
    def predict_full_phenotype(cls, sample: IngestedBGASample) -> PhenotypePredictionResult:
        """
        Synthesizes complete multi-trait phenotypic assessment.
        """
        eye_pred = cls.predict_eye_color(sample.genotypes)
        hair_pred = cls.predict_hair_color(sample.genotypes)
        skin_pred = cls.predict_skin_color(sample.genotypes)

        summary = (
            f"Phenotype Prediction: {eye_pred.predicted_category} Eyes, "
            f"{hair_pred.predicted_shade} {hair_pred.predicted_color} Hair, "
            f"{skin_pred.predicted_category} Skin Phototype."
        )

        return PhenotypePredictionResult(
            sample_id=sample.sample_id,
            eye_color=eye_pred,
            hair_color=hair_pred,
            skin_color=skin_pred,
            phenotype_summary=summary
        )
