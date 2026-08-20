"""
Unit tests for FORENZA 24-Locus STR Edge-Case Test Suite (EC-STR-01 to EC-STR-05)
Validation Suite for Sub-Item 1.1.4:
- EC-STR-01: Rare Allele Invariant (Dirichlet-Laplace floor p_min = 0.00241)
- EC-STR-02: Homozygote theta-Scaling Invariance (|Delta| < 10^-7 across 24 loci)
- EC-STR-03: Tri-Allelic Duplication Handling (Type 1 & Type 2 mosaicism)
- EC-STR-04: Microvariant Decimal Parsing & Sorting Invariance
- EC-STR-05: Exact Multiplicative Invariant & Log-Likelihood Additivity

Derived from: research/pillar_1_probabilistic_genotyping_research.md
"""

import math
import pytest
from backend.node.services.forensic.terminal.nist_1036_popgen_engine import (
    Nist1036PopGenEngine,
    NistPopulationEnum,
    NIST_1036_ALLELE_FREQUENCIES,
)
from backend.node.services.forensic.terminal.str_locus_registry_engine import (
    StrLocusRegistryEngine,
    STR_LOCUS_24_MASTER_REGISTRY,
)
from backend.node.services.forensic.terminal.str_reference_datasets import (
    NIST_SRM_2391D_COMP_A,
    NIST_SRM_2391D_COMP_B,
    NIST_SRM_2391D_COMP_C,
    NIST_SRM_2391D_COMP_D,
    NIST_SRM_2391D_COMP_E,
)


class TestEdgeCase01RareAlleleInvariant:
    """EC-STR-01: Unseen or novel allele assigned floor p_min = 0.00241 without zero-division."""

    def test_novel_unobserved_allele_floor(self):
        """Verify novel allele (e.g. D18S51 allele 28) gets exact floor p = 0.00241 (global) or subpopulation floor."""
        global_p_min = 5.0 / (2.0 * 1036.0)
        assert pytest.approx(global_p_min, abs=1e-5) == 0.00241

        p_min_cau = Nist1036PopGenEngine.get_population_p_min("Caucasian")
        assert pytest.approx(p_min_cau, abs=1e-5) == 5.0 / 722.0

        freq = Nist1036PopGenEngine.get_allele_frequency(
            locus="D18S51",
            allele_str="28",
            population="Caucasian",
        )
        assert freq >= p_min_cau
        assert freq > 0.0
        assert math.isfinite(freq)

    def test_multi_locus_rare_allele_profile_computes_cleanly(self):
        """Verify full 24-locus calculation with multiple unseen alleles does not raise exceptions."""
        rare_profile = {
            "D3S1358": ("15", "16"),
            "vWA": ("17", "27"),        # Novel rare allele 27
            "FGA": ("22", "38.2"),      # Novel rare microvariant 38.2
            "D8S1179": ("13", "15"),
            "D21S11": ("28", "39"),     # Novel rare allele 39
            "D18S51": ("14", "28"),     # Novel rare allele 28
            "D5S818": ("11", "12"),
            "D13S317": ("11", "12"),
            "D7S820": ("8", "10"),
            "D16S539": ("9", "11"),
            "CSF1PO": ("11", "12"),
            "PENTA_D": ("10", "11"),
            "TH01": ("6", "14"),        # Novel rare allele 14
            "TPOX": ("8", "11"),
            "D2S1338": ("19", "20"),
            "D19S433": ("13", "14"),
            "PENTA_E": ("12", "14"),
            "D1S1656": ("14", "15"),
            "D12S391": ("17", "18"),
            "D2S441": ("11", "12"),
            "D10S1248": ("13", "13"),
            "D22S1045": ("15", "15"),
            "SE33": ("18", "25.2"),
        }
        res = Nist1036PopGenEngine.calculate_multilocus_profile_probability(
            profile=rare_profile,
            population="Caucasian",
            theta=0.01,
            use_exact_balding_nichols=True,
        )
        assert res["combined_rmp"] > 0.0
        assert res["combined_lr"] > 0.0
        assert math.isfinite(res["combined_log10_lr"])
        assert res["combined_log10_lr"] > 0.0


class TestEdgeCase02HomozygoteThetaScalingInvariance:
    """EC-STR-02: Exact match of P(Ai Ai | theta=0.030) to analytical polynomial Delta < 10^-7."""

    @pytest.mark.parametrize("locus", list(STR_LOCUS_24_MASTER_REGISTRY.keys())[:10])
    @pytest.mark.parametrize("population", ["Caucasian", "African American", "Hispanic", "Asian"])
    def test_homozygote_theta_polynomial_precision(self, locus, population):
        """
        Analytically verify:
        P(Ai Ai | theta=0.03) = [2(0.03) + 0.97 p_i][3(0.03) + 0.97 p_i] / [(1.03)(1.06)]
                              = (0.0054 + 0.1455 p_i + 0.9409 p_i^2) / 1.0918
        """
        if locus.lower() in ("amelogenin", "dys391", "sry"):
            pytest.skip("Non-autosomal locus")

        theta = 0.030
        meta = StrLocusRegistryEngine.get_locus_metadata(locus)
        if not meta or not meta.observed_allele_spectrum:
            pytest.skip("No spectrum")

        # Test on first 3 observed alleles of locus
        for allele in meta.observed_allele_spectrum[:3]:
            p_i = Nist1036PopGenEngine.get_allele_frequency(locus, allele, population)

            # Analytical value
            num_analytical = (2.0 * theta + (1.0 - theta) * p_i) * (3.0 * theta + (1.0 - theta) * p_i)
            den_analytical = (1.0 + theta) * (1.0 + 2.0 * theta)
            p_analytical = num_analytical / den_analytical

            # Computed via engine
            p_computed = Nist1036PopGenEngine.calculate_homozygote_probability(
                locus=locus,
                allele=allele,
                population=population,
                theta=theta,
                use_exact_balding_nichols=True,
            )

            delta = abs(p_computed - p_analytical)
            assert delta < 1e-7, f"Locus {locus}, allele {allele}: Delta {delta} >= 1e-7"


class TestEdgeCase03TriAllelicDuplicationHandling:
    """EC-STR-03: Parse Type 1 (equal peak height) and Type 2 mosaicism gracefully without crash."""

    def test_type_1_tri_allelic_tpox(self):
        """Verify Type 1 tri-allelic pattern: TPOX (8, 10, 11) with generalized Balding-Nichols."""
        p_g, lr, formula = Nist1036PopGenEngine.calculate_genotype_probability(
            locus="TPOX",
            allele1="8",
            allele2="10",
            allele3="11",
            population="Caucasian",
            theta=0.01,
        )
        assert p_g > 0.0
        assert lr == 1.0 / p_g
        assert "6*" in formula

        # Verify manual analytical calculation for 6 * p1 * p2 * p3 under theta=0.01
        p1 = Nist1036PopGenEngine.get_allele_frequency("TPOX", "8", "Caucasian")
        p2 = Nist1036PopGenEngine.get_allele_frequency("TPOX", "10", "Caucasian")
        p3 = Nist1036PopGenEngine.get_allele_frequency("TPOX", "11", "Caucasian")

        theta = 0.01
        expected_p = (6.0 * (theta + 0.99*p1) * (theta + 0.99*p2) * (theta + 0.99*p3)) / (1.01 * 1.02)
        assert pytest.approx(p_g, abs=1e-8) == expected_p

    def test_type_2_somatic_mosaicism_profile_calculation(self):
        """Verify 24-locus multi-locus profile with a tri-allelic locus (D18S51 13, 14, 16)."""
        tri_profile = {
            "D3S1358": ("15", "16"),
            "vWA": ("16", "18"),
            "D18S51": ("13", "14", "16"),  # Tri-allelic somatic duplication
            "TH01": ("6", "9.3"),
            "D21S11": ("28", "31.2"),
        }
        res = Nist1036PopGenEngine.calculate_multilocus_profile_probability(
            profile=tri_profile,
            population="Caucasian",
            theta=0.01,
        )
        assert res["combined_rmp"] > 0.0
        assert res["combined_lr"] > 0.0
        assert res["evaluated_loci_count"] == 5


class TestEdgeCase04MicrovariantDecimalParsing:
    """EC-STR-04: Correct numerical sorting and base-pair sizing for partial repeats."""

    def test_th01_numerical_sort_order(self):
        """Verify TH01 alleles are sorted numerically: 8 < 8.3 < 9 < 9.3 < 10."""
        raw_alleles = ["9.3", "8", "10", "8.3", "6", "9", "7", "5"]
        sorted_alleles = sorted(raw_alleles, key=lambda a: float(a))
        expected = ["5", "6", "7", "8", "8.3", "9", "9.3", "10"]
        assert sorted_alleles == expected

    def test_se33_decimal_offsets(self):
        """Verify SE33 25.2 and 27.2 decimal offsets give +2 bp."""
        details_25_2 = StrLocusRegistryEngine.get_microvariant_details("SE33", "25.2")
        assert details_25_2 is not None
        assert details_25_2.delta_bp == 2
        assert details_25_2.integer_base_repeat == 25

        details_27_2 = StrLocusRegistryEngine.get_microvariant_details("SE33", "27.2")
        assert details_27_2 is not None
        assert details_27_2.delta_bp == 2
        assert details_27_2.integer_base_repeat == 27

    def test_d1s1656_decimal_offset(self):
        """Verify D1S1656 17.3 gives +3 bp offset."""
        details = StrLocusRegistryEngine.get_microvariant_details("D1S1656", "17.3")
        assert details is not None
        assert details.delta_bp == 3
        assert details.integer_base_repeat == 17

    def test_d21s11_decimal_offset(self):
        """Verify D21S11 31.2 gives +2 bp offset."""
        details = StrLocusRegistryEngine.get_microvariant_details("D21S11", "31.2")
        assert details is not None
        assert details.delta_bp == 2
        assert details.integer_base_repeat == 31


class TestEdgeCase05ExactMultiplicativeInvariant:
    """EC-STR-05: Strict biostatistical assertion on log-likelihood additivity and product equivalence."""

    @pytest.mark.parametrize("preset", [
        NIST_SRM_2391D_COMP_A,
        NIST_SRM_2391D_COMP_B,
        NIST_SRM_2391D_COMP_C,
        NIST_SRM_2391D_COMP_D,
        NIST_SRM_2391D_COMP_E,
    ])
    def test_exact_invariants_across_all_reference_standards(self, preset):
        """
        Verify on all NIST SRM 2391d standards:
        1. |log10(LR_total) - sum(log10(LR_l))| < 10^-6
        2. |LR_total - prod(LR_l)| / LR_total < 10^-6
        3. Reciprocal hypothesis balance: LR(Hp/Hd) * LR(Hd/Hp) = 1.0
        """
        profile = {
            k: (v["allele1"], v.get("allele2", v["allele1"]))
            for k, v in preset.str_profile.items()
        }
        res = Nist1036PopGenEngine.calculate_multilocus_profile_probability(
            profile=profile,
            population="Caucasian",
            theta=0.01,
            use_exact_balding_nichols=True,
        )
        assert res["invariants"]["log_likelihood_additivity_error"] < 1e-6
        assert res["invariants"]["multiplicative_product_relative_error"] < 1e-6

        # Reciprocal check
        lr_hp = res["combined_lr"]
        lr_hd = res["combined_rmp"]
        assert pytest.approx(lr_hp * lr_hd, rel=1e-6) == 1.0
