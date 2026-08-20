"""
Forensic DNA STR Locus Master Registry & Micro-Variant Engine
Compliant with ISO/IEC 17025:2017, SWGDAM 2020, ENFSI 2017, and ISFG Guidelines.
Derived verbatim from research specification: research/str_24_locus_microvariants_research.md
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Set


# ═══════════════════════════════════════════════════════════════════════════════
# 1. ENUMS & DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

class StrRepeatUnitClass(str, Enum):
    TETRANUCLEOTIDE = "Tetranucleotide"
    PENTANUCLEOTIDE = "Pentanucleotide"
    TRINUCLEOTIDE = "Trinucleotide"
    NON_STR_INDEL = "Non-STR Indel"


class StrMotifClass(str, Enum):
    SIMPLE = "Simple"
    COMPOUND = "Compound"
    COMPLEX = "Complex"
    DIMORPHIC = "Dimorphic"
    MONOMORPHIC = "Monomorphic"


class MicrovariantEtiologyClass(str, Enum):
    SINGLE_BASE_DELETION = "Single-base deletion in core repeat unit"
    SINGLE_BASE_INSERTION = "Single-base insertion"
    DINUCLEOTIDE_INDEL = "Dinucleotide insertion/deletion"
    TRINUCLEOTIDE_INSERTION = "Trinucleotide motif insertion"
    PARTIAL_REPEAT_COLLAPSE = "Partial repeat collapse / residual unit"
    COMPLEX_ARRAY_FRAMESHIFT = "Complex array hypervariable frameshift"
    INTRONIC_INDEL = "Intronic Insertion/Deletion"


@dataclass(frozen=True)
class StrLocusMetadata:
    locus_name: str
    cytogenetic_band: str
    grch38_coords: str
    repeat_unit_class: StrRepeatUnitClass
    repeat_unit_size_bp: int
    motif_class: StrMotifClass
    canonical_motif_sequence: str
    observed_allele_spectrum: Tuple[str, ...]
    documented_microvariants: Tuple[str, ...]
    max_reverse_stutter_ratio: float      # SR_max
    germline_mutation_rate_10k: float     # mu * 10^-3
    stepwise_mutation_r: float = 0.850    # r parameter in SMM
    is_codis_core: bool = True
    dye_channel_default: str = "BLUE"


@dataclass(frozen=True)
class MicrovariantDetail:
    locus_name: str
    fractional_allele: str
    integer_base_repeat: int
    fractional_offset: float
    delta_bp: int
    alternate_delta_bp: Optional[int]
    sequence_representation: str
    etiology_description: str
    etiology_class: MicrovariantEtiologyClass


# ═══════════════════════════════════════════════════════════════════════════════
# 2. MASTER 24-LOCUS AUTOSOMAL STR MASTER REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

STR_LOCUS_24_MASTER_REGISTRY: Dict[str, StrLocusMetadata] = {
    "D3S1358": StrLocusMetadata(
        locus_name="D3S1358",
        cytogenetic_band="3p21.31",
        grch38_coords="chr3:45,540,056-45,540,210",
        repeat_unit_class=StrRepeatUnitClass.TETRANUCLEOTIDE,
        repeat_unit_size_bp=4,
        motif_class=StrMotifClass.COMPOUND,
        canonical_motif_sequence="TCTA [TCTG]n [TCTA]m",
        observed_allele_spectrum=("8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"),
        documented_microvariants=(),
        max_reverse_stutter_ratio=0.110,
        germline_mutation_rate_10k=1.20,
        stepwise_mutation_r=0.850,
        is_codis_core=True,
        dye_channel_default="BLUE",
    ),
    "vWA": StrLocusMetadata(
        locus_name="vWA",
        cytogenetic_band="12p13.31",
        grch38_coords="chr12:5,983,161-5,983,350",
        repeat_unit_class=StrRepeatUnitClass.TETRANUCLEOTIDE,
        repeat_unit_size_bp=4,
        motif_class=StrMotifClass.COMPOUND,
        canonical_motif_sequence="TCTA [TCTG]n [TCTA]m",
        observed_allele_spectrum=("10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25"),
        documented_microvariants=(),
        max_reverse_stutter_ratio=0.115,
        germline_mutation_rate_10k=2.50,
        stepwise_mutation_r=0.880,
        is_codis_core=True,
        dye_channel_default="GREEN",
    ),
    "FGA": StrLocusMetadata(
        locus_name="FGA",
        cytogenetic_band="4q31.3",
        grch38_coords="chr4:154,582,650-154,582,980",
        repeat_unit_class=StrRepeatUnitClass.TETRANUCLEOTIDE,
        repeat_unit_size_bp=4,
        motif_class=StrMotifClass.COMPLEX,
        canonical_motif_sequence="[GGAA]2 GGAG [AAAG]n AGAA AAAA [GAAA]m",
        observed_allele_spectrum=(
            "15", "16", "16.2", "17", "18", "19", "20", "21", "21.2", "22", "22.2", "23",
            "24", "25", "25.2", "26", "26.2", "27", "28", "29", "30", "30.2", "31", "32",
            "33", "42.2", "43.2", "44.2", "45.2", "46.2", "47.2", "48.2", "49.2", "50.2", "51.2"
        ),
        documented_microvariants=("16.2", "21.2", "22.2", "25.2", "26.2", "30.2", "42.2", "43.2", "44.2", "45.2", "46.2", "47.2", "48.2", "49.2", "50.2", "51.2"),
        max_reverse_stutter_ratio=0.130,
        germline_mutation_rate_10k=2.80,
        stepwise_mutation_r=0.820,
        is_codis_core=True,
        dye_channel_default="BLUE",
    ),
    "D8S1179": StrLocusMetadata(
        locus_name="D8S1179",
        cytogenetic_band="8q24.13",
        grch38_coords="chr8:124,892,010-124,892,210",
        repeat_unit_class=StrRepeatUnitClass.TETRANUCLEOTIDE,
        repeat_unit_size_bp=4,
        motif_class=StrMotifClass.COMPOUND,
        canonical_motif_sequence="[TCTA]n [TCTG]m",
        observed_allele_spectrum=("7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19"),
        documented_microvariants=(),
        max_reverse_stutter_ratio=0.100,
        germline_mutation_rate_10k=1.40,
        stepwise_mutation_r=0.860,
        is_codis_core=True,
        dye_channel_default="GREEN",
    ),
    "D21S11": StrLocusMetadata(
        locus_name="D21S11",
        cytogenetic_band="21q21.1",
        grch38_coords="chr21:19,182,000-19,182,400",
        repeat_unit_class=StrRepeatUnitClass.TETRANUCLEOTIDE,
        repeat_unit_size_bp=4,
        motif_class=StrMotifClass.COMPLEX,
        canonical_motif_sequence="[TCTA]n [TCTG]m [TCTA]3 TA [TCTA]3 TCA [TCTA]2 TCTA [TCTG]p [TCTA]q",
        observed_allele_spectrum=(
            "24", "24.2", "25", "26", "27", "28", "28.2", "29", "29.2", "30", "30.2",
            "31", "31.2", "32", "32.2", "33", "33.2", "34", "34.2", "35", "36", "37", "38"
        ),
        documented_microvariants=("24.2", "28.2", "29.2", "30.2", "31.2", "32.2", "33.2", "34.2"),
        max_reverse_stutter_ratio=0.120,
        germline_mutation_rate_10k=2.10,
        stepwise_mutation_r=0.800,
        is_codis_core=True,
        dye_channel_default="YELLOW",
    ),
    "D18S51": StrLocusMetadata(
        locus_name="D18S51",
        cytogenetic_band="18q21.33",
        grch38_coords="chr18:61,431,200-61,431,600",
        repeat_unit_class=StrRepeatUnitClass.TETRANUCLEOTIDE,
        repeat_unit_size_bp=4,
        motif_class=StrMotifClass.SIMPLE,
        canonical_motif_sequence="[AGAA]n",
        observed_allele_spectrum=(
            "7", "8", "9", "10", "10.2", "11", "12", "13", "13.2", "14", "14.2", "15",
            "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27"
        ),
        documented_microvariants=("10.2", "13.2", "14.2"),
        max_reverse_stutter_ratio=0.140,
        germline_mutation_rate_10k=2.20,
        stepwise_mutation_r=0.900,
        is_codis_core=True,
        dye_channel_default="BLUE",
    ),
    "D5S818": StrLocusMetadata(
        locus_name="D5S818",
        cytogenetic_band="5q23.2",
        grch38_coords="chr5:123,774,100-123,774,350",
        repeat_unit_class=StrRepeatUnitClass.TETRANUCLEOTIDE,
        repeat_unit_size_bp=4,
        motif_class=StrMotifClass.SIMPLE,
        canonical_motif_sequence="[AGAT]n",
        observed_allele_spectrum=("7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18"),
        documented_microvariants=(),
        max_reverse_stutter_ratio=0.090,
        germline_mutation_rate_10k=1.00,
        stepwise_mutation_r=0.920,
        is_codis_core=True,
        dye_channel_default="YELLOW",
    ),
    "D13S317": StrLocusMetadata(
        locus_name="D13S317",
        cytogenetic_band="13q31.1",
        grch38_coords="chr13:82,147,100-82,147,350",
        repeat_unit_class=StrRepeatUnitClass.TETRANUCLEOTIDE,
        repeat_unit_size_bp=4,
        motif_class=StrMotifClass.SIMPLE,
        canonical_motif_sequence="[TATC]n",
        observed_allele_spectrum=("5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"),
        documented_microvariants=(),
        max_reverse_stutter_ratio=0.080,
        germline_mutation_rate_10k=1.30,
        stepwise_mutation_r=0.910,
        is_codis_core=True,
        dye_channel_default="GREEN",
    ),
    "D7S820": StrLocusMetadata(
        locus_name="D7S820",
        cytogenetic_band="7q21.11",
        grch38_coords="chr7:83,789,100-83,789,350",
        repeat_unit_class=StrRepeatUnitClass.TETRANUCLEOTIDE,
        repeat_unit_size_bp=4,
        motif_class=StrMotifClass.SIMPLE,
        canonical_motif_sequence="[GATA]n",
        observed_allele_spectrum=("6", "7", "8", "8.1", "9", "9.1", "10", "11", "12", "13", "14", "15"),
        documented_microvariants=("8.1", "9.1"),
        max_reverse_stutter_ratio=0.080,
        germline_mutation_rate_10k=1.00,
        stepwise_mutation_r=0.920,
        is_codis_core=True,
        dye_channel_default="GREEN",
    ),
    "D16S539": StrLocusMetadata(
        locus_name="D16S539",
        cytogenetic_band="16q24.1",
        grch38_coords="chr16:84,947,100-84,947,350",
        repeat_unit_class=StrRepeatUnitClass.TETRANUCLEOTIDE,
        repeat_unit_size_bp=4,
        motif_class=StrMotifClass.SIMPLE,
        canonical_motif_sequence="[GATA]n",
        observed_allele_spectrum=("5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"),
        documented_microvariants=(),
        max_reverse_stutter_ratio=0.090,
        germline_mutation_rate_10k=1.10,
        stepwise_mutation_r=0.910,
        is_codis_core=True,
        dye_channel_default="RED",
    ),
    "CSF1PO": StrLocusMetadata(
        locus_name="CSF1PO",
        cytogenetic_band="5q33.1",
        grch38_coords="chr5:150,076,200-150,076,450",
        repeat_unit_class=StrRepeatUnitClass.TETRANUCLEOTIDE,
        repeat_unit_size_bp=4,
        motif_class=StrMotifClass.SIMPLE,
        canonical_motif_sequence="[ATCT]n",
        observed_allele_spectrum=("6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"),
        documented_microvariants=(),
        max_reverse_stutter_ratio=0.080,
        germline_mutation_rate_10k=1.20,
        stepwise_mutation_r=0.930,
        is_codis_core=True,
        dye_channel_default="GREEN",
    ),
    "TH01": StrLocusMetadata(
        locus_name="TH01",
        cytogenetic_band="11p15.5",
        grch38_coords="chr11:2,171,050-2,171,250",
        repeat_unit_class=StrRepeatUnitClass.TETRANUCLEOTIDE,
        repeat_unit_size_bp=4,
        motif_class=StrMotifClass.SIMPLE,
        canonical_motif_sequence="[AATG]n",
        observed_allele_spectrum=("3", "4", "5", "6", "7", "8", "8.3", "9", "9.3", "10", "10.3", "11", "12", "13.3", "14"),
        documented_microvariants=("8.3", "9.3", "10.3", "13.3"),
        max_reverse_stutter_ratio=0.050,
        germline_mutation_rate_10k=0.60,
        stepwise_mutation_r=0.950,
        is_codis_core=True,
        dye_channel_default="YELLOW",
    ),
    "TPOX": StrLocusMetadata(
        locus_name="TPOX",
        cytogenetic_band="2p25.3",
        grch38_coords="chr2:1,489,000-1,489,200",
        repeat_unit_class=StrRepeatUnitClass.TETRANUCLEOTIDE,
        repeat_unit_size_bp=4,
        motif_class=StrMotifClass.SIMPLE,
        canonical_motif_sequence="[AATG]n",
        observed_allele_spectrum=("4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"),
        documented_microvariants=(),
        max_reverse_stutter_ratio=0.050,
        germline_mutation_rate_10k=0.50,
        stepwise_mutation_r=0.960,
        is_codis_core=True,
        dye_channel_default="YELLOW",
    ),
    "D1S1656": StrLocusMetadata(
        locus_name="D1S1656",
        cytogenetic_band="1q42.2",
        grch38_coords="chr1:230,784,100-230,784,400",
        repeat_unit_class=StrRepeatUnitClass.TETRANUCLEOTIDE,
        repeat_unit_size_bp=4,
        motif_class=StrMotifClass.COMPLEX,
        canonical_motif_sequence="CCTA [TCTA]n TCA [TCTA]m",
        observed_allele_spectrum=(
            "9", "10", "11", "12", "13", "14", "14.3", "15", "15.3", "16", "16.3", "17",
            "17.3", "18", "18.3", "19", "19.3", "20.3"
        ),
        documented_microvariants=("14.3", "15.3", "16.3", "17.3", "18.3", "19.3", "20.3"),
        max_reverse_stutter_ratio=0.130,
        germline_mutation_rate_10k=2.20,
        stepwise_mutation_r=0.830,
        is_codis_core=True,
        dye_channel_default="BLUE",
    ),
    "D2S441": StrLocusMetadata(
        locus_name="D2S441",
        cytogenetic_band="2p14",
        grch38_coords="chr2:68,011,200-68,011,450",
        repeat_unit_class=StrRepeatUnitClass.TETRANUCLEOTIDE,
        repeat_unit_size_bp=4,
        motif_class=StrMotifClass.COMPOUND,
        canonical_motif_sequence="[TCTA]n TCA [TCTA]m",
        observed_allele_spectrum=("8", "9", "10", "10.3", "11", "11.3", "12", "12.3", "13", "13.3", "14", "15", "16", "17"),
        documented_microvariants=("10.3", "11.3", "12.3", "13.3"),
        max_reverse_stutter_ratio=0.080,
        germline_mutation_rate_10k=1.10,
        stepwise_mutation_r=0.890,
        is_codis_core=True,
        dye_channel_default="RED",
    ),
    "D2S1338": StrLocusMetadata(
        locus_name="D2S1338",
        cytogenetic_band="2q35",
        grch38_coords="chr2:218,058,100-218,058,450",
        repeat_unit_class=StrRepeatUnitClass.TETRANUCLEOTIDE,
        repeat_unit_size_bp=4,
        motif_class=StrMotifClass.COMPOUND,
        canonical_motif_sequence="[GGAA]n [GGCA]m",
        observed_allele_spectrum=("15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28"),
        documented_microvariants=(),
        max_reverse_stutter_ratio=0.110,
        germline_mutation_rate_10k=1.60,
        stepwise_mutation_r=0.870,
        is_codis_core=True,
        dye_channel_default="BLUE",
    ),
    "D10S1248": StrLocusMetadata(
        locus_name="D10S1248",
        cytogenetic_band="10q26.3",
        grch38_coords="chr10:130,562,100-130,562,350",
        repeat_unit_class=StrRepeatUnitClass.TETRANUCLEOTIDE,
        repeat_unit_size_bp=4,
        motif_class=StrMotifClass.SIMPLE,
        canonical_motif_sequence="[GGAA]n",
        observed_allele_spectrum=("7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19"),
        documented_microvariants=(),
        max_reverse_stutter_ratio=0.090,
        germline_mutation_rate_10k=0.90,
        stepwise_mutation_r=0.930,
        is_codis_core=True,
        dye_channel_default="RED",
    ),
    "D12S391": StrLocusMetadata(
        locus_name="D12S391",
        cytogenetic_band="12p13.2",
        grch38_coords="chr12:12,341,200-12,341,550",
        repeat_unit_class=StrRepeatUnitClass.TETRANUCLEOTIDE,
        repeat_unit_size_bp=4,
        motif_class=StrMotifClass.COMPOUND,
        canonical_motif_sequence="[AGAT]n [AGAC]m",
        observed_allele_spectrum=(
            "14", "15", "16", "17", "17.3", "18", "18.3", "19", "19.3", "20", "20.3",
            "21", "22", "23", "24", "25", "26", "27"
        ),
        documented_microvariants=("17.3", "18.3", "19.3", "20.3"),
        max_reverse_stutter_ratio=0.140,
        germline_mutation_rate_10k=2.50,
        stepwise_mutation_r=0.810,
        is_codis_core=True,
        dye_channel_default="GREEN",
    ),
    "D19S433": StrLocusMetadata(
        locus_name="D19S433",
        cytogenetic_band="19q12",
        grch38_coords="chr19:30,417,100-30,417,350",
        repeat_unit_class=StrRepeatUnitClass.TETRANUCLEOTIDE,
        repeat_unit_size_bp=4,
        motif_class=StrMotifClass.COMPOUND,
        canonical_motif_sequence="[AAGG]n [TAGG]m",
        observed_allele_spectrum=("9", "10", "11", "12", "12.2", "13", "13.2", "14", "14.2", "15", "15.2", "16", "16.2", "17.2"),
        documented_microvariants=("12.2", "13.2", "14.2", "15.2", "16.2", "17.2"),
        max_reverse_stutter_ratio=0.100,
        germline_mutation_rate_10k=1.20,
        stepwise_mutation_r=0.880,
        is_codis_core=True,
        dye_channel_default="YELLOW",
    ),
    "D22S1045": StrLocusMetadata(
        locus_name="D22S1045",
        cytogenetic_band="22q12.3",
        grch38_coords="chr22:35,789,100-35,789,300",
        repeat_unit_class=StrRepeatUnitClass.TRINUCLEOTIDE,
        repeat_unit_size_bp=3,
        motif_class=StrMotifClass.SIMPLE,
        canonical_motif_sequence="[ATT]n",
        observed_allele_spectrum=("7", "8", "9", "10", "11", "12", "13", "14", "14.1", "15", "15.1", "16", "17", "18", "19", "20"),
        documented_microvariants=("14.1", "15.1"),
        max_reverse_stutter_ratio=0.150,
        germline_mutation_rate_10k=1.80,
        stepwise_mutation_r=0.780,
        is_codis_core=True,
        dye_channel_default="RED",
    ),
    "SE33": StrLocusMetadata(
        locus_name="SE33",
        cytogenetic_band="6q14.2",
        grch38_coords="chr6:88,270,100-88,270,850",
        repeat_unit_class=StrRepeatUnitClass.TETRANUCLEOTIDE,
        repeat_unit_size_bp=4,
        motif_class=StrMotifClass.COMPLEX,
        canonical_motif_sequence="[AAAG]n AG [AAAG]m",
        observed_allele_spectrum=(
            "4.2", "9", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22",
            "22.2", "23.2", "24.2", "25.2", "26.2", "27.2", "28.2", "29.2", "30.2", "31.2",
            "32.2", "33.2", "34.2", "35.2", "36.2", "37"
        ),
        documented_microvariants=("4.2", "22.2", "23.2", "24.2", "25.2", "26.2", "27.2", "28.2", "29.2", "30.2", "31.2", "32.2", "33.2", "34.2", "35.2", "36.2"),
        max_reverse_stutter_ratio=0.160,
        germline_mutation_rate_10k=6.40,
        stepwise_mutation_r=0.700,
        is_codis_core=False,  # ESS / European standard set locus
        dye_channel_default="PURPLE",
    ),
    "Penta D": StrLocusMetadata(
        locus_name="Penta D",
        cytogenetic_band="21q22.3",
        grch38_coords="chr21:43,780,100-43,780,450",
        repeat_unit_class=StrRepeatUnitClass.PENTANUCLEOTIDE,
        repeat_unit_size_bp=5,
        motif_class=StrMotifClass.SIMPLE,
        canonical_motif_sequence="[AAAGA]n",
        observed_allele_spectrum=("2.2", "3.2", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17"),
        documented_microvariants=("2.2", "3.2"),
        max_reverse_stutter_ratio=0.040,
        germline_mutation_rate_10k=1.00,
        stepwise_mutation_r=0.940,
        is_codis_core=False,
        dye_channel_default="PURPLE",
    ),
    "Penta E": StrLocusMetadata(
        locus_name="Penta E",
        cytogenetic_band="15q26.2",
        grch38_coords="chr15:96,732,100-96,732,550",
        repeat_unit_class=StrRepeatUnitClass.PENTANUCLEOTIDE,
        repeat_unit_size_bp=5,
        motif_class=StrMotifClass.SIMPLE,
        canonical_motif_sequence="[AAAGA]n",
        observed_allele_spectrum=(
            "5", "6", "7", "8", "9", "10", "10.4", "11", "12", "13", "14", "15", "16", "17",
            "18", "19", "20", "21", "22", "23", "24"
        ),
        documented_microvariants=("10.4",),
        max_reverse_stutter_ratio=0.040,
        germline_mutation_rate_10k=1.20,
        stepwise_mutation_r=0.930,
        is_codis_core=False,
        dye_channel_default="PURPLE",
    ),
    "Amelogenin": StrLocusMetadata(
        locus_name="Amelogenin",
        cytogenetic_band="Xp22.2 / Yp11.2",
        grch38_coords="X:11,210,100-11,210,210 / Y:6,710,100-6,710,220",
        repeat_unit_class=StrRepeatUnitClass.NON_STR_INDEL,
        repeat_unit_size_bp=6,
        motif_class=StrMotifClass.DIMORPHIC,
        canonical_motif_sequence="Intron 1 Indel (6-bp Y insertion)",
        observed_allele_spectrum=("X", "Y"),
        documented_microvariants=(),
        max_reverse_stutter_ratio=0.000,
        germline_mutation_rate_10k=0.00,
        stepwise_mutation_r=1.000,
        is_codis_core=True,
        dye_channel_default="RED",
    ),
    "DYS391": StrLocusMetadata(
        locus_name="DYS391",
        cytogenetic_band="Yq11.22",
        grch38_coords="chrY:14,130,000-14,130,200",
        repeat_unit_class=StrRepeatUnitClass.TETRANUCLEOTIDE,
        repeat_unit_size_bp=4,
        motif_class=StrMotifClass.SIMPLE,
        canonical_motif_sequence="[GATA]n",
        observed_allele_spectrum=("7", "8", "9", "10", "11", "12", "13"),
        documented_microvariants=(),
        max_reverse_stutter_ratio=0.080,
        germline_mutation_rate_10k=2.40,
        stepwise_mutation_r=0.880,
        is_codis_core=False,
        dye_channel_default="RED",
    ),
    "SRY": StrLocusMetadata(
        locus_name="SRY",
        cytogenetic_band="Yp11.2",
        grch38_coords="chrY:2,780,000-2,780,500",
        repeat_unit_class=StrRepeatUnitClass.NON_STR_INDEL,
        repeat_unit_size_bp=0,
        motif_class=StrMotifClass.MONOMORPHIC,
        canonical_motif_sequence="Single-copy Y gene confirmation",
        observed_allele_spectrum=("Present", "Absent"),
        documented_microvariants=(),
        max_reverse_stutter_ratio=0.000,
        germline_mutation_rate_10k=0.00,
        stepwise_mutation_r=1.000,
        is_codis_core=False,
        dye_channel_default="RED",
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# 3. MICRO-VARIANT STRUCTURAL CATALOG (13 ADMISSIBLE LOCI)
# ═══════════════════════════════════════════════════════════════════════════════

MICROVARIANT_MUTATIONAL_CATALOG: Dict[str, List[MicrovariantDetail]] = {
    "TH01": [
        MicrovariantDetail(
            locus_name="TH01",
            fractional_allele="9.3",
            integer_base_repeat=9,
            fractional_offset=0.3,
            delta_bp=3,
            alternate_delta_bp=-1,
            sequence_representation="[AATG]6 ATG [AATG]3",
            etiology_description="Single-base deletion of Adenine in 7th unit of [AATG]10, creating an ATG trinucleotide insert",
            etiology_class=MicrovariantEtiologyClass.SINGLE_BASE_DELETION,
        ),
        MicrovariantDetail(
            locus_name="TH01",
            fractional_allele="8.3",
            integer_base_repeat=8,
            fractional_offset=0.3,
            delta_bp=3,
            alternate_delta_bp=-1,
            sequence_representation="[AATG]5 ATG [AATG]3",
            etiology_description="Single-base deletion within 9-repeat array",
            etiology_class=MicrovariantEtiologyClass.SINGLE_BASE_DELETION,
        ),
        MicrovariantDetail(
            locus_name="TH01",
            fractional_allele="10.3",
            integer_base_repeat=10,
            fractional_offset=0.3,
            delta_bp=3,
            alternate_delta_bp=-1,
            sequence_representation="[AATG]7 ATG [AATG]3",
            etiology_description="Single-base deletion within 11-repeat array",
            etiology_class=MicrovariantEtiologyClass.SINGLE_BASE_DELETION,
        ),
    ],
    "FGA": [
        MicrovariantDetail(
            locus_name="FGA",
            fractional_allele="21.2",
            integer_base_repeat=21,
            fractional_offset=0.2,
            delta_bp=2,
            alternate_delta_bp=None,
            sequence_representation="[GGAA]2 GGAG [AAAG]n AG [AAAG]m AGAA AAAA [GAAA]3",
            etiology_description="Dinucleotide AG insertion/deletion within the variable AAAG repeat block",
            etiology_class=MicrovariantEtiologyClass.DINUCLEOTIDE_INDEL,
        ),
        MicrovariantDetail(
            locus_name="FGA",
            fractional_allele="22.2",
            integer_base_repeat=22,
            fractional_offset=0.2,
            delta_bp=2,
            alternate_delta_bp=None,
            sequence_representation="[GGAA]2 GGAG [AAAG]n AG [AAAG]m AGAA AAAA [GAAA]3",
            etiology_description="Slipped-strand mispairing inducing a 2-bp AG deletion within AAAG array",
            etiology_class=MicrovariantEtiologyClass.DINUCLEOTIDE_INDEL,
        ),
        MicrovariantDetail(
            locus_name="FGA",
            fractional_allele="26.2",
            integer_base_repeat=26,
            fractional_offset=0.2,
            delta_bp=2,
            alternate_delta_bp=None,
            sequence_representation="[GGAA]2 GGAG [AAAG]n AG [AAAG]m AGAA AAAA [GAAA]3",
            etiology_description="Internal AG dinucleotide unit insertion in high-molecular weight FGA allele",
            etiology_class=MicrovariantEtiologyClass.DINUCLEOTIDE_INDEL,
        ),
    ],
    "D21S11": [
        MicrovariantDetail(
            locus_name="D21S11",
            fractional_allele="28.2",
            integer_base_repeat=28,
            fractional_offset=0.2,
            delta_bp=2,
            alternate_delta_bp=None,
            sequence_representation="[TCTA]n [TCTG]m [TCTA]3 TA [TCTA]3 TCA [TCTA]2 TCTA [TCTG]p [TCTA]q",
            etiology_description="Retention of an internal non-repeating TA dinucleotide invariant block",
            etiology_class=MicrovariantEtiologyClass.DINUCLEOTIDE_INDEL,
        ),
        MicrovariantDetail(
            locus_name="D21S11",
            fractional_allele="29.2",
            integer_base_repeat=29,
            fractional_offset=0.2,
            delta_bp=2,
            alternate_delta_bp=None,
            sequence_representation="[TCTA]n [TCTG]m [TCTA]3 TA [TCTA]3 TCA [TCTA]2 TCTA [TCTG]p [TCTA]q",
            etiology_description="Complex motif shift with internal TA insert adjacent to TCA linker",
            etiology_class=MicrovariantEtiologyClass.DINUCLEOTIDE_INDEL,
        ),
        MicrovariantDetail(
            locus_name="D21S11",
            fractional_allele="30.2",
            integer_base_repeat=30,
            fractional_offset=0.2,
            delta_bp=2,
            alternate_delta_bp=None,
            sequence_representation="[TCTA]n [TCTG]m [TCTA]3 TA [TCTA]3 TCA [TCTA]2 TCTA [TCTG]p [TCTA]q",
            etiology_description="Internal TA dinucleotide invariant insertion in 30-repeat array",
            etiology_class=MicrovariantEtiologyClass.DINUCLEOTIDE_INDEL,
        ),
        MicrovariantDetail(
            locus_name="D21S11",
            fractional_allele="31.2",
            integer_base_repeat=31,
            fractional_offset=0.2,
            delta_bp=2,
            alternate_delta_bp=None,
            sequence_representation="[TCTA]n [TCTG]m [TCTA]3 TA [TCTA]3 TCA [TCTA]2 TCTA [TCTG]p [TCTA]q",
            etiology_description="Common European/African 31.2 allele with TA dinucleotide insertion",
            etiology_class=MicrovariantEtiologyClass.DINUCLEOTIDE_INDEL,
        ),
    ],
    "D1S1656": [
        MicrovariantDetail(
            locus_name="D1S1656",
            fractional_allele="14.3",
            integer_base_repeat=14,
            fractional_offset=0.3,
            delta_bp=3,
            alternate_delta_bp=-1,
            sequence_representation="CCTA [TCTA]n TCA [TCTA]m",
            etiology_description="Inclusion of a 3-bp TCA trinucleotide unit situated between CCTA and TCTA blocks",
            etiology_class=MicrovariantEtiologyClass.TRINUCLEOTIDE_INSERTION,
        ),
        MicrovariantDetail(
            locus_name="D1S1656",
            fractional_allele="15.3",
            integer_base_repeat=15,
            fractional_offset=0.3,
            delta_bp=3,
            alternate_delta_bp=-1,
            sequence_representation="CCTA [TCTA]n TCA [TCTA]m",
            etiology_description="Trinucleotide TCA unit insertion between variable TCTA repeats",
            etiology_class=MicrovariantEtiologyClass.TRINUCLEOTIDE_INSERTION,
        ),
        MicrovariantDetail(
            locus_name="D1S1656",
            fractional_allele="17.3",
            integer_base_repeat=17,
            fractional_offset=0.3,
            delta_bp=3,
            alternate_delta_bp=-1,
            sequence_representation="CCTA [TCTA]n TCA [TCTA]m",
            etiology_description="High-frequency European 17.3 allele with TCA linker insertion",
            etiology_class=MicrovariantEtiologyClass.TRINUCLEOTIDE_INSERTION,
        ),
    ],
    "D2S441": [
        MicrovariantDetail(
            locus_name="D2S441",
            fractional_allele="10.3",
            integer_base_repeat=10,
            fractional_offset=0.3,
            delta_bp=3,
            alternate_delta_bp=-1,
            sequence_representation="[TCTA]n TCA [TCTA]m",
            etiology_description="Insertion of a 3-bp TCA trinucleotide motif interrupting the tetranucleotide repeat structure",
            etiology_class=MicrovariantEtiologyClass.TRINUCLEOTIDE_INSERTION,
        ),
        MicrovariantDetail(
            locus_name="D2S441",
            fractional_allele="11.3",
            integer_base_repeat=11,
            fractional_offset=0.3,
            delta_bp=3,
            alternate_delta_bp=-1,
            sequence_representation="[TCTA]n TCA [TCTA]m",
            etiology_description="Diagnostic 11.3 microvariant with internal TCA trinucleotide insertion",
            etiology_class=MicrovariantEtiologyClass.TRINUCLEOTIDE_INSERTION,
        ),
    ],
    "D19S433": [
        MicrovariantDetail(
            locus_name="D19S433",
            fractional_allele="12.2",
            integer_base_repeat=12,
            fractional_offset=0.2,
            delta_bp=2,
            alternate_delta_bp=None,
            sequence_representation="[AAGG]n AG [TAGG]m",
            etiology_description="Retention of an AG dinucleotide transition motif between AAGG and TAGG blocks",
            etiology_class=MicrovariantEtiologyClass.DINUCLEOTIDE_INDEL,
        ),
        MicrovariantDetail(
            locus_name="D19S433",
            fractional_allele="13.2",
            integer_base_repeat=13,
            fractional_offset=0.2,
            delta_bp=2,
            alternate_delta_bp=None,
            sequence_representation="[AAGG]n AG [TAGG]m",
            etiology_description="Compound dinucleotide AG bridge retention in 13-repeat allele",
            etiology_class=MicrovariantEtiologyClass.DINUCLEOTIDE_INDEL,
        ),
        MicrovariantDetail(
            locus_name="D19S433",
            fractional_allele="14.2",
            integer_base_repeat=14,
            fractional_offset=0.2,
            delta_bp=2,
            alternate_delta_bp=None,
            sequence_representation="[AAGG]n AG [TAGG]m",
            etiology_description="High-frequency African American 14.2 allele with AG dinucleotide bridge",
            etiology_class=MicrovariantEtiologyClass.DINUCLEOTIDE_INDEL,
        ),
        MicrovariantDetail(
            locus_name="D19S433",
            fractional_allele="15.2",
            integer_base_repeat=15,
            fractional_offset=0.2,
            delta_bp=2,
            alternate_delta_bp=None,
            sequence_representation="[AAGG]n AG [TAGG]m",
            etiology_description="Dinucleotide AG transition bridge in 15-repeat allele",
            etiology_class=MicrovariantEtiologyClass.DINUCLEOTIDE_INDEL,
        ),
    ],
    "SE33": [
        MicrovariantDetail(
            locus_name="SE33",
            fractional_allele="22.2",
            integer_base_repeat=22,
            fractional_offset=0.2,
            delta_bp=2,
            alternate_delta_bp=None,
            sequence_representation="[AAAG]n AG [AAAG]m",
            etiology_description="Hypervariable AG dinucleotide frameshift in complex AAAG array",
            etiology_class=MicrovariantEtiologyClass.COMPLEX_ARRAY_FRAMESHIFT,
        ),
        MicrovariantDetail(
            locus_name="SE33",
            fractional_allele="26.2",
            integer_base_repeat=26,
            fractional_offset=0.2,
            delta_bp=2,
            alternate_delta_bp=None,
            sequence_representation="[AAAG]n AG [AAAG]m",
            etiology_description="Complex AAAG array with dinucleotide AG insert",
            etiology_class=MicrovariantEtiologyClass.COMPLEX_ARRAY_FRAMESHIFT,
        ),
        MicrovariantDetail(
            locus_name="SE33",
            fractional_allele="27.2",
            integer_base_repeat=27,
            fractional_offset=0.2,
            delta_bp=2,
            alternate_delta_bp=None,
            sequence_representation="[AAAG]n AG [AAAG]m",
            etiology_description="Internal AG dinucleotide insertion in 27-repeat complex allele",
            etiology_class=MicrovariantEtiologyClass.COMPLEX_ARRAY_FRAMESHIFT,
        ),
        MicrovariantDetail(
            locus_name="SE33",
            fractional_allele="28.2",
            integer_base_repeat=28,
            fractional_offset=0.2,
            delta_bp=2,
            alternate_delta_bp=None,
            sequence_representation="[AAAG]n AG [AAAG]m",
            etiology_description="High-frequency European 28.2 allele with complex dinucleotide frameshift",
            etiology_class=MicrovariantEtiologyClass.COMPLEX_ARRAY_FRAMESHIFT,
        ),
        MicrovariantDetail(
            locus_name="SE33",
            fractional_allele="30.2",
            integer_base_repeat=30,
            fractional_offset=0.2,
            delta_bp=2,
            alternate_delta_bp=None,
            sequence_representation="[AAAG]n AG [AAAG]m",
            etiology_description="Internal AG dinucleotide frameshift in 30-repeat allele",
            etiology_class=MicrovariantEtiologyClass.COMPLEX_ARRAY_FRAMESHIFT,
        ),
        MicrovariantDetail(
            locus_name="SE33",
            fractional_allele="31.2",
            integer_base_repeat=31,
            fractional_offset=0.2,
            delta_bp=2,
            alternate_delta_bp=None,
            sequence_representation="[AAAG]n AG [AAAG]m",
            etiology_description="Internal AG dinucleotide frameshift in 31-repeat allele",
            etiology_class=MicrovariantEtiologyClass.COMPLEX_ARRAY_FRAMESHIFT,
        ),
    ],
    "D12S391": [
        MicrovariantDetail(
            locus_name="D12S391",
            fractional_allele="17.3",
            integer_base_repeat=17,
            fractional_offset=0.3,
            delta_bp=3,
            alternate_delta_bp=-1,
            sequence_representation="[AGAT]n AGA [AGAC]m",
            etiology_description="Single base deletion producing a 3-bp AGA inter-block linker between AGAT and AGAC domains",
            etiology_class=MicrovariantEtiologyClass.SINGLE_BASE_DELETION,
        ),
        MicrovariantDetail(
            locus_name="D12S391",
            fractional_allele="18.3",
            integer_base_repeat=18,
            fractional_offset=0.3,
            delta_bp=3,
            alternate_delta_bp=-1,
            sequence_representation="[AGAT]n AGA [AGAC]m",
            etiology_description="Single-base deletion boundary linker in 18-repeat allele",
            etiology_class=MicrovariantEtiologyClass.SINGLE_BASE_DELETION,
        ),
        MicrovariantDetail(
            locus_name="D12S391",
            fractional_allele="19.3",
            integer_base_repeat=19,
            fractional_offset=0.3,
            delta_bp=3,
            alternate_delta_bp=-1,
            sequence_representation="[AGAT]n AGA [AGAC]m",
            etiology_description="Single-base deletion boundary linker in 19-repeat allele",
            etiology_class=MicrovariantEtiologyClass.SINGLE_BASE_DELETION,
        ),
    ],
    "Penta D": [
        MicrovariantDetail(
            locus_name="Penta D",
            fractional_allele="2.2",
            integer_base_repeat=2,
            fractional_offset=0.2,
            delta_bp=2,
            alternate_delta_bp=-3,
            sequence_representation="[AAAGA]n AA",
            etiology_description="Partial pentanucleotide repeat collapse resulting in a residual AA dinucleotide unit",
            etiology_class=MicrovariantEtiologyClass.PARTIAL_REPEAT_COLLAPSE,
        ),
        MicrovariantDetail(
            locus_name="Penta D",
            fractional_allele="3.2",
            integer_base_repeat=3,
            fractional_offset=0.2,
            delta_bp=2,
            alternate_delta_bp=-3,
            sequence_representation="[AAAGA]n AA",
            etiology_description="Partial pentanucleotide repeat collapse in 3-repeat allele",
            etiology_class=MicrovariantEtiologyClass.PARTIAL_REPEAT_COLLAPSE,
        ),
    ],
    "D22S1045": [
        MicrovariantDetail(
            locus_name="D22S1045",
            fractional_allele="14.1",
            integer_base_repeat=14,
            fractional_offset=0.1,
            delta_bp=1,
            alternate_delta_bp=-2,
            sequence_representation="[ATT]n A",
            etiology_description="Single-base insertion following a trinucleotide array yielding a fractional +1 bp displacement",
            etiology_class=MicrovariantEtiologyClass.SINGLE_BASE_INSERTION,
        ),
        MicrovariantDetail(
            locus_name="D22S1045",
            fractional_allele="15.1",
            integer_base_repeat=15,
            fractional_offset=0.1,
            delta_bp=1,
            alternate_delta_bp=-2,
            sequence_representation="[ATT]n A",
            etiology_description="Trinucleotide single-base A insertion in 15-repeat allele",
            etiology_class=MicrovariantEtiologyClass.SINGLE_BASE_INSERTION,
        ),
    ],
    "D7S820": [
        MicrovariantDetail(
            locus_name="D7S820",
            fractional_allele="8.1",
            integer_base_repeat=8,
            fractional_offset=0.1,
            delta_bp=1,
            alternate_delta_bp=None,
            sequence_representation="[GATA]n T",
            etiology_description="Single Thymine or Adenine insertion adjacent to the downstream flanking region",
            etiology_class=MicrovariantEtiologyClass.SINGLE_BASE_INSERTION,
        ),
        MicrovariantDetail(
            locus_name="D7S820",
            fractional_allele="9.1",
            integer_base_repeat=9,
            fractional_offset=0.1,
            delta_bp=1,
            alternate_delta_bp=None,
            sequence_representation="[GATA]n T",
            etiology_description="Flanking single-base insertion in 9-repeat allele",
            etiology_class=MicrovariantEtiologyClass.SINGLE_BASE_INSERTION,
        ),
    ],
    "D18S51": [
        MicrovariantDetail(
            locus_name="D18S51",
            fractional_allele="10.2",
            integer_base_repeat=10,
            fractional_offset=0.2,
            delta_bp=2,
            alternate_delta_bp=None,
            sequence_representation="[AGAA]n AG",
            etiology_description="Dinucleotide AG addition within simple tetranucleotide repeat structure",
            etiology_class=MicrovariantEtiologyClass.DINUCLEOTIDE_INDEL,
        ),
        MicrovariantDetail(
            locus_name="D18S51",
            fractional_allele="13.2",
            integer_base_repeat=13,
            fractional_offset=0.2,
            delta_bp=2,
            alternate_delta_bp=None,
            sequence_representation="[AGAA]n AG",
            etiology_description="Dinucleotide AG addition in 13-repeat allele",
            etiology_class=MicrovariantEtiologyClass.DINUCLEOTIDE_INDEL,
        ),
        MicrovariantDetail(
            locus_name="D18S51",
            fractional_allele="14.2",
            integer_base_repeat=14,
            fractional_offset=0.2,
            delta_bp=2,
            alternate_delta_bp=None,
            sequence_representation="[AGAA]n AG",
            etiology_description="Dinucleotide AG addition in 14-repeat allele",
            etiology_class=MicrovariantEtiologyClass.DINUCLEOTIDE_INDEL,
        ),
    ],
    "Penta E": [
        MicrovariantDetail(
            locus_name="Penta E",
            fractional_allele="10.4",
            integer_base_repeat=10,
            fractional_offset=0.4,
            delta_bp=4,
            alternate_delta_bp=-1,
            sequence_representation="[AAAGA]n AAAG",
            etiology_description="Single base deletion from pentanucleotide unit resulting in a 4-bp residual fragment",
            etiology_class=MicrovariantEtiologyClass.SINGLE_BASE_DELETION,
        ),
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# 4. BIOCOMPUTATIONAL HELPER ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class StrLocusRegistryEngine:
    """
    Core computational engine for 24-STR locus metadata, micro-variant parsing,
    Stepwise Mutation Model (SMM) dynamics, and capillary sizing verification.
    """

    @classmethod
    def get_locus_metadata(cls, locus_name: str) -> Optional[StrLocusMetadata]:
        """Retrieves frozen metadata for a given locus name (case-insensitive)."""
        normalized = locus_name.strip()
        # Direct lookup
        if normalized in STR_LOCUS_24_MASTER_REGISTRY:
            return STR_LOCUS_24_MASTER_REGISTRY[normalized]
        # Case-insensitive lookup
        for name, meta in STR_LOCUS_24_MASTER_REGISTRY.items():
            if name.lower() == normalized.lower():
                return meta
        return None

    @classmethod
    def is_valid_locus(cls, locus_name: str) -> bool:
        """Returns True if the locus is recognized in the master registry."""
        return cls.get_locus_metadata(locus_name) is not None

    @classmethod
    def is_microvariant(cls, allele_str: str) -> bool:
        """Determines if an allele call contains a decimal fractional repeat (e.g. '9.3', '28.2')."""
        clean = allele_str.strip().replace("[", "").replace("]", "")
        if clean in ("X", "Y", "0", "[0]", "Present", "Absent", "?", "OL"):
            return False
        try:
            val = float(clean)
            return not val.is_integer()
        except ValueError:
            return False

    @classmethod
    def parse_repeat_and_fraction(cls, allele_str: str) -> Tuple[int, float]:
        """
        Parses allele string into integer repeat and fractional portion.
        Example: '9.3' -> (9, 0.3); '15' -> (15, 0.0)
        """
        clean = allele_str.strip().replace("[", "").replace("]", "")
        try:
            val = float(clean)
            integer_part = int(math.floor(val))
            fraction_part = round(val - integer_part, 2)
            return integer_part, fraction_part
        except ValueError:
            return 0, 0.0

    @classmethod
    def get_microvariant_details(cls, locus_name: str, allele_str: str) -> Optional[MicrovariantDetail]:
        """
        Looks up specific micro-variant etiology from the curated catalog.
        Returns None if the locus or allele is not a cataloged microvariant.
        """
        meta = cls.get_locus_metadata(locus_name)
        if not meta:
            return None
        norm_name = meta.locus_name
        clean_allele = allele_str.strip().replace("[", "").replace("]", "")

        variants = MICROVARIANT_MUTATIONAL_CATALOG.get(norm_name, [])
        for v in variants:
            if v.fractional_allele == clean_allele:
                return v

        # If not explicitly in catalog but is microvariant, generate computed detail
        if cls.is_microvariant(clean_allele):
            int_part, frac_part = cls.parse_repeat_and_fraction(clean_allele)
            bp_delta = int(round(frac_part * 10))
            return MicrovariantDetail(
                locus_name=norm_name,
                fractional_allele=clean_allele,
                integer_base_repeat=int_part,
                fractional_offset=frac_part,
                delta_bp=bp_delta,
                alternate_delta_bp=bp_delta - meta.repeat_unit_size_bp if meta.repeat_unit_size_bp > 0 else None,
                sequence_representation=f"{meta.canonical_motif_sequence} (+{bp_delta}bp)",
                etiology_description=f"Fractional repeat allele with +{bp_delta} bp insertion relative to repeat {int_part}",
                etiology_class=MicrovariantEtiologyClass.SINGLE_BASE_INSERTION if bp_delta == 1 else MicrovariantEtiologyClass.DINUCLEOTIDE_INDEL,
            )
        return None

    @classmethod
    def calculate_smm_transition_probability(
        cls,
        locus_name: str,
        allele_i: float,
        allele_j: float,
    ) -> float:
        """
        Computes transition probability under the Stepwise Mutation Model (SMM):
        P(i -> j) = (1 - r) * r^(|i - j| - 1)
        """
        meta = cls.get_locus_metadata(locus_name)
        r = meta.stepwise_mutation_r if meta else 0.850
        diff = abs(allele_i - allele_j)

        if diff < 1e-6:
            # Identity (no mutation)
            return 1.0 - (meta.germline_mutation_rate_10k * 1e-3 if meta else 0.001)

        steps = int(round(diff))
        if steps < 1:
            steps = 1

        # SMM formulation
        p_step = (1.0 - r) * (r ** (steps - 1))
        # Scaled by overall mutation rate
        mu = meta.germline_mutation_rate_10k * 1e-3 if meta else 0.001
        return mu * p_step * 0.5  # 0.5 for bidirectional expansion/contraction

    @classmethod
    def calculate_allele_size_bp(
        cls,
        locus_name: str,
        allele_str: str,
        base_offset: float = 60.0,
    ) -> float:
        """
        Calculates electrophoretic base-pair migration size:
        bp(a) = offset_L + integer_repeats * unit_size + micro_delta
        """
        meta = cls.get_locus_metadata(locus_name)
        clean = allele_str.strip().replace("[", "").replace("]", "")
        if locus_name.lower() == "amelogenin" or (meta and meta.repeat_unit_class == StrRepeatUnitClass.NON_STR_INDEL):
            if clean.upper() == "X":
                return 106.0
            elif clean.upper() == "Y":
                return 112.0
            elif clean.lower() == "present":
                return 517.0
            return base_offset

        if not meta:
            return base_offset

        mv = cls.get_microvariant_details(locus_name, clean)
        if mv:
            return base_offset + (mv.integer_base_repeat * meta.repeat_unit_size_bp) + mv.delta_bp
        try:
            num = float(clean)
            return base_offset + (num * meta.repeat_unit_size_bp)
        except ValueError:
            return base_offset

    @classmethod
    def get_all_loci_names(cls) -> List[str]:
        """Returns ordered list of all 24 loci names."""
        return list(STR_LOCUS_24_MASTER_REGISTRY.keys())

    @classmethod
    def get_codis_core_loci_names(cls) -> List[str]:
        """Returns the list of 20 FBI CODIS core loci."""
        return [k for k, v in STR_LOCUS_24_MASTER_REGISTRY.items() if v.is_codis_core and v.repeat_unit_class != StrRepeatUnitClass.NON_STR_INDEL]

    @classmethod
    def get_microvariant_loci_names(cls) -> List[str]:
        """Returns list of 13 loci with documented microvariants."""
        return list(MICROVARIANT_MUTATIONAL_CATALOG.keys())
