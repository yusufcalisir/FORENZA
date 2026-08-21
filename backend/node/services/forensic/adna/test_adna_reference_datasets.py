"""
Unit Test Suite for FORENZA Ancient DNA Reference Datasets & Casework Cohorts (Module 2.5).
Validates certified cohorts, Columbus series, Briggs series, and negative controls.
"""

import pytest

from node.services.forensic.adna.adna_reference_datasets import (
    AdnaReferenceDatasets,
    ADNA_CASEWORK_COHORTS,
)
from node.services.forensic.adna.adna_mathematical_formulation import (
    DegradationRiskTier,
)


class TestAdnaReferenceDatasets:
    """Verifies certified aDNA benchmark cohorts."""

    def test_five_cohorts_registered(self):
        assert len(ADNA_CASEWORK_COHORTS) == 5
        cohorts = AdnaReferenceDatasets.list_casework_cohorts()
        assert len(cohorts) == 5

    def test_columbus_benchmark_parameters(self):
        cohort = ADNA_CASEWORK_COHORTS["BENCHMARK_COLUMBUS_SKELETAL"]
        assert cohort.delta_0 == 0.38
        assert cohort.mean_fragment_length == 52.4
        assert cohort.expected_degradation_tier == DegradationRiskTier.SEVERE
        assert cohort.pre_break_purine_fraction == 0.72

    def test_briggs_ancient_benchmark(self):
        cohort = ADNA_CASEWORK_COHORTS["BENCHMARK_BRIGGS_ANCIENT"]
        assert cohort.delta_0 == 0.28
        assert cohort.decay_alpha == 0.12
        assert cohort.expected_degradation_tier == DegradationRiskTier.SEVERE

    def test_modern_negative_control(self):
        cohort = ADNA_CASEWORK_COHORTS["BENCHMARK_MODERN_CONTROL_NEGATIVE"]
        assert cohort.delta_0 <= 0.005
        assert cohort.mean_fragment_length >= 300.0
        assert cohort.expected_degradation_tier == DegradationRiskTier.PRISTINE
