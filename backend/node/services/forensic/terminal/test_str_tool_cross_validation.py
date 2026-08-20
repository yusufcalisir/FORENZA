"""
Unit tests for FORENZA 24-Locus STR Independent Tool Cross-Validation Engine
Validation Suite for Sub-Item 1.1.3:
- NIST 1036 PopGen Frequency Engine Analytical Cross-Comparison (Butler et al. 2012)
- FragalyseQt CE Fragment Sizing & Allelic Ladder Binning (+/- 0.50 bp window)
- SoftGenetics GeneMarker HID Hybrid STR Artifact Filter Framework
Derived from: research/pillar_1_probabilistic_genotyping_research.md
"""

import pytest
from backend.node.services.forensic.terminal.str_tool_cross_validation import (
    NistPopGenAnalyticalBenchmarkEngine,
    FragalyseQtCEBinningBenchmarkEngine,
    GeneMarkerHIDBenchmarkFilter,
    ArtifactClassificationEnum,
)
from backend.node.services.forensic.terminal.str_reference_datasets import (
    NIST_SRM_2391D_COMP_A,
    NIST_SRM_2391D_COMP_B,
    NIST_SRM_2391D_COMP_E,
)


class TestNistPopGenAnalyticalCrossValidation:
    """Test suite for NIST 1036 PopGen multi-population comparative calculations."""

    @pytest.fixture
    def european_test_profile(self):
        return {
            k: (v["allele1"], v.get("allele2", v["allele1"]))
            for k, v in NIST_SRM_2391D_COMP_A.str_profile.items()
        }

    def test_multi_population_cross_comparison(self, european_test_profile):
        """
        Verify that profile likelihood is calculated across all 4 NIST populations
        and cross-population comparison ratios are generated without NaN or underflow.
        """
        res = NistPopGenAnalyticalBenchmarkEngine.compute_multi_population_cross_comparison(
            profile=european_test_profile,
            theta=0.01,
        )
        assert res["evaluated_loci_count"] == 23
        pop_res = res["population_results"]

        assert "Caucasian" in pop_res
        assert "African American" in pop_res
        assert "Hispanic" in pop_res
        assert "Asian" in pop_res

        # For a Caucasian individual (9947A), LR under Caucasian background should be distinct from African American
        cau_lr = pop_res["Caucasian"]["lr"]
        afr_lr = pop_res["African American"]["lr"]
        assert cau_lr > 0
        assert afr_lr > 0

        ratios = res["cross_population_ratios"]
        assert ratios["ratio_EUR_to_AFR"] > 0
        assert ratios["ratio_EUR_to_HIS"] > 0
        assert ratios["ratio_EUR_to_EAS"] > 0


class TestFragalyseQtCEBinningConcordance:
    """Test suite for FragalyseQt CE fragment sizing and allelic ladder binning."""

    def test_ladder_generation_th01(self):
        """Verify allelic ladder bins for TH01 including 9.3 microvariant."""
        ladder = FragalyseQtCEBinningBenchmarkEngine.generate_locus_allelic_ladder("TH01", base_offset_bp=60.0)
        assert len(ladder) > 0
        allele_calls = [b.allele_call for b in ladder]
        assert "6" in allele_calls
        assert "7" in allele_calls
        assert "8" in allele_calls
        assert "9" in allele_calls
        assert "9.3" in allele_calls

        # Center bp check: TH01 repeat size is 4 bp.
        # Repeat 6: 60 + 6*4 = 84.0 bp
        bin_6 = next(b for b in ladder if b.allele_call == "6")
        assert bin_6.center_bp == 84.0
        assert bin_6.bin_min_bp == 83.5
        assert bin_6.bin_max_bp == 84.5

        # Microvariant 9.3: 60 + 9*4 + 3 = 99.0 bp
        bin_9_3 = next(b for b in ladder if b.allele_call == "9.3")
        assert bin_9_3.center_bp == 99.0
        assert bin_9_3.is_microvariant is True

    def test_binning_within_tolerance(self):
        """Verify observed peak within +/- 0.50 bp bins into nominal allele."""
        # Observed peak at 84.2 bp should bin into TH01 allele 6 (center 84.0 bp)
        peak = FragalyseQtCEBinningBenchmarkEngine.bin_peak(
            locus_name="TH01",
            observed_size_bp=84.2,
            peak_height_rfu=2500,
            base_offset_bp=60.0,
        )
        assert peak.is_off_ladder is False
        assert peak.assigned_allele == "6"
        assert pytest.approx(peak.bin_offset_bp, abs=1e-3) == 0.2

    def test_binning_microvariant_th01_9_3(self):
        """Verify observed peak at 99.1 bp bins into TH01 9.3 microvariant."""
        peak = FragalyseQtCEBinningBenchmarkEngine.bin_peak(
            locus_name="TH01",
            observed_size_bp=99.1,
            peak_height_rfu=3200,
            base_offset_bp=60.0,
        )
        assert peak.is_off_ladder is False
        assert peak.assigned_allele == "9.3"

    def test_off_ladder_peak_flagged(self):
        """Verify observed peak outside +/- 0.50 bp window is flagged as Off-Ladder (OL)."""
        # Intermediate peak at 85.8 bp (between allele 6 [84.0 bp] and allele 7 [88.0 bp])
        peak = FragalyseQtCEBinningBenchmarkEngine.bin_peak(
            locus_name="TH01",
            observed_size_bp=85.8,
            peak_height_rfu=1500,
            base_offset_bp=60.0,
        )
        assert peak.is_off_ladder is True
        assert peak.assigned_allele == "OL"
        assert "OFF_LADDER" in peak.quality_flag


class TestGeneMarkerHIDArtifactFiltering:
    """Test suite for SoftGenetics GeneMarker HID artifact filter rules."""

    def test_reverse_stutter_filter(self):
        """
        Verify that peak at N-1 repeat (-4 bp) with ratio <= SR_max is filtered as reverse stutter.
        TH01 SR_max = 0.050 (5.0%).
        Parent peak: 99.0 bp (allele 9.3), 2000 RFU.
        Stutter peak: 95.0 bp (allele 8.3 / N-1), 90 RFU (ratio = 90/2000 = 0.045 <= 0.050).
        """
        peaks = [
            {"size_bp": 99.0, "height_rfu": 2000.0, "dye_channel": "BLUE"},
            {"size_bp": 95.0, "height_rfu": 90.0, "dye_channel": "BLUE"},
        ]
        classified = GeneMarkerHIDBenchmarkFilter.classify_and_filter_peaks(
            locus_name="TH01",
            peaks=peaks,
            base_offset_bp=60.0,
        )
        assert len(classified) == 2
        stutter_call = next(c for c in classified if c.size_bp == 95.0)
        assert stutter_call.classification == ArtifactClassificationEnum.REVERSE_STUTTER
        assert stutter_call.is_filtered is True

    def test_forward_stutter_filter(self):
        """
        Verify forward stutter filter at N+1 repeat (+4 bp) with ratio <= 0.035.
        """
        peaks = [
            {"size_bp": 99.0, "height_rfu": 2000.0, "dye_channel": "BLUE"},
            {"size_bp": 103.0, "height_rfu": 50.0, "dye_channel": "BLUE"},
        ]
        classified = GeneMarkerHIDBenchmarkFilter.classify_and_filter_peaks(
            locus_name="TH01",
            peaks=peaks,
            base_offset_bp=60.0,
        )
        fwd_call = next(c for c in classified if c.size_bp == 103.0)
        assert fwd_call.classification == ArtifactClassificationEnum.FORWARD_STUTTER
        assert fwd_call.is_filtered is True

    def test_minus_a_split_peak_filter(self):
        """
        Verify incomplete adenylation (-A split peak) at -1.0 bp with ratio <= 0.15.
        """
        peaks = [
            {"size_bp": 99.0, "height_rfu": 2000.0, "dye_channel": "BLUE"},
            {"size_bp": 98.0, "height_rfu": 160.0, "dye_channel": "BLUE"},  # -A peak (ratio 0.08)
        ]
        classified = GeneMarkerHIDBenchmarkFilter.classify_and_filter_peaks(
            locus_name="TH01",
            peaks=peaks,
            base_offset_bp=60.0,
        )
        minus_a_call = next(c for c in classified if c.size_bp == 98.0)
        assert minus_a_call.classification == ArtifactClassificationEnum.MINUS_A_SPLIT_PEAK
        assert minus_a_call.is_filtered is True

    def test_spectral_pull_up_filter(self):
        """
        Verify spectral bleed-through artifact from saturated parent peak (>4000 RFU).
        """
        peaks = [
            {"size_bp": 99.0, "height_rfu": 4500.0, "dye_channel": "BLUE"},  # Saturated primary
            {"size_bp": 99.02, "height_rfu": 220.0, "dye_channel": "GREEN"}, # Pull-up in Green
        ]
        classified = GeneMarkerHIDBenchmarkFilter.classify_and_filter_peaks(
            locus_name="TH01",
            peaks=peaks,
            base_offset_bp=60.0,
        )
        pull_up_call = next(c for c in classified if c.height_rfu == 220.0)
        assert pull_up_call.classification == ArtifactClassificationEnum.SPECTRAL_PULL_UP
        assert pull_up_call.is_filtered is True
        assert pull_up_call.dye_channel == "GREEN"

    def test_below_analytical_threshold_filter(self):
        """Verify sub-50 RFU baseline peaks are culled."""
        peaks = [
            {"size_bp": 99.0, "height_rfu": 1500.0, "dye_channel": "BLUE"},
            {"size_bp": 84.0, "height_rfu": 35.0, "dye_channel": "BLUE"},  # Below AT=50 RFU
        ]
        classified = GeneMarkerHIDBenchmarkFilter.classify_and_filter_peaks(
            locus_name="TH01",
            peaks=peaks,
            base_offset_bp=60.0,
        )
        sub_at_call = next(c for c in classified if c.height_rfu == 35.0)
        assert sub_at_call.classification == ArtifactClassificationEnum.BELOW_ANALYTICAL_THRESHOLD
        assert sub_at_call.is_filtered is True

    def test_heterozygote_peak_height_ratio(self):
        """Verify PHR evaluation: >= 0.60 passes, < 0.60 flags imbalance."""
        phr_pass, is_balanced = GeneMarkerHIDBenchmarkFilter.evaluate_heterozygote_balance(1800.0, 1500.0)
        assert is_balanced is True
        assert pytest.approx(phr_pass, abs=1e-3) == 1500.0 / 1800.0

        phr_fail, is_balanced_fail = GeneMarkerHIDBenchmarkFilter.evaluate_heterozygote_balance(2000.0, 700.0)
        assert is_balanced_fail is False
        assert pytest.approx(phr_fail, abs=1e-3) == 700.0 / 2000.0
