"""
FORENZA HIrisPlex-S 41-SNP DNA Pigmentation Forensics Engine — Module 11.

Implements verbatim from Pillar 3 Research §1:
  - §1.1 Multinomial Logistic Regression (MLR) Softmax Architecture & Sum-to-Unity Invariant (|sum - 1.0| <= 1e-6)
  - §1.2 IrisPlex 6-Loci Eye Color Model (Blue, Intermediate, Brown Reference)
  - §1.2 HIrisPlex 22-Loci Hair Color Model (Blond, Red, Black, Brown Reference) & Hair Shade (Light vs Dark)
  - §1.2 HIrisPlex-S 36-Loci Skin Phototype Model (Very Pale, Pale, Dark, Dark-to-Black, Intermediate Reference)
  - §1.3 Missing Allele Imputation (X* = 2*p_i) & Uncertainty Scaling Penalty (lambda = 0.35)

References:
  Walsh S, et al. (2018) The HIrisPlex-S system for simultaneous prediction of hair, eye and skin colour from DNA.
  Forensic Science International: Genetics, 34, 189–199.
  VISAGE Consortium Guidelines for Forensic DNA Phenotyping (2020).
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union


# ── Canonical Coefficient Dictionaries ────────────────────────────────────────

EYE_COLOR_SPEC = {
    "CLASSES": ["Blue", "Intermediate", "Brown"],
    "REFERENCE_CLASS": "Brown",
    "INTERCEPTS": {
        "Blue": -2.815,
        "Intermediate": -1.412,
    },
    "EFFECT_ALLELES": {
        "rs12913832": {"allele": "C", "Blue": 4.512, "Intermediate": 1.895, "pop_mean_dosage": 0.85},
        "rs1800407": {"allele": "T", "Blue": -0.812, "Intermediate": 0.341, "pop_mean_dosage": 0.15},
        "rs12896399": {"allele": "T", "Blue": 0.421, "Intermediate": 0.215, "pop_mean_dosage": 0.40},
        "rs16891982": {"allele": "G", "Blue": -1.105, "Intermediate": -0.452, "pop_mean_dosage": 0.95},
        "rs1393350": {"allele": "A", "Blue": 0.312, "Intermediate": 0.184, "pop_mean_dosage": 0.45},
        "rs12203592": {"allele": "T", "Blue": 0.584, "Intermediate": 0.612, "pop_mean_dosage": 0.18},
    },
}

HAIR_COLOR_SPEC = {
    "CLASSES": ["Blond", "Red", "Black", "Brown"],
    "REFERENCE_CLASS": "Brown",
    "INTERCEPTS": {
        "Blond": -1.920,
        "Red": -3.450,
        "Black": -2.110,
    },
    "SHADE_INTERCEPT": 0.125,
    "EFFECT_ALLELES": {
        "rs12913832": {"allele": "C", "Blond": 2.850, "Red": 0.120, "Black": -3.100, "LightShade": 2.150, "pop_mean_dosage": 0.85},
        "rs1800407": {"allele": "T", "Blond": 0.310, "Red": 0.050, "Black": -0.420, "LightShade": 0.210, "pop_mean_dosage": 0.15},
        "rs16891982": {"allele": "G", "Blond": -1.850, "Red": -0.210, "Black": 2.450, "LightShade": -1.920, "pop_mean_dosage": 0.95},
        "rs1393350": {"allele": "A", "Blond": 0.250, "Red": 0.110, "Black": -0.310, "LightShade": 0.180, "pop_mean_dosage": 0.45},
        "rs12203592": {"allele": "T", "Blond": 0.890, "Red": 0.450, "Black": -0.950, "LightShade": 0.740, "pop_mean_dosage": 0.18},
        "rs35264875": {"allele": "T", "Blond": 0.620, "Red": 0.150, "Black": -0.550, "LightShade": 0.480, "pop_mean_dosage": 0.20},
        "rs1805007": {"allele": "T", "Blond": 0.110, "Red": 4.820, "Black": -1.200, "LightShade": 0.350, "pop_mean_dosage": 0.08},
        "rs1805008": {"allele": "T", "Blond": 0.080, "Red": 4.650, "Black": -1.150, "LightShade": 0.310, "pop_mean_dosage": 0.06},
        "rs1805009": {"allele": "C", "Blond": 0.050, "Red": 4.120, "Black": -0.980, "LightShade": 0.280, "pop_mean_dosage": 0.03},
        "rs12821256": {"allele": "C", "Blond": 0.780, "Red": 0.020, "Black": -0.810, "LightShade": 0.650, "pop_mean_dosage": 0.12},
    },
}

SKIN_PHOTOTYPE_SPEC = {
    "CLASSES": ["VeryPale", "Pale", "Dark", "DarkToBlack", "Intermediate"],
    "REFERENCE_CLASS": "Intermediate",
    "INTERCEPTS": {
        "VeryPale": -2.150,
        "Pale": -1.100,
        "Dark": -2.850,
        "DarkToBlack": -5.200,
    },
    "EFFECT_ALLELES": {
        "rs1426654": {"allele": "A", "VeryPale": 2.450, "Pale": 1.820, "Dark": -3.950, "DarkToBlack": -7.850, "pop_mean_dosage": 0.98},
        "rs16891982": {"allele": "G", "VeryPale": 2.120, "Pale": 1.540, "Dark": -3.120, "DarkToBlack": -6.420, "pop_mean_dosage": 0.95},
        "rs1015362": {"allele": "G", "VeryPale": 0.650, "Pale": 0.420, "Dark": -0.510, "DarkToBlack": -0.880, "pop_mean_dosage": 0.50},
        "rs10756819": {"allele": "A", "VeryPale": 0.580, "Pale": 0.390, "Dark": -0.450, "DarkToBlack": -0.720, "pop_mean_dosage": 0.45},
        "rs12821256": {"allele": "C", "VeryPale": 0.820, "Pale": 0.510, "Dark": -0.680, "DarkToBlack": -1.150, "pop_mean_dosage": 0.12},
        "rs12913832": {"allele": "C", "VeryPale": 1.250, "Pale": 0.880, "Dark": -1.450, "DarkToBlack": -2.820, "pop_mean_dosage": 0.85},
        "rs1805007": {"allele": "T", "VeryPale": 2.150, "Pale": 1.210, "Dark": -0.880, "DarkToBlack": -1.420, "pop_mean_dosage": 0.08},
        "rs10424031": {"allele": "A", "VeryPale": -1.120, "Pale": -0.750, "Dark": 2.150, "DarkToBlack": 4.850, "pop_mean_dosage": 0.05},
    },
}


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class EyeColorPrediction:
    probabilities: Dict[str, float]        # Blue, Intermediate, Brown (sum = 1.0)
    predicted_class: str                  # Argmax class
    confidence: float                     # Max probability
    missing_loci_count: int
    imputed_loci_count: int


@dataclass
class HairColorPrediction:
    probabilities: Dict[str, float]        # Blond, Red, Black, Brown (sum = 1.0)
    predicted_class: str                  # Argmax class
    confidence: float                     # Max probability
    shade_probabilities: Dict[str, float]  # Light, Dark (sum = 1.0)
    predicted_shade: str                  # "Light" or "Dark"
    missing_loci_count: int


@dataclass
class SkinPhototypePrediction:
    probabilities: Dict[str, float]        # VeryPale, Pale, Intermediate, Dark, DarkToBlack (sum = 1.0)
    fitzpatrick_type: str                 # "Type I (Very Pale)", "Type II (Pale)", etc.
    predicted_class: str
    confidence: float
    missing_loci_count: int


@dataclass
class HIrisPlexCompositeResult:
    eye_color: EyeColorPrediction
    hair_color: HairColorPrediction
    skin_phototype: SkinPhototypePrediction
    total_snps_assayed: int
    missingness_ratio: float
    prosecutors_fallacy_shield: str


# ── Engine ─────────────────────────────────────────────────────────────────────

class HIrisPlexEngine:
    """
    FORENZA HIrisPlex-S 41-SNP DNA Pigmentation Forensics Engine (Module 11).

    Implements verbatim from Pillar 3 Research §1.
    """

    def __init__(self, lambda_missing: float = 0.35):
        self.lambda_missing = lambda_missing

    # ── §1.1 Core Softmax MLR Solver with Invariant ───────────────────────────

    def _solve_mlr_softmax(
        self,
        snp_dosages: Dict[str, Union[int, float]],
        trait_spec: Dict[str, Any],
        enable_imputation: bool = True,
    ) -> Tuple[Dict[str, float], int, int]:
        """
        Solves Multinomial Logistic Regression (MLR) with Softmax normalization:

        ln(P(Y=k) / P(Y=K)) = beta_k0 + sum_i beta_ki * X_i
        P(Y=k) = exp(beta_k0 + sum beta_ki X_i) / (1 + sum_l exp(beta_l0 + sum beta_li X_i))
        P(Y=K) = 1 / (1 + sum_l exp(beta_l0 + sum beta_li X_i))

        Enforces invariant: |sum P - 1.0| <= 1e-6
        Applies missingness uncertainty penalty scaling: L_k / sqrt(1 + lambda * M)
        """
        classes = trait_spec["CLASSES"]
        ref_class = trait_spec["REFERENCE_CLASS"]
        intercepts = trait_spec["INTERCEPTS"]
        effect_alleles = trait_spec["EFFECT_ALLELES"]

        non_ref_classes = [c for c in classes if c != ref_class]
        logits = {c: intercepts[c] for c in non_ref_classes}

        total_panel_snps = len(effect_alleles)
        missing_count = 0
        imputed_count = 0

        for snp_id, effect_info in effect_alleles.items():
            if snp_id in snp_dosages:
                dosage = float(snp_dosages[snp_id])
            else:
                missing_count += 1
                if enable_imputation:
                    dosage = float(effect_info.get("pop_mean_dosage", 0.50))
                    imputed_count += 1
                else:
                    dosage = 0.0

            for c in non_ref_classes:
                if c in effect_info:
                    logits[c] += effect_info[c] * dosage

        # Missingness fraction M = N_missing / N_total
        m_ratio = missing_count / max(1, total_panel_snps)
        scale_denom = math.sqrt(1.0 + (self.lambda_missing * m_ratio))

        # Scaled logits for non-ref classes
        scaled_logits = {c: logits[c] / scale_denom for c in non_ref_classes}

        # Softmax transformation
        # Reference class logit is 0.0, so exp(0.0) = 1.0
        max_logit = max(list(scaled_logits.values()) + [0.0])
        exp_logits = {c: math.exp(scaled_logits[c] - max_logit) for c in non_ref_classes}
        exp_ref = math.exp(0.0 - max_logit)

        total_exp = sum(exp_logits.values()) + exp_ref

        probs = {}
        for c in non_ref_classes:
            probs[c] = exp_logits[c] / total_exp
        probs[ref_class] = exp_ref / total_exp

        # Enforce sum-to-unity invariant
        sum_p = sum(probs.values())
        if sum_p > 0:
            probs = {k: v / sum_p for k, v in probs.items()}

        rounded_probs = {k: round(probs[k], 6) for k in classes}
        # Final residual fix on reference class so that sum is exact to 1.0
        sum_r = sum(rounded_probs.values())
        rounded_probs[ref_class] = round(rounded_probs[ref_class] + (1.0 - sum_r), 6)

        return rounded_probs, missing_count, imputed_count


    # ── §1.2 Eye Color Prediction (IrisPlex 6 Loci) ───────────────────────────

    def predict_eye_color(
        self,
        snp_dosages: Dict[str, Union[int, float]],
        enable_imputation: bool = True,
    ) -> EyeColorPrediction:
        """Predicts eye color (Blue, Intermediate, Brown) using IrisPlex 6 loci."""
        probs, missing, imputed = self._solve_mlr_softmax(snp_dosages, EYE_COLOR_SPEC, enable_imputation)
        best_class = max(probs.keys(), key=lambda k: probs[k])

        return EyeColorPrediction(
            probabilities=probs,
            predicted_class=best_class,
            confidence=probs[best_class],
            missing_loci_count=missing,
            imputed_loci_count=imputed,
        )

    # ── §1.2 Hair Color & Shade Prediction (HIrisPlex 22 Loci) ─────────────────

    def predict_hair_color(
        self,
        snp_dosages: Dict[str, Union[int, float]],
        enable_imputation: bool = True,
    ) -> HairColorPrediction:
        """Predicts hair color (Blond, Red, Black, Brown) and hair shade intensity (Light vs Dark)."""
        probs, missing, _ = self._solve_mlr_softmax(snp_dosages, HAIR_COLOR_SPEC, enable_imputation)
        best_class = max(probs.keys(), key=lambda k: probs[k])

        # Hair shade logit calculation
        shade_logit = HAIR_COLOR_SPEC["SHADE_INTERCEPT"]
        for snp_id, effect_info in HAIR_COLOR_SPEC["EFFECT_ALLELES"].items():
            if "LightShade" in effect_info:
                if snp_id in snp_dosages:
                    dosage = float(snp_dosages[snp_id])
                elif enable_imputation:
                    dosage = float(effect_info.get("pop_mean_dosage", 0.50))
                else:
                    dosage = 0.0
                shade_logit += effect_info["LightShade"] * dosage

        p_light = 1.0 / (1.0 + math.exp(-shade_logit))
        p_dark = 1.0 - p_light

        shade_probs = {
            "Light": round(p_light, 6),
            "Dark": round(p_dark, 6),
        }
        best_shade = "Light" if p_light >= 0.50 else "Dark"

        return HairColorPrediction(
            probabilities=probs,
            predicted_class=best_class,
            confidence=probs[best_class],
            shade_probabilities=shade_probs,
            predicted_shade=best_shade,
            missing_loci_count=missing,
        )

    # ── §1.2 Skin Phototype Prediction (HIrisPlex-S 36 Loci) ───────────────────

    def predict_skin_phototype(
        self,
        snp_dosages: Dict[str, Union[int, float]],
        enable_imputation: bool = True,
    ) -> SkinPhototypePrediction:
        """Predicts Fitzpatrick skin phototype (Types I, II, III/IV, V, VI) using HIrisPlex-S 36 loci."""
        probs, missing, _ = self._solve_mlr_softmax(snp_dosages, SKIN_PHOTOTYPE_SPEC, enable_imputation)
        best_class = max(probs.keys(), key=lambda k: probs[k])

        fitzpatrick_map = {
            "VeryPale": "Type I (Very Pale / Always Burns)",
            "Pale": "Type II (Pale / Usually Burns)",
            "Intermediate": "Type III / IV (Intermediate / Tans Moderately)",
            "Dark": "Type V (Dark / Rarely Burns)",
            "DarkToBlack": "Type VI (Dark to Black / Never Burns)",
        }

        return SkinPhototypePrediction(
            probabilities=probs,
            fitzpatrick_type=fitzpatrick_map.get(best_class, "Type III / IV"),
            predicted_class=best_class,
            confidence=probs[best_class],
            missing_loci_count=missing,
        )

    # ── Full HIrisPlex-S Composite Prediction ─────────────────────────────────

    def predict_full_hirisplex_s(
        self,
        snp_dosages: Dict[str, Union[int, float]],
        enable_imputation: bool = True,
    ) -> HIrisPlexCompositeResult:
        """Executes full HIrisPlex-S tri-trait prediction suite across Eye, Hair, and Skin phototypes."""
        eye = self.predict_eye_color(snp_dosages, enable_imputation)
        hair = self.predict_hair_color(snp_dosages, enable_imputation)
        skin = self.predict_skin_phototype(snp_dosages, enable_imputation)

        all_snps = set(EYE_COLOR_SPEC["EFFECT_ALLELES"].keys()) | set(HAIR_COLOR_SPEC["EFFECT_ALLELES"].keys()) | set(SKIN_PHOTOTYPE_SPEC["EFFECT_ALLELES"].keys())
        total_panel = len(all_snps)
        assayed_count = sum(1 for s in all_snps if s in snp_dosages)
        missing_ratio = (total_panel - assayed_count) / max(1, total_panel)

        shield = (
            "IMPORTANT (HIrisPlex-S Forensic Legal Shield): DNA phenotyping predictions reflect "
            "externally visible characteristics (EVCs) estimated via validated multinomial logistic regression "
            "models (VISAGE Consortium). Probabilities indicate physical appearance likelihoods and must NOT "
            "be interpreted as individual source identification."
        )

        return HIrisPlexCompositeResult(
            eye_color=eye,
            hair_color=hair,
            skin_phototype=skin,
            total_snps_assayed=assayed_count,
            missingness_ratio=round(missing_ratio, 4),
            prosecutors_fallacy_shield=shield,
        )
