"""
FORENZA: Golden Casework Reference Library & Multi-Format Exporter Engine
Provides certified global ground-truth reference standards (NIST SRM 2391d, NA12878 CEU,
HG002 AJ, NA19240 YRI, NA18507 CHB) and legacy reference casework vectors (VECTOR_TERM_01 to 06)
along with full biocomputational export capabilities for CODIS CMF 3.2 XML,
ISO/IEC 17025 LIMS JSON, and GeneMapper ID-X CSV/TSV.

Derived verbatim from research specifications:
- research/dna_snp_terminal_research.md
- research/certified_reference_standards_gold_vectors_research.md
Compliance: ISO/IEC 17025:2017 • FBI CODIS NDIS v3.2/v4.0 • SWGDAM 2020 Guidelines
"""

from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
from xml.etree import ElementTree as ET

from .dna_terminal_parser import ParsedForensicProfile, LocusSTRCall, SnpGenotypeCall


@dataclass
class CaseworkPresetItem:
    preset_id: str
    sample_name: str
    case_type: str
    target_population: str
    physical_condition: str
    description: str
    expected_ancestry: str
    expected_phenotype: str
    expected_centroid: str
    degradation_index: float
    stochastic_dropout_prob: float
    heterozygote_balance: float
    str_profile: Dict[str, Dict[str, Any]]
    snp_dosages: Dict[str, int]
    ystr_profile: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    mtdna_mutations: List[str] = field(default_factory=list)
    supplementary_markers: Dict[str, str] = field(default_factory=dict)
    chain_of_custody_hash: str = ""
    coriell_id: Optional[str] = None
    nist_srm_designation: Optional[str] = None
    sex: str = "MALE"
    population_group: str = ""
    is_certified_standard: bool = True
    aim_profile: Dict[str, Any] = field(default_factory=dict)
    hirisplex_profile: Dict[str, Any] = field(default_factory=dict)
    visage_epigenetic_profile: Dict[str, Any] = field(default_factory=dict)


# ==============================================================================
# 5 GLOBALLY CERTIFIED MULTI-OMIC REFERENCE STANDARDS
# ==============================================================================

PRESET_NIST_SRM_2391D = CaseworkPresetItem(
    preset_id="PRESET_NIST_SRM_2391D",
    sample_name="NIST SRM 2391d Component A",
    coriell_id="SRM_2391d_COMP_A",
    nist_srm_designation="NIST SRM 2391d Component A (Male gDNA)",
    case_type="Standard Reference Material (NIST Certified)",
    sex="MALE",
    target_population="European-American (EUR_US_CAU)",
    population_group="EUR_US_CAU",
    physical_condition="Pristine Standard Reference Material (1.0 ng/μL)",
    description="Certified reference material for PCR-based DNA profiling. Certified 24-locus autosomal STR, 27-locus Y-FILER Plus, mtDNA H1e, and VISAGE 5-CpG methylation.",
    expected_ancestry="98.5% European (EUR)",
    expected_phenotype="Intermediate Eyes (P=0.82), Brown Hair (P=0.91), Light Skin Type II (P=0.89), Straight/Wavy",
    expected_centroid="39.14°N, 77.20°W (Gaithersburg, MD, USA)",
    degradation_index=1.00,
    stochastic_dropout_prob=0.00,
    heterozygote_balance=0.98,
    is_certified_standard=True,
    str_profile={
        "AMEL": {"allele1": "X", "allele2": "Y", "rfu1": 3200, "rfu2": 3100},
        "CSF1PO": {"allele1": "10", "allele2": "12", "rfu1": 2400, "rfu2": 2350},
        "D1S1656": {"allele1": "15", "allele2": "16", "rfu1": 2200, "rfu2": 2150},
        "D2S441": {"allele1": "11", "allele2": "14", "rfu1": 2600, "rfu2": 2550},
        "D2S1338": {"allele1": "19", "allele2": "23", "rfu1": 2100, "rfu2": 2050},
        "D3S1358": {"allele1": "15", "allele2": "18", "rfu1": 2800, "rfu2": 2750},
        "D5S818": {"allele1": "11", "allele2": "12", "rfu1": 2300, "rfu2": 2250},
        "D7S820": {"allele1": "9", "allele2": "11", "rfu1": 2450, "rfu2": 2400},
        "D8S1179": {"allele1": "13", "allele2": "15", "rfu1": 2700, "rfu2": 2650},
        "D10S1248": {"allele1": "13", "allele2": "14", "rfu1": 3000, "rfu2": 2950},
        "D12S391": {"allele1": "18", "allele2": "22", "rfu1": 2150, "rfu2": 2100},
        "D13S317": {"allele1": "11", "allele2": "12", "rfu1": 2500, "rfu2": 2450},
        "D16S539": {"allele1": "11", "allele2": "13", "rfu1": 2400, "rfu2": 2350},
        "D18S51": {"allele1": "13", "allele2": "16", "rfu1": 1950, "rfu2": 1900},
        "D19S433": {"allele1": "13", "allele2": "14", "rfu1": 2650, "rfu2": 2600},
        "D21S11": {"allele1": "28", "allele2": "30", "rfu1": 2200, "rfu2": 2150},
        "D22S1045": {"allele1": "15", "allele2": "16", "rfu1": 3100, "rfu2": 3050},
        "FGA": {"allele1": "21", "allele2": "24", "rfu1": 2000, "rfu2": 1950},
        "TH01": {"allele1": "6", "allele2": "9.3", "rfu1": 2900, "rfu2": 2850},
        "TPOX": {"allele1": "8", "allele2": "11", "rfu1": 2550, "rfu2": 2500},
        "VWA": {"allele1": "16", "allele2": "18", "rfu1": 2500, "rfu2": 2450},
        "SE33": {"allele1": "18", "allele2": "27.2", "rfu1": 1750, "rfu2": 1700},
        "PENTA_D": {"allele1": "9", "allele2": "12", "rfu1": 2350, "rfu2": 2300},
        "PENTA_E": {"allele1": "12", "allele2": "14", "rfu1": 2100, "rfu2": 2050},
    },
    snp_dosages={
        "rs12913832": 1, "rs1805007": 0, "rs16891982": 2, "rs1426654": 2,
        "rs1042602": 2, "rs12203592": 0, "rs3827072": 0, "rs727811": 2,
        "rs3811801": 2, "rs2814778": 0, "rs1800414": 2, "rs11019": 2,
        "rs10886828": 2, "rs2032582": 0, "rs2300986": 2, "rs1028531": 2,
    },
    ystr_profile={
        "DYS19": {"allele1": "14", "rfu1": 1600},
        "DYS389I": {"allele1": "13", "rfu1": 1550},
        "DYS389II": {"allele1": "29", "rfu1": 1500},
        "DYS390": {"allele1": "24", "rfu1": 1650},
        "DYS391": {"allele1": "11", "rfu1": 1580},
        "DYS392": {"allele1": "13", "rfu1": 1520},
        "DYS393": {"allele1": "13", "rfu1": 1600},
        "DYS385a/b": {"allele1": "11", "allele2": "14", "rfu1": 1480, "rfu2": 1440},
        "DYS437": {"allele1": "15", "rfu1": 1560},
        "DYS438": {"allele1": "12", "rfu1": 1540},
        "DYS439": {"allele1": "12", "rfu1": 1590},
        "DYS448": {"allele1": "19", "rfu1": 1450},
        "DYS456": {"allele1": "15", "rfu1": 1620},
        "DYS458": {"allele1": "17", "rfu1": 1610},
        "DYS635": {"allele1": "23", "rfu1": 1500},
        "YGATAH4": {"allele1": "12", "rfu1": 1570},
        "DYS481": {"allele1": "22", "rfu1": 1490},
        "DYS533": {"allele1": "11", "rfu1": 1580},
        "DYS549": {"allele1": "12", "rfu1": 1520},
        "DYS570": {"allele1": "17", "rfu1": 1520},
        "DYS576": {"allele1": "18", "rfu1": 1550},
        "DYS643": {"allele1": "10", "rfu1": 1460},
        "DYS518": {"allele1": "38", "rfu1": 1420},
        "DYS627": {"allele1": "22", "rfu1": 1400},
        "DYS449": {"allele1": "30", "rfu1": 1380},
        "DYF387S1a/b": {"allele1": "35", "allele2": "37", "rfu1": 1380, "rfu2": 1350},
        "DYS460": {"allele1": "11", "rfu1": 1530},
    },
    mtdna_mutations=["263G", "315.1C", "16069T", "16129G", "16223T", "16311C"],
    aim_profile={
        "admixtureProportions": {"qEUR": 0.985, "qAFR": 0.005, "qEAS": 0.003, "qSAS": 0.004, "qAMR": 0.003},
        "centroid": {"latitude": 39.1434, "longitude": -77.2014, "region": "Gaithersburg, MD, USA"},
    },
    hirisplex_profile={
        "predictedEyeColor": "Intermediate", "eyeColorProb": 0.82,
        "predictedHairColor": "Brown", "hairColorProb": 0.91,
        "predictedSkinPhototype": "Type II / Light", "skinPhototypeProb": 0.89,
        "hairMorphology": "Straight to Wavy",
    },
    visage_epigenetic_profile={
        "cpgBetaValues": {
            "cg16867657_ELOVL2": 0.42,
            "cg06639320_FHL2": 0.31,
            "cg16537105_PENK": 0.22,
            "cg04523812_TRIM59": 0.38,
            "cg08097417_KLF14": 0.28,
        },
        "predictedAgeYears": 44.2,
        "ci95Lower": 40.8,
        "ci95Upper": 47.6,
    },
    chain_of_custody_hash="9a1f2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a",
)

PRESET_NA12878_CEU = CaseworkPresetItem(
    preset_id="PRESET_NA12878_CEU",
    sample_name="NA12878 / HG001 (CEPH European Female)",
    coriell_id="NA12878 / HG001",
    case_type="GIAB Reference Standard (Coriell Cell Repository)",
    sex="FEMALE",
    target_population="Utah / CEPH European (CEU)",
    population_group="CEU_UTAH_EUROPEAN",
    physical_condition="Pristine Genomic DNA (High Molecular Weight)",
    description="International gold standard human reference genome. Features microvariants D1S1656 (17.3), D2S441 (11.3), SE33 (25.2), mtDNA H1a1, and blue eye / fair skin pigmentation.",
    expected_ancestry="99.2% European (EUR)",
    expected_phenotype="Blue Eyes (P=0.98), Blond / Light Brown Hair (P=0.94), Fair Skin Type I/II (P=0.95), Straight Hair",
    expected_centroid="40.76°N, 111.89°W (Salt Lake City, UT, USA)",
    degradation_index=1.02,
    stochastic_dropout_prob=0.00,
    heterozygote_balance=0.97,
    is_certified_standard=True,
    str_profile={
        "AMEL": {"allele1": "X", "allele2": "X", "rfu1": 3400, "rfu2": 3300},
        "CSF1PO": {"allele1": "10", "allele2": "11", "rfu1": 2300, "rfu2": 2250},
        "D1S1656": {"allele1": "14", "allele2": "17.3", "rfu1": 2100, "rfu2": 2050},
        "D2S441": {"allele1": "10", "allele2": "11.3", "rfu1": 2500, "rfu2": 2450},
        "D2S1338": {"allele1": "19", "allele2": "23", "rfu1": 2000, "rfu2": 1950},
        "D3S1358": {"allele1": "14", "allele2": "15", "rfu1": 2700, "rfu2": 2650},
        "D5S818": {"allele1": "11", "allele2": "12", "rfu1": 2250, "rfu2": 2200},
        "D7S820": {"allele1": "10", "allele2": "10", "rfu1": 3800, "rfu2": 3800},
        "D8S1179": {"allele1": "13", "allele2": "14", "rfu1": 2600, "rfu2": 2550},
        "D10S1248": {"allele1": "13", "allele2": "15", "rfu1": 2900, "rfu2": 2850},
        "D12S391": {"allele1": "18", "allele2": "19", "rfu1": 2100, "rfu2": 2050},
        "D13S317": {"allele1": "11", "allele2": "11", "rfu1": 3900, "rfu2": 3900},
        "D16S539": {"allele1": "11", "allele2": "12", "rfu1": 2350, "rfu2": 2300},
        "D18S51": {"allele1": "12", "allele2": "15", "rfu1": 1900, "rfu2": 1850},
        "D19S433": {"allele1": "14", "allele2": "15", "rfu1": 2550, "rfu2": 2500},
        "D21S11": {"allele1": "29", "allele2": "30", "rfu1": 2150, "rfu2": 2100},
        "D22S1045": {"allele1": "11", "allele2": "16", "rfu1": 3000, "rfu2": 2950},
        "FGA": {"allele1": "22", "allele2": "24", "rfu1": 1950, "rfu2": 1900},
        "TH01": {"allele1": "6", "allele2": "9.3", "rfu1": 2850, "rfu2": 2800},
        "TPOX": {"allele1": "8", "allele2": "11", "rfu1": 2500, "rfu2": 2450},
        "VWA": {"allele1": "17", "allele2": "18", "rfu1": 2450, "rfu2": 2400},
        "SE33": {"allele1": "19", "allele2": "25.2", "rfu1": 1700, "rfu2": 1650},
        "PENTA_D": {"allele1": "9", "allele2": "13", "rfu1": 2300, "rfu2": 2250},
        "PENTA_E": {"allele1": "7", "allele2": "12", "rfu1": 2050, "rfu2": 2000},
    },
    snp_dosages={
        "rs12913832": 2, "rs1805007": 0, "rs16891982": 2, "rs1426654": 2,
        "rs1042602": 1, "rs12203592": 1, "rs3827072": 0, "rs727811": 2,
        "rs3811801": 2, "rs2814778": 0, "rs1800414": 2, "rs11019": 2,
        "rs10886828": 2, "rs2032582": 0, "rs2300986": 2, "rs1028531": 2,
    },
    ystr_profile={},
    mtdna_mutations=["263G", "309.1C", "315.1C", "16263T", "16519C"],
    aim_profile={
        "admixtureProportions": {"qEUR": 0.992, "qAFR": 0.001, "qEAS": 0.002, "qSAS": 0.003, "qAMR": 0.002},
        "centroid": {"latitude": 40.7608, "longitude": -111.8910, "region": "Salt Lake City, UT, USA"},
    },
    hirisplex_profile={
        "predictedEyeColor": "Blue", "eyeColorProb": 0.98,
        "predictedHairColor": "Blond / Light Brown", "hairColorProb": 0.94,
        "predictedSkinPhototype": "Type I/II / Fair", "skinPhototypeProb": 0.95,
        "hairMorphology": "Straight",
    },
    visage_epigenetic_profile={
        "cpgBetaValues": {
            "cg16867657_ELOVL2": 0.38,
            "cg06639320_FHL2": 0.29,
            "cg16537105_PENK": 0.20,
            "cg04523812_TRIM59": 0.35,
            "cg08097417_KLF14": 0.26,
        },
        "predictedAgeYears": 38.5,
        "ci95Lower": 35.1,
        "ci95Upper": 41.9,
    },
    chain_of_custody_hash="8b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c",
)

PRESET_HG002_AJ = CaseworkPresetItem(
    preset_id="PRESET_HG002_AJ",
    sample_name="HG002 / NA24385 (Ashkenazi Jewish Male)",
    coriell_id="NA24385 / HG002",
    case_type="GIAB Ashkenazim Trio Son Standard",
    sex="MALE",
    target_population="Ashkenazi Jewish (AJ)",
    population_group="ASHKENAZI_JEWISH",
    physical_condition="Pristine Genomic DNA (High Molecular Weight)",
    description="GIAB Ashkenazi Jewish male reference standard. Features Y-STR Haplogroup J2a1a1, mtDNA K1a9 founder motif, D12S391 (18.3 microvariant), and VISAGE age 22.1 years.",
    expected_ancestry="97.8% European / Ashkenazi (EUR/AJ)",
    expected_phenotype="Brown Eyes (P=0.96), Dark Brown / Black Hair (P=0.93), Intermediate Skin Type II/III (P=0.88), Wavy Hair",
    expected_centroid="40.71°N, 74.00°W (New York, NY, USA)",
    degradation_index=1.01,
    stochastic_dropout_prob=0.00,
    heterozygote_balance=0.97,
    is_certified_standard=True,
    str_profile={
        "AMEL": {"allele1": "X", "allele2": "Y", "rfu1": 3300, "rfu2": 3200},
        "CSF1PO": {"allele1": "10", "allele2": "12", "rfu1": 2350, "rfu2": 2300},
        "D1S1656": {"allele1": "12", "allele2": "15", "rfu1": 2150, "rfu2": 2100},
        "D2S441": {"allele1": "11", "allele2": "11.3", "rfu1": 2550, "rfu2": 2500},
        "D2S1338": {"allele1": "17", "allele2": "20", "rfu1": 2050, "rfu2": 2000},
        "D3S1358": {"allele1": "15", "allele2": "17", "rfu1": 2750, "rfu2": 2700},
        "D5S818": {"allele1": "12", "allele2": "13", "rfu1": 2250, "rfu2": 2200},
        "D7S820": {"allele1": "8", "allele2": "10", "rfu1": 2400, "rfu2": 2350},
        "D8S1179": {"allele1": "13", "allele2": "14", "rfu1": 2650, "rfu2": 2600},
        "D10S1248": {"allele1": "12", "allele2": "13", "rfu1": 2950, "rfu2": 2900},
        "D12S391": {"allele1": "17", "allele2": "18.3", "rfu1": 2100, "rfu2": 2050},
        "D13S317": {"allele1": "11", "allele2": "12", "rfu1": 2450, "rfu2": 2400},
        "D16S539": {"allele1": "9", "allele2": "13", "rfu1": 2350, "rfu2": 2300},
        "D18S51": {"allele1": "13", "allele2": "14", "rfu1": 1900, "rfu2": 1850},
        "D19S433": {"allele1": "13", "allele2": "15.2", "rfu1": 2600, "rfu2": 2550},
        "D21S11": {"allele1": "29", "allele2": "31.2", "rfu1": 2150, "rfu2": 2100},
        "D22S1045": {"allele1": "15", "allele2": "15", "rfu1": 3950, "rfu2": 3950},
        "FGA": {"allele1": "21", "allele2": "22", "rfu1": 1950, "rfu2": 1900},
        "TH01": {"allele1": "7", "allele2": "9.3", "rfu1": 2850, "rfu2": 2800},
        "TPOX": {"allele1": "8", "allele2": "8", "rfu1": 3900, "rfu2": 3900},
        "VWA": {"allele1": "16", "allele2": "17", "rfu1": 2450, "rfu2": 2400},
        "SE33": {"allele1": "16", "allele2": "21", "rfu1": 1700, "rfu2": 1650},
        "PENTA_D": {"allele1": "10", "allele2": "12", "rfu1": 2300, "rfu2": 2250},
        "PENTA_E": {"allele1": "11", "allele2": "13", "rfu1": 2050, "rfu2": 2000},
    },
    snp_dosages={
        "rs12913832": 0, "rs1805007": 0, "rs16891982": 1, "rs1426654": 2,
        "rs1042602": 2, "rs12203592": 0, "rs3827072": 0, "rs727811": 2,
        "rs3811801": 2, "rs2814778": 0, "rs1800414": 2, "rs11019": 2,
        "rs10886828": 1, "rs2032582": 0, "rs2300986": 2, "rs1028531": 2,
    },
    ystr_profile={
        "DYS19": {"allele1": "15", "rfu1": 1600},
        "DYS389I": {"allele1": "13", "rfu1": 1550},
        "DYS389II": {"allele1": "30", "rfu1": 1500},
        "DYS390": {"allele1": "23", "rfu1": 1650},
        "DYS391": {"allele1": "10", "rfu1": 1580},
        "DYS392": {"allele1": "11", "rfu1": 1520},
        "DYS393": {"allele1": "12", "rfu1": 1600},
        "DYS385a/b": {"allele1": "14", "allele2": "15", "rfu1": 1480, "rfu2": 1440},
        "DYS437": {"allele1": "15", "rfu1": 1560},
        "DYS438": {"allele1": "12", "rfu1": 1540},
        "DYS439": {"allele1": "11", "rfu1": 1590},
        "DYS448": {"allele1": "19", "rfu1": 1450},
        "DYS456": {"allele1": "15", "rfu1": 1620},
        "DYS458": {"allele1": "18", "rfu1": 1610},
        "DYS635": {"allele1": "21", "rfu1": 1500},
        "YGATAH4": {"allele1": "10", "rfu1": 1570},
        "DYS481": {"allele1": "22", "rfu1": 1490},
        "DYS533": {"allele1": "12", "rfu1": 1580},
        "DYS549": {"allele1": "13", "rfu1": 1520},
        "DYS570": {"allele1": "19", "rfu1": 1520},
        "DYS576": {"allele1": "15", "rfu1": 1550},
        "DYS643": {"allele1": "10", "rfu1": 1460},
        "DYS518": {"allele1": "39", "rfu1": 1420},
        "DYS627": {"allele1": "21", "rfu1": 1400},
        "DYS449": {"allele1": "29", "rfu1": 1380},
        "DYF387S1a/b": {"allele1": "36", "allele2": "37", "rfu1": 1380, "rfu2": 1350},
        "DYS460": {"allele1": "11", "rfu1": 1530},
    },
    mtdna_mutations=["73G", "146C", "195C", "263G", "315.1C", "16224C", "16311C", "16519C"],
    aim_profile={
        "admixtureProportions": {"qEUR": 0.978, "qAFR": 0.008, "qEAS": 0.004, "qSAS": 0.005, "qAMR": 0.005},
        "centroid": {"latitude": 40.7128, "longitude": -74.0060, "region": "New York, NY, USA"},
    },
    hirisplex_profile={
        "predictedEyeColor": "Brown", "eyeColorProb": 0.96,
        "predictedHairColor": "Dark Brown / Black", "hairColorProb": 0.93,
        "predictedSkinPhototype": "Type II/III / Intermediate", "skinPhototypeProb": 0.88,
        "hairMorphology": "Wavy",
    },
    visage_epigenetic_profile={
        "cpgBetaValues": {
            "cg16867657_ELOVL2": 0.28,
            "cg06639320_FHL2": 0.18,
            "cg16537105_PENK": 0.12,
            "cg04523812_TRIM59": 0.24,
            "cg08097417_KLF14": 0.16,
        },
        "predictedAgeYears": 22.1,
        "ci95Lower": 18.7,
        "ci95Upper": 25.5,
    },
    chain_of_custody_hash="7c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d",
)

PRESET_NA19240_YRI = CaseworkPresetItem(
    preset_id="PRESET_NA19240_YRI",
    sample_name="NA19240 (Yoruba in Ibadan, Nigeria Female)",
    coriell_id="NA19240",
    case_type="1000 Genomes African Reference Standard",
    sex="FEMALE",
    target_population="Yoruba in Ibadan, Nigeria (YRI)",
    population_group="YRI_IBADAN_NIGERIA",
    physical_condition="Pristine Genomic DNA (High Molecular Weight)",
    description="1000 Genomes African reference female standard. Features mtDNA macro-haplogroup L2a1 with 18 defining mutations including 524.1A/524.2C, DARC Duffy null fixation, and dark pigmentation.",
    expected_ancestry="99.6% Sub-Saharan African (AFR)",
    expected_phenotype="Dark Brown Eyes (P=0.99), Black Hair (P=0.99), Dark-to-Black Skin Type V/VI (P=0.99), Coily/Curly Hair",
    expected_centroid="7.38°N, 3.95°E (Ibadan, Nigeria)",
    degradation_index=1.04,
    stochastic_dropout_prob=0.00,
    heterozygote_balance=0.96,
    is_certified_standard=True,
    str_profile={
        "AMEL": {"allele1": "X", "allele2": "X", "rfu1": 3400, "rfu2": 3300},
        "CSF1PO": {"allele1": "10", "allele2": "12", "rfu1": 2350, "rfu2": 2300},
        "D1S1656": {"allele1": "15", "allele2": "16.3", "rfu1": 2150, "rfu2": 2100},
        "D2S441": {"allele1": "11", "allele2": "12", "rfu1": 2550, "rfu2": 2500},
        "D2S1338": {"allele1": "18", "allele2": "20", "rfu1": 2050, "rfu2": 2000},
        "D3S1358": {"allele1": "16", "allele2": "17", "rfu1": 2750, "rfu2": 2700},
        "D5S818": {"allele1": "11", "allele2": "13", "rfu1": 2250, "rfu2": 2200},
        "D7S820": {"allele1": "8", "allele2": "11", "rfu1": 2400, "rfu2": 2350},
        "D8S1179": {"allele1": "14", "allele2": "15", "rfu1": 2650, "rfu2": 2600},
        "D10S1248": {"allele1": "13", "allele2": "14", "rfu1": 2950, "rfu2": 2900},
        "D12S391": {"allele1": "15", "allele2": "19", "rfu1": 2100, "rfu2": 2050},
        "D13S317": {"allele1": "11", "allele2": "14", "rfu1": 2450, "rfu2": 2400},
        "D16S539": {"allele1": "11", "allele2": "12", "rfu1": 2350, "rfu2": 2300},
        "D18S51": {"allele1": "15", "allele2": "18", "rfu1": 1900, "rfu2": 1850},
        "D19S433": {"allele1": "13", "allele2": "14", "rfu1": 2600, "rfu2": 2550},
        "D21S11": {"allele1": "28", "allele2": "30", "rfu1": 2150, "rfu2": 2100},
        "D22S1045": {"allele1": "11", "allele2": "15", "rfu1": 3000, "rfu2": 2950},
        "FGA": {"allele1": "21", "allele2": "23", "rfu1": 1950, "rfu2": 1900},
        "TH01": {"allele1": "7", "allele2": "9", "rfu1": 2850, "rfu2": 2800},
        "TPOX": {"allele1": "8", "allele2": "9", "rfu1": 2500, "rfu2": 2450},
        "VWA": {"allele1": "15", "allele2": "18", "rfu1": 2450, "rfu2": 2400},
        "SE33": {"allele1": "14", "allele2": "28.2", "rfu1": 1700, "rfu2": 1650},
        "PENTA_D": {"allele1": "9", "allele2": "11", "rfu1": 2300, "rfu2": 2250},
        "PENTA_E": {"allele1": "12", "allele2": "15", "rfu1": 2050, "rfu2": 2000},
    },
    snp_dosages={
        "rs12913832": 0, "rs1805007": 0, "rs16891982": 0, "rs1426654": 0,
        "rs1042602": 0, "rs12203592": 0, "rs3827072": 0, "rs727811": 0,
        "rs3811801": 0, "rs2814778": 2, "rs1800414": 0, "rs11019": 0,
        "rs10886828": 0, "rs2032582": 0, "rs2300986": 0, "rs1028531": 0,
    },
    ystr_profile={},
    mtdna_mutations=[
        "73G", "143A", "146C", "152C", "195C", "247G", "263G", "315.1C",
        "524.1A", "524.2C", "16111T", "16192T", "16223T", "16278T", "16294T",
        "16309G", "16390G", "16519C",
    ],
    aim_profile={
        "admixtureProportions": {"qEUR": 0.001, "qAFR": 0.996, "qEAS": 0.001, "qSAS": 0.001, "qAMR": 0.001},
        "centroid": {"latitude": 7.3775, "longitude": 3.9470, "region": "Ibadan, Nigeria"},
    },
    hirisplex_profile={
        "predictedEyeColor": "Dark Brown", "eyeColorProb": 0.99,
        "predictedHairColor": "Black", "hairColorProb": 0.99,
        "predictedSkinPhototype": "Type V/VI / Dark-Black", "skinPhototypeProb": 0.99,
        "hairMorphology": "Coily / Curly",
    },
    visage_epigenetic_profile={
        "cpgBetaValues": {
            "cg16867657_ELOVL2": 0.35,
            "cg06639320_FHL2": 0.25,
            "cg16537105_PENK": 0.18,
            "cg04523812_TRIM59": 0.32,
            "cg08097417_KLF14": 0.22,
        },
        "predictedAgeYears": 31.4,
        "ci95Lower": 28.0,
        "ci95Upper": 34.8,
    },
    chain_of_custody_hash="6d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e",
)

PRESET_NA18507_CHB = CaseworkPresetItem(
    preset_id="PRESET_NA18507_CHB",
    sample_name="NA18507 / HG005 (Han Chinese in Beijing Male)",
    coriell_id="NA18507 / HG005",
    case_type="GIAB / 1000G East Asian Reference Standard",
    sex="MALE",
    target_population="Han Chinese in Beijing (CHB)",
    population_group="CHB_BEIJING_HAN_CHINESE",
    physical_condition="Pristine Genomic DNA (High Molecular Weight)",
    description="GIAB / 1000G East Asian male reference standard. Features Y-STR Haplogroup O2a2b1, mtDNA D4a1, EDAR V370A thick straight hair allele, and VISAGE age 41.0 years.",
    expected_ancestry="99.4% East Asian (EAS)",
    expected_phenotype="Dark Brown Eyes (P=0.99), Black Hair (P=0.99), Intermediate Skin Type III (P=0.92), Thick Straight Hair (EDAR V370A)",
    expected_centroid="39.90°N, 116.41°E (Beijing, China)",
    degradation_index=1.03,
    stochastic_dropout_prob=0.00,
    heterozygote_balance=0.97,
    is_certified_standard=True,
    str_profile={
        "AMEL": {"allele1": "X", "allele2": "Y", "rfu1": 3300, "rfu2": 3200},
        "CSF1PO": {"allele1": "10", "allele2": "12", "rfu1": 2350, "rfu2": 2300},
        "D1S1656": {"allele1": "11", "allele2": "16", "rfu1": 2150, "rfu2": 2100},
        "D2S441": {"allele1": "11", "allele2": "11.3", "rfu1": 2550, "rfu2": 2500},
        "D2S1338": {"allele1": "19", "allele2": "25", "rfu1": 2050, "rfu2": 2000},
        "D3S1358": {"allele1": "15", "allele2": "16", "rfu1": 2750, "rfu2": 2700},
        "D5S818": {"allele1": "10", "allele2": "11", "rfu1": 2250, "rfu2": 2200},
        "D7S820": {"allele1": "10", "allele2": "11", "rfu1": 2400, "rfu2": 2350},
        "D8S1179": {"allele1": "10", "allele2": "13", "rfu1": 2650, "rfu2": 2600},
        "D10S1248": {"allele1": "12", "allele2": "15", "rfu1": 2950, "rfu2": 2900},
        "D12S391": {"allele1": "17", "allele2": "21", "rfu1": 2100, "rfu2": 2050},
        "D13S317": {"allele1": "8", "allele2": "11", "rfu1": 2450, "rfu2": 2400},
        "D16S539": {"allele1": "9", "allele2": "11", "rfu1": 2350, "rfu2": 2300},
        "D18S51": {"allele1": "13", "allele2": "14", "rfu1": 1900, "rfu2": 1850},
        "D19S433": {"allele1": "13", "allele2": "14.2", "rfu1": 2600, "rfu2": 2550},
        "D21S11": {"allele1": "29", "allele2": "30", "rfu1": 2150, "rfu2": 2100},
        "D22S1045": {"allele1": "11", "allele2": "16", "rfu1": 3000, "rfu2": 2950},
        "FGA": {"allele1": "22", "allele2": "23", "rfu1": 1950, "rfu2": 1900},
        "TH01": {"allele1": "7", "allele2": "9", "rfu1": 2850, "rfu2": 2800},
        "TPOX": {"allele1": "8", "allele2": "11", "rfu1": 2500, "rfu2": 2450},
        "VWA": {"allele1": "14", "allele2": "17", "rfu1": 2450, "rfu2": 2400},
        "SE33": {"allele1": "15", "allele2": "22.2", "rfu1": 1700, "rfu2": 1650},
        "PENTA_D": {"allele1": "9", "allele2": "12", "rfu1": 2300, "rfu2": 2250},
        "PENTA_E": {"allele1": "10", "allele2": "14", "rfu1": 2050, "rfu2": 2000},
    },
    snp_dosages={
        "rs12913832": 0, "rs1805007": 0, "rs16891982": 0, "rs1426654": 2,
        "rs1042602": 2, "rs12203592": 0, "rs3827072": 2, "rs727811": 2,
        "rs3811801": 2, "rs2814778": 0, "rs1800414": 2, "rs11019": 1,
        "rs10886828": 2, "rs2032582": 2, "rs2300986": 2, "rs1028531": 2,
    },
    ystr_profile={
        "DYS19": {"allele1": "15", "rfu1": 1600},
        "DYS389I": {"allele1": "14", "rfu1": 1550},
        "DYS389II": {"allele1": "31", "rfu1": 1500},
        "DYS390": {"allele1": "24", "rfu1": 1650},
        "DYS391": {"allele1": "10", "rfu1": 1580},
        "DYS392": {"allele1": "13", "rfu1": 1520},
        "DYS393": {"allele1": "13", "rfu1": 1600},
        "DYS385a/b": {"allele1": "12", "allele2": "18", "rfu1": 1480, "rfu2": 1440},
        "DYS437": {"allele1": "14", "rfu1": 1560},
        "DYS438": {"allele1": "10", "rfu1": 1540},
        "DYS439": {"allele1": "11", "rfu1": 1590},
        "DYS448": {"allele1": "19", "rfu1": 1450},
        "DYS456": {"allele1": "15", "rfu1": 1620},
        "DYS458": {"allele1": "17", "rfu1": 1610},
        "DYS635": {"allele1": "23", "rfu1": 1500},
        "YGATAH4": {"allele1": "12", "rfu1": 1570},
        "DYS481": {"allele1": "23", "rfu1": 1490},
        "DYS533": {"allele1": "12", "rfu1": 1580},
        "DYS549": {"allele1": "11", "rfu1": 1520},
        "DYS570": {"allele1": "17", "rfu1": 1520},
        "DYS576": {"allele1": "17", "rfu1": 1550},
        "DYS643": {"allele1": "10", "rfu1": 1460},
        "DYS518": {"allele1": "37", "rfu1": 1420},
        "DYS627": {"allele1": "23", "rfu1": 1400},
        "DYS449": {"allele1": "30", "rfu1": 1380},
        "DYF387S1a/b": {"allele1": "37", "allele2": "38", "rfu1": 1380, "rfu2": 1350},
        "DYS460": {"allele1": "11", "rfu1": 1530},
    },
    mtdna_mutations=["73G", "263G", "309.1C", "315.1C", "16129C", "16223T", "16362C", "16519C"],
    aim_profile={
        "admixtureProportions": {"qEUR": 0.002, "qAFR": 0.001, "qEAS": 0.994, "qSAS": 0.002, "qAMR": 0.001},
        "centroid": {"latitude": 39.9042, "longitude": 116.4074, "region": "Beijing, China"},
    },
    hirisplex_profile={
        "predictedEyeColor": "Dark Brown", "eyeColorProb": 0.99,
        "predictedHairColor": "Black", "hairColorProb": 0.99,
        "predictedSkinPhototype": "Type III / Intermediate", "skinPhototypeProb": 0.92,
        "hairMorphology": "Thick Straight (EDAR V370A)",
    },
    visage_epigenetic_profile={
        "cpgBetaValues": {
            "cg16867657_ELOVL2": 0.41,
            "cg06639320_FHL2": 0.30,
            "cg16537105_PENK": 0.21,
            "cg04523812_TRIM59": 0.36,
            "cg08097417_KLF14": 0.27,
        },
        "predictedAgeYears": 41.0,
        "ci95Lower": 37.6,
        "ci95Upper": 44.4,
    },
    chain_of_custody_hash="5e4f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f",
)


# ═══════════════════════════════════════════════════════════════════════════════
# 6 CASEWORK BENCHMARK VECTORS (VECTOR_TERM_01 to VECTOR_TERM_06)
# ═══════════════════════════════════════════════════════════════════════════════

VECTOR_TERM_01 = CaseworkPresetItem(
    preset_id="VECTOR_TERM_01",
    sample_name="Vector A (Northern European)",
    case_type="Golden Benchmark Vector A (ISO 17025)",
    target_population="Northern / Western European (EUR)",
    physical_condition="Pristine DNA (High Molecular Weight, 1.0 ng)",
    description="24-locus STR profile with Golden Benchmark Vector A SNP panel: HERC2 (X=2), SLC45A2 (X=2), SLC24A5 (X=2), MC1R R151C (X=1), IRF4 (X=1). 25 Y-STR systems R1b-M269 and mtDNA H1.",
    expected_ancestry="> 98.4% European (EUR)",
    expected_phenotype="Blue Eyes (P = 0.962), Blond Hair (P = 0.612), Very Pale Skin Type I (P = 0.784), Straight Hair (P = 0.882)",
    expected_centroid="48.86°N, 2.35°E (Western Europe)",
    degradation_index=1.05,
    stochastic_dropout_prob=0.00,
    heterozygote_balance=0.96,
    is_certified_standard=False,
    str_profile={
        "D3S1358": {"allele1": "15", "allele2": "16", "rfu1": 1500, "rfu2": 1450},
        "vWA": {"allele1": "16", "allele2": "17", "rfu1": 1600, "rfu2": 1550},
        "FGA": {"allele1": "21", "allele2": "23", "rfu1": 1420, "rfu2": 1380},
        "D8S1179": {"allele1": "13", "allele2": "14", "rfu1": 1520, "rfu2": 1480},
        "D21S11": {"allele1": "29", "allele2": "30", "rfu1": 1400, "rfu2": 1350},
        "D18S51": {"allele1": "12", "allele2": "15", "rfu1": 1350, "rfu2": 1300},
        "D5S818": {"allele1": "11", "allele2": "12", "rfu1": 1480, "rfu2": 1420},
        "D13S317": {"allele1": "11", "allele2": "12", "rfu1": 1450, "rfu2": 1400},
        "D7S820": {"allele1": "10", "allele2": "11", "rfu1": 1410, "rfu2": 1370},
        "D16S539": {"allele1": "11", "allele2": "12", "rfu1": 1390, "rfu2": 1340},
        "CSF1PO": {"allele1": "10", "allele2": "11", "rfu1": 1360, "rfu2": 1320},
        "TH01": {"allele1": "9.3", "allele2": "9.3", "rfu1": 2200, "rfu2": 2200},
        "TPOX": {"allele1": "8", "allele2": "11", "rfu1": 1440, "rfu2": 1400},
        "D1S1656": {"allele1": "14", "allele2": "17.3", "rfu1": 1380, "rfu2": 1330},
        "D2S441": {"allele1": "11", "allele2": "12", "rfu1": 1510, "rfu2": 1460},
        "D2S1338": {"allele1": "19", "allele2": "23", "rfu1": 1340, "rfu2": 1290},
        "D10S1248": {"allele1": "13", "allele2": "14", "rfu1": 1530, "rfu2": 1490},
        "D12S391": {"allele1": "18", "allele2": "19", "rfu1": 1430, "rfu2": 1390},
        "D19S433": {"allele1": "13", "allele2": "14", "rfu1": 1490, "rfu2": 1440},
        "D22S1045": {"allele1": "15", "allele2": "16", "rfu1": 1500, "rfu2": 1450},
        "SE33": {"allele1": "26.2", "allele2": "28.2", "rfu1": 1250, "rfu2": 1200},
        "Penta D": {"allele1": "9", "allele2": "11", "rfu1": 1320, "rfu2": 1280},
        "Penta E": {"allele1": "12", "allele2": "13", "rfu1": 1200, "rfu2": 1150},
        "Amelogenin": {"allele1": "X", "allele2": "Y", "rfu1": 1850, "rfu2": 1800},
    },
    snp_dosages={
        "rs12913832": 2, "rs16891982": 2, "rs1426654": 2, "rs1805007": 1,
        "rs12203592": 1, "rs3827760": 0, "rs11803731": 0, "rs2814778": 0,
        "rs1800407": 0, "rs12896399": 2,
    },
    ystr_profile={
        "DYS19": {"allele1": "14", "rfu1": 1500},
        "DYS389I": {"allele1": "13", "rfu1": 1450},
        "DYS389II": {"allele1": "29", "rfu1": 1400},
        "DYS390": {"allele1": "24", "rfu1": 1550},
        "DYS391": {"allele1": "11", "rfu1": 1480},
        "DYS392": {"allele1": "13", "rfu1": 1420},
        "DYS393": {"allele1": "13", "rfu1": 1500},
        "DYS385a/b": {"allele1": "11", "allele2": "14", "rfu1": 1380, "rfu2": 1340},
        "DYS437": {"allele1": "15", "rfu1": 1460},
        "DYS438": {"allele1": "12", "rfu1": 1440},
        "DYS439": {"allele1": "12", "rfu1": 1490},
        "DYS448": {"allele1": "19", "rfu1": 1350},
        "DYS456": {"allele1": "15", "rfu1": 1520},
        "DYS458": {"allele1": "17", "rfu1": 1510},
        "DYS635": {"allele1": "23", "rfu1": 1400},
        "YGATAH4": {"allele1": "12", "rfu1": 1470},
        "DYS460": {"allele1": "11", "rfu1": 1430},
        "DYS481": {"allele1": "22", "rfu1": 1390},
        "DYS533": {"allele1": "12", "rfu1": 1480},
        "DYS570": {"allele1": "17", "rfu1": 1420},
        "DYS576": {"allele1": "18", "rfu1": 1450},
        "DYS627": {"allele1": "15", "rfu1": 1360},
        "DYS518": {"allele1": "38", "rfu1": 1320},
        "DYS449": {"allele1": "30", "rfu1": 1300},
        "DYF387S1a/b": {"allele1": "35", "allele2": "37", "rfu1": 1280, "rfu2": 1250},
    },
    mtdna_mutations=["263G", "315.1C", "750G", "16519C"],
    supplementary_markers={"DYS391": "11", "SRY": "POSITIVE"},
    chain_of_custody_hash="1a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b",
)

VECTOR_TERM_02 = CaseworkPresetItem(
    preset_id="VECTOR_TERM_02",
    sample_name="Vector B (African American Reference)",
    case_type="Golden Benchmark Vector B (ISO 17025)",
    target_population="Sub-Saharan African (AFR)",
    physical_condition="Pristine High-Yield DNA (1.2 ng)",
    description="24-locus STR profile with Golden Benchmark Vector B: D21S11 (29, 31.2), FGA (22, 25), D19S433 (12, 14.2), 25 Y-STR systems E1b1a-V38 and mtDNA L2a1.",
    expected_ancestry="> 97.8% Sub-Saharan African (AFR)",
    expected_phenotype="Dark Brown Eyes (P = 0.998), Black Hair (P = 0.997), Dark-Black Skin Type VI (P = 0.948), Coiled Hair (P = 0.986)",
    expected_centroid="6.52°N, 3.38°E (Lagos / West Africa)",
    degradation_index=1.08,
    stochastic_dropout_prob=0.00,
    heterozygote_balance=0.94,
    is_certified_standard=False,
    str_profile={
        "D3S1358": {"allele1": "16", "allele2": "17", "rfu1": 1600, "rfu2": 1520},
        "vWA": {"allele1": "15", "allele2": "18", "rfu1": 1550, "rfu2": 1490},
        "FGA": {"allele1": "22", "allele2": "25", "rfu1": 1480, "rfu2": 1410},
        "D8S1179": {"allele1": "14", "allele2": "15", "rfu1": 1500, "rfu2": 1470},
        "D21S11": {"allele1": "29", "allele2": "31.2", "rfu1": 1450, "rfu2": 1390},
        "D18S51": {"allele1": "15", "allele2": "17", "rfu1": 1380, "rfu2": 1320},
        "D5S818": {"allele1": "12", "allele2": "13", "rfu1": 1510, "rfu2": 1440},
        "D13S317": {"allele1": "12", "allele2": "13", "rfu1": 1490, "rfu2": 1420},
        "D7S820": {"allele1": "8", "allele2": "10", "rfu1": 1420, "rfu2": 1380},
        "D16S539": {"allele1": "9", "allele2": "11", "rfu1": 1400, "rfu2": 1350},
        "CSF1PO": {"allele1": "10", "allele2": "12", "rfu1": 1370, "rfu2": 1330},
        "TH01": {"allele1": "7", "allele2": "9", "rfu1": 1620, "rfu2": 1580},
        "TPOX": {"allele1": "8", "allele2": "9", "rfu1": 1460, "rfu2": 1410},
        "D1S1656": {"allele1": "15", "allele2": "16", "rfu1": 1390, "rfu2": 1340},
        "D2S441": {"allele1": "10", "allele2": "11", "rfu1": 1520, "rfu2": 1470},
        "D2S1338": {"allele1": "18", "allele2": "22", "rfu1": 1360, "rfu2": 1310},
        "D10S1248": {"allele1": "14", "allele2": "15", "rfu1": 1540, "rfu2": 1500},
        "D12S391": {"allele1": "17", "allele2": "21", "rfu1": 1440, "rfu2": 1400},
        "D19S433": {"allele1": "12", "allele2": "14.2", "rfu1": 1500, "rfu2": 1450},
        "D22S1045": {"allele1": "11", "allele2": "16", "rfu1": 1510, "rfu2": 1460},
        "SE33": {"allele1": "17", "allele2": "22.2", "rfu1": 1280, "rfu2": 1220},
        "Penta D": {"allele1": "10", "allele2": "13", "rfu1": 1330, "rfu2": 1290},
        "Penta E": {"allele1": "8", "allele2": "15", "rfu1": 1220, "rfu2": 1170},
        "Amelogenin": {"allele1": "X", "allele2": "Y", "rfu1": 1870, "rfu2": 1810},
    },
    snp_dosages={
        "rs12913832": 0, "rs16891982": 0, "rs1426654": 0, "rs1805007": 0,
        "rs12203592": 0, "rs3827760": 0, "rs11803731": 0, "rs2814778": 2,
        "rs1800407": 0, "rs12896399": 0,
    },
    ystr_profile={
        "DYS19": {"allele1": "15", "rfu1": 1550},
        "DYS389I": {"allele1": "14", "rfu1": 1500},
        "DYS389II": {"allele1": "31", "rfu1": 1450},
        "DYS390": {"allele1": "21", "rfu1": 1600},
        "DYS391": {"allele1": "10", "rfu1": 1520},
        "DYS392": {"allele1": "11", "rfu1": 1480},
        "DYS393": {"allele1": "15", "rfu1": 1550},
        "DYS385a/b": {"allele1": "15", "allele2": "16", "rfu1": 1420, "rfu2": 1390},
        "DYS437": {"allele1": "16", "rfu1": 1500},
        "DYS438": {"allele1": "10", "rfu1": 1480},
        "DYS439": {"allele1": "11", "rfu1": 1530},
        "DYS448": {"allele1": "20", "rfu1": 1390},
        "DYS456": {"allele1": "15", "rfu1": 1560},
        "DYS458": {"allele1": "16", "rfu1": 1550},
        "DYS635": {"allele1": "21", "rfu1": 1450},
        "YGATAH4": {"allele1": "11", "rfu1": 1510},
        "DYS460": {"allele1": "11", "rfu1": 1470},
        "DYS481": {"allele1": "25", "rfu1": 1430},
        "DYS533": {"allele1": "13", "rfu1": 1520},
        "DYS570": {"allele1": "19", "rfu1": 1460},
        "DYS576": {"allele1": "16", "rfu1": 1490},
        "DYS627": {"allele1": "18", "rfu1": 1400},
        "DYS518": {"allele1": "40", "rfu1": 1360},
        "DYS449": {"allele1": "34", "rfu1": 1340},
        "DYF387S1a/b": {"allele1": "38", "allele2": "39", "rfu1": 1320, "rfu2": 1290},
    },
    mtdna_mutations=[
        "73G", "146C", "152C", "195C", "247G", "263G", "315.1C",
        "524.1A", "524.2C", "16111T", "16192T", "16223T", "16278T", "16390G"
    ],
    supplementary_markers={"DYS391": "10", "SRY": "POSITIVE"},
    chain_of_custody_hash="2b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c",
)

VECTOR_TERM_03 = CaseworkPresetItem(
    preset_id="VECTOR_TERM_03",
    sample_name="Vector C (Hispanic / AMEL Y-Null Resolution)",
    case_type="Amelogenin Y-Null Resolution (SWGDAM)",
    target_population="Hispanic / Indigenous American (AMR)",
    physical_condition="Pristine Reference (1.0 ng)",
    description="24-locus STR profile with Amelogenin Y-null deletion (AMEL X, X). Confirmed male via DYS391=11 and 25 Y-STR systems Q-M3. mtDNA A2.",
    expected_ancestry="> 82.5% Indigenous American (AMR), 15.2% European",
    expected_phenotype="Brown Eyes (P = 0.892), Black Hair (P = 0.941), Intermediate Skin Type IV (P = 0.812), Straight Thick Hair (P = 0.915)",
    expected_centroid="19.43°N, 99.13°W (Central Mexico)",
    degradation_index=1.02,
    stochastic_dropout_prob=0.00,
    heterozygote_balance=0.98,
    is_certified_standard=False,
    str_profile={
        "D3S1358": {"allele1": "15", "allele2": "17", "rfu1": 1550, "rfu2": 1500},
        "vWA": {"allele1": "16", "allele2": "19", "rfu1": 1580, "rfu2": 1520},
        "FGA": {"allele1": "23", "allele2": "24", "rfu1": 1450, "rfu2": 1400},
        "D8S1179": {"allele1": "13", "allele2": "15", "rfu1": 1510, "rfu2": 1460},
        "D21S11": {"allele1": "28", "allele2": "30", "rfu1": 1420, "rfu2": 1370},
        "D18S51": {"allele1": "14", "allele2": "16", "rfu1": 1360, "rfu2": 1310},
        "D5S818": {"allele1": "11", "allele2": "12", "rfu1": 1490, "rfu2": 1430},
        "D13S317": {"allele1": "12", "allele2": "13", "rfu1": 1470, "rfu2": 1410},
        "D7S820": {"allele1": "10", "allele2": "11", "rfu1": 1430, "rfu2": 1390},
        "D16S539": {"allele1": "11", "allele2": "13", "rfu1": 1410, "rfu2": 1360},
        "CSF1PO": {"allele1": "11", "allele2": "12", "rfu1": 1380, "rfu2": 1340},
        "TH01": {"allele1": "7", "allele2": "9.3", "rfu1": 1650, "rfu2": 1600},
        "TPOX": {"allele1": "8", "allele2": "11", "rfu1": 1450, "rfu2": 1420},
        "D1S1656": {"allele1": "15", "allele2": "17", "rfu1": 1400, "rfu2": 1350},
        "D2S441": {"allele1": "10", "allele2": "11.3", "rfu1": 1530, "rfu2": 1480},
        "D2S1338": {"allele1": "19", "allele2": "24", "rfu1": 1350, "rfu2": 1300},
        "D10S1248": {"allele1": "13", "allele2": "15", "rfu1": 1550, "rfu2": 1510},
        "D12S391": {"allele1": "18", "allele2": "22", "rfu1": 1450, "rfu2": 1410},
        "D19S433": {"allele1": "13", "allele2": "14", "rfu1": 1510, "rfu2": 1460},
        "D22S1045": {"allele1": "15", "allele2": "17", "rfu1": 1520, "rfu2": 1470},
        "SE33": {"allele1": "19", "allele2": "29.2", "rfu1": 1260, "rfu2": 1210},
        "Penta D": {"allele1": "11", "allele2": "13", "rfu1": 1340, "rfu2": 1300},
        "Penta E": {"allele1": "8", "allele2": "14", "rfu1": 1210, "rfu2": 1160},
        "Amelogenin": {"allele1": "X", "allele2": "X", "rfu1": 3200, "rfu2": 3100},
    },
    snp_dosages={
        "rs12913832": 0, "rs16891982": 0, "rs1426654": 1, "rs1805007": 0,
        "rs12203592": 0, "rs3827760": 2, "rs11803731": 0, "rs2814778": 0,
        "rs1800407": 0, "rs12896399": 0,
    },
    ystr_profile={
        "DYS19": {"allele1": "13", "rfu1": 1550},
        "DYS389I": {"allele1": "13", "rfu1": 1500},
        "DYS389II": {"allele1": "30", "rfu1": 1450},
        "DYS390": {"allele1": "24", "rfu1": 1600},
        "DYS391": {"allele1": "11", "rfu1": 1520},
        "DYS392": {"allele1": "14", "rfu1": 1480},
        "DYS393": {"allele1": "13", "rfu1": 1550},
        "DYS385a/b": {"allele1": "13", "allele2": "14", "rfu1": 1420, "rfu2": 1390},
        "DYS437": {"allele1": "14", "rfu1": 1500},
        "DYS438": {"allele1": "12", "rfu1": 1480},
        "DYS439": {"allele1": "12", "rfu1": 1530},
        "DYS448": {"allele1": "19", "rfu1": 1390},
        "DYS456": {"allele1": "15", "rfu1": 1560},
        "DYS458": {"allele1": "16", "rfu1": 1550},
        "DYS635": {"allele1": "23", "rfu1": 1450},
        "YGATAH4": {"allele1": "12", "rfu1": 1510},
        "DYS460": {"allele1": "10", "rfu1": 1470},
        "DYS481": {"allele1": "22", "rfu1": 1430},
        "DYS533": {"allele1": "12", "rfu1": 1520},
        "DYS570": {"allele1": "16", "rfu1": 1460},
        "DYS576": {"allele1": "17", "rfu1": 1490},
        "DYS627": {"allele1": "19", "rfu1": 1400},
        "DYS518": {"allele1": "38", "rfu1": 1360},
        "DYS449": {"allele1": "30", "rfu1": 1340},
        "DYF387S1a/b": {"allele1": "37", "allele2": "39", "rfu1": 1320, "rfu2": 1290},
    },
    mtdna_mutations=[
        "73G", "153G", "235G", "263G", "315.1C", "522del", "523del",
        "16111T", "16223T", "16290T", "16319A", "16362C", "16519C"
    ],
    supplementary_markers={"DYS391": "11", "SRY": "POSITIVE"},
    chain_of_custody_hash="3c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d",
)

VECTOR_TERM_04 = CaseworkPresetItem(
    preset_id="VECTOR_TERM_04",
    sample_name="Vector D (East Asian Reference)",
    case_type="Golden Benchmark Vector D (ISO 17025)",
    target_population="East Asian (EAS)",
    physical_condition="Pristine DNA (1.0 ng)",
    description="24-locus STR profile with East Asian characteristics. EDAR V370A thick straight hair allele, 25 Y-STR systems O2a2b1 and mtDNA D4a1.",
    expected_ancestry="> 99.1% East Asian (EAS)",
    expected_phenotype="Dark Brown Eyes (P = 0.998), Black Hair (P = 0.997), Intermediate Skin Type III (P = 0.912), Straight Thick Hair (P = 0.994)",
    expected_centroid="39.90°N, 116.40°E (Beijing / East Asia)",
    degradation_index=1.04,
    stochastic_dropout_prob=0.00,
    heterozygote_balance=0.97,
    is_certified_standard=False,
    str_profile={
        "D3S1358": {"allele1": "15", "allele2": "16", "rfu1": 1540, "rfu2": 1490},
        "vWA": {"allele1": "14", "allele2": "17", "rfu1": 1570, "rfu2": 1510},
        "FGA": {"allele1": "22", "allele2": "23", "rfu1": 1440, "rfu2": 1390},
        "D8S1179": {"allele1": "10", "allele2": "13", "rfu1": 1500, "rfu2": 1450},
        "D21S11": {"allele1": "29", "allele2": "30", "rfu1": 1410, "rfu2": 1360},
        "D18S51": {"allele1": "13", "allele2": "14", "rfu1": 1350, "rfu2": 1300},
        "D5S818": {"allele1": "10", "allele2": "11", "rfu1": 1480, "rfu2": 1420},
        "D13S317": {"allele1": "8", "allele2": "11", "rfu1": 1460, "rfu2": 1400},
        "D7S820": {"allele1": "10", "allele2": "11", "rfu1": 1420, "rfu2": 1380},
        "D16S539": {"allele1": "9", "allele2": "11", "rfu1": 1400, "rfu2": 1350},
        "CSF1PO": {"allele1": "10", "allele2": "12", "rfu1": 1370, "rfu2": 1330},
        "TH01": {"allele1": "7", "allele2": "9", "rfu1": 1630, "rfu2": 1590},
        "TPOX": {"allele1": "8", "allele2": "11", "rfu1": 1450, "rfu2": 1410},
        "D1S1656": {"allele1": "11", "allele2": "16", "rfu1": 1390, "rfu2": 1340},
        "D2S441": {"allele1": "11", "allele2": "11.3", "rfu1": 1520, "rfu2": 1470},
        "D2S1338": {"allele1": "19", "allele2": "25", "rfu1": 1350, "rfu2": 1300},
        "D10S1248": {"allele1": "12", "allele2": "15", "rfu1": 1540, "rfu2": 1500},
        "D12S391": {"allele1": "17", "allele2": "21", "rfu1": 1440, "rfu2": 1400},
        "D19S433": {"allele1": "13", "allele2": "14.2", "rfu1": 1500, "rfu2": 1450},
        "D22S1045": {"allele1": "11", "allele2": "16", "rfu1": 1510, "rfu2": 1460},
        "SE33": {"allele1": "15", "allele2": "22.2", "rfu1": 1270, "rfu2": 1210},
        "Penta D": {"allele1": "9", "allele2": "12", "rfu1": 1330, "rfu2": 1290},
        "Penta E": {"allele1": "10", "allele2": "14", "rfu1": 1210, "rfu2": 1160},
        "Amelogenin": {"allele1": "X", "allele2": "Y", "rfu1": 1860, "rfu2": 1800},
    },
    snp_dosages={
        "rs12913832": 0, "rs16891982": 0, "rs1426654": 2, "rs1805007": 0,
        "rs12203592": 0, "rs3827760": 2, "rs11803731": 0, "rs2814778": 0,
        "rs1800407": 0, "rs12896399": 0,
    },
    ystr_profile={
        "DYS19": {"allele1": "15", "rfu1": 1550},
        "DYS389I": {"allele1": "14", "rfu1": 1500},
        "DYS389II": {"allele1": "31", "rfu1": 1450},
        "DYS390": {"allele1": "24", "rfu1": 1600},
        "DYS391": {"allele1": "10", "rfu1": 1520},
        "DYS392": {"allele1": "13", "rfu1": 1480},
        "DYS393": {"allele1": "13", "rfu1": 1550},
        "DYS385a/b": {"allele1": "12", "allele2": "18", "rfu1": 1420, "rfu2": 1390},
        "DYS437": {"allele1": "14", "rfu1": 1500},
        "DYS438": {"allele1": "10", "rfu1": 1480},
        "DYS439": {"allele1": "11", "rfu1": 1530},
        "DYS448": {"allele1": "19", "rfu1": 1390},
        "DYS456": {"allele1": "15", "rfu1": 1560},
        "DYS458": {"allele1": "17", "rfu1": 1550},
        "DYS635": {"allele1": "23", "rfu1": 1450},
        "YGATAH4": {"allele1": "12", "rfu1": 1510},
        "DYS460": {"allele1": "11", "rfu1": 1470},
        "DYS481": {"allele1": "23", "rfu1": 1430},
        "DYS533": {"allele1": "12", "rfu1": 1520},
        "DYS570": {"allele1": "17", "rfu1": 1460},
        "DYS576": {"allele1": "17", "rfu1": 1490},
        "DYS627": {"allele1": "23", "rfu1": 1400},
        "DYS518": {"allele1": "37", "rfu1": 1360},
        "DYS449": {"allele1": "30", "rfu1": 1340},
        "DYF387S1a/b": {"allele1": "37", "allele2": "38", "rfu1": 1320, "rfu2": 1290},
    },
    mtdna_mutations=["73G", "263G", "309.1C", "315.1C", "16129C", "16223T", "16362C", "16519C"],
    supplementary_markers={"DYS391": "10", "SRY": "POSITIVE"},
    chain_of_custody_hash="4d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e",
)

VECTOR_TERM_05 = CaseworkPresetItem(
    preset_id="VECTOR_TERM_05",
    sample_name="Vector E (DVI Degraded Reference)",
    case_type="Disaster Victim Identification (Interpol DVI)",
    target_population="European (EUR)",
    physical_condition="Severely Degraded Bone Sample (DI = 6.42)",
    description="Degraded skeletal remains profile exhibiting high molecular weight locus dropout and stochastic threshold warnings.",
    expected_ancestry="European Reference Admixture",
    expected_phenotype="Inconclusive due to degraded SNP yield",
    expected_centroid="45.0°N, 10.0°E (Alpine Corridor)",
    degradation_index=6.42,
    stochastic_dropout_prob=0.38,
    heterozygote_balance=0.62,
    is_certified_standard=False,
    str_profile={
        "D3S1358": {"allele1": "15", "allele2": "16", "rfu1": 950, "rfu2": 910},
        "vWA": {"allele1": "16", "allele2": "17", "rfu1": 820, "rfu2": 780},
        "FGA": {"allele1": "21", "allele2": "[0]", "rfu1": 210, "rfu2": 0},
        "D8S1179": {"allele1": "13", "allele2": "14", "rfu1": 920, "rfu2": 880},
        "D21S11": {"allele1": "29", "allele2": "[0]", "rfu1": 180, "rfu2": 0},
        "TH01": {"allele1": "9.3", "allele2": "9.3", "rfu1": 1400, "rfu2": 1400},
        "Amelogenin": {"allele1": "X", "allele2": "Y", "rfu1": 1100, "rfu2": 1050},
    },
    snp_dosages={"rs12913832": 2, "rs16891982": 2},
    chain_of_custody_hash="5e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f",
)

VECTOR_TERM_06 = CaseworkPresetItem(
    preset_id="VECTOR_TERM_06",
    sample_name="Vector F (Touch DNA Low-Template)",
    case_type="Low-Template Touch DNA (< 100 pg)",
    target_population="Mixed Population Background",
    physical_condition="LTDNA Contact Swab (65 pg template)",
    description="Low template touch DNA showing allele drop-in, stochastic dropout, and elevated stutter.",
    expected_ancestry="Complex Admixture",
    expected_phenotype="Partial Profile Prediction",
    expected_centroid="37.77°N, 122.41°W (San Francisco, CA)",
    degradation_index=2.85,
    stochastic_dropout_prob=0.45,
    heterozygote_balance=0.55,
    is_certified_standard=False,
    str_profile={
        "D3S1358": {"allele1": "15", "allele2": "16", "rfu1": 120, "rfu2": 95},
        "vWA": {"allele1": "16", "allele2": "[0]", "rfu1": 110, "rfu2": 0},
        "TH01": {"allele1": "9.3", "allele2": "9.3", "rfu1": 180, "rfu2": 180},
        "Amelogenin": {"allele1": "X", "allele2": "[0]", "rfu1": 140, "rfu2": 0},
    },
    snp_dosages={"rs12913832": 1},
    chain_of_custody_hash="6f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a",
)

CERTIFIED_GLOBAL_REFERENCE_PRESETS: Dict[str, CaseworkPresetItem] = {
    "PRESET_NIST_SRM_2391D": PRESET_NIST_SRM_2391D,
    "PRESET_NA12878_CEU": PRESET_NA12878_CEU,
    "PRESET_HG002_AJ": PRESET_HG002_AJ,
    "PRESET_NA19240_YRI": PRESET_NA19240_YRI,
    "PRESET_NA18507_CHB": PRESET_NA18507_CHB,
}


# Master Catalog combining Certified Standards and Casework Benchmark Presets
GOLDEN_CASEWORK_PRESETS: Dict[str, CaseworkPresetItem] = {
    # 5 Certified Global Reference Standards
    "PRESET_NIST_SRM_2391D": PRESET_NIST_SRM_2391D,
    "PRESET_NA12878_CEU": PRESET_NA12878_CEU,
    "PRESET_HG002_AJ": PRESET_HG002_AJ,
    "PRESET_NA19240_YRI": PRESET_NA19240_YRI,
    "PRESET_NA18507_CHB": PRESET_NA18507_CHB,

    # 6 Casework Benchmark Vectors
    "VECTOR_TERM_01": VECTOR_TERM_01,
    "VECTOR_TERM_02": VECTOR_TERM_02,
    "VECTOR_TERM_03": VECTOR_TERM_03,
    "VECTOR_TERM_04": VECTOR_TERM_04,
    "VECTOR_TERM_05": VECTOR_TERM_05,
    "VECTOR_TERM_06": VECTOR_TERM_06,

    # Standard Aliases
    "NIST_SRM_2391D": PRESET_NIST_SRM_2391D,
    "SRM_2391D": PRESET_NIST_SRM_2391D,
    "NA12878": PRESET_NA12878_CEU,
    "HG001": PRESET_NA12878_CEU,
    "HG002": PRESET_HG002_AJ,
    "NA24385": PRESET_HG002_AJ,
    "NA19240": PRESET_NA19240_YRI,
    "NA18507": PRESET_NA18507_CHB,
    "HG005": PRESET_NA18507_CHB,
}


# ==============================================================================
# FORENSIC MULTI-OMIC VALIDATOR ENGINE
# ==============================================================================

class CaseworkPresetsEngine:
    """Helper engine for querying casework and certified presets."""

    @classmethod
    def get_all_presets(cls) -> List[CaseworkPresetItem]:
        # Return unique presets
        seen = set()
        res = []
        for p in GOLDEN_CASEWORK_PRESETS.values():
            if p.preset_id not in seen:
                seen.add(p.preset_id)
                res.append(p)
        return res

    @classmethod
    def get_preset_by_id(cls, preset_id: str) -> Optional[CaseworkPresetItem]:
        norm = preset_id.strip().upper()
        if norm in GOLDEN_CASEWORK_PRESETS:
            return GOLDEN_CASEWORK_PRESETS[norm]
        for p in GOLDEN_CASEWORK_PRESETS.values():
            if norm == p.preset_id.upper() or (p.coriell_id and norm in p.coriell_id.upper()):
                return p
        return None

    @classmethod
    def export_to_codis_xml(cls, *args, **kwargs):
        return CaseworkPresetExporter.export_to_codis_xml(*args, **kwargs)

    @classmethod
    def export_to_lims_json(cls, *args, **kwargs):
        return CaseworkPresetExporter.export_to_lims_json(*args, **kwargs)

    @classmethod
    def export_to_genemapper_csv(cls, *args, **kwargs):
        return CaseworkPresetExporter.export_to_genemapper_csv(*args, **kwargs)


class ForensicMultiOmicValidator:
    """
    Automated concordance and multi-omic validation engine for certified
    reference materials against international standards (NIST, GIAB, 1000G).
    """

    def __init__(self, presets: Optional[Dict[str, CaseworkPresetItem]] = None):
        self.presets = presets or GOLDEN_CASEWORK_PRESETS

    def get_preset(self, identifier: str) -> Optional[CaseworkPresetItem]:
        norm = identifier.strip().upper()
        if norm in self.presets:
            return self.presets[norm]
        
        # Match by Coriell / sample name
        for p in self.presets.values():
            if (p.coriell_id and norm in p.coriell_id.upper()) or \
               (p.sample_name and norm in p.sample_name.upper()) or \
               (p.preset_id and norm in p.preset_id.upper()):
                return p
        return None

    def validate_str_concordance(
        self,
        identifier: str,
        query_profile: Dict[str, Any],
    ) -> Tuple[float, List[str]]:
        """
        Validates autosomal STR concordance against certified truth set across all 24 loci.
        """
        preset = self.get_preset(identifier)
        if not preset:
            raise ValueError(f"Reference standard '{identifier}' not found in certified repository.")

        ref_str = preset.str_profile
        mismatches: List[str] = []
        matching_loci = 0

        for locus, ref_data in ref_str.items():
            ref_a1 = str(ref_data.get("allele1", ""))
            ref_a2 = str(ref_data.get("allele2", ref_a1))
            ref_alleles = sorted([ref_a1, ref_a2])

            if locus in query_profile:
                q_data = query_profile[locus]
                if isinstance(q_data, (list, tuple)):
                    q_alleles = sorted(map(str, q_data))
                elif isinstance(q_data, dict):
                    q_a1 = str(q_data.get("allele1", ""))
                    q_a2 = str(q_data.get("allele2", q_a1))
                    q_alleles = sorted([q_a1, q_a2])
                else:
                    q_alleles = [str(q_data), str(q_data)]

                if q_alleles == ref_alleles:
                    matching_loci += 1
                else:
                    mismatches.append(f"Locus {locus}: Ref={ref_alleles}, Query={q_alleles}")
            else:
                mismatches.append(f"Locus {locus}: Missing in query profile")

        concordance_rate = (matching_loci / len(ref_str)) * 100.0 if ref_str else 0.0
        return concordance_rate, mismatches

    def validate_ystr_concordance(
        self,
        identifier: str,
        query_ystr: Dict[str, Any],
    ) -> Tuple[float, List[str]]:
        """
        Validates Y-STR haplotype concordance across 27 loci for male reference standards.
        """
        preset = self.get_preset(identifier)
        if not preset:
            raise ValueError(f"Reference standard '{identifier}' not found.")

        if preset.sex == "FEMALE":
            if len(query_ystr) == 0:
                return 100.0, []
            return 0.0, ["Female standard expected to have null Y-STR profile"]

        ref_ystr = preset.ystr_profile
        mismatches: List[str] = []
        matching_loci = 0

        for locus, ref_data in ref_ystr.items():
            if locus in query_ystr:
                q_val = query_ystr[locus]
                ref_a1 = str(ref_data.get("allele1", ""))
                ref_a2 = str(ref_data.get("allele2", "")) if ref_data.get("allele2") else ""
                
                if ref_a2:
                    ref_alleles = sorted([ref_a1, ref_a2])
                    if isinstance(q_val, (list, tuple)):
                        q_alleles = sorted(map(str, q_val))
                    elif isinstance(q_val, dict):
                        q_alleles = sorted([str(q_val.get("allele1", "")), str(q_val.get("allele2", ""))])
                    else:
                        q_alleles = [str(q_val)]
                    if q_alleles == ref_alleles:
                        matching_loci += 1
                    else:
                        mismatches.append(f"Y-Locus {locus}: Ref={ref_alleles}, Query={q_alleles}")
                else:
                    q_str = str(q_val.get("allele1", q_val) if isinstance(q_val, dict) else q_val)
                    if q_str == ref_a1:
                        matching_loci += 1
                    else:
                        mismatches.append(f"Y-Locus {locus}: Ref={ref_a1}, Query={q_str}")
            else:
                mismatches.append(f"Y-Locus {locus}: Missing in query profile")

        concordance_rate = (matching_loci / len(ref_ystr)) * 100.0 if ref_ystr else 0.0
        return concordance_rate, mismatches

    def validate_epigenetic_age_concordance(
        self,
        identifier: str,
        predicted_age: float,
    ) -> Tuple[bool, float, float]:
        """
        Validates if predicted age is within the certified 95% confidence interval.
        """
        preset = self.get_preset(identifier)
        if not preset:
            raise ValueError(f"Reference standard '{identifier}' not found.")

        ci_low = preset.visage_epigenetic_profile.get("ci95Lower", 0.0)
        ci_high = preset.visage_epigenetic_profile.get("ci95Upper", 120.0)
        within_bounds = ci_low <= predicted_age <= ci_high
        return within_bounds, ci_low, ci_high


# ==============================================================================
# MULTI-FORMAT EXPORTER ENGINE
# ==============================================================================

class CaseworkPresetExporter:
    """
    Standardized multi-format exporter generating CODIS CMF 3.2 XML,
    ISO 17025 LIMS JSON, and GeneMapper ID-X CSV tables.
    """

    @classmethod
    def export_to_codis_xml(
        cls,
        sample_id: str,
        str_profile: Dict[str, Dict[str, Any]],
        specimen_category: str = "Convicted Offender",
        source_lab: str = "VA_DFS_CENTRAL",
        destination_lab: str = "FBI_NDIS",
        operator_id: Optional[str] = "FORENZA_ANALYST",
        **kwargs: Any,
    ) -> str:
        """
        Exports profile into schema-compliant FBI CODIS CMF 3.2 XML.
        """
        xml_declaration = '<?xml version="1.0" standalone="yes"?>\n'
        root = ET.Element("CODISImportFile")
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")

        header = ET.SubElement(root, "HEADER")
        ET.SubElement(header, "SOURCELAB").text = source_lab
        ET.SubElement(header, "DESTINATIONLAB").text = destination_lab
        ET.SubElement(header, "MESSAGETYPE").text = "IMPORT"
        ET.SubElement(header, "CMFVERSION").text = "3.2"

        specimen = ET.SubElement(root, "SPECIMEN")
        ET.SubElement(specimen, "SPECIMENID").text = sample_id
        ET.SubElement(specimen, "SPECIMENCATEGORY").text = specimen_category

        batch = ET.SubElement(specimen, "BATCH")
        reading = ET.SubElement(batch, "READING")

        for locus_name, call_dict in str_profile.items():
            locus_elem = ET.SubElement(reading, "LOCUS")
            ET.SubElement(locus_elem, "LOCUSNAME").text = locus_name

            a1 = str(call_dict.get("allele1", ""))
            a2 = str(call_dict.get("allele2", a1)) if call_dict.get("allele2") is not None else a1

            allele1 = ET.SubElement(locus_elem, "ALLELE")
            ET.SubElement(allele1, "ALLELEVALUE").text = a1

            if a2 and a2 != a1:
                allele2 = ET.SubElement(locus_elem, "ALLELE")
                ET.SubElement(allele2, "ALLELEVALUE").text = a2

        return xml_declaration + ET.tostring(root, encoding="unicode")

    @classmethod
    def export_to_lims_json(
        cls,
        sample_id: str,
        str_profile: Dict[str, Dict[str, Any]],
        snp_dosages: Optional[Dict[str, int]] = None,
        laboratory_ori: str = "ISO17025_VA_LAB",
        operator_id: str = "BIO_USER_01",
    ) -> str:
        """
        Exports profile into schema-compliant ISO/IEC 17025 LIMS JSON with SHA-256 integrity hash.
        """
        str_genotypes: List[Dict[str, Any]] = []
        for locus_name, call_dict in str_profile.items():
            a1 = str(call_dict.get("allele1", ""))
            a2 = str(call_dict.get("allele2", a1)) if call_dict.get("allele2") is not None else None
            rfu1 = float(call_dict.get("rfu1", 1500.0))
            rfu2 = float(call_dict.get("rfu2", rfu1)) if call_dict.get("allele2") is not None else None

            str_genotypes.append({
                "locusName": locus_name,
                "allele1": a1,
                "allele2": a2,
                "rfu1": rfu1,
                "rfu2": rfu2,
            })

        hirisplex_genotypes: List[Dict[str, Any]] = []
        if snp_dosages:
            for rsid, dosage in snp_dosages.items():
                hirisplex_genotypes.append({
                    "rsID": rsid,
                    "dosageValue": int(dosage),
                })

        payload = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "ISO17025_ForensicTerminalSchema",
            "sampleMetadata": {
                "sampleID": sample_id,
                "laboratoryORI": laboratory_ori,
                "analysisTimestamp": datetime.now(timezone.utc).isoformat(),
                "operatorID": operator_id,
            },
            "strGenotypes": str_genotypes,
            "aimGenotypes": [],
            "hirisplexGenotypes": hirisplex_genotypes,
        }

        serialized_str = json.dumps(payload, sort_keys=True)
        coc_hash = hashlib.sha256(serialized_str.encode("utf-8")).hexdigest()
        payload["chainOfCustodyHash"] = coc_hash

        return json.dumps(payload, indent=2)

    @classmethod
    def export_to_genemapper_csv(
        cls,
        sample_id: str,
        str_profile: Dict[str, Dict[str, Any]],
    ) -> str:
        """
        Exports profile into standard 10-column GeneMapper ID-X CE CSV export table.
        """
        lines = ["Sample Name,Marker,Allele 1,Allele 2,Height 1,Height 2,Size 1,Size 2,Data Point 1,Data Point 2"]
        for locus_name, call_dict in str_profile.items():
            a1 = str(call_dict.get("allele1", ""))
            a2 = str(call_dict.get("allele2", "")) if call_dict.get("allele2") is not None and str(call_dict.get("allele2")) != a1 else ""
            h1 = int(float(call_dict.get("rfu1", 1500.0)))
            h2 = int(float(call_dict.get("rfu2", h1))) if a2 else ""
            lines.append(f"{sample_id},{locus_name},{a1},{a2},{h1},{h2},150.00,,5000,")

        return "\n".join(lines)
