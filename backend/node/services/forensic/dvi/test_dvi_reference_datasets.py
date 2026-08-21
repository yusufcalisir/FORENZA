"""
Unit Test Suite for FORENZA DVI Reference Datasets & Casework Cohorts (Module 2.4).
Validates pedigree templates, certified standards, and casework cohorts.
"""

import pytest

from node.services.forensic.dvi.dvi_reference_datasets import (
    DviReferenceDatasets,
    DviPedigreeTemplateType,
    DVI_PEDIGREE_TEMPLATES,
    DVI_CASEWORK_COHORTS,
)
from node.services.forensic.dvi.dvi_mathematical_formulation import (
    DviMathematicalFormulation,
)


class TestPedigreeTemplates:
    """Verifies Interpol DVI standard pedigree templates."""

    def test_all_four_templates_registered(self):
        assert len(DVI_PEDIGREE_TEMPLATES) == 4
        assert DviPedigreeTemplateType.DIRECT_AM in DVI_PEDIGREE_TEMPLATES
        assert DviPedigreeTemplateType.TRIO_PARENTS in DVI_PEDIGREE_TEMPLATES
        assert DviPedigreeTemplateType.DEFICIENCY_DUO in DVI_PEDIGREE_TEMPLATES
        assert DviPedigreeTemplateType.FULL_SIBLINGS in DVI_PEDIGREE_TEMPLATES


class TestCaseworkCohorts:
    """Verifies certified casework cohorts."""

    def test_vector_p2_03_benchmark(self):
        cohort = DVI_CASEWORK_COHORTS["VECTOR_P2_03_DEGRADED_SKELETAL"]
        joint_lr, log10_joint = DviMathematicalFormulation.compute_multi_omic_joint_lr(
            autosomal_lr=cohort.autosomal_lr,
            ystr_p_upper=cohort.ystr_p_upper,
            mtdna_p_upper=cohort.mtdna_p_upper,
            has_ystr=cohort.has_ystr,
            has_mtdna=cohort.has_mtdna,
        )
        assert abs(joint_lr - cohort.expected_joint_lr) < 1e5
        assert abs(log10_joint - cohort.expected_log10_lr) < 1e-4

    def test_direct_am_match_cohort(self):
        cohort = DVI_CASEWORK_COHORTS["BENCHMARK_DIRECT_AM_MATCH"]
        assert cohort.expected_joint_lr > 1.0e15
        assert cohort.expected_tier == "DEFINITIVE_IDENTIFICATION"

    def test_unrelated_exclusion_cohort(self):
        cohort = DVI_CASEWORK_COHORTS["BENCHMARK_UNRELATED_EXCLUSION"]
        assert cohort.expected_joint_lr < 1.0e-6
        assert cohort.expected_tier == "EXCLUSION"
