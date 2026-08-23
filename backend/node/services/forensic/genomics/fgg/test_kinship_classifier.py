"""
Unit Tests for Probabilistic Kinship Degree Classifier.
"""

import pytest
from backend.node.services.forensic.genomics.fgg.schemas import (
    KinshipDegreeEnum,
    PairwiseIBDResult,
    GenotypeStateEnum,
    BitwiseGenotypeBlock,
    ProfileQCReport,
    PlatformFormatEnum,
    IngestedFGGProfile
)
from backend.node.services.forensic.genomics.fgg.bitwise_packer import BitwiseGenotypePacker
from backend.node.services.forensic.genomics.fgg.kinship_classifier import FGGKinshipClassifier


def _create_simple_profile(pid: str) -> IngestedFGGProfile:
    # Minimal profile for testing
    states = [GenotypeStateEnum.HOM_REF if i % 2 == 0 else GenotypeStateEnum.HET for i in range(1000)]
    packed = BitwiseGenotypePacker.pack_states(states)
    blocks = {
        "1": BitwiseGenotypeBlock(
            chromosome="1", snp_count=1000, packed_bytes_hex=packed.hex(),
            positions_bp=[1000 + i * 2000 for i in range(1000)], rsids=[f"rs_{i}" for i in range(1000)]
        )
    }
    qc = ProfileQCReport(
        total_snps_evaluated=1000, called_snps=1000, missing_snps=0,
        call_rate_percentage=100.0, heterozygosity_rate_percentage=50.0,
        is_call_rate_valid=True, degradation_warning=False, contamination_warning=False,
        detected_platform=PlatformFormatEnum.ILLUMINA_GSA
    )
    return IngestedFGGProfile(
        profile_id=pid, source_filename=f"{pid}.txt", platform=PlatformFormatEnum.ILLUMINA_GSA,
        assembly_version="GRCh38", qc_report=qc, chromosome_blocks=blocks
    )


class TestFGGKinshipClassifier:
    """Tests relationship degree classification and posterior probability normalization."""

    def test_classify_parent_child(self):
        # 3450 cM, 100% IBD1 (k1=1.0, k2=0.0) -> DEGREE_1_PARENT_CHILD
        pair = PairwiseIBDResult(
            sample_a_id="P1", sample_b_id="P2", total_shared_cm=3450.0, longest_segment_cm=280.0,
            segment_count=22, segments=[], cotterman_k0=0.0, cotterman_k1=1.0, cotterman_k2=0.0,
            kinship_phi=0.25, wright_r=0.50, king_phi=0.25, qualifying_segments_count=22
        )
        p1 = _create_simple_profile("P1")
        p2 = _create_simple_profile("P2")

        res = FGGKinshipClassifier.classify_kinship(pair, p1, p2)
        assert res.top_candidate.degree == KinshipDegreeEnum.DEGREE_1_PARENT_CHILD
        assert res.top_candidate.probability > 0.90
        # Simplex check: sum of candidate probabilities == 1.0
        assert abs(sum(c.probability for c in res.all_candidates) - 1.0) < 1e-4

    def test_classify_full_sibling(self):
        # 2600 cM, mixed IBD1/IBD2 (k1=0.50, k2=0.25) -> DEGREE_1_FULL_SIBLING
        pair = PairwiseIBDResult(
            sample_a_id="S1", sample_b_id="S2", total_shared_cm=2600.0, longest_segment_cm=140.0,
            segment_count=45, segments=[], cotterman_k0=0.25, cotterman_k1=0.50, cotterman_k2=0.25,
            kinship_phi=0.25, wright_r=0.50, king_phi=0.25, qualifying_segments_count=45
        )
        p1 = _create_simple_profile("S1")
        p2 = _create_simple_profile("S2")

        res = FGGKinshipClassifier.classify_kinship(pair, p1, p2)
        assert res.top_candidate.degree == KinshipDegreeEnum.DEGREE_1_FULL_SIBLING
        assert res.top_candidate.probability > 0.90

    def test_classify_first_cousin(self):
        # 860 cM -> DEGREE_3_FIRST_COUSIN
        pair = PairwiseIBDResult(
            sample_a_id="C1", sample_b_id="C2", total_shared_cm=860.0, longest_segment_cm=75.0,
            segment_count=18, segments=[], cotterman_k0=0.75, cotterman_k1=0.25, cotterman_k2=0.0,
            kinship_phi=0.0625, wright_r=0.125, king_phi=0.0625, qualifying_segments_count=18
        )
        p1 = _create_simple_profile("C1")
        p2 = _create_simple_profile("C2")

        res = FGGKinshipClassifier.classify_kinship(pair, p1, p2)
        assert res.top_candidate.degree == KinshipDegreeEnum.DEGREE_3_FIRST_COUSIN
        assert res.top_candidate.probability > 0.80

    def test_classify_second_cousin(self):
        # 220 cM -> DEGREE_5_SECOND_COUSIN
        pair = PairwiseIBDResult(
            sample_a_id="2C_1", sample_b_id="2C_2", total_shared_cm=220.0, longest_segment_cm=44.0,
            segment_count=9, segments=[], cotterman_k0=0.9375, cotterman_k1=0.0625, cotterman_k2=0.0,
            kinship_phi=0.0156, wright_r=0.0312, king_phi=0.0156, qualifying_segments_count=9
        )
        p1 = _create_simple_profile("2C_1")
        p2 = _create_simple_profile("2C_2")

        res = FGGKinshipClassifier.classify_kinship(pair, p1, p2)
        assert res.top_candidate.degree == KinshipDegreeEnum.DEGREE_5_SECOND_COUSIN
        assert res.top_candidate.probability > 0.60
