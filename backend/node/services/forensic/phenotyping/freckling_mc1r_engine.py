"""
FORENZA Ephelides (Freckling), MC1R Epistasis & UV Sensitivity Index Engine — Module 15.

Implements verbatim from Pillar 3 Research §5:
  - §5.1 MC1R Variant Classification Matrix ('R' High Risk, 'r' Low Risk, wt)
  - §5.2 Compound Heterozygosity and Quantitative Freckling Score (F_score)
  - Minimal Erythema Dose (MED) & UV Sensitivity Tiers
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union


# ── MC1R & Modifier Loci Constants ─────────────────────────────────────────────

MC1R_R_VARIANTS = {
    "rs1805006":  {"name": "D84E",  "amino_acid": "Asp84Glu",  "weight": 2.50, "risk_class": "R"},
    "rs75570604": {"name": "R142H", "amino_acid": "Arg142His", "weight": 2.40, "risk_class": "R"},
    "rs1805007":  {"name": "R151C", "amino_acid": "Arg151Cys", "weight": 2.85, "risk_class": "R"},
    "rs1805008":  {"name": "R160W", "amino_acid": "Arg160Trp", "weight": 2.75, "risk_class": "R"},
    "rs1805009":  {"name": "D294H", "amino_acid": "Asp294His", "weight": 2.60, "risk_class": "R"},
}

MC1R_r_VARIANTS = {
    "rs1805005": {"name": "V60L",  "amino_acid": "Val60Leu",  "weight": 1.10, "risk_class": "r"},
    "rs2228479": {"name": "V92M",  "amino_acid": "Val92Met",  "weight": 0.85, "risk_class": "r"},
    "rs885479":  {"name": "R163Q", "amino_acid": "Arg163Gln", "weight": 0.75, "risk_class": "r"},
}

MODIFIER_LOCI = {
    "rs1015362":  {"gene": "ASIP", "weight": 0.85},
    "rs10756819": {"gene": "BNC2", "weight": 0.65},
}


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class MC1RDiplotypeResult:
    diplotype: str                       # "R/R", "R/r", "R/wt", "r/r", "r/wt", "wt/wt"
    functional_classification: str        # "SEVERE_LOSS", "MODERATE_LOSS", "MILD_LOSS", "WILD_TYPE"
    total_mc1r_loss_weight: float        # W_MC1R
    r_high_risk_alleles_count: int       # n_R
    r_low_risk_alleles_count: int        # n_r
    detected_variants: List[str]


@dataclass
class FrecklingScoreResult:
    freckling_score_pct: float           # F_score in [0.0, 100.0]%
    freckling_intensity: str             # "DENSE", "MODERATE", "MILD", "MINIMAL"
    epistatic_modifiers_applied: Dict[str, float]


@dataclass
class UVSensitivityResult:
    minimal_erythema_dose_category: str  # "<20 mJ/cm2", "20-35 mJ/cm2", "35-50 mJ/cm2", ">50 mJ/cm2"
    tanning_capacity: str                # "NEVER_TANS_ALWAYS_BURNS", "RARE_TAN_FREQUENT_BURN", "MILD_TAN_OCCASIONAL_BURN", "NORMAL_TAN_RARE_BURN"
    photoprotection_guidance: str


@dataclass
class FrecklingAndUVCompositeResult:
    mc1r: MC1RDiplotypeResult
    freckling: FrecklingScoreResult
    uv_sensitivity: UVSensitivityResult
    assayed_snps_count: int
    prosecutors_fallacy_shield: str


# ── Engine ─────────────────────────────────────────────────────────────────────

class FrecklingMC1REngine:
    """
    FORENZA Ephelides (Freckling), MC1R Epistasis & UV Sensitivity Index Engine.

    Derives verbatim from Pillar 3 Research §5.
    """

    def __init__(self):
        self.r_high = MC1R_R_VARIANTS
        self.r_low = MC1R_r_VARIANTS
        self.modifiers = MODIFIER_LOCI

    def determine_mc1r_diplotype(
        self,
        snp_dosages: Dict[str, Union[int, float]],
    ) -> MC1RDiplotypeResult:
        """
        Calculates total MC1R loss-of-function weight and classifies diplotype (Research §5.1).
        """
        w_total = 0.0
        n_R = 0
        n_r = 0
        detected = []

        # Check 'R' High-Risk Variants
        for rsid, info in self.r_high.items():
            dosage = int(round(float(snp_dosages.get(rsid, 0))))
            if dosage > 0:
                w_total += info["weight"] * dosage
                n_R += dosage
                detected.append(f"{info['name']} (rsID {rsid}, dosage={dosage}, Class R)")

        # Check 'r' Low-Risk Variants
        for rsid, info in self.r_low.items():
            dosage = int(round(float(snp_dosages.get(rsid, 0))))
            if dosage > 0:
                w_total += info["weight"] * dosage
                n_r += dosage
                detected.append(f"{info['name']} (rsID {rsid}, dosage={dosage}, Class r)")

        # Classify Diplotype
        if n_R >= 2:
            diplotype = "R/R"
            classification = "SEVERE_LOSS"
        elif n_R >= 1 and n_r >= 1:
            diplotype = "R/r"
            classification = "MODERATE_LOSS"
        elif n_R == 1 and n_r == 0:
            diplotype = "R/wt"
            classification = "MODERATE_LOSS"
        elif n_R == 0 and n_r >= 2:
            diplotype = "r/r"
            classification = "MILD_LOSS"
        elif n_R == 0 and n_r == 1:
            diplotype = "r/wt"
            classification = "MILD_LOSS"
        else:
            diplotype = "wt/wt"
            classification = "WILD_TYPE"

        return MC1RDiplotypeResult(
            diplotype=diplotype,
            functional_classification=classification,
            total_mc1r_loss_weight=round(w_total, 3),
            r_high_risk_alleles_count=n_R,
            r_low_risk_alleles_count=n_r,
            detected_variants=detected,
        )

    def calculate_freckling_score(
        self,
        mc1r_result: MC1RDiplotypeResult,
        snp_dosages: Dict[str, Union[int, float]],
    ) -> FrecklingScoreResult:
        """
        Calculates quantitative Freckling Score F_score in [0.0, 100.0]% (Research §5.2).

        Formula:
          logit = -2.50 + 1.35*W_MC1R + 0.85*X_ASIP + 0.65*X_BNC2
          F_score = min(100.0, 100.0 / (1.0 + exp(-logit)))
        """
        x_asip = float(snp_dosages.get("rs1015362", 0))
        x_bnc2 = float(snp_dosages.get("rs10756819", 0))

        logit = -2.50 + (1.35 * mc1r_result.total_mc1r_loss_weight) + (0.85 * x_asip) + (0.65 * x_bnc2)
        exp_val = math.exp(-logit) if logit < 50.0 else 0.0
        f_score = min(100.0, 100.0 / (1.0 + exp_val))

        # Intensity categorization
        if f_score >= 75.0:
            intensity = "DENSE (Extensive Ephelides)"
        elif f_score >= 45.0:
            intensity = "MODERATE (Moderate Facial / Body Ephelides)"
        elif f_score >= 20.0:
            intensity = "MILD (Few Ephelides Upon Sun Exposure)"
        else:
            intensity = "MINIMAL (Rare / No Visible Ephelides)"

        modifiers = {
            "ASIP_rs1015362": x_asip,
            "BNC2_rs10756819": x_bnc2,
        }

        return FrecklingScoreResult(
            freckling_score_pct=round(f_score, 2),
            freckling_intensity=intensity,
            epistatic_modifiers_applied=modifiers,
        )

    def determine_uv_sensitivity(
        self,
        mc1r_result: MC1RDiplotypeResult,
    ) -> UVSensitivityResult:
        """
        Maps MC1R diplotype to Minimal Erythema Dose (MED) and Sun Sensitivity guidance (Research §5.2).
        """
        if mc1r_result.diplotype == "R/R":
            med_cat = "< 20 mJ/cm2 (Extremely Low MED / Severe Erythema Risk)"
            tanning = "NEVER_TANS_ALWAYS_BURNS"
            guidance = "Extremely high photosensitivity. High melanoma and basal cell carcinoma relative risk."
        elif mc1r_result.diplotype in ["R/r", "R/wt"]:
            med_cat = "20 - 35 mJ/cm2 (Low MED / Frequent Erythema Risk)"
            tanning = "RARE_TAN_FREQUENT_BURN"
            guidance = "Elevated photosensitivity. Tanning occurs rarely; burning is frequent under UV index >= 4."
        elif mc1r_result.diplotype in ["r/r", "r/wt"]:
            med_cat = "35 - 50 mJ/cm2 (Moderate MED / Moderate Erythema Risk)"
            tanning = "MILD_TAN_OCCASIONAL_BURN"
            guidance = "Moderate photosensitivity. Gradual tanning occurs with occasional erythema."
        else:
            med_cat = "> 50 mJ/cm2 (High MED / Normal Erythema Tolerance)"
            tanning = "NORMAL_TAN_RARE_BURN"
            guidance = "Low photosensitivity. Normal melanin synthesis and high MED UV tolerance."

        return UVSensitivityResult(
            minimal_erythema_dose_category=med_cat,
            tanning_capacity=tanning,
            photoprotection_guidance=guidance,
        )

    def analyze_ephelides_profile(
        self,
        snp_dosages: Dict[str, Union[int, float]],
    ) -> FrecklingAndUVCompositeResult:
        """
        Full composite analysis of MC1R diplotype, quantitative freckling score, and UV sensitivity.
        """
        mc1r_res = self.determine_mc1r_diplotype(snp_dosages)
        freckle_res = self.calculate_freckling_score(mc1r_res, snp_dosages)
        uv_res = self.determine_uv_sensitivity(mc1r_res)

        assayed_loci = (
            set(self.r_high.keys()) | set(self.r_low.keys()) | set(self.modifiers.keys())
        )
        assayed_count = sum(1 for rs in assayed_loci if rs in snp_dosages)

        shield_statement = (
            "IMPORTANT (Ephelides & UV Sensitivity Legal Shield): Ephelides (freckling) scores and UV sensitivity "
            "metrics represent statistical probabilities of cutaneous melanin response and minimal erythema dose (MED). "
            "Ephelides expression is strongly modulated by cumulative seasonal UV exposure, sun protection behavior, "
            "and age. These predictions must NEVER be treated as absolute individual identification."
        )

        return FrecklingAndUVCompositeResult(
            mc1r=mc1r_res,
            freckling=freckle_res,
            uv_sensitivity=uv_res,
            assayed_snps_count=assayed_count,
            prosecutors_fallacy_shield=shield_statement,
        )
