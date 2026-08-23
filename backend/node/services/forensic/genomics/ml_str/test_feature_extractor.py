"""
Unit Tests for FORENZA 24-Dimensional ML Feature Extractor (Phase 1).
"""

import pytest
from node.services.forensic.genomics.ml_str.feature_extractor import MLSTRFeatureExtractor


class TestMLSTRFeatureExtractor:
    """Tests feature extraction across morphological, stutter, entropy and mixture dimensions."""

    def test_shannon_entropy_calculation(self):
        # Mononucleotide repeat AAAAA... -> minimum entropy 0.0
        assert MLSTRFeatureExtractor.calculate_shannon_entropy("AAAAAAAAAAAA") == 0.0
        
        # Equal distribution of A, C, G, T -> maximum entropy 2.0
        assert MLSTRFeatureExtractor.calculate_shannon_entropy("ACGTACGTACGT") == 2.0
        
        # Complex tetranucleotide repeat core e.g. D3S1358 [TCTA]n [TCTG]m
        ent = MLSTRFeatureExtractor.calculate_shannon_entropy("TCTATCTATCTATCTGTCTGTCTATCTA")
        assert 1.40 <= ent <= 1.95

    def test_homopolymer_and_gc_fraction(self):
        seq = "TTTTTTTGCGCAAA"
        assert MLSTRFeatureExtractor.calculate_longest_homopolymer(seq) == 7
        assert MLSTRFeatureExtractor.calculate_gc_fraction(seq) == round(4 / 14, 4)

    def test_assemble_24d_feature_vector(self):
        feat = MLSTRFeatureExtractor.extract_features(
            locus_name="TH01",
            peak_id="Allele_9.3",
            peak_height=1850.0,
            peak_area=1968.4,
            fwhm=1.0,
            bp_position=180.0,
            major_allele_bp=180.0,
            repeat_unit_len=4,
            sequence_string="[AATG]6 ATG [AATG]3",
            analytical_threshold=50.0
        )
        
        assert feat.locus_name == "TH01"
        assert feat.peak_identifier == "Allele_9.3"
        assert len(feat.vector) == 24
        assert feat.morphology.peak_height == 1850.0
        assert feat.stutter.relative_bp_delta == 0.0
        assert feat.mixture.analytical_threshold_margin == (1850.0 - 50.0) / 50.0
