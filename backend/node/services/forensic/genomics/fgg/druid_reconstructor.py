"""
DRUID (Deep Relatedness Utilizing Identity by Descent) Ancestor Reconstruction Engine.

Reconstructs ungenotyped ancestor chromosomal sharing profiles by pooling
sibling and avuncular match sets, reducing recombination noise by 1-2 generations.
"""

from typing import List, Dict, Tuple
from .schemas import IBDSegment, IBDStateEnum


class FGGDruidReconstructor:
    """Reconstructs ancestral shared IBD blocks via sibling/avuncular union pooling."""

    @classmethod
    def reconstruct_parental_shared_segments(
        cls,
        sibling_segment_lists: List[List[IBDSegment]]
    ) -> Tuple[List[IBDSegment], float, float]:
        """
        Takes list of IBD segment lists between target and multiple full siblings.
        Computes the chromosomal union of segments to approximate the ungenotyped parent's IBD profile.
        Returns: (union_segments, total_parental_cm, delta_cm_gain)
        """
        if not sibling_segment_lists:
            return ([], 0.0, 0.0)
        if len(sibling_segment_lists) == 1:
            segs = sibling_segment_lists[0]
            tot = sum(s.length_cm for s in segs)
            return (segs, round(tot, 4), 0.0)

        # Group all segments by chromosome
        by_chrom: Dict[str, List[IBDSegment]] = {}
        for seg_list in sibling_segment_lists:
            for seg in seg_list:
                by_chrom.setdefault(seg.chromosome, []).append(seg)

        union_segments: List[IBDSegment] = []
        for ch, segs in by_chrom.items():
            merged = cls._merge_chromosome_intervals(ch, segs)
            union_segments.extend(merged)

        total_parental_cm = sum(s.length_cm for s in union_segments)
        individual_max_cm = max(sum(s.length_cm for s in seg_list) for seg_list in sibling_segment_lists)
        delta_gain = max(0.0, total_parental_cm - individual_max_cm)

        return (union_segments, round(total_parental_cm, 4), round(delta_gain, 4))

    @staticmethod
    def _merge_chromosome_intervals(chromosome: str, segments: List[IBDSegment]) -> List[IBDSegment]:
        """Merges overlapping or contiguous IBD intervals on a single chromosome."""
        if not segments:
            return []

        # Sort by start_bp
        sorted_segs = sorted(segments, key=lambda s: s.start_bp)
        merged: List[IBDSegment] = []

        curr_start_bp = sorted_segs[0].start_bp
        curr_end_bp = sorted_segs[0].end_bp
        curr_start_cm = sorted_segs[0].start_cm
        curr_end_cm = sorted_segs[0].end_cm
        curr_snps = sorted_segs[0].snp_count

        for seg in sorted_segs[1:]:
            if seg.start_bp <= curr_end_bp + 500000:  # Within 500 kb / overlap
                curr_end_bp = max(curr_end_bp, seg.end_bp)
                curr_end_cm = max(curr_end_cm, seg.end_cm)
                curr_snps += seg.snp_count
            else:
                length_cm = round(max(0.0, curr_end_cm - curr_start_cm), 4)
                density = round(curr_snps / length_cm, 2) if length_cm > 0 else 0.0
                merged.append(IBDSegment(
                    chromosome=chromosome,
                    start_bp=curr_start_bp,
                    end_bp=curr_end_bp,
                    start_cm=curr_start_cm,
                    end_cm=curr_end_cm,
                    length_cm=length_cm,
                    snp_count=curr_snps,
                    density_snps_per_cm=density,
                    ibd_state=IBDStateEnum.IBD1
                ))
                curr_start_bp = seg.start_bp
                curr_end_bp = seg.end_bp
                curr_start_cm = seg.start_cm
                curr_end_cm = seg.end_cm
                curr_snps = seg.snp_count

        # Append last
        length_cm = round(max(0.0, curr_end_cm - curr_start_cm), 4)
        density = round(curr_snps / length_cm, 2) if length_cm > 0 else 0.0
        merged.append(IBDSegment(
            chromosome=chromosome,
            start_bp=curr_start_bp,
            end_bp=curr_end_bp,
            start_cm=curr_start_cm,
            end_cm=curr_end_cm,
            length_cm=length_cm,
            snp_count=curr_snps,
            density_snps_per_cm=density,
            ibd_state=IBDStateEnum.IBD1
        ))

        return merged
