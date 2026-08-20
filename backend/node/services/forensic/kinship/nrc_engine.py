"""
FORENZA Module 1.3: NRC-II Population Genetics & Substructure Engine.
Production-Grade Biocomputational Service Engine.

Orchestrates:
  - 24-Locus Autosomal STR Profile Likelihood Ratio under Balding-Nichols coancestry theta
  - Demographic Stratification Cross-Comparison (Caucasian, African American, Hispanic, Asian)
  - Weir & Cockerham (1984) Unbiased ANOVA Fst / theta Estimation
  - Dirichlet Compound Multinomial (DCM) Log-Gamma Likelihood Evaluation
  - Diploid Genotype Probability Simplex Normalization Invariant Check
  - Certified Golden Reference Standards (NIST SRM 2391d Comp A/B/C, GIAB NA12878)
  - ENFSI (2017) 7-Tier Bilingual Evaluative Reporting with Prosecutor's Fallacy Shield

Compliance: ISO/IEC 17025:2017 • SWGDAM (2020) • ENFSI (2017) • NRC II (1996)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from node.services.forensic.frequency_db import (
    POPULATION_FREQUENCIES,
    LOCI_24,
    CODIS_20_LOCI,
    NRC_II_P_MIN_RULE_4_1,
)
from node.services.forensic.population.nrc_mathematical_formulation import (
    DirichletCompoundMultinomial,
    BaldingNicholsMatchModel,
    WeirCockerhamEstimator,
    NRC2LikelihoodRatioEngine,
    NRCProfileLRResult,
    SimplexValidationResult,
    DCMResult,
    WeirCockerhamResult,
    DEFAULT_THETA,
    CONSERVATIVE_THETA,
    P_MIN_NRC_II,
)
from node.services.forensic.population.nrc_reference_datasets import (
    NIST1036StratifiedDatabase,
    GOLDEN_REFERENCE_PROFILES,
    ReferenceProfile,
    PopulationDemographicMeta,
    NIST_1036_POPULATION_METADATA,
)


@dataclass(frozen=True)
class DemographicStratificationReport:
    """Multi-population comparison for a single suspect profile."""
    profile_id: Optional[str]
    theta_used: float
    population_lrs: Dict[str, float]
    population_log10_lrs: Dict[str, float]
    verbal_scales_en: Dict[str, str]
    verbal_scales_tr: Dict[str, str]
    min_lr: float
    max_lr: float
    stratification_ratio: float  # max_lr / min_lr


class NRCPopulationEngine:
    """
    Unified production service engine for forensic population genetics,
    Balding-Nichols coancestry correction, and demographic stratification analysis.
    """

    def __init__(self, default_theta: float = DEFAULT_THETA):
        self.default_theta = default_theta

    # ── 1. Single-Source Profile LR Evaluation ───────────────────────────────

    def compute_profile_lr(
        self,
        suspect_profile: Dict[str, Tuple[float, float]],
        evidence_profile: Optional[Dict[str, Tuple[float, float]]] = None,
        population: str = "Caucasian",
        theta: Optional[float] = None,
        p_min: float = P_MIN_NRC_II
    ) -> NRCProfileLRResult:
        """
        Computes the composite 24-locus Likelihood Ratio under NRC-II / Balding-Nichols.
        """
        evid_prof = evidence_profile or suspect_profile
        used_theta = theta if theta is not None else self.default_theta

        pop_freqs = POPULATION_FREQUENCIES.get(
            population, POPULATION_FREQUENCIES.get("Caucasian", {})
        )

        return NRC2LikelihoodRatioEngine.compute_profile_lr(
            suspect_profile=suspect_profile,
            evidence_profile=evid_prof,
            population_frequencies=pop_freqs,
            theta=used_theta,
            population_name=population,
            p_min=p_min
        )

    # ── 2. Demographic Stratification Cross-Comparison ───────────────────────

    def evaluate_demographic_stratification(
        self,
        suspect_profile: Dict[str, Tuple[float, float]],
        theta: Optional[float] = None,
        profile_id: Optional[str] = None
    ) -> DemographicStratificationReport:
        """
        Evaluates the evidence LR across all 4 NIST 1036 demographic populations.
        """
        used_theta = theta if theta is not None else self.default_theta
        pop_lrs: Dict[str, float] = {}
        pop_log10_lrs: Dict[str, float] = {}
        verbal_en: Dict[str, str] = {}
        verbal_tr: Dict[str, str] = {}

        for pop_name in ["Caucasian", "AfricanAmerican", "Hispanic", "Asian"]:
            res = self.compute_profile_lr(
                suspect_profile=suspect_profile,
                population=pop_name,
                theta=used_theta
            )
            pop_lrs[pop_name] = res.total_lr
            pop_log10_lrs[pop_name] = res.log10_total_lr
            verbal_en[pop_name] = res.verbal_scale_en
            verbal_tr[pop_name] = res.verbal_scale_tr

        valid_lrs = [lr for lr in pop_lrs.values() if math.isfinite(lr) and lr > 0]
        min_lr = min(valid_lrs) if valid_lrs else 1.0
        max_lr = max(valid_lrs) if valid_lrs else 1.0
        ratio = max_lr / min_lr if min_lr > 0 else 1.0

        return DemographicStratificationReport(
            profile_id=profile_id,
            theta_used=used_theta,
            population_lrs=pop_lrs,
            population_log10_lrs=pop_log10_lrs,
            verbal_scales_en=verbal_en,
            verbal_scales_tr=verbal_tr,
            min_lr=min_lr,
            max_lr=max_lr,
            stratification_ratio=ratio
        )

    # ── 3. Weir & Cockerham ANOVA Fst Estimation ─────────────────────────────

    def estimate_weir_cockerham_fst(
        self,
        subpop_allele_counts: Dict[str, Dict[float, int]],
        locus: Optional[str] = None
    ) -> WeirCockerhamResult:
        """
        Estimates unbiased theta_hat across multiple sub-populations for a locus.
        """
        return WeirCockerhamEstimator.estimate_locus_theta(
            subpop_allele_counts=subpop_allele_counts,
            locus=locus
        )

    # ── 4. Dirichlet Compound Multinomial (DCM) Evaluation ───────────────────

    def evaluate_dcm_likelihood(
        self,
        allele_counts: Dict[float, int],
        population: str = "Caucasian",
        locus: str = "TH01",
        theta: Optional[float] = None
    ) -> DCMResult:
        """
        Computes Dirichlet Compound Multinomial log-likelihood for observed allele counts.
        """
        used_theta = theta if theta is not None else self.default_theta
        pop_db = POPULATION_FREQUENCIES.get(population, POPULATION_FREQUENCIES["Caucasian"])
        locus_freqs = pop_db.get(locus.upper(), {})

        return DirichletCompoundMultinomial.log_likelihood(
            allele_counts=allele_counts,
            allele_freqs=locus_freqs,
            theta=used_theta
        )

    # ── 5. Simplex Normalization Invariant Check ─────────────────────────────

    def validate_locus_simplex(
        self,
        locus: str,
        population: str = "Caucasian",
        theta: Optional[float] = None,
        tolerance: float = 1e-6
    ) -> SimplexValidationResult:
        """
        Validates the mathematical invariant: sum_{i <= j} P(Ai Aj | theta) = 1.00000000 ± 1e-6.
        """
        used_theta = theta if theta is not None else self.default_theta
        pop_db = POPULATION_FREQUENCIES.get(population, POPULATION_FREQUENCIES["Caucasian"])
        locus_freqs = pop_db.get(locus.upper(), {})

        return BaldingNicholsMatchModel.validate_simplex_normalization(
            locus=locus,
            allele_frequencies=locus_freqs,
            theta=used_theta,
            tolerance=tolerance
        )

    # ── 6. Golden Reference Standards Ingestion ──────────────────────────────

    def get_golden_reference_profile(self, profile_id: str) -> ReferenceProfile:
        """
        Retrieves a certified reference individual profile (SRM 2391d Comp A/B/C, NA12878).
        """
        profile = GOLDEN_REFERENCE_PROFILES.get(profile_id)
        if not profile:
            raise KeyError(
                f"Unknown reference profile: '{profile_id}'. "
                f"Supported: {list(GOLDEN_REFERENCE_PROFILES.keys())}"
            )
        return profile

    def list_golden_reference_profiles(self) -> List[Dict[str, Any]]:
        """
        Lists all available certified golden reference profiles.
        """
        return [
            {
                "profile_id": p.profile_id,
                "sample_name": p.sample_name,
                "ethnicity": p.ethnicity,
                "sex": p.sex,
                "num_loci": len(p.loci_genotypes),
                "standard_source": p.standard_source
            }
            for p in GOLDEN_REFERENCE_PROFILES.values()
        ]
