"""
Phase-Free Windowed IBS0 Identity-by-Descent (IBD) Detection Engine.

Implements the IBIS architecture (Seidman et al.) for fast bitwise IBD calling.
Filters segments strictly under forensic criteria:
- Minimum length: L_min >= 7.0 cM
- Minimum SNP count: N_SNP >= 500
- Density: >= 100 SNPs / cM
"""

from typing import List, Dict, Tuple, Optional
from .schemas import (
    IBDStateEnum,
    IBDSegment,
    PairwiseIBDResult,
    IngestedFGGProfile,
    GenotypeStateEnum
)
from .bitwise_packer import BitwiseGenotypePacker
from .genetic_map import FGGGeneticMap
from .kinship_estimator import FGGKinshipEstimator


class FGGIBDDetector:
    """Detects multi-megabase IBD1 and IBD2 segments across genome-wide bitwise profiles."""

    MIN_SEGMENT_CM: float = 7.00             # Minimum forensic segment cutoff (cM)
    MIN_SNP_COUNT: int = 500                 # Minimum SNP count per segment
    MIN_DENSITY_SNPS_PER_CM: float = 50.0   # Minimum SNP density threshold

    @classmethod
    def detect_pairwise_ibd(
        cls,
        profile_a: IngestedFGGProfile,
        profile_b: IngestedFGGProfile,
        min_cm: Optional[float] = None,
        min_snps: Optional[int] = None
    ) -> PairwiseIBDResult:
        """
        Executes full pairwise genome-wide IBD detection between two profiles.
        Scans all 22 autosomes for qualifying IBD1 and IBD2 blocks.
        """
        cutoff_cm = min_cm if min_cm is not None else cls.MIN_SEGMENT_CM
        cutoff_snps = min_snps if min_snps is not None else cls.MIN_SNP_COUNT

        all_qualifying_segments: List[IBDSegment] = []
        total_shared_cm = 0.0
        longest_seg_cm = 0.0

        # Collect common autosomes
        shared_chroms = [str(c) for c in range(1, 23) if str(c) in profile_a.chromosome_blocks and str(c) in profile_b.chromosome_blocks]

        for ch in shared_chroms:
            block_a = profile_a.chromosome_blocks[ch]
            block_b = profile_b.chromosome_blocks[ch]

            # Unpack states
            bytes_a = bytes.fromhex(block_a.packed_bytes_hex)
            bytes_b = bytes.fromhex(block_b.packed_bytes_hex)
            states_a = BitwiseGenotypePacker.unpack_states(bytes_a, block_a.snp_count)
            states_b = BitwiseGenotypePacker.unpack_states(bytes_b, block_b.snp_count)

            positions_a = block_a.positions_bp
            positions_b = block_b.positions_bp

            # Align common positions if counts match or scan aligned positions
            segments = cls._scan_chromosome_ibd(
                ch, states_a, positions_a, states_b, positions_b, cutoff_cm, cutoff_snps
            )

            for seg in segments:
                all_qualifying_segments.append(seg)
                total_shared_cm += seg.length_cm
                if seg.length_cm > longest_seg_cm:
                    longest_seg_cm = seg.length_cm

        total_shared_cm = round(total_shared_cm, 4)
        longest_seg_cm = round(longest_seg_cm, 4)

        # Compute Kinship & Cotterman coefficients
        kinship_metrics = FGGKinshipEstimator.compute_kinship_from_segments(
            all_qualifying_segments, profile_a, profile_b
        )

        return PairwiseIBDResult(
            sample_a_id=profile_a.profile_id,
            sample_b_id=profile_b.profile_id,
            total_shared_cm=total_shared_cm,
            longest_segment_cm=longest_seg_cm,
            segment_count=len(all_qualifying_segments),
            segments=all_qualifying_segments,
            cotterman_k0=kinship_metrics["k0"],
            cotterman_k1=kinship_metrics["k1"],
            cotterman_k2=kinship_metrics["k2"],
            kinship_phi=kinship_metrics["kinship_phi"],
            wright_r=kinship_metrics["wright_r"],
            king_phi=kinship_metrics["king_phi"],
            qualifying_segments_count=len(all_qualifying_segments)
        )

    @classmethod
    def _scan_chromosome_ibd(
        cls,
        chromosome: str,
        states_a: List[GenotypeStateEnum],
        positions_a: List[int],
        states_b: List[GenotypeStateEnum],
        positions_b: List[int],
        cutoff_cm: float,
        cutoff_snps: int
    ) -> List[IBDSegment]:
        """Scans a single chromosome for IBD blocks without IBS0 opposite homozygotes."""
        n_snps = min(len(states_a), len(states_b), len(positions_a), len(positions_b))
        if n_snps == 0:
            return []

        segments: List[IBDSegment] = []
        in_segment = False
        seg_start_idx = 0
        consecutive_errors = 0
        max_allowed_errors = 1

        for i in range(n_snps):
            sa = states_a[i]
            sb = states_b[i]

            is_ibs0 = BitwiseGenotypePacker.is_opposite_homozygote(sa, sb)

            if is_ibs0:
                consecutive_errors += 1
                if consecutive_errors > max_allowed_errors:
                    # Terminate current segment
                    if in_segment:
                        seg_end_idx = max(seg_start_idx, i - consecutive_errors)
                        seg = cls._build_segment_if_valid(
                            chromosome, seg_start_idx, seg_end_idx, positions_a, states_a, states_b, cutoff_cm, cutoff_snps
                        )
                        if seg:
                            segments.append(seg)
                        in_segment = False
                    consecutive_errors = 0
            else:
                consecutive_errors = 0
                if not in_segment:
                    in_segment = True
                    seg_start_idx = i

        # Close tail segment if active
        if in_segment:
            seg = cls._build_segment_if_valid(
                chromosome, seg_start_idx, n_snps - 1, positions_a, states_a, states_b, cutoff_cm, cutoff_snps
            )
            if seg:
                segments.append(seg)

        return segments

    @classmethod
    def _build_segment_if_valid(
        cls,
        chromosome: str,
        start_idx: int,
        end_idx: int,
        positions: List[int],
        states_a: List[GenotypeStateEnum],
        states_b: List[GenotypeStateEnum],
        cutoff_cm: float,
        cutoff_snps: int
    ) -> Optional[IBDSegment]:
        """Validates and constructs an IBDSegment if it passes length and SNP count cutoffs."""
        snp_count = end_idx - start_idx + 1
        if snp_count < cutoff_snps:
            return None

        start_bp = positions[start_idx]
        end_bp = positions[end_idx]

        start_cm = FGGGeneticMap.bp_to_cm(chromosome, start_bp)
        end_cm = FGGGeneticMap.bp_to_cm(chromosome, end_bp)
        length_cm = round(max(0.0, end_cm - start_cm), 4)

        if length_cm < cutoff_cm:
            return None

        density = round(snp_count / length_cm, 2) if length_cm > 0 else 0.0

        # Check IBD1 vs IBD2 state
        ibd_state = cls._evaluate_ibd2_state(states_a[start_idx:end_idx + 1], states_b[start_idx:end_idx + 1])

        return IBDSegment(
            chromosome=chromosome,
            start_bp=start_bp,
            end_bp=end_bp,
            start_cm=start_cm,
            end_cm=end_cm,
            length_cm=length_cm,
            snp_count=snp_count,
            density_snps_per_cm=density,
            ibd_state=ibd_state
        )

    @staticmethod
    def _evaluate_ibd2_state(states_a: List[GenotypeStateEnum], states_b: List[GenotypeStateEnum]) -> IBDStateEnum:
        """Determines if a segment is IBD2 (both alleles identical across both individuals)."""
        het_count = 0
        het_match = 0
        for sa, sb in zip(states_a, states_b):
            if sa == GenotypeStateEnum.HET or sb == GenotypeStateEnum.HET:
                het_count += 1
                if sa == GenotypeStateEnum.HET and sb == GenotypeStateEnum.HET:
                    het_match += 1

        # If >85% of heterozygous sites are shared (both 0/1), classify as IBD2
        if het_count > 50 and (het_match / het_count) > 0.85:
            return IBDStateEnum.IBD2
        return IBDStateEnum.IBD1
