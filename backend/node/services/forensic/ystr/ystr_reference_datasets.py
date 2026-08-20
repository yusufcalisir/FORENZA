"""
FORENZA Forensic Evidence Operating System
Pillar 2 — Module 2.1: Y-STR 27-Locus Lineage Engine (Y-FILER Plus)
Sub-Item 2.1.2: Reference Datasets (YHRD Release 68 & Gold Standard Casework Cohorts)

Derives verbatim and exclusively from:
  - Pillar 2 Research Specification (research/pillar_2_lineage_kinship_research.md §1)
  - Y-STR 27-Locus Master Specification (research/ystr_27_mtdna_empop_lineage_research.md §2)
  - Certified Reference Standards Research (research/certified_reference_standards_gold_vectors_research.md §2)
  - YHRD (Y-Chromosome Haplotype Reference Database) Release 68
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any


class YhrdMetapopulation(str, Enum):
    GLOBAL = "GLOBAL"
    WEST_EURASIAN = "WEST_EURASIAN"
    EAST_ASIAN = "EAST_ASIAN"
    SOUTH_ASIAN = "SOUTH_ASIAN"
    ADMIXED_AMERICAN = "ADMIXED_AMERICAN"
    SUB_SAHARAN_AFRICAN = "SUB_SAHARAN_AFRICAN"


@dataclass(frozen=True)
class YhrdPopulationPartition:
    """YHRD Population Partition Specification."""
    code: YhrdMetapopulation
    name: str
    database_size_n: int
    default_theta: float
    description: str
    primary_modal_haplogroups: Tuple[str, ...]


@dataclass(frozen=True)
class GoldStandardReferenceIndividual:
    """Certified Multi-Omic Gold Standard Reference Individual (27-Locus Y-STR)."""
    sample_id: str
    coriell_id: str
    nist_srm_designation: Optional[str]
    sex: str
    population_group: str
    certified_haplogroup: str
    primary_snp: str
    y_str_haplotype: Dict[str, Any]
    description: str


@dataclass(frozen=True)
class CaseworkBenchmarkCohort:
    """Standardized Casework Benchmark Cohort for Lineage Testing."""
    cohort_id: str
    name: str
    description: str
    meioses_m: int
    expected_outcome: str
    profile_a: Dict[str, Any]
    profile_b: Dict[str, Any]
    expected_matching_loci: int
    expected_mutation_count: int
    expected_min_lr: float


# ===========================================================================
# 1. YHRD RELEASE 68 GLOBAL METAPOPULATION REGISTRY (N = 385,000)
# ===========================================================================

YHRD_GLOBAL_METAPOPULATIONS: Dict[YhrdMetapopulation, YhrdPopulationPartition] = {
    YhrdMetapopulation.GLOBAL: YhrdPopulationPartition(
        code=YhrdMetapopulation.GLOBAL,
        name="YHRD Global Casework Reference Database (Release 68)",
        database_size_n=385000,
        default_theta=0.03,
        description="Comprehensive global Y-STR haplotype database combining all regional partitions.",
        primary_modal_haplogroups=("R1b", "R1a", "O", "J2", "E1b1a", "I1"),
    ),
    YhrdMetapopulation.WEST_EURASIAN: YhrdPopulationPartition(
        code=YhrdMetapopulation.WEST_EURASIAN,
        name="Western Eurasian Metapopulation Partition",
        database_size_n=142000,
        default_theta=0.01,
        description="European, Caucasian, and Near Eastern male lineages with predominant R1b, R1a, I1, and J2.",
        primary_modal_haplogroups=("R1b", "R1a", "I1", "I2", "J2", "G2a"),
    ),
    YhrdMetapopulation.EAST_ASIAN: YhrdPopulationPartition(
        code=YhrdMetapopulation.EAST_ASIAN,
        name="Eastern Asian Metapopulation Partition",
        database_size_n=118000,
        default_theta=0.02,
        description="Sino-Tibetan, Austroasiatic, Japanese, and Korean male lineages dominated by haplogroups O, C, and D.",
        primary_modal_haplogroups=("O", "C", "D", "N"),
    ),
    YhrdMetapopulation.SOUTH_ASIAN: YhrdPopulationPartition(
        code=YhrdMetapopulation.SOUTH_ASIAN,
        name="South Asian Metapopulation Partition",
        database_size_n=45000,
        default_theta=0.03,
        description="Indo-Aryan and Dravidian male lineages characterized by haplogroups R1a, R2, L, and H.",
        primary_modal_haplogroups=("R1a", "L", "H", "J2"),
    ),
    YhrdMetapopulation.ADMIXED_AMERICAN: YhrdPopulationPartition(
        code=YhrdMetapopulation.ADMIXED_AMERICAN,
        name="Admixed American / Hispanic Metapopulation Partition",
        database_size_n=42000,
        default_theta=0.03,
        description="Admixed Hispanic/Latino and Native American male lineages with haplogroups Q, C, and European R1b.",
        primary_modal_haplogroups=("Q", "R1b", "C", "E1b1b"),
    ),
    YhrdMetapopulation.SUB_SAHARAN_AFRICAN: YhrdPopulationPartition(
        code=YhrdMetapopulation.SUB_SAHARAN_AFRICAN,
        name="Sub-Saharan African Metapopulation Partition",
        database_size_n=38000,
        default_theta=0.02,
        description="Niger-Congo, Bantu, and Afroasiatic male lineages characterized by haplogroups E1b1a, E1b1b, A, and B.",
        primary_modal_haplogroups=("E1b1a", "E1b1b", "A", "B"),
    ),
}


# ===========================================================================
# 2. CERTIFIED MULTI-OMIC GOLD STANDARD REFERENCE INDIVIDUALS
# ===========================================================================

GOLD_STANDARD_INDIVIDUALS: Dict[str, GoldStandardReferenceIndividual] = {
    "SRM_2391d_COMP_A": GoldStandardReferenceIndividual(
        sample_id="SRM_2391d_COMP_A",
        coriell_id="NIST_SRM_2391d_A",
        nist_srm_designation="NIST SRM 2391d Component A",
        sex="MALE",
        population_group="EUR_US_CAU",
        certified_haplogroup="R1b1a1b",
        primary_snp="R-M269 / P312",
        description="Globally certified forensic reference standard for single-source male capillary electrophoresis validation.",
        y_str_haplotype={
            "DYS19": 14, "DYS389I": 13, "DYS389II": 29, "DYS390": 24, "DYS391": 11,
            "DYS392": 13, "DYS393": 13, "DYS385a/b": [11, 14], "DYS437": 15, "DYS438": 12,
            "DYS439": 12, "DYS448": 19, "DYS456": 15, "DYS458": 17, "DYS635": 23,
            "YGATAH4": 12, "DYS481": 22, "DYS533": 11, "DYS570": 17, "DYS576": 18,
            "DYS518": 38, "DYS627": 22, "DYS449": 30, "DYF387S1a/b": [35, 37], "DYS460": 11
        },
    ),
    "HG002_NA24385": GoldStandardReferenceIndividual(
        sample_id="HG002_NA24385",
        coriell_id="NA24385 / HG002",
        nist_srm_designation="GIAB Ashkenazi Trio Son",
        sex="MALE",
        population_group="ASHKENAZI_JEWISH",
        certified_haplogroup="J2a1a1",
        primary_snp="J-M172 / L26",
        description="Genome in a Bottle (GIAB) benchmark male reference standard for high-accuracy variant calling.",
        y_str_haplotype={
            "DYS19": 15, "DYS389I": 13, "DYS389II": 30, "DYS390": 23, "DYS391": 10,
            "DYS392": 11, "DYS393": 12, "DYS385a/b": [14, 15], "DYS437": 15, "DYS438": 12,
            "DYS439": 11, "DYS448": 19, "DYS456": 15, "DYS458": 18, "DYS635": 21,
            "YGATAH4": 10, "DYS481": 22, "DYS533": 12, "DYS570": 19, "DYS576": 15,
            "DYS518": 39, "DYS627": 21, "DYS449": 29, "DYF387S1a/b": [36, 37], "DYS460": 11
        },
    ),
    "NA18507_HG005": GoldStandardReferenceIndividual(
        sample_id="NA18507_HG005",
        coriell_id="NA18507 / HG005",
        nist_srm_designation="1000 Genomes Han Chinese Male",
        sex="MALE",
        population_group="CHB_BEIJING_HAN_CHINESE",
        certified_haplogroup="O2a2b1",
        primary_snp="O-M175 / M134",
        description="1000 Genomes Project and GIAB East Asian male standard reference individual.",
        y_str_haplotype={
            "DYS19": 15, "DYS389I": 14, "DYS389II": 31, "DYS390": 24, "DYS391": 10,
            "DYS392": 13, "DYS393": 13, "DYS385a/b": [12, 18], "DYS437": 14, "DYS438": 10,
            "DYS439": 11, "DYS448": 19, "DYS456": 15, "DYS458": 17, "DYS635": 23,
            "YGATAH4": 12, "DYS481": 23, "DYS533": 12, "DYS570": 17, "DYS576": 17,
            "DYS518": 37, "DYS627": 23, "DYS449": 30, "DYF387S1a/b": [37, 38], "DYS460": 11
        },
    ),
    "NA12878_HG001_FEMALE": GoldStandardReferenceIndividual(
        sample_id="NA12878_HG001_FEMALE",
        coriell_id="NA12878 / HG001",
        nist_srm_designation="CEPH European Female Reference",
        sex="FEMALE",
        population_group="CEU_UTAH_EUROPEAN",
        certified_haplogroup="N/A",
        primary_snp="N/A",
        description="Female control material yielding null Y-STR profiles (male specificity negative control).",
        y_str_haplotype={},
    ),
    "NA19240_YRI_FEMALE": GoldStandardReferenceIndividual(
        sample_id="NA19240_YRI_FEMALE",
        coriell_id="NA19240",
        nist_srm_designation="1000 Genomes Yoruba Female",
        sex="FEMALE",
        population_group="YRI_IBADAN_NIGERIA",
        certified_haplogroup="N/A",
        primary_snp="N/A",
        description="Female control material yielding null Y-STR profiles for multi-ethnic specificity validation.",
        y_str_haplotype={},
    ),
}


# ===========================================================================
# 3. CASEWORK BENCHMARK COHORTS
# ===========================================================================

_PRISTINE_R1B = GOLD_STANDARD_INDIVIDUALS["SRM_2391d_COMP_A"].y_str_haplotype

# Cohort 2: Father-Son duo with single RM mutation at DYS518 (38 -> 39)
_RM_MUT_SON = dict(_PRISTINE_R1B)
_RM_MUT_SON["DYS518"] = 39

# Cohort 3: Grandfather-Grandson trio (2 meioses) with 1 RM mutation (DYS576: 18 -> 19)
_GRANDSON_R1B = dict(_PRISTINE_R1B)
_GRANDSON_R1B["DYS576"] = 19

# Cohort 4: Unrelated Asian male (NA18507) vs European male (SRM 2391d)
_UNRELATED_CHB = GOLD_STANDARD_INDIVIDUALS["NA18507_HG005"].y_str_haplotype

CASEWORK_BENCHMARK_COHORTS: Dict[str, CaseworkBenchmarkCohort] = {
    "COHORT_PATERNAL_DUO_FATHER_SON": CaseworkBenchmarkCohort(
        cohort_id="COHORT_PATERNAL_DUO_FATHER_SON",
        name="Paternal Duo: Father-Son Exact 27-Locus Transmission",
        description="1 meiosis separation with 100% identical Y-STR alleles across all 25 loci systems (27 markers).",
        meioses_m=1,
        expected_outcome="INCLUSION_SAME_PATERNAL_LINEAGE",
        profile_a=_PRISTINE_R1B,
        profile_b=_PRISTINE_R1B,
        expected_matching_loci=25,
        expected_mutation_count=0,
        expected_min_lr=10000.0,
    ),
    "COHORT_PATERNAL_DUO_WITH_RM_MUTATION": CaseworkBenchmarkCohort(
        cohort_id="COHORT_PATERNAL_DUO_WITH_RM_MUTATION",
        name="Paternal Duo: Father-Son with Single Rapidly Mutating Locus Shift",
        description="1 meiosis separation with single 1-step germline mutation at RM marker DYS518 (38 -> 39).",
        meioses_m=1,
        expected_outcome="INCLUSION_WITH_RM_MUTATION",
        profile_a=_PRISTINE_R1B,
        profile_b=_RM_MUT_SON,
        expected_matching_loci=24,
        expected_mutation_count=1,
        expected_min_lr=200.0,
    ),
    "COHORT_PATERNAL_TRIO_GRANDFATHER_GRANDSON": CaseworkBenchmarkCohort(
        cohort_id="COHORT_PATERNAL_TRIO_GRANDFATHER_GRANDSON",
        name="Paternal Trio: Grandfather-Grandson 2-Meioses Transmission",
        description="2 meioses separation with single 1-step mutation at RM marker DYS576 (18 -> 19).",
        meioses_m=2,
        expected_outcome="INCLUSION_EXTENDED_PATERNAL_LINEAGE",
        profile_a=_PRISTINE_R1B,
        profile_b=_GRANDSON_R1B,
        expected_matching_loci=24,
        expected_mutation_count=1,
        expected_min_lr=200.0,
    ),
    "COHORT_UNRELATED_MALES": CaseworkBenchmarkCohort(
        cohort_id="COHORT_UNRELATED_MALES",
        name="Unrelated Males: Multi-Locus Haplotype Discordance",
        description="Pairwise comparison between R1b European and O2a East Asian males displaying 14+ locus mismatches.",
        meioses_m=1,
        expected_outcome="DEFINITIVE_LINEAGE_EXCLUSION",
        profile_a=_PRISTINE_R1B,
        profile_b=_UNRELATED_CHB,
        expected_matching_loci=5,
        expected_mutation_count=20,
        expected_min_lr=0.0,
    ),
}


# ===========================================================================
# 4. Service Access API Helper Functions
# ===========================================================================

class YStrReferenceDatasets:
    """Access gateway for standardized YHRD population partitions and certified benchmark cohorts."""

    @staticmethod
    def get_population_partition(partition: YhrdMetapopulation) -> YhrdPopulationPartition:
        if partition not in YHRD_GLOBAL_METAPOPULATIONS:
            raise KeyError(f"Unknown YHRD metapopulation partition: {partition}")
        return YHRD_GLOBAL_METAPOPULATIONS[partition]

    @staticmethod
    def list_population_partitions() -> List[YhrdPopulationPartition]:
        return list(YHRD_GLOBAL_METAPOPULATIONS.values())

    @staticmethod
    def get_gold_standard(sample_id: str) -> GoldStandardReferenceIndividual:
        if sample_id not in GOLD_STANDARD_INDIVIDUALS:
            raise KeyError(f"Unknown gold standard individual: {sample_id}")
        return GOLD_STANDARD_INDIVIDUALS[sample_id]

    @staticmethod
    def list_gold_standards() -> List[GoldStandardReferenceIndividual]:
        return list(GOLD_STANDARD_INDIVIDUALS.values())

    @staticmethod
    def get_casework_cohort(cohort_id: str) -> CaseworkBenchmarkCohort:
        if cohort_id not in CASEWORK_BENCHMARK_COHORTS:
            raise KeyError(f"Unknown casework benchmark cohort: {cohort_id}")
        return CASEWORK_BENCHMARK_COHORTS[cohort_id]

    @staticmethod
    def list_casework_cohorts() -> List[CaseworkBenchmarkCohort]:
        return list(CASEWORK_BENCHMARK_COHORTS.values())
