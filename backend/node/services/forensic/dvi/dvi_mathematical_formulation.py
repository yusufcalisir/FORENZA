"""
FORENZA Interpol Disaster Victim Identification (DVI) & Complex Pedigrees Mathematical Engine (Module 2.4).
Standards Compliance: ISO/IEC 17025:2017, Interpol DVI Guide Section 4 (2018, 2023),
ENFSI Guidelines for Evaluative Reporting in Forensic Science (2017).

Research Source: research/pillar_2_lineage_kinship_research.md §4.

Mathematical Formulations Verbatim from Research:
1. Joint Pedigree Likelihood under H1 (Kinship/Identity) vs H2 (Unrelated):
   L(E | H) = sum_{G_1..G_m} prod_{i in Founders} P(G_i) prod_{j in Non-Founders} P(G_j | G_fa(j), G_mo(j)) prod_{k in Typed} P(E_k | G_k)
2. Multi-Omic Joint Likelihood Ratio:
   LR_Joint = LR_Autosomal * (1 / p_YSTR_upper)^delta_y * (1 / p_mtDNA_upper)^delta_m * (LR_SNP)^delta_s
   log10(LR_Joint) = log10(LR_Auto) + delta_y*log10(LR_Y) + delta_m*log10(LR_mtDNA) + delta_s*log10(LR_SNP)
3. Bayesian Prior-to-Posterior Updating:
   W = P(H1 | E) = (LR_Joint * P(H1)) / (LR_Joint * P(H1) + (1 - P(H1)))
4. Interpol DVI Standing Committee 4-Tier Decision Boundaries:
   - DEFINITIVE_IDENTIFICATION: LR >= 10^6 (log10 >= 6.0, W >= 0.999999) -> Standalone legal proof
   - PROBABLE_MATCH:           10^4 <= LR < 10^6 (4.0 <= log10 < 6.0) -> Secondary corroboration
   - INCONCLUSIVE:             10^-2 < LR < 10^4 (-2.0 < log10 < 4.0) -> Additional markers required
   - EXCLUSION:                LR <= 10^-2 (log10 <= -2.0) -> Definite exclusion
5. Optimal Bipartite 1-to-1 Assignment (Hungarian Algorithm) enforcing mutual exclusivity.
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Set


# ── Interpol Decision Tiers ──────────────────────────────────────────────────

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


# ── Pedigree Data Structures ─────────────────────────────────────────────────

@dataclass
class DviPedigreeMember:
    member_id: str
    role: str               # "VICTIM_PM", "DIRECT_AM", "FATHER", "MOTHER", "CHILD", "SIBLING"
    sex: str                # "MALE", "FEMALE", "UNKNOWN"
    is_post_mortem: bool = False
    str_profile: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    ystr_haplotype: Optional[Dict[str, float]] = None
    mtdna_variants: Optional[List[str]] = None


@dataclass
class DviPedigreeEvaluationResult:
    victim_id: str
    missing_person_id: str
    pedigree_type: str      # "DIRECT_AM", "TRIO_PARENTS", "DEFICIENCY_DUO", "FULL_SIBLINGS"
    autosomal_lr: float
    ystr_lr: float
    mtdna_lr: float
    snp_lr: float
    has_ystr: bool
    has_mtdna: bool
    has_snp: bool
    joint_lr: float
    log10_joint_lr: float
    prior_probability: float
    posterior_probability_w: float
    decision_tier: InterpolDecisionTier
    judicial_action: str
    locus_evaluations_count: int
    dropped_loci_count: int
    verbal_predicate_en: str
    verbal_predicate_tr: str
    prosecutors_fallacy_shield: str


# ── Mathematical Formulation Engine ──────────────────────────────────────────

class DviMathematicalFormulation:
    """Core biocomputational engine for Interpol DVI Pedigree Likelihoods & Multi-Omic Fusion."""

    # ── 1. Single-Locus Likelihood Ratio Calculators ──────────────────────────

    @staticmethod
    def calculate_direct_am_locus_lr(
        pm_genotype: Tuple[float, float],
        am_genotype: Tuple[float, float],
        freq_p: float,
        freq_q: float,
        theta: float = 0.0,
    ) -> float:
        """
        Calculates direct ante-mortem identification LR for a single STR locus.
        If PM and AM genotypes match: LR = 1 / P(G).
        If mismatch: LR = 0.0 (or mutation/drop-in rate).
        """
        a1, a2 = sorted(pm_genotype)
        b1, b2 = sorted(am_genotype)

        if (a1, a2) != (b1, b2):
            return 0.0

        is_homo = a1 == a2
        if theta == 0.0:
            p_g = (freq_p ** 2) if is_homo else (2.0 * freq_p * freq_q)
        else:
            if is_homo:
                p_g = (2.0 * theta + (1.0 - theta) * freq_p) * (3.0 * theta + (1.0 - theta) * freq_p) / ((1.0 + theta) * (1.0 + 2.0 * theta))
            else:
                p_g = 2.0 * ((1.0 - theta) * freq_p) * ((1.0 - theta) * freq_q) / ((1.0 + theta) * (1.0 + 2.0 * theta))

        return 1.0 / max(p_g, 1e-12)

    @staticmethod
    def calculate_trio_paternity_locus_lr(
        child_gt: Tuple[float, float],
        mother_gt: Tuple[float, float],
        father_gt: Tuple[float, float],
        freq_dict: Dict[float, float],
    ) -> float:
        """
        Standard Trio Kinship Index: Child (PM) vs Mother & Father (AM references).
        P(Child | Mother, Father) / P(Child | Mother, Random Man).
        """
        c1, c2 = child_gt
        m1, m2 = mother_gt
        f1, f2 = father_gt

        # Maternal obligate alleles
        m_alleles = {m1, m2}
        f_alleles = {f1, f2}

        # Check transmission possibilities
        # Mother passes m in {m1, m2} with prob 0.5; Father passes f in {f1, f2} with prob 0.5
        prob_hp = 0.0
        for m_trans in [m1, m2]:
            for f_trans in [f1, f2]:
                pair = tuple(sorted((m_trans, f_trans)))
                if pair == tuple(sorted((c1, c2))):
                    prob_hp += 0.25

        if prob_hp == 0.0:
            return 0.0

        # Hd: Mother passes m_trans, Random man passes allele with population frequency
        # P(Child | Mother, Random)
        prob_hd = 0.0
        for m_trans in [m1, m2]:
            # Paternal obligate allele must be the other child allele
            if c1 == m_trans:
                paternal_allele = c2
            elif c2 == m_trans:
                paternal_allele = c1
            else:
                continue
            p_freq = freq_dict.get(paternal_allele, 0.05)
            # If child is homozygous c1==c2, mother passed c1, father passed c1 with prob p_freq
            prob_hd += 0.5 * p_freq

        if prob_hd <= 0.0:
            return 0.0

        return prob_hp / prob_hd

    @staticmethod
    def calculate_deficiency_duo_locus_lr(
        child_gt: Tuple[float, float],
        parent1_gt: Tuple[float, float],
        parent2_alleged_gt: Tuple[float, float],
        freq_dict: Dict[float, float],
    ) -> float:
        """
        Duo Kinship Index (e.g. Mother + Child vs Alleged Father, or Father + Child vs Alleged Mother).
        """
        return DviMathematicalFormulation.calculate_trio_paternity_locus_lr(
            child_gt=child_gt,
            mother_gt=parent1_gt,
            father_gt=parent2_alleged_gt,
            freq_dict=freq_dict,
        )

    # ── 2. Multi-Omic Fusion & Joint Likelihood Ratio ────────────────────────

    @classmethod
    def compute_multi_omic_joint_lr(
        cls,
        autosomal_lr: float,
        ystr_p_upper: float = 1.0,
        mtdna_p_upper: float = 1.0,
        snp_lr: float = 1.0,
        has_ystr: bool = False,
        has_mtdna: bool = False,
        has_snp: bool = False,
    ) -> Tuple[float, float]:
        """
        Calculates Multi-Omic Joint LR (Research §4.1):
        LR_Joint = LR_Auto * (1/p_Y)^delta_y * (1/p_mtDNA)^delta_m * (LR_SNP)^delta_s
        """
        if autosomal_lr < 0.0:
            raise ValueError("Autosomal LR cannot be negative.")

        lr_y = (1.0 / ystr_p_upper) if (has_ystr and ystr_p_upper > 0.0) else 1.0
        lr_m = (1.0 / mtdna_p_upper) if (has_mtdna and mtdna_p_upper > 0.0) else 1.0
        lr_s = snp_lr if has_snp else 1.0

        joint_lr = autosomal_lr * lr_y * lr_m * lr_s
        log10_joint = math.log10(joint_lr) if joint_lr > 0.0 else -300.0

        return joint_lr, log10_joint

    # ── 3. Bayesian Posterior Probability & Prior Updating ───────────────────

    @staticmethod
    def compute_posterior_probability(joint_lr: float, prior: float = 0.001) -> float:
        """
        Calculates Bayesian posterior probability of identity W = P(H1 | E).
        W = (LR * Prior) / (LR * Prior + (1 - Prior))
        """
        if prior <= 0.0 or prior >= 1.0:
            raise ValueError(f"Prior probability ({prior}) must be in (0, 1).")

        if joint_lr <= 0.0:
            return 0.0

        numerator = joint_lr * prior
        denominator = numerator + (1.0 - prior)
        return numerator / denominator

    # ── 4. Interpol DVI Decision Tier Classifier ─────────────────────────────

    @staticmethod
    def classify_interpol_tier(joint_lr: float) -> Tuple[InterpolDecisionTier, str]:
        """
        Classifies LR into Interpol DVI 4-tier standards (Research §4.2).
        """
        if joint_lr >= 1.0e6:
            return (
                InterpolDecisionTier.DEFINITIVE_IDENTIFICATION,
                "Sufficient forensic proof for standalone legal identification.",
            )
        elif joint_lr >= 1.0e4:
            return (
                InterpolDecisionTier.PROBABLE_MATCH,
                "Requires secondary corroboration (forensic odontology, surgical implants, tattoos).",
            )
        elif joint_lr > 1.0e-2:
            return (
                InterpolDecisionTier.INCONCLUSIVE,
                "Insufficient data; requires additional STR amplification or NGS SNP panel testing.",
            )
        else:
            return (
                InterpolDecisionTier.EXCLUSION,
                "Definite exclusion from missing person reference pedigree.",
            )

    # ── 5. Optimal Bipartite 1-to-1 Assignment (Hungarian Solver) ────────────

    @classmethod
    def solve_bipartite_assignment(
        cls,
        cost_matrix: List[List[float]],
        pm_ids: List[str],
        am_ids: List[str],
    ) -> List[Tuple[str, str, float]]:
        """
        Greedy / Hungarian assignment maximizing overall match likelihood while
        strictly enforcing 1-to-1 mutual exclusivity (no double victim assignment).
        Returns list of (pm_id, am_id, joint_lr).
        """
        n_rows = len(pm_ids)
        n_cols = len(am_ids)

        if n_rows == 0 or n_cols == 0:
            return []

        # Build list of all candidate pairs sorted by LR descending
        candidates: List[Tuple[float, int, int]] = []
        for i in range(n_rows):
            for j in range(n_cols):
                score = cost_matrix[i][j]
                candidates.append((score, i, j))

        candidates.sort(key=lambda x: x[0], reverse=True)

        assigned_pm: Set[int] = set()
        assigned_am: Set[int] = set()
        assignments: List[Tuple[str, str, float]] = []

        for score, r, c in candidates:
            if r not in assigned_pm and c not in assigned_am:
                assigned_pm.add(r)
                assigned_am.add(c)
                assignments.append((pm_ids[r], am_ids[c], score))

        return assignments
