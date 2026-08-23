"""
Unit and Integration Tests for FORENZA MPS STR 4-Population Frequencies & Biostatistics (Phase 2).
"""

import pytest
from node.services.forensic.genomics.mps_str.frequency_matrices import (
    SequenceFrequencyMatrixEngine,
    POPULATION_COHORTS,
    EMPIRICAL_SEQUENCE_FREQUENCIES,
)
from node.services.forensic.genomics.mps_str.biostatistics import (
    ForensicBiostatisticsEngine,
    LocusBiostatisticsReport,
    MultiLocusDiversitySummary,
)


class TestSequenceFrequencyMatrices:
    """Tests empirical frequency retrieval, Dirichlet smoothing, and simplex normalization."""

    def test_population_cohorts_metadata(self):
        assert "AFRICAN_AMERICAN" in POPULATION_COHORTS
        assert "CAUCASIAN" in POPULATION_COHORTS
        assert "HISPANIC" in POPULATION_COHORTS
        assert "KOREAN" in POPULATION_COHORTS
        assert "GLOBAL_COMPOSITE" in POPULATION_COHORTS
        
        cauc = POPULATION_COHORTS["CAUCASIAN"]
        assert cauc.sample_count == 82
        assert cauc.chromosome_count == 164
        assert abs(cauc.p_min_floor - (1.0 / 165)) < 1e-6

    def test_simplex_normalization_invariant(self):
        # Verify sum(p_i) == 1.000000 across all loci and populations
        for locus in EMPIRICAL_SEQUENCE_FREQUENCIES:
            for pop in ["AFRICAN_AMERICAN", "CAUCASIAN", "HISPANIC", "KOREAN", "GLOBAL_COMPOSITE"]:
                freq_dict = SequenceFrequencyMatrixEngine.get_all_frequencies_for_locus(locus, pop)
                total_sum = sum(freq_dict.values())
                assert abs(total_sum - 1.0) < 1e-6, f"Simplex violation at {locus} in {pop}: sum={total_sum}"

    def test_dirichlet_smoothing_unseen_allele(self):
        unseen_freq = SequenceFrequencyMatrixEngine.get_sequence_frequency(
            "SE33",
            "[CTTT]99_NOVEL_UNSEEN_ALLELE",
            "KOREAN"
        )
        assert unseen_freq == POPULATION_COHORTS["KOREAN"].p_min_floor

    def test_population_specific_frequency_bias(self):
        # D3S1358 15b is much higher in African-American (0.145) than Caucasian (0.030)
        f_afam = SequenceFrequencyMatrixEngine.get_sequence_frequency("D3S1358", "[TCTA]1 [TCTG]2 [TCTA]12", "AFRICAN_AMERICAN")
        f_cauc = SequenceFrequencyMatrixEngine.get_sequence_frequency("D3S1358", "[TCTA]1 [TCTG]2 [TCTA]12", "CAUCASIAN")
        assert f_afam > f_cauc * 4.0


class TestForensicBiostatisticsEngine:
    """Tests Expected Heterozygosity, Power of Discrimination, and Match Probability calculations."""

    def test_se33_biostatistics_high_heterozygosity(self):
        rep = ForensicBiostatisticsEngine.calculate_locus_biostatistics("SE33", "GLOBAL_COMPOSITE")
        
        assert rep.locus_name == "SE33"
        # In empirical sequence analysis, SE33 H_exp is > 0.90
        assert rep.expected_heterozygosity >= 0.85
        assert rep.power_of_discrimination >= 0.90
        assert rep.match_probability < 0.10

    def test_d3s1358_heterozygosity_boost(self):
        rep = ForensicBiostatisticsEngine.calculate_locus_biostatistics("D3S1358", "GLOBAL_COMPOSITE")
        
        # Sequence-based D3S1358 achieves elevated heterozygosity (~0.85 - 0.91)
        assert rep.expected_heterozygosity >= 0.80
        assert rep.power_of_discrimination >= 0.90

    def test_multi_locus_combined_diversity_summary(self):
        test_loci = ["SE33", "D3S1358", "D21S11", "vWA", "TH01"]
        summary = ForensicBiostatisticsEngine.calculate_multi_locus_summary(test_loci, "GLOBAL_COMPOSITE")
        
        assert len(summary.loci_reports) == 5
        assert summary.combined_match_probability < 1e-4
        assert summary.combined_power_of_discrimination > 0.9999
        assert summary.mean_expected_heterozygosity > 0.75
