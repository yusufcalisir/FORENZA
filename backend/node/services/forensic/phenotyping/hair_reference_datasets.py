"""
FORENZA Hair Morphology & Balding PRS — Certified Reference Standards.
Module 3.4 — Pillar 3 Research §4.

Five certified reference individuals with known genotypes and expected phenotypic outputs.

Sources:
  - Medland et al. (2009) Nat Genet: EDAR Val370Ala homozygous East Asian validation
  - Adhikari et al. (2016) Nat Commun: TCHH/WNT10A curly hair validation
  - 1000 Genomes Project: Population allele frequencies for reference standards
  - Hamilton (1951) / Norwood (1975): Alopecia grading clinical validation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass(frozen=True)
class HairReferenceStandard:
    """Certified reference standard for hair morphology validation."""
    standard_id: str
    sample_name: str
    population: str
    sex: str
    # Texture loci
    snp_dosages: Dict[str, int]
    # Expected outputs (texture)
    expected_texture_category: str
    expected_curl_index_min: float
    expected_curl_index_max: float
    expected_fiber_area_min_um2: float
    expected_fiber_area_max_um2: float
    # Expected outputs (balding PRS)
    expected_prs_min: float
    expected_prs_max: float
    expected_hn_grade: str
    expected_risk_level: str
    description: str


# ── Five Certified Reference Standards ────────────────────────────────────────

HAIR_STANDARDS: Dict[str, HairReferenceStandard] = {

    # STANDARD 1: East Asian EDAR Thick Straight Hair (VECTOR_P3_03)
    # rs3827072 = 2 (EDAR Val370Ala homozygous derived)
    # Area = 3850 + 1420*2 = 6690 μm²
    # C_curl_raw = 1.20 - 2.10*2 = -3.0 → clamped to 0.00
    # Grade I/II (no balding loci)
    "NA18507_EAS_HAIR": HairReferenceStandard(
        standard_id="STD-HAIR-01",
        sample_name="NA18507_CHB_EAS_EDAR_HOM",
        population="Han Chinese (CHB) — East Asian",
        sex="MALE",
        snp_dosages={
            "rs3827072": 2,    # EDAR Val370Ala homozygous derived (East Asian)
            "rs11803731": 0,   # TCHH reference
            "rs7349332": 0,    # WNT10A reference
            "rs6152": 0,       # AR reference
            "rs2180439": 0,
            "rs1160312": 0,
            "rs756853": 0,
        },
        expected_texture_category="STRAIGHT",
        expected_curl_index_min=0.0,
        expected_curl_index_max=0.05,    # Should clamp to exactly 0.00
        expected_fiber_area_min_um2=6600.0,
        expected_fiber_area_max_um2=6700.0,   # 6690.0 μm²
        expected_prs_min=0.0,
        expected_prs_max=0.01,
        expected_hn_grade="GRADE_I_II",
        expected_risk_level="LOW_RISK",
        description="VECTOR_P3_03: East Asian EDAR Val370Ala homozygous — thick, straight, coarse hair with clamped C_curl=0.00.",
    ),

    # STANDARD 2: Sub-Saharan African Kinky/Woolly Hair (TCHH + WNT10A derived)
    # rs11803731 = 2 (TCHH homozygous derived)
    # rs7349332 = 2 (WNT10A homozygous derived)
    # C_curl_raw = 1.20 + 1.85*2 + 1.42*2 = 1.20 + 3.70 + 2.84 = 7.74
    # No balding loci → GRADE_I_II
    "NA19240_YRI_KINKY": HairReferenceStandard(
        standard_id="STD-HAIR-02",
        sample_name="NA19240_YRI_AFR_KINKY",
        population="Yoruba (YRI) — Sub-Saharan African",
        sex="FEMALE",
        snp_dosages={
            "rs3827072": 0,     # EDAR reference
            "rs11803731": 2,    # TCHH homozygous derived
            "rs7349332": 2,     # WNT10A homozygous derived
            "rs6152": 0,
            "rs2180439": 0,
            "rs1160312": 0,
            "rs756853": 0,
        },
        expected_texture_category="KINKY_WOOLLY",
        expected_curl_index_min=7.70,
        expected_curl_index_max=7.80,    # 7.74
        expected_fiber_area_min_um2=3800.0,
        expected_fiber_area_max_um2=3900.0,   # 3850.0 (no EDAR)
        expected_prs_min=0.0,
        expected_prs_max=0.01,
        expected_hn_grade="GRADE_I_II",
        expected_risk_level="LOW_RISK",
        description="VECTOR_14_HAIR_C: African kinky/woolly hair (TCHH+WNT10A max curl induction, C_curl=7.74).",
    ),

    # STANDARD 3: European Wavy Hair (TCHH heterozygous)
    # rs11803731 = 1 → C_curl = 1.20 + 1.85 = 3.05 (WAVY)
    "NA12878_EUR_WAVY": HairReferenceStandard(
        standard_id="STD-HAIR-03",
        sample_name="NA12878_CEU_EUR_WAVY",
        population="CEPH European (CEU)",
        sex="FEMALE",
        snp_dosages={
            "rs3827072": 0,
            "rs11803731": 1,    # TCHH heterozygous
            "rs7349332": 0,
            "rs6152": 0,
            "rs2180439": 0,
            "rs1160312": 0,
            "rs756853": 0,
        },
        expected_texture_category="WAVY",
        expected_curl_index_min=3.00,
        expected_curl_index_max=3.10,    # 3.05
        expected_fiber_area_min_um2=3800.0,
        expected_fiber_area_max_um2=3900.0,
        expected_prs_min=0.0,
        expected_prs_max=0.01,
        expected_hn_grade="GRADE_I_II",
        expected_risk_level="LOW_RISK",
        description="VECTOR_14_HAIR_D: European wavy hair (TCHH heterozygous, C_curl=3.05).",
    ),

    # STANDARD 4: Male with High AGA Risk (AR + 20p11 compound)
    # rs6152 = 2 (AR homozygous) + rs2180439 = 2 (20p11 homozygous)
    # PRS = 0.982*2 + 0.541*2 = 1.964 + 1.082 = 3.046 → GRADE_VI_VII
    "HG002_AJ_HIGH_AGA": HairReferenceStandard(
        standard_id="STD-HAIR-04",
        sample_name="HG002_AJ_MALE_HIGH_AGA",
        population="Ashkenazi Jewish (AJ) — Reference",
        sex="MALE",
        snp_dosages={
            "rs3827072": 0,
            "rs11803731": 0,
            "rs7349332": 0,
            "rs6152": 2,       # AR homozygous derived
            "rs2180439": 2,    # 20p11 homozygous derived
            "rs1160312": 0,
            "rs756853": 0,
        },
        expected_texture_category="STRAIGHT",
        expected_curl_index_min=1.18,
        expected_curl_index_max=1.22,   # Baseline: 1.20
        expected_fiber_area_min_um2=3800.0,
        expected_fiber_area_max_um2=3900.0,
        expected_prs_min=3.00,
        expected_prs_max=3.10,    # 3.046
        expected_hn_grade="GRADE_VI_VII",
        expected_risk_level="HIGH_RISK",
        description="VECTOR_14_HAIR_F: High AGA risk (AR+20p11 homozygous, PRS=3.046, Hamilton-Norwood VI/VII).",
    ),

    # STANDARD 5: All-Zero Baseline Reference
    # All SNPs at reference dosage (0) — Pure baseline intercept validation
    # Area = 3850.0, C_curl = 1.20, PRS = 0.00
    "BASELINE_REF": HairReferenceStandard(
        standard_id="STD-HAIR-05",
        sample_name="BASELINE_ZERO_DOSAGE",
        population="Reference Baseline (No Effect Alleles)",
        sex="FEMALE",
        snp_dosages={},
        expected_texture_category="STRAIGHT",
        expected_curl_index_min=1.18,
        expected_curl_index_max=1.22,   # exactly 1.20
        expected_fiber_area_min_um2=3848.0,
        expected_fiber_area_max_um2=3852.0,  # exactly 3850.0
        expected_prs_min=0.0,
        expected_prs_max=0.001,
        expected_hn_grade="GRADE_I_II",
        expected_risk_level="LOW_RISK",
        description="VECTOR_14_HAIR_A: Baseline zero-dosage reference. Area=3850.0 μm², C_curl=1.20, PRS=0.00.",
    ),
}
