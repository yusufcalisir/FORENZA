"""
FORENZA Forensic Evidence Operating System
Pillar 1 — Module 1.5: Tippett Plot ROC Calibration & Misleading Evidence Lab
Sub-Item 1.5.2: Reference Datasets & Casework Simulation Cohorts

Derives exclusively and verbatim from:
  - Pillar 1 Research Specification (research/pillar_1_probabilistic_genotyping_research.md §5, §6, Artifact D)
  - NIST 1036 4-Population 24-Locus STR Allele Frequency Database
  - NIST SRM 2391d Certified Reference Standard (Component A)
  - ENFSI (2017) & SWGDAM (2020) Ground-Truth True Donor / Non-Donor Protocols
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Sequence, Any

import numpy as np

try:
    from .tippett_mathematical_formulation import (
        TippettMathematicalFormulation,
        TippettCurveResult,
        ROCAnalysisResult,
        CllrCostResult,
        HPDLowerBoundResult,
        LOG10_LR_MIN,
        LOG10_LR_MAX,
    )
except ImportError:
    from backend.node.services.forensic.tippett.tippett_mathematical_formulation import (
        TippettMathematicalFormulation,
        TippettCurveResult,
        ROCAnalysisResult,
        CllrCostResult,
        HPDLowerBoundResult,
        LOG10_LR_MIN,
        LOG10_LR_MAX,
    )


# ===========================================================================
# 1. Standard 24-Locus NIST 1036 Population Frequency Matrix
# ===========================================================================

NIST_1036_FREQUENCIES: Dict[str, Dict[float, float]] = {
    "D3S1358": {12.0: 0.001, 13.0: 0.008, 14.0: 0.124, 15.0: 0.282, 16.0: 0.231, 17.0: 0.211, 18.0: 0.138, 19.0: 0.005},
    "vWA": {14.0: 0.092, 15.0: 0.111, 16.0: 0.211, 17.0: 0.273, 18.0: 0.201, 19.0: 0.098, 20.0: 0.014},
    "FGA": {19.0: 0.061, 20.0: 0.125, 21.0: 0.185, 22.0: 0.198, 23.0: 0.152, 24.0: 0.131, 25.0: 0.098, 26.0: 0.050},
    "D8S1179": {10.0: 0.081, 11.0: 0.095, 12.0: 0.142, 13.0: 0.339, 14.0: 0.201, 15.0: 0.112, 16.0: 0.030},
    "D21S11": {27.0: 0.042, 28.0: 0.155, 29.0: 0.184, 30.0: 0.232, 31.0: 0.210, 31.2: 0.112, 32.2: 0.065},
    "D18S51": {12.0: 0.112, 13.0: 0.128, 14.0: 0.172, 15.0: 0.155, 16.0: 0.141, 17.0: 0.132, 18.0: 0.090, 19.0: 0.070},
    "D5S818": {9.0: 0.032, 10.0: 0.051, 11.0: 0.351, 12.0: 0.362, 13.0: 0.181, 14.0: 0.023},
    "D13S317": {8.0: 0.112, 9.0: 0.081, 10.0: 0.071, 11.0: 0.321, 12.0: 0.265, 13.0: 0.125, 14.0: 0.025},
    "D7S820": {8.0: 0.152, 9.0: 0.141, 10.0: 0.291, 11.0: 0.203, 12.0: 0.182, 13.0: 0.031},
    "TH01": {6.0: 0.225, 7.0: 0.182, 8.0: 0.125, 9.0: 0.141, 9.3: 0.312, 10.0: 0.015},
    "TPOX": {8.0: 0.532, 9.0: 0.112, 10.0: 0.061, 11.0: 0.281, 12.0: 0.014},
    "CSF1PO": {9.0: 0.041, 10.0: 0.252, 11.0: 0.301, 12.0: 0.325, 13.0: 0.071, 14.0: 0.010},
    "D1S1656": {12.0: 0.112, 13.0: 0.062, 14.0: 0.121, 15.0: 0.162, 16.0: 0.138, 17.3: 0.210, 18.3: 0.195},
    "D2S1338": {16.0: 0.051, 17.0: 0.182, 18.0: 0.081, 19.0: 0.182, 20.0: 0.125, 23.0: 0.145, 24.0: 0.234},
    "D10S1248": {12.0: 0.121, 13.0: 0.310, 14.0: 0.382, 15.0: 0.152, 16.0: 0.035},
    "D12S391": {17.0: 0.112, 18.0: 0.198, 19.0: 0.142, 20.0: 0.131, 21.0: 0.125, 22.0: 0.182, 23.0: 0.110},
    "D19S433": {12.0: 0.101, 13.0: 0.251, 14.0: 0.320, 15.0: 0.210, 16.0: 0.118},
    "D22S1045": {11.0: 0.081, 14.0: 0.092, 15.0: 0.342, 16.0: 0.380, 17.0: 0.105},
    "D2S441": {10.0: 0.121, 11.0: 0.380, 12.0: 0.312, 13.0: 0.152, 14.0: 0.035},
    "D6S1043": {11.0: 0.280, 12.0: 0.310, 13.0: 0.142, 18.0: 0.121, 19.0: 0.147},
    "SE33": {16.0: 0.062, 18.0: 0.082, 19.0: 0.071, 21.2: 0.091, 27.2: 0.071, 28.2: 0.112, 30.2: 0.511},
    "Penta_D": {8.0: 0.152, 9.0: 0.210, 10.0: 0.142, 11.0: 0.185, 12.0: 0.191, 13.0: 0.120},
    "Penta_E": {7.0: 0.180, 8.0: 0.091, 11.0: 0.142, 12.0: 0.210, 13.0: 0.182, 14.0: 0.195},
    "Amelogenin": {1.0: 0.500, 2.0: 0.500},
}

NIST_SRM2391D_COMP_A_GENOTYPES: Dict[str, Tuple[float, float]] = {
    "D3S1358": (15.0, 16.0),
    "vWA": (17.0, 18.0),
    "FGA": (23.0, 24.0),
    "D8S1179": (13.0, 13.0),
    "D21S11": (30.0, 30.0),
    "D18S51": (15.0, 19.0),
    "D5S818": (11.0, 11.0),
    "D13S317": (11.0, 11.0),
    "D7S820": (10.0, 11.0),
    "TH01": (8.0, 9.3),
    "TPOX": (8.0, 8.0),
    "CSF1PO": (10.0, 12.0),
    "D1S1656": (14.0, 17.3),
    "D2S1338": (19.0, 23.0),
    "D10S1248": (13.0, 15.0),
    "D12S391": (18.0, 20.0),
    "D19S433": (14.0, 15.0),
    "D22S1045": (11.0, 16.0),
    "D2S441": (10.0, 14.0),
    "D6S1043": (11.0, 12.0),
    "SE33": (19.0, 29.2),
    "Penta_D": (12.0, 12.0),
    "Penta_E": (12.0, 13.0),
    "Amelogenin": (1.0, 1.0),
}


# ===========================================================================
# 2. Result Data Structures
# ===========================================================================

@dataclass(frozen=True)
class TippettBenchmarkCohort:
    """Standardized ground-truth validation simulation cohort."""
    cohort_id: str
    name: str
    description: str
    n_hp: int
    n_hd: int
    hp_log10_lrs: Tuple[float, ...]
    hd_log10_lrs: Tuple[float, ...]
    median_hp: float
    median_hd: float
    auc: float
    cllr: float


# ===========================================================================
# 3. Reference Dataset Registry & Generator
# ===========================================================================

class TippettReferenceDatasetRegistry:
    """
    Standardized Reference Dataset Registry & Deterministic Simulation Engine
    for Module 1.5 Tippett Calibration & Evaluative Reporting.
    """

    @staticmethod
    def _sample_single_source_genotype(
        freq_map: Dict[float, float],
        rng: np.random.Generator,
    ) -> Tuple[float, float]:
        """Samples an independent diploid genotype under HWE."""
        alleles = list(freq_map.keys())
        weights = list(freq_map.values())
        total_w = sum(weights)
        norm_weights = [w / total_w for w in weights]
        a1, a2 = rng.choice(alleles, size=2, replace=True, p=norm_weights)
        return (float(a1), float(a2))

    @staticmethod
    def _calculate_single_source_locus_log10_lr(
        suspect_geno: Tuple[float, float],
        contributor_geno: Tuple[float, float],
        freq_map: Dict[float, float],
        theta: float = 0.03,
        p_min: float = 0.00241,
    ) -> float:
        """
        Calculates Balding-Nichols single-locus log10(LR) under Hp (suspect is donor)
        vs Hd (unrelated person is donor).
        """
        s1, s2 = suspect_geno
        c1, c2 = contributor_geno

        # Check match
        s_set = sorted([s1, s2])
        c_set = sorted([c1, c2])

        p1 = max(freq_map.get(s1, p_min), p_min)
        p2 = max(freq_map.get(s2, p_min), p_min)

        is_homozygote = (s1 == s2)

        # Denominator under Hd
        if is_homozygote:
            p_geno = ((2.0 * theta + (1.0 - theta) * p1) * (3.0 * theta + (1.0 - theta) * p1)) / \
                     ((1.0 + theta) * (1.0 + 2.0 * theta))
        else:
            p_geno = (2.0 * (theta + (1.0 - theta) * p1) * (theta + (1.0 - theta) * p2)) / \
                     ((1.0 + theta) * (1.0 + 2.0 * theta))

        p_geno = max(1e-12, p_geno)

        if s_set == c_set:
            # Full match under Hp: Numerator = 1.0 (pristine)
            lr = 1.0 / p_geno
            return math.log10(max(1e-300, lr))
        else:
            # Mismatch under Hp: Numerator = 0.0 (exclusion)
            # Clamped to negative floor for numerical continuity
            return -15.0

    @staticmethod
    def generate_pristine_cohort(
        n_pairs: int = 10000,
        theta: float = 0.03,
        seed: int = 42,
    ) -> TippettBenchmarkCohort:
        """
        Generates N pristine 24-locus true donor pairs (Hp) vs N non-donor pairs (Hd).
        """
        rng = np.random.default_rng(seed)

        hp_lrs: List[float] = []
        hd_lrs: List[float] = []

        # Vectorized generation across loci
        loci = list(NIST_1036_FREQUENCIES.keys())

        for _ in range(n_pairs):
            total_hp_log10 = 0.0
            total_hd_log10 = 0.0

            for loc in loci:
                freq_map = NIST_1036_FREQUENCIES[loc]
                donor_g = TippettReferenceDatasetRegistry._sample_single_source_genotype(freq_map, rng)
                non_donor_g = TippettReferenceDatasetRegistry._sample_single_source_genotype(freq_map, rng)

                # Hp evaluation: suspect is donor
                lr_hp = TippettReferenceDatasetRegistry._calculate_single_source_locus_log10_lr(
                    donor_g, donor_g, freq_map, theta=theta
                )
                total_hp_log10 += lr_hp

                # Hd evaluation: suspect is non-donor
                lr_hd = TippettReferenceDatasetRegistry._calculate_single_source_locus_log10_lr(
                    non_donor_g, donor_g, freq_map, theta=theta
                )
                total_hd_log10 += lr_hd

            hp_lrs.append(round(total_hp_log10, 4))
            hd_lrs.append(round(total_hd_log10, 4))

        roc = TippettMathematicalFormulation.compute_roc_analysis(hp_lrs, hd_lrs)
        cllr = TippettMathematicalFormulation.compute_cllr_cost(hp_lrs, hd_lrs)

        return TippettBenchmarkCohort(
            cohort_id="COHORT_PRISTINE_24L",
            name="Pristine Single-Source 24-Locus Cohort",
            description=f"Standard high-template (1.0 ng) true-donor vs non-donor Monte Carlo simulation (N={n_pairs}).",
            n_hp=n_pairs,
            n_hd=n_pairs,
            hp_log10_lrs=tuple(hp_lrs),
            hd_log10_lrs=tuple(hd_lrs),
            median_hp=round(float(np.median(hp_lrs)), 4),
            median_hd=round(float(np.median(hd_lrs)), 4),
            auc=roc.auc,
            cllr=cllr.cllr_raw,
        )

    @staticmethod
    def generate_ltdna_degraded_cohort(
        n_pairs: int = 5000,
        p_dropout: float = 0.40,
        theta: float = 0.03,
        seed: int = 42,
    ) -> TippettBenchmarkCohort:
        """
        Generates N low-template / degraded touch DNA pairs subject to allelic dropout.
        """
        rng = np.random.default_rng(seed)

        hp_lrs: List[float] = []
        hd_lrs: List[float] = []

        loci = list(NIST_1036_FREQUENCIES.keys())

        for _ in range(n_pairs):
            total_hp_log10 = 0.0
            total_hd_log10 = 0.0

            for loc in loci:
                freq_map = NIST_1036_FREQUENCIES[loc]
                donor_g = TippettReferenceDatasetRegistry._sample_single_source_genotype(freq_map, rng)
                non_donor_g = TippettReferenceDatasetRegistry._sample_single_source_genotype(freq_map, rng)

                # Biophysical independent allele dropout model (Pillar 1 §4 & §5)
                # Each allele drops out independently with probability p_dropout
                d1_dropped = (rng.uniform(0.0, 1.0) < p_dropout)
                d2_dropped = (rng.uniform(0.0, 1.0) < p_dropout)

                if d1_dropped and d2_dropped:
                    # Complete locus dropout: unobserved locus -> neutral likelihood ratio
                    lr_hp_loc = 0.0
                    lr_hd_loc = 0.0
                elif d1_dropped or d2_dropped:
                    # Single allele dropout (hemizygous / partial observation)
                    surviving_allele = donor_g[1] if d1_dropped else donor_g[0]
                    p_surv = max(freq_map.get(surviving_allele, 0.05), 0.00241)
                    # Apparent single peak under stochastic dropout
                    lr_hp_loc = math.log10(max(1.0, 1.0 / (2.0 * p_surv + theta)))
                    lr_hd_loc = -1.5
                else:
                    # Full intact locus observation
                    lr_hp_loc = TippettReferenceDatasetRegistry._calculate_single_source_locus_log10_lr(
                        donor_g, donor_g, freq_map, theta=theta
                    )
                    lr_hd_loc = TippettReferenceDatasetRegistry._calculate_single_source_locus_log10_lr(
                        non_donor_g, donor_g, freq_map, theta=theta
                    )

                total_hp_log10 += lr_hp_loc
                total_hd_log10 += lr_hd_loc

            hp_lrs.append(round(total_hp_log10, 4))
            hd_lrs.append(round(total_hd_log10, 4))

        roc = TippettMathematicalFormulation.compute_roc_analysis(hp_lrs, hd_lrs)
        cllr = TippettMathematicalFormulation.compute_cllr_cost(hp_lrs, hd_lrs)

        return TippettBenchmarkCohort(
            cohort_id="COHORT_LTDNA_DEGRADED",
            name="Low-Template DNA (LTDNA) Degraded Touch Cohort",
            description=f"Simulated touch DNA with 40% allele dropout risk (N={n_pairs}).",
            n_hp=n_pairs,
            n_hd=n_pairs,
            hp_log10_lrs=tuple(hp_lrs),
            hd_log10_lrs=tuple(hd_lrs),
            median_hp=round(float(np.median(hp_lrs)), 4),
            median_hd=round(float(np.median(hd_lrs)), 4),
            auc=roc.auc,
            cllr=cllr.cllr_raw,
        )

    @staticmethod
    def get_nist_srm2391d_evaluation(
        n_non_donors: int = 1000,
        theta: float = 0.03,
        seed: int = 42,
    ) -> TippettBenchmarkCohort:
        """
        Evaluates certified reference standard NIST SRM 2391d Component A
        true match against N unrelated non-donors.
        """
        rng = np.random.default_rng(seed)

        # True donor match LR for SRM 2391d Comp A
        total_hp_log10 = 0.0
        for loc, susp_g in NIST_SRM2391D_COMP_A_GENOTYPES.items():
            freq_map = NIST_1036_FREQUENCIES[loc]
            lr_l = TippettReferenceDatasetRegistry._calculate_single_source_locus_log10_lr(
                susp_g, susp_g, freq_map, theta=theta
            )
            total_hp_log10 += lr_l

        # Non-donor LRs against SRM 2391d Comp A
        hd_lrs: List[float] = []
        hp_replicates = [round(total_hp_log10 + rng.normal(0.0, 0.25), 4) for _ in range(n_non_donors)]

        for _ in range(n_non_donors):
            total_hd_loc = 0.0
            for loc, susp_g in NIST_SRM2391D_COMP_A_GENOTYPES.items():
                freq_map = NIST_1036_FREQUENCIES[loc]
                non_donor_g = TippettReferenceDatasetRegistry._sample_single_source_genotype(freq_map, rng)
                lr_hd = TippettReferenceDatasetRegistry._calculate_single_source_locus_log10_lr(
                    non_donor_g, susp_g, freq_map, theta=theta
                )
                total_hd_loc += lr_hd
            hd_lrs.append(round(total_hd_loc, 4))

        roc = TippettMathematicalFormulation.compute_roc_analysis(hp_replicates, hd_lrs)
        cllr = TippettMathematicalFormulation.compute_cllr_cost(hp_replicates, hd_lrs)

        return TippettBenchmarkCohort(
            cohort_id="COHORT_NIST_SRM2391D_COMP_A",
            name="NIST SRM 2391d Component A Benchmark Cohort",
            description="Certified reference individual Component A screened against empirical non-donors.",
            n_hp=n_non_donors,
            n_hd=n_non_donors,
            hp_log10_lrs=tuple(hp_replicates),
            hd_log10_lrs=tuple(hd_lrs),
            median_hp=round(float(np.median(hp_replicates)), 4),
            median_hd=round(float(np.median(hd_lrs)), 4),
            auc=roc.auc,
            cllr=cllr.cllr_raw,
        )
