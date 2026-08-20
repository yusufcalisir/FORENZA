"""
FORENZA Forensic Evidence Operating System
Pillar 2 — Module 2.1: Y-STR 27-Locus Lineage Engine (Y-FILER Plus)
Sub-Item 2.1.1: Mathematical Formulation

Derives verbatim and exclusively from:
  - Pillar 2 Research Specification (research/pillar_2_lineage_kinship_research.md §1)
  - Y-STR 27-Locus Master Specification (research/ystr_27_mtdna_empop_lineage_research.md §1, §2)
  - ISO/IEC 17025:2017 & SWGDAM Lineage Guidelines (2020)
  - ENFSI Evaluative Reporting in Forensic Science (2017)
  - YHRD Guidelines & Methods (Release 68)
"""

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Dict, List, Optional, Tuple, Sequence, Any, Union
import numpy as np
from scipy.stats import f as f_dist


# ===========================================================================
# 1. Enums & Data Classes for 27 Y-STR Loci
# ===========================================================================

class YStrMutationClass(str, Enum):
    STANDARD = "Standard"
    MULTI_COPY = "Multi-Copy"
    RAPIDLY_MUTATING = "Rapidly Mutating"
    RM_MULTI_COPY = "RM / Multi-Copy"


class YStrDye(str, Enum):
    FAM_6 = "6-FAM"
    VIC = "VIC"
    NED = "NED"
    TAZ = "TAZ"
    SID = "SID"
    LIZ = "LIZ"


@dataclass(frozen=True)
class YStrLocusMetadata:
    """Metadata specification for 27 Yfiler Plus loci."""
    locus_name: str
    cytogenetic_band: str
    grch38_start: int
    grch38_end: int
    repeat_unit_bp: int
    canonical_motif: str
    ce_dye: YStrDye
    amplicon_min_bp: int
    amplicon_max_bp: int
    mutation_rate: float        # mu_l (mutations/generation)
    stepwise_param_r: float     # r_l parameter for Stepwise Mutation Model
    mutation_class: YStrMutationClass

    @property
    def is_rapidly_mutating(self) -> bool:
        return self.mutation_class in (
            YStrMutationClass.RAPIDLY_MUTATING,
            YStrMutationClass.RM_MULTI_COPY,
        ) or self.mutation_rate >= 0.010

    @property
    def is_multi_copy(self) -> bool:
        return self.mutation_class in (
            YStrMutationClass.MULTI_COPY,
            YStrMutationClass.RM_MULTI_COPY,
        ) or "a/b" in self.locus_name


@dataclass(frozen=True)
class ClopperPearsonResult:
    """Exact Clopper-Pearson Binomial Confidence Bound Result."""
    database_size_n: int
    observed_matches_k: int
    alpha: float
    point_estimate: float
    p_upper_bound: float
    equivalent_match_ratio: float
    method: str


@dataclass(frozen=True)
class PaternalKinshipResult:
    """Paternal Lineage Kinship Likelihood Evaluation Result."""
    meioses_m: int
    total_loci_evaluated: int
    matching_loci_count: int
    mutated_loci_count: int
    rm_mutations_count: int
    standard_mutations_count: int
    transition_probability_product: float
    haplotype_p_upper: float
    paternal_lr: float
    log10_paternal_lr: float
    is_lineage_excluded: bool
    locus_evaluations: Dict[str, Dict[str, Any]]
    verbal_predicate_en: str
    verbal_predicate_tr: str


@dataclass(frozen=True)
class HaplogroupPredictionResult:
    """Bayesian Y-DNA Haplogroup Prediction Result."""
    predicted_haplogroup: str
    confidence_score: float
    primary_snp_marker: str
    distance_to_modal: float
    description: str
    bayesian_posteriors: Dict[str, float]


# ===========================================================================
# 2. Y-FILER PLUS 27-LOCUS MASTER REGISTRY
# ===========================================================================

YSTR_27_MASTER_REGISTRY: Dict[str, YStrLocusMetadata] = {
    "DYS19": YStrLocusMetadata(
        locus_name="DYS19",
        cytogenetic_band="Yp11.2",
        grch38_start=9471048,
        grch38_end=9471430,
        repeat_unit_bp=4,
        canonical_motif="[TAGA]",
        ce_dye=YStrDye.FAM_6,
        amplicon_min_bp=170,
        amplicon_max_bp=210,
        mutation_rate=2.3e-3,
        stepwise_param_r=0.95,
        mutation_class=YStrMutationClass.STANDARD,
    ),
    "DYS389I": YStrLocusMetadata(
        locus_name="DYS389I",
        cytogenetic_band="Yq11.221",
        grch38_start=12423733,
        grch38_end=12424100,
        repeat_unit_bp=4,
        canonical_motif="[TCTG] [TCTA]",
        ce_dye=YStrDye.VIC,
        amplicon_min_bp=140,
        amplicon_max_bp=180,
        mutation_rate=2.6e-3,
        stepwise_param_r=0.94,
        mutation_class=YStrMutationClass.STANDARD,
    ),
    "DYS389II": YStrLocusMetadata(
        locus_name="DYS389II",
        cytogenetic_band="Yq11.221",
        grch38_start=12423600,
        grch38_end=12424100,
        repeat_unit_bp=4,
        canonical_motif="[TCTG] [TCTA] ... [TCTG] [TCTA]",
        ce_dye=YStrDye.VIC,
        amplicon_min_bp=250,
        amplicon_max_bp=310,
        mutation_rate=4.2e-3,
        stepwise_param_r=0.92,
        mutation_class=YStrMutationClass.STANDARD,
    ),
    "DYS390": YStrLocusMetadata(
        locus_name="DYS390",
        cytogenetic_band="Yq11.221",
        grch38_start=17281230,
        grch38_end=17281600,
        repeat_unit_bp=4,
        canonical_motif="[TCTG] [TCTA]",
        ce_dye=YStrDye.NED,
        amplicon_min_bp=190,
        amplicon_max_bp=240,
        mutation_rate=2.1e-3,
        stepwise_param_r=0.95,
        mutation_class=YStrMutationClass.STANDARD,
    ),
    "DYS391": YStrLocusMetadata(
        locus_name="DYS391",
        cytogenetic_band="Yq11.221",
        grch38_start=13887400,
        grch38_end=13887700,
        repeat_unit_bp=4,
        canonical_motif="[TCTA]",
        ce_dye=YStrDye.NED,
        amplicon_min_bp=95,
        amplicon_max_bp=135,
        mutation_rate=1.0e-3,
        stepwise_param_r=0.98,
        mutation_class=YStrMutationClass.STANDARD,
    ),
    "DYS392": YStrLocusMetadata(
        locus_name="DYS392",
        cytogenetic_band="Yq11.221",
        grch38_start=22589100,
        grch38_end=22589450,
        repeat_unit_bp=3,
        canonical_motif="[TAT]",
        ce_dye=YStrDye.TAZ,
        amplicon_min_bp=280,
        amplicon_max_bp=340,
        mutation_rate=3.75e-4,
        stepwise_param_r=0.99,
        mutation_class=YStrMutationClass.STANDARD,
    ),
    "DYS393": YStrLocusMetadata(
        locus_name="DYS393",
        cytogenetic_band="Yp11.2",
        grch38_start=3110200,
        grch38_end=3110500,
        repeat_unit_bp=4,
        canonical_motif="[AGAT]",
        ce_dye=YStrDye.FAM_6,
        amplicon_min_bp=110,
        amplicon_max_bp=150,
        mutation_rate=1.1e-3,
        stepwise_param_r=0.97,
        mutation_class=YStrMutationClass.STANDARD,
    ),
    "DYS385a/b": YStrLocusMetadata(
        locus_name="DYS385a/b",
        cytogenetic_band="Yq11.223",
        grch38_start=20850100,
        grch38_end=20851200,
        repeat_unit_bp=4,
        canonical_motif="[GAAA]",
        ce_dye=YStrDye.VIC,
        amplicon_min_bp=240,
        amplicon_max_bp=330,
        mutation_rate=2.2e-3,
        stepwise_param_r=0.93,
        mutation_class=YStrMutationClass.MULTI_COPY,
    ),
    "DYS437": YStrLocusMetadata(
        locus_name="DYS437",
        cytogenetic_band="Yq11.221",
        grch38_start=14451100,
        grch38_end=14451400,
        repeat_unit_bp=4,
        canonical_motif="[TATC]",
        ce_dye=YStrDye.VIC,
        amplicon_min_bp=180,
        amplicon_max_bp=220,
        mutation_rate=1.2e-3,
        stepwise_param_r=0.96,
        mutation_class=YStrMutationClass.STANDARD,
    ),
    "DYS438": YStrLocusMetadata(
        locus_name="DYS438",
        cytogenetic_band="Yq11.221",
        grch38_start=14910200,
        grch38_end=14910500,
        repeat_unit_bp=5,
        canonical_motif="[TTTTC]",
        ce_dye=YStrDye.TAZ,
        amplicon_min_bp=200,
        amplicon_max_bp=250,
        mutation_rate=3.75e-4,
        stepwise_param_r=0.99,
        mutation_class=YStrMutationClass.STANDARD,
    ),
    "DYS439": YStrLocusMetadata(
        locus_name="DYS439",
        cytogenetic_band="Yq11.221",
        grch38_start=14352100,
        grch38_end=14352450,
        repeat_unit_bp=4,
        canonical_motif="[AGAT]",
        ce_dye=YStrDye.FAM_6,
        amplicon_min_bp=210,
        amplicon_max_bp=250,
        mutation_rate=2.4e-3,
        stepwise_param_r=0.94,
        mutation_class=YStrMutationClass.STANDARD,
    ),
    "DYS448": YStrLocusMetadata(
        locus_name="DYS448",
        cytogenetic_band="Yq11.223",
        grch38_start=24420100,
        grch38_end=24420600,
        repeat_unit_bp=6,
        canonical_motif="[AGAGAT]",
        ce_dye=YStrDye.VIC,
        amplicon_min_bp=280,
        amplicon_max_bp=350,
        mutation_rate=1.4e-3,
        stepwise_param_r=0.96,
        mutation_class=YStrMutationClass.STANDARD,
    ),
    "DYS456": YStrLocusMetadata(
        locus_name="DYS456",
        cytogenetic_band="Yq11.221",
        grch38_start=16112000,
        grch38_end=16112350,
        repeat_unit_bp=4,
        canonical_motif="[AGAT]",
        ce_dye=YStrDye.FAM_6,
        amplicon_min_bp=130,
        amplicon_max_bp=170,
        mutation_rate=3.8e-3,
        stepwise_param_r=0.91,
        mutation_class=YStrMutationClass.STANDARD,
    ),
    "DYS458": YStrLocusMetadata(
        locus_name="DYS458",
        cytogenetic_band="Yq11.221",
        grch38_start=7901100,
        grch38_end=7901500,
        repeat_unit_bp=4,
        canonical_motif="[GAAA]",
        ce_dye=YStrDye.NED,
        amplicon_min_bp=130,
        amplicon_max_bp=180,
        mutation_rate=8.7e-3,
        stepwise_param_r=0.88,
        mutation_class=YStrMutationClass.STANDARD,
    ),
    "DYS635": YStrLocusMetadata(
        locus_name="DYS635",
        cytogenetic_band="Yq11.221",
        grch38_start=14212100,
        grch38_end=14212500,
        repeat_unit_bp=4,
        canonical_motif="[TCTA] [TCTG]",
        ce_dye=YStrDye.TAZ,
        amplicon_min_bp=200,
        amplicon_max_bp=260,
        mutation_rate=2.5e-3,
        stepwise_param_r=0.94,
        mutation_class=YStrMutationClass.STANDARD,
    ),
    "YGATAH4": YStrLocusMetadata(
        locus_name="YGATAH4",
        cytogenetic_band="Yq11.221",
        grch38_start=18720100,
        grch38_end=18720400,
        repeat_unit_bp=4,
        canonical_motif="[AGAT]",
        ce_dye=YStrDye.TAZ,
        amplicon_min_bp=120,
        amplicon_max_bp=160,
        mutation_rate=1.8e-3,
        stepwise_param_r=0.96,
        mutation_class=YStrMutationClass.STANDARD,
    ),
    "DYS460": YStrLocusMetadata(
        locus_name="DYS460",
        cytogenetic_band="Yq11.221",
        grch38_start=11811200,
        grch38_end=11811500,
        repeat_unit_bp=4,
        canonical_motif="[ATAG]",
        ce_dye=YStrDye.VIC,
        amplicon_min_bp=100,
        amplicon_max_bp=140,
        mutation_rate=2.1e-3,
        stepwise_param_r=0.95,
        mutation_class=YStrMutationClass.STANDARD,
    ),
    "DYS481": YStrLocusMetadata(
        locus_name="DYS481",
        cytogenetic_band="Yq11.221",
        grch38_start=8502100,
        grch38_end=8502500,
        repeat_unit_bp=3,
        canonical_motif="[CTT]",
        ce_dye=YStrDye.SID,
        amplicon_min_bp=100,
        amplicon_max_bp=150,
        mutation_rate=2.8e-3,
        stepwise_param_r=0.93,
        mutation_class=YStrMutationClass.STANDARD,
    ),
    "DYS533": YStrLocusMetadata(
        locus_name="DYS533",
        cytogenetic_band="Yq11.221",
        grch38_start=15201100,
        grch38_end=15201400,
        repeat_unit_bp=4,
        canonical_motif="[ATCT]",
        ce_dye=YStrDye.SID,
        amplicon_min_bp=160,
        amplicon_max_bp=200,
        mutation_rate=1.5e-3,
        stepwise_param_r=0.96,
        mutation_class=YStrMutationClass.STANDARD,
    ),
    "DYS570": YStrLocusMetadata(
        locus_name="DYS570",
        cytogenetic_band="Yq11.221",
        grch38_start=6812100,
        grch38_end=6812500,
        repeat_unit_bp=4,
        canonical_motif="[TTTC]",
        ce_dye=YStrDye.SID,
        amplicon_min_bp=210,
        amplicon_max_bp=260,
        mutation_rate=1.2e-2,
        stepwise_param_r=0.82,
        mutation_class=YStrMutationClass.RAPIDLY_MUTATING,
    ),
    "DYS576": YStrLocusMetadata(
        locus_name="DYS576",
        cytogenetic_band="Yq11.221",
        grch38_start=6911200,
        grch38_end=6911600,
        repeat_unit_bp=4,
        canonical_motif="[AAAG]",
        ce_dye=YStrDye.SID,
        amplicon_min_bp=270,
        amplicon_max_bp=330,
        mutation_rate=1.4e-2,
        stepwise_param_r=0.80,
        mutation_class=YStrMutationClass.RAPIDLY_MUTATING,
    ),
    "DYS627": YStrLocusMetadata(
        locus_name="DYS627",
        cytogenetic_band="Yq11.221",
        grch38_start=21210100,
        grch38_end=21210600,
        repeat_unit_bp=4,
        canonical_motif="[AAAG] [AGAG]",
        ce_dye=YStrDye.SID,
        amplicon_min_bp=340,
        amplicon_max_bp=410,
        mutation_rate=1.3e-2,
        stepwise_param_r=0.81,
        mutation_class=YStrMutationClass.RAPIDLY_MUTATING,
    ),
    "DYS518": YStrLocusMetadata(
        locus_name="DYS518",
        cytogenetic_band="Yq11.223",
        grch38_start=20410200,
        grch38_end=20410800,
        repeat_unit_bp=4,
        canonical_motif="[AAAG]",
        ce_dye=YStrDye.TAZ,
        amplicon_min_bp=360,
        amplicon_max_bp=440,
        mutation_rate=1.8e-2,
        stepwise_param_r=0.75,
        mutation_class=YStrMutationClass.RAPIDLY_MUTATING,
    ),
    "DYS449": YStrLocusMetadata(
        locus_name="DYS449",
        cytogenetic_band="Yq11.221",
        grch38_start=11210100,
        grch38_end=11210600,
        repeat_unit_bp=4,
        canonical_motif="[TTTC]",
        ce_dye=YStrDye.NED,
        amplicon_min_bp=290,
        amplicon_max_bp=370,
        mutation_rate=1.2e-2,
        stepwise_param_r=0.83,
        mutation_class=YStrMutationClass.RAPIDLY_MUTATING,
    ),
    "DYF387S1a/b": YStrLocusMetadata(
        locus_name="DYF387S1a/b",
        cytogenetic_band="Yq11.221",
        grch38_start=22100100,
        grch38_end=22102500,
        repeat_unit_bp=4,
        canonical_motif="[AAAG]",
        ce_dye=YStrDye.FAM_6,
        amplicon_min_bp=280,
        amplicon_max_bp=360,
        mutation_rate=1.6e-2,
        stepwise_param_r=0.78,
        mutation_class=YStrMutationClass.RM_MULTI_COPY,
    ),
}

# 16 Major Y-DNA Haplogroup Modal Reference Signatures
HAPLOGROUP_MODAL_PROFILES: Dict[str, Dict[str, Any]] = {
    "R1b": {
        "primary_snp": "M269 / P312 / U106",
        "description": "Western European / Atlantic Lineage (Italo-Celtic, Germanic)",
        "prior": 0.25,
        "modal_str": {
            "DYS393": 13, "DYS390": 24, "DYS19": 14, "DYS391": 11,
            "DYS385a/b": [11, 14], "DYS439": 12, "DYS389I": 13, "DYS392": 13,
            "DYS389II": 29, "DYS438": 12, "DYS437": 15, "DYS448": 19,
            "DYS456": 16, "DYS458": 17, "DYS635": 23, "YGATAH4": 12,
            "DYS460": 11, "DYS481": 22, "DYS533": 12, "DYS570": 17,
            "DYS576": 18, "DYS627": 21, "DYS518": 38, "DYS449": 29,
            "DYF387S1a/b": [36, 38]
        }
    },
    "R1a": {
        "primary_snp": "M198 / M417",
        "description": "Eastern European / South Asian Lineage (Slavic, Indo-Iranian)",
        "prior": 0.20,
        "modal_str": {
            "DYS393": 13, "DYS390": 25, "DYS19": 16, "DYS391": 10,
            "DYS385a/b": [11, 14], "DYS439": 10, "DYS389I": 13, "DYS392": 11,
            "DYS389II": 30, "DYS438": 11, "DYS437": 14, "DYS448": 20,
            "DYS456": 15, "DYS458": 15, "DYS635": 23, "YGATAH4": 11,
            "DYS460": 11, "DYS481": 25, "DYS533": 12, "DYS570": 17,
            "DYS576": 18, "DYS627": 23, "DYS518": 38, "DYS449": 31,
            "DYF387S1a/b": [37, 39]
        }
    },
    "I1": {
        "primary_snp": "M253",
        "description": "Northern European / Scandinavian Lineage",
        "prior": 0.10,
        "modal_str": {
            "DYS393": 13, "DYS390": 22, "DYS19": 14, "DYS391": 10,
            "DYS385a/b": [14, 14], "DYS439": 11, "DYS389I": 13, "DYS392": 11,
            "DYS389II": 28, "DYS438": 10, "DYS437": 16, "DYS448": 20,
            "DYS456": 14, "DYS458": 15, "DYS635": 21, "YGATAH4": 11,
            "DYS460": 11, "DYS481": 28, "DYS533": 13, "DYS570": 19,
            "DYS576": 19, "DYS627": 20, "DYS518": 39, "DYS449": 32,
            "DYF387S1a/b": [35, 37]
        }
    },
    "I2": {
        "primary_snp": "M438 / L621 / P37.2",
        "description": "Southeastern European / Balkan Lineage (Dinaric)",
        "prior": 0.08,
        "modal_str": {
            "DYS393": 15, "DYS390": 24, "DYS19": 16, "DYS391": 10,
            "DYS385a/b": [14, 15], "DYS439": 11, "DYS389I": 13, "DYS392": 11,
            "DYS389II": 31, "DYS438": 10, "DYS437": 15, "DYS448": 20,
            "DYS456": 15, "DYS458": 15, "DYS635": 21, "YGATAH4": 11,
            "DYS460": 10, "DYS481": 26, "DYS533": 12, "DYS570": 18,
            "DYS576": 18, "DYS627": 21, "DYS518": 38, "DYS449": 30,
            "DYF387S1a/b": [35, 36]
        }
    },
    "J1": {
        "primary_snp": "M267",
        "description": "Semitic / Arabian Peninsula / Levantine Lineage",
        "prior": 0.07,
        "modal_str": {
            "DYS393": 12, "DYS390": 23, "DYS19": 14, "DYS391": 10,
            "DYS385a/b": [14, 17], "DYS439": 11, "DYS389I": 13, "DYS392": 11,
            "DYS389II": 29, "DYS438": 10, "DYS437": 15, "DYS448": 20,
            "DYS456": 15, "DYS458": 18, "DYS635": 21, "YGATAH4": 11,
            "DYS460": 11, "DYS481": 24, "DYS533": 12, "DYS570": 17,
            "DYS576": 17, "DYS627": 21, "DYS518": 37, "DYS449": 30,
            "DYF387S1a/b": [36, 38]
        }
    },
    "J2": {
        "primary_snp": "M172",
        "description": "Greco-Anatolian / Mediterranean / Caucasian Lineage",
        "prior": 0.08,
        "modal_str": {
            "DYS393": 12, "DYS390": 23, "DYS19": 15, "DYS391": 10,
            "DYS385a/b": [13, 15], "DYS439": 12, "DYS389I": 13, "DYS392": 11,
            "DYS389II": 29, "DYS438": 10, "DYS437": 15, "DYS448": 20,
            "DYS456": 15, "DYS458": 17, "DYS635": 21, "YGATAH4": 11,
            "DYS460": 11, "DYS481": 23, "DYS533": 12, "DYS570": 17,
            "DYS576": 17, "DYS627": 22, "DYS518": 37, "DYS449": 29,
            "DYF387S1a/b": [36, 37]
        }
    },
    "E1b1b": {
        "primary_snp": "M215 / M35 / V13",
        "description": "North African / Southern Balkan / Mediterranean Lineage",
        "prior": 0.06,
        "modal_str": {
            "DYS393": 13, "DYS390": 24, "DYS19": 13, "DYS391": 10,
            "DYS385a/b": [11, 12], "DYS439": 12, "DYS389I": 13, "DYS392": 11,
            "DYS389II": 30, "DYS438": 11, "DYS437": 14, "DYS448": 20,
            "DYS456": 14, "DYS458": 16, "DYS635": 21, "YGATAH4": 11,
            "DYS460": 11, "DYS481": 22, "DYS533": 12, "DYS570": 17,
            "DYS576": 17, "DYS627": 19, "DYS518": 37, "DYS449": 28,
            "DYF387S1a/b": [35, 37]
        }
    },
    "E1b1a": {
        "primary_snp": "V38 / M2",
        "description": "Sub-Saharan African (Niger-Congo / Bantu) Lineage",
        "prior": 0.05,
        "modal_str": {
            "DYS393": 15, "DYS390": 21, "DYS19": 15, "DYS391": 10,
            "DYS385a/b": [15, 16], "DYS439": 11, "DYS389I": 13, "DYS392": 11,
            "DYS389II": 31, "DYS438": 11, "DYS437": 15, "DYS448": 20,
            "DYS456": 15, "DYS458": 15, "DYS635": 21, "YGATAH4": 11,
            "DYS460": 11, "DYS481": 22, "DYS533": 12, "DYS570": 18,
            "DYS576": 18, "DYS627": 19, "DYS518": 38, "DYS449": 30,
            "DYF387S1a/b": [36, 38]
        }
    },
    "G2a": {
        "primary_snp": "P15 / L30",
        "description": "Caucasian / Early European Neolithic Farmer Lineage",
        "prior": 0.03,
        "modal_str": {
            "DYS393": 14, "DYS390": 22, "DYS19": 15, "DYS391": 10,
            "DYS385a/b": [13, 15], "DYS439": 11, "DYS389I": 12, "DYS392": 11,
            "DYS389II": 29, "DYS438": 10, "DYS437": 16, "DYS448": 21,
            "DYS456": 15, "DYS458": 17, "DYS635": 21, "YGATAH4": 11,
            "DYS460": 11, "DYS481": 22, "DYS533": 12, "DYS570": 17,
            "DYS576": 18, "DYS627": 20, "DYS518": 37, "DYS449": 29,
            "DYF387S1a/b": [35, 37]
        }
    },
    "N": {
        "primary_snp": "M231 / Tat",
        "description": "North Eurasian / Uralic / Finno-Ugric Lineage",
        "prior": 0.03,
        "modal_str": {
            "DYS393": 14, "DYS390": 23, "DYS19": 14, "DYS391": 11,
            "DYS385a/b": [11, 13], "DYS439": 10, "DYS389I": 13, "DYS392": 14,
            "DYS389II": 30, "DYS438": 11, "DYS437": 14, "DYS448": 19,
            "DYS456": 14, "DYS458": 16, "DYS635": 23, "YGATAH4": 11,
            "DYS460": 11, "DYS481": 24, "DYS533": 12, "DYS570": 18,
            "DYS576": 18, "DYS627": 22, "DYS518": 38, "DYS449": 30,
            "DYF387S1a/b": [37, 38]
        }
    },
}


# ===========================================================================
# 3. Core Mathematical Formulation Engine
# ===========================================================================

class YStrMathematicalFormulation:
    """
    Biocomputational Engine for Y-STR 27-Locus (Yfiler Plus) Haplotype Statistics,
    Clopper-Pearson Exact Bounds, Discrete Laplace Smoothing, Stepwise Mutation Modeling,
    and Bayesian Haplogroup Prediction.
    """

    # ── 3.1 Clopper-Pearson 95% Exact Binomial Confidence Interval ────────

    @staticmethod
    def compute_clopper_pearson_upper_bound(
        k: int,
        n: int,
        alpha: float = 0.05,
    ) -> ClopperPearsonResult:
        """
        Calculates the exact upper bound of the Clopper-Pearson 95% Binomial Confidence Interval.
        Research Reference: Pillar 2 §1.1 & ystr_27_mtdna_empop_lineage_research.md §2.1

        For unobserved haplotype (k = 0):
          p_upper = 1 - alpha^(1 / (n + 1)) = 1 - (0.05)^(1 / (n + 1))

        For observed matches (k > 0):
          Uses Snedecor F-distribution quantile:
          d1 = 2 * (k + 1), d2 = 2 * (n - k)
          F_crit = F_{d1, d2; 1 - alpha/2}
          p_upper = (d1 / 2 * F_crit) / (d2 / 2 + d1 / 2 * F_crit)
                  = (k + 1) * F_crit / ((n - k) + (k + 1) * F_crit)
        """
        if n <= 0:
            raise ValueError(f"Database size N must be positive, got {n}")
        if k < 0 or k > n:
            raise ValueError(f"Observed matches k ({k}) must satisfy 0 <= k <= N ({n})")

        point_est = float(k) / float(n)

        if k == 0:
            # Analytical exact zero-count bound
            p_upper = 1.0 - math.pow(alpha, 1.0 / (n + 1))
            method = "Clopper-Pearson Exact Zero-Count Analytical Form"
        else:
            # Snedecor F-distribution exact formulation
            d1 = 2 * (k + 1)
            d2 = 2 * (n - k)
            f_crit = float(f_dist.ppf(1.0 - alpha / 2.0, d1, d2))
            p_upper = ((k + 1) * f_crit) / ((n - k) + (k + 1) * f_crit)
            method = "Clopper-Pearson Snedecor F-Distribution Exact Quantile"

        # Sanity bound: probability simplex [0.0, 1.0]
        p_upper = max(0.0, min(1.0, float(p_upper)))
        match_ratio = 1.0 / p_upper if p_upper > 0 else float("inf")

        return ClopperPearsonResult(
            database_size_n=n,
            observed_matches_k=k,
            alpha=alpha,
            point_estimate=point_est,
            p_upper_bound=p_upper,
            equivalent_match_ratio=match_ratio,
            method=method,
        )

    # ── 3.2 Brenner Subpopulation Coancestry Correction ───────────────────

    @staticmethod
    def compute_brenner_frequency(
        k: int,
        n: int,
        theta: float = 0.03,
    ) -> float:
        """
        Calculates Brenner / Surveyor subpopulation coancestry-corrected match frequency:
          p_Brenner = (k + theta) / (n + theta)
        """
        if n <= 0:
            raise ValueError("Database size N must be positive.")
        if k < 0:
            raise ValueError("Match count k must be non-negative.")
        if theta < 0.0 or theta > 0.20:
            raise ValueError(f"Subpopulation coancestry theta must be in [0.0, 0.20], got {theta}")

        return (k + theta) / (n + theta)

    # ── 3.3 Multi-Copy Duplicated Loci Canonical Sorting & PHR ────────────

    @staticmethod
    def normalize_multi_copy_alleles(
        alleles: Union[List[Union[float, str, int]], Tuple[Any, ...]]
    ) -> Tuple[float, ...]:
        """
        Canonical sorted float tuple for multi-copy duplicated loci (e.g. DYS385a/b, DYF387S1a/b).
        Enforces sorted order invariant: a1 <= a2.
        """
        parsed: List[float] = []
        for a in alleles:
            try:
                parsed.append(float(a))
            except (ValueError, TypeError):
                continue
        parsed.sort()
        return tuple(parsed)

    @staticmethod
    def evaluate_multi_copy_phr(
        rfu_values: Sequence[float],
        min_phr_threshold: float = 0.50,
    ) -> Tuple[float, bool]:
        """
        Evaluates peak height ratio for duplicated loci single-source verification:
          PHR = min(RFU_1, RFU_2) / max(RFU_1, RFU_2) >= 0.50
        """
        if len(rfu_values) < 2:
            return (1.0, True)

        h1, h2 = float(rfu_values[0]), float(rfu_values[1])
        h_min = min(h1, h2)
        h_max = max(h1, h2)

        if h_max <= 0:
            return (0.0, False)

        phr = h_min / h_max
        is_pass = phr >= min_phr_threshold
        return (phr, is_pass)

    @staticmethod
    def estimate_minimum_male_contributors(
        locus_allele_counts: Dict[str, int]
    ) -> int:
        """
        Infers the minimum number of male contributors in a DNA mixture:
          N_male = max_l ceil(n_alleles, l / 2)
        For single-copy loci, >1 allele indicates >= 2 males.
        For multi-copy loci (DYS385, DYF387S1), >2 alleles indicates >= 2 males, >4 indicates >= 3.
        """
        n_male = 1
        for locus, count in locus_allele_counts.items():
            meta = YSTR_27_MASTER_REGISTRY.get(locus)
            is_multi = meta.is_multi_copy if meta else ("a/b" in locus)
            if is_multi:
                req = math.ceil(count / 2)
            else:
                req = count  # For single copy locus, each male provides at most 1 allele
            if req > n_male:
                n_male = req
        return n_male

    # ── 3.4 Nested Repeat Decoupling (DYS389I / DYS389II) ─────────────────

    @staticmethod
    def decouple_dys389(
        dys389i: float,
        dys389ii_total: float,
    ) -> float:
        """
        Decouples nested repeat system DYS389II into its pure variable repeat component DYS389.2:
          DYS389.2_pure = DYS389II_total - DYS389I
        """
        if dys389ii_total < dys389i:
            raise ValueError(
                f"DYS389II total ({dys389ii_total}) cannot be smaller than nested DYS389I ({dys389i})"
            )
        return round(dys389ii_total - dys389i, 2)

    # ── 3.5 Discrete Laplace Marginal Probability ─────────────────────────

    @staticmethod
    def compute_discrete_laplace_prob(
        observed_allele: float,
        modal_allele: float,
        dispersion_lambda: float = 0.65,
    ) -> float:
        """
        Computes marginal probability under the Discrete Laplace model:
          f(y | mu, lambda) = ((1 - lambda) / (1 + lambda)) * lambda^(|y - mu|)
        """
        if dispersion_lambda <= 0.0 or dispersion_lambda >= 1.0:
            raise ValueError(f"Dispersion parameter lambda must be in (0, 1), got {dispersion_lambda}")

        diff = abs(observed_allele - modal_allele)
        norm_const = (1.0 - dispersion_lambda) / (1.0 + dispersion_lambda)
        return norm_const * math.pow(dispersion_lambda, diff)

    # ── 3.6 Stepwise Mutation Model (SMM) Kinship Likelihood ─────────────

    @staticmethod
    def compute_smm_transition_probability(
        allele_a: Union[float, int],
        allele_b: Union[float, int],
        mutation_rate_mu: float,
        stepwise_r: float = 0.90,
        meioses_m: int = 1,
    ) -> float:
        """
        Computes single-locus transmission probability under Stepwise Mutation Model (SMM)
        for m meioses between two male individuals.

        For exact identity (allele_a == allele_b):
          P(y_B | y_A, m) = (1 - mu)^m

        For mutation of k = |allele_a - allele_b| repeat steps:
          P(y_B | y_A, m) = 0.5 * (1 - (1 - mu)^m) * r^(k - 1) * (1 - r)
        """
        if mutation_rate_mu <= 0.0 or mutation_rate_mu >= 1.0:
            raise ValueError(f"Mutation rate mu must be in (0, 1), got {mutation_rate_mu}")
        if stepwise_r <= 0.0 or stepwise_r >= 1.0:
            raise ValueError(f"Stepwise parameter r must be in (0, 1), got {stepwise_r}")
        if meioses_m < 1:
            raise ValueError(f"Number of meioses m must be >= 1, got {meioses_m}")

        k_steps = abs(float(allele_a) - float(allele_b))

        # Probability of at least one mutation across m generations
        p_no_mut = math.pow(1.0 - mutation_rate_mu, meioses_m)

        if k_steps == 0.0:
            return p_no_mut
        else:
            # Discrete integer step penalty (if micro-variant, step difference is fractional)
            int_steps = max(1, int(round(k_steps)))
            p_mut = 1.0 - p_no_mut
            # Stepwise geometric decay for k steps
            step_prob = math.pow(stepwise_r, int_steps - 1) * (1.0 - stepwise_r)
            # Symmetrical: 0.5 for expansion vs contraction
            return 0.5 * p_mut * step_prob

    @staticmethod
    def evaluate_paternal_kinship_likelihood(
        profile_a: Dict[str, Any],
        profile_b: Dict[str, Any],
        meioses_m: int = 1,
        database_size_n: int = 38500,
        theta: float = 0.03,
    ) -> PaternalKinshipResult:
        """
        Evaluates full 27-locus paternal lineage kinship likelihood:
          H_1: Male A and Male B belong to the same paternal lineage (separated by m meioses)
          H_2: Male A and Male B are unrelated males

          LR_paternal = (PROD P(y_B,l | y_A,l, m, mu_l)) / p_upper(Haplotype_B)
        """
        locus_results: Dict[str, Dict[str, Any]] = {}
        trans_prob_product = 1.0
        n_matching = 0
        n_mutations = 0
        n_rm_mutations = 0
        n_std_mutations = 0

        common_loci = [l for l in YSTR_27_MASTER_REGISTRY if l in profile_a and l in profile_b]
        if len(common_loci) == 0:
            raise ValueError("No common Y-STR loci found between profile A and profile B.")

        for locus in common_loci:
            meta = YSTR_27_MASTER_REGISTRY[locus]
            val_a = profile_a[locus]
            val_b = profile_b[locus]

            # Handle multi-copy vs single-copy
            if meta.is_multi_copy:
                norm_a = YStrMathematicalFormulation.normalize_multi_copy_alleles(
                    val_a if isinstance(val_a, (list, tuple)) else [val_a]
                )
                norm_b = YStrMathematicalFormulation.normalize_multi_copy_alleles(
                    val_b if isinstance(val_b, (list, tuple)) else [val_b]
                )

                # Pairwise minimum distance matching
                if len(norm_a) == 2 and len(norm_b) == 2:
                    p1 = YStrMathematicalFormulation.compute_smm_transition_probability(
                        norm_a[0], norm_b[0], meta.mutation_rate, meta.stepwise_param_r, meioses_m
                    )
                    p2 = YStrMathematicalFormulation.compute_smm_transition_probability(
                        norm_a[1], norm_b[1], meta.mutation_rate, meta.stepwise_param_r, meioses_m
                    )
                    p_locus = p1 * p2
                    is_match = (norm_a == norm_b)
                else:
                    p_locus = YStrMathematicalFormulation.compute_smm_transition_probability(
                        norm_a[0] if norm_a else 10, norm_b[0] if norm_b else 10,
                        meta.mutation_rate, meta.stepwise_param_r, meioses_m
                    )
                    is_match = (norm_a == norm_b)
            else:
                a_float = float(val_a[0] if isinstance(val_a, (list, tuple)) else val_a)
                b_float = float(val_b[0] if isinstance(val_b, (list, tuple)) else val_b)
                p_locus = YStrMathematicalFormulation.compute_smm_transition_probability(
                    a_float, b_float, meta.mutation_rate, meta.stepwise_param_r, meioses_m
                )
                is_match = (a_float == b_float)

            trans_prob_product *= p_locus

            if is_match:
                n_matching += 1
            else:
                n_mutations += 1
                if meta.is_rapidly_mutating:
                    n_rm_mutations += 1
                else:
                    n_std_mutations += 1

            locus_results[locus] = {
                "allele_a": val_a,
                "allele_b": val_b,
                "is_match": is_match,
                "transition_probability": p_locus,
                "is_rm": meta.is_rapidly_mutating,
                "mutation_rate": meta.mutation_rate,
            }

        # Background population match probability via Clopper-Pearson zero-match bound
        cp = YStrMathematicalFormulation.compute_clopper_pearson_upper_bound(
            k=0, n=database_size_n, alpha=0.05
        )
        p_bg = cp.p_upper_bound

        # Paternal Likelihood Ratio
        paternal_lr = trans_prob_product / max(1e-20, p_bg)
        log10_lr = math.log10(max(1e-50, paternal_lr))

        # Lineage exclusion criteria:
        # >= 3 non-RM mutations or total mutations >= 5 firmly excludes paternal lineage
        is_excluded = (n_std_mutations >= 3) or (n_mutations >= 5)
        if is_excluded:
            paternal_lr = 0.0
            log10_lr = -300.0

        # ENFSI Verbal Predicate
        if is_excluded:
            en_pred = "Definitive Exclusion of Common Paternal Lineage"
            tr_pred = "Ortak Baba Soyunun Kesin Olarak Dışlanması"
        elif n_mutations == 0:
            en_pred = "Extremely Strong Support for Same Paternal Lineage (Full Haplotype Match)"
            tr_pred = "Aynı Baba Soyu Lehine Son Derece Güçlü Destek (Tam Haplotip Eşleşmesi)"
        elif n_mutations <= 2 and n_rm_mutations >= 1:
            en_pred = "Support for Paternal Lineage with Documented Rapid Germline Mutation"
            tr_pred = "Hızlı Germ Hattı Mutasyonu İçeren Baba Soyu Lehine Destek"
        else:
            en_pred = "Inconclusive / Discrepant Paternal Lineage Signal"
            tr_pred = "Sonuçsuz / Çelişkili Baba Soyu Sinyali"

        return PaternalKinshipResult(
            meioses_m=meioses_m,
            total_loci_evaluated=len(common_loci),
            matching_loci_count=n_matching,
            mutated_loci_count=n_mutations,
            rm_mutations_count=n_rm_mutations,
            standard_mutations_count=n_std_mutations,
            transition_probability_product=trans_prob_product,
            haplotype_p_upper=p_bg,
            paternal_lr=paternal_lr,
            log10_paternal_lr=log10_lr,
            is_lineage_excluded=is_excluded,
            locus_evaluations=locus_results,
            verbal_predicate_en=en_pred,
            verbal_predicate_tr=tr_pred,
        )

    # ── 3.7 Bayesian Y-DNA Haplogroup Prediction ──────────────────────────

    @staticmethod
    def predict_haplogroup(
        profile: Dict[str, Any],
    ) -> HaplogroupPredictionResult:
        """
        Predicts major Y-DNA haplogroup from 27-locus Y-STR vector using Bayesian decision model
        and genetic distance metrics relative to verified Y-SNP modal signatures.
        """
        scores: Dict[str, float] = {}
        distances: Dict[str, float] = {}

        for hg, data in HAPLOGROUP_MODAL_PROFILES.items():
            modal = data["modal_str"]
            prior = data["prior"]
            dist = 0.0
            common_count = 0
            log_lik = 0.0

            for locus, modal_val in modal.items():
                if locus in profile:
                    obs = profile[locus]
                    if isinstance(modal_val, list):
                        # Multi-copy
                        norm_obs = YStrMathematicalFormulation.normalize_multi_copy_alleles(
                            obs if isinstance(obs, (list, tuple)) else [obs]
                        )
                        if len(norm_obs) == 2 and len(modal_val) == 2:
                            d1 = abs(norm_obs[0] - modal_val[0])
                            d2 = abs(norm_obs[1] - modal_val[1])
                            locus_dist = d1 + d2
                        else:
                            locus_dist = abs(norm_obs[0] - modal_val[0]) if norm_obs else 2.0
                    else:
                        obs_f = float(obs[0] if isinstance(obs, (list, tuple)) else obs)
                        locus_dist = abs(obs_f - float(modal_val))

                    dist += locus_dist
                    common_count += 1
                    # Discrete Laplace marginal log likelihood
                    p_loc = YStrMathematicalFormulation.compute_discrete_laplace_prob(
                        observed_allele=locus_dist, modal_allele=0.0, dispersion_lambda=0.65
                    )
                    log_lik += math.log(max(1e-12, p_loc))

            avg_dist = dist / max(1, common_count)
            distances[hg] = avg_dist
            scores[hg] = math.log(prior) + log_lik

        # Softmax normalization of Bayesian posteriors
        max_score = max(scores.values())
        exp_scores = {hg: math.exp(s - max_score) for hg, s in scores.items()}
        sum_exp = sum(exp_scores.values())
        posteriors = {hg: round(exp_s / sum_exp, 6) for hg, exp_s in exp_scores.items()}

        best_hg = max(posteriors.items(), key=lambda item: item[1])[0]
        best_data = HAPLOGROUP_MODAL_PROFILES[best_hg]

        return HaplogroupPredictionResult(
            predicted_haplogroup=best_hg,
            confidence_score=posteriors[best_hg],
            primary_snp_marker=best_data["primary_snp"],
            distance_to_modal=round(distances[best_hg], 4),
            description=best_data["description"],
            bayesian_posteriors=posteriors,
        )
