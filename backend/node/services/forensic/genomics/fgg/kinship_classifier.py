"""
Shared cM Project Probabilistic Kinship Classifier & Relationship Resolver.

Maps pairwise IBD metrics (cM, L_max, N_seg, k0, k1, k2) to ranked relationship
hypotheses with full probability simplex normalization (Sum P_i = 1.0).
"""

import math
from typing import List, Dict, Tuple
from .schemas import (
    KinshipDegreeEnum,
    RelationshipCandidate,
    KinshipClassificationResult,
    PairwiseIBDResult,
    IngestedFGGProfile
)
from .endogamy_filter import FGGEndogamyFilter


class FGGKinshipClassifier:
    """Probabilistic relationship degree classifier compliant with SWGDAM FGG (2023)."""

    # Relationship parameters: (degree, label, mean_cm, std_cm, min_cm, max_cm, description)
    RELATIONSHIP_MODELS: List[Tuple[KinshipDegreeEnum, str, float, float, float, float, str]] = [
        (
            KinshipDegreeEnum.DEGREE_0_TWIN_SELF,
            "Monozygotic Twin / Duplicate Profile",
            3545.0, 50.0, 3300.0, 3600.0,
            "Complete genomic identity across all 22 autosomes (k2 ≈ 1.0)"
        ),
        (
            KinshipDegreeEnum.DEGREE_1_PARENT_CHILD,
            "Parent / Child",
            3450.0, 65.0, 3300.0, 3600.0,
            "Direct first-degree generational transmission (100% IBD1 across genome, k1 ≈ 1.0)"
        ),
        (
            KinshipDegreeEnum.DEGREE_1_FULL_SIBLING,
            "Full Sibling",
            2600.0, 180.0, 2200.0, 3400.0,
            "Shared biparental heritage with mixed IBD1 (~50%) and IBD2 (~25%) segments"
        ),
        (
            KinshipDegreeEnum.DEGREE_2_HALF_SIB_AVUNCULAR,
            "Half-Sibling / Grandparent / Avuncular",
            1750.0, 190.0, 1200.0, 2300.0,
            "Second-degree relationship sharing on average ~25% of the genome (pure IBD1)"
        ),
        (
            KinshipDegreeEnum.DEGREE_3_FIRST_COUSIN,
            "1st Cousin (1C)",
            860.0, 140.0, 450.0, 1300.0,
            "Third-degree relationship sharing common grandparents (expected ~12.5% IBD)"
        ),
        (
            KinshipDegreeEnum.DEGREE_4_1C1R_HALF_1C,
            "1st Cousin Once Removed (1C1R) / Half-1C",
            430.0, 105.0, 150.0, 850.0,
            "Fourth-degree relationship (expected ~6.25% IBD sharing)"
        ),
        (
            KinshipDegreeEnum.DEGREE_5_SECOND_COUSIN,
            "2nd Cousin (2C)",
            220.0, 65.0, 50.0, 450.0,
            "Fifth-degree relationship sharing common great-grandparents (expected ~3.125% IBD)"
        ),
        (
            KinshipDegreeEnum.DEGREE_6_THIRD_COUSIN,
            "3rd Cousin (3C)",
            70.0, 30.0, 15.0, 200.0,
            "Seventh-degree relationship sharing common great-great-grandparents (~0.78% IBD)"
        ),
        (
            KinshipDegreeEnum.DEGREE_7_FOURTH_COUSIN_DISTANT,
            "4th Cousin (4C) / Distant Match",
            30.0, 15.0, 7.0, 85.0,
            "Distant genealogical trace sharing common 3G-grandparents"
        ),
        (
            KinshipDegreeEnum.UNRELATED,
            "Unrelated",
            0.0, 5.0, 0.0, 15.0,
            "No qualifying IBD sharing detected above forensic thresholds (< 7 cM)"
        )
    ]

    @classmethod
    def classify_kinship(
        cls,
        pairwise_result: PairwiseIBDResult,
        profile_a: IngestedFGGProfile,
        profile_b: IngestedFGGProfile
    ) -> KinshipClassificationResult:
        """
        Classifies relationship degree, applies endogamy adjustment, and ranks hypotheses.
        """
        # Step 1: Compute individual ROH scores
        f_roh_a = FGGEndogamyFilter.compute_individual_f_roh(profile_a)
        f_roh_b = FGGEndogamyFilter.compute_individual_f_roh(profile_b)

        # Step 2: Apply endogamy / pedigree collapse adjustment
        adjusted_cm, adj_delta, is_endogamous = FGGEndogamyFilter.adjust_endogamy_ibd(
            pairwise_result, f_roh_a, f_roh_b
        )

        # Step 3: Compute likelihoods across all models
        candidates = []
        log_likelihoods = []

        k1 = pairwise_result.cotterman_k1
        k2 = pairwise_result.cotterman_k2

        for degree, label, mean_cm, std_cm, min_cm, max_cm, desc in cls.RELATIONSHIP_MODELS:
            # Special check for Parent-Child vs Full-Sibling
            if degree == KinshipDegreeEnum.DEGREE_1_PARENT_CHILD and k2 > 0.10:
                # Parent-child mathematically has zero IBD2
                ll = -100.0
            elif degree == KinshipDegreeEnum.DEGREE_1_FULL_SIBLING and k2 < 0.05 and adjusted_cm > 3000.0:
                # Full siblings must exhibit IBD2
                ll = -100.0
            elif degree == KinshipDegreeEnum.DEGREE_0_TWIN_SELF and (k2 < 0.70 or adjusted_cm < 3200.0):
                ll = -100.0
            else:
                # Gaussian log-likelihood
                diff = adjusted_cm - mean_cm
                ll = -0.5 * ((diff / std_cm) ** 2) - math.log(std_cm * math.sqrt(2.0 * math.pi))

            log_likelihoods.append(ll)

        # Softmax normalization
        max_ll = max(log_likelihoods)
        exp_weights = [math.exp(ll - max_ll) for ll in log_likelihoods]
        sum_exp = sum(exp_weights)

        for i, (degree, label, mean_cm, std_cm, min_cm, max_cm, desc) in enumerate(cls.RELATIONSHIP_MODELS):
            prob = exp_weights[i] / sum_exp if sum_exp > 0 else 0.0
            candidates.append(RelationshipCandidate(
                degree=degree,
                relationship_label=label,
                probability=round(prob, 6),
                expected_mean_cm=mean_cm,
                typical_cm_range_min=min_cm,
                typical_cm_range_max=max_cm,
                description=desc
            ))

        # Sort candidates descending by probability
        candidates.sort(key=lambda c: c.probability, reverse=True)
        top = candidates[0]

        # Formulate morphological note
        l_max = pairwise_result.longest_segment_cm
        n_seg = pairwise_result.segment_count
        note = cls._generate_morphology_note(adjusted_cm, l_max, n_seg, is_endogamous, adj_delta)

        return KinshipClassificationResult(
            sample_a_id=profile_a.profile_id,
            sample_b_id=profile_b.profile_id,
            raw_shared_cm=pairwise_result.total_shared_cm,
            adjusted_shared_cm=adjusted_cm,
            longest_segment_cm=l_max,
            segment_count=n_seg,
            endogamy_roh_score_a=f_roh_a,
            endogamy_roh_score_b=f_roh_b,
            endogamy_adjustment_applied_cm=adj_delta,
            top_candidate=top,
            all_candidates=candidates,
            bivariate_morphology_note=note,
            is_endogamy_suspected=is_endogamous
        )

    @staticmethod
    def _generate_morphology_note(
        cM: float, l_max: float, n_seg: int, is_endogamous: bool, delta: float
    ) -> str:
        """Generates analytical note resolving bivariate L_max vs segment count."""
        if cM < 15.0:
            return "No significant identity-by-descent blocks detected; individuals are genetically unrelated."
        if is_endogamous:
            return f"Endogamy/pedigree collapse detected (ROH adjustment: -{delta:.1f} cM). Multiple short segments ({n_seg} segs, L_max={l_max:.1f} cM) reflect background population linkage."
        if l_max >= 40.0:
            return f"Strong unbroken segment structure (L_max={l_max:.1f} cM) indicates close genealogical connection with minimal intervening recombination."
        return f"Standard outbred segment distribution ({n_seg} segments, L_max={l_max:.1f} cM) consistent with expected Poisson meiotic crossovers."
