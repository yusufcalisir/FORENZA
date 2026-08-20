"""
Unit tests for NIST 1036 Population Genetics & Dirichlet-Laplace Smoothing Engine
ISO/IEC 17025:2017 and NRC II Rule 4.1/4.2 Validation.
Derived from: research/str_24_locus_microvariants_research.md
"""

import pytest
import math
from backend.node.services.forensic.terminal.nist_1036_popgen_engine import (
    Nist1036PopGenEngine,
    NistPopulationEnum,
    POPULATION_SAMPLE_SIZES,
    POPULATION_P_MIN_FLOORS,
    NIST_1036_ALLELE_FREQUENCIES,
)


class TestNist1036PopGenEngineConstants:
    """Test suite for population sample sizes, NRC II floors, and dataset completeness."""

    def test_population_sample_sizes(self):
        """Verify sample sizes (N, 2N) across all 4 NIST population groups."""
        assert POPULATION_SAMPLE_SIZES[NistPopulationEnum.CAUCASIAN] == (361, 722)
        assert POPULATION_SAMPLE_SIZES[NistPopulationEnum.AFRICAN_AMERICAN] == (342, 684)
        assert POPULATION_SAMPLE_SIZES[NistPopulationEnum.HISPANIC] == (236, 472)
        assert POPULATION_SAMPLE_SIZES[NistPopulationEnum.ASIAN] == (97, 194)
        assert POPULATION_SAMPLE_SIZES[NistPopulationEnum.TOTAL_DATASET] == (1036, 2072)

    def test_nrc_ii_p_min_floors(self):
        """Verify exact NRC II Recommendation 4.1 minimum frequency lower bounds."""
        assert pytest.approx(POPULATION_P_MIN_FLOORS[NistPopulationEnum.CAUCASIAN], rel=1e-6) == 5.0 / 722.0
        assert pytest.approx(POPULATION_P_MIN_FLOORS[NistPopulationEnum.AFRICAN_AMERICAN], rel=1e-6) == 5.0 / 684.0
        assert pytest.approx(POPULATION_P_MIN_FLOORS[NistPopulationEnum.HISPANIC], rel=1e-6) == 5.0 / 472.0
        assert pytest.approx(POPULATION_P_MIN_FLOORS[NistPopulationEnum.ASIAN], rel=1e-6) == 5.0 / 194.0
        assert pytest.approx(POPULATION_P_MIN_FLOORS[NistPopulationEnum.TOTAL_DATASET], rel=1e-6) == 5.0 / 2072.0

    def test_all_24_loci_matrix_presence(self):
        """Verify all 24 standard loci are cataloged in NIST_1036_ALLELE_FREQUENCIES."""
        expected = [
            "D3S1358", "vWA", "FGA", "D8S1179", "D21S11", "D18S51",
            "D5S818", "D13S317", "D7S820", "D16S539", "CSF1PO", "TH01",
            "TPOX", "D1S1656", "D2S441", "D2S1338", "D10S1248", "D12S391",
            "D19S433", "D22S1045", "SE33", "Penta D", "Penta E", "Amelogenin"
        ]
        for locus in expected:
            assert locus in NIST_1036_ALLELE_FREQUENCIES, f"Locus {locus} missing in frequency matrix"


class TestNist1036AlleleFrequencies:
    """Test suite for exact empirical allele frequencies and micro-variants."""

    def test_th01_9_3_microvariant_frequency(self):
        """Verify TH01 9.3 microvariant across populations."""
        assert Nist1036PopGenEngine.get_allele_frequency("TH01", "9.3", "Caucasian") == 0.3587
        assert Nist1036PopGenEngine.get_allele_frequency("TH01", "9.3", "African American") == 0.1067
        assert Nist1036PopGenEngine.get_allele_frequency("TH01", "9.3", "Hispanic") == 0.2140
        assert Nist1036PopGenEngine.get_allele_frequency("TH01", "9.3", "Asian") == 0.1340

    def test_fga_22_2_microvariant_frequency(self):
        """Verify FGA 22.2 microvariant across populations."""
        assert Nist1036PopGenEngine.get_allele_frequency("FGA", "22.2", "Caucasian") == 0.0125
        assert Nist1036PopGenEngine.get_allele_frequency("FGA", "22.2", "African American") == 0.0161
        assert Nist1036PopGenEngine.get_allele_frequency("FGA", "22.2", "Hispanic", apply_p_min_floor=False) == 0.0085
        # In Asian, empirical freq is 0.0052; with p_min floor (5/194 ≈ 0.02577), floor is applied
        freq_asian_floored = Nist1036PopGenEngine.get_allele_frequency("FGA", "22.2", "Asian", apply_p_min_floor=True)
        assert pytest.approx(freq_asian_floored, rel=1e-4) == 5.0 / 194.0

    def test_d21s11_31_2_microvariant_frequency(self):
        """Verify D21S11 31.2 microvariant."""
        assert Nist1036PopGenEngine.get_allele_frequency("D21S11", "31.2", "Caucasian") == 0.0706
        assert Nist1036PopGenEngine.get_allele_frequency("D21S11", "31.2", "African American") == 0.1243
        assert Nist1036PopGenEngine.get_allele_frequency("D21S11", "31.2", "Hispanic") == 0.0699

    def test_d1s1656_17_3_microvariant_frequency(self):
        """Verify D1S1656 17.3 microvariant."""
        assert Nist1036PopGenEngine.get_allele_frequency("D1S1656", "17.3", "Caucasian") == 0.2064
        assert Nist1036PopGenEngine.get_allele_frequency("D1S1656", "17.3", "African American") == 0.1287
        assert Nist1036PopGenEngine.get_allele_frequency("D1S1656", "17.3", "Hispanic") == 0.1801

    def test_dirichlet_laplace_smoothing_unobserved_allele(self):
        """Verify Dirichlet-Laplace smoothing for rare/unobserved alleles."""
        smoothed_caucasian = Nist1036PopGenEngine.calculate_dirichlet_laplace_smoothed_freq("D3S1358", "Caucasian", alpha=1.0)
        p_min_caucasian = POPULATION_P_MIN_FLOORS[NistPopulationEnum.CAUCASIAN]
        assert smoothed_caucasian >= p_min_caucasian


class TestGenotypeProbabilitiesAndInvariants:
    """Test suite for Balding-Nichols coancestry models and log-likelihood additivity."""

    def test_homozygote_calculation_th01_9_3(self):
        """
        Verify TH01 (9.3, 9.3) in Caucasian under theta=0.01:
        p_1 = 0.3587
        P(G) = (0.3587)^2 + (0.3587)(0.6413)(0.01) = 0.12866569 + 0.00230034 = 0.130966
        """
        p_g, lr, formula = Nist1036PopGenEngine.calculate_genotype_probability(
            locus="TH01",
            allele1="9.3",
            allele2="9.3",
            population="Caucasian",
            theta=0.01,
        )
        assert pytest.approx(p_g, rel=1e-4) == 0.130965
        assert pytest.approx(lr, rel=1e-3) == 7.6356

    def test_heterozygote_calculation_d3s1358(self):
        """
        Verify D3S1358 (15, 16) in Caucasian:
        p_1 = 0.2479, p_2 = 0.2313
        P(G) = 2 * (0.2479) * (0.2313) = 0.114679
        LR = 1 / P(G) = 8.7200
        """
        p_g, lr, formula = Nist1036PopGenEngine.calculate_genotype_probability(
            locus="D3S1358",
            allele1="15",
            allele2="16",
            population="Caucasian",
            theta=0.01,
        )
        assert pytest.approx(p_g, rel=1e-4) == 0.114679
        assert pytest.approx(lr, rel=1e-3) == 8.7200

    def test_single_allele_dropout_calculation(self):
        """Verify dropout formula: 2*p_1*(1-p_1)*Q + p_1^2*Q^2."""
        p_g, lr, formula = Nist1036PopGenEngine.calculate_genotype_probability(
            locus="D3S1358",
            allele1="15",
            allele2=None,
            population="Caucasian",
            is_dropout=True,
            dropout_q=0.05,
        )
        p_1 = 0.2479
        expected = 2.0 * p_1 * (1.0 - p_1) * 0.05 + (p_1 ** 2) * (0.05 ** 2)
        assert pytest.approx(p_g, rel=1e-6) == expected
        assert lr == pytest.approx(1.0 / expected, rel=1e-4)

    def test_multilocus_profile_log_likelihood_invariant(self):
        """
        Enforce strict invariant: |log10(LR) - sum(log10(LR_m))| < 10^-6.
        """
        profile = {
            "D3S1358": ("15", "16"),
            "vWA": ("16", "17"),
            "FGA": ("21", "23"),
            "TH01": ("9.3", "9.3"),
            "SE33": ("26.2", "28.2"),
        }
        res = Nist1036PopGenEngine.calculate_multilocus_profile_probability(
            profile=profile,
            population="Caucasian",
            theta=0.01,
        )
        log10_lr = res["combined_log10_lr"]
        sum_locus_log10_lr = sum(r["log10_lr"] for r in res["locus_results"])
        assert abs(log10_lr - sum_locus_log10_lr) < 1e-6
