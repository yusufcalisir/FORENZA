"""
Unit Tests for Runs of Homozygosity (ROH) and Endogamy Background Filter.
"""

import pytest
from backend.node.services.forensic.genomics.fgg.schemas import (
    GenotypeStateEnum,
    BitwiseGenotypeBlock,
    ProfileQCReport,
    PlatformFormatEnum,
    IngestedFGGProfile,
    PairwiseIBDResult
)
from backend.node.services.forensic.genomics.fgg.bitwise_packer import BitwiseGenotypePacker
from backend.node.services.forensic.genomics.fgg.endogamy_filter import FGGEndogamyFilter


def _create_roh_profile(profile_id: str, roh_fraction: float) -> IngestedFGGProfile:
    blocks = {}
    total_snps = 0
    # Simulate across autosomes 1 through 10
    chroms = [str(i) for i in range(1, 11)]
    for ch in chroms:
        n = 2000
        n_roh = int(n * roh_fraction)
        # ROH is pure homozygous calls (HOM_REF) with 0 HETs
        states = [GenotypeStateEnum.HOM_REF] * n_roh + [GenotypeStateEnum.HET if i % 4 == 0 else GenotypeStateEnum.HOM_REF for i in range(n - n_roh)]
        packed = BitwiseGenotypePacker.pack_states(states)
        # Span across 50 Mb per chromosome
        positions = [1000000 + i * 25000 for i in range(n)]
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
        heterozygosity_rate_percentage=15.0,
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


class TestFGGEndogamyFilter:
    """Tests ROH quantification and endogamy background cM adjustment."""

    def test_outbred_sample_f_roh_low(self):
        # Outbred sample with 0% long homozygous runs
        p_outbred = _create_roh_profile("OUTBRED", roh_fraction=0.0)
        f_roh = FGGEndogamyFilter.compute_individual_f_roh(p_outbred)
        assert f_roh < 0.015

    def test_endogamous_sample_f_roh_elevated(self):
        # Sample with 80% homozygous blocks on Chr 1 and Chr 2
        p_inbred = _create_roh_profile("INBRED", roh_fraction=0.80)
        f_roh = FGGEndogamyFilter.compute_individual_f_roh(p_inbred)
        assert f_roh >= FGGEndogamyFilter.ENDOGAMY_ROH_THRESHOLD

    def test_endogamy_ibd_adjustment(self):
        # Raw 300 cM across 12 fragmented segments (L_max = 12 cM) with high ROH
        mock_pair = PairwiseIBDResult(
            sample_a_id="A",
            sample_b_id="B",
            total_shared_cm=300.0,
            longest_segment_cm=12.0,
            segment_count=12,
            segments=[],
            cotterman_k0=0.90,
            cotterman_k1=0.10,
            cotterman_k2=0.0,
            kinship_phi=0.025,
            wright_r=0.05,
            king_phi=0.025,
            qualifying_segments_count=12
        )
        adj_cm, delta, is_suspected = FGGEndogamyFilter.adjust_endogamy_ibd(mock_pair, f_roh_a=0.06, f_roh_b=0.06)
        assert is_suspected is True
        assert delta > 50.0
        assert adj_cm < 250.0
