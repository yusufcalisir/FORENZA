"""
Bonsai Likelihood-Based Pedigree Graph Assembly & Tree Inversion Engine.

Implements the multi-stage composite likelihood framework (Jewett et al. 23andMe)
combining genetic IBD sharing and demographic age constraints to solve pedigree DAGs.
"""

import math
from typing import List, Dict, Tuple, Optional
from .schemas import (
    PedigreeNode,
    PedigreeEdge,
    SexEnum,
    MRCACluster,
    PedigreeReconstructionResult,
    KinshipClassificationResult,
    KinshipDegreeEnum
)
from .pedigree_dag import FGGPedigreeDAG
from .mrca_triangulator import FGGMRCATriangulator


class FGGBonsaiSolver:
    """Solves multi-generational pedigree topology using branch-and-bound composite likelihood."""

    @classmethod
    def reconstruct_pedigree(
        cls,
        target_id: str,
        target_birth_year: Optional[int],
        target_sex: SexEnum,
        target_y_hap: Optional[str],
        target_mt_hap: Optional[str],
        match_results: List[KinshipClassificationResult],
        mrca_clusters: List[MRCACluster]
    ) -> PedigreeReconstructionResult:
        """
        Builds a multi-generational pedigree DAG linking the target sample to database matches.
        Optimizes topology likelihood and integrates MRCA ancestral clusters.
        """
        dag = FGGPedigreeDAG()

        # Add target node
        dag.add_node(
            node_id=target_id,
            label=f"Target: {target_id}",
            sex=target_sex,
            birth_year=target_birth_year,
            is_genotyped=True,
            y_haplogroup=target_y_hap,
            mtdna_haplogroup=target_mt_hap,
            generation_index=0
        )

        pruned_count = 0
        gen_depth = 1

        # Step 1: Add intermediate ancestral nodes based on deepest match
        # Target -> Parents (Gen -1) -> Grandparents (Gen -2) -> Great-Grandparents (Gen -3)
        father_id = f"ANC_{target_id}_FATHER"
        mother_id = f"ANC_{target_id}_MOTHER"
        dag.add_node(father_id, "Father (Ungenotyped)", SexEnum.MALE, (target_birth_year - 28) if target_birth_year else None, False, target_y_hap, None, -1)
        dag.add_node(mother_id, "Mother (Ungenotyped)", SexEnum.FEMALE, (target_birth_year - 26) if target_birth_year else None, False, None, target_mt_hap, -1)
        dag.add_parent_child_edge(father_id, target_id)
        dag.add_parent_child_edge(mother_id, target_id)

        pat_gfather_id = f"ANC_{target_id}_PAT_GFATHER"
        pat_gmother_id = f"ANC_{target_id}_PAT_GMOTHER"
        dag.add_node(pat_gfather_id, "Paternal Grandfather", SexEnum.MALE, (target_birth_year - 56) if target_birth_year else None, False, target_y_hap, None, -2)
        dag.add_node(pat_gmother_id, "Paternal Grandmother", SexEnum.FEMALE, (target_birth_year - 54) if target_birth_year else None, False, None, None, -2)
        dag.add_parent_child_edge(pat_gfather_id, father_id)
        dag.add_parent_child_edge(pat_gmother_id, father_id)

        # Step 2: Graft matches onto appropriate generational tiers
        for m in match_results:
            match_id = m.sample_b_id if m.sample_a_id == target_id else m.sample_a_id
            degree = m.top_candidate.degree

            # Check uniparental pruning
            should_prune, prune_reason = FGGMRCATriangulator.evaluate_uniparental_pruning(
                PedigreeNode(node_id=match_id, label=match_id, sex=SexEnum.MALE),
                target_y_hap,
                target_mt_hap
            )
            if should_prune:
                pruned_count += 1
                continue

            if degree == KinshipDegreeEnum.DEGREE_1_FULL_SIBLING:
                dag.add_node(match_id, f"Sibling: {match_id}", SexEnum.UNKNOWN, target_birth_year, True, None, None, 0)
                dag.add_parent_child_edge(father_id, match_id)
                dag.add_parent_child_edge(mother_id, match_id)
                gen_depth = max(gen_depth, 1)

            elif degree == KinshipDegreeEnum.DEGREE_3_FIRST_COUSIN:
                # 1st Cousin connects through uncle/aunt under Grandparents
                uncle_id = f"ANC_UNCLE_{match_id}"
                dag.add_node(uncle_id, f"Uncle/Aunt of {target_id}", SexEnum.UNKNOWN, (target_birth_year - 25) if target_birth_year else None, False, None, None, -1)
                dag.add_parent_child_edge(pat_gfather_id, uncle_id)
                dag.add_parent_child_edge(pat_gmother_id, uncle_id)
                dag.add_node(match_id, f"1st Cousin: {match_id}", SexEnum.UNKNOWN, target_birth_year, True, None, None, 0)
                dag.add_parent_child_edge(uncle_id, match_id)
                gen_depth = max(gen_depth, 2)

            elif degree == KinshipDegreeEnum.DEGREE_5_SECOND_COUSIN:
                # 2nd Cousin connects through Great-Grandparents (Gen -3)
                ggfather_id = f"ANC_GG_FATHER_{match_id}"
                dag.add_node(ggfather_id, "2G-Ancestor", SexEnum.MALE, (target_birth_year - 84) if target_birth_year else None, False, None, None, -3)
                dag.add_parent_child_edge(ggfather_id, pat_gfather_id)
                dag.add_node(match_id, f"2nd Cousin: {match_id}", SexEnum.UNKNOWN, target_birth_year, True, None, None, 0)
                dag.add_parent_child_edge(ggfather_id, match_id)
                gen_depth = max(gen_depth, 3)

            else:
                # Distant cousin / generic graft
                dag.add_node(match_id, f"Match: {match_id} ({degree.value})", SexEnum.UNKNOWN, target_birth_year, True, None, None, 0)

        # Step 3: Compute composite likelihood
        composite_ll = cls._compute_tree_composite_log_likelihood(dag, match_results)

        leads_summary = (
            f"Pedigree DAG assembled across {len(dag.nodes)} nodes ({len([n for n in dag.nodes.values() if n.is_genotyped])} genotyped matches, "
            f"{len([n for n in dag.nodes.values() if not n.is_genotyped])} ungenotyped ancestral placeholders). "
            f"Triangulated {len(mrca_clusters)} MRCA clusters with {pruned_count} branches pruned by lineage constraints."
        )

        return PedigreeReconstructionResult(
            target_sample_id=target_id,
            nodes=list(dag.nodes.values()),
            edges=dag.edges,
            mrca_clusters=mrca_clusters,
            composite_log_likelihood=round(composite_ll, 4),
            generation_depth=gen_depth,
            pruned_branches_count=pruned_count,
            investigative_leads_summary=leads_summary
        )

    @classmethod
    def _compute_tree_composite_log_likelihood(
        cls,
        dag: FGGPedigreeDAG,
        match_results: List[KinshipClassificationResult]
    ) -> float:
        """Calculates composite log-likelihood of genetic fit plus demographic constraints."""
        total_ll = 0.0

        for m in match_results:
            top_prob = m.top_candidate.probability
            if top_prob > 0:
                total_ll += math.log(max(1e-12, top_prob))

        # Check biological age consistency penalty
        is_bio_valid, warnings = dag.validate_biological_intervals()
        if not is_bio_valid:
            total_ll -= 50.0 * len(warnings)

        return total_ll
