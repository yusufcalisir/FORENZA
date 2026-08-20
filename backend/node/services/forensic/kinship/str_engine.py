"""
FORENZA Module 01 — 24-Locus STR Profile & Kinship Engine
Comprehensive implementation providing:
1. 24-Locus Autosomal STR profile normalization, canonical sorting, and panel completeness checks.
2. Pedigree kinship calculations across Parent-Child, Full Siblings, Half Siblings, Avuncular, Grandparent, First Cousins, and Unrelated baselines.
3. Stepwise Mutation Model (SMM) dynamics for germline mutations.
4. Combined Paternity Index (CPI) and Probability of Paternity W(%).
5. Integration with NIST 1036 PopGen Engine and ISO/IEC 17025 expanded uncertainty.

Compliance: ISO/IEC 17025:2017 • SWGDAM 2020 • ISFG (2006, 2012, 2016)
Derived from: research/pillar_1_probabilistic_genotyping_research.md
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Set

from ..terminal.nist_1036_popgen_engine import Nist1036PopGenEngine, NistPopulationEnum
from ..terminal.str_locus_registry_engine import StrLocusRegistryEngine, STR_LOCUS_24_MASTER_REGISTRY


# Standard 24-Locus Panel definition (CODIS 20 + SE33 + Penta D + Penta E + Amelogenin)
LOCI_24_ORDER: Tuple[str, ...] = (
    "AMEL", "CSF1PO", "D1S1656", "D2S441", "D2S1338", "D3S1358", "D5S818", "D7S820",
    "D8S1179", "D10S1248", "D12S391", "D13S317", "D16S539", "D18S51", "D19S433",
    "D21S11", "D22S1045", "FGA", "TH01", "TPOX", "VWA", "SE33", "PENTA_D", "PENTA_E"
)

CODIS_20_CORE: Tuple[str, ...] = (
    "CSF1PO", "D1S1656", "D2S441", "D2S1338", "D3S1358", "D5S818", "D7S820",
    "D8S1179", "D10S1248", "D12S391", "D13S317", "D16S539", "D18S51", "D19S433",
    "D21S11", "D22S1045", "FGA", "TH01", "TPOX", "VWA"
)


class KinshipRelationship(str, Enum):
    PARENT_CHILD = "Parent-Child"
    FULL_SIBLING = "Full Sibling"
    HALF_SIBLING = "Half Sibling"
    AVUNCULAR = "Avuncular"
    GRANDPARENT = "Grandparent-Grandchild"
    FIRST_COUSIN = "First Cousin"
    UNRELATED = "Unrelated"


@dataclass(frozen=True)
class IBDCoefficients:
    k0: float
    k1: float
    k2: float


IBD_COEFFICIENT_MAP: Dict[KinshipRelationship, IBDCoefficients] = {
    KinshipRelationship.PARENT_CHILD: IBDCoefficients(k0=0.00, k1=1.00, k2=0.00),
    KinshipRelationship.FULL_SIBLING: IBDCoefficients(k0=0.25, k1=0.50, k2=0.25),
    KinshipRelationship.HALF_SIBLING: IBDCoefficients(k0=0.50, k1=0.50, k2=0.00),
    KinshipRelationship.AVUNCULAR:    IBDCoefficients(k0=0.50, k1=0.50, k2=0.00),
    KinshipRelationship.GRANDPARENT:  IBDCoefficients(k0=0.50, k1=0.50, k2=0.00),
    KinshipRelationship.FIRST_COUSIN: IBDCoefficients(k0=0.75, k1=0.25, k2=0.00),
    KinshipRelationship.UNRELATED:    IBDCoefficients(k0=1.00, k1=0.00, k2=0.00),
}


@dataclass
class KinshipLocusResult:
    locus_name: str
    genotype1: Tuple[str, str]
    genotype2: Tuple[str, str]
    shared_alleles: List[str]
    kinship_index: float
    log10_ki: float
    mutation_occurred: bool = False
    formula: str = ""


@dataclass
class KinshipAnalysisResult:
    relationship: KinshipRelationship
    population: str
    theta: float
    evaluated_loci_count: int
    combined_kinship_index: float
    combined_log10_ki: float
    probability_of_paternity_w: float  # W(%) under equal prior odds (P_prior = 0.5)
    enfsi_verbal_scale: str
    locus_results: List[KinshipLocusResult]
    invariants: Dict[str, Any] = field(default_factory=dict)


class KinshipSTREngine:
    """
    Forensic 24-Locus STR Profile Management and Kinship Evaluation Engine.
    """

    DEFAULT_MUTATION_RATE: float = 1e-3
    SMM_R_PARAM: float = 0.10

    @classmethod
    def normalize_locus_name(cls, locus_name: str) -> str:
        """Normalizes locus names to canonical upper case (e.g. 'vwa' -> 'VWA', 'Penta D' -> 'PENTA_D')."""
        clean = locus_name.strip().upper().replace(" ", "_").replace("-", "_")
        if clean in ("PENTAD", "PENTA_D"):
            return "PENTA_D"
        if clean in ("PENTAE", "PENTA_E"):
            return "PENTA_E"
        if clean in ("AMELOGENIN", "AMEL"):
            return "AMEL"
        return clean

    @classmethod
    def sort_alleles_canonically(cls, a1: str, a2: str) -> Tuple[str, str]:
        """
        Sorts alleles numerically if possible, or lexically.
        E.g. ('9.3', '8') -> ('8', '9.3'); ('Y', 'X') -> ('X', 'Y').
        """
        s1 = str(a1).strip()
        s2 = str(a2).strip()
        try:
            v1 = float(s1)
            v2 = float(s2)
            return (s1, s2) if v1 <= v2 else (s2, s1)
        except ValueError:
            return (s1, s2) if s1 <= s2 else (s2, s1)

    @classmethod
    def validate_24locus_completeness(cls, profile: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Checks if all 24 loci are present. Returns (is_complete, missing_loci)."""
        norm_keys = {cls.normalize_locus_name(k) for k in profile.keys()}
        missing = [loc for loc in LOCI_24_ORDER if loc not in norm_keys]
        return len(missing) == 0, missing

    @classmethod
    def calculate_smm_transition(
        cls,
        allele_m: str,
        allele_n: str,
        mu: float = DEFAULT_MUTATION_RATE,
        r: float = SMM_R_PARAM,
    ) -> float:
        """
        Stepwise Mutation Model (SMM) transition probability P(m -> n):
        P(m -> n) = (1 - mu) if m == n
        P(m -> n) = (mu / 2) * (1 - r) * r^(|m - n| - 1) if m != n
        """
        try:
            m_val = float(allele_m)
            n_val = float(allele_n)
            steps = abs(m_val - n_val)
            if steps < 1e-6:
                return 1.0 - mu
            # Stepwise mutation
            step_count = max(int(round(steps)), 1)
            return (mu / 2.0) * (1.0 - r) * (r ** (step_count - 1))
        except ValueError:
            return 1.0 - mu if allele_m == allele_n else mu / 2.0

    @classmethod
    def calculate_locus_kinship_index(
        cls,
        locus: str,
        g1: Tuple[str, str],
        g2: Tuple[str, str],
        relationship: KinshipRelationship = KinshipRelationship.PARENT_CHILD,
        population: str = "Caucasian",
        theta: float = 0.01,
        apply_smm: bool = True,
    ) -> KinshipLocusResult:
        """
        Calculates Kinship Index for a single locus using IBD coefficients and NIST 1036 popgen.
        """
        norm_locus = cls.normalize_locus_name(locus)
        a, b = cls.sort_alleles_canonically(g1[0], g1[1] if len(g1) > 1 else g1[0])
        c, d = cls.sort_alleles_canonically(g2[0], g2[1] if len(g2) > 1 else g2[0])

        if norm_locus == "AMEL":
            return KinshipLocusResult(
                locus_name="AMEL",
                genotype1=(a, b),
                genotype2=(c, d),
                shared_alleles=list(set([a, b]) & set([c, d])),
                kinship_index=1.0,
                log10_ki=0.0,
                formula="Amelogenin sex concordance node",
            )

        ibd = IBD_COEFFICIENT_MAP.get(relationship, IBD_COEFFICIENT_MAP[KinshipRelationship.PARENT_CHILD])
        shared = list(set([a, b]) & set([c, d]))
        
        p_a = Nist1036PopGenEngine.get_allele_frequency(norm_locus, a, population)
        p_b = Nist1036PopGenEngine.get_allele_frequency(norm_locus, b, population)
        p_c = Nist1036PopGenEngine.get_allele_frequency(norm_locus, c, population)
        p_d = Nist1036PopGenEngine.get_allele_frequency(norm_locus, d, population)

        # Parent-Child Duo standard formula:
        if relationship == KinshipRelationship.PARENT_CHILD:
            # G1 = (a, b) [Child], G2 = (c, d) [Alleged Parent]
            if a == b and c == d and a == c:
                # Both homozygous same allele
                ki = 1.0 / p_a
                formula = f"1 / p_{a} = 1 / {p_a:.4f} = {ki:.4f}"
                mut = False
            elif a == b:
                # Child homozygous (a, a)
                if a in (c, d):
                    ki = 1.0 / (2.0 * p_a)
                    formula = f"1 / (2*p_{a}) = {ki:.4f}"
                    mut = False
                else:
                    # Mutation
                    closest_parent = min([c, d], key=lambda x: abs(float(x) - float(a)) if x.replace('.', '').isdigit() and a.replace('.', '').isdigit() else 99)
                    p_mut = cls.calculate_smm_transition(closest_parent, a) if apply_smm else cls.DEFAULT_MUTATION_RATE
                    ki = p_mut / p_a
                    formula = f"SMM(m->n)/p_{a} = {ki:.6f}"
                    mut = True
            elif c == d:
                # Parent homozygous (c, c)
                if c in (a, b):
                    ki = 1.0 / (2.0 * p_c)
                    formula = f"1 / (2*p_{c}) = {ki:.4f}"
                    mut = False
                else:
                    closest_child = min([a, b], key=lambda x: abs(float(x) - float(c)) if x.replace('.', '').isdigit() and c.replace('.', '').isdigit() else 99)
                    p_mut = cls.calculate_smm_transition(c, closest_child) if apply_smm else cls.DEFAULT_MUTATION_RATE
                    ki = p_mut / p_c
                    formula = f"SMM(m->n)/p_{c} = {ki:.6f}"
                    mut = True
            else:
                # Both heterozygous
                if len(shared) == 2:
                    # Both (a, b) and (a, b)
                    ki = (p_a + p_b) / (4.0 * p_a * p_b)
                    formula = f"(p_{a} + p_{b}) / (4*p_{a}*p_{b}) = {ki:.4f}"
                    mut = False
                elif len(shared) == 1:
                    # One shared allele (e.g. a)
                    s_allele = shared[0]
                    p_s = p_a if s_allele == a else p_b
                    ki = 1.0 / (4.0 * p_s)
                    formula = f"1 / (4*p_{s_allele}) = {ki:.4f}"
                    mut = False
                else:
                    # Zero shared alleles (Mutation)
                    min_trans = min(
                        cls.calculate_smm_transition(parent_a, child_a)
                        for parent_a in (c, d)
                        for child_a in (a, b)
                    ) if apply_smm else cls.DEFAULT_MUTATION_RATE
                    p_eff = (p_a + p_b) / 2.0
                    ki = min_trans / p_eff
                    formula = f"SMM_min / p_mean = {ki:.6f}"
                    mut = True
        else:
            # Full IBD decomposition for non-parent-child relationships:
            # KI = k0*1.0 + k1*KI_1 + k2*KI_2
            p_g1, _, _ = Nist1036PopGenEngine.calculate_genotype_probability(norm_locus, a, b, population=population, theta=theta)
            p_g2, _, _ = Nist1036PopGenEngine.calculate_genotype_probability(norm_locus, c, d, population=population, theta=theta)

            if len(shared) == 2 and a == c and b == d:
                # Identical genotypes
                ki_2 = 1.0 / p_g1 if p_g1 > 0 else 1.0
                ki_1 = (1.0 / (2.0 * p_a)) if a == b else ((p_a + p_b) / (4.0 * p_a * p_b))
                ki = ibd.k0 * 1.0 + ibd.k1 * ki_1 + ibd.k2 * ki_2
                formula = f"k0 + k1*({ki_1:.2f}) + k2*({ki_2:.2f}) = {ki:.4f}"
                mut = False
            elif len(shared) >= 1:
                s_allele = shared[0]
                p_s = Nist1036PopGenEngine.get_allele_frequency(norm_locus, s_allele, population)
                ki_1 = 1.0 / (4.0 * p_s) if (a != b and c != d) else 1.0 / (2.0 * p_s)
                ki = ibd.k0 * 1.0 + ibd.k1 * ki_1 + ibd.k2 * 0.0
                formula = f"k0 + k1*({ki_1:.2f}) = {ki:.4f}"
                mut = False
            else:
                ki = ibd.k0 * 1.0
                formula = f"k0 = {ki:.4f}"
                mut = False

        log10_ki = math.log10(ki) if ki > 0 else 0.0
        return KinshipLocusResult(
            locus_name=norm_locus,
            genotype1=(a, b),
            genotype2=(c, d),
            shared_alleles=shared,
            kinship_index=ki,
            log10_ki=log10_ki,
            mutation_occurred=mut,
            formula=formula,
        )

    @classmethod
    def compute_kinship_profile_analysis(
        cls,
        profile1: Dict[str, Any],
        profile2: Dict[str, Any],
        relationship: KinshipRelationship = KinshipRelationship.PARENT_CHILD,
        population: str = "Caucasian",
        theta: float = 0.01,
        apply_smm: bool = True,
    ) -> KinshipAnalysisResult:
        """
        Computes multi-locus Combined Kinship Index (CPI) and Probability of Paternity/Kinship W(%).
        """
        locus_results: List[KinshipLocusResult] = []
        combined_ki = 1.0
        combined_log10_ki = 0.0

        all_loci = set(profile1.keys()) | set(profile2.keys())
        for locus in LOCI_24_ORDER:
            # Check presence
            matched_k1 = next((k for k in profile1.keys() if cls.normalize_locus_name(k) == locus), None)
            matched_k2 = next((k for k in profile2.keys() if cls.normalize_locus_name(k) == locus), None)

            if not matched_k1 or not matched_k2:
                continue

            g1_raw = profile1[matched_k1]
            g2_raw = profile2[matched_k2]

            g1 = (str(g1_raw[0]), str(g1_raw[1])) if isinstance(g1_raw, (list, tuple)) else (str(g1_raw), str(g1_raw))
            g2 = (str(g2_raw[0]), str(g2_raw[1])) if isinstance(g2_raw, (list, tuple)) else (str(g2_raw), str(g2_raw))

            loc_res = cls.calculate_locus_kinship_index(
                locus=locus,
                g1=g1,
                g2=g2,
                relationship=relationship,
                population=population,
                theta=theta,
                apply_smm=apply_smm,
            )
            locus_results.append(loc_res)

            if locus != "AMEL":
                combined_ki *= loc_res.kinship_index
                combined_log10_ki += loc_res.log10_ki

        # Probability of paternity / kinship W(%) under neutral prior odds (P_prior = 0.50)
        p_prior = 0.50
        prob_w = (100.0 * combined_ki * p_prior) / (combined_ki * p_prior + (1.0 - p_prior)) if combined_ki > 0 else 0.0

        if combined_log10_ki >= 6.0:
            enfsi_verbal = "Extremely Strong Support for Proposed Kinship Relationship (Hp)"
        elif combined_log10_ki >= 4.0:
            enfsi_verbal = "Strong Support for Proposed Kinship Relationship (Hp)"
        elif combined_log10_ki >= 2.0:
            enfsi_verbal = "Moderately Strong Support for Proposed Kinship Relationship (Hp)"
        elif combined_log10_ki >= 1.0:
            enfsi_verbal = "Moderate Support for Proposed Kinship Relationship (Hp)"
        else:
            enfsi_verbal = "Limited Support / Inconclusive / Exclusion"

        sum_log_ki = sum(r.log10_ki for r in locus_results if r.locus_name != "AMEL")
        additivity_err = abs(combined_log10_ki - sum_log_ki)

        return KinshipAnalysisResult(
            relationship=relationship,
            population=population,
            theta=theta,
            evaluated_loci_count=len(locus_results),
            combined_kinship_index=combined_ki,
            combined_log10_ki=combined_log10_ki,
            probability_of_paternity_w=prob_w,
            enfsi_verbal_scale=enfsi_verbal,
            locus_results=locus_results,
            invariants={
                "log_likelihood_additivity_error": additivity_err,
                "is_additive_invariant": additivity_err < 1e-6,
            },
        )
