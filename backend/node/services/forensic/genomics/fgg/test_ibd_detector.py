"""
Unit Tests for Phase-Free Windowed IBD Detector (IBIS Architecture).
"""

import pytest
from backend.node.services.forensic.genomics.fgg.schemas import (
    GenotypeStateEnum,
    BitwiseGenotypeBlock,
    ProfileQCReport,
    PlatformFormatEnum,
    IngestedFGGProfile,
    IBDStateEnum
)
from backend.node.services.forensic.genomics.fgg.bitwise_packer import BitwiseGenotypePacker
from backend.node.services.forensic.genomics.fgg.ibd_detector import FGGIBDDetector


def _generate_synthetic_profile(profile_id: str, chrom_states: dict) -> IngestedFGGProfile:
    blocks = {}
    total_snps = 0
    for ch, states in chrom_states.items():
        packed = BitwiseGenotypePacker.pack_states(states)
        n = len(states)
        # 1 SNP every 1000 bp
        positions = [100000 + i * 2000 for i in range(n)]
        blocks[ch] = BitwiseGenotypeBlock(
            chromosome=ch,
            snp_count=n,
            packed_bytes_hex=packed.hex(),
            positions_bp=positions,
            genetic_positions_cm=[],
            rsids=[f"rs_{ch}_{i}" for i in range(n)]
        )
        total_snps += n

    qc = ProfileQCReport(
        total_snps_evaluated=total_snps,
        called_snps=total_snps,
        missing_snps=0,
        call_rate_percentage=100.0,
        heterozygosity_rate_percentage=25.0,
        is_call_rate_valid=True,
        degradation_warning=False,
        contamination_warning=False,
        detected_platform=PlatformFormatEnum.ILLUMINA_GSA
    )
    return IngestedFGGProfile(
        profile_id=profile_id,
        source_filename=f"{profile_id}.txt",
        platform=PlatformFormatEnum.ILLUMINA_GSA,
        assembly_version="GRCh38",
        qc_report=qc,
        chromosome_blocks=blocks
    )


class TestFGGIBDDetector:
    """Tests IBD segment detection and 7 cM threshold filtering."""

    def test_parent_child_ibd1_sharing(self):
        # 5,000 SNPs on Chromosome 1: Parent (HOM_REF 0/0) vs Child (HET 0/1) -> Zero IBS0 opposite homozygotes
        parent_states = [GenotypeStateEnum.HOM_REF] * 5000
        child_states = [GenotypeStateEnum.HET] * 5000

        p_parent = _generate_synthetic_profile("PARENT", {"1": parent_states})
        p_child = _generate_synthetic_profile("CHILD", {"1": child_states})

        result = FGGIBDDetector.detect_pairwise_ibd(p_parent, p_child)
        assert result.segment_count >= 1
        assert result.total_shared_cm > 5.0
        assert result.cotterman_k1 > 0.0

    def test_sub_7cm_segment_culling(self):
        # Only 200 SNPs (~0.4 Mb, ~0.5 cM) -> Should be culled (EC-FGG-01: cutoff >= 7.0 cM and >= 500 SNPs)
        s1 = [GenotypeStateEnum.HOM_REF] * 200
        s2 = [GenotypeStateEnum.HET] * 200

        p1 = _generate_synthetic_profile("S1", {"1": s1})
        p2 = _generate_synthetic_profile("S2", {"1": s2})

        result = FGGIBDDetector.detect_pairwise_ibd(p1, p2)
        assert result.segment_count == 0
        assert result.total_shared_cm == 0.0

    def test_ibs0_interruption_splits_segments(self):
        # 1,000 shared, then 10 IBS0 opposite homozygotes, then 1,000 shared
        part1_a = [GenotypeStateEnum.HOM_REF] * 1000
        part1_b = [GenotypeStateEnum.HET] * 1000

        # IBS0 block (0/0 vs 1/1)
        ibs0_a = [GenotypeStateEnum.HOM_REF] * 10
        ibs0_b = [GenotypeStateEnum.HOM_ALT] * 10

        part2_a = [GenotypeStateEnum.HOM_REF] * 1000
        part2_b = [GenotypeStateEnum.HET] * 1000

        s_a = part1_a + ibs0_a + part2_a
        s_b = part1_b + ibs0_b + part2_b

        p_a = _generate_synthetic_profile("PA", {"1": s_a})
        p_b = _generate_synthetic_profile("PB", {"1": s_b})

        # With min_cm=1.0 and min_snps=500, should produce 2 distinct segments split by IBS0
        result = FGGIBDDetector.detect_pairwise_ibd(p_a, p_b, min_cm=1.0, min_snps=500)
        assert result.segment_count == 2
