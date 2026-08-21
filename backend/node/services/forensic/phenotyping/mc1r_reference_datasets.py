"""
FORENZA MC1R Epistasis & UV Sensitivity — Certified Reference Standards.
Module 3.5 — Pillar 3 Research §5.

Five certified reference individuals covering all MC1R diplotype classes.

Sources:
  - Sulem et al. (2007) Nat Genet — MC1R red hair GWAS (R/R, R/r cohorts)
  - Sulem et al. (2008) Nat Genet — Ephelides GWAS (ASIP, BNC2 modifier validation)
  - Valverde et al. (1995) Nat Genet — Original RHC classification
  - Fitzpatrick (1988) — Skin phototype to MED mapping
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class MC1RReferenceStandard:
    """Certified reference standard for MC1R-UV validation."""
    standard_id: str
    sample_name: str
    population: str
    description: str
    # Input genotypes
    snp_dosages: Dict[str, int]
    # Expected MC1R diplotype
    expected_diplotype: str
    expected_functional_class: str
    expected_w_mc1r_min: float
    expected_w_mc1r_max: float
    expected_n_R: int
    expected_n_r: int
    # Expected freckling
    expected_f_score_min: float
    expected_f_score_max: float
    expected_intensity_contains: str
    # Expected UV / MED
    expected_med_contains: str
    expected_tanning: str


FRECKLING_STANDARDS: Dict[str, MC1RReferenceStandard] = {

    # STD-MC1R-01: Wild-Type Baseline
    # All dosages = 0 → wt/wt, W=0, F_score = 100/(1+exp(2.5)) = 7.59%
    "WT_BASELINE": MC1RReferenceStandard(
        standard_id="STD-MC1R-01",
        sample_name="WT_BASELINE_ZERO_DOSAGE",
        population="Baseline Reference (No MC1R Variants)",
        description="VECTOR_15_FRECKLE_A: Wild-type baseline. W_MC1R=0, F_score=7.59%, MED > 50 mJ/cm².",
        snp_dosages={},
        expected_diplotype="wt/wt",
        expected_functional_class="WILD_TYPE",
        expected_w_mc1r_min=0.0,
        expected_w_mc1r_max=0.001,
        expected_n_R=0,
        expected_n_r=0,
        expected_f_score_min=7.40,
        expected_f_score_max=7.80,
        expected_intensity_contains="MINIMAL",
        expected_med_contains="> 50",
        expected_tanning="NORMAL_TAN_RARE_BURN",
    ),

    # STD-MC1R-02: R151C Homozygous (R/R) — Sulem 2007 Red Hair Celtic
    # rs1805007 = 2 (R151C homozygous) → n_R=2, W=5.70, F_score ≈ 99.45%
    "R151C_HOM_RED": MC1RReferenceStandard(
        standard_id="STD-MC1R-02",
        sample_name="R151C_HOMOZYGOUS_CELTIC_RED",
        population="Celtic European — Red Hair",
        description="VECTOR_15_FRECKLE_B: R151C homozygous. W=5.70, diplotype R/R, F_score≥99%, MED<20.",
        snp_dosages={"rs1805007": 2},
        expected_diplotype="R/R",
        expected_functional_class="SEVERE_LOSS",
        expected_w_mc1r_min=5.69,
        expected_w_mc1r_max=5.71,    # exactly 5.70
        expected_n_R=2,
        expected_n_r=0,
        expected_f_score_min=99.0,
        expected_f_score_max=100.0,
        expected_intensity_contains="DENSE",
        expected_med_contains="< 20",
        expected_tanning="NEVER_TANS_ALWAYS_BURNS",
    ),

    # STD-MC1R-03: R151C (R) + V60L (r) — Compound Heterozygous
    # rs1805007=1 (R151C, R class, w=2.85) + rs1805005=1 (V60L, r class, w=1.10)
    # W = 3.95, diplotype R/r
    # F_score = 100/(1+exp(-(-2.5+1.35*3.95))) = 100/(1+exp(-2.8325)) = 94.44%
    "R151C_V60L_COMPOUND": MC1RReferenceStandard(
        standard_id="STD-MC1R-03",
        sample_name="R151C_V60L_COMPOUND_HET",
        population="Northern European — Compound Heterozygous",
        description="VECTOR_15_FRECKLE_C: R/r compound heterozygous. W=3.95, F_score=94.44%.",
        snp_dosages={"rs1805007": 1, "rs1805005": 1},
        expected_diplotype="R/r",
        expected_functional_class="MODERATE_LOSS",
        expected_w_mc1r_min=3.94,
        expected_w_mc1r_max=3.96,    # exactly 3.95
        expected_n_R=1,
        expected_n_r=1,
        expected_f_score_min=94.0,
        expected_f_score_max=95.0,
        expected_intensity_contains="DENSE",
        expected_med_contains="20 - 35",
        expected_tanning="RARE_TAN_FREQUENT_BURN",
    ),

    # STD-MC1R-04: V60L Homozygous (r/r) — Mild Loss
    # rs1805005=2 → n_r=2, W=2.20
    # F_score = 100/(1+exp(-(-2.5+1.35*2.2))) = 100/(1+exp(-0.47)) = 61.54%
    "V60L_HOM_MILD": MC1RReferenceStandard(
        standard_id="STD-MC1R-04",
        sample_name="V60L_HOMOZYGOUS_MILD_LOSS",
        population="European — Mild MC1R Loss",
        description="VECTOR_15_FRECKLE_D: V60L homozygous r/r. W=2.20, F_score=61.54%, MED 35-50.",
        snp_dosages={"rs1805005": 2},
        expected_diplotype="r/r",
        expected_functional_class="MILD_LOSS",
        expected_w_mc1r_min=2.19,
        expected_w_mc1r_max=2.21,   # exactly 2.20
        expected_n_R=0,
        expected_n_r=2,
        expected_f_score_min=61.0,
        expected_f_score_max=62.5,
        expected_intensity_contains="MODERATE",
        expected_med_contains="35 - 50",
        expected_tanning="MILD_TAN_OCCASIONAL_BURN",
    ),

    # STD-MC1R-05: ASIP + BNC2 Epistatic Boosting (no MC1R variants)
    # rs1015362=2 + rs10756819=2 → W_MC1R=0, X_ASIP=2, X_BNC2=2
    # logit = -2.50 + 0 + 0.85*2 + 0.65*2 = -2.5+1.7+1.3 = 0.50
    # F_score = 100/(1+exp(-0.50)) = 62.25%
    "ASIP_BNC2_EPISTATIC": MC1RReferenceStandard(
        standard_id="STD-MC1R-05",
        sample_name="ASIP_BNC2_HOMOZYGOUS_BOOST",
        population="Reference — ASIP+BNC2 Epistatic Modifier",
        description="VECTOR_15_FRECKLE_F: Pure ASIP+BNC2 epistatic boost. W=0, F_score=62.25%.",
        snp_dosages={"rs1015362": 2, "rs10756819": 2},
        expected_diplotype="wt/wt",
        expected_functional_class="WILD_TYPE",
        expected_w_mc1r_min=0.0,
        expected_w_mc1r_max=0.001,
        expected_n_R=0,
        expected_n_r=0,
        expected_f_score_min=62.0,
        expected_f_score_max=62.5,
        expected_intensity_contains="MODERATE",
        expected_med_contains="> 50",
        expected_tanning="NORMAL_TAN_RARE_BURN",
    ),
}
