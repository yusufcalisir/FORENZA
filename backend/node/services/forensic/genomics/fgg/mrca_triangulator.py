"""
MRCA (Most Recent Common Ancestor) Cluster Triangulator & Uniparental Pruning Engine.

Triangulates overlapping IBD chromosomal segments across collateral matches
and integrates Y-STR / mtDNA haplogroup constraints to prune incompatible branches.
"""

from typing import List, Dict, Tuple, Optional
from .schemas import MRCACluster, IBDSegment, PedigreeNode


class FGGMRCATriangulator:
    """Identifies overlapping IBD blocks and prunes discordant uniparental lineages."""

    @classmethod
    def triangulate_clusters(
        cls,
        match_segments: Dict[str, List[IBDSegment]],
        target_y_haplogroup: Optional[str] = None,
        target_mtdna_haplogroup: Optional[str] = None
    ) -> List[MRCACluster]:
        """
        Groups collateral database matches that share overlapping IBD regions with the target.
        Returns triangulated MRCA clusters.
        """
        # Map matches by chromosome
        by_chrom: Dict[str, List[Tuple[str, IBDSegment]]] = {}
        for match_id, segs in match_segments.items():
            for s in segs:
                by_chrom.setdefault(s.chromosome, []).append((match_id, s))

        clusters: List[MRCACluster] = []
        cluster_idx = 1

        for ch, match_seg_pairs in by_chrom.items():
            if len(match_seg_pairs) < 2:
                continue

            # Check for overlaps between pairs of matches
            n = len(match_seg_pairs)
            for i in range(n):
                m1_id, s1 = match_seg_pairs[i]
                overlapping_matches = [m1_id]
                ov_start = s1.start_bp
                ov_end = s1.end_bp
                ov_start_cm = s1.start_cm
                ov_end_cm = s1.end_cm

                for j in range(i + 1, n):
                    m2_id, s2 = match_seg_pairs[j]
                    if m2_id in overlapping_matches:
                        continue

                    # Overlap condition
                    if max(s1.start_bp, s2.start_bp) < min(s1.end_bp, s2.end_bp):
                        overlapping_matches.append(m2_id)
                        ov_start = max(ov_start, s2.start_bp)
                        ov_end = min(ov_end, s2.end_bp)
                        ov_start_cm = max(ov_start_cm, s2.start_cm)
                        ov_end_cm = min(ov_end_cm, s2.end_cm)

                if len(overlapping_matches) >= 2:
                    overlap_len_cm = round(max(0.0, ov_end_cm - ov_start_cm), 4)
                    if overlap_len_cm >= 5.0: # Meaningful overlap
                        # Estimate generation depth based on overlap length
                        # Longer overlap -> closer generation (e.g. 40 cM -> 2G, 10 cM -> 4G)
                        if overlap_len_cm >= 30.0:
                            gen_depth = 2  # Grandparents / 1C
                        elif overlap_len_cm >= 15.0:
                            gen_depth = 3  # Great-Grandparents / 2C
                        elif overlap_len_cm >= 7.0:
                            gen_depth = 4  # 2G-Grandparents / 3C
                        else:
                            gen_depth = 5  # 3G-Grandparents / 4C

                        cid = f"MRCA_CLUSTER_{cluster_idx:02d}"
                        clusters.append(MRCACluster(
                            cluster_id=cid,
                            mrca_couple_label=f"MRCA Couple {cluster_idx} (Chr {ch}: {ov_start//1000000}M-{ov_end//1000000}M)",
                            shared_matches_ids=overlapping_matches,
                            overlapping_chromosome=ch,
                            start_bp=ov_start,
                            end_bp=ov_end,
                            overlap_length_cm=overlap_len_cm,
                            estimated_generation_depth=gen_depth,
                            uniparental_lineage_status="CONCORDANT"
                        ))
                        cluster_idx += 1

        return clusters

    @classmethod
    def evaluate_uniparental_pruning(
        cls,
        candidate_node: PedigreeNode,
        target_y_haplogroup: Optional[str],
        target_mtdna_haplogroup: Optional[str]
    ) -> Tuple[bool, str]:
        """
        Evaluates whether a candidate branch should be pruned due to Y-STR or mtDNA haplogroup clash.
        Returns: (should_prune, reason)
        """
        # Paternal check (Y chromosome)
        if target_y_haplogroup and candidate_node.y_haplogroup:
            if candidate_node.sex == "MALE" and not cls._is_haplogroup_compatible(target_y_haplogroup, candidate_node.y_haplogroup):
                return (True, f"Patrilineal clash: Target ({target_y_haplogroup}) vs Candidate ({candidate_node.y_haplogroup})")

        # Maternal check (mtDNA)
        if target_mtdna_haplogroup and candidate_node.mtdna_haplogroup:
            if not cls._is_haplogroup_compatible(target_mtdna_haplogroup, candidate_node.mtdna_haplogroup):
                return (True, f"Matrilineal clash: Target ({target_mtdna_haplogroup}) vs Candidate ({candidate_node.mtdna_haplogroup})")

        return (False, "Lineage concordant")

    @staticmethod
    def _is_haplogroup_compatible(hap1: str, hap2: str) -> bool:
        """Checks if two haplogroup strings share common root clade (e.g. R1b vs R1b1a)."""
        h1 = hap1.strip().upper()
        h2 = hap2.strip().upper()
        if h1 == h2:
            return True
        if h1.startswith(h2) or h2.startswith(h1):
            return True
        # First major clade letter must match (e.g. 'R' vs 'R', 'H' vs 'H')
        return h1[0] == h2[0] if h1 and h2 else True
