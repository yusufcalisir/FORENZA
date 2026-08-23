"""
Unit Tests for MRCA Triangulation, DRUID Imputation, and Lineage Pruning.
"""

import pytest
from backend.node.services.forensic.genomics.fgg.schemas import (
    IBDSegment,
    IBDStateEnum,
    PedigreeNode,
    SexEnum
)
from backend.node.services.forensic.genomics.fgg.druid_reconstructor import FGGDruidReconstructor
from backend.node.services.forensic.genomics.fgg.mrca_triangulator import FGGMRCATriangulator


class TestFGGMRCATriangulator:
    """Tests MRCA cluster triangulation, DRUID pooling, and Y-STR / mtDNA branch pruning."""

    def test_druid_sibling_union_reconstruction(self):
        # Sibling 1 shares 10-50 Mb on Chr 1 (~45 cM)
        seg_sib1 = [IBDSegment(
            chromosome="1", start_bp=10000000, end_bp=50000000, start_cm=11.5, end_cm=57.5,
            length_cm=46.0, snp_count=2000, density_snps_per_cm=43.0, ibd_state=IBDStateEnum.IBD1
        )]
        # Sibling 2 shares 40-80 Mb on Chr 1 (~46 cM)
        seg_sib2 = [IBDSegment(
            chromosome="1", start_bp=40000000, end_bp=80000000, start_cm=46.0, end_cm=92.0,
            length_cm=46.0, snp_count=2000, density_snps_per_cm=43.0, ibd_state=IBDStateEnum.IBD1
        )]

        union_segs, total_cm, delta_gain = FGGDruidReconstructor.reconstruct_parental_shared_segments([seg_sib1, seg_sib2])
        # Merged segment should span 10 Mb to 80 Mb (~80.5 cM), yielding higher total cM than individual 46.0 cM
        assert len(union_segs) == 1
        assert union_segs[0].start_bp == 10000000
        assert union_segs[0].end_bp == 80000000
        assert total_cm > 46.0
        assert delta_gain > 0.0

    def test_mrca_triangulation_cluster(self):
        # Match 1 and Match 2 both share overlapping 20-60 Mb on Chr 1
        seg_m1 = [IBDSegment(
            chromosome="1", start_bp=20000000, end_bp=60000000, start_cm=23.0, end_cm=69.0,
            length_cm=46.0, snp_count=2000, density_snps_per_cm=43.0, ibd_state=IBDStateEnum.IBD1
        )]
        seg_m2 = [IBDSegment(
            chromosome="1", start_bp=30000000, end_bp=70000000, start_cm=34.5, end_cm=80.5,
            length_cm=46.0, snp_count=2000, density_snps_per_cm=43.0, ibd_state=IBDStateEnum.IBD1
        )]

        match_map = {"MATCH_1": seg_m1, "MATCH_2": seg_m2}
        clusters = FGGMRCATriangulator.triangulate_clusters(match_map)
        assert len(clusters) >= 1
        assert clusters[0].overlapping_chromosome == "1"
        assert "MATCH_1" in clusters[0].shared_matches_ids
        assert "MATCH_2" in clusters[0].shared_matches_ids
        assert clusters[0].overlap_length_cm > 30.0

    def test_uniparental_lineage_pruning_ec_fgg_04(self):
        # Target is R1b-M269, candidate is E1b1b (patrilineal clash)
        cand_male_clash = PedigreeNode(node_id="CAND_01", label="Candidate 1", sex=SexEnum.MALE, y_haplogroup="E1b1b")
        should_prune, reason = FGGMRCATriangulator.evaluate_uniparental_pruning(
            cand_male_clash, target_y_haplogroup="R1b-M269", target_mtdna_haplogroup="H1a"
        )
        assert should_prune is True
        assert "Patrilineal clash" in reason

        # Target is R1b-M269, candidate is R1b1a (compatible)
        cand_male_ok = PedigreeNode(node_id="CAND_02", label="Candidate 2", sex=SexEnum.MALE, y_haplogroup="R1b1a")
        should_prune_ok, reason_ok = FGGMRCATriangulator.evaluate_uniparental_pruning(
            cand_male_ok, target_y_haplogroup="R1b-M269", target_mtdna_haplogroup="H1a"
        )
        assert should_prune_ok is False
        assert "Lineage concordant" in reason_ok
