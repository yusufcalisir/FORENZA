"""
Unit Tests for Cotterman Probabilities, Wright r, and KING-Robust Estimator.
"""

import pytest
from backend.node.services.forensic.genomics.fgg.schemas import (
    IBDSegment,
    IBDStateEnum,
    PlatformFormatEnum,
    GenotypeStateEnum,
    BitwiseGenotypeBlock,
    ProfileQCReport,
    IngestedFGGProfile
)
from backend.node.services.forensic.genomics.fgg.bitwise_packer import BitwiseGenotypePacker
from backend.node.services.forensic.genomics.fgg.kinship_estimator import FGGKinshipEstimator


def _create_mock_profile(profile_id: str, states_by_chrom: dict) -> IngestedFGGProfile:
    chrom_blocks = {}
    total_snps = 0
    all_states = []
    for ch, states in states_by_chrom.items():
        packed = BitwiseGenotypePacker.pack_states(states)
        chrom_blocks[ch] = BitwiseGenotypeBlock(
            chromosome=ch,
            snp_count=len(states),
            packed_bytes_hex=packed.hex(),
            positions_bp=[i * 1000 for i in range(len(states))],
            rsids=[f"rs_{ch}_{i}" for i in range(len(states))]
        )
        total_snps += len(states)
        all_states.extend(states)

    qc = ProfileQCReport(
        total_snps_evaluated=total_snps,
        called_snps=total_snps,
        missing_snps=0,
        call_rate_percentage=100.0,
        heterozygosity_rate_percentage=20.0,
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
        chromosome_blocks=chrom_blocks
    )


class TestFGGKinshipEstimator:
    """Tests Cotterman, Wright, and KING-robust estimators."""

    def test_cotterman_simplex_normalization(self):
        # 1000 cM IBD1, 500 cM IBD2
        seg1 = IBDSegment(
            chromosome="1", start_bp=1000, end_bp=100000, start_cm=10.0, end_cm=1010.0, length_cm=1000.0,
            snp_count=5000, density_snps_per_cm=5.0, ibd_state=IBDStateEnum.IBD1
        )
        seg2 = IBDSegment(
            chromosome="2", start_bp=1000, end_bp=100000, start_cm=10.0, end_cm=510.0, length_cm=500.0,
            snp_count=2500, density_snps_per_cm=5.0, ibd_state=IBDStateEnum.IBD2
        )
        p1 = _create_mock_profile("S1", {"1": [GenotypeStateEnum.HET] * 100})
        p2 = _create_mock_profile("S2", {"1": [GenotypeStateEnum.HET] * 100})

        metrics = FGGKinshipEstimator.compute_kinship_from_segments([seg1, seg2], p1, p2)
        assert abs((metrics["k0"] + metrics["k1"] + metrics["k2"]) - 1.0) < 1e-5
        assert metrics["kinship_phi"] == round(0.5 * metrics["k2"] + 0.25 * metrics["k1"], 6)
        assert metrics["wright_r"] == round(metrics["k2"] + 0.5 * metrics["k1"], 6)

    def test_king_robust_identical_twins(self):
        # Identical genotypes across all loci -> phi_hat ~ 0.50
        states = [GenotypeStateEnum.HOM_REF, GenotypeStateEnum.HET, GenotypeStateEnum.HOM_ALT] * 300
        p1 = _create_mock_profile("TWIN_1", {"1": states, "2": states})
        p2 = _create_mock_profile("TWIN_2", {"1": states, "2": states})

        phi_hat = FGGKinshipEstimator.compute_king_robust(p1, p2)
        assert phi_hat == 0.50

    def test_king_robust_unrelated_individuals(self):
        # Opposite homozygotes and random heterozygosity -> phi_hat < 0.02
        states1 = [GenotypeStateEnum.HOM_REF] * 500 + [GenotypeStateEnum.HET] * 100
        states2 = [GenotypeStateEnum.HOM_ALT] * 500 + [GenotypeStateEnum.HET] * 100
        p1 = _create_mock_profile("UNREL_1", {"1": states1})
        p2 = _create_mock_profile("UNREL_2", {"1": states2})

        phi_hat = FGGKinshipEstimator.compute_king_robust(p1, p2)
        assert phi_hat <= 0.0
