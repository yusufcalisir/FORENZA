"""
Unit Tests for FORENZA X-STR Reference Datasets & Gold Standards (Module 2.2).
Validates population frequencies, multi-omic gold standards, and casework cohorts.
"""

import pytest

from node.services.forensic.xstr.xstr_reference_datasets import (
    XStrReferenceDatasets,
    XStrPopulationGroup,
    XSTR_POPULATION_METADATA,
    XSTR_POPULATION_FREQUENCIES,
    XSTR_GOLD_STANDARDS,
    XSTR_CASEWORK_COHORTS,
)
from node.services.forensic.xstr.xstr_mathematical_formulation import (
    XStrMathematicalFormulation,
    ARGUS_X12_MASTER_REGISTRY,
    KinshipRelationshipType,
)


class TestXStrPopulationDatasets:
    """Verifies population datasets and allele frequency distributions."""

    def test_three_population_metadata_partitions(self):
        assert len(XSTR_POPULATION_METADATA) == 3
        assert XStrPopulationGroup.EUROPEAN in XSTR_POPULATION_METADATA
        assert XStrPopulationGroup.EAST_ASIAN in XSTR_POPULATION_METADATA
        assert XStrPopulationGroup.AFRICAN_AMERICAN in XSTR_POPULATION_METADATA

    def test_frequencies_cover_all_12_loci(self):
        assert len(XSTR_POPULATION_FREQUENCIES) == 12
        for loc in ARGUS_X12_MASTER_REGISTRY:
            assert loc in XSTR_POPULATION_FREQUENCIES
            freqs = XSTR_POPULATION_FREQUENCIES[loc]
            assert len(freqs) >= 4
            # Sum of frequencies should be positive and close to 1
            sum_f = sum(freqs.values())
            assert 0.80 <= sum_f <= 1.05


class TestGoldStandardIndividuals:
    """Verifies certified multi-omic reference standards."""

    def test_all_four_standards_registered(self):
        assert len(XSTR_GOLD_STANDARDS) == 4
        assert "NA12878_CEU_FEMALE" in XSTR_GOLD_STANDARDS
        assert "NA19240_YRI_FEMALE" in XSTR_GOLD_STANDARDS
        assert "SRM_2391d_COMP_A_MALE" in XSTR_GOLD_STANDARDS
        assert "HG002_NA24385_MALE" in XSTR_GOLD_STANDARDS

    def test_female_standards_have_diploid_genotypes(self):
        female = XSTR_GOLD_STANDARDS["NA12878_CEU_FEMALE"]
        assert female.sex == "FEMALE"
        for loc, alleles in female.x_str_genotypes.items():
            assert len(alleles) in [1, 2]

    def test_male_standards_have_hemizygous_single_alleles(self):
        male = XSTR_GOLD_STANDARDS["SRM_2391d_COMP_A_MALE"]
        assert male.sex == "MALE"
        for loc, alleles in male.x_str_genotypes.items():
            assert len(alleles) == 1


class TestCaseworkCohorts:
    """Verifies casework benchmark cohorts execution."""

    def test_paternal_half_sisters_benchmark(self):
        cohort = XSTR_CASEWORK_COHORTS["VECTOR_P2_02_PATERNAL_HALF_SISTERS"]
        res = XStrMathematicalFormulation.evaluate_xstr_kinship(
            profile_a=cohort.profile_a,
            profile_b=cohort.profile_b,
            sex_a=cohort.sex_a,
            sex_b=cohort.sex_b,
            relationship=KinshipRelationshipType.PATERNAL_HALF_SISTERS,
            population_frequencies=XSTR_POPULATION_FREQUENCIES,
        )
        assert res.matching_loci_count == cohort.expected_matching_loci
        assert res.combined_ki >= cohort.expected_min_ki
        assert res.is_kinship_supported is True

    def test_father_daughter_duo_benchmark(self):
        cohort = XSTR_CASEWORK_COHORTS["COHORT_FATHER_DAUGHTER_DUO"]
        res = XStrMathematicalFormulation.evaluate_xstr_kinship(
            profile_a=cohort.profile_a,
            profile_b=cohort.profile_b,
            sex_a=cohort.sex_a,
            sex_b=cohort.sex_b,
            relationship=KinshipRelationshipType.FATHER_DAUGHTER,
            population_frequencies=XSTR_POPULATION_FREQUENCIES,
        )
        assert res.matching_loci_count == 12
        assert res.combined_ki >= cohort.expected_min_ki
