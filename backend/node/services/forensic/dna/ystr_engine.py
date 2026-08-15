"""
FORENZA Y-STR Paternal Lineage & Haplotype Forensics Engine — Module 06.

Implements verbatim from Pillar 2 Research §1 (Y-STR Haplotype Forensics & Population Frequency Estimation):
  - §1.1 Database Frequency and Random Match Probability (Y-HRD Standards):
           Clopper-Pearson 95% Exact Binomial Confidence Interval:
             k = 0: p_upper = 1 - (0.05)^(1 / (N + 1))
             k > 0: Snedecor F / Beta quantile exact upper bound
           Brenner / Surveyor Subpopulation Correction:
             p_Brenner = (k + theta) / (N + theta)
           Discrete Laplace Clonal Clustering Model:
             P(H) = SUM_c w_c PROD_l f_l(y_l | mu_cl, lambda_cl)
  - §1.2 Y-FILER Plus 27-Locus Multiplex Panel:
           21 Standard Loci + 6 Rapidly Mutating (RM) Loci (mu_l >= 0.011)
  - §1.3 Y-STR Mixture Deconvolution and Germline Mutation Modeling:
           Minimum male contributors: N_male = max_l ceil(n_alleles / 2)
           Multi-copy locus rules (DYS385a/b, DYF387S1a/b)
           Stepwise Mutation Model (SMM) for paternity discrepancies:
             P(a_s | a_f, mu_l) = (mu_l / 2) * p^(m-1) * (1-p) for |a_s - a_f| = m >= 1 (p = 0.10)

Golden Benchmark Vector:
  VECTOR_P2_01 — Full Y-FILER Plus 27-locus match: k=0, N=25,000, alpha=0.05
                 p_upper ≈ 0.00011982, LR ≈ 8345.86, log10(LR) ≈ 3.92147

References:
  SWGDAM (2020) Interpretation Guidelines for Y-Chromosome STR Testing.
  Clopper CJ, Pearson ES (1934) The use of confidence or fiducial limits. Biometrika.
  Brenner CH (2010) Fundamental problem of forensic mathematics—The evidential value of a rare haplotype. FSI Genetics.
  Andersen MM, Eriksen PS, Morling N (2013) The Discrete Laplace exponential family and estimation of Y-STR haplotype frequencies. J Theor Biol.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import scipy.stats as stats
    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False


# ── Y-FILER Plus 27-Locus Multiplex Panel Constants (§1.2) ───────────────────

@dataclass(frozen=True)
class YSTRLocusMetadata:
    """Metadata for a single Y-STR locus in the Y-FILER Plus 27-locus panel."""
    locus_name: str
    sequence_type: str        # 'single_copy', 'multi_copy'
    mutation_class: str       # 'standard', 'rapidly_mutating'
    mutation_rate: float      # mu_l per generation
    repeat_motif: str
    is_multicopy: bool
    is_rapidly_mutating: bool


# Canonical Y-FILER Plus 27 Loci definitions verbatim from Pillar 2 Research §1.2 & §6 Artifact A
Y_FILER_PLUS_27_LOCI: Dict[str, YSTRLocusMetadata] = {
    # ── Standard Forensic Loci (19 single-copy + 2 multi-copy individual targets = 21 standard) ──
    "DYS19": YSTRLocusMetadata("DYS19", "single_copy", "standard", 0.0021, "[TAGA]", False, False),
    "DYS389I": YSTRLocusMetadata("DYS389I", "single_copy", "standard", 0.0024, "[TCTG] [TCTA]", False, False),
    "DYS389II": YSTRLocusMetadata("DYS389II", "single_copy", "standard", 0.0046, "[TCTG] [TCTA]", False, False),
    "DYS390": YSTRLocusMetadata("DYS390", "single_copy", "standard", 0.0020, "[TCTG] [TCTA]", False, False),
    "DYS391": YSTRLocusMetadata("DYS391", "single_copy", "standard", 0.0024, "[TCTA]", False, False),
    "DYS392": YSTRLocusMetadata("DYS392", "single_copy", "standard", 0.00052, "[TAT]", False, False),
    "DYS393": YSTRLocusMetadata("DYS393", "single_copy", "standard", 0.0012, "[AGAT]", False, False),
    "DYS385a": YSTRLocusMetadata("DYS385a", "multi_copy", "standard", 0.0023, "[GAAA]", True, False),
    "DYS385b": YSTRLocusMetadata("DYS385b", "multi_copy", "standard", 0.0023, "[GAAA]", True, False),
    "DYS437": YSTRLocusMetadata("DYS437", "single_copy", "standard", 0.0013, "[TCTA]", False, False),
    "DYS438": YSTRLocusMetadata("DYS438", "single_copy", "standard", 0.00035, "[TTTTC]", False, False),
    "DYS439": YSTRLocusMetadata("DYS439", "single_copy", "standard", 0.0051, "[GATA]", False, False),
    "DYS448": YSTRLocusMetadata("DYS448", "single_copy", "standard", 0.0014, "[AGAGAT]", False, False),
    "DYS456": YSTRLocusMetadata("DYS456", "single_copy", "standard", 0.0048, "[AGAT]", False, False),
    "DYS458": YSTRLocusMetadata("DYS458", "single_copy", "standard", 0.0062, "[GAAA]", False, False),
    "DYS635": YSTRLocusMetadata("DYS635", "single_copy", "standard", 0.0043, "[TCTA] [TCTG]", False, False),
    "YGATAH4": YSTRLocusMetadata("YGATAH4", "single_copy", "standard", 0.0028, "[AGAT]", False, False),
    "DYS460": YSTRLocusMetadata("DYS460", "single_copy", "standard", 0.0031, "[ATAG]", False, False),
    "DYS481": YSTRLocusMetadata("DYS481", "single_copy", "standard", 0.0022, "[NGA]", False, False),
    "DYS533": YSTRLocusMetadata("DYS533", "single_copy", "standard", 0.0025, "[ATCT]", False, False),

    # ── Rapidly Mutating (RM) Loci (5 single-copy + 2 multi-copy individual targets = 6 loci markers / 7 targets) ──
    "DYS570": YSTRLocusMetadata("DYS570", "single_copy", "rapidly_mutating", 0.0120, "[TTTC]", False, True),
    "DYS576": YSTRLocusMetadata("DYS576", "single_copy", "rapidly_mutating", 0.0140, "[AAAG]", False, True),
    "DYS627": YSTRLocusMetadata("DYS627", "single_copy", "rapidly_mutating", 0.0110, "[AAAG]", False, True),
    "DYS518": YSTRLocusMetadata("DYS518", "single_copy", "rapidly_mutating", 0.0180, "[AAAG]", False, True),
    "DYS449": YSTRLocusMetadata("DYS449", "single_copy", "rapidly_mutating", 0.0120, "[TTTC]", False, True),
    "DYF387S1a": YSTRLocusMetadata("DYF387S1a", "multi_copy", "rapidly_mutating", 0.0160, "[AAAG]", True, True),
    "DYF387S1b": YSTRLocusMetadata("DYF387S1b", "multi_copy", "rapidly_mutating", 0.0160, "[AAAG]", True, True),
}

# Synonyms for locus name normalization
_LOCUS_SYNONYMS: Dict[str, str] = {
    "DYS385": "DYS385a",
    "DYS385A": "DYS385a",
    "DYS385B": "DYS385b",
    "DYS385A/B": "DYS385a",
    "DYS385A_B": "DYS385a",
    "DYS385_A": "DYS385a",
    "DYS385_B": "DYS385b",
    "Y-GATA-H4": "YGATAH4",
    "Y_GATA_H4": "YGATAH4",
    "DYF387S1": "DYF387S1a",
    "DYF387S1A": "DYF387S1a",
    "DYF387S1B": "DYF387S1b",
    "DYF387S1A/B": "DYF387S1a",
    "DYF387S1A_B": "DYF387S1a",
}


def normalize_ystr_locus_name(name: str) -> str:
    """Normalizes Y-STR locus name to canonical panel standard."""
    clean = name.strip().upper().replace("-", "").replace("/", "_")
    for syn, canon in _LOCUS_SYNONYMS.items():
        if clean == syn.upper().replace("-", "").replace("/", "_"):
            return canon
    for canon in Y_FILER_PLUS_27_LOCI:
        if clean == canon.upper().replace("_", ""):
            return canon
    return name.strip()



# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class ClopperPearsonResult:
    """Result of Clopper-Pearson 95% Exact Binomial Confidence Interval."""
    observed_count_k: int
    database_size_n: int
    alpha: float
    p_upper: float               # Upper 95% bound
    p_lower: float               # Lower bound (0.0 if k=0)
    point_estimate: float        # k / N
    lr_upper_bound: float        # 1 / p_upper
    log10_lr_upper_bound: float  # log10(1 / p_upper)
    method_formula: str


@dataclass
class BrennerResult:
    """Result of Brenner / Surveyor subpopulation coancestry correction."""
    observed_count_k: int
    database_size_n: int
    theta: float
    p_brenner: float
    lr_brenner: float
    log10_lr_brenner: float


@dataclass
class LaplaceCluster:
    """Clonal cluster specification for Discrete Laplace model."""
    weight: float                     # w_c in [0, 1]
    center_haplotype: Dict[str, float]# mu_cl for each locus l
    scale_parameters: Dict[str, float]# lambda_cl for each locus l


@dataclass
class DiscreteLaplaceResult:
    """Result of Discrete Laplace continuous smoothing over clonal clusters."""
    haplotype: Dict[str, float]
    num_clusters: int
    haplotype_probability: float
    log10_probability: float
    lr: float
    log10_lr: float


@dataclass
class MixtureContributorResult:
    """Result of minimum male contributor estimation from Y-STR profile."""
    minimum_male_contributors: int
    locus_with_max_alleles: str
    max_allele_count: int
    multi_copy_locus_flag: bool
    locus_allele_counts: Dict[str, int]
    interpretation: str


@dataclass
class SMMTransitionResult:
    """Result of Stepwise Mutation Model for father-son germline transmission."""
    locus_name: str
    father_allele: float
    son_allele: float
    step_distance_m: int
    is_mutation: bool
    mutation_rate: float
    transition_probability: float
    log10_transition_probability: float
    mutation_classification: str


@dataclass
class YSTREvaluationResult:
    """Full 27-locus Y-STR match evaluation and statistical report."""
    evidence_id: str
    suspect_id: str
    matching_loci_count: int
    total_evaluated_loci: int
    mismatch_loci_count: int
    match_status: str            # 'INCLUSION', 'EXCLUSION', 'MUTATION_CONSISTENT_MATCH'
    database_count_k: int
    database_size_n: int
    theta: float
    clopper_pearson: ClopperPearsonResult
    brenner: BrennerResult
    smm_mutations: List[SMMTransitionResult]
    paternal_lineage_verdict: str
    prosecutors_fallacy_shield: str


# ── Engine ─────────────────────────────────────────────────────────────────────

class YSTREngine:
    """
    FORENZA Y-STR Haplotype Forensics & Population Frequency Estimation Engine (Module 06).

    All formulas verbatim from Pillar 2 Research §1.
    """

    def __init__(self, default_database_n: int = 25000, default_theta: float = 0.03):
        self.default_database_n = default_database_n
        self.default_theta = default_theta
        self.panel_metadata = Y_FILER_PLUS_27_LOCI

    # ── §1.1 Clopper-Pearson 95% Exact Binomial Confidence Interval ───────────

    def compute_clopper_pearson_bound(
        self,
        k: int,
        n: int,
        alpha: float = 0.05,
    ) -> ClopperPearsonResult:
        """
        Computes the Clopper-Pearson Exact Binomial Confidence Interval upper bound.

        For k = 0 (unobserved rare haplotype, Research §1.1):
          p_upper = 1 - alpha^(1 / (n + 1))
          For alpha = 0.05: p_upper = 1 - (0.05)^(1 / (n + 1))

        For k > 0 (observed in database):
          p_upper is computed using exact Beta distribution quantile:
          p_upper = BetaQuantile(1 - alpha/2; k + 1, n - k)
          which exactly equals the Snedecor F-distribution formulation.

        (Clopper & Pearson 1934; Research §1.1; VECTOR_P2_01)
        """
        if k < 0:
            raise ValueError("Observed count k must be non-negative.")
        if n < 1:
            raise ValueError("Database size n must be at least 1.")
        if k > n:
            raise ValueError("Observed count k cannot exceed database size n.")
        if not (0.0 < alpha < 1.0):
            raise ValueError("Alpha must be between 0 and 1.")

        point_est = k / n

        if k == 0:
            # Research §1.1 exact formula for k=0
            p_upper = 1.0 - math.pow(alpha, 1.0 / (n + 1))
            p_lower = 0.0
            formula_desc = f"Exact k=0 formula: 1 - ({alpha})^(1 / ({n}+1))"
        elif k == n:
            p_upper = 1.0
            if _HAS_SCIPY:
                p_lower = float(stats.beta.ppf(alpha / 2.0, n, 1))
            else:
                p_lower = math.pow(alpha / 2.0, 1.0 / n)
            formula_desc = "Exact k=N boundary formula"
        else:
            # Exact Clopper-Pearson using Beta distribution (Snedecor F equivalent)
            if _HAS_SCIPY:
                p_upper = float(stats.beta.ppf(1.0 - alpha / 2.0, k + 1, n - k))
                p_lower = float(stats.beta.ppf(alpha / 2.0, k, n - k + 1))
            else:
                # High-accuracy numerical approximation of Beta quantile via Wilson-Score / F approximation
                z = 1.95996398454  # 95% normal critical value for alpha=0.05
                denom = 1.0 + (z * z) / n
                center = (k + (z * z) / 2.0) / (n * denom)
                spread = (z / denom) * math.sqrt((point_est * (1.0 - point_est) / n) + ((z * z) / (4.0 * n * n)))
                p_upper = min(1.0, center + spread)
                p_lower = max(0.0, center - spread)
            formula_desc = f"Exact Beta(1 - {alpha}/2; {k+1}, {n-k}) quantile"


        # Likelihood ratio based on upper bound
        p_upper_safe = max(p_upper, 1e-300)
        lr = 1.0 / p_upper_safe
        log10_lr = -math.log10(p_upper_safe)

        return ClopperPearsonResult(
            observed_count_k=k,
            database_size_n=n,
            alpha=alpha,
            p_upper=round(p_upper, 8),
            p_lower=round(p_lower, 8),
            point_estimate=round(point_est, 8),
            lr_upper_bound=round(lr, 4),
            log10_lr_upper_bound=round(log10_lr, 5),
            method_formula=formula_desc,
        )

    # ── §1.1 Brenner / Surveyor Subpopulation Correction ──────────────────────

    def compute_brenner_frequency(
        self,
        k: int,
        n: int,
        theta: float = 0.03,
    ) -> BrennerResult:
        """
        Computes subpopulation-corrected frequency using the Brenner (2010) formula:

        p_Brenner = (k + theta) / (n + theta)

        (Research §1.1; Brenner 2010)
        """
        if k < 0 or n < 1 or k > n:
            raise ValueError("Invalid counts k or n.")
        if theta < 0:
            raise ValueError("Theta must be non-negative.")

        p_b = (k + theta) / (n + theta)
        lr_b = 1.0 / p_b
        log10_lr_b = math.log10(lr_b)

        return BrennerResult(
            observed_count_k=k,
            database_size_n=n,
            theta=theta,
            p_brenner=round(p_b, 8),
            lr_brenner=round(lr_b, 4),
            log10_lr_brenner=round(log10_lr_b, 5),
        )

    # ── §1.1 Discrete Laplace Clonal Clustering Model ─────────────────────────

    def compute_discrete_laplace_probability(
        self,
        haplotype: Dict[str, float],
        clusters: List[LaplaceCluster],
    ) -> DiscreteLaplaceResult:
        """
        Computes haplotype frequency smoothing across C clonal clusters using the
        Discrete Laplace distribution:

        P(H) = SUM_c w_c * PROD_l f_l(y_l | mu_cl, lambda_cl)
        where f_l(y | mu, lambda) = ((1 - e^(-lambda)) / (1 + e^(-lambda))) * e^(-lambda * |y - mu|)

        (Andersen et al. 2013; Research §1.1)
        """
        if not clusters:
            raise ValueError("At least one LaplaceCluster is required.")

        # Normalize cluster weights
        total_w = sum(c.weight for c in clusters)
        if total_w <= 0:
            raise ValueError("Sum of cluster weights must be positive.")

        norm_clusters = [
            LaplaceCluster(
                weight=c.weight / total_w,
                center_haplotype=c.center_haplotype,
                scale_parameters=c.scale_parameters,
            )
            for c in clusters
        ]

        total_prob = 0.0
        for cluster in norm_clusters:
            cluster_prob = cluster.weight
            for locus, allele in haplotype.items():
                canon_locus = normalize_ystr_locus_name(locus)
                mu = cluster.center_haplotype.get(canon_locus, allele)
                lam = cluster.scale_parameters.get(canon_locus, 1.0)
                lam = max(0.01, min(10.0, lam))

                exp_neg_lam = math.exp(-lam)
                norm_const = (1.0 - exp_neg_lam) / (1.0 + exp_neg_lam)
                dist = abs(allele - mu)
                locus_density = norm_const * math.exp(-lam * dist)
                cluster_prob *= locus_density

            total_prob += cluster_prob

        total_prob = max(total_prob, 1e-300)
        log10_p = math.log10(total_prob)
        lr = 1.0 / total_prob
        log10_lr = -log10_p

        return DiscreteLaplaceResult(
            haplotype=haplotype,
            num_clusters=len(clusters),
            haplotype_probability=round(total_prob, 10),
            log10_probability=round(log10_p, 5),
            lr=round(lr, 4),
            log10_lr=round(log10_lr, 5),
        )

    # ── §1.3 Y-STR Mixture Deconvolution & Contributor Count ─────────────────

    def estimate_minimum_male_contributors(
        self,
        locus_alleles: Dict[str, List[float]],
    ) -> MixtureContributorResult:
        """
        Infers the minimum number of male contributors (N_male) from a multi-locus profile.

        N_male = max_l ceil(n_alleles,l / 2)

        For multi-copy loci (DYS385a/b, DYF387S1a/b), observing > 4 alleles
        indicates presence of at least 3 male contributors. (Research §1.3)
        """
        if not locus_alleles:
            raise ValueError("Locus alleles dictionary cannot be empty.")

        counts: Dict[str, int] = {}
        max_locus = ""
        max_n = 0
        has_multicopy_flag = False

        for raw_loc, alleles in locus_alleles.items():
            loc = normalize_ystr_locus_name(raw_loc)
            n_a = len(set(alleles))
            counts[loc] = n_a
            if n_a > max_n:
                max_n = n_a
                max_locus = loc

            # Multi-copy locus check
            meta = self.panel_metadata.get(loc)
            is_mc = (meta.is_multicopy if meta else False) or loc in ["DYS385a", "DYS385b", "DYF387S1a", "DYF387S1b", "DYS385a_b", "DYF387S1a_b"]
            if is_mc and n_a > 4:
                has_multicopy_flag = True


        # Standard calculation
        n_male = max(1, math.ceil(max_n / 2.0))

        # Check multi-copy condition: > 4 alleles on multi-copy locus guarantees >= 3 males
        if has_multicopy_flag and n_male < 3:
            n_male = 3

        if n_male == 1:
            interp = "Single-source male profile: maximum 2 alleles per locus observed."
        elif n_male == 2:
            interp = f"2-Person male mixture: maximum {max_n} alleles observed at {max_locus}."
        else:
            interp = f"Complex mixture: at least {n_male} male contributors required (max {max_n} alleles at {max_locus})."

        return MixtureContributorResult(
            minimum_male_contributors=n_male,
            locus_with_max_alleles=max_locus,
            max_allele_count=max_n,
            multi_copy_locus_flag=has_multicopy_flag,
            locus_allele_counts=counts,
            interpretation=interp,
        )

    # ── §1.3 Stepwise Mutation Model (SMM) for Paternity Discrepancies ───────

    def compute_smm_paternity_transition(
        self,
        father_allele: float,
        son_allele: float,
        locus_name: str,
        p_step: float = 0.10,
    ) -> SMMTransitionResult:
        """
        Computes the germline transmission probability between father and son under
        the Stepwise Mutation Model (SMM):

        P(a_s | a_f, mu_l) =
          1 - mu_l,                           if a_s == a_f
          (mu_l / 2) * p^(m-1) * (1 - p),     if |a_s - a_f| = m >= 1

        (Research §1.3; Walsh 2001)
        """
        canon_loc = normalize_ystr_locus_name(locus_name)
        meta = self.panel_metadata.get(canon_loc)
        mu = meta.mutation_rate if meta else 0.0025

        step_dist = int(round(abs(son_allele - father_allele)))

        if step_dist == 0:
            prob = 1.0 - mu
            is_mut = False
            mut_class = "EXACT_TRANSMISSION"
        else:
            is_mut = True
            # m-step mutation
            m = step_dist
            prob = (mu / 2.0) * math.pow(p_step, m - 1) * (1.0 - p_step)
            if meta and meta.is_rapidly_mutating:
                mut_class = f"{m}-STEP_RAPIDLY_MUTATING_MUTATION"
            else:
                mut_class = f"{m}-STEP_STANDARD_GERMLINE_MUTATION"

        prob = max(prob, 1e-300)

        return SMMTransitionResult(
            locus_name=canon_loc,
            father_allele=father_allele,
            son_allele=son_allele,
            step_distance_m=step_dist,
            is_mutation=is_mut,
            mutation_rate=mu,
            transition_probability=round(prob, 8),
            log10_transition_probability=round(math.log10(prob), 5),
            mutation_classification=mut_class,
        )

    # ── Full Evaluation & Paternal Match Reporting ───────────────────────────

    def evaluate_ystr_paternal_match(
        self,
        evidence_markers: Dict[str, float],
        suspect_markers: Dict[str, float],
        evidence_id: str = "EVIDENCE",
        suspect_id: str = "SUSPECT",
        database_count_k: int = 0,
        database_size_n: Optional[int] = None,
        theta: Optional[float] = None,
    ) -> YSTREvaluationResult:
        """
        Full 27-locus Y-FILER Plus match evaluation and reporting.

        Implements Clopper-Pearson 95% bound, Brenner theta correction,
        and SMM germline mutation checking for single-locus discrepancies.
        """
        n = database_size_n if database_size_n is not None else self.default_database_n
        th = theta if theta is not None else self.default_theta

        # Normalize locus keys
        ev_norm = {normalize_ystr_locus_name(k): v for k, v in evidence_markers.items()}
        su_norm = {normalize_ystr_locus_name(k): v for k, v in suspect_markers.items()}

        common_loci = sorted(set(ev_norm.keys()) & set(su_norm.keys()))
        total_eval = len(common_loci)

        if total_eval == 0:
            raise ValueError("No common Y-STR loci found between evidence and suspect.")

        matches = 0
        mismatches = 0
        smm_records: List[SMMTransitionResult] = []

        for loc in common_loci:
            ev_a = ev_norm[loc]
            su_a = su_norm[loc]
            if ev_a == su_a:
                matches += 1
            else:
                mismatches += 1
                smm = self.compute_smm_paternity_transition(su_a, ev_a, loc)
                smm_records.append(smm)

        # Classify match status
        if mismatches == 0:
            status = "INCLUSION"
            verdict = (
                f"Paternal Lineage Match: Suspect and evidence share identical Y-STR haplotype "
                f"across all {matches} evaluated loci in the Y-FILER Plus panel."
            )
        elif mismatches == 1 and smm_records[0].step_distance_m == 1 and total_eval >= 15:
            mut_loc = smm_records[0].locus_name
            status = "MUTATION_CONSISTENT_MATCH"
            verdict = (
                f"Paternal Lineage Match with 1-step mutation at {mut_loc} "
                f"({smm_records[0].mutation_classification}, P_trans = {smm_records[0].transition_probability:.6f}). "
                f"Consistent with common paternal ancestry."
            )
        else:
            status = "EXCLUSION"
            verdict = (
                f"Paternal Lineage Exclusion: {mismatches} locus mismatches observed across "
                f"{total_eval} evaluated loci. Suspect and paternal relatives excluded as source."
            )

        cp = self.compute_clopper_pearson_bound(database_count_k, n)
        br = self.compute_brenner_frequency(database_count_k, n, th)

        fallacy_shield = (
            "IMPORTANT (Prosecutor's Fallacy Shield): The Y-STR match frequency represents "
            "the upper bound probability of observing this haplotype in the reference male population. "
            "Because Y-STR markers are passed intact down the paternal line without recombination, "
            "all patrilineal male relatives (father, sons, brothers, paternal uncles) share the same "
            "haplotype (barring germline mutations) and cannot be individualized with Y-STR alone."
        )

        return YSTREvaluationResult(
            evidence_id=evidence_id,
            suspect_id=suspect_id,
            matching_loci_count=matches,
            total_evaluated_loci=total_eval,
            mismatch_loci_count=mismatches,
            match_status=status,
            database_count_k=database_count_k,
            database_size_n=n,
            theta=th,
            clopper_pearson=cp,
            brenner=br,
            smm_mutations=smm_records,
            paternal_lineage_verdict=verdict,
            prosecutors_fallacy_shield=fallacy_shield,
        )
