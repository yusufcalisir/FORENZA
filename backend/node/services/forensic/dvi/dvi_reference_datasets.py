"""
FORENZA Interpol Disaster Victim Identification (DVI) Reference Datasets & Casework Cohorts (Module 2.4).
Interpol DVI Standard Pedigrees, Certified Golden Vectors, and Mass Disaster Scenarios.

Research Source: research/pillar_2_lineage_kinship_research.md §4.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any


class DviPedigreeTemplateType(str, Enum):
    DIRECT_AM = "DIRECT_AM"
    TRIO_PARENTS = "TRIO_PARENTS"
    DEFICIENCY_DUO = "DEFICIENCY_DUO"
    FULL_SIBLINGS = "FULL_SIBLINGS"


@dataclass(frozen=True)
class DviPedigreeTemplate:
    template_id: DviPedigreeTemplateType
    name: str
    description: str
    required_am_members: List[str]
    expected_min_autosomal_lr: float


@dataclass(frozen=True)
class DviCaseworkCohort:
    cohort_id: str
    name: str
    pedigree_type: DviPedigreeTemplateType
    description: str
    autosomal_lr: float
    ystr_p_upper: float
    mtdna_p_upper: float
    snp_lr: float
    has_ystr: bool
    has_mtdna: bool
    has_snp: bool
    expected_joint_lr: float
    expected_log10_lr: float
    expected_tier: str
    prior_probability: float
    expected_min_w: float


# ── 1. Interpol DVI Reference Standard Pedigrees ─────────────────────────────

DVI_PEDIGREE_TEMPLATES: Dict[DviPedigreeTemplateType, DviPedigreeTemplate] = {
    DviPedigreeTemplateType.DIRECT_AM: DviPedigreeTemplate(
        template_id=DviPedigreeTemplateType.DIRECT_AM,
        name="Direct Ante-Mortem Reference Standard",
        description="Victim compared directly against confirmed personal item (toothbrush, comb, biopsy).",
        required_am_members=["PERSONAL_ITEM_AM"],
        expected_min_autosomal_lr=1.0e15,
    ),
    DviPedigreeTemplateType.TRIO_PARENTS: DviPedigreeTemplate(
        template_id=DviPedigreeTemplateType.TRIO_PARENTS,
        name="Biological Parents Trio (Missing Child)",
        description="Biological Mother and Father typed to identify an unidentified child.",
        required_am_members=["BIOLOGICAL_MOTHER", "BIOLOGICAL_FATHER"],
        expected_min_autosomal_lr=1.0e6,
    ),
    DviPedigreeTemplateType.DEFICIENCY_DUO: DviPedigreeTemplate(
        template_id=DviPedigreeTemplateType.DEFICIENCY_DUO,
        name="Single Parent Deficiency Duo (Missing Father / Mother)",
        description="Mother and known Child typed to reconstruct missing father.",
        required_am_members=["KNOWN_PARENT", "KNOWN_CHILD"],
        expected_min_autosomal_lr=1.0e4,
    ),
    DviPedigreeTemplateType.FULL_SIBLINGS: DviPedigreeTemplate(
        template_id=DviPedigreeTemplateType.FULL_SIBLINGS,
        name="Full Sibling Kinship Pedigree",
        description="Typed full sibling(s) used for collateral kinship identification.",
        required_am_members=["FULL_SIBLING_1"],
        expected_min_autosomal_lr=1.0e3,
    ),
}


# ── 2. Certified Casework Benchmark Cohorts ──────────────────────────────────

DVI_CASEWORK_COHORTS: Dict[str, DviCaseworkCohort] = {
    "VECTOR_P2_03_DEGRADED_SKELETAL": DviCaseworkCohort(
        cohort_id="VECTOR_P2_03_DEGRADED_SKELETAL",
        name="Golden Benchmark VECTOR_P2_03 (Degraded PM Remains)",
        pedigree_type=DviPedigreeTemplateType.DEFICIENCY_DUO,
        description=(
            "Severely degraded PM skeletal sample with Autosomal LR=5.2e3, Y-STR p=0.0002 (LR=5000), "
            "mtDNA p=0.0001 (LR=10000) yielding Combined LR=2.6e11 (log10=11.4149)."
        ),
        autosomal_lr=5.2e3,
        ystr_p_upper=0.0002,
        mtdna_p_upper=0.0001,
        snp_lr=1.0,
        has_ystr=True,
        has_mtdna=True,
        has_snp=False,
        expected_joint_lr=2.6e11,
        expected_log10_lr=11.4149,
        expected_tier="DEFINITIVE_IDENTIFICATION",
        prior_probability=0.001,
        expected_min_w=0.999999,
    ),
    "BENCHMARK_DIRECT_AM_MATCH": DviCaseworkCohort(
        cohort_id="BENCHMARK_DIRECT_AM_MATCH",
        name="Direct Ante-Mortem Personal Item Reference",
        pedigree_type=DviPedigreeTemplateType.DIRECT_AM,
        description="Full 24-locus autosomal match to ante-mortem toothbrush reference standard.",
        autosomal_lr=4.5e18,
        ystr_p_upper=1.0,
        mtdna_p_upper=1.0,
        snp_lr=1.0,
        has_ystr=False,
        has_mtdna=False,
        has_snp=False,
        expected_joint_lr=4.5e18,
        expected_log10_lr=18.6532,
        expected_tier="DEFINITIVE_IDENTIFICATION",
        prior_probability=0.001,
        expected_min_w=0.999999,
    ),
    "BENCHMARK_TRIO_MISSING_CHILD": DviCaseworkCohort(
        cohort_id="BENCHMARK_TRIO_MISSING_CHILD",
        name="Trio Parents Reconciling Missing Child",
        pedigree_type=DviPedigreeTemplateType.TRIO_PARENTS,
        description="Biological Mother and Father identifying unidentified victim child with high certainty.",
        autosomal_lr=8.7e7,
        ystr_p_upper=1.0,
        mtdna_p_upper=1.0,
        snp_lr=1.0,
        has_ystr=False,
        has_mtdna=False,
        has_snp=False,
        expected_joint_lr=8.7e7,
        expected_log10_lr=7.9395,
        expected_tier="DEFINITIVE_IDENTIFICATION",
        prior_probability=0.001,
        expected_min_w=0.9999,
    ),
    "BENCHMARK_DEGRADED_PM_3_DROPOUTS": DviCaseworkCohort(
        cohort_id="BENCHMARK_DEGRADED_PM_3_DROPOUTS",
        name="Degraded PM Remains with 3 Loci Dropout",
        pedigree_type=DviPedigreeTemplateType.DIRECT_AM,
        description="Victim sample with 3 dropped loci (21 typed loci) resolved cleanly under Bayesian prior.",
        autosomal_lr=1.2e12,
        ystr_p_upper=1.0,
        mtdna_p_upper=1.0,
        snp_lr=1.0,
        has_ystr=False,
        has_mtdna=False,
        has_snp=False,
        expected_joint_lr=1.2e12,
        expected_log10_lr=12.0792,
        expected_tier="DEFINITIVE_IDENTIFICATION",
        prior_probability=0.001,
        expected_min_w=0.999999,
    ),
    "BENCHMARK_UNRELATED_EXCLUSION": DviCaseworkCohort(
        cohort_id="BENCHMARK_UNRELATED_EXCLUSION",
        name="Unrelated Non-Kin Exclusion",
        pedigree_type=DviPedigreeTemplateType.TRIO_PARENTS,
        description="Multiple Mendelian exclusions across 24 loci yielding definitive exclusion LR.",
        autosomal_lr=1.0e-8,
        ystr_p_upper=1.0,
        mtdna_p_upper=1.0,
        snp_lr=1.0,
        has_ystr=False,
        has_mtdna=False,
        has_snp=False,
        expected_joint_lr=1.0e-8,
        expected_log10_lr=-8.0,
        expected_tier="EXCLUSION",
        prior_probability=0.001,
        expected_min_w=0.0,
    ),
}


class DviReferenceDatasets:
    """Service for accessing Interpol DVI reference standards and casework cohorts."""

    @staticmethod
    def list_pedigree_templates() -> List[DviPedigreeTemplate]:
        return list(DVI_PEDIGREE_TEMPLATES.values())

    @staticmethod
    def list_casework_cohorts() -> List[DviCaseworkCohort]:
        return list(DVI_CASEWORK_COHORTS.values())
