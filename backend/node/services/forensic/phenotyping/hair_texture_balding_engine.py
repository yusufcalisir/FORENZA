"""
FORENZA Hair Texture Dynamics & Androgenetic Alopecia (Balding Risk PRS) Engine — Module 14.

Implements verbatim from Pillar 3 Research §4:
  - §4.1 Hair Fiber Cross-Sectional Geometry & Curl Density Index (C_curl) from EDAR, TCHH, WNT10A
  - §4.2 Androgenetic Alopecia Polygenic Risk Score (PRS_balding) and Hamilton-Norwood Scale Mapping
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Union


# ── Loci Constants ─────────────────────────────────────────────────────────────

TEXTURE_LOCI = {
    "rs3827072": {"gene": "EDAR (Val370Ala)", "trait": "Fiber Thickness & Straightening", "weight_curl": -2.10},
    "rs11803731": {"gene": "TCHH (Trichohyalin)", "trait": "Curl Induction", "weight_curl": 1.85},
    "rs7349332": {"gene": "WNT10A", "trait": "Curl Induction", "weight_curl": 1.42},
}

BALDING_PRS_LOCI = {
    "rs6152":    {"gene": "AR (Androgen Receptor)", "weight_prs": 0.982},
    "rs2180439": {"gene": "20p11 Locus",            "weight_prs": 0.541},
    "rs1160312": {"gene": "20p11 Locus",            "weight_prs": 0.485},
    "rs756853":  {"gene": "HDAC9 Locus",          "weight_prs": 0.362},
}


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class HairTextureResult:
    curl_density_index: float
    texture_category: str
    fiber_cross_sectional_area_um2: float
    estimated_fiber_diameter_um: str
    assayed_texture_snps: int


@dataclass
class BaldingPRSResult:
    prs_score: float
    hamilton_norwood_grade: str
    clinical_description: str
    risk_level: str
    assayed_balding_snps: int


@dataclass
class HairAnalysisResult:
    texture: HairTextureResult
    balding: BaldingPRSResult
    prosecutors_fallacy_shield: str


# ── Engine ─────────────────────────────────────────────────────────────────────

class HairTextureBaldingEngine:
    """
    FORENZA Hair Texture Dynamics and Androgenetic Alopecia PRS Engine.

    Derives verbatim from Pillar 3 Research §4.
    """

    def __init__(self):
        self.texture_loci = TEXTURE_LOCI
        self.balding_loci = BALDING_PRS_LOCI

    def compute_hair_texture(
        self,
        snp_dosages: Dict[str, Union[int, float]],
    ) -> HairTextureResult:
        """
        Calculates hair fiber cross-sectional area and Curl Density Index (Research §4.1).
        
        Formula:
          Area (um^2) = 3850.0 + 1420.0 * X_EDAR
          C_curl = clamp(1.20 + 1.85 * X_TCHH + 1.42 * X_WNT10A - 2.10 * X_EDAR, 0.0, 10.0)
        """
        x_edar = float(snp_dosages.get("rs3827072", 0))
        x_tchh = float(snp_dosages.get("rs11803731", 0))
        x_wnt10a = float(snp_dosages.get("rs7349332", 0))

        # Biophysical Cross-Sectional Area
        area_um2 = 3850.0 + (1420.0 * x_edar)

        # Curl Density Index
        raw_curl = 1.20 + (1.85 * x_tchh) + (1.42 * x_wnt10a) - (2.10 * x_edar)
        c_curl = max(0.0, min(10.0, raw_curl))

        # Categorization & Diameter
        if c_curl < 2.0:
            category = "STRAIGHT"
            if x_edar >= 1.5:
                diameter_str = "85.0 - 110.0 um (Thick Straight / Asian Variant)"
            else:
                diameter_str = "70.0 - 85.0 um (Fine / Medium Straight)"
        elif c_curl < 4.5:
            category = "WAVY"
            diameter_str = "65.0 - 80.0 um (Wavy Texture)"
        elif c_curl < 7.0:
            category = "CURLY"
            diameter_str = "55.0 - 70.0 um (Defined Curls)"
        else:
            category = "KINKY_WOOLLY"
            diameter_str = "45.0 - 60.0 um (Tight Coil / Afro-textured)"

        assayed_count = sum(1 for rs in self.texture_loci if rs in snp_dosages)

        return HairTextureResult(
            curl_density_index=round(c_curl, 3),
            texture_category=category,
            fiber_cross_sectional_area_um2=round(area_um2, 1),
            estimated_fiber_diameter_um=diameter_str,
            assayed_texture_snps=assayed_count,
        )

    def compute_balding_prs(
        self,
        snp_dosages: Dict[str, Union[int, float]],
    ) -> BaldingPRSResult:
        """
        Calculates Androgenetic Alopecia Polygenic Risk Score (Research §4.2).
        
        Formula:
          PRS_balding = 0.982*X_rs6152 + 0.541*X_rs2180439 + 0.485*X_rs1160312 + 0.362*X_rs756853
        """
        prs = 0.0
        for rsid, info in self.balding_loci.items():
            dosage = float(snp_dosages.get(rsid, 0))
            prs += info["weight_prs"] * dosage

        prs = round(prs, 3)

        # Hamilton-Norwood Scale Mapping
        if prs < 0.50:
            grade = "GRADE_I_II"
            desc = "Hamilton-Norwood Grade I / II — Minimal or No Hair Loss"
            risk = "LOW_RISK"
        elif prs < 1.20:
            grade = "GRADE_III"
            desc = "Hamilton-Norwood Grade III — Slight Temporal / Vertex Recess"
            risk = "MODERATE_RISK"
        elif prs < 2.10:
            grade = "GRADE_IV_V"
            desc = "Hamilton-Norwood Grade IV / V — Moderate Vertex Loss"
            risk = "ELEVATED_RISK"
        else:
            grade = "GRADE_VI_VII"
            desc = "Hamilton-Norwood Grade VI / VII — Severe / Extensive Balding"
            risk = "HIGH_RISK"

        assayed_count = sum(1 for rs in self.balding_loci if rs in snp_dosages)

        return BaldingPRSResult(
            prs_score=prs,
            hamilton_norwood_grade=grade,
            clinical_description=desc,
            risk_level=risk,
            assayed_balding_snps=assayed_count,
        )

    def analyze_hair_profile(
        self,
        snp_dosages: Dict[str, Union[int, float]],
    ) -> HairAnalysisResult:
        """
        Executes full composite analysis of hair morphology, texture dynamics, and balding PRS.
        """
        texture_res = self.compute_hair_texture(snp_dosages)
        balding_res = self.compute_balding_prs(snp_dosages)

        shield_statement = (
            "IMPORTANT (Hair Morphology & Balding Legal Shield): Hair texture metrics and androgenetic alopecia "
            "polygenic scores represent probabilistic biophysical estimates. Phenotypic expression can be influenced "
            "by age, hormonal fluctuations, environmental treatments, and epigenetics. These results must NEVER be "
            "treated as absolute individual identification."
        )

        return HairAnalysisResult(
            texture=texture_res,
            balding=balding_res,
            prosecutors_fallacy_shield=shield_statement,
        )
