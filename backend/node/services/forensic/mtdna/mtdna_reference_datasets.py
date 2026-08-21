"""
FORENZA Mitochondrial DNA (mtDNA) Reference Datasets & Gold Standards (Module 2.3).
EMPOP Release 15 Metapopulation Partitions, Multi-Omic References, and Casework Benchmark Cohorts.

Research Source: research/ystr_27_mtdna_empop_lineage_research.md §3 & §4.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any


class MtDnaPopulationGroup(str, Enum):
    GLOBAL = "GLOBAL"
    WEST_EURASIAN = "WEST_EURASIAN"
    EAST_ASIAN = "EAST_ASIAN"
    AFRICAN = "AFRICAN"
    ADMIXED_AMERICAN = "ADMIXED_AMERICAN"
    SOUTH_ASIAN = "SOUTH_ASIAN"


@dataclass(frozen=True)
class MtDnaPopulationMetadata:
    code: MtDnaPopulationGroup
    name: str
    sample_size_n: int
    citation: str
    description: str


@dataclass(frozen=True)
class MtDnaGoldStandard:
    sample_id: str
    coriell_id: str
    nist_designation: Optional[str]
    haplogroup: str
    population: str
    description: str
    variants: List[str]


@dataclass(frozen=True)
class MtDnaCaseworkCohort:
    cohort_id: str
    name: str
    relationship: str
    description: str
    expected_verdict: str
    expected_matches_k: int
    database_size_n: int
    expected_min_lr: float
    profile_a_variants: List[str]
    profile_b_variants: List[str]


# ── 1. EMPOP Release 15 Database Metapopulations ─────────────────────────────

MTDNA_EMPOP_METADATA: Dict[MtDnaPopulationGroup, MtDnaPopulationMetadata] = {
    MtDnaPopulationGroup.GLOBAL: MtDnaPopulationMetadata(
        code=MtDnaPopulationGroup.GLOBAL,
        name="Global EMPOP Database (Release 15)",
        sample_size_n=48500,
        citation="EMPOP (EDNAP Mitochondrial DNA Population Database) Release 15 (2023).",
        description="Global reference collection of 48,500 forensic-quality mitogenomes.",
    ),
    MtDnaPopulationGroup.WEST_EURASIAN: MtDnaPopulationMetadata(
        code=MtDnaPopulationGroup.WEST_EURASIAN,
        name="West Eurasian Metapopulation",
        sample_size_n=24500,
        citation="EMPOP West Eurasian Mitogenome Partition.",
        description="European, Middle Eastern, and North African reference lineages.",
    ),
    MtDnaPopulationGroup.EAST_ASIAN: MtDnaPopulationMetadata(
        code=MtDnaPopulationGroup.EAST_ASIAN,
        name="East Asian Metapopulation",
        sample_size_n=11200,
        citation="EMPOP East Asian Mitogenome Partition.",
        description="East Asian, Southeast Asian, and Siberian reference lineages.",
    ),
    MtDnaPopulationGroup.AFRICAN: MtDnaPopulationMetadata(
        code=MtDnaPopulationGroup.AFRICAN,
        name="African Metapopulation",
        sample_size_n=6400,
        citation="EMPOP Sub-Saharan African Mitogenome Partition.",
        description="Sub-Saharan African reference lineages (Macro-haplogroup L0-L6).",
    ),
    MtDnaPopulationGroup.ADMIXED_AMERICAN: MtDnaPopulationMetadata(
        code=MtDnaPopulationGroup.ADMIXED_AMERICAN,
        name="Admixed American Metapopulation",
        sample_size_n=4300,
        citation="EMPOP Admixed American Mitogenome Partition.",
        description="Indigenous American and Hispanic/Latino admixed lineages.",
    ),
    MtDnaPopulationGroup.SOUTH_ASIAN: MtDnaPopulationMetadata(
        code=MtDnaPopulationGroup.SOUTH_ASIAN,
        name="South Asian Metapopulation",
        sample_size_n=2100,
        citation="EMPOP South Asian Mitogenome Partition.",
        description="Indian Subcontinent reference lineages (Macro-haplogroups M & U).",
    ),
}


# ── 2. Certified Multi-Omic Gold Standards ───────────────────────────────────

MTDNA_GOLD_STANDARDS: Dict[str, MtDnaGoldStandard] = {
    "NA12878_CEU_FEMALE": MtDnaGoldStandard(
        sample_id="NA12878_CEU_FEMALE",
        coriell_id="NA12878",
        nist_designation="NIST RM 8398 (HG001)",
        haplogroup="H1",
        population="Utah / CEU European",
        description="Standard reference female (46,XX) with European H1 mitogenome.",
        variants=["263G", "315.1C", "750G", "16519C"],
    ),
    "NA19240_YRI_FEMALE": MtDnaGoldStandard(
        sample_id="NA19240_YRI_FEMALE",
        coriell_id="NA19240",
        nist_designation="1000 Genomes YRI Reference",
        haplogroup="L2a1",
        population="Yoruba in Ibadan, Nigeria",
        description="African female reference standard (46,XX) with African L2a1 mitogenome.",
        variants=[
            "146C", "152C", "182C", "198C", "263G", "309.1C", "315.1C",
            "750G", "16129C", "16223C", "16278C", "16390C", "16519C",
        ],
    ),
    "HG002_NA24385_MALE": MtDnaGoldStandard(
        sample_id="HG002_NA24385_MALE",
        coriell_id="NA24385",
        nist_designation="NIST RM 8391 / GIAB HG002",
        haplogroup="T2b",
        population="Ashkenazi Jewish",
        description="Hemizygous male standard (46,XY) with European T2b mitogenome.",
        variants=["263G", "315.1C", "16126C", "16294T", "16296T", "16519C"],
    ),
    "NA18507_HG005_MALE": MtDnaGoldStandard(
        sample_id="NA18507_HG005_MALE",
        coriell_id="NA18507",
        nist_designation="GIAB HG005 Han Chinese",
        haplogroup="D4a1",
        population="Han Chinese in Beijing",
        description="East Asian reference standard with D4a1 mitogenome.",
        variants=["263G", "309.1C", "315.1C", "16223C", "16362C", "16519C"],
    ),
    "NIST_SRM_2391d_COMP_A": MtDnaGoldStandard(
        sample_id="NIST_SRM_2391d_COMP_A",
        coriell_id="NA06990",
        nist_designation="NIST SRM 2391d Component A",
        haplogroup="H1a1",
        population="European Male",
        description="NIST certified reference standard with H1a1 mitogenome.",
        variants=["263G", "315.1C", "750G", "16162G", "16519C"],
    ),
}


# ── 3. Certified Casework Benchmark Cohorts ──────────────────────────────────

MTDNA_CASEWORK_COHORTS: Dict[str, MtDnaCaseworkCohort] = {
    "BENCHMARK_LINEAGE_A_EUR": MtDnaCaseworkCohort(
        cohort_id="BENCHMARK_LINEAGE_A_EUR",
        name="Benchmark LINEAGE-A (European Reference / EUR)",
        relationship="MATERNAL_LINEAGE_MATCH",
        description="Common European H1 haplotype (263G, 315.1C, 750G, 16519C) with k=1,420 in EMPOP (N=48,200).",
        expected_verdict="MATCH",
        expected_matches_k=1420,
        database_size_n=48200,
        expected_min_lr=30.0,
        profile_a_variants=["263G", "315.1C", "750G", "16519C"],
        profile_b_variants=["263G", "315.1C", "750G", "16519C"],
    ),
    "BENCHMARK_LINEAGE_B_AFR": MtDnaCaseworkCohort(
        cohort_id="BENCHMARK_LINEAGE_B_AFR",
        name="Benchmark LINEAGE-B (African American / AFR)",
        relationship="MATERNAL_LINEAGE_MATCH",
        description="Distinct African L2a1 haplotype with k=12 matches in EMPOP (N=48,200).",
        expected_verdict="MATCH",
        expected_matches_k=12,
        database_size_n=48200,
        expected_min_lr=2000.0,
        profile_a_variants=[
            "146C", "152C", "182C", "198C", "263G", "309.1C", "315.1C",
            "750G", "16129C", "16223C", "16278C", "16390C", "16519C",
        ],
        profile_b_variants=[
            "146C", "152C", "182C", "198C", "263G", "309.1C", "315.1C",
            "750G", "16129C", "16223C", "16278C", "16390C", "16519C",
        ],
    ),
    "COHORT_POINT_HETEROPLASMY_PAIR": MtDnaCaseworkCohort(
        cohort_id="COHORT_POINT_HETEROPLASMY_PAIR",
        name="Point Heteroplasmy Pair (16189Y vs 16189C)",
        relationship="MATERNAL_LINEAGE_MATCH",
        description="Questioned sample with point heteroplasmy 16189Y (C/T) vs reference homoplasmic 16189C.",
        expected_verdict="MATCH",
        expected_matches_k=0,
        database_size_n=48500,
        expected_min_lr=10000.0,
        profile_a_variants=["263G", "315.1C", "16189Y", "16519C"],
        profile_b_variants=["263G", "315.1C", "16189C", "16519C"],
    ),
    "COHORT_MATERNAL_DUO_UNOBSERVED": MtDnaCaseworkCohort(
        cohort_id="COHORT_MATERNAL_DUO_UNOBSERVED",
        name="Rare Unobserved Maternal Lineage Duo (k=0)",
        relationship="MATERNAL_LINEAGE_MATCH",
        description="Mother and daughter sharing a rare control region haplotype unobserved (k=0) in EMPOP.",
        expected_verdict="MATCH",
        expected_matches_k=0,
        database_size_n=48500,
        expected_min_lr=15000.0,
        profile_a_variants=["263G", "315.1C", "524.1AC", "16189C", "16278C", "16362C"],
        profile_b_variants=["263G", "315.1C", "524.1AC", "16189C", "16278C", "16362C"],
    ),
    "COHORT_UNRELATED_EXCLUSION": MtDnaCaseworkCohort(
        cohort_id="COHORT_UNRELATED_EXCLUSION",
        name="Unrelated Non-Kin Exclusion Pair",
        relationship="MATERNAL_LINEAGE_MATCH",
        description="Two unrelated individuals showing 11 homoplasmic point differences between H1 and L2a1.",
        expected_verdict="EXCLUSION",
        expected_matches_k=0,
        database_size_n=48500,
        expected_min_lr=0.0,
        profile_a_variants=["263G", "315.1C", "750G", "16519C"],
        profile_b_variants=[
            "146C", "152C", "182C", "198C", "263G", "309.1C", "315.1C",
            "750G", "16129C", "16223C", "16278C", "16390C", "16519C",
        ],
    ),
}


class MtDnaReferenceDatasets:
    """Service for accessing mtDNA reference databases and benchmarks."""

    @staticmethod
    def get_population_metadata(group: MtDnaPopulationGroup = MtDnaPopulationGroup.GLOBAL) -> MtDnaPopulationMetadata:
        return MTDNA_EMPOP_METADATA[group]

    @staticmethod
    def list_gold_standards() -> List[MtDnaGoldStandard]:
        return list(MTDNA_GOLD_STANDARDS.values())

    @staticmethod
    def list_casework_cohorts() -> List[MtDnaCaseworkCohort]:
        return list(MTDNA_CASEWORK_COHORTS.values())
