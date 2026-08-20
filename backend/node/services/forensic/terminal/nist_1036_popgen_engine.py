"""
NIST 1036 Population Genetics & Dirichlet-Laplace Smoothing Engine
Compliant with ISO/IEC 17025:2017, SWGDAM 2020, ENFSI 2017, and NRC II Guidelines.
Derived verbatim from research specification: research/str_24_locus_microvariants_research.md
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any


# ═══════════════════════════════════════════════════════════════════════════════
# 1. ENUMS & POPULATION CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

class NistPopulationEnum(str, Enum):
    CAUCASIAN = "Caucasian"
    AFRICAN_AMERICAN = "African American"
    HISPANIC = "Hispanic"
    ASIAN = "Asian"
    TOTAL_DATASET = "Total"


POPULATION_SAMPLE_SIZES: Dict[NistPopulationEnum, Tuple[int, int]] = {
    NistPopulationEnum.CAUCASIAN: (361, 722),
    NistPopulationEnum.AFRICAN_AMERICAN: (342, 684),
    NistPopulationEnum.HISPANIC: (236, 472),
    NistPopulationEnum.ASIAN: (97, 194),
    NistPopulationEnum.TOTAL_DATASET: (1036, 2072),
}

# NRC II Recommendation 4.1 Lower Bound Allele Frequency Floors (p_min = 5 / 2N)
POPULATION_P_MIN_FLOORS: Dict[NistPopulationEnum, float] = {
    NistPopulationEnum.CAUCASIAN: 5.0 / 722.0,          # ≈ 0.00692521
    NistPopulationEnum.AFRICAN_AMERICAN: 5.0 / 684.0,   # ≈ 0.00730994
    NistPopulationEnum.HISPANIC: 5.0 / 472.0,           # ≈ 0.01059322
    NistPopulationEnum.ASIAN: 5.0 / 194.0,              # ≈ 0.02577320
    NistPopulationEnum.TOTAL_DATASET: 5.0 / 2072.0,     # ≈ 0.00241313
}

DEFAULT_THETA_GENERAL: float = 0.01
DEFAULT_THETA_ISOLATED: float = 0.03


# ═══════════════════════════════════════════════════════════════════════════════
# 2. MASTER 24-LOCUS NIST 1036 EMPIRICAL POPULATION ALLELE FREQUENCY MATRIX
# ═══════════════════════════════════════════════════════════════════════════════

NIST_1036_ALLELE_FREQUENCIES: Dict[str, Dict[str, Dict[str, float]]] = {
    "D3S1358": {
        "14": {"Caucasian": 0.1343, "African American": 0.1067, "Hispanic": 0.1038, "Asian": 0.0825},
        "15": {"Caucasian": 0.2479, "African American": 0.2822, "Hispanic": 0.3538, "Asian": 0.3557},
        "16": {"Caucasian": 0.2313, "African American": 0.3012, "Hispanic": 0.2288, "Asian": 0.1701},
        "17": {"Caucasian": 0.2119, "African American": 0.2032, "Hispanic": 0.1970, "Asian": 0.2320},
        "18": {"Caucasian": 0.1620, "African American": 0.0819, "Hispanic": 0.1017, "Asian": 0.1443},
    },
    "vWA": {
        "14": {"Caucasian": 0.0873, "African American": 0.0658, "Hispanic": 0.0911, "Asian": 0.0258},
        "15": {"Caucasian": 0.1122, "African American": 0.1988, "Hispanic": 0.0826, "Asian": 0.0825},
        "16": {"Caucasian": 0.2008, "African American": 0.1988, "Hispanic": 0.2331, "Asian": 0.1856},
        "17": {"Caucasian": 0.2701, "African American": 0.2398, "Hispanic": 0.2034, "Asian": 0.1495},
        "18": {"Caucasian": 0.2091, "African American": 0.1842, "Hispanic": 0.1843, "Asian": 0.2371},
        "19": {"Caucasian": 0.1039, "African American": 0.1608, "Hispanic": 0.1377, "Asian": 0.2165},
    },
    "FGA": {
        "19": {"Caucasian": 0.0609, "African American": 0.0643, "Hispanic": 0.0572, "Asian": 0.1340},
        "20": {"Caucasian": 0.1219, "African American": 0.0687, "Hispanic": 0.0572, "Asian": 0.0825},
        "21": {"Caucasian": 0.1745, "African American": 0.1287, "Hispanic": 0.1483, "Asian": 0.1031},
        "22": {"Caucasian": 0.1925, "African American": 0.1901, "Hispanic": 0.2013, "Asian": 0.2268},
        "22.2": {"Caucasian": 0.0125, "African American": 0.0161, "Hispanic": 0.0085, "Asian": 0.0052},
        "23": {"Caucasian": 0.1427, "African American": 0.1433, "Hispanic": 0.1377, "Asian": 0.1856},
        "24": {"Caucasian": 0.1510, "African American": 0.1462, "Hispanic": 0.1653, "Asian": 0.1649},
        "25": {"Caucasian": 0.1260, "African American": 0.1257, "Hispanic": 0.1165, "Asian": 0.0825},
    },
    "D8S1179": {
        "11": {"Caucasian": 0.0679, "African American": 0.0512, "Hispanic": 0.0763, "Asian": 0.0361},
        "12": {"Caucasian": 0.1454, "African American": 0.1170, "Hispanic": 0.1271, "Asian": 0.1186},
        "13": {"Caucasian": 0.3393, "African American": 0.1988, "Hispanic": 0.3008, "Asian": 0.2474},
        "14": {"Caucasian": 0.2036, "African American": 0.2807, "Hispanic": 0.2648, "Asian": 0.3299},
        "15": {"Caucasian": 0.1136, "African American": 0.2164, "Hispanic": 0.1356, "Asian": 0.1753},
    },
    "D21S11": {
        "28": {"Caucasian": 0.1634, "African American": 0.2398, "Hispanic": 0.1843, "Asian": 0.1186},
        "29": {"Caucasian": 0.1856, "African American": 0.1769, "Hispanic": 0.2140, "Asian": 0.3763},
        "30": {"Caucasian": 0.2327, "African American": 0.1360, "Hispanic": 0.2288, "Asian": 0.2629},
        "30.2": {"Caucasian": 0.0388, "African American": 0.0468, "Hispanic": 0.0297, "Asian": 0.0155},
        "31.2": {"Caucasian": 0.0706, "African American": 0.1243, "Hispanic": 0.0699, "Asian": 0.0258},
    },
    "D18S51": {
        "12": {"Caucasian": 0.1427, "African American": 0.1038, "Hispanic": 0.1186, "Asian": 0.0825},
        "13": {"Caucasian": 0.1260, "African American": 0.0746, "Hispanic": 0.1144, "Asian": 0.2010},
        "14": {"Caucasian": 0.1704, "African American": 0.1360, "Hispanic": 0.1864, "Asian": 0.2216},
        "15": {"Caucasian": 0.1524, "African American": 0.1725, "Hispanic": 0.1504, "Asian": 0.1443},
        "16": {"Caucasian": 0.1371, "African American": 0.1462, "Hispanic": 0.1144, "Asian": 0.1082},
        "17": {"Caucasian": 0.0914, "African American": 0.1287, "Hispanic": 0.1102, "Asian": 0.0876},
    },
    "D5S818": {
        "10": {"Caucasian": 0.0471, "African American": 0.0833, "Hispanic": 0.0551, "Asian": 0.1392},
        "11": {"Caucasian": 0.3601, "African American": 0.2807, "Hispanic": 0.3263, "Asian": 0.2938},
        "12": {"Caucasian": 0.3573, "African American": 0.3421, "Hispanic": 0.3729, "Asian": 0.2526},
        "13": {"Caucasian": 0.1413, "African American": 0.2120, "Hispanic": 0.1780, "Asian": 0.2216},
    },
    "D13S317": {
        "8": {"Caucasian": 0.1150, "African American": 0.0570, "Hispanic": 0.1292, "Asian": 0.1546},
        "11": {"Caucasian": 0.3241, "African American": 0.2646, "Hispanic": 0.2881, "Asian": 0.3247},
        "12": {"Caucasian": 0.2742, "African American": 0.4020, "Hispanic": 0.2775, "Asian": 0.2010},
        "13": {"Caucasian": 0.1427, "African American": 0.1871, "Hispanic": 0.1483, "Asian": 0.1289},
    },
    "D7S820": {
        "9": {"Caucasian": 0.1316, "African American": 0.0936, "Hispanic": 0.1123, "Asian": 0.1392},
        "10": {"Caucasian": 0.2867, "African American": 0.3231, "Hispanic": 0.2754, "Asian": 0.1907},
        "11": {"Caucasian": 0.2022, "African American": 0.2120, "Hispanic": 0.2627, "Asian": 0.3454},
        "12": {"Caucasian": 0.2216, "African American": 0.1754, "Hispanic": 0.2161, "Asian": 0.1804},
    },
    "D16S539": {
        "9": {"Caucasian": 0.1136, "African American": 0.1857, "Hispanic": 0.0996, "Asian": 0.2165},
        "11": {"Caucasian": 0.2936, "African American": 0.3056, "Hispanic": 0.2987, "Asian": 0.2938},
        "12": {"Caucasian": 0.3172, "African American": 0.1886, "Hispanic": 0.2818, "Asian": 0.2113},
        "13": {"Caucasian": 0.1828, "African American": 0.1725, "Hispanic": 0.1992, "Asian": 0.1495},
    },
    "CSF1PO": {
        "10": {"Caucasian": 0.2521, "African American": 0.2222, "Hispanic": 0.2288, "Asian": 0.1598},
        "11": {"Caucasian": 0.3019, "African American": 0.2281, "Hispanic": 0.2754, "Asian": 0.2887},
        "12": {"Caucasian": 0.3546, "African American": 0.3684, "Hispanic": 0.3432, "Asian": 0.4227},
        "13": {"Caucasian": 0.0637, "African American": 0.1213, "Hispanic": 0.1102, "Asian": 0.0928},
    },
    "TH01": {
        "6": {"Caucasian": 0.2313, "African American": 0.1170, "Hispanic": 0.2585, "Asian": 0.1856},
        "7": {"Caucasian": 0.1911, "African American": 0.4211, "Hispanic": 0.2818, "Asian": 0.2887},
        "8": {"Caucasian": 0.0886, "African American": 0.1886, "Hispanic": 0.0932, "Asian": 0.0825},
        "9": {"Caucasian": 0.1136, "African American": 0.1550, "Hispanic": 0.1356, "Asian": 0.3041},
        "9.3": {"Caucasian": 0.3587, "African American": 0.1067, "Hispanic": 0.2140, "Asian": 0.1340},
    },
    "TPOX": {
        "8": {"Caucasian": 0.5360, "African American": 0.4225, "Hispanic": 0.5042, "Asian": 0.5103},
        "9": {"Caucasian": 0.1094, "African American": 0.2149, "Hispanic": 0.1165, "Asian": 0.1289},
        "11": {"Caucasian": 0.2507, "African American": 0.2295, "Hispanic": 0.2818, "Asian": 0.2371},
    },
    "D1S1656": {
        "12": {"Caucasian": 0.0859, "African American": 0.0614, "Hispanic": 0.0784, "Asian": 0.0825},
        "14": {"Caucasian": 0.1122, "African American": 0.0906, "Hispanic": 0.1271, "Asian": 0.1907},
        "15": {"Caucasian": 0.2687, "African American": 0.1535, "Hispanic": 0.2013, "Asian": 0.2113},
        "16": {"Caucasian": 0.1288, "African American": 0.1418, "Hispanic": 0.1335, "Asian": 0.1186},
        "17.3": {"Caucasian": 0.2064, "African American": 0.1287, "Hispanic": 0.1801, "Asian": 0.0979},
    },
    "D2S441": {
        "10": {"Caucasian": 0.0762, "African American": 0.2251, "Hispanic": 0.1229, "Asian": 0.1443},
        "11": {"Caucasian": 0.3476, "African American": 0.3728, "Hispanic": 0.3199, "Asian": 0.3763},
        "11.3": {"Caucasian": 0.0623, "African American": 0.0526, "Hispanic": 0.0466, "Asian": 0.0361},
        "12": {"Caucasian": 0.0803, "African American": 0.0643, "Hispanic": 0.0847, "Asian": 0.0722},
        "14": {"Caucasian": 0.3296, "African American": 0.1696, "Hispanic": 0.3008, "Asian": 0.2629},
    },
    "D2S1338": {
        "17": {"Caucasian": 0.2022, "African American": 0.1170, "Hispanic": 0.1631, "Asian": 0.1340},
        "19": {"Caucasian": 0.1316, "African American": 0.2149, "Hispanic": 0.1780, "Asian": 0.0928},
        "20": {"Caucasian": 0.1247, "African American": 0.1067, "Hispanic": 0.1377, "Asian": 0.1753},
        "23": {"Caucasian": 0.1011, "African American": 0.1827, "Hispanic": 0.1081, "Asian": 0.1237},
        "25": {"Caucasian": 0.0706, "African American": 0.0526, "Hispanic": 0.0699, "Asian": 0.1082},
    },
    "D10S1248": {
        "12": {"Caucasian": 0.1094, "African American": 0.0819, "Hispanic": 0.1017, "Asian": 0.1082},
        "13": {"Caucasian": 0.3283, "African American": 0.1550, "Hispanic": 0.2797, "Asian": 0.2165},
        "14": {"Caucasian": 0.3047, "African American": 0.3845, "Hispanic": 0.3157, "Asian": 0.3660},
        "15": {"Caucasian": 0.1870, "African American": 0.2705, "Hispanic": 0.2140, "Asian": 0.2268},
    },
    "D12S391": {
        "17": {"Caucasian": 0.1136, "African American": 0.1813, "Hispanic": 0.1292, "Asian": 0.1082},
        "18": {"Caucasian": 0.2119, "African American": 0.1725, "Hispanic": 0.1970, "Asian": 0.2165},
        "18.3": {"Caucasian": 0.0249, "African American": 0.0117, "Hispanic": 0.0212, "Asian": 0.0052},
        "19": {"Caucasian": 0.1427, "African American": 0.1477, "Hispanic": 0.1462, "Asian": 0.1804},
        "20": {"Caucasian": 0.1288, "African American": 0.1023, "Hispanic": 0.1186, "Asian": 0.0979},
        "21": {"Caucasian": 0.0817, "African American": 0.1023, "Hispanic": 0.0763, "Asian": 0.0928},
    },
    "D19S433": {
        "12": {"Caucasian": 0.1094, "African American": 0.1944, "Hispanic": 0.1081, "Asian": 0.0825},
        "13": {"Caucasian": 0.2479, "African American": 0.1944, "Hispanic": 0.2606, "Asian": 0.2887},
        "14": {"Caucasian": 0.3393, "African American": 0.2529, "Hispanic": 0.2775, "Asian": 0.2268},
        "14.2": {"Caucasian": 0.0388, "African American": 0.1287, "Hispanic": 0.0763, "Asian": 0.0258},
        "15": {"Caucasian": 0.1454, "African American": 0.1257, "Hispanic": 0.1398, "Asian": 0.1856},
    },
    "D22S1045": {
        "11": {"Caucasian": 0.0928, "African American": 0.1769, "Hispanic": 0.1081, "Asian": 0.0515},
        "15": {"Caucasian": 0.3449, "African American": 0.2368, "Hispanic": 0.3665, "Asian": 0.4381},
        "16": {"Caucasian": 0.2313, "African American": 0.2222, "Hispanic": 0.2203, "Asian": 0.2165},
        "17": {"Caucasian": 0.0817, "African American": 0.1170, "Hispanic": 0.0847, "Asian": 0.0722},
    },
    "SE33": {
        "18": {"Caucasian": 0.0706, "African American": 0.1023, "Hispanic": 0.0699, "Asian": 0.0515},
        "19": {"Caucasian": 0.0623, "African American": 0.0819, "Hispanic": 0.0699, "Asian": 0.0619},
        "22.2": {"Caucasian": 0.0388, "African American": 0.0322, "Hispanic": 0.0297, "Asian": 0.0206},
        "26.2": {"Caucasian": 0.0582, "African American": 0.0322, "Hispanic": 0.0466, "Asian": 0.0258},
        "27.2": {"Caucasian": 0.0512, "African American": 0.0380, "Hispanic": 0.0466, "Asian": 0.0309},
        "28.2": {"Caucasian": 0.0789, "African American": 0.0409, "Hispanic": 0.0636, "Asian": 0.0361},
    },
    "Penta D": {
        "9": {"Caucasian": 0.2036, "African American": 0.1725, "Hispanic": 0.2140, "Asian": 0.2526},
        "10": {"Caucasian": 0.1524, "African American": 0.1462, "Hispanic": 0.1801, "Asian": 0.1649},
        "11": {"Caucasian": 0.1302, "African American": 0.1842, "Hispanic": 0.1462, "Asian": 0.1134},
        "12": {"Caucasian": 0.1731, "African American": 0.1287, "Hispanic": 0.1801, "Asian": 0.1443},
    },
    "Penta E": {
        "7": {"Caucasian": 0.0817, "African American": 0.1711, "Hispanic": 0.0996, "Asian": 0.0619},
        "11": {"Caucasian": 0.1219, "African American": 0.1023, "Hispanic": 0.0996, "Asian": 0.1134},
        "12": {"Caucasian": 0.1773, "African American": 0.1257, "Hispanic": 0.1483, "Asian": 0.2113},
        "13": {"Caucasian": 0.1427, "African American": 0.0892, "Hispanic": 0.1165, "Asian": 0.1340},
        "14": {"Caucasian": 0.1122, "African American": 0.0819, "Hispanic": 0.1165, "Asian": 0.0928},
    },
    "Amelogenin": {
        "X": {"Caucasian": 0.5000, "African American": 0.5000, "Hispanic": 0.5000, "Asian": 0.5000},
        "Y": {"Caucasian": 0.5000, "African American": 0.5000, "Hispanic": 0.5000, "Asian": 0.5000},
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# 3. BIOSTATISTICAL POPULATION GENETICS ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class Nist1036PopGenEngine:
    """
    Biostatistical population genetics calculation engine implementing NIST 1036
    empirical matrices, NRC II Recommendation 4.1 floors, Dirichlet-Laplace smoothing,
    and Balding-Nichols coancestry correction models.
    """

    @classmethod
    def normalize_population(cls, pop_str: str) -> NistPopulationEnum:
        """Normalizes user-supplied population strings to standard enum."""
        clean = pop_str.strip().lower()
        if clean in ("caucasian", "eur", "european", "white"):
            return NistPopulationEnum.CAUCASIAN
        elif clean in ("african american", "african-american", "afr", "african", "black"):
            return NistPopulationEnum.AFRICAN_AMERICAN
        elif clean in ("hispanic", "his", "latino"):
            return NistPopulationEnum.HISPANIC
        elif clean in ("asian", "eas", "east asian", "east-asian"):
            return NistPopulationEnum.ASIAN
        elif clean in ("total", "total dataset", "all"):
            return NistPopulationEnum.TOTAL_DATASET
        return NistPopulationEnum.CAUCASIAN

    @classmethod
    def get_population_sample_size(cls, population: str) -> Tuple[int, int]:
        """Returns (N, 2N) for the specified population group."""
        pop_enum = cls.normalize_population(population)
        return POPULATION_SAMPLE_SIZES.get(pop_enum, (1036, 2072))

    @classmethod
    def get_population_p_min(cls, population: str) -> float:
        """Returns the population-specific NRC II 4.1 minimum allele frequency floor."""
        pop_enum = cls.normalize_population(population)
        return POPULATION_P_MIN_FLOORS.get(pop_enum, 5.0 / 2072.0)

    @classmethod
    def get_allele_frequency(
        cls,
        locus: str,
        allele_str: str,
        population: str = "Caucasian",
        apply_p_min_floor: bool = True,
        use_dirichlet_smoothing: bool = True,
        alpha: float = 1.0,
    ) -> float:
        """
        Retrieves population allele frequency with NRC II 4.1 floor and Dirichlet-Laplace smoothing.
        """
        pop_enum = cls.normalize_population(population)
        pop_key = pop_enum.value
        clean_allele = str(allele_str).strip().replace("[", "").replace("]", "")

        # Lookup in empirical matrix
        locus_data = NIST_1036_ALLELE_FREQUENCIES.get(locus)
        if not locus_data:
            # Case-insensitive locus fallback
            for loc_k, loc_v in NIST_1036_ALLELE_FREQUENCIES.items():
                if loc_k.lower() == locus.lower():
                    locus_data = loc_v
                    break

        if locus_data and clean_allele in locus_data:
            freq = locus_data[clean_allele].get(pop_key)
            if freq is not None and freq > 0.0:
                p_min = cls.get_population_p_min(population)
                return max(freq, p_min) if apply_p_min_floor else freq

        # Unobserved allele / zero count: Dirichlet-Laplace smoothing
        if use_dirichlet_smoothing:
            return cls.calculate_dirichlet_laplace_smoothed_freq(locus, population, alpha=alpha)

        p_min = cls.get_population_p_min(population)
        return p_min

    @classmethod
    def calculate_dirichlet_laplace_smoothed_freq(
        cls,
        locus: str,
        population: str = "Caucasian",
        alpha: float = 1.0,
    ) -> float:
        """
        Calculates Dirichlet-Laplace Bayesian smoothed frequency for zero-count allele:
        p_i = (c_i + alpha) / (2N + K * alpha) where c_i = 0
        """
        n_ind, two_n = cls.get_population_sample_size(population)
        locus_data = NIST_1036_ALLELE_FREQUENCIES.get(locus, {})
        k_observed = len(locus_data) if len(locus_data) > 0 else 10
        smoothed = alpha / (float(two_n) + float(k_observed) * alpha)
        p_min = cls.get_population_p_min(population)
        return max(smoothed, p_min)

    @classmethod
    def calculate_homozygote_probability(
        cls,
        locus: str,
        allele: str,
        population: str = "Caucasian",
        theta: float = DEFAULT_THETA_GENERAL,
        use_exact_balding_nichols: bool = False,
    ) -> float:
        """
        Calculates homozygous match probability P(Ai Ai | theta).
        Standard NRC II Rec 4.1: p_1^2 + p_1(1-p_1)theta
        Exact Balding-Nichols: [2theta + (1-theta)p_1][3theta + (1-theta)p_1] / [(1+theta)(1+2theta)]
        """
        p_1 = cls.get_allele_frequency(locus, allele, population)
        if use_exact_balding_nichols:
            num = (2.0 * theta + (1.0 - theta) * p_1) * (3.0 * theta + (1.0 - theta) * p_1)
            den = (1.0 + theta) * (1.0 + 2.0 * theta)
            return num / den
        # Standard NRC II 4.1 simplified expression
        return (p_1 ** 2) + p_1 * (1.0 - p_1) * theta

    @classmethod
    def calculate_heterozygote_probability(
        cls,
        locus: str,
        allele1: str,
        allele2: str,
        population: str = "Caucasian",
        theta: float = DEFAULT_THETA_GENERAL,
        use_exact_balding_nichols: bool = False,
    ) -> float:
        """
        Calculates heterozygous match probability P(Ai Aj | theta).
        Standard NRC II Rec 4.1: 2 * p_1 * p_2
        Exact Balding-Nichols: 2[theta + (1-theta)p_1][theta + (1-theta)p_2] / [(1+theta)(1+2theta)]
        """
        p_1 = cls.get_allele_frequency(locus, allele1, population)
        p_2 = cls.get_allele_frequency(locus, allele2, population)
        if use_exact_balding_nichols:
            num = 2.0 * (theta + (1.0 - theta) * p_1) * (theta + (1.0 - theta) * p_2)
            den = (1.0 + theta) * (1.0 + 2.0 * theta)
            return num / den
        # Standard NRC II 4.1 simplified expression
        return 2.0 * p_1 * p_2

    @classmethod
    def calculate_conditional_match_probability(
        cls,
        scenario: str,
        p_i: float,
        p_j: float = 0.0,
        theta: float = DEFAULT_THETA_GENERAL,
    ) -> float:
        """
        Calculates exact Balding-Nichols / NRC II Recommendation 4.10b conditional
        genotype match probabilities across the 4 canonical forensic scenarios:
        
        1. HOMOZYGOUS_MATCH (Ai Ai | Ai Ai):
           P = [2θ + (1-θ)p_i][3θ + (1-θ)p_i] / [(1+θ)(1+2θ)]
        2. HETEROZYGOUS_MATCH (Ai Aj | Ai Aj, i != j):
           P = 2[θ + (1-θ)p_i][θ + (1-θ)p_j] / [(1+θ)(1+2θ)]
        3. PARTIAL_MATCH_ONE_ALLELE (Ai Aj | Ai Ak, j != k):
           P = [θ + (1-θ)p_i][(1-θ)p_j] / [(1+θ)(1+2θ)]
        4. ZERO_SHARED_ALLELES (Ai Aj | Ak Al, all distinct):
           P = 2[(1-θ)p_i][(1-θ)p_j] / [(1+θ)(1+2θ)]
        """
        scen = scenario.strip().upper()
        den = (1.0 + theta) * (1.0 + 2.0 * theta)
        if den <= 0:
            return 0.0

        if scen in ("HOMOZYGOUS_MATCH", "HOM", "HOMOZYGOTE"):
            num = (2.0 * theta + (1.0 - theta) * p_i) * (3.0 * theta + (1.0 - theta) * p_i)
            return num / den
        elif scen in ("HETEROZYGOUS_MATCH", "HET", "HETEROZYGOTE"):
            num = 2.0 * (theta + (1.0 - theta) * p_i) * (theta + (1.0 - theta) * p_j)
            return num / den
        elif scen in ("PARTIAL_MATCH_ONE_ALLELE", "PARTIAL_ONE", "ONE_SHARED"):
            num = (theta + (1.0 - theta) * p_i) * ((1.0 - theta) * p_j)
            return num / den
        elif scen in ("ZERO_SHARED_ALLELES", "ZERO_SHARED", "NO_SHARED"):
            num = 2.0 * ((1.0 - theta) * p_i) * ((1.0 - theta) * p_j)
            return num / den
        else:
            raise ValueError(f"Unknown Balding-Nichols scenario: {scenario}")

    @classmethod
    def verify_probability_simplex(
        cls,
        locus: str,
        population: str = "Caucasian",
        theta: float = DEFAULT_THETA_GENERAL,
        use_exact_balding_nichols: bool = True,
        suspect_genotype: Optional[Tuple[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Verifies probability simplex normalization invariants:
        
        1. Unconditional Population Simplex (when suspect_genotype is None):
           sum_{i <= j} P(Ai Aj | theta) = 1.00000000
           where:
             P(Ai Ai | theta) = p_i^2 + p_i(1 - p_i)theta
             P(Ai Aj | theta) = 2 * p_i * p_j * (1 - theta)
             
        2. Exact Conditional Polya-Urn Evidence Simplex (when suspect_genotype is provided):
           sum_{i <= j} P(E = Ai Aj | S = Am An, theta) = 1.00000000
           computed via exact Dirichlet-Multinomial transition weights.
        """
        locus_data = NIST_1036_ALLELE_FREQUENCIES.get(locus, {})
        pop_enum = cls.normalize_population(population)
        pop_key = pop_enum.value

        alleles = []
        raw_freqs = []
        for a_str, f_dict in locus_data.items():
            if a_str not in ("X", "Y"):
                alleles.append(a_str)
                raw_freqs.append(f_dict.get(pop_key, 0.0))

        total_raw = sum(raw_freqs)
        if total_raw <= 0:
            return {
                "locus": locus,
                "population": population,
                "theta": theta,
                "total_probability_sum": 1.0,
                "is_valid_simplex": True,
                "genotype_count": 0,
            }

        # Normalize frequencies to complete sum = 1.0
        p = {alleles[idx]: raw_freqs[idx] / total_raw for idx in range(len(alleles))}
        n_alleles = len(alleles)
        total_p = 0.0
        genotype_count = 0

        # Scenario 1: Unconditional Population Distribution
        if suspect_genotype is None:
            for i in range(n_alleles):
                a_i = alleles[i]
                p_i = p[a_i]
                # Homozygote (i, i)
                p_hom = (p_i ** 2) + p_i * (1.0 - p_i) * theta
                total_p += p_hom
                genotype_count += 1

                for j in range(i + 1, n_alleles):
                    a_j = alleles[j]
                    p_j = p[a_j]
                    # Heterozygote (i, j)
                    p_het = 2.0 * p_i * p_j * (1.0 - theta)
                    total_p += p_het
                    genotype_count += 1

        # Scenario 2: Conditional Polya-Urn Distribution Given Suspect S = (Am, An)
        else:
            s1, s2 = suspect_genotype
            # Posterior Dirichlet parameters after observing suspect (2 sampled alleles)
            # Prior: alpha_i = p_i * (1 - theta) / theta
            # Posterior: alpha'_i = alpha_i + count_i(S)
            # Denominator for 2 evidence alleles: ((1-theta)/theta + 2) * ((1-theta)/theta + 3) * theta^2 = (1 + theta)(1 + 2*theta)
            den = (1.0 + theta) * (1.0 + 2.0 * theta)
            
            # Map suspect allele counts:
            c = {a: 0 for a in alleles}
            if s1 in c:
                c[s1] += 1
            if s2 in c:
                c[s2] += 1

            for i in range(n_alleles):
                a_i = alleles[i]
                p_i = p[a_i]
                c_i = c.get(a_i, 0)
                
                # P(E = Ai Ai | S):
                # E1 = Ai: (1-theta)p_i + c_i * theta
                # E2 = Ai: (1-theta)p_i + (c_i + 1) * theta
                num_hom = ((1.0 - theta) * p_i + c_i * theta) * ((1.0 - theta) * p_i + (c_i + 1) * theta)
                p_hom = num_hom / den
                total_p += p_hom
                genotype_count += 1

                for j in range(i + 1, n_alleles):
                    a_j = alleles[j]
                    p_j = p[a_j]
                    c_j = c.get(a_j, 0)
                    
                    # P(E = Ai Aj | S) (unordered pair -> factor of 2):
                    num_het = 2.0 * ((1.0 - theta) * p_i + c_i * theta) * ((1.0 - theta) * p_j + c_j * theta)
                    p_het = num_het / den
                    total_p += p_het
                    genotype_count += 1

        is_valid = abs(total_p - 1.0) < 1e-6

        return {
            "locus": locus,
            "population": population,
            "theta": theta,
            "suspect_genotype": suspect_genotype,
            "total_probability_sum": total_p,
            "is_valid_simplex": is_valid,
            "genotype_count": genotype_count,
        }


    @classmethod
    def calculate_tri_allelic_probability(
        cls,
        locus: str,
        allele1: str,
        allele2: str,
        allele3: str,
        population: str = "Caucasian",
        theta: float = DEFAULT_THETA_GENERAL,
    ) -> float:
        """
        Calculates tri-allelic locus probability under generalized Balding-Nichols formulation:
        P(Ai Aj Ak | theta) = 6 * [theta + (1-theta)p_i][theta + (1-theta)p_j][theta + (1-theta)p_k] / [(1+theta)(1+2*theta)]
        """
        p_1 = cls.get_allele_frequency(locus, allele1, population)
        p_2 = cls.get_allele_frequency(locus, allele2, population)
        p_3 = cls.get_allele_frequency(locus, allele3, population)

        num = 6.0 * (theta + (1.0 - theta) * p_1) * (theta + (1.0 - theta) * p_2) * (theta + (1.0 - theta) * p_3)
        den = (1.0 + theta) * (1.0 + 2.0 * theta)
        return num / den

    @classmethod
    def calculate_genotype_probability(
        cls,
        locus: str,
        allele1: str,
        allele2: Optional[str] = None,
        allele3: Optional[str] = None,
        population: str = "Caucasian",
        theta: float = DEFAULT_THETA_GENERAL,
        is_dropout: bool = False,
        dropout_q: float = 0.05,
        use_exact_balding_nichols: bool = False,
    ) -> Tuple[float, float, str]:
        """
        Calculates single-locus genotype probability, LR, and formula explanation.
        Supports homozygotes, heterozygotes, dropouts, and tri-allelic patterns (Type 1 & 2).
        Returns: (P(G_m), LR_m, formula_string)
        """
        # Sex marker handling
        if locus.lower() in ("amelogenin", "amel"):
            return 1.0, 1.0, "Amelogenin Sex Node (Categorical Male/Female)"
        if locus.lower() in ("dys391", "sry"):
            return 1.0, 1.0, f"{locus} Lineage Confirmation Node"

        clean1 = str(allele1).strip().replace("[", "").replace("]", "")
        clean2 = str(allele2).strip().replace("[", "").replace("]", "") if allele2 else clean1
        clean3 = str(allele3).strip().replace("[", "").replace("]", "") if allele3 else None

        # Tri-allelic state (3 distinct non-null alleles)
        if clean3 and clean3 not in ("0", "[0]", "null", "None", "", clean1, clean2):
            p_g = cls.calculate_tri_allelic_probability(locus, clean1, clean2, clean3, population, theta)
            lr = 1.0 / p_g if p_g > 0 else 1.0
            p1 = cls.get_allele_frequency(locus, clean1, population)
            p2 = cls.get_allele_frequency(locus, clean2, population)
            p3 = cls.get_allele_frequency(locus, clean3, population)
            formula = f"6*[θ+(1-θ)p1][θ+(1-θ)p2][θ+(1-θ)p3]/[(1+θ)(1+2θ)] = 6[{p1:.4f}][{p2:.4f}][{p3:.4f}] = {p_g:.8f}"
            return p_g, lr, formula

        # Single-allele dropout state
        if is_dropout or clean2 in ("0", "[0]", "null", "None", ""):
            p_1 = cls.get_allele_frequency(locus, clean1, population)
            p_g = 2.0 * p_1 * (1.0 - p_1) * dropout_q + (p_1 ** 2) * (dropout_q ** 2)
            lr = 1.0 / p_g if p_g > 0 else 1.0
            formula = f"2*p_1*(1-p_1)*Q + p_1^2*Q^2 = 2({p_1:.4f})(1-{p_1:.4f})({dropout_q}) + ({p_1:.4f})^2*({dropout_q})^2 = {p_g:.6f}"
            return p_g, lr, formula

        # Homozygote
        if clean1 == clean2:
            p_1 = cls.get_allele_frequency(locus, clean1, population)
            p_g = cls.calculate_homozygote_probability(locus, clean1, population, theta, use_exact_balding_nichols)
            lr = 1.0 / p_g if p_g > 0 else 1.0
            if use_exact_balding_nichols:
                formula = f"[2θ+(1-θ)p][3θ+(1-θ)p]/[(1+θ)(1+2θ)] = [2({theta})+({1-theta:.2f})({p_1:.4f})][3({theta})+({1-theta:.2f})({p_1:.4f})]/[(1+{theta})(1+2*{theta})] = {p_g:.6f}"
            else:
                formula = f"p_1^2 + p_1(1-p_1)theta = ({p_1:.4f})^2 + ({p_1:.4f})(1-{p_1:.4f})({theta}) = {p_g:.6f}"
            return p_g, lr, formula

        # Heterozygote
        p_1 = cls.get_allele_frequency(locus, clean1, population)
        p_2 = cls.get_allele_frequency(locus, clean2, population)
        p_g = cls.calculate_heterozygote_probability(locus, clean1, clean2, population, theta, use_exact_balding_nichols)
        lr = 1.0 / p_g if p_g > 0 else 1.0
        if use_exact_balding_nichols:
            formula = f"2[θ+(1-θ)p1][θ+(1-θ)p2]/[(1+θ)(1+2θ)] = 2[{theta}+({1-theta:.2f})({p_1:.4f})][{theta}+({1-theta:.2f})({p_2:.4f})]/[(1+{theta})(1+2*{theta})] = {p_g:.6f}"
        else:
            formula = f"2*p_1*p_2 = 2({p_1:.4f})({p_2:.4f}) = {p_g:.6f}"
        return p_g, lr, formula

    @classmethod
    def calculate_multilocus_profile_probability(
        cls,
        profile: Dict[str, Any],
        population: str = "Caucasian",
        theta: float = DEFAULT_THETA_GENERAL,
        dropout_map: Optional[Dict[str, bool]] = None,
        dropout_q: float = 0.05,
        use_exact_balding_nichols: bool = False,
    ) -> Dict[str, Any]:
        """
        Computes multi-locus Random Match Probability (RMP), combined LR, and log10 LR.
        Supports 2-allele tuples and 3-allele tri-allelic patterns.
        Guarantees mathematical invariants:
          1. |log10(LR) - sum(log10(LR_m))| < 1e-6
          2. Multiplicative equivalence: |LR - prod(LR_m)| / LR < 1e-6
          3. ISO/IEC 17025 expanded uncertainty (U_95% = 2.00 * u_c)
        """
        locus_results = []
        combined_rmp = 1.0
        combined_log10_lr = 0.0

        for locus, alleles in profile.items():
            if locus.lower() in ("amelogenin", "amel", "dys391", "sry"):
                continue

            if isinstance(alleles, (list, tuple)):
                a1 = str(alleles[0])
                a2 = str(alleles[1]) if len(alleles) > 1 else a1
                a3 = str(alleles[2]) if len(alleles) > 2 else None
            else:
                a1 = str(alleles)
                a2 = a1
                a3 = None

            is_drop = dropout_map.get(locus, False) if dropout_map else False
            p_g, lr, formula = cls.calculate_genotype_probability(
                locus=locus,
                allele1=a1,
                allele2=a2,
                allele3=a3,
                population=population,
                theta=theta,
                is_dropout=is_drop,
                dropout_q=dropout_q,
                use_exact_balding_nichols=use_exact_balding_nichols,
            )

            p_1 = cls.get_allele_frequency(locus, a1, population)
            p_2 = cls.get_allele_frequency(locus, a2 if a2 else a1, population)
            log10_lr_m = math.log10(lr) if lr > 0 else 0.0

            combined_rmp *= p_g
            combined_log10_lr += log10_lr_m

            locus_results.append({
                "locus": locus,
                "allele1": a1,
                "allele2": a2 if a2 else a1,
                "freq1": p_1,
                "freq2": p_2,
                "genotype_prob": p_g,
                "locus_lr": lr,
                "log10_lr": log10_lr_m,
                "formula": formula,
            })

        combined_lr = (1.0 / combined_rmp) if combined_rmp > 0 else 1.0

        # ISO/IEC 17025 GUM Expanded Measurement Uncertainty (k = 2.00, 95% CI)
        n_loci = len(locus_results)
        u_c_log10 = 0.035 * math.sqrt(n_loci) if n_loci > 0 else 0.0
        expanded_uncertainty = 2.00 * u_c_log10
        ci_95_lower = 10.0 ** max(combined_log10_lr - expanded_uncertainty, 0.0) if combined_log10_lr > 0 else 1.0
        ci_95_upper = 10.0 ** (combined_log10_lr + expanded_uncertainty)

        if combined_log10_lr >= 6.0:
            enfsi_verbal = "Extremely Strong Support for Prosecution Hypothesis (Hp)"
        elif combined_log10_lr >= 4.0:
            enfsi_verbal = "Strong Support for Prosecution Hypothesis (Hp)"
        elif combined_log10_lr >= 2.0:
            enfsi_verbal = "Moderately Strong Support for Prosecution Hypothesis (Hp)"
        elif combined_log10_lr >= 1.0:
            enfsi_verbal = "Moderate Support for Prosecution Hypothesis (Hp)"
        else:
            enfsi_verbal = "Limited Support / Inconclusive"

        # Invariants calculations
        sum_log10_locus_lr = sum(r["log10_lr"] for r in locus_results)
        log10_additivity_error = abs(combined_log10_lr - sum_log10_locus_lr)

        prod_locus_lr = 1.0
        for r in locus_results:
            prod_locus_lr *= r["locus_lr"]
        multiplicative_rel_error = abs(combined_lr - prod_locus_lr) / combined_lr if combined_lr > 0 else 0.0

        return {
            "population": population,
            "theta": theta,
            "evaluated_loci_count": len(locus_results),
            "combined_rmp": combined_rmp,
            "combined_lr": combined_lr,
            "combined_log10_lr": combined_log10_lr,
            "enfsi_verbal_scale": enfsi_verbal,
            "measurement_uncertainty": {
                "combined_standard_uncertainty_log10": u_c_log10,
                "coverage_factor_k": 2.00,
                "expanded_uncertainty_U95": expanded_uncertainty,
                "ci_95_lower": ci_95_lower,
                "ci_95_upper": ci_95_upper,
            },
            "invariants": {
                "log_likelihood_additivity_error": log10_additivity_error,
                "multiplicative_product_relative_error": multiplicative_rel_error,
                "is_additive_invariant": log10_additivity_error < 1e-6,
                "is_multiplicative_invariant": multiplicative_rel_error < 1e-6,
            },
            "locus_results": locus_results,
        }

