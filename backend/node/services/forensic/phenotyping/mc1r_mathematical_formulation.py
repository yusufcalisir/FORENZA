"""
FORENZA MC1R Epistasis, Ephelides (Freckling) & UV Sensitivity — Mathematical Formulation Engine.
Module 3.5 — Pillar 3: Phenotyping, Biogeographic Ancestry & Morphometrics.

Derives verbatim from:
  - Pillar 3 Research Specification (§5: MC1R Functional Variants, Ephelides & UV Sensitivity)
  - Sulem et al. (2007) Nat Genet — MC1R 'R' high-risk variant (R151C, R160W, D294H) cohort
  - Sulem et al. (2008) Nat Genet — Ephelides GWAS (ASIP, BNC2 modifier loci)
  - Valverde et al. (1995) Nat Genet — Original MC1R Red Hair Color (RHC) classification matrix
  - Mekkas et al. (2021) VISAGE Consortium — UV sensitivity MED thresholds

Verbatim Constants (Research §5):
  Freckling intercept:  β₀ = -2.50
  W_MC1R coefficient:   β₁ = +1.35
  ASIP coefficient:     β₂ = +0.85 (rs1015362)
  BNC2 coefficient:     β₃ = +0.65 (rs10756819)
  R-High variant weights: D84E=2.50, R142H=2.40, R151C=2.85, R160W=2.75, D294H=2.60
  r-Low variant weights:  V60L=1.10, V92M=0.85, R163Q=0.75
  MED diplotype mapping: R/R < 20 mJ/cm², R/r|R/wt = 20-35, r/r|r/wt = 35-50, wt/wt > 50
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union


# ── MC1R 'R' High-Risk Variant Weights (Research §5.1) ───────────────────────

MC1R_R_WEIGHTS: Dict[str, Dict] = {
    "rs1805006": {"name": "D84E",  "amino_acid": "Asp84Glu",  "weight": 2.50, "risk_class": "R"},
    "rs75570604":{"name": "R142H", "amino_acid": "Arg142His", "weight": 2.40, "risk_class": "R"},
    "rs1805007": {"name": "R151C", "amino_acid": "Arg151Cys", "weight": 2.85, "risk_class": "R"},
    "rs1805008": {"name": "R160W", "amino_acid": "Arg160Trp", "weight": 2.75, "risk_class": "R"},
    "rs1805009": {"name": "D294H", "amino_acid": "Asp294His", "weight": 2.60, "risk_class": "R"},
}

# ── MC1R 'r' Low-Risk Variant Weights (Research §5.1) ────────────────────────

MC1R_r_WEIGHTS: Dict[str, Dict] = {
    "rs1805005": {"name": "V60L",  "amino_acid": "Val60Leu",  "weight": 1.10, "risk_class": "r"},
    "rs2228479": {"name": "V92M",  "amino_acid": "Val92Met",  "weight": 0.85, "risk_class": "r"},
    "rs885479":  {"name": "R163Q", "amino_acid": "Arg163Gln", "weight": 0.75, "risk_class": "r"},
}

# ── Epistatic Modifier Loci Weights (Research §5.2) ──────────────────────────

MODIFIER_WEIGHTS: Dict[str, Dict] = {
    "rs1015362":  {"gene": "ASIP (Agouti Signaling Protein)", "weight": 0.85},
    "rs10756819": {"gene": "BNC2 (Basonuclin-2)",             "weight": 0.65},
}

# ── Freckling Logistic Model Constants (Research §5.2) ───────────────────────

FRECKLING_INTERCEPT: float = -2.50     # β₀
FRECKLING_W_MC1R_COEFF: float = 1.35  # β₁ (W_MC1R coefficient)
FRECKLING_ASIP_COEFF: float = 0.85    # β₂ (ASIP rs1015362)
FRECKLING_BNC2_COEFF: float = 0.65    # β₃ (BNC2 rs10756819)

# ── Freckling Intensity Category Thresholds ───────────────────────────────────

FRECKLING_DENSE_THRESHOLD: float = 75.0     # F_score ≥ 75 → DENSE
FRECKLING_MODERATE_THRESHOLD: float = 45.0  # F_score ≥ 45 → MODERATE
FRECKLING_MILD_THRESHOLD: float = 20.0      # F_score ≥ 20 → MILD

# ── Diplotype Classification Thresholds ──────────────────────────────────────

# Diplotype rules (Research §5.1):
#   n_R ≥ 2           → R/R  (SEVERE_LOSS)
#   n_R ≥ 1, n_r ≥ 1 → R/r  (MODERATE_LOSS)
#   n_R == 1, n_r == 0→ R/wt (MODERATE_LOSS)
#   n_R == 0, n_r ≥ 2 → r/r  (MILD_LOSS)
#   n_R == 0, n_r == 1 → r/wt (MILD_LOSS)
#   n_R == 0, n_r == 0 → wt/wt (WILD_TYPE)

# ── MED Thresholds — (Research §5.2) ─────────────────────────────────────────
MED_R_R_CATEGORY: str = "< 20 mJ/cm2 (Extremely Low MED / Severe Erythema Risk)"
MED_R_HET_CATEGORY: str = "20 - 35 mJ/cm2 (Low MED / Frequent Erythema Risk)"
MED_r_HOM_CATEGORY: str = "35 - 50 mJ/cm2 (Moderate MED / Moderate Erythema Risk)"
MED_WT_CATEGORY: str = "> 50 mJ/cm2 (High MED / Normal Erythema Tolerance)"


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class MC1RFormulationResult:
    """Verbatim MC1R diplotype and functional classification from mathematical formulation."""
    diplotype: str                         # "R/R", "R/r", "R/wt", "r/r", "r/wt", "wt/wt"
    functional_classification: str         # "SEVERE_LOSS" / "MODERATE_LOSS" / "MILD_LOSS" / "WILD_TYPE"
    total_mc1r_loss_weight: float          # W_MC1R = Σ w_i * X_i
    r_high_risk_alleles_count: int         # n_R
    r_low_risk_alleles_count: int          # n_r
    detected_variants: List[str]
    max_possible_weight: float             # 2 * max(R-weight) = 2 * 2.85 = 5.70


@dataclass(frozen=True)
class FrecklingFormulationResult:
    """Quantitative freckling score from mathematical formulation."""
    logit_raw: float                       # -2.50 + 1.35*W + 0.85*ASIP + 0.65*BNC2
    freckling_score_pct: float             # F_score ∈ [0.0, 100.0]
    freckling_intensity: str               # DENSE / MODERATE / MILD / MINIMAL
    x_asip: float
    x_bnc2: float
    w_mc1r_used: float


@dataclass(frozen=True)
class UVFormulationResult:
    """UV sensitivity from MC1R diplotype mapping."""
    diplotype_input: str
    minimal_erythema_dose_category: str
    tanning_capacity: str
    photoprotection_guidance: str


# ── Core Mathematical Formulation ─────────────────────────────────────────────

class MC1RMathematicalFormulation:
    """
    Formal mathematical engine for MC1R Epistasis, Ephelides & UV Sensitivity.

    All constants derive verbatim from Pillar 3 Research §5.
    """

    @staticmethod
    def compute_mc1r_loss_weight(
        snp_dosages: Dict[str, Union[int, float]],
    ) -> Tuple[float, int, int, List[str]]:
        """
        Research §5.1 — Additive MC1R Loss-of-Function Weight:

            W_MC1R = Σ_i (w_i * X_i)

        where the sum is over all detected 'R' high-risk and 'r' low-risk variants.
        X_i ∈ {0, 1, 2} = allele dosage at locus i.

        Returns: (w_total, n_R, n_r, detected_variants)
        """
        w_total = 0.0
        n_R = 0
        n_r = 0
        detected: List[str] = []

        for rsid, info in MC1R_R_WEIGHTS.items():
            dosage = int(round(float(snp_dosages.get(rsid, 0))))
            if dosage > 0:
                w_total += info["weight"] * dosage
                n_R += dosage
                detected.append(f"{info['name']} ({rsid}, dosage={dosage}, Class R, w={info['weight']})")

        for rsid, info in MC1R_r_WEIGHTS.items():
            dosage = int(round(float(snp_dosages.get(rsid, 0))))
            if dosage > 0:
                w_total += info["weight"] * dosage
                n_r += dosage
                detected.append(f"{info['name']} ({rsid}, dosage={dosage}, Class r, w={info['weight']})")

        return round(w_total, 6), n_R, n_r, detected

    @staticmethod
    def classify_diplotype(n_R: int, n_r: int) -> Tuple[str, str]:
        """
        Research §5.1 — MC1R Diplotype Classification:

            n_R ≥ 2               → "R/R"  (SEVERE_LOSS)
            n_R ≥ 1 and n_r ≥ 1  → "R/r"  (MODERATE_LOSS)
            n_R == 1, n_r == 0    → "R/wt" (MODERATE_LOSS)
            n_R == 0, n_r ≥ 2     → "r/r"  (MILD_LOSS)
            n_R == 0, n_r == 1    → "r/wt" (MILD_LOSS)
            else                  → "wt/wt" (WILD_TYPE)

        Returns: (diplotype, functional_classification)
        """
        if n_R >= 2:
            return "R/R", "SEVERE_LOSS"
        elif n_R >= 1 and n_r >= 1:
            return "R/r", "MODERATE_LOSS"
        elif n_R == 1 and n_r == 0:
            return "R/wt", "MODERATE_LOSS"
        elif n_R == 0 and n_r >= 2:
            return "r/r", "MILD_LOSS"
        elif n_R == 0 and n_r == 1:
            return "r/wt", "MILD_LOSS"
        else:
            return "wt/wt", "WILD_TYPE"

    @staticmethod
    def compute_freckling_score(
        w_mc1r: float,
        x_asip: float,
        x_bnc2: float,
    ) -> Tuple[float, float]:
        """
        Research §5.2 — Quantitative Freckling Score Formula:

            logit = -2.50 + 1.35 × W_MC1R + 0.85 × X_ASIP + 0.65 × X_BNC2
            F_score = min(100.0, 100.0 / (1 + exp(-logit)))

        Returns: (f_score_pct, logit_raw)
        """
        logit = (
            FRECKLING_INTERCEPT
            + FRECKLING_W_MC1R_COEFF * w_mc1r
            + FRECKLING_ASIP_COEFF * x_asip
            + FRECKLING_BNC2_COEFF * x_bnc2
        )
        # Numerical stability: avoid overflow in exp
        exp_val = math.exp(-logit) if logit < 500.0 else 0.0
        f_score = min(100.0, 100.0 / (1.0 + exp_val))
        return round(f_score, 4), round(logit, 6)

    @staticmethod
    def classify_freckling_intensity(f_score: float) -> str:
        """
        Research §5.2 — Freckling Intensity Classification:

            F_score ≥ 75.0 → DENSE (Extensive Ephelides)
            F_score ≥ 45.0 → MODERATE (Moderate Facial / Body Ephelides)
            F_score ≥ 20.0 → MILD (Few Ephelides Upon Sun Exposure)
            F_score < 20.0 → MINIMAL (Rare / No Visible Ephelides)
        """
        if f_score >= FRECKLING_DENSE_THRESHOLD:
            return "DENSE (Extensive Ephelides)"
        elif f_score >= FRECKLING_MODERATE_THRESHOLD:
            return "MODERATE (Moderate Facial / Body Ephelides)"
        elif f_score >= FRECKLING_MILD_THRESHOLD:
            return "MILD (Few Ephelides Upon Sun Exposure)"
        else:
            return "MINIMAL (Rare / No Visible Ephelides)"

    @staticmethod
    def compute_uv_sensitivity(diplotype: str) -> Tuple[str, str, str]:
        """
        Research §5.2 — MED Diplotype Mapping:

            R/R             → < 20 mJ/cm²  (NEVER_TANS_ALWAYS_BURNS)
            R/r or R/wt     → 20-35 mJ/cm² (RARE_TAN_FREQUENT_BURN)
            r/r or r/wt     → 35-50 mJ/cm² (MILD_TAN_OCCASIONAL_BURN)
            wt/wt           → > 50 mJ/cm²  (NORMAL_TAN_RARE_BURN)

        Returns: (med_category, tanning_capacity, photoprotection_guidance)
        """
        if diplotype == "R/R":
            return (
                MED_R_R_CATEGORY,
                "NEVER_TANS_ALWAYS_BURNS",
                "Extremely high photosensitivity. High melanoma and basal cell carcinoma relative risk.",
            )
        elif diplotype in ("R/r", "R/wt"):
            return (
                MED_R_HET_CATEGORY,
                "RARE_TAN_FREQUENT_BURN",
                "Elevated photosensitivity. Tanning occurs rarely; burning is frequent under UV index >= 4.",
            )
        elif diplotype in ("r/r", "r/wt"):
            return (
                MED_r_HOM_CATEGORY,
                "MILD_TAN_OCCASIONAL_BURN",
                "Moderate photosensitivity. Gradual tanning occurs with occasional erythema.",
            )
        else:
            return (
                MED_WT_CATEGORY,
                "NORMAL_TAN_RARE_BURN",
                "Low photosensitivity. Normal melanin synthesis and high MED UV tolerance.",
            )

    @classmethod
    def run_mc1r_formulation(
        cls,
        snp_dosages: Dict[str, Union[int, float]],
    ) -> MC1RFormulationResult:
        """Full MC1R diplotype classification pipeline."""
        w_total, n_R, n_r, detected = cls.compute_mc1r_loss_weight(snp_dosages)
        diplotype, classification = cls.classify_diplotype(n_R, n_r)

        # Max possible weight: R151C homozygous = 2 * 2.85 = 5.70
        max_w = 2.0 * max(v["weight"] for v in MC1R_R_WEIGHTS.values())

        return MC1RFormulationResult(
            diplotype=diplotype,
            functional_classification=classification,
            total_mc1r_loss_weight=round(w_total, 3),
            r_high_risk_alleles_count=n_R,
            r_low_risk_alleles_count=n_r,
            detected_variants=detected,
            max_possible_weight=round(max_w, 2),
        )

    @classmethod
    def run_freckling_formulation(
        cls,
        snp_dosages: Dict[str, Union[int, float]],
        w_mc1r: float,
    ) -> FrecklingFormulationResult:
        """Full freckling score formulation pipeline."""
        x_asip = float(snp_dosages.get("rs1015362", 0))
        x_bnc2 = float(snp_dosages.get("rs10756819", 0))
        f_score, logit = cls.compute_freckling_score(w_mc1r, x_asip, x_bnc2)
        intensity = cls.classify_freckling_intensity(f_score)

        return FrecklingFormulationResult(
            logit_raw=logit,
            freckling_score_pct=f_score,
            freckling_intensity=intensity,
            x_asip=x_asip,
            x_bnc2=x_bnc2,
            w_mc1r_used=w_mc1r,
        )

    @classmethod
    def run_uv_formulation(cls, diplotype: str) -> UVFormulationResult:
        """Full UV sensitivity mapping pipeline."""
        med, tanning, guidance = cls.compute_uv_sensitivity(diplotype)
        return UVFormulationResult(
            diplotype_input=diplotype,
            minimal_erythema_dose_category=med,
            tanning_capacity=tanning,
            photoprotection_guidance=guidance,
        )
