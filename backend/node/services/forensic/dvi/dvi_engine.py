"""
FORENZA Interpol Disaster Victim Identification (DVI) Multi-Omic Engine — Module 09.

Implements verbatim from Pillar 2 Research §4:
  - §4.1 Multi-Omic Joint Likelihood Ratio (LR_Joint):
           LR_DVI,Total = LR_Autosomal * (1 / p_YSTR)^delta_y * (1 / p_mtDNA)^delta_m * LR_SNP^delta_s
           log10(LR_Joint) = log10(LR_Auto) + delta_y * log10(LR_Y) + delta_m * log10(LR_mtDNA) + delta_s * log10(LR_SNP)
  - §4.2 Interpol DVI Standing Committee Decision Boundaries:
           - DEFINITIVE_IDENTIFICATION: LR >= 10^6 (log10 >= 6.0) -> Standalone legal proof
           - PROBABLE_MATCH:           10^4 <= LR < 10^6 (4.0 <= log10 < 6.0) -> Secondary corroboration
           - INCONCLUSIVE:             10^-2 < LR < 10^4 (-2.0 < log10 < 4.0) -> Additional markers needed
           - EXCLUSION:                LR <= 10^-2 (log10 <= -2.0) -> Definite exclusion
  - §4.1 N x M Ante-Mortem (AM) vs Post-Mortem (PM) Reconciliation Matrix & Missing Persons Ranking

Golden Benchmark Vector:
  VECTOR_P2_03 — Severely Degraded PM Skeletal Sample:
                 Autosomal LR = 5.2e3, Y-STR p_upper = 0.0002 (LR_Y = 5000), mtDNA p_upper = 0.0001 (LR_mtDNA = 10000)
                 Combined DVI LR = 2.6e11, log10(LR) = 11.4149
                 Status: DEFINITIVE IDENTIFICATION (LR >= 10^6)

References:
  Interpol Disaster Victim Identification (DVI) Guide Section 4 (2018, 2023).
  ENFSI Guidelines for Evaluative Reporting in Forensic Science (2017).
  Brenner CH (2006) Some mathematical problems in the DNA identification of victims in the World Trade Center disaster.
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# ── Interpol Decision Tiers (§4.2) ────────────────────────────────────────────

class InterpolDecisionTier(str, Enum):
    DEFINITIVE_IDENTIFICATION = "DEFINITIVE_IDENTIFICATION"
    PROBABLE_MATCH = "PROBABLE_MATCH"
    INCONCLUSIVE = "INCONCLUSIVE"
    EXCLUSION = "EXCLUSION"


@dataclass(frozen=True)
class InterpolTierMetadata:
    tier: InterpolDecisionTier
    min_lr: float
    max_lr: float
    min_log10: float
    max_log10: float
    judicial_action_criterion: str
    requires_secondary_corroboration: bool
    is_court_admissible_standalone: bool


INTERPOL_TIER_RULES: Dict[InterpolDecisionTier, InterpolTierMetadata] = {
    InterpolDecisionTier.DEFINITIVE_IDENTIFICATION: InterpolTierMetadata(
        tier=InterpolDecisionTier.DEFINITIVE_IDENTIFICATION,
        min_lr=1.0e6,
        max_lr=float("inf"),
        min_log10=6.0,
        max_log10=float("inf"),
        judicial_action_criterion="Sufficient forensic proof for standalone legal identification.",
        requires_secondary_corroboration=False,
        is_court_admissible_standalone=True,
    ),
    InterpolDecisionTier.PROBABLE_MATCH: InterpolTierMetadata(
        tier=InterpolDecisionTier.PROBABLE_MATCH,
        min_lr=1.0e4,
        max_lr=1.0e6,
        min_log10=4.0,
        max_log10=6.0,
        judicial_action_criterion="Requires secondary corroboration (forensic odontology, surgical implants, tattoos).",
        requires_secondary_corroboration=True,
        is_court_admissible_standalone=False,
    ),
    InterpolDecisionTier.INCONCLUSIVE: InterpolTierMetadata(
        tier=InterpolDecisionTier.INCONCLUSIVE,
        min_lr=1.0e-2,
        max_lr=1.0e4,
        min_log10=-2.0,
        max_log10=4.0,
        judicial_action_criterion="Insufficient data; requires additional STR amplification or NGS SNP panel testing.",
        requires_secondary_corroboration=True,
        is_court_admissible_standalone=False,
    ),
    InterpolDecisionTier.EXCLUSION: InterpolTierMetadata(
        tier=InterpolDecisionTier.EXCLUSION,
        min_lr=0.0,
        max_lr=1.0e-2,
        min_log10=-float("inf"),
        max_log10=-2.0,
        judicial_action_criterion="Definite exclusion from missing person reference pedigree.",
        requires_secondary_corroboration=False,
        is_court_admissible_standalone=True,
    ),
}


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class DviMultiOmicComponents:
    """Breakdown of individual multi-omic Likelihood Ratios contributing to Joint LR."""
    autosomal_str_lr: float
    ystr_lr: float
    ystr_p_upper: Optional[float]
    has_ystr: bool
    mtdna_lr: float
    mtdna_p_upper: Optional[float]
    has_mtdna: bool
    snp_lr: float
    has_snp: bool


@dataclass
class DviPairwiseJointResult:
    """Pairwise multi-omic evaluation between one PM remain and one AM family reference."""
    pm_profile_id: str
    am_family_id: str
    joint_lr: float
    log10_joint_lr: float
    decision_tier: InterpolDecisionTier
    components: DviMultiOmicComponents
    judicial_action: str
    is_positive_identification: bool


@dataclass
class DviMissingPersonCandidate:
    """A candidate AM family match for a given PM remain."""
    am_family_id: str
    relationship_tested: str
    joint_lr: float
    log10_joint_lr: float
    decision_tier: InterpolDecisionTier
    posterior_probability: float


@dataclass
class DviReconciliationReport:
    """Full N x M mass disaster cross-reconciliation matrix report."""
    disaster_event_id: str
    total_pm_remains: int
    total_am_families: int
    definitive_identifications_count: int
    probable_matches_count: int
    inconclusive_count: int
    exclusions_count: int
    reconciliation_matrix: List[DviPairwiseJointResult]
    interpol_summary: str
    prosecutors_fallacy_shield: str


# ── Engine ─────────────────────────────────────────────────────────────────────

class DviEngine:
    """
    FORENZA Interpol DVI Mass Disaster Multi-Omic Reconciliation Engine (Module 09).

    Implements verbatim from Pillar 2 Research §4.
    """

    # ── §4.1 Multi-Omic Joint Likelihood Ratio Computation ────────────────────

    @staticmethod
    def compute_multi_omic_joint_lr(
        autosomal_lr: float = 1.0,
        ystr_p_upper: Optional[float] = None,
        mtdna_p_upper: Optional[float] = None,
        snp_lr: float = 1.0,
        has_ystr: bool = False,
        has_mtdna: bool = False,
        has_snp: bool = False,
    ) -> Tuple[float, float, DviMultiOmicComponents]:
        """
        Computes the Multi-Omic Joint Likelihood Ratio (LR_Joint) across available genetic systems:

        LR_Joint = LR_Auto * (1 / p_YSTR)^delta_y * (1 / p_mtDNA)^delta_m * LR_SNP^delta_s

        (Research §4.1; VECTOR_P2_03)
        """
        lr_auto = max(1e-12, autosomal_lr)

        # Y-STR Component
        if has_ystr and ystr_p_upper is not None and ystr_p_upper > 0:
            p_y = max(1e-12, min(1.0, ystr_p_upper))
            lr_y = 1.0 / p_y
        else:
            p_y = None
            lr_y = 1.0
            has_ystr = False

        # mtDNA Component
        if has_mtdna and mtdna_p_upper is not None and mtdna_p_upper > 0:
            p_m = max(1e-12, min(1.0, mtdna_p_upper))
            lr_m = 1.0 / p_m
        else:
            p_m = None
            lr_m = 1.0
            has_mtdna = False

        # SNP Component
        if has_snp:
            lr_snp_val = max(1e-12, snp_lr)
        else:
            lr_snp_val = 1.0

        # Multi-omic product rule
        joint_lr = lr_auto * (lr_y if has_ystr else 1.0) * (lr_m if has_mtdna else 1.0) * (lr_snp_val if has_snp else 1.0)
        log10_joint = math.log10(joint_lr) if joint_lr > 0 else -float("inf")

        components = DviMultiOmicComponents(
            autosomal_str_lr=round(lr_auto, 4),
            ystr_lr=round(lr_y, 4),
            ystr_p_upper=round(p_y, 8) if p_y is not None else None,
            has_ystr=has_ystr,
            mtdna_lr=round(lr_m, 4),
            mtdna_p_upper=round(p_m, 8) if p_m is not None else None,
            has_mtdna=has_mtdna,
            snp_lr=round(lr_snp_val, 4),
            has_snp=has_snp,
        )

        return joint_lr, log10_joint, components

    # ── §4.2 Interpol Decision Boundary Classification ────────────────────────

    @staticmethod
    def classify_interpol_decision_tier(joint_lr: float) -> Tuple[InterpolDecisionTier, str]:
        """
        Classifies Joint LR into Interpol DVI Decision Boundaries:
        - LR >= 10^6: DEFINITIVE_IDENTIFICATION
        - 10^4 <= LR < 10^6: PROBABLE_MATCH
        - 10^-2 < LR < 10^4: INCONCLUSIVE
        - LR <= 10^-2: EXCLUSION

        (Research §4.2)
        """
        if joint_lr >= 1.0e6:
            tier = InterpolDecisionTier.DEFINITIVE_IDENTIFICATION
        elif joint_lr >= 1.0e4:
            tier = InterpolDecisionTier.PROBABLE_MATCH
        elif joint_lr > 1.0e-2:
            tier = InterpolDecisionTier.INCONCLUSIVE
        else:
            tier = InterpolDecisionTier.EXCLUSION

        meta = INTERPOL_TIER_RULES[tier]
        return tier, meta.judicial_action_criterion

    # ── §4.1 N x M Mass Disaster Reconciliation Matrix ────────────────────────

    def reconcile_dvi_matrix(
        self,
        disaster_event_id: str,
        pm_remains: List[Dict[str, Any]],
        am_families: List[Dict[str, Any]],
        threshold_lr: float = 1.0e6,
    ) -> DviReconciliationReport:
        """
        Evaluates N PM victim remains against M AM missing person family pedigrees,
        computing pairwise multi-omic Joint LRs and Interpol decision tiers.

        (Research §4.1, §4.2)
        """
        matrix: List[DviPairwiseJointResult] = []
        tier_counts = {tier: 0 for tier in InterpolDecisionTier}

        for pm in pm_remains:
            pm_id = pm["pm_id"]
            pm_auto_map = pm.get("autosomal_lr_map", {})
            pm_ystr_p = pm.get("ystr_p_upper", None)
            pm_mtdna_p = pm.get("mtdna_p_upper", None)
            pm_snp_map = pm.get("snp_lr_map", {})

            for am in am_families:
                am_id = am["am_id"]
                auto_lr = pm_auto_map.get(am_id, pm.get("default_autosomal_lr", 1.0))
                snp_lr = pm_snp_map.get(am_id, 1.0)

                has_male_ref = am.get("has_male_reference", False) and pm_ystr_p is not None
                has_mat_ref = am.get("has_maternal_reference", False) and pm_mtdna_p is not None
                has_snp_data = am.get("has_snp_data", False)

                joint_lr, log10_joint, comp = self.compute_multi_omic_joint_lr(
                    autosomal_lr=auto_lr,
                    ystr_p_upper=pm_ystr_p,
                    mtdna_p_upper=pm_mtdna_p,
                    snp_lr=snp_lr,
                    has_ystr=has_male_ref,
                    has_mtdna=has_mat_ref,
                    has_snp=has_snp_data,
                )

                tier, action = self.classify_interpol_decision_tier(joint_lr)
                tier_counts[tier] += 1

                matrix.append(
                    DviPairwiseJointResult(
                        pm_profile_id=pm_id,
                        am_family_id=am_id,
                        joint_lr=round(joint_lr, 4),
                        log10_joint_lr=round(log10_joint, 5),
                        decision_tier=tier,
                        components=comp,
                        judicial_action=action,
                        is_positive_identification=(joint_lr >= threshold_lr),
                    )
                )

        def_count = tier_counts[InterpolDecisionTier.DEFINITIVE_IDENTIFICATION]
        prob_count = tier_counts[InterpolDecisionTier.PROBABLE_MATCH]
        incon_count = tier_counts[InterpolDecisionTier.INCONCLUSIVE]
        excl_count = tier_counts[InterpolDecisionTier.EXCLUSION]

        summary = (
            f"Interpol DVI Reconciliation Complete for Event '{disaster_event_id}': "
            f"{def_count} Definitive Identifications (LR >= 10^6), "
            f"{prob_count} Probable Matches (10^4 <= LR < 10^6), "
            f"{incon_count} Inconclusive Pairs, {excl_count} Exclusions across "
            f"{len(pm_remains)} PM remains and {len(am_families)} AM families."
        )

        shield = (
            "IMPORTANT (Interpol DVI Multi-Omic Legal Notice): Multi-omic Joint Likelihood Ratios (LR_Joint) "
            "synthesize independent autosomal STR, Y-STR, mtDNA, and SNP likelihoods under the product rule. "
            "Per Interpol DVI Guidelines, standalone legal identification requires LR >= 10^6 (log10 >= 6.0). "
            "Lineage markers (Y-STR / mtDNA) confirm familial lineage, not singular uniqueness."
        )

        return DviReconciliationReport(
            disaster_event_id=disaster_event_id,
            total_pm_remains=len(pm_remains),
            total_am_families=len(am_families),
            definitive_identifications_count=def_count,
            probable_matches_count=prob_count,
            inconclusive_count=incon_count,
            exclusions_count=excl_count,
            reconciliation_matrix=matrix,
            interpol_summary=summary,
            prosecutors_fallacy_shield=shield,
        )

    # ── Missing Persons Candidate Ranking ────────────────────────────────────

    def rank_missing_person_candidates(
        self,
        pm_profile_id: str,
        candidate_evaluations: List[Dict[str, Any]],
        prior_probability: float = 0.01,
    ) -> List[DviMissingPersonCandidate]:
        """
        Ranks candidate AM families for a given PM remain by Multi-Omic Joint LR
        and normalized posterior probability.
        """
        scored: List[Tuple[float, DviMissingPersonCandidate]] = []
        raw_posteriors = []

        for cand in candidate_evaluations:
            am_id = cand["am_family_id"]
            rel = cand.get("relationship_tested", "PARENT_CHILD")
            auto_lr = cand.get("autosomal_lr", 1.0)
            ystr_p = cand.get("ystr_p_upper", None)
            mtdna_p = cand.get("mtdna_p_upper", None)
            has_ystr = cand.get("has_ystr", False)
            has_mtdna = cand.get("has_mtdna", False)

            joint_lr, log10_joint, _ = self.compute_multi_omic_joint_lr(
                autosomal_lr=auto_lr,
                ystr_p_upper=ystr_p,
                mtdna_p_upper=mtdna_p,
                has_ystr=has_ystr,
                has_mtdna=has_mtdna,
            )

            tier, _ = self.classify_interpol_decision_tier(joint_lr)
            # Odds = LR * (prior / (1 - prior)) => Posterior = Odds / (1 + Odds)
            odds = joint_lr * (prior_probability / (1.0 - prior_probability))
            post = odds / (1.0 + odds) if odds < 1e12 else 1.0

            cand_obj = DviMissingPersonCandidate(
                am_family_id=am_id,
                relationship_tested=rel,
                joint_lr=round(joint_lr, 4),
                log10_joint_lr=round(log10_joint, 5),
                decision_tier=tier,
                posterior_probability=round(post, 6),
            )
            scored.append((joint_lr, cand_obj))

        # Sort descending by Joint LR
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored]
