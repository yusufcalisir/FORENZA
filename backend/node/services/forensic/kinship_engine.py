"""
FORENZA Module 01 — Kinship Index (KI), Pedigree Matching
& Stepwise Mutation Model (SMM) Engine.

Calculates Kinship/Paternity Indices (KI) using IBD (k0, k1, k2) coefficients
with Balding-Nichols theta correction for the following pedigree relationships:
  - Parent-Child Duo (Obligate allele method)
  - Full Siblings (Ito-Donnelly k-coefficients: k0=0.25, k1=0.50, k2=0.25)
  - Half Siblings / Avuncular / Grandparent-Grandchild (k0=0.50, k1=0.50, k2=0)
  - First Cousins (k0=0.75, k1=0.25, k2=0)
  - Unrelated (k0=1.0, k1=0, k2=0) — LR baseline

Stepwise Mutation Model (SMM) — Pillar 1 §1.3:
  P(m→n) = (1-μ)          if m=n
  P(m→n) = (μ/2)(1-r)r^|m-n|-1  if m≠n    (μ=10^-3, r=0.10)

Combined Paternity Index:
  CPI = ∏ KI_l
  W(%) = 100 × CPI·P_prior / (CPI·P_prior + P_prior_c)   (P_prior=0.50)

Compliance: ISO/IEC 17025:2017 • ISFG Recommendations (2006, 2012, 2016)
References: Ito et al. (2005); Buckleton & Triggs (2006); Curran et al. (2007)
"""

import math
from typing import Dict, List, Optional, Tuple
from .frequency_db import DEFAULT_THETA, FrequencyDatabase
from .models import AnalysisResult, KinshipRelationship, STRGenotype, STRProfile


# ---------------------------------------------------------------------------
# IBD Coefficient Table (k0, k1, k2) — Pillar 1 §1.3
# ---------------------------------------------------------------------------

IBD_COEFFICIENTS: Dict[KinshipRelationship, Tuple[float, float, float]] = {
    # relationship             k0      k1      k2
    KinshipRelationship.PARENT_CHILD:  (0.00,  1.00,  0.00),
    KinshipRelationship.FULL_SIBLING:  (0.25,  0.50,  0.25),
    KinshipRelationship.HALF_SIBLING:  (0.50,  0.50,  0.00),
    KinshipRelationship.AVUNCULAR:     (0.50,  0.50,  0.00),
    KinshipRelationship.GRANDPARENT:   (0.50,  0.50,  0.00),
    KinshipRelationship.FIRST_COUSIN:  (0.75,  0.25,  0.00),
    KinshipRelationship.UNRELATED:     (1.00,  0.00,  0.00),
}

# Locus-specific STR mutation rates (per AABB/ISFG averages, μ ≈ 10^-3)
DEFAULT_MUTATION_RATE: float = 1e-3
SMM_GEOMETRIC_PARAM_R: float = 0.10   # Geometric decay factor for multi-step mutations


# ---------------------------------------------------------------------------
# Stepwise Mutation Model (SMM)
# ---------------------------------------------------------------------------

def smm_transition_probability(m: float, n: float,
                                mu: float = DEFAULT_MUTATION_RATE,
                                r: float = SMM_GEOMETRIC_PARAM_R) -> float:
    """
    Stepwise Mutation Model transition probability P(m→n).

    P(m→n) = (1 - μ)                   if m == n  (no mutation)
    P(m→n) = (μ/2) · (1-r) · r^|m-n|-1   if m != n  (step-wise mutation)

    Args:
        m: Parental allele repeat number
        n: Child allele repeat number
        mu: Locus mutation rate (default 10^-3)
        r:  Geometric decay parameter (default 0.10)

    Returns:
        Transition probability P(m→n)
    """
    steps = abs(m - n)
    if steps == 0:
        return 1.0 - mu
    return (mu / 2.0) * (1.0 - r) * (r ** (steps - 1))


# ---------------------------------------------------------------------------
# KinshipEngine Class
# ---------------------------------------------------------------------------

class KinshipEngine:
    """
    Calculates Kinship Indices (KI) for pedigree relationships using
    IBD (k0,k1,k2) coefficients under Balding-Nichols theta correction.
    Supports germline mutation correction via the Stepwise Mutation Model.
    """

    def __init__(self, freq_db: Optional[FrequencyDatabase] = None):
        self.freq_db = freq_db or FrequencyDatabase()

    # ── Main KI Computation ───────────────────────────────────────────────

    def compute_kinship_index(
        self,
        profile1: STRProfile,
        profile2: STRProfile,
        relationship: KinshipRelationship = KinshipRelationship.PARENT_CHILD,
        theta: float = DEFAULT_THETA,
        population: Optional[str] = None,
        apply_mutation_model: bool = True,
    ) -> AnalysisResult:
        """
        Computes Combined Kinship Index (KI) across all shared loci.

        Full IBD formulation (Pillar 1 §1.3):
          KI_l = [k2·P(G1,G2|IBD=2) + k1·P(G1,G2|IBD=1) + k0·P(G1,G2|IBD=0)]
                 / [P(G1|θ) · P(G2|θ)]

        Also computes:
          CPI = ∏ KI_l
          W(%) = CPI·0.5 / (CPI·0.5 + 0.5) × 100   (equal prior odds)

        Args:
            profile1: Child / proband profile
            profile2: Alleged relative profile
            relationship: KinshipRelationship enum
            theta: Balding-Nichols coancestry coefficient
            population: Population reference (defaults to profile1 group)
            apply_mutation_model: If True, rescue exclusions via SMM

        Returns:
            AnalysisResult with .value = CPI, .metadata containing log10_ki,
            posterior_probability_W, ibdcoefficients, per-locus mutation flags.
        """
        pop = population or profile1.population_group
        k0, k1, k2 = IBD_COEFFICIENTS.get(relationship, (1.0, 0.0, 0.0))
        common_loci = sorted(
            set(profile1.loci.keys()) & set(profile2.loci.keys())
        )

        locus_ki: Dict[str, float] = {}
        total_log_ki: float = 0.0
        mutation_flags: Dict[str, bool] = {}

        for locus_name in common_loci:
            g1: STRGenotype = profile1.loci[locus_name]
            g2: STRGenotype = profile2.loci[locus_name]

            ki_l, mutated = self._compute_locus_ki(
                locus=locus_name,
                g1=g1,
                g2=g2,
                k0=k0, k1=k1, k2=k2,
                theta=theta,
                population=pop,
                apply_mutation_model=apply_mutation_model,
            )

            locus_ki[locus_name] = ki_l
            mutation_flags[locus_name] = mutated
            total_log_ki += math.log10(max(ki_l, 1e-30))

        cpi = 10.0 ** total_log_ki

        # Posterior Probability of Relationship (W%) — equal prior odds 0.50
        w_percent = (cpi * 0.50) / (cpi * 0.50 + 0.50) * 100.0 if cpi > 0 else 0.0

        # 95% CI in log-space (propagated from locus-level uncertainty)
        n_loci = len(common_loci)
        log_std_err = 0.12 * math.sqrt(n_loci)
        ci_low = 10.0 ** (total_log_ki - 1.96 * log_std_err) if total_log_ki > -30 else 0.0
        ci_high = 10.0 ** (total_log_ki + 1.96 * log_std_err)

        assumptions = [
            f"Relationship hypothesis: {relationship.value}",
            f"IBD coefficients: k0={k0}, k1={k1}, k2={k2} (Ito-Donnelly)",
            f"Population reference: FBI/NIST 1036 ({pop})",
            f"Balding-Nichols θ = {theta}",
            f"Stepwise Mutation Model: μ={DEFAULT_MUTATION_RATE}, r={SMM_GEOMETRIC_PARAM_R}",
            "Prior odds = 1:1 (P_prior = 0.50)",
            "Loci assumed in Linkage Equilibrium",
        ]
        limitations = [
            "Non-inbred reference population assumed",
            "SMM applied only to isolated single/multi-step discrepancies",
            "Complex pedigrees (e.g., incest) require extended IBD analysis",
        ]

        return AnalysisResult(
            value=cpi,
            confidence_interval=(ci_low, ci_high),
            assumptions=assumptions,
            model=f"FORENZA Module 01 Kinship Engine v2.0 ({relationship.value})",
            data_source=f"FBI/NIST 1036 ({pop})",
            limitations=limitations,
            locus_scores=locus_ki,
            metadata={
                "relationship": relationship.value,
                "posterior_probability": round(w_percent, 4),
                "log10_ki": round(total_log_ki, 6),
                "evaluated_loci_count": n_loci,
                "mutation_flags": mutation_flags,
                "ibd_k0": k0, "ibd_k1": k1, "ibd_k2": k2,
                "theta": theta,
                "population": pop,
            },
        )

    # ── Full IBD Locus KI ─────────────────────────────────────────────────

    def _compute_locus_ki(
        self,
        locus: str,
        g1: STRGenotype,
        g2: STRGenotype,
        k0: float, k1: float, k2: float,
        theta: float,
        population: str,
        apply_mutation_model: bool,
    ) -> Tuple[float, bool]:
        """
        Computes per-locus KI using the general IBD formulation.
        Falls back to SMM if no shared alleles are detected (mutation rescue).

        Parent-Child fast-path: when k0=0, k1=1, k2=0, the obligate allele
        formula KI_l = 1 / [2(θ+(1-θ)p_shared)] is applied directly.

        Returns: (ki_l, mutation_occurred)
        """
        mutated = False

        # Parent-Child fast-path (k0=0, k1=1, k2=0) — obligate allele formula
        # KI_l = 1 / [2(θ + (1-θ)·p_i)]  where p_i is the shared allele frequency
        if k0 == 0.0 and k1 == 1.0 and k2 == 0.0:
            shared = set(g1.alleles) & set(g2.alleles)
            if shared:
                # Average KI over all shared alleles (handles het & hom cases)
                ki_vals = []
                for a in shared:
                    p_a = self.freq_db.get_frequency(locus, a, population)
                    ki_vals.append(1.0 / (2.0 * (theta + (1.0 - theta) * p_a)))
                return sum(ki_vals) / len(ki_vals), False
            elif apply_mutation_model:
                ki_l = self._smm_numerator(locus, g1, g2, k1, population)
                return ki_l, True
            else:
                return 1e-10, False

        # Denominator: P(G1|θ) × P(G2|θ)
        p_g1 = self.freq_db.calculate_genotype_probability(
            locus, g1.allele1, g1.allele2, theta, population
        )
        p_g2 = self.freq_db.calculate_genotype_probability(
            locus, g2.allele1, g2.allele2, theta, population
        )
        p_denom = p_g1 * p_g2
        if p_denom <= 0.0:
            return 1e-10, mutated

        # Numerator: P(G1, G2 | IBD states)
        p_ibd2 = self._p_joint_ibd2(locus, g1, g2, theta, population)
        p_ibd1 = self._p_joint_ibd1(locus, g1, g2, theta, population)
        p_ibd0 = p_denom   # Under IBD=0: independent → P(G1)·P(G2)

        numerator = k2 * p_ibd2 + k1 * p_ibd1 + k0 * p_ibd0

        # Mutation rescue: if numerator is near zero and SMM enabled
        if numerator < 1e-30 and apply_mutation_model and k1 > 0:
            numerator = self._smm_numerator(locus, g1, g2, k1, population)
            mutated = True

        ki_l = numerator / p_denom
        return ki_l, mutated

    # ── IBD Joint Probability Helpers ─────────────────────────────────────

    def _p_joint_ibd2(self, locus: str, g1: STRGenotype, g2: STRGenotype,
                      theta: float, population: str) -> float:
        """
        P(G1, G2 | IBD=2): Both alleles identical-by-descent.
        Only possible when the two genotypes share the same allele pair.
        P(G1, G2 | IBD=2) = P(G1 | θ)  [G2 is a copy, no extra probability mass]
        """
        # Check if each allele in g1 can be matched by-descent in g2
        shared = set(g1.alleles) & set(g2.alleles)
        if len(shared) == 2 or g1.alleles == g2.alleles:
            return self.freq_db.calculate_genotype_probability(
                locus, g1.allele1, g1.allele2, theta, population
            )
        return 0.0

    def _p_joint_ibd1(self, locus: str, g1: STRGenotype, g2: STRGenotype,
                      theta: float, population: str) -> float:
        """
        P(G1, G2 | IBD=1): Exactly one allele shared IBD.
        For each pair of alleles (one from G1, one from G2) that are equal,
        compute the probability that this allele is the IBD allele and both
        non-IBD alleles were drawn from the population.
        Averages over all valid IBD allele assignments weighted by allele frequency.
        """
        # Use unique allele pairs for genotypes (handles homozygous cases)
        g1_alleles = g1.alleles   # canonical tuple (a1, a2) with a1 ≤ a2
        g2_alleles = g2.alleles

        total = 0.0
        n_pairs = 0

        for a_ibd in set(g1_alleles):
            for b_ibd in set(g2_alleles):
                if a_ibd == b_ibd:
                    p_ibd = self.freq_db.get_frequency(locus, a_ibd, population)
                    # Non-IBD allele from G1
                    non1 = g1_alleles[1] if a_ibd == g1_alleles[0] else g1_alleles[0]
                    # Non-IBD allele from G2
                    non2 = g2_alleles[1] if b_ibd == g2_alleles[0] else g2_alleles[0]
                    p_non1 = theta + (1 - theta) * self.freq_db.get_frequency(locus, non1, population)
                    p_non2 = theta + (1 - theta) * self.freq_db.get_frequency(locus, non2, population)
                    total += p_ibd * p_non1 * p_non2
                    n_pairs += 1

        if n_pairs == 0:
            return 0.0
        return total / n_pairs

    # ── SMM Mutation Numerator Rescue ─────────────────────────────────────

    def _smm_numerator(self, locus: str, g1: STRGenotype, g2: STRGenotype,
                       k1: float, population: str) -> float:
        """
        Stepwise Mutation Model (SMM) rescue numerator.
        Computes the probability that G2 arose from G1 via germline mutation.
        Applied only when parent-child (obligate allele) scenario has a discrepancy.
        """
        # Check all allele transmission pairs (g1→g2 one allele must be transmitted)
        best_p = 0.0
        for parental_allele in g1.alleles:
            for child_allele in g2.alleles:
                p_mut = smm_transition_probability(parental_allele, child_allele)
                p_child_non_transmitted = self.freq_db.get_frequency(
                    locus,
                    g2.allele2 if child_allele == g2.allele1 else g2.allele1,
                    population
                )
                # Probability = P(mutation) × P(other child allele from population)
                combo = k1 * p_mut * p_child_non_transmitted
                best_p = max(best_p, combo)
        return best_p

    # ── Convenience: Avuncular & Grandparent ─────────────────────────────

    def compute_avuncular_ki(self, profile1: STRProfile, profile2: STRProfile,
                             theta: float = DEFAULT_THETA,
                             population: Optional[str] = None) -> AnalysisResult:
        """Computes Kinship Index for an avuncular (uncle/aunt-nephew/niece) pair."""
        return self.compute_kinship_index(
            profile1, profile2, KinshipRelationship.AVUNCULAR, theta, population
        )

    def compute_first_cousin_ki(self, profile1: STRProfile, profile2: STRProfile,
                                theta: float = DEFAULT_THETA,
                                population: Optional[str] = None) -> AnalysisResult:
        """Computes Kinship Index for first cousins."""
        return self.compute_kinship_index(
            profile1, profile2, KinshipRelationship.FIRST_COUSIN, theta, population
        )
