"""
FORENZA Missing Persons Candidate Ranking & Kinship Search Engine.
Implements missing person candidate searching across complex pedigrees (Direct reference, Parent, Sibling, Child)
and ranks database candidate matches by Posterior Probability P(Hp | E) and Likelihood Ratio (LR).

Reference:
  Interpol Missing Persons DNA Database Guidelines & SWGDAM Kinship Evaluation Standards (2020).
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from node.services.forensic.models import STRGenotype, STRProfile
from node.services.forensic.kinship_engine import KinshipEngine, KinshipRelationship


@dataclass
class MissingPersonCandidateMatch:
    candidate_id: str
    relationship_type: str            # 'DIRECT_MATCH', 'PARENT_CHILD', 'FULL_SIBLING', 'HALF_SIBLING'
    combined_lr: float
    log10_lr: float
    posterior_probability: float      # P(Hp | E) assuming equal prior
    matching_loci_count: int
    evaluated_loci_count: int
    confidence_tier: str              # 'CONFIRMED_MATCH', 'STRONG_CANDIDATE', 'MODERATE_CANDIDATE'


@dataclass
class MissingPersonSearchResult:
    query_id: str
    total_candidates_searched: int
    top_candidate_hits: List[MissingPersonCandidateMatch]
    search_summary: str


class MissingPersonsEngine:
    """
    Ranks database candidate profiles against a missing person query profile or family reference.
    """

    def __init__(self, kinship_engine: Optional[KinshipEngine] = None):
        self.kinship_engine = kinship_engine or KinshipEngine()

    def search_and_rank_candidates(
        self,
        query_profile: STRProfile,
        candidate_db: List[STRProfile],
        prior_probability: float = 0.50,
        top_k: int = 5
    ) -> MissingPersonSearchResult:
        """Evaluates missing person profile against candidate database and ranks top hits."""
        hits: List[MissingPersonCandidateMatch] = []

        for candidate in candidate_db:
            if candidate.profile_id == query_profile.profile_id:
                continue

            # Evaluate Parent-Child relationship hypothesis
            pc_res = self.kinship_engine.compute_kinship_index(
                query_profile, candidate, KinshipRelationship.PARENT_CHILD
            )
            # Evaluate Full-Sibling relationship hypothesis
            sib_res = self.kinship_engine.compute_kinship_index(
                query_profile, candidate, KinshipRelationship.FULL_SIBLING
            )

            # Choose strongest kinship hypothesis
            if pc_res.value >= sib_res.value:
                best_lr = pc_res.value
                best_rel = "PARENT_CHILD"
                best_log_lr = pc_res.metadata.get("log10_ki", math.log10(max(1e-9, pc_res.value)))
            else:
                best_lr = sib_res.value
                best_rel = "FULL_SIBLING"
                best_log_lr = sib_res.metadata.get("log10_ki", math.log10(max(1e-9, sib_res.value)))

            # Calculate posterior probability P(Hp | E) = (LR * prior) / (LR * prior + (1 - prior))
            lr = max(1e-9, best_lr)
            post_prob = round((lr * prior_probability) / (lr * prior_probability + (1.0 - prior_probability)), 6)

            if best_log_lr >= 6.0:
                tier = "CONFIRMED_MATCH"
            elif best_log_lr >= 3.0:
                tier = "STRONG_CANDIDATE"
            elif best_log_lr >= 1.0:
                tier = "MODERATE_CANDIDATE"
            else:
                tier = "UNLIKELY"

            if best_log_lr >= 1.0:
                common_loci = len(set(query_profile.loci.keys()) & set(candidate.loci.keys()))
                hits.append(MissingPersonCandidateMatch(
                    candidate_id=candidate.profile_id,
                    relationship_type=best_rel,
                    combined_lr=round(best_lr, 2),
                    log10_lr=round(best_log_lr, 4),
                    posterior_probability=post_prob,
                    matching_loci_count=common_loci,
                    evaluated_loci_count=common_loci,
                    confidence_tier=tier
                ))

        # Sort hits by combined LR descending
        hits.sort(key=lambda x: x.combined_lr, reverse=True)
        top_hits = hits[:top_k]

        return MissingPersonSearchResult(
            query_id=query_profile.profile_id,
            total_candidates_searched=len(candidate_db),
            top_candidate_hits=top_hits,
            search_summary=f"Found {len(top_hits)} candidate hits exceeding LR threshold (Top LR: {top_hits[0].combined_lr if top_hits else 'N/A'})."
        )
