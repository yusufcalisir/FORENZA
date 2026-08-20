"""
Unit Test Suite for Y-STR 27-Locus (Yfiler Plus) Reference Datasets & Casework Cohorts.
Sub-Item 2.1.2: Reference Datasets

Tests:
  - YHRD Release 68 global and regional population partitions
  - Certified Gold Standard Reference Individuals (SRM 2391d A, HG002, NA18507)
  - Female negative control validation (NA12878, NA19240)
  - Casework benchmark cohorts for paternal lineage evaluation
  - API query functions
"""

import pytest

from node.services.forensic.ystr.ystr_mathematical_formulation import (
    YStrMathematicalFormulation,
)
from node.services.forensic.ystr.ystr_reference_datasets import (
    YhrdMetapopulation,
    YHRD_GLOBAL_METAPOPULATIONS,
    GOLD_STANDARD_INDIVIDUALS,
    CASEWORK_BENCHMARK_COHORTS,
    YStrReferenceDatasets,
)


class TestYhrdMetapopulations:
    """Verifies YHRD Release 68 database partitions and parameters."""

    def test_six_metapopulation_partitions_present(self):
        partitions = YStrReferenceDatasets.list_population_partitions()
        assert len(partitions) == 6
        expected_codes = {
            YhrdMetapopulation.GLOBAL,
            YhrdMetapopulation.WEST_EURASIAN,
            YhrdMetapopulation.EAST_ASIAN,
            YhrdMetapopulation.SOUTH_ASIAN,
            YhrdMetapopulation.ADMIXED_AMERICAN,
            YhrdMetapopulation.SUB_SAHARAN_AFRICAN,
        }
        actual_codes = {p.code for p in partitions}
        assert actual_codes == expected_codes

    def test_global_database_size_385000(self):
        glob = YStrReferenceDatasets.get_population_partition(YhrdMetapopulation.GLOBAL)
        assert glob.database_size_n == 385000
        assert glob.default_theta == 0.03
        assert "R1b" in glob.primary_modal_haplogroups

    def test_regional_database_sizes_and_theta(self):
        eur = YStrReferenceDatasets.get_population_partition(YhrdMetapopulation.WEST_EURASIAN)
        assert eur.database_size_n == 142000
        assert eur.default_theta == 0.01

        eas = YStrReferenceDatasets.get_population_partition(YhrdMetapopulation.EAST_ASIAN)
        assert eas.database_size_n == 118000
        assert eas.default_theta == 0.02

        sas = YStrReferenceDatasets.get_population_partition(YhrdMetapopulation.SOUTH_ASIAN)
        assert sas.database_size_n == 45000
        assert sas.default_theta == 0.03

        afr = YStrReferenceDatasets.get_population_partition(YhrdMetapopulation.SUB_SAHARAN_AFRICAN)
        assert afr.database_size_n == 38000
        assert afr.default_theta == 0.02


class TestGoldStandardReferenceIndividuals:
    """Verifies multi-omic gold standard reference individuals."""

    def test_all_five_reference_individuals_registered(self):
        standards = YStrReferenceDatasets.list_gold_standards()
        assert len(standards) == 5
        sample_ids = {s.sample_id for s in standards}
        assert "SRM_2391d_COMP_A" in sample_ids
        assert "HG002_NA24385" in sample_ids
        assert "NA18507_HG005" in sample_ids
        assert "NA12878_HG001_FEMALE" in sample_ids
        assert "NA19240_YRI_FEMALE" in sample_ids

    def test_srm2391d_male_canonical_profile(self):
        srm = YStrReferenceDatasets.get_gold_standard("SRM_2391d_COMP_A")
        assert srm.sex == "MALE"
        assert srm.certified_haplogroup == "R1b1a1b"
        assert srm.y_str_haplotype["DYS19"] == 14
        assert srm.y_str_haplotype["DYS385a/b"] == [11, 14]
        assert srm.y_str_haplotype["DYF387S1a/b"] == [35, 37]
        assert srm.y_str_haplotype["DYS518"] == 38

    def test_hg002_ashkenazi_male_profile(self):
        hg002 = YStrReferenceDatasets.get_gold_standard("HG002_NA24385")
        assert hg002.sex == "MALE"
        assert hg002.certified_haplogroup == "J2a1a1"
        assert hg002.y_str_haplotype["DYS19"] == 15
        assert hg002.y_str_haplotype["DYS393"] == 12

    def test_na18507_han_chinese_male_profile(self):
        na18507 = YStrReferenceDatasets.get_gold_standard("NA18507_HG005")
        assert na18507.sex == "MALE"
        assert na18507.certified_haplogroup == "O2a2b1"
        assert na18507.y_str_haplotype["DYS389I"] == 14
        assert na18507.y_str_haplotype["DYS389II"] == 31

    def test_female_controls_have_null_profiles(self):
        na12878 = YStrReferenceDatasets.get_gold_standard("NA12878_HG001_FEMALE")
        na19240 = YStrReferenceDatasets.get_gold_standard("NA19240_YRI_FEMALE")
        assert na12878.sex == "FEMALE"
        assert len(na12878.y_str_haplotype) == 0
        assert na19240.sex == "FEMALE"
        assert len(na19240.y_str_haplotype) == 0


class TestCaseworkBenchmarkCohorts:
    """Verifies empirical behavior on certified casework benchmark cohorts."""

    def test_father_son_exact_transmission(self):
        cohort = YStrReferenceDatasets.get_casework_cohort("COHORT_PATERNAL_DUO_FATHER_SON")
        res = YStrMathematicalFormulation.evaluate_paternal_kinship_likelihood(
            profile_a=cohort.profile_a,
            profile_b=cohort.profile_b,
            meioses_m=cohort.meioses_m,
            database_size_n=385000,
        )
        assert res.matching_loci_count == cohort.expected_matching_loci
        assert res.mutated_loci_count == cohort.expected_mutation_count
        assert res.is_lineage_excluded is False
        assert res.paternal_lr >= cohort.expected_min_lr
        assert "Extremely Strong Support" in res.verbal_predicate_en

    def test_father_son_with_rm_mutation(self):
        cohort = YStrReferenceDatasets.get_casework_cohort("COHORT_PATERNAL_DUO_WITH_RM_MUTATION")
        res = YStrMathematicalFormulation.evaluate_paternal_kinship_likelihood(
            profile_a=cohort.profile_a,
            profile_b=cohort.profile_b,
            meioses_m=cohort.meioses_m,
            database_size_n=385000,
        )
        assert res.matching_loci_count == cohort.expected_matching_loci
        assert res.mutated_loci_count == cohort.expected_mutation_count
        assert res.rm_mutations_count == 1
        assert res.is_lineage_excluded is False
        assert res.paternal_lr >= cohort.expected_min_lr
        assert "Rapid Germline Mutation" in res.verbal_predicate_en

    def test_grandfather_grandson_two_meioses(self):
        cohort = YStrReferenceDatasets.get_casework_cohort("COHORT_PATERNAL_TRIO_GRANDFATHER_GRANDSON")
        res = YStrMathematicalFormulation.evaluate_paternal_kinship_likelihood(
            profile_a=cohort.profile_a,
            profile_b=cohort.profile_b,
            meioses_m=cohort.meioses_m,
            database_size_n=385000,
        )
        assert res.matching_loci_count == cohort.expected_matching_loci
        assert res.mutated_loci_count == cohort.expected_mutation_count
        assert res.is_lineage_excluded is False
        assert res.paternal_lr >= cohort.expected_min_lr

    def test_unrelated_males_definitive_exclusion(self):
        cohort = YStrReferenceDatasets.get_casework_cohort("COHORT_UNRELATED_MALES")
        res = YStrMathematicalFormulation.evaluate_paternal_kinship_likelihood(
            profile_a=cohort.profile_a,
            profile_b=cohort.profile_b,
            meioses_m=cohort.meioses_m,
            database_size_n=385000,
        )
        assert res.is_lineage_excluded is True
        assert res.paternal_lr == 0.0
        assert "Definitive Exclusion" in res.verbal_predicate_en
