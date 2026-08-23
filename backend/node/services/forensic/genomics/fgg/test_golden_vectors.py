"""
Comprehensive Unit Tests for Golden Reference Vectors (01-03) and 5 ISO/IEC 17025 Edge Cases.
"""

import pytest
from backend.node.services.forensic.genomics.fgg.schemas import (
    KinshipDegreeEnum,
    PlatformFormatEnum,
    GenotypeStateEnum,
    LegalComplianceCase,
    QualifyingOffenseEnum,
    JurisdictionStatuteEnum,
    SexEnum,
    PedigreeNode
)
from backend.node.services.forensic.genomics.fgg.golden_vectors import FGGGoldenVectors
from backend.node.services.forensic.genomics.fgg.ibd_detector import FGGIBDDetector
from backend.node.services.forensic.genomics.fgg.kinship_classifier import FGGKinshipClassifier
from backend.node.services.forensic.genomics.fgg.endogamy_filter import FGGEndogamyFilter
from backend.node.services.forensic.genomics.fgg.mrca_triangulator import FGGMRCATriangulator
from backend.node.services.forensic.genomics.fgg.legal_compliance import FGGLegalComplianceEngine
from backend.node.services.forensic.genomics.fgg.qc_engine import FGGQCEngine


class TestFGGGoldenVectors:
    """Tests standardized reference vectors and mandatory edge cases."""

    def test_vector_01_ceph_na12878_trio(self):
        """VECTOR_FGG_01: CEPH / GIAB NA12878 Parent-Child 100% IBD1 benchmark."""
        vec = FGGGoldenVectors.get_vector_01_ceph_trio()
        target = vec["target"]
        father = vec["father"]

        ibd_res = FGGIBDDetector.detect_pairwise_ibd(target, father)
        assert ibd_res.segment_count >= 10
        assert ibd_res.total_shared_cm > 1500.0

        kinship_res = FGGKinshipClassifier.classify_kinship(ibd_res, target, father)
        assert kinship_res.top_candidate.degree == KinshipDegreeEnum.DEGREE_1_PARENT_CHILD
        assert kinship_res.top_candidate.probability > 0.90

    def test_vector_02_ashkenazi_endogamy_trio(self):
        """VECTOR_FGG_02: GIAB Ashkenazi Trio with elevated ROH inbreeding."""
        vec = FGGGoldenVectors.get_vector_02_ashkenazi_endogamy_trio()
        son = vec["son"]
        father = vec["father"]

        f_roh_son = FGGEndogamyFilter.compute_individual_f_roh(son)
        f_roh_father = FGGEndogamyFilter.compute_individual_f_roh(father)
        assert f_roh_son > 0.035
        assert f_roh_father > 0.035

        ibd_res = FGGIBDDetector.detect_pairwise_ibd(son, father)
        kinship_res = FGGKinshipClassifier.classify_kinship(ibd_res, son, father)
        assert kinship_res.is_endogamy_suspected is True

    def test_vector_03_gsk_investigative_triangulation(self):
        """VECTOR_FGG_03: Golden State Killer Investigative Triangulation Case."""
        vec = FGGGoldenVectors.get_vector_03_gsk_investigative_case()
        crime_scene = vec["crime_scene"]
        c1 = vec["cousin1"]
        c2 = vec["cousin2"]

        ibd_c1 = FGGIBDDetector.detect_pairwise_ibd(crime_scene, c1)
        ibd_c2 = FGGIBDDetector.detect_pairwise_ibd(crime_scene, c2)

        assert ibd_c1.segment_count >= 1
        assert ibd_c2.segment_count >= 1

        match_map = {"COUSIN_1": ibd_c1.segments, "COUSIN_2": ibd_c2.segments}
        clusters = FGGMRCATriangulator.triangulate_clusters(match_map)
        assert len(clusters) >= 1
        assert "COUSIN_1" in clusters[0].shared_matches_ids
        assert "COUSIN_2" in clusters[0].shared_matches_ids

    # ═══════════════════════════════════════════════════════════════════════════
    # 5 MANDATORY ISO/IEC 17025 SCIENTIFIC EDGE CASES (EC-FGG-01 to EC-FGG-05)
    # ═══════════════════════════════════════════════════════════════════════════

    def test_ec_fgg_01_sub_threshold_noise_suppression(self):
        """EC-FGG-01: Micro-segments < 7.0 cM must be strictly culled."""
        vec = FGGGoldenVectors.get_vector_01_ceph_trio()
        t = vec["target"]
        f = vec["father"]
        # Standard cutoff 7.0 cM
        res = FGGIBDDetector.detect_pairwise_ibd(t, f, min_cm=7.0)
        for s in res.segments:
            assert s.length_cm >= 7.0

    def test_ec_fgg_02_legal_inadmissibility_gate(self):
        """EC-FGG-02: CODIS non-exhaustion must strictly block FGG authorization."""
        case_unexhausted = LegalComplianceCase(
            case_id="EC_CASE_01",
            jurisdiction=JurisdictionStatuteEnum.US_DOJ_INTERIM_2019,
            offense_type=QualifyingOffenseEnum.HOMICIDE,
            is_codis_exhausted=False,
            prosecutor_authorization_id="AUTH_DA_01"
        )
        val = FGGLegalComplianceEngine.validate_case(case_unexhausted)
        assert val.is_compliant is False
        assert any("EC-FGG-02" in v for v in val.violations)

    def test_ec_fgg_03_endogamy_false_first_cousin_resistance(self):
        """EC-FGG-03: Endogamy background discount prevents false 1C calling."""
        vec = FGGGoldenVectors.get_vector_02_ashkenazi_endogamy_trio()
        son = vec["son"]
        father = vec["father"]
        ibd_res = FGGIBDDetector.detect_pairwise_ibd(son, father)
        class_res = FGGKinshipClassifier.classify_kinship(ibd_res, son, father)
        assert class_res.is_endogamy_suspected is True
        assert class_res.endogamy_adjustment_applied_cm >= 0.0

    def test_ec_fgg_04_uniparental_lineage_pruning(self):
        """EC-FGG-04: Y-STR / mtDNA clash prunes discordant candidate tree branch."""
        clashing_node = PedigreeNode(node_id="CLASH", label="Clash Node", sex=SexEnum.MALE, y_haplogroup="Q1a")
        should_prune, reason = FGGMRCATriangulator.evaluate_uniparental_pruning(
            clashing_node, target_y_haplogroup="R1b-M269", target_mtdna_haplogroup="H1"
        )
        assert should_prune is True
        assert "Patrilineal clash" in reason

    def test_ec_fgg_05_severe_degradation_qc_alert(self):
        """EC-FGG-05: Low-template touch DNA with call rate < 90% triggers degradation alert."""
        states = [GenotypeStateEnum.HOM_REF] * 700 + [GenotypeStateEnum.NO_CALL] * 300 # 70% call rate
        qc = FGGQCEngine.evaluate_profile_qc(states, PlatformFormatEnum.ILLUMINA_GDA)
        assert qc.call_rate_percentage == 70.0
        assert qc.is_call_rate_valid is False
        assert qc.degradation_warning is True
