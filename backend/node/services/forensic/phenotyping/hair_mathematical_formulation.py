"""
FORENZA Hair Morphology, Cross-Sectional Curvature & Balding PRS Mathematical Formulation Engine.
Module 3.4 — Pillar 3: Phenotyping, Biogeographic Ancestry & Morphometrics.

Derives verbatim from:
  - Pillar 3 Research Specification (§4: Hair Texture Dynamics & Androgenetic Alopecia PRS)
  - Medland et al. (2009) Nat Genet — EDAR Val370Ala (rs3827072) East Asian hair morphology
  - Adhikari et al. (2016) Nat Commun — TCHH (rs11803731), WNT10A (rs7349332) curl loci
  - Li et al. (2022) PLOS Genetics — Hamilton-Norwood AGA GWAS (rs6152, rs2180439, rs1160312, rs756853)
  - Martin & Saller (1957) Anthropological cephalometric reference baselines

Constants:
  Area baseline     : 3850.0 μm² (European/baseline intercept)
  EDAR weight       : +1420.0 μm² per derived allele (Val370Ala, rs3827072)
  Curl baseline     : 1.20 (additive logit baseline)
  TCHH weight       : +1.85 per derived allele (rs11803731)
  WNT10A weight     : +1.42 per derived allele (rs7349332)
  EDAR curl weight  : -2.10 per derived allele (rs3827072, straightening effect)
  Curl clamp        : [0.0, 10.0]
  PRS weights       : AR=0.982, 20p11a=0.541, 20p11b=0.485, HDAC9=0.362
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Union


# ── Primary Morphometric Loci Constants ───────────────────────────────────────

HAIR_TEXTURE_LOCI: Dict[str, Dict] = {
    "rs3827072": {
        "gene": "EDAR (Val370Ala)",
        "effect_allele": "C",
        "trait": "Fiber Cross-Sectional Thickness & Straightening",
        "weight_area_um2": 1420.0,   # μm² per derived allele
        "weight_curl": -2.10,        # Curl Density Index decrement per derived allele
        "reference": "Medland et al. 2009 Nat Genet",
    },
    "rs11803731": {
        "gene": "TCHH (Trichohyalin)",
        "effect_allele": "T",
        "trait": "Curl Induction — Cortical Fiber Curvature",
        "weight_area_um2": 0.0,
        "weight_curl": 1.85,
        "reference": "Adhikari et al. 2016 Nat Commun",
    },
    "rs7349332": {
        "gene": "WNT10A",
        "effect_allele": "T",
        "trait": "Curl Induction — Wnt Signaling Pathway",
        "weight_area_um2": 0.0,
        "weight_curl": 1.42,
        "reference": "Adhikari et al. 2016 Nat Commun",
    },
}

BALDING_PRS_LOCI: Dict[str, Dict] = {
    "rs6152": {
        "gene": "AR (Androgen Receptor, Xq11-12)",
        "effect_allele": "A",
        "weight_prs": 0.982,
        "reference": "Hillmer et al. 2005 AJHG",
    },
    "rs2180439": {
        "gene": "20p11 (FOXA2/PAX1 Locus)",
        "effect_allele": "T",
        "weight_prs": 0.541,
        "reference": "Li et al. 2022 PLOS Genetics",
    },
    "rs1160312": {
        "gene": "20p11 (FOXA2/PAX1 Locus)",
        "effect_allele": "C",
        "weight_prs": 0.485,
        "reference": "Li et al. 2022 PLOS Genetics",
    },
    "rs756853": {
        "gene": "HDAC9 (Histone Deacetylase 9)",
        "effect_allele": "C",
        "weight_prs": 0.362,
        "reference": "Li et al. 2022 PLOS Genetics",
    },
}

# ── Biophysical Baseline Constants (Research §4.1) ────────────────────────────
FIBER_AREA_BASELINE_UM2: float = 3850.0    # μm² baseline cross-sectional area (European baseline)
CURL_INDEX_BASELINE: float = 1.20          # Additive logit baseline (no effect alleles)
CURL_CLAMP_MIN: float = 0.0
CURL_CLAMP_MAX: float = 10.0

# ── Hamilton-Norwood Grade Thresholds (Research §4.2) ─────────────────────────
HN_GRADE_I_II_THRESHOLD: float = 0.50     # PRS < 0.50 -> Grade I/II (Minimal)
HN_GRADE_III_THRESHOLD: float = 1.20      # 0.50 <= PRS < 1.20 -> Grade III (Slight)
HN_GRADE_IV_V_THRESHOLD: float = 2.10     # 1.20 <= PRS < 2.10 -> Grade IV/V (Moderate)
# PRS >= 2.10 -> Grade VI/VII (Severe)

# ── Texture Category Thresholds ────────────────────────────────────────────────
CURL_STRAIGHT_MAX: float = 2.0    # C_curl < 2.0 -> STRAIGHT
CURL_WAVY_MAX: float = 4.5        # 2.0 <= C_curl < 4.5 -> WAVY
CURL_CURLY_MAX: float = 7.0       # 4.5 <= C_curl < 7.0 -> CURLY
# C_curl >= 7.0 -> KINKY_WOOLLY


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class HairTextureFormulationResult:
    """Biophysical hair morphology result from pure mathematical formulation."""
    curl_density_index: float        # C_curl ∈ [0.0, 10.0] (clamped)
    raw_curl_index: float            # Unclamped C_curl (for diagnostic purposes)
    texture_category: str            # STRAIGHT / WAVY / CURLY / KINKY_WOOLLY
    fiber_cross_sectional_area_um2: float  # μm²
    fiber_diameter_category: str     # Diameter range string
    edar_dosage: float
    tchh_dosage: float
    wnt10a_dosage: float
    assayed_texture_loci: int


@dataclass(frozen=True)
class BaldingPRSFormulationResult:
    """Androgenetic Alopecia PRS result from pure mathematical formulation."""
    prs_raw: float                   # Σ (w_i * X_i) before clamping
    prs_score: float                 # Rounded to 3 decimal places
    hamilton_norwood_grade: str      # GRADE_I_II / GRADE_III / GRADE_IV_V / GRADE_VI_VII
    clinical_description: str        # Full clinical description string
    risk_level: str                  # LOW_RISK / MODERATE_RISK / ELEVATED_RISK / HIGH_RISK
    max_possible_prs: float          # 2 * Σ w_i = 4.740 (all homozygous)
    assayed_balding_loci: int


# ── Core Mathematical Formulation ─────────────────────────────────────────────

class HairMathematicalFormulation:
    """
    Formal mathematical engine for Hair Morphology, Cross-Sectional Curvature & Balding PRS.

    All constants derive verbatim from Pillar 3 Research §4.
    """

    @staticmethod
    def compute_fiber_area_um2(x_edar: float) -> float:
        """
        Research §4.1 — Biophysical Cross-Sectional Area Formula:

            Area(μm²) = 3850.0 + 1420.0 × X_EDAR

        where X_EDAR ∈ {0, 1, 2} = count of EDAR Val370Ala derived alleles (rs3827072).

        Baseline: 3850.0 μm² (mean European fiber area, Martin & Saller 1957)
        EDAR slope: +1420.0 μm²/allele (Asian coarse-hair EDAR variant)
        Range: [3850.0, 6690.0] μm² for X_EDAR ∈ {0, 1, 2}
        """
        return FIBER_AREA_BASELINE_UM2 + (1420.0 * x_edar)

    @staticmethod
    def compute_curl_density_index(
        x_edar: float,
        x_tchh: float,
        x_wnt10a: float,
    ) -> tuple[float, float]:
        """
        Research §4.1 — Curl Density Index Formula:

            C_curl_raw = 1.20 + 1.85 × X_TCHH + 1.42 × X_WNT10A - 2.10 × X_EDAR
            C_curl = clamp(C_curl_raw, 0.0, 10.0)

        SNP weights (verbatim):
          +1.85 per TCHH derived allele (rs11803731) — Trichohyalin curvature induction
          +1.42 per WNT10A derived allele (rs7349332) — Wnt signaling pathway
          -2.10 per EDAR derived allele  (rs3827072)  — Val370Ala straightening force

        Returns: (c_curl_clamped, c_curl_raw)
        """
        raw = CURL_INDEX_BASELINE + (1.85 * x_tchh) + (1.42 * x_wnt10a) - (2.10 * x_edar)
        clamped = max(CURL_CLAMP_MIN, min(CURL_CLAMP_MAX, raw))
        return round(clamped, 3), round(raw, 3)

    @staticmethod
    def classify_texture_category(c_curl: float) -> str:
        """
        Research §4.1 — Hair Texture Category Classification:

            C_curl < 2.0 → STRAIGHT
            2.0 ≤ C_curl < 4.5 → WAVY
            4.5 ≤ C_curl < 7.0 → CURLY
            C_curl ≥ 7.0 → KINKY_WOOLLY
        """
        if c_curl < CURL_STRAIGHT_MAX:
            return "STRAIGHT"
        elif c_curl < CURL_WAVY_MAX:
            return "WAVY"
        elif c_curl < CURL_CURLY_MAX:
            return "CURLY"
        else:
            return "KINKY_WOOLLY"

    @staticmethod
    def classify_fiber_diameter(x_edar: float, texture: str) -> str:
        """
        Research §4.1 — Fiber Diameter Classification by EDAR dosage and texture:

            EDAR ≥ 1.5 (thick Asian):  85.0 – 110.0 μm (Thick Straight / Asian Variant)
            STRAIGHT (European):        70.0 – 85.0  μm (Fine / Medium Straight)
            WAVY:                        65.0 – 80.0  μm (Wavy Texture)
            CURLY:                       55.0 – 70.0  μm (Defined Curls)
            KINKY_WOOLLY:                45.0 – 60.0  μm (Tight Coil / Afro-textured)
        """
        if texture == "STRAIGHT" and x_edar >= 1.5:
            return "85.0 - 110.0 um (Thick Straight / Asian Variant)"
        elif texture == "STRAIGHT":
            return "70.0 - 85.0 um (Fine / Medium Straight)"
        elif texture == "WAVY":
            return "65.0 - 80.0 um (Wavy Texture)"
        elif texture == "CURLY":
            return "55.0 - 70.0 um (Defined Curls)"
        else:
            return "45.0 - 60.0 um (Tight Coil / Afro-textured)"

    @staticmethod
    def compute_balding_prs(snp_dosages: Dict[str, Union[int, float]]) -> float:
        """
        Research §4.2 — Androgenetic Alopecia Polygenic Risk Score:

            PRS_balding = 0.982 × X_rs6152 + 0.541 × X_rs2180439
                        + 0.485 × X_rs1160312 + 0.362 × X_rs756853

        Weights (verbatim):
          AR (rs6152):        w = 0.982 (strongest single locus: X-linked AR promoter)
          20p11 (rs2180439):  w = 0.541
          20p11 (rs1160312):  w = 0.485
          HDAC9 (rs756853):   w = 0.362

        Max PRS = 2 × (0.982 + 0.541 + 0.485 + 0.362) = 2 × 2.370 = 4.740
        Min PRS = 0.000 (all reference alleles)
        """
        prs = 0.0
        for rsid, info in BALDING_PRS_LOCI.items():
            dosage = float(snp_dosages.get(rsid, 0))
            prs += info["weight_prs"] * dosage
        return prs

    @staticmethod
    def classify_hamilton_norwood(prs: float) -> tuple[str, str, str]:
        """
        Research §4.2 — Hamilton-Norwood Grade Mapping:

            PRS < 0.50       → GRADE_I_II   (Minimal or No Hair Loss)
            0.50 ≤ PRS < 1.20 → GRADE_III   (Slight Temporal / Vertex Recess)
            1.20 ≤ PRS < 2.10 → GRADE_IV_V  (Moderate Vertex Loss)
            PRS ≥ 2.10        → GRADE_VI_VII (Severe / Extensive Balding)

        Returns: (grade, clinical_description, risk_level)
        """
        if prs < HN_GRADE_I_II_THRESHOLD:
            return (
                "GRADE_I_II",
                "Hamilton-Norwood Grade I / II — Minimal or No Hair Loss",
                "LOW_RISK",
            )
        elif prs < HN_GRADE_III_THRESHOLD:
            return (
                "GRADE_III",
                "Hamilton-Norwood Grade III — Slight Temporal / Vertex Recess",
                "MODERATE_RISK",
            )
        elif prs < HN_GRADE_IV_V_THRESHOLD:
            return (
                "GRADE_IV_V",
                "Hamilton-Norwood Grade IV / V — Moderate Vertex Loss",
                "ELEVATED_RISK",
            )
        else:
            return (
                "GRADE_VI_VII",
                "Hamilton-Norwood Grade VI / VII — Severe / Extensive Balding",
                "HIGH_RISK",
            )

    @classmethod
    def run_hair_texture_formulation(
        cls,
        snp_dosages: Dict[str, Union[int, float]],
    ) -> HairTextureFormulationResult:
        """
        Full hair texture formulation pipeline: Area → Curl → Classify.
        """
        x_edar = float(snp_dosages.get("rs3827072", 0.0))
        x_tchh = float(snp_dosages.get("rs11803731", 0.0))
        x_wnt10a = float(snp_dosages.get("rs7349332", 0.0))

        area = cls.compute_fiber_area_um2(x_edar)
        c_curl, raw_curl = cls.compute_curl_density_index(x_edar, x_tchh, x_wnt10a)
        texture = cls.classify_texture_category(c_curl)
        diameter = cls.classify_fiber_diameter(x_edar, texture)

        assayed = sum(1 for rs in HAIR_TEXTURE_LOCI if rs in snp_dosages)

        return HairTextureFormulationResult(
            curl_density_index=c_curl,
            raw_curl_index=raw_curl,
            texture_category=texture,
            fiber_cross_sectional_area_um2=round(area, 1),
            fiber_diameter_category=diameter,
            edar_dosage=x_edar,
            tchh_dosage=x_tchh,
            wnt10a_dosage=x_wnt10a,
            assayed_texture_loci=assayed,
        )

    @classmethod
    def run_balding_prs_formulation(
        cls,
        snp_dosages: Dict[str, Union[int, float]],
    ) -> BaldingPRSFormulationResult:
        """
        Full balding PRS formulation pipeline: Σ weights → Hamilton-Norwood Grade.
        """
        prs_raw = cls.compute_balding_prs(snp_dosages)
        prs_rounded = round(prs_raw, 3)
        grade, desc, risk = cls.classify_hamilton_norwood(prs_raw)

        assayed = sum(1 for rs in BALDING_PRS_LOCI if rs in snp_dosages)

        # Max PRS: all 4 loci at dosage=2
        max_prs = 2.0 * sum(info["weight_prs"] for info in BALDING_PRS_LOCI.values())

        return BaldingPRSFormulationResult(
            prs_raw=round(prs_raw, 6),
            prs_score=prs_rounded,
            hamilton_norwood_grade=grade,
            clinical_description=desc,
            risk_level=risk,
            max_possible_prs=round(max_prs, 3),
            assayed_balding_loci=assayed,
        )
