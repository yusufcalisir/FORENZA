"""
FORENZA Interpol Disaster Victim Identification (DVI) Cross-Validation Engine (Module 2.4).
Cross-validates against Familias 3 DVI Batch Module, Interpol DVI Standards (2018, 2023), and ENFSI (2017).

Research Source: research/pillar_2_lineage_kinship_research.md §4.
"""

from dataclasses import dataclass
from typing import Dict, List, Any

from .dvi_mathematical_formulation import (
    DviMathematicalFormulation,
    InterpolDecisionTier,
)
from .dvi_reference_datasets import (
    DVI_CASEWORK_COHORTS,
)


@dataclass(frozen=True)
class DviCrossValidationResult:
    tool_name: str
    benchmark_name: str
    computed_value: float
    expected_value: float
    relative_residual: float
    is_concordant: bool
    description: str


class DviCrossValidationEngine:
    """Validates mathematical concordance against published external benchmark systems."""

    @staticmethod
    def cross_validate_vector_p2_03() -> DviCrossValidationResult:
        """
        Cross-validates against Golden Benchmark VECTOR_P2_03 (Research §4.1 & Golden Vectors §2):
        Autosomal LR = 5.2e3, Y-STR p_upper = 0.0002 (LR_Y = 5000), mtDNA p_upper = 0.0001 (LR_M = 10000).
        Expected Combined LR = 2.6e11 (log10 = 11.4149).
        """
        cohort = DVI_CASEWORK_COHORTS["VECTOR_P2_03_DEGRADED_SKELETAL"]
        joint_lr, log10_joint = DviMathematicalFormulation.compute_multi_omic_joint_lr(
            autosomal_lr=cohort.autosomal_lr,
            ystr_p_upper=cohort.ystr_p_upper,
            mtdna_p_upper=cohort.mtdna_p_upper,
            snp_lr=cohort.snp_lr,
            has_ystr=cohort.has_ystr,
            has_mtdna=cohort.has_mtdna,
            has_snp=cohort.has_snp,
        )

        expected_lr = 2.6e11
        rel_diff = abs(joint_lr - expected_lr) / expected_lr
        concordant = abs(log10_joint - 11.4149) < 1e-4

        return DviCrossValidationResult(
            tool_name="Interpol DVI Multi-Omic Fusion Standard",
            benchmark_name="Golden Benchmark VECTOR_P2_03",
            computed_value=joint_lr,
            expected_value=expected_lr,
            relative_residual=round(rel_diff, 6),
            is_concordant=concordant,
            description="Multi-omic evidence fusion combining Autosomal STR, Y-STR, and mtDNA.",
        )

    @staticmethod
    def cross_validate_bayesian_prior_updating() -> DviCrossValidationResult:
        """
        Cross-validates Bayesian posterior probability W = P(H1 | E) updating from prior P(H1) = 0.001.
        For LR = 2.6e11: W = (2.6e11 * 0.001) / (2.6e11 * 0.001 + 0.999) ≈ 0.999999996.
        """
        w = DviMathematicalFormulation.compute_posterior_probability(joint_lr=2.6e11, prior=0.001)
        expected_w = 0.999999996
        rel_diff = abs(w - expected_w)

        return DviCrossValidationResult(
            tool_name="Bayesian Pedigree Posterior Odds Model",
            benchmark_name="Prior Updating P(H1)=0.001 to Posterior W",
            computed_value=w,
            expected_value=expected_w,
            relative_residual=round(rel_diff, 8),
            is_concordant=w > 0.999999,
            description="Bayesian posterior odds updating under Interpol mass disaster prior.",
        )

    @staticmethod
    def get_interpol_dvi_reporting_shield() -> Dict[str, Any]:
        """Returns Interpol DVI Standing Committee & ENFSI reporting guidelines disclaimer."""
        return {
            "has_dvi_disclaimer": True,
            "prosecutors_fallacy_shield_active": True,
            "disclaimer_text_en": (
                "IMPORTANT (Interpol DVI Multi-Omic Legal Shield): Standalone judicial identification "
                "requires LR_Joint >= 10^6 (log10 >= 6.0, Posterior Probability W >= 0.999999). Lower LRs "
                "(10^4 <= LR < 10^6) mandate secondary corroboration by forensic odontology, surgical serial "
                "numbers, or physical marks."
            ),
            "disclaimer_text_tr": (
                "ÖNEMLİ (İnterpol DVI Çoklu-Omik Hukuki Kalkanı): Bağımsız adli kimliklendirme "
                "için Birleşik LR_Joint >= 10^6 (log10 >= 6.0, Sonsal Olasılık W >= 0.999999) şarttır. Daha düşük "
                "oranlar (10^4 <= LR < 10^6) adli diş hekimliği (odontoloji), cerrahi implant seri numaraları veya "
                "fiziksel ayırt edici işaretlerle ikincil doğrulamayı zorunlu kılar."
            ),
        }
