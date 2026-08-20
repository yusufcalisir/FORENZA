"""
FORENZA Forensic Evidence Operating System
Module: Y-STR 27-Locus (Yfiler Plus) & RM Y-STR Lineage Biocomputational Engine
Standards Compliance: ISO/IEC 17025:2017, SWGDAM Lineage Guidelines (2020), ENFSI Evaluative Reporting (2017)
Research Source: research/ystr_27_mtdna_empop_lineage_research.md
"""

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Dict, List, Optional, Tuple, Any
from scipy.stats import f as f_dist


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
    mutation_rate: float  # mu_l (mutations/generation)
    stepwise_param_r: float  # r_l parameter for Stepwise Mutation Model
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


@dataclass
class YStrLocusResult:
    locus_name: str
    alleles: List[str]
    rfu_values: List[float] = field(default_factory=list)
    peak_height_ratio: Optional[float] = None
    is_microvariant: bool = False
    is_off_ladder: bool = False
    flags: List[str] = field(default_factory=list)


@dataclass
class YStrHaplogroupPrediction:
    predicted_haplogroup: str
    confidence_score: float
    bayesian_posteriors: Dict[str, float]
    distance_to_modal: float
    primary_snp_marker: str
    description: str


# ═══════════════════════════════════════════════════════════════════════════════
# 1. 27-LOCUS MASTER SPECIFICATION CATALOG (Thermo Fisher Yfiler Plus)
# ═══════════════════════════════════════════════════════════════════════════════

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

# Ordered list of all 27 loci names in standard Yfiler Plus multiplex order
YSTR_27_LOCI_ORDER: List[str] = list(YSTR_27_MASTER_REGISTRY.keys())

# The 7 Rapidly Mutating loci in Yfiler Plus
RM_YSTR_LOCI_SET = {
    "DYS570", "DYS576", "DYS627", "DYS518", "DYS449", "DYF387S1a/b"
}

# ═══════════════════════════════════════════════════════════════════════════════
# 2. Y-DNA HAPLOGROUP MODAL SIGNATURES & SNP CATALOG
# ═══════════════════════════════════════════════════════════════════════════════

Y_HAPLOGROUP_MODAL_PROFILES: Dict[str, Dict[str, Any]] = {
    "R1b-M269": {
        "primary_snp": "M269 / P312 / U106",
        "description": "Western European / Atlantic Modal Haplotype",
        "modals": {
            "DYS393": 13, "DYS390": 24, "DYS19": 14, "DYS391": 11,
            "DYS385a/b": [11, 14], "DYS438": 12, "DYS439": 12, "DYS437": 15,
            "DYS481": 22, "DYS533": 12, "DYS458": 17, "DYS456": 15,
            "DYS635": 23, "YGATAH4": 12, "DYS389I": 13, "DYS389II": 29,
            "DYS448": 19, "DYS460": 11, "DYS392": 13, "DYS570": 17,
            "DYS576": 18, "DYS627": 15, "DYS518": 38, "DYS449": 30,
            "DYF387S1a/b": [35, 37],
        }
    },
    "R1a-M198": {
        "primary_snp": "M198 / M417",
        "description": "Eastern European / South Asian Lineage",
        "modals": {
            "DYS393": 13, "DYS390": 25, "DYS19": 16, "DYS391": 10,
            "DYS385a/b": [11, 14], "DYS438": 11, "DYS439": 10, "DYS437": 14,
            "DYS481": 22, "DYS533": 12, "DYS458": 15, "DYS456": 15,
            "DYS635": 23, "YGATAH4": 11, "DYS389I": 13, "DYS389II": 30,
            "DYS448": 20, "DYS460": 11, "DYS392": 11, "DYS570": 17,
            "DYS576": 17, "DYS627": 17, "DYS518": 38, "DYS449": 32,
            "DYF387S1a/b": [36, 38],
        }
    },
    "I1-M253": {
        "primary_snp": "M253",
        "description": "Northern European / Scandinavian Lineage",
        "modals": {
            "DYS393": 13, "DYS390": 22, "DYS19": 14, "DYS391": 10,
            "DYS385a/b": [14, 14], "DYS438": 10, "DYS439": 11, "DYS437": 16,
            "DYS481": 28, "DYS533": 12, "DYS458": 15, "DYS456": 14,
            "DYS635": 21, "YGATAH4": 10, "DYS389I": 13, "DYS389II": 28,
            "DYS448": 20, "DYS460": 11, "DYS392": 11, "DYS570": 19,
            "DYS576": 15, "DYS627": 18, "DYS518": 39, "DYS449": 29,
            "DYF387S1a/b": [37, 37],
        }
    },
    "I2-M438": {
        "primary_snp": "M438 / L621",
        "description": "Balkans / Dinaric & Western European Lineage",
        "modals": {
            "DYS393": 15, "DYS390": 24, "DYS19": 16, "DYS391": 10,
            "DYS385a/b": [14, 15], "DYS438": 10, "DYS439": 11, "DYS437": 15,
            "DYS481": 21, "DYS533": 13, "DYS458": 15, "DYS456": 15,
            "DYS635": 24, "YGATAH4": 11, "DYS389I": 13, "DYS389II": 31,
            "DYS448": 20, "DYS460": 11, "DYS392": 11, "DYS570": 17,
            "DYS576": 17, "DYS627": 17, "DYS518": 39, "DYS449": 30,
            "DYF387S1a/b": [36, 38],
        }
    },
    "J1-M267": {
        "primary_snp": "M267",
        "description": "Middle Eastern / Semitic Lineage",
        "modals": {
            "DYS393": 12, "DYS390": 23, "DYS19": 14, "DYS391": 10,
            "DYS385a/b": [14, 17], "DYS438": 10, "DYS439": 11, "DYS437": 14,
            "DYS481": 22, "DYS533": 12, "DYS458": 18, "DYS456": 15,
            "DYS635": 21, "YGATAH4": 11, "DYS389I": 13, "DYS389II": 29,
            "DYS448": 20, "DYS460": 11, "DYS392": 11, "DYS570": 18,
            "DYS576": 17, "DYS627": 20, "DYS518": 38, "DYS449": 30,
            "DYF387S1a/b": [37, 38],
        }
    },
    "J2-M172": {
        "primary_snp": "M172",
        "description": "Anatolian / Mediterranean / Caucasian Lineage",
        "modals": {
            "DYS393": 12, "DYS390": 23, "DYS19": 15, "DYS391": 10,
            "DYS385a/b": [13, 15], "DYS438": 10, "DYS439": 12, "DYS437": 15,
            "DYS481": 23, "DYS533": 12, "DYS458": 17, "DYS456": 15,
            "DYS635": 22, "YGATAH4": 11, "DYS389I": 13, "DYS389II": 29,
            "DYS448": 20, "DYS460": 11, "DYS392": 11, "DYS570": 17,
            "DYS576": 16, "DYS627": 18, "DYS518": 38, "DYS449": 30,
            "DYF387S1a/b": [36, 38],
        }
    },
    "E1b1b-M215": {
        "primary_snp": "M215 / M35",
        "description": "North / East African & Southern European Lineage",
        "modals": {
            "DYS393": 13, "DYS390": 24, "DYS19": 13, "DYS391": 10,
            "DYS385a/b": [11, 12], "DYS438": 10, "DYS439": 12, "DYS437": 15,
            "DYS481": 22, "DYS533": 12, "DYS458": 16, "DYS456": 16,
            "DYS635": 21, "YGATAH4": 11, "DYS389I": 13, "DYS389II": 30,
            "DYS448": 20, "DYS460": 11, "DYS392": 11, "DYS570": 17,
            "DYS576": 18, "DYS627": 18, "DYS518": 38, "DYS449": 30,
            "DYF387S1a/b": [36, 38],
        }
    },
    "E1b1a-V38": {
        "primary_snp": "V38 / M2",
        "description": "Sub-Saharan African / Bantu Expansion Lineage",
        "modals": {
            "DYS393": 15, "DYS390": 21, "DYS19": 15, "DYS391": 10,
            "DYS385a/b": [15, 16], "DYS438": 10, "DYS439": 11, "DYS437": 16,
            "DYS481": 25, "DYS533": 13, "DYS458": 16, "DYS456": 15,
            "DYS635": 21, "YGATAH4": 11, "DYS389I": 14, "DYS389II": 31,
            "DYS448": 20, "DYS460": 11, "DYS392": 11, "DYS570": 19,
            "DYS576": 16, "DYS627": 18, "DYS518": 40, "DYS449": 34,
            "DYF387S1a/b": [38, 39],
        }
    },
    "G2a-P15": {
        "primary_snp": "P15 / L30",
        "description": "Caucasian / Early European Neolithic Farmer Lineage",
        "modals": {
            "DYS393": 14, "DYS390": 22, "DYS19": 15, "DYS391": 10,
            "DYS385a/b": [13, 15], "DYS438": 10, "DYS439": 11, "DYS437": 15,
            "DYS481": 22, "DYS533": 12, "DYS458": 17, "DYS456": 15,
            "DYS635": 21, "YGATAH4": 11, "DYS389I": 12, "DYS389II": 29,
            "DYS448": 21, "DYS460": 11, "DYS392": 11, "DYS570": 17,
            "DYS576": 17, "DYS627": 18, "DYS518": 38, "DYS449": 30,
            "DYF387S1a/b": [36, 38],
        }
    },
    "N-M231": {
        "primary_snp": "M231 / Tat",
        "description": "North Eurasian / Uralic & Siberian Lineage",
        "modals": {
            "DYS393": 14, "DYS390": 23, "DYS19": 14, "DYS391": 11,
            "DYS385a/b": [11, 13], "DYS438": 10, "DYS439": 11, "DYS437": 14,
            "DYS481": 22, "DYS533": 12, "DYS458": 17, "DYS456": 14,
            "DYS635": 22, "YGATAH4": 11, "DYS389I": 13, "DYS389II": 30,
            "DYS448": 19, "DYS460": 11, "DYS392": 14, "DYS570": 17,
            "DYS576": 17, "DYS627": 18, "DYS518": 38, "DYS449": 30,
            "DYF387S1a/b": [36, 38],
        }
    },
    "O-M175": {
        "primary_snp": "M175",
        "description": "East Asian / Southeast Asian Lineage",
        "modals": {
            "DYS393": 12, "DYS390": 24, "DYS19": 15, "DYS391": 10,
            "DYS385a/b": [12, 18], "DYS438": 11, "DYS439": 11, "DYS437": 14,
            "DYS481": 22, "DYS533": 12, "DYS458": 18, "DYS456": 15,
            "DYS635": 21, "YGATAH4": 11, "DYS389I": 12, "DYS389II": 29,
            "DYS448": 20, "DYS460": 11, "DYS392": 13, "DYS570": 17,
            "DYS576": 18, "DYS627": 18, "DYS518": 38, "DYS449": 30,
            "DYF387S1a/b": [36, 38],
        }
    },
    "Q-M3": {
        "primary_snp": "M242 / M3",
        "description": "Indigenous American / North & Central Asian Lineage",
        "modals": {
            "DYS393": 13, "DYS390": 24, "DYS19": 13, "DYS391": 10,
            "DYS385a/b": [12, 13], "DYS438": 10, "DYS439": 12, "DYS437": 14,
            "DYS481": 22, "DYS533": 11, "DYS458": 17.2, "DYS456": 15,
            "DYS635": 23, "YGATAH4": 11, "DYS389I": 13, "DYS389II": 30,
            "DYS448": 20, "DYS460": 10, "DYS392": 14, "DYS570": 16,
            "DYS576": 17, "DYS627": 20.2, "DYS518": 36, "DYS449": 28,
            "DYF387S1a/b": [36, 37],
        }
    },
    "T-M184": {
        "primary_snp": "M184",
        "description": "Horn of Africa / South Asian Lineage",
        "modals": {
            "DYS393": 13, "DYS390": 24, "DYS19": 15, "DYS391": 10,
            "DYS385a/b": [11, 14], "DYS438": 11, "DYS439": 12, "DYS437": 15,
            "DYS481": 22, "DYS533": 12, "DYS458": 16, "DYS456": 15,
            "DYS635": 21, "YGATAH4": 11, "DYS389I": 13, "DYS389II": 30,
            "DYS448": 20, "DYS460": 11, "DYS392": 11, "DYS570": 17,
            "DYS576": 17, "DYS627": 18, "DYS518": 38, "DYS449": 30,
            "DYF387S1a/b": [36, 38],
        }
    },
    "L-M20": {
        "primary_snp": "M20",
        "description": "South Asian / Indus Valley Lineage",
        "modals": {
            "DYS393": 12, "DYS390": 23, "DYS19": 14, "DYS391": 10,
            "DYS385a/b": [13, 14], "DYS438": 10, "DYS439": 11, "DYS437": 14,
            "DYS481": 22, "DYS533": 12, "DYS458": 17, "DYS456": 15,
            "DYS635": 21, "YGATAH4": 11, "DYS389I": 13, "DYS389II": 30,
            "DYS448": 20, "DYS460": 11, "DYS392": 11, "DYS570": 17,
            "DYS576": 17, "DYS627": 18, "DYS518": 38, "DYS449": 30,
            "DYF387S1a/b": [36, 38],
        }
    },
    "C-M130": {
        "primary_snp": "M130 / P39",
        "description": "Oceanian / Mongolian / Indigenous American Lineage",
        "modals": {
            "DYS393": 13, "DYS390": 25, "DYS19": 15, "DYS391": 10,
            "DYS385a/b": [12, 13], "DYS438": 10, "DYS439": 11, "DYS437": 14,
            "DYS481": 22, "DYS533": 12, "DYS458": 17, "DYS456": 15,
            "DYS635": 22, "YGATAH4": 11, "DYS389I": 13, "DYS389II": 30,
            "DYS448": 20, "DYS460": 11, "DYS392": 11, "DYS570": 17,
            "DYS576": 17, "DYS627": 18, "DYS518": 38, "DYS449": 30,
            "DYF387S1a/b": [36, 38],
        }
    },
    "D-CTS11577": {
        "primary_snp": "CTS11577",
        "description": "Tibetan / Japanese (Jomon) / Andaman Lineage",
        "modals": {
            "DYS393": 14, "DYS390": 23, "DYS19": 16, "DYS391": 10,
            "DYS385a/b": [13, 14], "DYS438": 10, "DYS439": 11, "DYS437": 14,
            "DYS481": 22, "DYS533": 12, "DYS458": 17, "DYS456": 15,
            "DYS635": 21, "YGATAH4": 11, "DYS389I": 14, "DYS389II": 31,
            "DYS448": 20, "DYS460": 11, "DYS392": 12, "DYS570": 17,
            "DYS576": 17, "DYS627": 18, "DYS518": 38, "DYS449": 30,
            "DYF387S1a/b": [36, 38],
        }
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# 3. BIOCOMPUTATIONAL HELPER ENGINE CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class YStr27LocusEngine:
    """
    Core Biocomputational Engine for Y-STR 27-Locus (Yfiler Plus) Multiplexing:
    - Master locus registry & micro-variant analysis
    - Multi-copy PHR verification & DYS389 decoupling
    - Clopper-Pearson 95% binomial bounds & Brenner theta-correction
    - Discrete Laplace mixture smoothing model
    - Bayesian Y-DNA haplogroup prediction across 16 clades
    - Single-Step Mutation Model (SMM) kinship indexing
    - Male mixture deconvolution (N_male)
    """

    @classmethod
    def get_locus_metadata(cls, locus_name: str) -> Optional[YStrLocusMetadata]:
        """Retrieves metadata for a Y-STR locus (case-insensitive)."""
        trimmed = locus_name.strip()
        if trimmed in YSTR_27_MASTER_REGISTRY:
            return YSTR_27_MASTER_REGISTRY[trimmed]
        lower = trimmed.lower()
        for name, meta in YSTR_27_MASTER_REGISTRY.items():
            if name.lower() == lower:
                return meta
        return None

    @classmethod
    def decouple_dys389(cls, dys389i: float, dys389ii_total: float) -> Tuple[float, float]:
        """
        Decouples nested DYS389II total repeats into pure variable DYS389.2:
        DYS389.2_pure = DYS389II_total - DYS389I
        Returns: (DYS389I, DYS389.2_pure)
        """
        dys389_2_pure = dys389ii_total - dys389i
        return dys389i, dys389_2_pure

    @classmethod
    def evaluate_multi_copy_phr(
        cls,
        locus_name: str,
        rfu_values: List[float],
        threshold: float = 0.50
    ) -> Tuple[float, bool, Optional[str]]:
        """
        Evaluates Peak Height Ratio (PHR) for multi-copy duplicated loci (DYS385a/b, DYF387S1a/b):
        PHR = min(RFU_1, RFU_2) / max(RFU_1, RFU_2)
        Returns: (PHR, is_balanced, warning_flag)
        """
        if len(rfu_values) < 2:
            return 1.0, True, None
        
        rfu1, rfu2 = rfu_values[0], rfu_values[1]
        max_rfu = max(rfu1, rfu2)
        if max_rfu <= 0:
            return 1.0, True, None
            
        phr = min(rfu1, rfu2) / max_rfu
        if phr < threshold:
            warning = f"Imbalance warning: PHR ({phr:.2f}) < {threshold:.2f} at {locus_name} (Possible mixture or copy-number mutation)"
            return phr, False, warning
        return phr, True, None

    @classmethod
    def calculate_clopper_pearson_95_upper(cls, k: int, n: int, alpha: float = 0.05) -> float:
        """
        Computes the exact 95% Clopper-Pearson Binomial Upper Bound (p_upper).
        For k = 0: p_upper = 1 - (alpha)^(1 / (N + 1))
        For k > 0: derived via Snedecor F-distribution.
        """
        if n <= 0:
            return 1.0
            
        if k == 0:
            return 1.0 - math.pow(alpha, 1.0 / (n + 1.0))
            
        df1 = 2 * (k + 1)
        df2 = 2 * (n - k)
        
        # Upper tail critical value from F-distribution at 1 - alpha/2 (0.975 for alpha=0.05)
        f_crit = f_dist.ppf(1.0 - (alpha / 2.0), df1, df2)
        numerator = (k + 1) * f_crit
        denominator = (n - k) + (k + 1) * f_crit
        return float(numerator / denominator)

    @classmethod
    def calculate_brenner_frequency(cls, k: int, n: int, theta: float = 0.02) -> float:
        """
        Computes subpopulation-corrected Y-STR frequency using Brenner's formula:
        p_Brenner = (k + theta) / (N + theta)
        """
        if n <= 0:
            return 1.0
        return (k + theta) / (n + theta)

    @classmethod
    def calculate_discrete_laplace_locus_prob(
        cls,
        observed_allele: float,
        modal_allele: float,
        dispersion_lambda: float = 0.65
    ) -> float:
        """
        Calculates Discrete Laplace marginal locus probability:
        f(y | mu, lambda) = ((1 - lambda) / (1 + lambda)) * lambda^(|y - mu|)
        """
        diff = abs(observed_allele - modal_allele)
        coeff = (1.0 - dispersion_lambda) / (1.0 + dispersion_lambda)
        return coeff * math.pow(dispersion_lambda, diff)

    @staticmethod
    def _extract_allele_floats(val: Any) -> List[float]:
        if val is None:
            return []
        if isinstance(val, (int, float)):
            return [float(val)]
        if isinstance(val, list):
            res: List[float] = []
            for item in val:
                res.extend(YStr27LocusEngine._extract_allele_floats(item))
            return res
        if isinstance(val, dict):
            if "alleles" in val and isinstance(val["alleles"], list):
                return YStr27LocusEngine._extract_allele_floats(val["alleles"])
            res = []
            if "allele1" in val and val["allele1"] is not None:
                res.extend(YStr27LocusEngine._extract_allele_floats(val["allele1"]))
            if "allele2" in val and val["allele2"] is not None and str(val["allele2"]) != str(val.get("allele1")):
                res.extend(YStr27LocusEngine._extract_allele_floats(val["allele2"]))
            return res
        s = str(val).strip().replace("[", "").replace("]", "").replace("'", "").replace('"', '')
        parts = [p.strip() for p in s.split(",") if p.strip()]
        res = []
        for p in parts:
            try:
                res.append(float(p))
            except ValueError:
                pass
        return res

    @classmethod
    def predict_y_dna_haplogroup(
        cls,
        ystr_profile: Dict[str, Any]
    ) -> YStrHaplogroupPrediction:
        """
        Predicts major Y-DNA haplogroup from 27-locus Y-STR vector using a
        Bayesian decision framework with distance penalties relative to modal haplotypes.
        """
        scores: Dict[str, float] = {}
        distances: Dict[str, float] = {}

        for hg_name, hg_data in Y_HAPLOGROUP_MODAL_PROFILES.items():
            modals = hg_data["modals"]
            log_prob = 0.0
            dist_sum = 0.0
            evaluated_loci = 0

            for locus, modal_val in modals.items():
                if locus not in ystr_profile:
                    continue

                raw_val = ystr_profile[locus]
                obs_vals = cls._extract_allele_floats(raw_val)
                modal_list = modal_val if isinstance(modal_val, list) else [float(modal_val)]

                if not obs_vals:
                    continue

                meta = cls.get_locus_metadata(locus)
                if meta and meta.is_multi_copy:
                    if len(obs_vals) > 1 and len(modal_list) > 1:
                        d = abs(obs_vals[0] - modal_list[0]) + abs(obs_vals[1] - modal_list[1])
                        dist_sum += d
                        p_loc1 = cls.calculate_discrete_laplace_locus_prob(obs_vals[0], modal_list[0])
                        p_loc2 = cls.calculate_discrete_laplace_locus_prob(obs_vals[1], modal_list[1])
                        log_prob += math.log(max(p_loc1 * p_loc2, 1e-12))
                        evaluated_loci += 2
                    else:
                        d = abs(obs_vals[0] - modal_list[0])
                        dist_sum += d
                        p_loc = cls.calculate_discrete_laplace_locus_prob(obs_vals[0], modal_list[0])
                        log_prob += math.log(max(p_loc, 1e-12))
                        evaluated_loci += 1
                else:
                    obs_num = obs_vals[0]
                    modal_num = modal_list[0]
                    d = abs(obs_num - modal_num)
                    dist_sum += d
                    p_loc = cls.calculate_discrete_laplace_locus_prob(obs_num, modal_num)
                    log_prob += math.log(max(p_loc, 1e-12))
                    evaluated_loci += 1

            if evaluated_loci > 0:
                scores[hg_name] = log_prob
                distances[hg_name] = dist_sum / evaluated_loci
            else:
                scores[hg_name] = -999.0
                distances[hg_name] = 99.0

        # Softmax normalization for posteriors
        max_log = max(scores.values()) if scores else 0.0
        exp_sum = sum(math.exp(s - max_log) for s in scores.values())
        posteriors = {k: (math.exp(v - max_log) / exp_sum) for k, v in scores.items()}

        # Top prediction
        best_hg = max(posteriors, key=posteriors.get)
        best_conf = posteriors[best_hg]
        best_dist = distances.get(best_hg, 0.0)
        best_data = Y_HAPLOGROUP_MODAL_PROFILES[best_hg]

        return YStrHaplogroupPrediction(
            predicted_haplogroup=best_hg,
            confidence_score=best_conf,
            bayesian_posteriors=posteriors,
            distance_to_modal=best_dist,
            primary_snp_marker=best_data["primary_snp"],
            description=best_data["description"],
        )

    # Alias for method naming
    predict_haplogroup = predict_y_dna_haplogroup

    @classmethod
    def calculate_smm_kinship_index(
        cls,
        profile_a: Dict[str, Any],
        profile_b: Dict[str, Any],
        meioses: int = 1,
        database_size: int = 35000,
        unrelated_match_prob: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Computes the Combined Kinship Index (CPI_Y-STR) under the Single-Step Mutation Model:
        P(Y_B | Y_A, m) = Product_l P(y_B,l | y_A,l, m, mu_l)
        CPI = P(Y_B | Y_A, m) / P(Y_B)
        """
        prob_transmission = 1.0
        mutated_loci: List[Dict[str, Any]] = []
        compared_loci_count = 0

        for locus_name, meta in YSTR_27_MASTER_REGISTRY.items():
            if locus_name not in profile_a or locus_name not in profile_b:
                continue

            a_nums = cls._extract_allele_floats(profile_a[locus_name])
            b_nums = cls._extract_allele_floats(profile_b[locus_name])

            if not a_nums or not b_nums:
                continue

            if meta.is_multi_copy and len(a_nums) > 1 and len(b_nums) > 1:
                diff = (abs(a_nums[0] - b_nums[0]) + abs(a_nums[1] - b_nums[1])) / 2.0
            else:
                diff = abs(a_nums[0] - b_nums[0])

            mu = meta.mutation_rate
            m = meioses
            steps = int(round(diff))

            if steps == 0:
                p_loc = math.pow(1.0 - mu, m)
            elif steps == 1:
                p_loc = (m * mu * math.pow(1.0 - mu, m - 1)) / 2.0
                mutated_loci.append({
                    "locus": locus_name,
                    "allele_a": a_nums,
                    "allele_b": b_nums,
                    "steps": 1,
                    "mutation_rate": mu,
                    "transition_prob": p_loc,
                    "is_rapidly_mutating": meta.is_rapidly_mutating,
                })
            elif steps == 2:
                comb_m_2 = (m * (m - 1)) / 2.0 if m >= 2 else 0.5
                p_loc = (comb_m_2 * (mu ** 2) * math.pow(1.0 - mu, max(m - 2, 0))) / 4.0
                mutated_loci.append({
                    "locus": locus_name,
                    "allele_a": a_nums,
                    "allele_b": b_nums,
                    "steps": 2,
                    "mutation_rate": mu,
                    "transition_prob": p_loc,
                    "is_rapidly_mutating": meta.is_rapidly_mutating,
                })
            else:
                p_loc = (mu ** steps) / (2.0 ** steps)
                mutated_loci.append({
                    "locus": locus_name,
                    "allele_a": a_nums,
                    "allele_b": b_nums,
                    "steps": steps,
                    "mutation_rate": mu,
                    "transition_prob": p_loc,
                    "is_rapidly_mutating": meta.is_rapidly_mutating,
                })

            prob_transmission *= max(p_loc, 1e-18)
            compared_loci_count += 1

        p_unrelated = unrelated_match_prob or cls.calculate_clopper_pearson_95_upper(0, database_size)
        cpi = prob_transmission / p_unrelated if p_unrelated > 0 else 1.0

        return {
            "compared_loci_count": compared_loci_count,
            "meioses": meioses,
            "transmission_probability": prob_transmission,
            "unrelated_match_probability": p_unrelated,
            "combined_kinship_index": cpi,
            "mutated_loci": mutated_loci,
            "mutation_count": len(mutated_loci),
            "is_kinship_supported": cpi > 1.0,
        }


    # Method aliases
    calculate_kinship_likelihood_ratio = calculate_smm_kinship_index
    compare_haplotypes_for_kinship = calculate_smm_kinship_index


    @classmethod
    def deconvolute_male_mixture(cls, profile_alleles: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Determines minimum number of male contributors (N_male):
        N_male = max( max_single ceil(n_alleles / 1), max_multi ceil(n_alleles / 2) )
        """
        max_single = 1
        max_multi = 1
        locus_counts: Dict[str, int] = {}

        for locus_name, alleles in profile_alleles.items():
            meta = cls.get_locus_metadata(locus_name)
            count = len(alleles)
            locus_counts[locus_name] = count

            if meta and meta.is_multi_copy:
                n_contributors = int(math.ceil(count / 2.0))
                if n_contributors > max_multi:
                    max_multi = n_contributors
            else:
                if count > max_single:
                    max_single = count

        n_male_min = max(max_single, max_multi)
        return {
            "n_male_min": n_male_min,
            "is_mixture": n_male_min > 1,
            "max_single_copy_alleles": max_single,
            "max_multi_copy_alleles": max_multi * 2,
            "locus_counts": locus_counts,
        }


# Aliases for naming compatibility
Ystr27LocusEngine = YStr27LocusEngine
YSTR_HAPLOGROUP_MODALS = Y_HAPLOGROUP_MODAL_PROFILES

