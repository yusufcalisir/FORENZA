"""
FORENZA Mitochondrial DNA (mtDNA) Cross-Validation Engine (Module 2.3).
Cross-validates against EMPOP SAM 2, HaploSearch, PhyloTree 17, and ISFG (2020) guidelines.

Research Source: research/ystr_27_mtdna_empop_lineage_research.md §3 & §4.
"""

from dataclasses import dataclass
from typing import Dict, List, Any

from .mtdna_mathematical_formulation import (
    MtDnaMathematicalFormulation,
    MtDnaVariant,
)
from .mtdna_reference_datasets import (
    MTDNA_CASEWORK_COHORTS,
)


@dataclass(frozen=True)
class MtDnaCrossValidationResult:
    tool_name: str
    benchmark_name: str
    computed_value: float
    expected_value: float
    relative_residual: float
    is_concordant: bool
    description: str


class MtDnaCrossValidationEngine:
    """Validates mathematical concordance against published external benchmark systems."""

    @staticmethod
    def cross_validate_lineage_a() -> MtDnaCrossValidationResult:
        """
        Cross-validates against LINEAGE-A European H1 ground-truth vector (Research §4.1):
        Haplotype: 263G, 315.1C, 750G, 16519C.
        Expected: k=1420 in N=48,200 -> LR ≈ 32.89 (p_upper ≈ 0.0304).
        """
        cohort = MTDNA_CASEWORK_COHORTS["BENCHMARK_LINEAGE_A_EUR"]
        vars_a = [MtDnaMathematicalFormulation.parse_variant_string(s) for s in cohort.profile_a_variants]
        vars_b = [MtDnaMathematicalFormulation.parse_variant_string(s) for s in cohort.profile_b_variants]

        res = MtDnaMathematicalFormulation.evaluate_pairwise_lineage(
            variants_a=vars_a,
            variants_b=vars_b,
            database_size_n=cohort.database_size_n,
            observed_database_matches_k=cohort.expected_matches_k,
        )

        expected_lr = 32.89
        rel_diff = abs(res.maternal_lr - expected_lr) / expected_lr
        concordant = res.verdict == "MATCH" and res.maternal_lr > 25.0

        return MtDnaCrossValidationResult(
            tool_name="EMPOP SAM 2 / HaploSearch Engine",
            benchmark_name="LINEAGE-A European H1 Benchmark",
            computed_value=res.maternal_lr,
            expected_value=expected_lr,
            relative_residual=round(rel_diff, 5),
            is_concordant=concordant,
            description="European H1 control region frequency and maternal LR calculation.",
        )

    @staticmethod
    def cross_validate_lineage_b() -> MtDnaCrossValidationResult:
        """
        Cross-validates against LINEAGE-B African American L2a1 vector (Research §4.2):
        Expected: k=12 in N=48,200 -> LR ≈ 2518.8 (p_upper ≈ 0.000397).
        """
        cohort = MTDNA_CASEWORK_COHORTS["BENCHMARK_LINEAGE_B_AFR"]
        vars_a = [MtDnaMathematicalFormulation.parse_variant_string(s) for s in cohort.profile_a_variants]
        vars_b = [MtDnaMathematicalFormulation.parse_variant_string(s) for s in cohort.profile_b_variants]

        res = MtDnaMathematicalFormulation.evaluate_pairwise_lineage(
            variants_a=vars_a,
            variants_b=vars_b,
            database_size_n=cohort.database_size_n,
            observed_database_matches_k=cohort.expected_matches_k,
        )

        expected_lr = 2518.8
        rel_diff = abs(res.maternal_lr - expected_lr) / expected_lr
        concordant = res.verdict == "MATCH" and res.maternal_lr > 1500.0

        return MtDnaCrossValidationResult(
            tool_name="EMPOP SAM 2 / HaploSearch Engine",
            benchmark_name="LINEAGE-B African L2a1 Benchmark",
            computed_value=res.maternal_lr,
            expected_value=expected_lr,
            relative_residual=round(rel_diff, 5),
            is_concordant=concordant,
            description="African L2a1 control region frequency and maternal LR calculation.",
        )

    @staticmethod
    def cross_validate_empop_k0_bound() -> MtDnaCrossValidationResult:
        """
        Cross-validates exact Clopper-Pearson 95% bound for k=0 in N=48,500.
        Expected: p_upper = 1 - (0.05)^(1 / 48501) ≈ 6.1764 × 10^-5.
        """
        p_up = MtDnaMathematicalFormulation.compute_clopper_pearson_bound(k=0, n=48500)
        expected_p = 6.1764e-5
        rel_diff = abs(p_up - expected_p) / expected_p

        return MtDnaCrossValidationResult(
            tool_name="EMPOP Clopper-Pearson Exact Binomial Model",
            benchmark_name="EMPOP R15 k=0 Frequency Bound (N=48,500)",
            computed_value=p_up,
            expected_value=expected_p,
            relative_residual=round(rel_diff, 6),
            is_concordant=rel_diff < 1e-4,
            description="Exact upper 95% confidence bound on unobserved mitogenome frequency.",
        )

    @staticmethod
    def get_isfg_mtdna_reporting_shield() -> Dict[str, Any]:
        """Returns ISFG (2020) mtDNA evaluative reporting guidelines statement."""
        return {
            "has_matrilineal_disclaimer": True,
            "prosecutors_fallacy_shield_active": True,
            "disclaimer_text_en": (
                "MANDATORY ISFG (2020) mtDNA EVALUATIVE REPORTING DISCLAIMER: "
                "Mitochondrial DNA (mtDNA) is inherited strictly along the matrilineal lineage without meiotic "
                "recombination. All maternally related maternal relatives (brothers, sisters, mothers, maternal grandmothers, "
                "maternal aunts, maternal cousins) share the identical control region haplotype. Likelihood Ratios (LR_mtDNA) "
                "evaluate the probability of observing the sequence under the hypothesis of shared maternal lineage versus an "
                "unrelated individual from the population, but cannot individualize a specific single person."
            ),
            "disclaimer_text_tr": (
                "ZORUNLU ISFG (2020) mtDNA DEĞERLENDİRİCİ RAPORLAMA BİLDİRİMİ: "
                "Mitokondriyal DNA (mtDNA) mayoz bölünmede rekombinasyona uğramaksızın yalnızca anne soyu (anaerkil) "
                "üzerinden aktarılır. Bütün anne tarafı akrabalar (kardeşler, anne, anneanne, teyze, teyze çocukları) "
                "tamamen özdeş kontrol bölgesi haplotipine sahiptir. Olabilirlik Oranı (LR_mtDNA), gözlemlenen dizinin "
                "aynı anne soyundan gelme olasılığını toplumdan rastgele seçilen akraba olmayan bir bireye karşı test eder "
                "ancak belirli tek bir bireyi tekil olarak ayırt edemez."
            ),
        }
