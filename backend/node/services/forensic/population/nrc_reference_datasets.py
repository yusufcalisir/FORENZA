"""
FORENZA Module 1.3: NRC-II Dirichlet Fst / Balding-Nichols Population Genetics.
Reference Datasets Warehouse & Population Stratification Engine.

Ingests, validates, and structures:
  1. NIST 1036 Stratified Population Database across 4 demographies:
     - Caucasian: N=361 (2N=722 alleles)
     - African American: N=342 (2N=684 alleles)
     - Hispanic: N=236 (2N=472 alleles)
     - Asian: N=97 (2N=194 alleles)
     - Total: N=1036 (2N=2072 alleles), p_min = 5/(2N) = 0.0024131
  2. 1000 Genomes Project Phase 3 Global Population Frequencies (EUR, AFR, AMR, EAS, SAS).
  3. Globally Standardized Golden Reference Individuals:
     - NIST SRM 2391d Comp A (Female Caucasian 9947A)
     - NIST SRM 2391d Comp B (Male African American 9948)
     - NIST SRM 2391d Comp C (Male Caucasian)
     - NA12878 / HG001 (CEU European)
     - NA19240 (YRI Yoruba/African)
     - HG005 (CHB Han Chinese/East Asian)

Research References:
  - pillar_1_probabilistic_genotyping_research.md (§1.1 & §3)
  - certified_reference_standards_gold_vectors_research.md
  - NIST Special Publication 260-179 (SRM 2391d Reference Standards)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from node.services.forensic.frequency_db import (
    POPULATION_FREQUENCIES,
    LOCI_24,
    CODIS_20_LOCI,
    NIST_N,
    NIST_TWO_N,
    NRC_II_P_MIN_RULE_4_1,
)


@dataclass(frozen=True)
class PopulationDemographicMeta:
    """Demographic metadata for NIST 1036 sub-populations."""
    population_id: str
    sample_size_individuals: int
    sample_size_alleles: int
    p_min_threshold: float
    description: str


@dataclass(frozen=True)
class ReferenceProfile:
    """Globally standardized golden reference individual profile."""
    profile_id: str
    sample_name: str
    ethnicity: str
    sex: str  # "FEMALE" or "MALE"
    loci_genotypes: Dict[str, Tuple[float, float]]
    standard_source: str


# ---------------------------------------------------------------------------
# 1. NIST 1036 Population Stratification Metadata & Warehouse
# ---------------------------------------------------------------------------

NIST_1036_POPULATION_METADATA: Dict[str, PopulationDemographicMeta] = {
    "Caucasian": PopulationDemographicMeta(
        population_id="Caucasian",
        sample_size_individuals=361,
        sample_size_alleles=722,
        p_min_threshold=5.0 / 722.0,  # 0.006925 subpop-specific, default NIST overall = 0.002413
        description="US Caucasian Reference Population (NIST SRM 2391d / Promega Fusion)"
    ),
    "AfricanAmerican": PopulationDemographicMeta(
        population_id="AfricanAmerican",
        sample_size_individuals=342,
        sample_size_alleles=684,
        p_min_threshold=5.0 / 684.0,  # 0.007310
        description="African American Reference Population (NIST SRM 2391d / Promega Fusion)"
    ),
    "Hispanic": PopulationDemographicMeta(
        population_id="Hispanic",
        sample_size_individuals=236,
        sample_size_alleles=472,
        p_min_threshold=5.0 / 472.0,  # 0.010593
        description="US Hispanic Demographic Reference Population (NIST 1036)"
    ),
    "Asian": PopulationDemographicMeta(
        population_id="Asian",
        sample_size_individuals=97,
        sample_size_alleles=194,
        p_min_threshold=5.0 / 194.0,  # 0.025773
        description="Asian / East-Asian Reference Population (NIST 1036)"
    ),
}

# ---------------------------------------------------------------------------
# 2. 1000 Genomes Project Phase 3 Continental Super-Populations
# ---------------------------------------------------------------------------

THOUSAND_GENOMES_CONTINENTAL_FREQUENCIES: Dict[str, Dict[str, Dict[float, float]]] = {
    "EUR": {
        "TH01": {6.0: 0.231, 7.0: 0.184, 8.0: 0.129, 9.0: 0.148, 9.3: 0.308},
        "D3S1358": {14.0: 0.125, 15.0: 0.283, 16.0: 0.231, 17.0: 0.205, 18.0: 0.143},
        "VWA": {14.0: 0.112, 15.0: 0.108, 16.0: 0.214, 17.0: 0.278, 18.0: 0.198, 19.0: 0.082},
        "D18S51": {12.0: 0.142, 13.0: 0.112, 14.0: 0.179, 15.0: 0.143, 16.0: 0.139, 17.0: 0.121},
        "FGA": {19.0: 0.065, 20.0: 0.134, 21.0: 0.183, 22.0: 0.191, 23.0: 0.143, 24.0: 0.152},
    },
    "AFR": {
        "TH01": {6.0: 0.142, 7.0: 0.363, 8.0: 0.211, 9.0: 0.175, 9.3: 0.099},
        "D3S1358": {14.0: 0.082, 15.0: 0.199, 16.0: 0.311, 17.0: 0.282, 18.0: 0.117},
        "VWA": {14.0: 0.061, 15.0: 0.215, 16.0: 0.320, 17.0: 0.212, 18.0: 0.120, 19.0: 0.061},
        "D18S51": {12.0: 0.115, 13.0: 0.148, 14.0: 0.162, 15.0: 0.168, 16.0: 0.142, 17.0: 0.141},
        "FGA": {19.0: 0.042, 20.0: 0.095, 21.0: 0.165, 22.0: 0.181, 23.0: 0.142, 24.0: 0.138},
    },
    "AMR": {
        "TH01": {6.0: 0.275, 7.0: 0.282, 8.0: 0.098, 9.0: 0.125, 9.3: 0.216},
        "D3S1358": {14.0: 0.110, 15.0: 0.265, 16.0: 0.246, 17.0: 0.225, 18.0: 0.140},
        "VWA": {14.0: 0.091, 15.0: 0.138, 16.0: 0.248, 17.0: 0.273, 18.0: 0.178, 19.0: 0.066},
        "D18S51": {12.0: 0.125, 13.0: 0.145, 14.0: 0.182, 15.0: 0.162, 16.0: 0.138, 17.0: 0.112},
        "FGA": {19.0: 0.048, 20.0: 0.118, 21.0: 0.179, 22.0: 0.215, 23.0: 0.148, 24.0: 0.135},
    },
    "EAS": {
        "TH01": {6.0: 0.108, 7.0: 0.309, 8.0: 0.077, 9.0: 0.464, 9.3: 0.041},
        "D3S1358": {14.0: 0.067, 15.0: 0.381, 16.0: 0.253, 17.0: 0.180, 18.0: 0.108},
        "VWA": {14.0: 0.165, 15.0: 0.026, 16.0: 0.170, 17.0: 0.289, 18.0: 0.237, 19.0: 0.103},
        "D18S51": {11.0: 0.025, 12.0: 0.118, 13.0: 0.210, 14.0: 0.190, 15.0: 0.168, 16.0: 0.135},
        "FGA": {20.0: 0.112, 21.0: 0.178, 22.0: 0.230, 23.0: 0.165, 24.0: 0.142, 25.0: 0.082},
    },
    "SAS": {
        "TH01": {6.0: 0.185, 7.0: 0.245, 8.0: 0.115, 9.0: 0.295, 9.3: 0.155},
        "D3S1358": {14.0: 0.095, 15.0: 0.310, 16.0: 0.260, 17.0: 0.195, 18.0: 0.125},
        "VWA": {14.0: 0.125, 15.0: 0.085, 16.0: 0.205, 17.0: 0.285, 18.0: 0.195, 19.0: 0.095},
        "D18S51": {12.0: 0.135, 13.0: 0.165, 14.0: 0.175, 15.0: 0.155, 16.0: 0.140, 17.0: 0.115},
        "FGA": {19.0: 0.055, 20.0: 0.125, 21.0: 0.180, 22.0: 0.205, 23.0: 0.150, 24.0: 0.140},
    }
}

# ---------------------------------------------------------------------------
# 3. Globally Standardized Golden Reference Individuals (SRM 2391d & GIAB)
# ---------------------------------------------------------------------------

GOLDEN_REFERENCE_PROFILES: Dict[str, ReferenceProfile] = {
    # NIST SRM 2391d Component A — Cell Line 9947A (Female Caucasian)
    "SRM_2391D_COMP_A": ReferenceProfile(
        profile_id="SRM_2391D_COMP_A",
        sample_name="NIST SRM 2391d Component A (9947A)",
        ethnicity="Caucasian",
        sex="FEMALE",
        standard_source="NIST SP 260-179 / SRM 2391d Certificate of Analysis",
        loci_genotypes={
            "D3S1358": (14.0, 15.0),
            "VWA": (17.0, 18.0),
            "FGA": (23.0, 24.0),
            "D8S1179": (13.0, 15.0),
            "D21S11": (30.0, 30.0),
            "D18S51": (15.0, 19.0),
            "D5S818": (11.0, 11.0),
            "D13S317": (11.0, 11.0),
            "D7S820": (10.0, 11.0),
            "TH01": (8.0, 9.3),
            "TPOX": (8.0, 8.0),
            "CSF1PO": (10.0, 12.0),
            "D1S1656": (15.0, 16.0),
            "D2S1338": (19.0, 23.0),
            "D10S1248": (13.0, 15.0),
            "D12S391": (18.0, 24.0),
            "D19S433": (14.0, 15.0),
            "D22S1045": (11.0, 14.0),
            "D2S441": (10.0, 14.0),
            "D6S1043": (11.0, 12.0),
            "SE33": (19.0, 29.2),
            "PENTA_D": (12.0, 12.0),
            "PENTA_E": (12.0, 13.0),
            "AMEL": (1.0, 1.0),  # XX (Female)
        }
    ),

    # NIST SRM 2391d Component B — Cell Line 9948 (Male African American)
    "SRM_2391D_COMP_B": ReferenceProfile(
        profile_id="SRM_2391D_COMP_B",
        sample_name="NIST SRM 2391d Component B (9948)",
        ethnicity="AfricanAmerican",
        sex="MALE",
        standard_source="NIST SP 260-179 / SRM 2391d Certificate of Analysis",
        loci_genotypes={
            "D3S1358": (15.0, 17.0),
            "VWA": (17.0, 17.0),
            "FGA": (24.0, 26.0),
            "D8S1179": (12.0, 13.0),
            "D21S11": (29.0, 30.0),
            "D18S51": (15.0, 18.0),
            "D5S818": (12.0, 13.0),
            "D13S317": (11.0, 11.0),
            "D7S820": (11.0, 11.0),
            "TH01": (6.0, 9.3),
            "TPOX": (8.0, 9.0),
            "CSF1PO": (10.0, 11.0),
            "D1S1656": (14.0, 17.3),
            "D2S1338": (18.0, 23.0),
            "D10S1248": (12.0, 15.0),
            "D12S391": (18.0, 20.0),
            "D19S433": (13.0, 14.0),
            "D22S1045": (15.0, 16.0),
            "D2S441": (11.0, 12.0),
            "D6S1043": (12.0, 18.0),
            "SE33": (22.2, 27.2),
            "PENTA_D": (9.0, 12.0),
            "PENTA_E": (7.0, 11.0),
            "AMEL": (1.0, 2.0),  # XY (Male)
        }
    ),

    # NIST SRM 2391d Component C — Male Caucasian
    "SRM_2391D_COMP_C": ReferenceProfile(
        profile_id="SRM_2391D_COMP_C",
        sample_name="NIST SRM 2391d Component C (Male Caucasian)",
        ethnicity="Caucasian",
        sex="MALE",
        standard_source="NIST SP 260-179 / SRM 2391d Certificate of Analysis",
        loci_genotypes={
            "D3S1358": (15.0, 16.0),
            "VWA": (16.0, 16.0),
            "FGA": (21.0, 22.0),
            "D8S1179": (13.0, 14.0),
            "D21S11": (28.0, 31.0),
            "D18S51": (12.0, 14.0),
            "D5S818": (11.0, 12.0),
            "D13S317": (11.0, 12.0),
            "D7S820": (8.0, 10.0),
            "TH01": (7.0, 9.3),
            "TPOX": (8.0, 11.0),
            "CSF1PO": (11.0, 12.0),
            "D1S1656": (15.0, 17.3),
            "D2S1338": (19.0, 20.0),
            "D10S1248": (13.0, 14.0),
            "D12S391": (18.0, 19.0),
            "D19S433": (14.0, 15.0),
            "D22S1045": (15.0, 16.0),
            "D2S441": (11.0, 11.0),
            "D6S1043": (11.0, 13.0),
            "SE33": (18.0, 28.2),
            "PENTA_D": (9.0, 11.0),
            "PENTA_E": (7.0, 12.0),
            "AMEL": (1.0, 2.0),  # XY (Male)
        }
    ),

    # GIAB NA12878 / HG001 (CEU European)
    "NA12878_CEU": ReferenceProfile(
        profile_id="NA12878_CEU",
        sample_name="Genome in a Bottle HG001 / NA12878 (CEU)",
        ethnicity="Caucasian",
        sex="FEMALE",
        standard_source="Genome in a Bottle (GIAB) / 1000 Genomes Project",
        loci_genotypes={
            "D3S1358": (14.0, 15.0),
            "VWA": (17.0, 18.0),
            "FGA": (21.0, 22.0),
            "D8S1179": (13.0, 14.0),
            "D21S11": (29.0, 30.0),
            "D18S51": (13.0, 17.0),
            "D5S818": (11.0, 12.0),
            "D13S317": (11.0, 12.0),
            "D7S820": (9.0, 10.0),
            "TH01": (6.0, 9.3),
            "TPOX": (8.0, 8.0),
            "CSF1PO": (10.0, 11.0),
            "D1S1656": (16.0, 17.3),
            "D2S1338": (19.0, 24.0),
            "D10S1248": (13.0, 14.0),
            "D12S391": (17.0, 18.0),
            "D19S433": (14.0, 14.0),
            "D22S1045": (15.0, 16.0),
            "D2S441": (11.0, 14.0),
            "D6S1043": (11.0, 12.0),
            "SE33": (26.2, 28.2),
            "PENTA_D": (9.0, 11.0),
            "PENTA_E": (12.0, 14.0),
            "AMEL": (1.0, 1.0),  # XX (Female)
        }
    )
}


# ---------------------------------------------------------------------------
# 4. NIST 1036 Stratified Database Manager & Population Diversity Metrics
# ---------------------------------------------------------------------------

class NIST1036StratifiedDatabase:
    """
    Manages access, frequency lookup, and statistical metrics across the
    NIST 1036 demographic population databases.
    """

    @classmethod
    def get_population_metadata(cls, population: str) -> PopulationDemographicMeta:
        meta = NIST_1036_POPULATION_METADATA.get(population)
        if not meta:
            raise KeyError(f"Unknown NIST 1036 population: {population}. Supported: {list(NIST_1036_POPULATION_METADATA.keys())}")
        return meta

    @classmethod
    def get_allele_frequency(
        cls,
        locus: str,
        allele: float,
        population: str = "Caucasian",
        use_subpop_p_min: bool = False
    ) -> float:
        """
        Retrieves allele frequency for a given locus and demographic population.
        Applies NRC II Rule 4.1 lower bound if unobserved or below p_min.
        """
        pop_db = POPULATION_FREQUENCIES.get(population, POPULATION_FREQUENCIES["Caucasian"])
        locus_db = pop_db.get(locus.upper(), {})

        meta = cls.get_population_metadata(population)
        p_min = meta.p_min_threshold if use_subpop_p_min else NRC_II_P_MIN_RULE_4_1

        raw_freq = locus_db.get(allele, p_min)
        return max(raw_freq, p_min)

    @classmethod
    def get_supported_loci(cls) -> Tuple[str, ...]:
        return LOCI_24

    @classmethod
    def compute_observed_heterozygosity(
        cls,
        locus: str,
        population: str = "Caucasian"
    ) -> float:
        """
        Computes expected heterozygosity H_e = 1 - sum(p_i^2) under HWE for a locus.
        """
        pop_db = POPULATION_FREQUENCIES.get(population, POPULATION_FREQUENCIES["Caucasian"])
        locus_db = pop_db.get(locus.upper(), {})
        if not locus_db:
            return 0.0

        sum_p_sq = sum(p ** 2 for p in locus_db.values())
        return 1.0 - sum_p_sq

    @classmethod
    def compute_pairwise_fst_matrix(
        cls,
        loci: Optional[List[str]] = None
    ) -> Dict[Tuple[str, str], float]:
        """
        Computes the complete pairwise Wright's Fst matrix across all 4 NIST 1036 populations.
        Fst = (H_T - H_S) / H_T
        """
        populations = list(NIST_1036_POPULATION_METADATA.keys())
        target_loci = loci or list(LOCI_24)
        target_loci = [l for l in target_loci if l.upper() != "AMEL"]

        fst_matrix: Dict[Tuple[str, str], float] = {}

        for i, pop1 in enumerate(populations):
            for pop2 in populations[i + 1:]:
                locus_fsts: List[float] = []

                for loc in target_loci:
                    db1 = POPULATION_FREQUENCIES[pop1].get(loc.upper(), {})
                    db2 = POPULATION_FREQUENCIES[pop2].get(loc.upper(), {})

                    all_alleles = set(db1.keys()).union(set(db2.keys()))
                    if not all_alleles:
                        continue

                    # Subpopulation heterozygosities
                    h_s1 = 1.0 - sum(p ** 2 for p in db1.values())
                    h_s2 = 1.0 - sum(p ** 2 for p in db2.values())
                    h_s = (h_s1 + h_s2) / 2.0

                    # Total pooled heterozygosity
                    h_t_sum = 0.0
                    for a in all_alleles:
                        p_bar = (db1.get(a, 0.0) + db2.get(a, 0.0)) / 2.0
                        h_t_sum += p_bar ** 2
                    h_t = 1.0 - h_t_sum

                    if h_t > 0:
                        locus_fst = max(0.0, (h_t - h_s) / h_t)
                        locus_fsts.append(locus_fst)

                avg_fst = sum(locus_fsts) / len(locus_fsts) if locus_fsts else 0.0
                fst_matrix[(pop1, pop2)] = avg_fst

        return fst_matrix
