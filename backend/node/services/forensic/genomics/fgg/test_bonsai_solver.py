"""
Unit Tests for Bonsai Composite Likelihood Pedigree Reconstruction Engine.
"""

import pytest
from backend.node.services.forensic.genomics.fgg.schemas import (
    SexEnum,
    KinshipClassificationResult,
    RelationshipCandidate,
    KinshipDegreeEnum
)
from backend.node.services.forensic.genomics.fgg.bonsai_solver import FGGBonsaiSolver


class TestFGGBonsaiSolver:
    """Tests multi-generational tree assembly and composite likelihood scoring."""

    def test_reconstruct_3gen_family(self):
        target_id = "TARGET_01"
        target_birth = 1990

        # Candidate 1: Full sibling (2600 cM)
        cand_sib = RelationshipCandidate(
            degree=KinshipDegreeEnum.DEGREE_1_FULL_SIBLING,
            relationship_label="Full Sibling",
            probability=0.98,
            expected_mean_cm=2600.0,
            typical_cm_range_min=2200.0,
            typical_cm_range_max=3400.0,
            description="Full sibling"
        )
        res_sib = KinshipClassificationResult(
            sample_a_id=target_id, sample_b_id="MATCH_SIB", raw_shared_cm=2600.0, adjusted_shared_cm=2600.0,
            longest_segment_cm=140.0, segment_count=40, endogamy_roh_score_a=0.0, endogamy_roh_score_b=0.0,
            endogamy_adjustment_applied_cm=0.0, top_candidate=cand_sib, all_candidates=[cand_sib],
            bivariate_morphology_note="Full sibling morphology", is_endogamy_suspected=False
        )

        # Candidate 2: 1st Cousin (860 cM)
        cand_1c = RelationshipCandidate(
            degree=KinshipDegreeEnum.DEGREE_3_FIRST_COUSIN,
            relationship_label="1st Cousin",
            probability=0.88,
            expected_mean_cm=860.0,
            typical_cm_range_min=450.0,
            typical_cm_range_max=1300.0,
            description="1st cousin"
        )
        res_1c = KinshipClassificationResult(
            sample_a_id=target_id, sample_b_id="MATCH_1C", raw_shared_cm=860.0, adjusted_shared_cm=860.0,
            longest_segment_cm=75.0, segment_count=18, endogamy_roh_score_a=0.0, endogamy_roh_score_b=0.0,
            endogamy_adjustment_applied_cm=0.0, top_candidate=cand_1c, all_candidates=[cand_1c],
            bivariate_morphology_note="1st cousin morphology", is_endogamy_suspected=False
        )

        tree = FGGBonsaiSolver.reconstruct_pedigree(
            target_id=target_id,
            target_birth_year=target_birth,
            target_sex=SexEnum.MALE,
            target_y_hap="R1b-M269",
            target_mt_hap="H1a",
            match_results=[res_sib, res_1c],
            mrca_clusters=[]
        )

        assert tree.target_sample_id == target_id
        assert len(tree.nodes) >= 6
        assert tree.generation_depth >= 2
        assert tree.composite_log_likelihood < 0.0 # Log likelihoods are <= 0
        assert "Pedigree DAG assembled" in tree.investigative_leads_summary
