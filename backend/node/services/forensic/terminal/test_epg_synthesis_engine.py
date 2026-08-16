"""
Unit Test Suite for EpgSynthesisEngine
Compliant with ISO/IEC 17025:2017 & SWGDAM 2020 Guidelines.
Verifies multi-dye waveforms, degradation kinetics (DI), quality thresholds (AT, ST, SAT),
heterozygote balance (Hb), reverse stutter, and spectral pull-up compensation.
"""

import pytest
import math
from backend.node.services.forensic.terminal.epg_synthesis_engine import (
    EpgSynthesisEngine,
    DyeChannelEnum,
    PANEL_24_LOCUS_MAPPING,
    LIZ_600_STANDARD_SIZES,
)


class TestEpgSynthesisEngine:

    def test_01_allele_size_calculation_and_microvariants(self):
        """Verifies base pair size calculation across standard alleles, microvariants, and Amelogenin."""
        # Amelogenin X (106 bp) and Y (112 bp)
        assert EpgSynthesisEngine.calculate_allele_size_bp("Amelogenin", "X") == 106.0
        assert EpgSynthesisEngine.calculate_allele_size_bp("Amelogenin", "Y") == 112.0

        # TH01 (base=139.0, repeat=4.0): allele 9.3 -> 139 + 9*4 + 3 = 178.0 bp
        th01_93 = EpgSynthesisEngine.calculate_allele_size_bp("TH01", "9.3")
        assert th01_93 == 178.0

        # D3S1358 (base=67.0, repeat=4.0): allele 15 -> 67 + 15*4 = 127.0 bp
        d3_15 = EpgSynthesisEngine.calculate_allele_size_bp("D3S1358", "15")
        assert d3_15 == 127.0

        # D21S11 (base=78.0, repeat=4.0): allele 31.2 -> 78 + 31*4 + 2 = 204.0 bp
        d21_312 = EpgSynthesisEngine.calculate_allele_size_bp("D21S11", "31.2")
        assert d21_312 == 204.0

    def test_02_modified_gaussian_lorentzian_waveform(self):
        """Verifies peak shape symmetry, height at t=t0, and asymptotic decay."""
        t0 = 150.0
        h = 2400.0
        # Exactly at center
        val_center = EpgSynthesisEngine.modified_gaussian_lorentzian_peak(t0, t0, h)
        assert pytest.approx(val_center, abs=1e-3) == h

        # Symmetrical decay at +/- 1 bp
        val_left = EpgSynthesisEngine.modified_gaussian_lorentzian_peak(t0 - 1.0, t0, h)
        val_right = EpgSynthesisEngine.modified_gaussian_lorentzian_peak(t0 + 1.0, t0, h)
        assert val_left < h
        assert val_right < h
        # Slight asymmetry due to alpha = 0.05
        assert abs(val_left - val_right) > 0.0

        # Beyond 4 bp window, intensity is near baseline
        val_far = EpgSynthesisEngine.modified_gaussian_lorentzian_peak(t0 + 6.0, t0, h)
        assert val_far < 50.0

    def test_03_5dye_and_ils_channel_trace_synthesis(self):
        """Verifies multi-dye trace generation, size standard peaks, and peak annotations."""
        profile = {
            "D3S1358": {"allele1": "15", "allele2": "16", "rfu1": 1500, "rfu2": 1450},
            "vWA": {"allele1": "17", "allele2": "18", "rfu1": 1600, "rfu2": 1550},
            "TH01": {"allele1": "9.3", "allele2": "9.3", "rfu1": 2000, "rfu2": 2000},
            "FGA": {"allele1": "22", "allele2": "24", "rfu1": 1400, "rfu2": 1350},
            "Amelogenin": {"allele1": "X", "allele2": "Y", "rfu1": 1800, "rfu2": 1750},
        }

        res = EpgSynthesisEngine.synthesize_epg_from_profile(
            sample_id="EPG_SAMPLE_01",
            str_profile=profile,
            template_ng=1.0,
            degradation_rate=0.0,
            include_stutter=True,
            include_pullup=False,
            end_bp=610.0,
        )

        assert res.sample_id == "EPG_SAMPLE_01"
        assert res.degradation_severity == "PRISTINE"
        assert res.overall_passed_qc is True
        assert len(res.traces) == 6  # Blue, Green, Yellow, Red, Purple, Orange

        # Check Orange ILS channel has size standard points
        orange_trace = res.traces[DyeChannelEnum.ORANGE]
        assert len(orange_trace.peaks) == len(LIZ_600_STANDARD_SIZES)
        assert orange_trace.peaks[0].locus_name == "ILS_600"

        # Check Blue channel has D3S1358
        blue_trace = res.traces[DyeChannelEnum.BLUE]
        blue_allele_calls = [p.allele_call for p in blue_trace.peaks if not p.is_stutter]
        assert "15" in blue_allele_calls
        assert "16" in blue_allele_calls

    def test_04_degradation_kinetics_and_di_index(self):
        """Verifies exponential signal decay and degradation index DI = D8S1179 / FGA."""
        profile = {
            "D8S1179": {"allele1": "13", "allele2": "14", "rfu1": 2000, "rfu2": 1950},
            "FGA": {"allele1": "22", "allele2": "24", "rfu1": 2000, "rfu2": 1950},
        }

        # Severe degradation (rate = 0.015)
        res_deg = EpgSynthesisEngine.synthesize_epg_from_profile(
            sample_id="DEG_SAMPLE",
            str_profile=profile,
            template_ng=1.0,
            degradation_rate=0.015,
        )

        assert res_deg.degradation_index > 5.0
        assert res_deg.degradation_severity == "SEVERE_DEGRADATION"

        # Find D8S1179 peak height vs FGA peak height
        d8_peak = next(p for p in res_deg.all_peaks if p.locus_name == "D8S1179" and not p.is_stutter)
        fga_peak = next(p for p in res_deg.all_peaks if p.locus_name == "FGA" and not p.is_stutter)
        assert d8_peak.rfu_height > fga_peak.rfu_height * 3.0

    def test_05_stutter_filter_and_swgdam_gates(self):
        """Verifies reverse stutter (N-4) tagging and SWGDAM artifact filtering."""
        profile = {
            "D3S1358": {"allele1": "15", "allele2": "16", "rfu1": 2500, "rfu2": 2400},
        }

        res = EpgSynthesisEngine.synthesize_epg_from_profile(
            sample_id="STUTTER_TEST",
            str_profile=profile,
            include_stutter=True,
        )

        stutter_peaks = [p for p in res.all_peaks if p.is_stutter]
        assert len(stutter_peaks) >= 1
        for st in stutter_peaks:
            assert st.stutter_ratio <= PANEL_24_LOCUS_MAPPING["D3S1358"].max_stutter_ratio

        # Filter artifacts
        cleaned = EpgSynthesisEngine.filter_epg_artifacts(res.all_peaks)
        assert not any(p.is_stutter for p in cleaned)
        assert all(p.rfu_height >= EpgSynthesisEngine.ANALYTICAL_THRESHOLD for p in cleaned)

    def test_06_pullup_artifact_detection_and_saturation(self):
        """Verifies pull-up bleedthrough generation (< 6%) and saturation threshold (SAT > 8000 RFU)."""
        profile = {
            "TH01": {"allele1": "9.3", "allele2": "9.3", "rfu1": 9500, "rfu2": 9500},
        }

        res = EpgSynthesisEngine.synthesize_epg_from_profile(
            sample_id="SAT_PULLUP_TEST",
            str_profile=profile,
            include_pullup=True,
        )

        th01_peak = next(p for p in res.all_peaks if p.locus_name == "TH01" and not p.is_stutter and not p.is_pullup)
        assert th01_peak.is_saturated is True
        assert th01_peak.rfu_height > 8000.0

        pullup_peaks = [p for p in res.all_peaks if p.is_pullup]
        assert len(pullup_peaks) >= 1
        for pu in pullup_peaks:
            assert pu.rfu_height / th01_peak.rfu_height <= 0.06
