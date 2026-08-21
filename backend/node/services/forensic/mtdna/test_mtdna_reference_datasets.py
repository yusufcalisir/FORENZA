"""
Unit Test Suite for FORENZA mtDNA Reference Datasets & Gold Standards (Module 2.3).
Validates EMPOP metapopulation metadata, certified standards, and casework cohorts.
"""

import pytest

from node.services.forensic.mtdna.mtdna_reference_datasets import (
    MtDnaReferenceDatasets,
    MtDnaPopulationGroup,
    MTDNA_EMPOP_METADATA,
    MTDNA_GOLD_STANDARDS,
    MTDNA_CASEWORK_COHORTS,
)
from node.services.forensic.mtdna.mtdna_mathematical_formulation import (
    MtDnaMathematicalFormulation,
)


class TestEMPOPMetadata:
    """Verifies EMPOP Release 15 population partitions."""

    def test_all_six_metapopulations_registered(self):
        assert len(MTDNA_EMPOP_METADATA) == 6
        assert MtDnaPopulationGroup.GLOBAL in MTDNA_EMPOP_METADATA
        assert MtDnaPopulationGroup.WEST_EURASIAN in MTDNA_EMPOP_METADATA
        assert MtDnaPopulationGroup.EAST_ASIAN in MTDNA_EMPOP_METADATA
        assert MtDnaPopulationGroup.AFRICAN in MTDNA_EMPOP_METADATA

    def test_global_empop_sample_size_is_48500(self):
        meta = MTDNA_EMPOP_METADATA[MtDnaPopulationGroup.GLOBAL]
        assert meta.sample_size_n == 48500


class TestGoldStandards:
    """Verifies certified multi-omic reference standards."""

    def test_five_gold_standards_registered(self):
        assert len(MTDNA_GOLD_STANDARDS) == 5
        assert "NA12878_CEU_FEMALE" in MTDNA_GOLD_STANDARDS
        assert "NA19240_YRI_FEMALE" in MTDNA_GOLD_STANDARDS
        assert "HG002_NA24385_MALE" in MTDNA_GOLD_STANDARDS
        assert "NA18507_HG005_MALE" in MTDNA_GOLD_STANDARDS
        assert "NIST_SRM_2391d_COMP_A" in MTDNA_GOLD_STANDARDS

    def test_na12878_haplogroup_h1(self):
        std = MTDNA_GOLD_STANDARDS["NA12878_CEU_FEMALE"]
        assert std.haplogroup == "H1"
        assert "263G" in std.variants
        assert "315.1C" in std.variants


class TestCaseworkCohorts:
    """Verifies benchmark casework cohorts."""

    def test_lineage_a_european_benchmark(self):
        cohort = MTDNA_CASEWORK_COHORTS["BENCHMARK_LINEAGE_A_EUR"]
        vars_a = [MtDnaMathematicalFormulation.parse_variant_string(s) for s in cohort.profile_a_variants]
        vars_b = [MtDnaMathematicalFormulation.parse_variant_string(s) for s in cohort.profile_b_variants]
        res = MtDnaMathematicalFormulation.evaluate_pairwise_lineage(
            variants_a=vars_a,
            variants_b=vars_b,
            database_size_n=cohort.database_size_n,
            observed_database_matches_k=cohort.expected_matches_k,
        )
        assert res.verdict == cohort.expected_verdict
        assert res.maternal_lr >= cohort.expected_min_lr

    def test_unrelated_exclusion_cohort(self):
        cohort = MTDNA_CASEWORK_COHORTS["COHORT_UNRELATED_EXCLUSION"]
        vars_a = [MtDnaMathematicalFormulation.parse_variant_string(s) for s in cohort.profile_a_variants]
        vars_b = [MtDnaMathematicalFormulation.parse_variant_string(s) for s in cohort.profile_b_variants]
        res = MtDnaMathematicalFormulation.evaluate_pairwise_lineage(
            variants_a=vars_a,
            variants_b=vars_b,
            database_size_n=cohort.database_size_n,
            observed_database_matches_k=cohort.expected_matches_k,
        )
        assert res.verdict == "EXCLUSION"
        assert res.maternal_lr == 0.0
        assert res.homoplasmic_differences_count >= 2
