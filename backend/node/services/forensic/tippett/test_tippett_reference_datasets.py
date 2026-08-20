"""
FORENZA Forensic Evidence Operating System
Pillar 1 — Module 1.5: Tippett Plot ROC Calibration & Misleading Evidence Lab
Sub-Item 1.5.2: Reference Datasets Unit Test Suite
"""

import pytest
import numpy as np

try:
    from node.services.forensic.tippett.tippett_reference_datasets import (
        TippettReferenceDatasetRegistry,
        TippettBenchmarkCohort,
        NIST_1036_FREQUENCIES,
        NIST_SRM2391D_COMP_A_GENOTYPES,
    )
    from node.services.forensic.tippett.tippett_mathematical_formulation import (
        TippettMathematicalFormulation,
    )
except ImportError:
    from backend.node.services.forensic.tippett.tippett_reference_datasets import (
        TippettReferenceDatasetRegistry,
        TippettBenchmarkCohort,
        NIST_1036_FREQUENCIES,
        NIST_SRM2391D_COMP_A_GENOTYPES,
    )
    from backend.node.services.forensic.tippett.tippett_mathematical_formulation import (
        TippettMathematicalFormulation,
    )


# ===========================================================================
# 1. Test Suite: NIST 1036 Frequencies Simplex Invariant
# ===========================================================================

class TestNIST1036FrequencySimplex:
    """Verifies that all 24 loci frequency tables satisfy probability simplex sum-to-one."""

    def test_all_24_loci_present(self):
        assert len(NIST_1036_FREQUENCIES) == 24
        required_loci = [
            "D3S1358", "vWA", "FGA", "D8S1179", "D21S11", "D18S51", "D5S818", "D13S317",
            "D7S820", "TH01", "TPOX", "CSF1PO", "D1S1656", "D2S1338", "D10S1248",
            "D12S391", "D19S433", "D22S1045", "D2S441", "D6S1043", "SE33", "Penta_D",
            "Penta_E", "Amelogenin"
        ]
        for loc in required_loci:
            assert loc in NIST_1036_FREQUENCIES

    def test_frequency_sum_to_one_invariant(self):
        for loc, freqs in NIST_1036_FREQUENCIES.items():
            total = sum(freqs.values())
            assert abs(total - 1.0) < 1e-3, f"Locus {loc} frequency sum is {total} != 1.0"


# ===========================================================================
# 2. Test Suite: Pristine 24-Locus Cohort Simulation
# ===========================================================================

class TestPristineCohortGeneration:
    """Verifies pristine 24-locus benchmark simulation cohort."""

    def test_pristine_cohort_properties(self):
        cohort = TippettReferenceDatasetRegistry.generate_pristine_cohort(n_pairs=1000, seed=42)

        assert cohort.cohort_id == "COHORT_PRISTINE_24L"
        assert cohort.n_hp == 1000
        assert cohort.n_hd == 1000
        assert len(cohort.hp_log10_lrs) == 1000
        assert len(cohort.hd_log10_lrs) == 1000

        # Pristine Hp LRs are overwhelmingly positive (median > +20)
        assert cohort.median_hp > 20.0
        # Pristine Hd LRs are overwhelmingly negative (median < -20)
        assert cohort.median_hd < -20.0

        # Perfect separation
        assert cohort.auc >= 0.999
        assert cohort.cllr < 0.01

    def test_pristine_cohort_reproducibility(self):
        c1 = TippettReferenceDatasetRegistry.generate_pristine_cohort(n_pairs=100, seed=123)
        c2 = TippettReferenceDatasetRegistry.generate_pristine_cohort(n_pairs=100, seed=123)

        assert c1.hp_log10_lrs == c2.hp_log10_lrs
        assert c1.hd_log10_lrs == c2.hd_log10_lrs
        assert c1.median_hp == c2.median_hp


# ===========================================================================
# 3. Test Suite: Low-Template Degraded Cohort Simulation
# ===========================================================================

class TestLTDNADegradedCohort:
    """Verifies low-template degraded touch DNA cohort simulation."""

    def test_ltdna_degraded_cohort_shift(self):
        pristine = TippettReferenceDatasetRegistry.generate_pristine_cohort(n_pairs=500, seed=42)
        degraded = TippettReferenceDatasetRegistry.generate_ltdna_degraded_cohort(
            n_pairs=500, p_dropout=0.40, seed=42
        )

        assert degraded.cohort_id == "COHORT_LTDNA_DEGRADED"
        # Degraded median Hp is shifted leftwards due to missing alleles
        assert degraded.median_hp < pristine.median_hp
        # But still predominantly positive (supporting true donor)
        assert degraded.median_hp > 5.0
        # High discrimination maintained
        assert degraded.auc >= 0.990


# ===========================================================================
# 4. Test Suite: NIST SRM 2391d Component A Evaluation
# ===========================================================================

class TestNISTSRM2391dEvaluation:
    """Verifies NIST SRM 2391d Component A true match vs non-donor screening."""

    def test_srm2391d_benchmark_cohort(self):
        cohort = TippettReferenceDatasetRegistry.get_nist_srm2391d_evaluation(
            n_non_donors=1000, seed=42
        )

        assert cohort.cohort_id == "COHORT_NIST_SRM2391D_COMP_A"
        assert cohort.n_hp == 1000
        assert cohort.n_hd == 1000

        # Component A true match log10 LR is ~ +27.0
        assert cohort.median_hp > 25.0
        # Non-donor LRs are negative
        assert cohort.median_hd < -20.0
        # Zero false positives
        res = TippettMathematicalFormulation.evaluate_misleading_evidence_rate(
            cohort.hd_log10_lrs, threshold_log10=6.0
        )
        assert res["count_exceeding"] == 0
        assert res["bound_satisfied"] is True
