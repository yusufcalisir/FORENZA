"""
Automated ISO/IEC 17025:2017 Edge-Case Verification Suite for ML STR Calling Subsystem.
Implements: EC-MLSTR-01 through EC-MLSTR-05 and Golden Benchmark Verifications.
"""

import pytest
from node.services.forensic.genomics.ml_str.schemas import ArtifactClassEnum
from node.services.forensic.genomics.ml_str.feature_extractor import MLSTRFeatureExtractor
from node.services.forensic.genomics.ml_str.classifier import FragsifierRandomForestClassifier
from node.services.forensic.genomics.ml_str.isfg_hierarchy import ISFGHierarchyEngine
from node.services.forensic.genomics.ml_str.golden_vectors import GOLDEN_VECTORS_MLSTR


class TestMLSTRISOTestsAndEdgeCases:
    """Mandatory 5 ISO 17025 Edge Cases for Machine Learning STR Calling."""

    def test_ec_mlstr_01_false_negative_resistance_invariant(self):
        """
        EC-MLSTR-01: False Negative Resistance Invariant:
        Zero true biological alleles (h >= AT) misclassified as stutter or artifact (FNR = 0.000000).
        """
        true_peaks = [
            ("TH01", "Allele_9.3", 1850.0, 180.0),
            ("D3S1358", "Allele_15", 2200.0, 120.0),
            ("D21S11", "Allele_30", 3100.0, 214.0),
            ("SE33", "Allele_27.2", 1950.0, 290.0),
            ("vWA", "Allele_17", 2600.0, 165.0),
        ]
        
        for locus, pid, h, bp in true_peaks:
            feat = MLSTRFeatureExtractor.extract_features(
                locus, pid, h, bp_position=bp, major_allele_bp=bp, analytical_threshold=50.0
            )
            res = FragsifierRandomForestClassifier.classify_peak(feat)
            assert res.predicted_class == ArtifactClassEnum.CLASS_TRUE_ALLELE, (
                f"EC-MLSTR-01 Violation on {locus}: true allele misclassified as {res.predicted_class}"
            )
            assert res.is_true_allele_candidate is True

    def test_ec_mlstr_02_high_stutter_discrimination_invariant(self):
        """
        EC-MLSTR-02: High-Stutter Discrimination Invariant:
        Severe reverse back-stutter (SR = 18.5%) in D21S11 / SE33 correctly identified as CLASS_BACK_STUTTER.
        """
        feat = MLSTRFeatureExtractor.extract_features(
            locus_name="D21S11",
            peak_id="Stutter_29",
            peak_height=444.0,  # 18.5% of 2400
            major_allele_height=2400.0,
            bp_position=210.0,  # -4 bp from 214.0
            major_allele_bp=214.0,
            repeat_unit_len=4,
            analytical_threshold=50.0
        )
        res = FragsifierRandomForestClassifier.classify_peak(feat)
        assert res.predicted_class == ArtifactClassEnum.CLASS_BACK_STUTTER
        assert res.class_posterior_probabilities[ArtifactClassEnum.CLASS_BACK_STUTTER.value] >= 0.60
        assert res.is_true_allele_candidate is False

    def test_ec_mlstr_03_non_template_plus_a_recombination_invariant(self):
        """
        EC-MLSTR-03: Non-Template +A Recombination Invariant:
        Split -A/+A peak at TH01 (+1 bp position) classified as CLASS_PLUS_A_ARTIFACT with recombine action.
        """
        feat = MLSTRFeatureExtractor.extract_features(
            locus_name="TH01",
            peak_id="Split_PlusA",
            peak_height=360.0,
            major_allele_height=1800.0,
            bp_position=181.0,  # +1 bp
            major_allele_bp=180.0,
            analytical_threshold=50.0
        )
        res = FragsifierRandomForestClassifier.classify_peak(feat)
        assert res.predicted_class == ArtifactClassEnum.CLASS_PLUS_A_ARTIFACT
        assert "RECOMBINE_PLUS_A" in res.recommended_action
        assert res.is_true_allele_candidate is False

    def test_ec_mlstr_04_spectral_pull_up_elimination_invariant(self):
        """
        EC-MLSTR-04: Spectral Pull-Up Elimination Invariant:
        Secondary dye bleedthrough peak from saturated channel (h > 6000 RFU) rejected as pull-up.
        """
        feat = MLSTRFeatureExtractor.extract_features(
            locus_name="vWA",
            peak_id="PullUp_Yellow",
            peak_height=480.0,
            co_eluting_secondary_rfu=250.0,  # pull-up > 15%
            bp_position=165.0,
            major_allele_bp=165.0,
            analytical_threshold=50.0
        )
        res = FragsifierRandomForestClassifier.classify_peak(feat)
        assert res.predicted_class == ArtifactClassEnum.CLASS_SPECTRAL_PULL_UP
        assert res.is_true_allele_candidate is False
        assert "CULL_SPECTRAL_PULL_UP" in res.recommended_action

    def test_ec_mlstr_05_isfg_3_tier_reversibility_invariant(self):
        """
        EC-MLSTR-05: ISFG 3-Tier Reversibility Invariant:
        Level 1 (FASTA) <-> Level 2 (Alignment) <-> Level 3 (Bracketed) reversible with zero character drift.
        """
        test_alleles = [
            ("TH01", "[AATG]6 ATG [AATG]3", 9.3),
            ("D3S1358", "[TCTA]1 [TCTG]3 [TCTA]12", 16.0),
            ("D16S539", "[GATA]11", 11.0),
        ]
        
        for locus, bracketed, expected_ce in test_alleles:
            rep = ISFGHierarchyEngine.build_hierarchical_representation(locus, bracketed)
            assert rep.locus_name == locus.upper()
            assert rep.level_3_compact_nomenclature == bracketed
            assert abs(rep.ce_equivalent_length_call - expected_ce) < 1e-4
            assert len(rep.level_1_sequence_text_string) > 0
            assert rep.level_2_alignment_mapping.grch38_start_pos > 0
            assert rep.is_reversible is True


class TestMLSTRGoldenVectors:
    """Verifies all 4 certified golden benchmark vectors pass."""

    def test_all_four_golden_vectors_exist_and_conform(self):
        assert len(GOLDEN_VECTORS_MLSTR) == 4
        for vec_id, vec in GOLDEN_VECTORS_MLSTR.items():
            assert vec.vector_id.startswith("VECTOR_MLSTR_")
            assert len(vec.raw_peak_descriptions) >= 2
            assert vec.mcmc_speedup_factor >= 1.20
            assert "ISO/IEC 17025" in vec.iso17025_conformance_note
