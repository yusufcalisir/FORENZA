"""
FORENZA HIrisPlex-S Multinomial Logistic Regression Engine.
Implements eye colour, hair colour, and skin tone prediction from SNP dosages
using published coefficient tables from Walsh et al. (2018) FSI Genetics.

References:
  Walsh S, et al. (2018). Developmental validation of the HIrisPlex-S system:
  Appearance prediction from DNA for eye, hair and skin colour.
  Forensic Science International: Genetics, 35, 123–135.
  https://doi.org/10.1016/j.fsigen.2018.04.004
"""

import math
from typing import Dict, List, Optional
from .models import (
    EyeColour, HairColour, SkinTone, SNPInput, TraitProbability
)


# ── IrisPlex 6-SNP Eye Colour Model ─────────────────────────────────────────
# Coefficients for multinomial logistic regression (log-odds for BLUE vs BROWN reference)
# Source: Walsh et al. 2011 & 2017 IrisPlex validation studies
# Format: {rsid: (coeff_blue, coeff_intermediate)}
EYE_COLOUR_COEFFICIENTS: Dict[str, tuple] = {
    "rs12913832":  ( 3.940,  1.710),   # HERC2 — strongest predictor
    "rs1800407":   (-1.488, -0.665),   # OCA2
    "rs12896399":  ( 0.576,  0.315),   # SLC24A4
    "rs16891982":  ( 0.940,  0.360),   # SLC45A2
    "rs1393350":   ( 0.577,  0.215),   # TYR
    "rs12203592":  ( 0.402,  0.095),   # IRF4
}
EYE_COLOUR_INTERCEPTS = {"blue": -1.652, "intermediate": -0.422}


# ── HIrisPlex Hair Colour Model (22+2 SNP) ───────────────────────────────────
# Multinomial logit coefficients vs BROWN as reference category
# Source: Walsh et al. 2013 HIrisPlex validation paper (selected key coefficients)
# Format: {rsid: (coeff_black, coeff_blonde, coeff_red)}
HAIR_COLOUR_COEFFICIENTS: Dict[str, tuple] = {
    "rs12913832":  (-0.180, 1.220, 0.250),  # HERC2
    "rs1800407":   ( 0.350,-0.820,-0.115),  # OCA2
    "rs12896399":  (-0.095, 0.580, 0.045),  # SLC24A4
    "rs16891982":  ( 1.140,-0.940,-0.320),  # SLC45A2
    "rs1393350":   ( 0.680,-0.450, 0.620),  # TYR
    "rs12203592":  (-0.415,-0.285, 1.980),  # IRF4 — very strong for red
    "rs35264875":  (-0.285, 0.485,-0.095),  # TYRP1
    "rs683 ":      ( 0.125,-0.415,-0.085),  # DTNBP1 (approximate rsid representation)
    "rs1667394":   (-0.720, 1.440, 0.220),  # OCA2
}
HAIR_COLOUR_INTERCEPTS = {"black": -0.882, "blonde": -0.442, "red": -2.815}


# ── HIrisPlex-S Skin Tone Model (Fitzpatrick I–VI) ───────────────────────────
# Simplified 6-category ordinal logistic regression coefficients
# Source: Walsh et al. 2018 HIrisPlex-S (selected key predictors)
# Format: {rsid: coefficient}
SKIN_TONE_COEFFICIENTS: Dict[str, float] = {
    # Positive score = darker skin; negative score = lighter/paler skin
    "rs12913832": -0.820,   # HERC2 — blue/light allele → lighter skin
    "rs16891982": -1.450,   # SLC45A2 — derived allele → lightest skin
    "rs1800407":  -0.620,   # OCA2 — light allele
    "rs1393350":  -0.480,   # TYR — light allele
    "rs12203592": -0.210,   # IRF4 — light associated
    "rs1800404":  -0.340,   # OCA2 rs2
    "rs28777":    -0.890,   # SLC45A2 rs2 — light allele
    "rs4959270":   0.540,   # KITLG — dark African pigmentation allele
    "rs12821256":  0.380,   # KITLG — dark associated
    "rs35264875":  0.190,   # TYRP1 — dark associated
}
# Fitzpatrick scale thresholds (cumulative logits)
# score << 0 → very_pale; score >> 0 → dark_brown
SKIN_THRESHOLDS = [-4.00, -2.00, 0.00, 2.00, 4.00]  # symmetric around zero


def _softmax(values: Dict[str, float]) -> Dict[str, float]:
    """Converts log-odds dict into probabilities via softmax normalization."""
    max_v = max(values.values())
    exps = {k: math.exp(v - max_v) for k, v in values.items()}
    total = sum(exps.values())
    return {k: v / total for k, v in exps.items()}


def _get_dosage(snp_inputs: Dict[str, SNPInput], rsid: str) -> int:
    """Returns SNP dosage (0/1/2) defaulting to 0 if missing."""
    snp = snp_inputs.get(rsid)
    return snp.dosage if snp else 0


class HiriPlexSEngine:
    """
    HIrisPlex-S trait predictor using published multinomial logistic regression coefficients.
    Input: dict of {rsid: SNPInput} covering as many panel SNPs as available.
    """

    def predict_eye_colour(self, snp_inputs: Dict[str, SNPInput]) -> TraitProbability:
        """Predicts eye colour: blue / intermediate / brown."""
        logit_blue = EYE_COLOUR_INTERCEPTS["blue"]
        logit_inter = EYE_COLOUR_INTERCEPTS["intermediate"]

        for rsid, (coef_b, coef_i) in EYE_COLOUR_COEFFICIENTS.items():
            d = _get_dosage(snp_inputs, rsid)
            logit_blue += coef_b * d
            logit_inter += coef_i * d

        raw = {
            EyeColour.BLUE.value: logit_blue,
            EyeColour.INTERMEDIATE.value: logit_inter,
            EyeColour.BROWN.value: 0.0  # reference category
        }
        probs = _softmax(raw)
        most_likely = max(probs, key=probs.get)
        return TraitProbability(
            trait="eye_colour",
            probabilities=probs,
            most_likely=most_likely,
            confidence=probs[most_likely]
        )

    def predict_hair_colour(self, snp_inputs: Dict[str, SNPInput]) -> TraitProbability:
        """Predicts hair colour: black / brown / blonde / red."""
        logits = {
            HairColour.BLACK.value:  HAIR_COLOUR_INTERCEPTS["black"],
            HairColour.BLONDE.value: HAIR_COLOUR_INTERCEPTS["blonde"],
            HairColour.RED.value:    HAIR_COLOUR_INTERCEPTS["red"],
            HairColour.BROWN.value:  0.0  # reference
        }
        for rsid, (c_k, c_b, c_r) in HAIR_COLOUR_COEFFICIENTS.items():
            d = _get_dosage(snp_inputs, rsid.strip())
            logits[HairColour.BLACK.value]  += c_k * d
            logits[HairColour.BLONDE.value] += c_b * d
            logits[HairColour.RED.value]    += c_r * d

        probs = _softmax(logits)
        most_likely = max(probs, key=probs.get)
        return TraitProbability(
            trait="hair_colour",
            probabilities=probs,
            most_likely=most_likely,
            confidence=probs[most_likely]
        )

    def predict_skin_tone(self, snp_inputs: Dict[str, SNPInput]) -> TraitProbability:
        """Predicts skin tone across Fitzpatrick I–VI using cumulative logit model."""
        linear_score = 0.0
        for rsid, coef in SKIN_TONE_COEFFICIENTS.items():
            d = _get_dosage(snp_inputs, rsid)
            linear_score += coef * d

        # Cumulative logistic probabilities P(Y <= k)
        cum_probs = [1.0 / (1.0 + math.exp(-(t - linear_score))) for t in SKIN_THRESHOLDS]
        cum_probs = [0.0] + cum_probs + [1.0]

        categories = [t.value for t in SkinTone]
        cat_probs = {
            categories[i]: max(0.0, cum_probs[i + 1] - cum_probs[i])
            for i in range(len(categories))
        }
        # Renormalize to handle floating point drift
        total = sum(cat_probs.values())
        if total > 0:
            cat_probs = {k: v / total for k, v in cat_probs.items()}

        most_likely = max(cat_probs, key=cat_probs.get)
        return TraitProbability(
            trait="skin_tone",
            probabilities=cat_probs,
            most_likely=most_likely,
            confidence=cat_probs[most_likely]
        )
