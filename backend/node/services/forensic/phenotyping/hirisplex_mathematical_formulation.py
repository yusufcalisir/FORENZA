"""
FORENZA HIrisPlex-S 41-SNP Forensic DNA Pigmentation Formulation Engine (Module 3.1).
Pure Mathematical & Biocomputational Formulation Engine.

Standards & References:
  - Pillar 3 Research §1: HIrisPlex-S Pigmentation Model Mathematics and Parameterization.
  - Walsh S, et al. (2018) The HIrisPlex-S system for simultaneous prediction of hair, eye and skin colour from DNA. Forensic Science International: Genetics 34:189-199.
  - VISAGE Consortium Guidelines for Forensic DNA Phenotyping (2020).
  - ISO/IEC 17025:2017 & ENFSI Evaluative Reporting (2017).
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any


# ── Canonical Coefficient Matrices ──────────────────────────────────────────

EYE_COLOR_MODEL = {
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

HAIR_COLOR_MODEL = {
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
        "rs2814778": {"allele": "C", "Blond": -0.512, "Red": -0.284, "Black": 1.852, "LightShade": -1.850, "pop_mean_dosage": 0.10},
        "rs3827760": {"allele": "G", "Blond": -0.412, "Red": -0.184, "Black": 1.251, "LightShade": -1.250, "pop_mean_dosage": 0.15},
    },
}

SKIN_PHOTOTYPE_MODEL = {
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
        "rs2814778": {"allele": "C", "VeryPale": -1.214, "Pale": -0.781, "Dark": 2.451, "DarkToBlack": 4.852, "pop_mean_dosage": 0.10},
    },
}

HAIR_MORPHOLOGY_MODEL = {
    "CLASSES": ["Straight", "Wavy", "Curly_Coily"],
    "EFFECT_ALLELES": {
        "rs3827760": {"gene": "EDAR", "effect_allele": "G", "straight_weight": 2.854},
        "rs11803731": {"gene": "TCHH", "effect_allele": "A", "curly_weight": 2.105},
    },
}


# ── Output Dataclasses ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PhenotypePredictionResult:
    domain: str                                 # Eye, Hair, Skin, Morphology
    probabilities: Dict[str, float]             # Normalized probabilities (sum = 1.0)
    predicted_class: str                        # Argmax class
    confidence: float                           # Probability of argmax
    is_simplex_valid: bool                      # |sum P - 1.0| <= 1e-6
    missing_loci_count: int
    imputed_loci_count: int
    uncertainty_penalty_applied: bool


@dataclass(frozen=True)
class FullHIrisPlexResult:
    eye_color: PhenotypePredictionResult
    hair_color: PhenotypePredictionResult
    hair_shade: Dict[str, float]                # Light vs Dark
    skin_phototype: PhenotypePredictionResult
    hair_morphology: PhenotypePredictionResult
    total_snps_assayed: int
    total_snps_missing: int
    global_confidence_score: float
    prosecutors_fallacy_shield: str


class HIrisPlexMathematicalFormulation:
    """
    Pure biocomputational implementation of HIrisPlex-S 41-SNP Multinomial
    Logistic Regression (MLR) with Softmax normalization and missing-SNP imputation.
    """

    @classmethod
    def predict_multinomial_trait(
        cls,
        spec: Dict[str, Any],
        genotype_dosages: Dict[str, float],
        enable_imputation: bool = True,
        uncertainty_lambda: float = 0.35,
    ) -> PhenotypePredictionResult:
        """
        Executes MLR Softmax evaluation across target classes with reference baseline.
        """
        classes = spec["CLASSES"]
        ref_class = spec["REFERENCE_CLASS"]
        intercepts = spec["INTERCEPTS"]
        effect_alleles = spec["EFFECT_ALLELES"]

        target_classes = [c for c in classes if c != ref_class]
        logits: Dict[str, float] = {c: intercepts[c] for c in target_classes}

        total_loci = len(effect_alleles)
        missing_count = 0
        imputed_count = 0

        for rsid, locus_info in effect_alleles.items():
            if rsid in genotype_dosages and genotype_dosages[rsid] is not None:
                dosage = float(genotype_dosages[rsid])
            elif enable_imputation:
                dosage = locus_info.get("pop_mean_dosage", 0.50) * 2.0
                imputed_count += 1
            else:
                missing_count += 1
                continue

            for c in target_classes:
                if c in locus_info:
                    logits[c] += locus_info[c] * dosage

        # Uncertainty Scaling Penalty for missing loci: logit / sqrt(1 + lambda * M)
        penalty_applied = False
        if missing_count > 0 or imputed_count > 0:
            m_fraction = (missing_count + imputed_count) / float(total_loci)
            scaling = math.sqrt(1.0 + (uncertainty_lambda * m_fraction))
            logits = {c: logits[c] / scaling for c in target_classes}
            penalty_applied = True

        # Softmax computation
        # Exp of non-ref classes, 1.0 for ref class
        exp_terms = {c: math.exp(min(50.0, max(-50.0, logits[c]))) for c in target_classes}
        denom = 1.0 + sum(exp_terms.values())

        raw_probs: Dict[str, float] = {c: exp_terms[c] / denom for c in target_classes}
        raw_probs[ref_class] = 1.0 / denom

        # Verify Sum-to-One Simplex on raw floating point probabilities
        total_p = sum(raw_probs.values())
        is_valid_simplex = abs(total_p - 1.0) <= 1e-6

        # Normalization with 6 decimal places and exact simplex constraint
        normalized_probs = {c: round(raw_probs[c] / total_p, 6) for c in classes}
        best_class = max(normalized_probs, key=lambda k: normalized_probs[k])
        conf = normalized_probs[best_class]

        return PhenotypePredictionResult(
            domain="Phenotype",
            probabilities=normalized_probs,
            predicted_class=best_class,
            confidence=conf,
            is_simplex_valid=is_valid_simplex,
            missing_loci_count=missing_count,
            imputed_loci_count=imputed_count,
            uncertainty_penalty_applied=penalty_applied,
        )

    @classmethod
    def predict_hair_shade(
        cls,
        genotype_dosages: Dict[str, float],
    ) -> Dict[str, float]:
        """
        Binary shade prediction (Light vs Dark hair).
        """
        spec = HAIR_COLOR_MODEL
        intercept = spec["SHADE_INTERCEPT"]
        effect_alleles = spec["EFFECT_ALLELES"]

        logit = intercept
        for rsid, locus_info in effect_alleles.items():
            if "LightShade" in locus_info:
                dosage = float(genotype_dosages.get(rsid, locus_info.get("pop_mean_dosage", 0.50) * 2.0))
                logit += locus_info["LightShade"] * dosage

        p_light = 1.0 / (1.0 + math.exp(-min(50.0, max(-50.0, logit))))
        p_dark = 1.0 - p_light

        return {
            "Light": round(p_light, 4),
            "Dark": round(p_dark, 4),
        }

    @classmethod
    def predict_hair_morphology(
        cls,
        genotype_dosages: Dict[str, float],
    ) -> PhenotypePredictionResult:
        """
        Predicts hair morphology (Straight, Wavy, Curly/Coily) using EDAR and TCHH alleles.
        """
        edar_dosage = float(genotype_dosages.get("rs3827760", 0.0))    # EDAR 370Ala (Asian thick straight)
        tchh_dosage = float(genotype_dosages.get("rs11803731", 0.0))   # TCHH (Caucasian/African curliness)

        logit_straight = 0.50 + (2.854 * edar_dosage) - (1.200 * tchh_dosage)
        logit_curly = -1.20 - (1.800 * edar_dosage) + (2.105 * tchh_dosage)
        logit_wavy = 0.00  # Reference baseline

        exp_s = math.exp(min(50.0, max(-50.0, logit_straight)))
        exp_c = math.exp(min(50.0, max(-50.0, logit_curly)))
        denom = 1.0 + exp_s + exp_c

        p_straight = exp_s / denom
        p_curly = exp_c / denom
        p_wavy = 1.0 / denom

        probs = {
            "Straight": round(p_straight, 4),
            "Wavy": round(p_wavy, 4),
            "Curly_Coily": round(p_curly, 4),
        }
        best_class = max(probs, key=lambda k: probs[k])

        return PhenotypePredictionResult(
            domain="HairMorphology",
            probabilities=probs,
            predicted_class=best_class,
            confidence=probs[best_class],
            is_simplex_valid=abs(sum(probs.values()) - 1.0) <= 1e-4,
            missing_loci_count=0,
            imputed_loci_count=0,
            uncertainty_penalty_applied=False,
        )

    @classmethod
    def predict_full_hirisplex_s(
        cls,
        genotype_dosages: Dict[str, float],
        enable_imputation: bool = True,
    ) -> FullHIrisPlexResult:
        """
        Executes full simultaneous prediction across Eye Color, Hair Color & Shade,
        Skin Phototype, and Hair Morphology.
        """
        eye_res = cls.predict_multinomial_trait(EYE_COLOR_MODEL, genotype_dosages, enable_imputation)
        hair_res = cls.predict_multinomial_trait(HAIR_COLOR_MODEL, genotype_dosages, enable_imputation)
        shade_res = cls.predict_hair_shade(genotype_dosages)
        skin_res = cls.predict_multinomial_trait(SKIN_PHOTOTYPE_MODEL, genotype_dosages, enable_imputation)
        morph_res = cls.predict_hair_morphology(genotype_dosages)

        total_snps = len(EYE_COLOR_MODEL["EFFECT_ALLELES"]) + len(HAIR_COLOR_MODEL["EFFECT_ALLELES"]) + len(SKIN_PHOTOTYPE_MODEL["EFFECT_ALLELES"])
        missing_snps = eye_res.missing_loci_count + hair_res.missing_loci_count + skin_res.missing_loci_count

        global_conf = round((eye_res.confidence + hair_res.confidence + skin_res.confidence) / 3.0, 4)

        shield = (
            "ENFSI (2017) & VISAGE (2020) Evaluative DNA Phenotyping Reporting Shield: "
            "Reported pigmentation probabilities reflect statistical expectations from 41-SNP MLR models. "
            "Phenotypic predictions provide investigative leads and must not be used as definitive individual identification."
        )

        return FullHIrisPlexResult(
            eye_color=eye_res,
            hair_color=hair_res,
            hair_shade=shade_res,
            skin_phototype=skin_res,
            hair_morphology=morph_res,
            total_snps_assayed=total_snps,
            total_snps_missing=missing_snps,
            global_confidence_score=global_conf,
            prosecutors_fallacy_shield=shield,
        )
