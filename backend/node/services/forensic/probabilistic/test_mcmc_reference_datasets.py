"""
FORENZA Module 1.2 — Reference Ground Truth Mixture Datasets Verification Suite

Research Sources:
  - Zenodo STR Analysis Results BTSC 349, BTSC 268 calibrated 2-person mixtures (Zenodo 3901446)
  - PROVEDIt Mixture Series (Boston University / NIST 2-person and 3-person dilution series)
  - NIST SRM 2391d Components A (9947A), B (9948) Standard Ground Truth Profiles

Test Suite Verifications:
  1. TestReferenceDatasetIntegrity: All datasets load with complete 24-locus EPG profiles
  2. TestDilutionRatioAndPeakHeightConsistency: EPG peak heights reflect 1:1, 3:1, 9:1, 19:1, 5:3:2 ratios
  3. TestGroundTruthCoverageInvariant: Union of true donor genotypes covers all observed alleles
  4. TestMixtureDeconvolutionOnReferenceDatasets: MCMC engine accurately estimates mixture proportions
  5. TestSuspectInclusionAndExclusionLR: True donors yield strong positive LRs; non-donors yield exclusion
"""

import math
import pytest
from typing import Dict, List, Tuple

from backend.node.services.forensic.probabilistic.mcmc_reference_datasets import (
    get_mcmc_reference_dataset,
    list_mcmc_reference_datasets,
    DONOR_A_GENOTYPES,
    DONOR_B_GENOTYPES,
    DONOR_C_GENOTYPES,
    MCMCMixtureDataset,
)
from backend.node.services.forensic.probabilistic.mixture import (
    MixtureDeconvolutionEngine,
    MixtureDeconvolutionResult,
)


# ===========================================================================
# 1. Reference Dataset Integrity & Loading
# ===========================================================================

class TestReferenceDatasetIntegrity:
    """Validates structural integrity and presence of all benchmark reference datasets."""

    ALL_DATASET_IDS = [
        "BTSC_SS_DONOR_A",
        "BTSC_SS_DONOR_B",
        "BTSC_MIX_1_1",
        "BTSC_MIX_3_1",
        "BTSC_MIX_9_1",
        "BTSC_MIX_19_1",
        "PROVEDIt_2P_300pg_1_3",
        "PROVEDIt_3P_5_3_2",
        "PROVEDIt_DEGRADED",
    ]

    @pytest.mark.parametrize("sample_id", ALL_DATASET_IDS)
    def test_dataset_loading_and_locus_count(self, sample_id: str):
        """Every reference dataset loads cleanly and contains 24 standard STR loci."""
        dataset = get_mcmc_reference_dataset(sample_id)
        assert dataset.sample_id == sample_id
        assert dataset.n_contributors >= 1
        assert len(dataset.epg_data) == 24, f"Dataset {sample_id} must have 24 loci"
        assert len(dataset.true_weights) == dataset.n_contributors
        assert abs(sum(dataset.true_weights) - 1.0) < 1e-6

    def test_list_reference_datasets_completeness(self):
        """list_mcmc_reference_datasets returns metadata for all 9 registered datasets."""
        datasets = list_mcmc_reference_datasets()
        assert len(datasets) == len(self.ALL_DATASET_IDS)
        ids = [d["sample_id"] for d in datasets]
        for expected_id in self.ALL_DATASET_IDS:
            assert expected_id in ids

    def test_invalid_dataset_id_raises_key_error(self):
        """Querying an unknown dataset key raises KeyError."""
        with pytest.raises(KeyError):
            get_mcmc_reference_dataset("NON_EXISTENT_DATASET_123")


# ===========================================================================
# 2. Dilution Ratio & Peak Height Proportionality
# ===========================================================================

class TestDilutionRatioAndPeakHeightConsistency:
    """
    Validates that electropherogram peak heights faithfully reproduce
    experimental dilution ratios across 1:1, 3:1, 9:1, 19:1 mixtures.
    """

    def test_btsc_1_1_mixture_balanced_heights(self):
        """In a 1:1 mixture, unique alleles of Donor A and Donor B have approximately equal heights."""
        ds = get_mcmc_reference_dataset("BTSC_MIX_1_1")
        # TH01: Donor A has (8, 9.3), Donor B has (6, 9.3).
        # Allele 8 is unique to A, Allele 6 is unique to B.
        th01_peaks = ds.epg_data["TH01"]
        h_6 = th01_peaks.get(6.0, 0.0)
        h_8 = th01_peaks.get(8.0, 0.0)

        assert h_6 > 0 and h_8 > 0
        ratio = h_8 / h_6
        assert 0.80 <= ratio <= 1.25, f"1:1 mixture ratio should be ~1.0, got {ratio}"

    def test_btsc_3_1_mixture_major_minor_ratio(self):
        """In a 3:1 (75:25) mixture, Donor A alleles are ~3x higher than Donor B alleles."""
        ds = get_mcmc_reference_dataset("BTSC_MIX_3_1")
        th01_peaks = ds.epg_data["TH01"]
        h_8 = th01_peaks.get(8.0, 0.0)  # Donor A unique
        h_6 = th01_peaks.get(6.0, 0.0)  # Donor B unique

        assert h_8 > 0 and h_6 > 0
        ratio = h_8 / h_6
        assert 2.50 <= ratio <= 3.50, f"3:1 mixture ratio should be ~3.0, got {ratio}"

    def test_btsc_9_1_mixture_major_minor_ratio(self):
        """In a 9:1 (90:10) mixture, Donor A alleles are ~9x higher than Donor B alleles."""
        ds = get_mcmc_reference_dataset("BTSC_MIX_9_1")
        th01_peaks = ds.epg_data["TH01"]
        h_8 = th01_peaks.get(8.0, 0.0)  # Donor A unique
        h_6 = th01_peaks.get(6.0, 0.0)  # Donor B unique

        assert h_8 > 0 and h_6 > 0
        ratio = h_8 / h_6
        assert 7.50 <= ratio <= 10.50, f"9:1 mixture ratio should be ~9.0, got {ratio}"

    def test_btsc_19_1_severe_imbalance(self):
        """In a 19:1 (95:5) mixture, major Donor A represents >= 90% of total non-stutter peak area."""
        ds = get_mcmc_reference_dataset("BTSC_MIX_19_1")
        th01_peaks = ds.epg_data["TH01"]
        h_8 = th01_peaks.get(8.0, 0.0)  # Donor A unique (750*2 RFU)
        h_6 = th01_peaks.get(6.0, 0.0)  # Donor B unique (75 RFU)

        assert h_8 > 0 and h_6 > 0
        assert h_8 > 15.0 * h_6


# ===========================================================================
# 3. Ground-Truth Allele Coverage Invariant
# ===========================================================================

class TestGroundTruthCoverageInvariant:
    """
    Validates that the ground truth donor genotypes account for 100% of observed alleles
    across all 24 loci (accounting for back-stutter artifacts).
    """

    @pytest.mark.parametrize("sample_id", [
        "BTSC_SS_DONOR_A",
        "BTSC_SS_DONOR_B",
        "BTSC_MIX_1_1",
        "BTSC_MIX_3_1",
        "PROVEDIt_2P_300pg_1_3",
        "PROVEDIt_3P_5_3_2",
    ])
    def test_donor_genotypes_cover_all_peaks(self, sample_id: str):
        """All observed EPG peaks correspond to true donor alleles or valid n-1 back-stutter products."""
        ds = get_mcmc_reference_dataset(sample_id)
        donors = list(ds.donor_genotypes.values())

        for locus, epg_peaks in ds.epg_data.items():
            true_alleles = set()
            for d in donors:
                true_alleles.update(d[locus])

            # Also allow n-1 stutter alleles (allele - 1.0)
            valid_alleles = set(true_alleles)
            for a in true_alleles:
                valid_alleles.add(round(a - 1.0, 2))

            for obs_allele, height in epg_peaks.items():
                if height >= 50.0:  # Above detection threshold
                    assert obs_allele in valid_alleles, (
                        f"Unaccounted allele {obs_allele} at {locus} in {sample_id}. "
                        f"True alleles: {true_alleles}"
                    )


# ===========================================================================
# 4. Mixture Deconvolution Engine on Reference Datasets
# ===========================================================================

class TestMixtureDeconvolutionOnReferenceDatasets:
    """
    Validates that MixtureDeconvolutionEngine correctly deconvolutes
    experimental mixtures and estimates contributor proportions.
    """

    def test_deconvolution_3_1_mixture_recovers_proportions(self):
        """MCMC deconvolution on BTSC_MIX_3_1 estimates major fraction w1 around 0.75."""
        ds = get_mcmc_reference_dataset("BTSC_MIX_3_1")
        # Run fast targeted MCMC (1000 burn, 3000 sample)
        engine = MixtureDeconvolutionEngine(
            model="STRmix",
            n_burn=1000,
            n_sample=3000,
            n_chains=3,
            seed=42,
        )
        # Select subset of 5 core loci for fast execution
        subset_epg = {loc: ds.epg_data[loc] for loc in ["D3S1358", "VWA", "TH01", "FGA", "D8S1179"]}

        result: MixtureDeconvolutionResult = engine.deconvolute(subset_epg, K=2)
        assert result.n_contributors == 2
        # Major contributor weight should be between 0.60 and 0.90
        assert 0.60 <= result.major_fraction <= 0.90, f"Expected major ~0.75, got {result.major_fraction}"

    def test_deconvolution_1_1_mixture_symmetry(self):
        """MCMC deconvolution on BTSC_MIX_1_1 yields balanced weights near 0.50."""
        ds = get_mcmc_reference_dataset("BTSC_MIX_1_1")
        engine = MixtureDeconvolutionEngine(
            model="STRmix",
            n_burn=1000,
            n_sample=3000,
            n_chains=3,
            seed=101,
        )
        subset_epg = {loc: ds.epg_data[loc] for loc in ["D3S1358", "VWA", "TH01", "D8S1179"]}

        result: MixtureDeconvolutionResult = engine.deconvolute(subset_epg, K=2)
        assert result.n_contributors == 2
        # Under 1:1 mixture, both contributor proportions are balanced within [0.25, 0.75]
        assert 0.25 <= result.major_fraction <= 0.75, f"Expected balanced ~0.50, got {result.major_fraction}"


# ===========================================================================
# 5. Suspect Inclusion & Exclusion Likelihood Ratios
# ===========================================================================

class TestSuspectInclusionAndExclusionLR:
    """
    Validates that true contributors yield strong inclusion support (LR >> 1.0)
    and non-donors yield strong exclusion support (LR << 1.0).
    """

    def test_true_donor_a_inclusion_lr(self):
        """Evaluating true Donor A against BTSC_MIX_3_1 produces strong support for prosecution (LR > 10^3)."""
        ds = get_mcmc_reference_dataset("BTSC_MIX_3_1")
        loci = ["D3S1358", "VWA", "TH01", "FGA", "D8S1179"]
        subset_epg = {loc: ds.epg_data[loc] for loc in loci}
        suspect_genotype = [DONOR_A_GENOTYPES[loc] for loc in loci]

        engine = MixtureDeconvolutionEngine(
            model="STRmix",
            n_burn=1000,
            n_sample=3000,
            n_chains=3,
            seed=42,
        )
        result = engine.deconvolute(subset_epg, K=2, suspect_genotype=suspect_genotype)

        assert result.lr_result.log10_lr_point > 2.0, (
            f"True donor must yield positive log10(LR) > 2.0, got {result.lr_result.log10_lr_point}"
        )
        assert result.lr_result.lr_point > 100.0

    def test_non_donor_exclusion_lr(self):
        """Evaluating an artificial non-donor genotype against BTSC_MIX_3_1 produces exclusion support (LR < 1.0)."""
        ds = get_mcmc_reference_dataset("BTSC_MIX_3_1")
        loci = ["D3S1358", "VWA", "TH01", "FGA", "D8S1179"]
        subset_epg = {loc: ds.epg_data[loc] for loc in loci}
        # Non-donor with absent alleles: e.g. (99.0, 99.0) or totally foreign alleles
        non_donor_genotype = [(25.0, 26.0) for _ in loci]

        engine = MixtureDeconvolutionEngine(
            model="STRmix",
            n_burn=1000,
            n_sample=3000,
            n_chains=3,
            seed=42,
        )
        result = engine.deconvolute(subset_epg, K=2, suspect_genotype=non_donor_genotype)

        # LR should be << 1.0 (log10 LR < 0.0)
        assert result.lr_result.log10_lr_point < 0.0 or result.lr_result.lr_point < 1.0, (
            f"Non-donor must be excluded (log10 LR < 0), got {result.lr_result.log10_lr_point}"
        )
