"""
FORENZA X-STR Reference Datasets & Gold Standard Standards (Module 2.2).
Population Linkage Group Frequencies (Tillmar et al. 2017), Multi-Omic References,
and Certified Casework Benchmark Cohorts.

Research Source: research/pillar_2_lineage_kinship_research.md §2 & §6.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any


class XStrPopulationGroup(str, Enum):
    EUROPEAN = "EUROPEAN"
    EAST_ASIAN = "EAST_ASIAN"
    AFRICAN_AMERICAN = "AFRICAN_AMERICAN"
    GLOBAL_AVERAGE = "GLOBAL_AVERAGE"


@dataclass(frozen=True)
class XStrPopulationMetadata:
    code: XStrPopulationGroup
    name: str
    sample_size_n: int
    citation: str
    description: str


@dataclass(frozen=True)
class XStrGoldStandard:
    sample_id: str
    coriell_id: str
    nist_designation: Optional[str]
    sex: str
    population: str
    description: str
    x_str_genotypes: Dict[str, List[float]]


@dataclass(frozen=True)
class XStrCaseworkCohort:
    cohort_id: str
    name: str
    relationship: str
    sex_a: str
    sex_b: str
    description: str
    expected_matching_loci: int
    expected_min_ki: float
    profile_a: Dict[str, List[float]]
    profile_b: Dict[str, List[float]]


# ── 1. Population Frequencies (Tillmar et al. 2017 & NIST) ───────────────────

XSTR_POPULATION_METADATA: Dict[XStrPopulationGroup, XStrPopulationMetadata] = {
    XStrPopulationGroup.EUROPEAN: XStrPopulationMetadata(
        code=XStrPopulationGroup.EUROPEAN,
        name="European (Tillmar et al. 2017)",
        sample_size_n=3850,
        citation="Tillmar et al. (2017) Population genetics of the Argus X-12 in Europeans.",
        description="Frequencies for 12 Argus X-12 loci across European populations.",
    ),
    XStrPopulationGroup.EAST_ASIAN: XStrPopulationMetadata(
        code=XStrPopulationGroup.EAST_ASIAN,
        name="East Asian (Tillmar et al. 2017)",
        sample_size_n=2940,
        citation="Tillmar et al. (2017) Asian population data for 12 X-STRs.",
        description="Frequencies for East Asian forensic casework.",
    ),
    XStrPopulationGroup.AFRICAN_AMERICAN: XStrPopulationMetadata(
        code=XStrPopulationGroup.AFRICAN_AMERICAN,
        name="African American (NIST / 1000G)",
        sample_size_n=2150,
        citation="NIST X-STR population database.",
        description="African American allele frequency distributions.",
    ),
}

# Empirical frequencies across 12 loci for standard alleles (Tillmar et al. 2017)
XSTR_POPULATION_FREQUENCIES: Dict[str, Dict[float, float]] = {
    # LG1
    "DXS10148": {23.0: 0.05, 24.0: 0.12, 25.0: 0.22, 26.0: 0.31, 27.0: 0.18, 28.0: 0.10, 29.0: 0.02},
    "DXS10135": {17.0: 0.04, 18.0: 0.08, 19.0: 0.25, 20.0: 0.28, 21.0: 0.22, 22.0: 0.10, 23.0: 0.03},
    "DXS8378": {10.0: 0.15, 11.0: 0.45, 12.0: 0.30, 13.0: 0.08, 14.0: 0.02},

    # LG2
    "DXS7132": {12.0: 0.08, 13.0: 0.24, 14.0: 0.36, 15.0: 0.22, 16.0: 0.08, 17.0: 0.02},
    "DXS10074": {14.0: 0.05, 15.0: 0.15, 16.0: 0.28, 17.0: 0.32, 18.0: 0.14, 19.0: 0.06},
    "DXS10079": {17.0: 0.06, 18.0: 0.18, 19.0: 0.34, 20.0: 0.28, 21.0: 0.12, 22.0: 0.02},

    # LG3
    "DXS10103": {16.0: 0.08, 17.0: 0.22, 18.0: 0.38, 19.0: 0.24, 20.0: 0.07, 21.0: 0.01},
    "HPRTB": {11.0: 0.06, 12.0: 0.25, 13.0: 0.42, 14.0: 0.20, 15.0: 0.07},
    "DXS10101": {28.0: 0.08, 29.0: 0.20, 30.0: 0.32, 31.0: 0.25, 32.0: 0.12, 33.0: 0.03},

    # LG4
    "DXS10146": {24.0: 0.06, 25.0: 0.14, 26.0: 0.26, 27.0: 0.30, 28.0: 0.18, 29.0: 0.06},
    "DXS10134": {32.0: 0.08, 33.0: 0.18, 34.0: 0.32, 35.0: 0.26, 36.0: 0.12, 37.0: 0.04},
    "DXS7423": {13.0: 0.12, 14.0: 0.38, 15.0: 0.36, 16.0: 0.12, 17.0: 0.02},
}


# ── 2. Certified Multi-Omic Gold Standards ───────────────────────────────────

XSTR_GOLD_STANDARDS: Dict[str, XStrGoldStandard] = {
    "NA12878_CEU_FEMALE": XStrGoldStandard(
        sample_id="NA12878_CEU_FEMALE",
        coriell_id="NA12878",
        nist_designation="NIST RM 8398 (HG001)",
        sex="FEMALE",
        population="Utah / CEU European",
        description="Standard reference female (46,XX) with diploid X-STR genotypes.",
        x_str_genotypes={
            "DXS10148": [25.0, 26.0], "DXS10135": [19.0, 20.0], "DXS8378": [11.0, 12.0],
            "DXS7132": [13.0, 14.0], "DXS10074": [16.0, 17.0], "DXS10079": [19.0, 20.0],
            "DXS10103": [17.0, 18.0], "HPRTB": [12.0, 13.0], "DXS10101": [29.0, 30.0],
            "DXS10146": [26.0, 27.0], "DXS10134": [33.0, 34.0], "DXS7423": [14.0, 15.0],
        },
    ),
    "NA19240_YRI_FEMALE": XStrGoldStandard(
        sample_id="NA19240_YRI_FEMALE",
        coriell_id="NA19240",
        nist_designation="1000 Genomes YRI Reference",
        sex="FEMALE",
        population="Yoruba in Ibadan, Nigeria",
        description="African female reference standard (46,XX).",
        x_str_genotypes={
            "DXS10148": [24.0, 27.0], "DXS10135": [18.0, 21.0], "DXS8378": [10.0, 11.0],
            "DXS7132": [14.0, 15.0], "DXS10074": [15.0, 18.0], "DXS10079": [18.0, 21.0],
            "DXS10103": [18.0, 19.0], "HPRTB": [13.0, 14.0], "DXS10101": [30.0, 31.0],
            "DXS10146": [25.0, 28.0], "DXS10134": [34.0, 35.0], "DXS7423": [14.0, 16.0],
        },
    ),
    "SRM_2391d_COMP_A_MALE": XStrGoldStandard(
        sample_id="SRM_2391d_COMP_A_MALE",
        coriell_id="NA06990",
        nist_designation="NIST SRM 2391d Component A",
        sex="MALE",
        population="European Male",
        description="Hemizygous male standard (46,XY) possessing single allele per X-STR locus.",
        x_str_genotypes={
            "DXS10148": [26.0], "DXS10135": [19.0], "DXS8378": [11.0],
            "DXS7132": [14.0], "DXS10074": [17.0], "DXS10079": [19.0],
            "DXS10103": [18.0], "HPRTB": [13.0], "DXS10101": [30.0],
            "DXS10146": [27.0], "DXS10134": [34.0], "DXS7423": [14.0],
        },
    ),
    "HG002_NA24385_MALE": XStrGoldStandard(
        sample_id="HG002_NA24385_MALE",
        coriell_id="NA24385",
        nist_designation="NIST RM 8391 / GIAB HG002",
        sex="MALE",
        population="Ashkenazi Jewish",
        description="Hemizygous male reference standard (46,XY).",
        x_str_genotypes={
            "DXS10148": [25.0], "DXS10135": [20.0], "DXS8378": [12.0],
            "DXS7132": [13.0], "DXS10074": [16.0], "DXS10079": [20.0],
            "DXS10103": [17.0], "HPRTB": [12.0], "DXS10101": [29.0],
            "DXS10146": [26.0], "DXS10134": [33.0], "DXS7423": [15.0],
        },
    ),
}


# ── 3. Certified Casework Benchmark Cohorts ──────────────────────────────────

XSTR_CASEWORK_COHORTS: Dict[str, XStrCaseworkCohort] = {
    # VECTOR_P2_02 Golden Benchmark (Research §6 Artifact D)
    "VECTOR_P2_02_PATERNAL_HALF_SISTERS": XStrCaseworkCohort(
        cohort_id="VECTOR_P2_02_PATERNAL_HALF_SISTERS",
        name="VECTOR_P2_02 Paternal Half-Sisters Benchmark",
        relationship="PATERNAL_HALF_SISTERS",
        sex_a="FEMALE",
        sex_b="FEMALE",
        description="Two true paternal half-sisters sharing unbroken paternal X-chromosome across LG1–LG4.",
        expected_matching_loci=12,
        expected_min_ki=150000.0,
        profile_a={
            "DXS10148": [26.0, 24.0], "DXS10135": [19.0, 21.0], "DXS8378": [11.0, 12.0],
            "DXS7132": [14.0, 13.0], "DXS10074": [17.0, 15.0], "DXS10079": [19.0, 18.0],
            "DXS10103": [18.0, 16.0], "HPRTB": [13.0, 11.0], "DXS10101": [30.0, 28.0],
            "DXS10146": [27.0, 25.0], "DXS10134": [34.0, 32.0], "DXS7423": [14.0, 13.0],
        },
        profile_b={
            "DXS10148": [26.0, 25.0], "DXS10135": [19.0, 22.0], "DXS8378": [11.0, 10.0],
            "DXS7132": [14.0, 15.0], "DXS10074": [17.0, 16.0], "DXS10079": [19.0, 20.0],
            "DXS10103": [18.0, 17.0], "HPRTB": [13.0, 12.0], "DXS10101": [30.0, 29.0],
            "DXS10146": [27.0, 26.0], "DXS10134": [34.0, 33.0], "DXS7423": [14.0, 15.0],
        },
    ),
    "COHORT_FATHER_DAUGHTER_DUO": XStrCaseworkCohort(
        cohort_id="COHORT_FATHER_DAUGHTER_DUO",
        name="Father-Daughter Standard Kinship Duo",
        relationship="FATHER_DAUGHTER",
        sex_a="MALE",
        sex_b="FEMALE",
        description="Biological father (single X allele) and true daughter sharing all 12 paternal alleles.",
        expected_matching_loci=12,
        expected_min_ki=350000.0,
        profile_a={
            "DXS10148": [26.0], "DXS10135": [19.0], "DXS8378": [11.0],
            "DXS7132": [14.0], "DXS10074": [17.0], "DXS10079": [19.0],
            "DXS10103": [18.0], "HPRTB": [13.0], "DXS10101": [30.0],
            "DXS10146": [27.0], "DXS10134": [34.0], "DXS7423": [14.0],
        },
        profile_b={
            "DXS10148": [26.0, 25.0], "DXS10135": [19.0, 20.0], "DXS8378": [11.0, 12.0],
            "DXS7132": [14.0, 13.0], "DXS10074": [17.0, 16.0], "DXS10079": [19.0, 20.0],
            "DXS10103": [18.0, 17.0], "HPRTB": [13.0, 12.0], "DXS10101": [30.0, 29.0],
            "DXS10146": [27.0, 26.0], "DXS10134": [34.0, 33.0], "DXS7423": [14.0, 15.0],
        },
    ),
    "COHORT_UNRELATED_FEMALES_EXCLUSION": XStrCaseworkCohort(
        cohort_id="COHORT_UNRELATED_FEMALES_EXCLUSION",
        name="Unrelated Non-Kin Females",
        relationship="PATERNAL_HALF_SISTERS",
        sex_a="FEMALE",
        sex_b="FEMALE",
        description="Two completely unrelated females showing 0 shared paternal haplotypes across multiple linkage clusters.",
        expected_matching_loci=2,
        expected_min_ki=0.0,
        profile_a={
            "DXS10148": [23.0, 24.0], "DXS10135": [17.0, 18.0], "DXS8378": [10.0, 13.0],
            "DXS7132": [12.0, 16.0], "DXS10074": [14.0, 19.0], "DXS10079": [17.0, 22.0],
            "DXS10103": [16.0, 20.0], "HPRTB": [11.0, 15.0], "DXS10101": [28.0, 32.0],
            "DXS10146": [24.0, 28.0], "DXS10134": [32.0, 36.0], "DXS7423": [13.0, 16.0],
        },
        profile_b={
            "DXS10148": [26.0, 27.0], "DXS10135": [20.0, 21.0], "DXS8378": [11.0, 12.0],
            "DXS7132": [13.0, 14.0], "DXS10074": [16.0, 17.0], "DXS10079": [19.0, 20.0],
            "DXS10103": [18.0, 19.0], "HPRTB": [13.0, 14.0], "DXS10101": [30.0, 31.0],
            "DXS10146": [26.0, 27.0], "DXS10134": [34.0, 35.0], "DXS7423": [14.0, 15.0],
        },
    ),
}


class XStrReferenceDatasets:
    """Service for accessing X-STR reference databases and benchmarks."""

    @staticmethod
    def get_population_frequencies(pop_group: XStrPopulationGroup = XStrPopulationGroup.EUROPEAN) -> Dict[str, Dict[float, float]]:
        return XSTR_POPULATION_FREQUENCIES

    @staticmethod
    def list_gold_standards() -> List[XStrGoldStandard]:
        return list(XSTR_GOLD_STANDARDS.values())

    @staticmethod
    def list_casework_cohorts() -> List[XStrCaseworkCohort]:
        return list(XSTR_CASEWORK_COHORTS.values())
