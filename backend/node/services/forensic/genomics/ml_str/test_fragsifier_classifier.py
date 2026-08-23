"""
Unit Tests for Fragsifier Random Forest Ensemble Classifier (Phase 2).
"""

import pytest
from node.services.forensic.genomics.ml_str.schemas import ArtifactClassEnum
from node.services.forensic.genomics.ml_str.feature_extractor import MLSTRFeatureExtractor
from node.services.forensic.genomics.ml_str.classifier import FragsifierRandomForestClassifier


class TestFragsifierClassifier:
    """Tests 7-class signal classification, stutter discrimination, and pull-up culling."""

    def test_classify_true_major_allele(self):
        feat = MLSTRFeatureExtractor.extract_features(
            locus_name="D21S11",
            peak_id="Allele_30",
            peak_height=2400.0,
            bp_position=214.0,
            major_allele_bp=214.0,
            analytical_threshold=50.0
        )
        res = FragsifierRandomForestClassifier.classify_peak(feat)
        
        assert res.predicted_class == ArtifactClassEnum.CLASS_TRUE_ALLELE
        assert res.is_true_allele_candidate is True
        assert res.confidence_score > 0.90
        assert "RETAIN_AS_TRUE_ALLELE_CANDIDATE" in res.recommended_action

    def test_classify_back_stutter_signal(self):
        # Peak at -4 bp with 8.5% of major allele height (typical back stutter)
        feat = MLSTRFeatureExtractor.extract_features(
            locus_name="D21S11",
            peak_id="Stutter_29",
            peak_height=204.0,  # 8.5% of 2400
            major_allele_height=2400.0,
            bp_position=210.0,  # -4 bp from 214.0
            major_allele_bp=214.0,
            repeat_unit_len=4,
            analytical_threshold=50.0
        )
        res = FragsifierRandomForestClassifier.classify_peak(feat)
        
        assert res.predicted_class == ArtifactClassEnum.CLASS_BACK_STUTTER
        assert res.is_true_allele_candidate is False
        assert "SUBTRACT_STUTTER_SIGNAL" in res.recommended_action

    def test_classify_spectral_pull_up(self):
        # Secondary dye pull-up with 25% co-eluting intensity
        feat = MLSTRFeatureExtractor.extract_features(
            locus_name="vWA",
            peak_id="PullUp_Peak_16",
            peak_height=650.0,
            co_eluting_secondary_rfu=200.0,  # pull-up > 15%
            bp_position=160.0,
            major_allele_bp=160.0,
            analytical_threshold=50.0
        )
        res = FragsifierRandomForestClassifier.classify_peak(feat)
        
        assert res.predicted_class == ArtifactClassEnum.CLASS_SPECTRAL_PULL_UP
        assert res.is_true_allele_candidate is False
        assert "CULL_SPECTRAL_PULL_UP" in res.recommended_action

    def test_classify_plus_a_non_template_addition(self):
        # +1 bp peak next to major allele
        feat = MLSTRFeatureExtractor.extract_features(
            locus_name="TH01",
            peak_id="PlusA_Peak",
            peak_height=320.0,
            major_allele_height=1800.0,
            bp_position=181.0,  # +1 bp from 180.0
            major_allele_bp=180.0,
            analytical_threshold=50.0
        )
        res = FragsifierRandomForestClassifier.classify_peak(feat)
        
        assert res.predicted_class == ArtifactClassEnum.CLASS_PLUS_A_ARTIFACT
        assert res.is_true_allele_candidate is False
        assert "RECOMBINE_PLUS_A" in res.recommended_action

    def test_locus_multi_peak_pre_filter_report(self):
        # A locus with 1 major allele, 1 back-stutter, 1 pull-up, and 1 baseline drop-in
        major = MLSTRFeatureExtractor.extract_features(
            "SE33", "Allele_18", 2200.0, bp_position=280.0, major_allele_bp=280.0
        )
        stutter = MLSTRFeatureExtractor.extract_features(
            "SE33", "Stutter_17", 180.0, major_allele_height=2200.0, bp_position=276.0, major_allele_bp=280.0
        )
        pullup = MLSTRFeatureExtractor.extract_features(
            "SE33", "PullUp_Peak", 300.0, co_eluting_secondary_rfu=120.0, bp_position=290.0, major_allele_bp=280.0
        )
        noise = MLSTRFeatureExtractor.extract_features(
            "SE33", "Noise_Peak", 25.0, bp_position=260.0, major_allele_bp=280.0, analytical_threshold=50.0
        )
        
        rep = FragsifierRandomForestClassifier.filter_locus_peaks("SE33", [major, stutter, pullup, noise])
        
        assert rep.locus_name == "SE33"
        assert rep.total_raw_peaks == 4
        assert rep.true_alleles_retained == 1
        assert rep.artifacts_culled == 3
        assert rep.clean_candidate_alleles == ["Allele_18"]
        assert rep.mcmc_search_space_reduction_pct > 50.0
