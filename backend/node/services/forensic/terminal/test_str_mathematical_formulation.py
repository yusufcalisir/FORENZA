"""
FORENZA Mathematical Verification Test Suite: Sub-Item 1.1.1
Exhaustive validation of 24-Locus Autosomal STR Mathematical Formulations:
- Balding-Nichols / NRC II Eq (4.4) Exact Coancestry Match Probabilities
- Probability Simplex Normalization Invariants across 24 Loci (sum P = 1.000000)
- Multi-Locus Log-Likelihood Additivity and Multiplicative Equivalence Invariants
- Reciprocal Hypothesis Balance: LR(Hp/Hd) * LR(Hd/Hp) = 1.000000
- Stepwise Mutation Model (SMM) Geometric Decay & Parameter Bounds
- ISO/IEC 17025 GUM Expanded Measurement Uncertainty Formulations
Derived verbatim from: research/pillar_1_probabilistic_genotyping_research.md
"""

import pytest
import math
from backend.node.services.forensic.terminal.nist_1036_popgen_engine import (
    Nist1036PopGenEngine,
    NistPopulationEnum,
    POPULATION_SAMPLE_SIZES,
    POPULATION_P_MIN_FLOORS,
    NIST_1036_ALLELE_FREQUENCIES,
)
from backend.node.services.forensic.kinship_engine import (
    smm_transition_probability,
    IBD_COEFFICIENTS,
    KinshipRelationship,
    DEFAULT_MUTATION_RATE,
    SMM_GEOMETRIC_PARAM_R,
)
from backend.node.services.forensic.terminal.str_locus_registry_engine import (
    STR_LOCUS_24_MASTER_REGISTRY,
    StrLocusRegistryEngine,
)


class TestBaldingNicholsExactFormulation:
    """Mathematical validation of Balding-Nichols / NRC II Eq (4.4) analytical formulas."""

    def test_theta_zero_reduces_identically_to_hwe(self):
        """
        At theta = 0.0, the Balding-Nichols equations must simplify identically
        to standard Hardy-Weinberg Equilibrium probabilities.
        """
        p_i = 0.25
        p_j = 0.35
        theta = 0.0

        # Homozygote: P = p_i^2
        p_hom = Nist1036PopGenEngine.calculate_conditional_match_probability(
            scenario="HOMOZYGOUS_MATCH", p_i=p_i, theta=theta
        )
        assert pytest.approx(p_hom, abs=1e-9) == (p_i ** 2)
        assert pytest.approx(p_hom, abs=1e-9) == 0.0625

        # Heterozygote: P = 2 * p_i * p_j
        p_het = Nist1036PopGenEngine.calculate_conditional_match_probability(
            scenario="HETEROZYGOUS_MATCH", p_i=p_i, p_j=p_j, theta=theta
        )
        assert pytest.approx(p_het, abs=1e-9) == (2.0 * p_i * p_j)
        assert pytest.approx(p_het, abs=1e-9) == 0.1750

        # Partial match: P = p_i * p_j
        p_part = Nist1036PopGenEngine.calculate_conditional_match_probability(
            scenario="PARTIAL_MATCH_ONE_ALLELE", p_i=p_i, p_j=p_j, theta=theta
        )
        assert pytest.approx(p_part, abs=1e-9) == (p_i * p_j)
        assert pytest.approx(p_part, abs=1e-9) == 0.0875

        # Zero shared: P = 2 * p_i * p_j
        p_zero = Nist1036PopGenEngine.calculate_conditional_match_probability(
            scenario="ZERO_SHARED_ALLELES", p_i=p_i, p_j=p_j, theta=theta
        )
        assert pytest.approx(p_zero, abs=1e-9) == (2.0 * p_i * p_j)
        assert pytest.approx(p_zero, abs=1e-9) == 0.1750

    def test_exact_homozygote_formula_analytical_verification(self):
        """
        Verify exact homozygous match probability under theta=0.03, p_i=0.20:
        Analytical:
          num = [2(0.03) + 0.97(0.20)] * [3(0.03) + 0.97(0.20)]
              = [0.06 + 0.194] * [0.09 + 0.194] = 0.254 * 0.284 = 0.072136
          den = (1 + 0.03)(1 + 2(0.03)) = 1.03 * 1.06 = 1.0918
          P = 0.072136 / 1.0918 ≈ 0.06607070892104782
        """
        p_i = 0.20
        theta = 0.03
        expected = 0.072136 / 1.0918

        computed = Nist1036PopGenEngine.calculate_conditional_match_probability(
            scenario="HOMOZYGOUS_MATCH", p_i=p_i, theta=theta
        )
        assert pytest.approx(computed, abs=1e-9) == expected

    def test_exact_heterozygote_formula_analytical_verification(self):
        """
        Verify exact heterozygous match probability under theta=0.03, p_i=0.20, p_j=0.15:
        Analytical:
          num = 2 * [0.03 + 0.97(0.20)] * [0.03 + 0.97(0.15)]
              = 2 * [0.03 + 0.194] * [0.03 + 0.1455] = 2 * 0.224 * 0.1755 = 0.078624
          den = 1.03 * 1.06 = 1.0918
          P = 0.078624 / 1.0918 ≈ 0.07201318922879649
        """
        p_i = 0.20
        p_j = 0.15
        theta = 0.03
        expected = 0.078624 / 1.0918

        computed = Nist1036PopGenEngine.calculate_conditional_match_probability(
            scenario="HETEROZYGOUS_MATCH", p_i=p_i, p_j=p_j, theta=theta
        )
        assert pytest.approx(computed, abs=1e-9) == expected

    def test_partial_and_zero_shared_alleles_analytical_verification(self):
        """
        Verify partial match (1 shared) and zero shared alleles under theta=0.03, p_i=0.20, p_j=0.15:
        Partial:
          num = [0.03 + 0.97(0.20)] * [0.97(0.15)] = 0.224 * 0.1455 = 0.032592
          P = 0.032592 / 1.0918 ≈ 0.029851621176039568
        Zero Shared:
          num = 2 * [0.97(0.20)] * [0.97(0.15)] = 2 * 0.194 * 0.1455 = 0.056454
          P = 0.056454 / 1.0918 ≈ 0.05170727239421139
        """
        p_i = 0.20
        p_j = 0.15
        theta = 0.03
        den = 1.0918

        p_partial = Nist1036PopGenEngine.calculate_conditional_match_probability(
            scenario="PARTIAL_MATCH_ONE_ALLELE", p_i=p_i, p_j=p_j, theta=theta
        )
        assert pytest.approx(p_partial, abs=1e-9) == 0.032592 / den

        p_zero = Nist1036PopGenEngine.calculate_conditional_match_probability(
            scenario="ZERO_SHARED_ALLELES", p_i=p_i, p_j=p_j, theta=theta
        )
        assert pytest.approx(p_zero, abs=1e-9) == 0.056454 / den


class TestProbabilitySimplexNormalization:
    """Verification that sum of all genotype frequencies across loci equals 1.000000."""

    @pytest.mark.parametrize("population", ["Caucasian", "African American", "Hispanic", "Asian"])
    @pytest.mark.parametrize("theta", [0.00, 0.01, 0.03, 0.05])
    def test_24_loci_unconditional_simplex_sum(self, population, theta):
        """
        For each of the standard autosomal STR loci, verify that
        sum_{i <= j} P(Ai Aj | theta) == 1.00000000 +/- 1e-6 under the unconditional population model.
        """
        autosomal_loci = [
            "D3S1358", "vWA", "FGA", "D8S1179", "D21S11", "D18S51",
            "D5S818", "D13S317", "D7S820", "D16S539", "CSF1PO", "TH01",
            "TPOX", "D1S1656", "D2S441", "D2S1338", "D10S1248", "D12S391",
            "D19S433", "D22S1045", "SE33", "Penta D", "Penta E"
        ]

        for locus in autosomal_loci:
            res = Nist1036PopGenEngine.verify_probability_simplex(
                locus=locus,
                population=population,
                theta=theta,
                suspect_genotype=None,
            )
            assert res["is_valid_simplex"] is True, (
                f"Unconditional simplex normalization failed for {locus} in {population} (theta={theta}): "
                f"sum = {res['total_probability_sum']}"
            )
            assert pytest.approx(res["total_probability_sum"], abs=1e-6) == 1.0

    @pytest.mark.parametrize("population", ["Caucasian", "African American", "Hispanic", "Asian"])
    @pytest.mark.parametrize("theta", [0.00, 0.01, 0.03, 0.05])
    def test_24_loci_conditional_polya_urn_simplex_given_suspect(self, population, theta):
        """
        Verify that given a suspect genotype (both homozygote and heterozygote cases),
        the conditional evidence distribution sum_{i <= j} P(E = Ai Aj | S, theta) == 1.00000000 +/- 1e-6.
        """
        test_cases = [
            ("TH01", ("9.3", "9.3")),   # Homozygote suspect
            ("TH01", ("6", "9.3")),     # Heterozygote suspect
            ("D21S11", ("29", "31.2")), # Heterozygote microvariant
            ("D1S1656", ("15", "15")),  # Homozygote
            ("SE33", ("26.2", "28.2")), # Heterozygote complex
        ]

        for locus, suspect_gt in test_cases:
            res = Nist1036PopGenEngine.verify_probability_simplex(
                locus=locus,
                population=population,
                theta=theta,
                suspect_genotype=suspect_gt,
            )
            assert res["is_valid_simplex"] is True, (
                f"Conditional Polya-urn simplex failed for {locus} given S={suspect_gt} in {population} (theta={theta}): "
                f"sum = {res['total_probability_sum']}"
            )
            assert pytest.approx(res["total_probability_sum"], abs=1e-6) == 1.0



class TestMultiLocusInvariants:
    """Biostatistical and mathematical invariants across multi-locus profile calculations."""

    @pytest.fixture
    def standard_24_locus_profile(self):
        return {
            "D3S1358": ("15", "16"),
            "vWA": ("16", "17"),
            "FGA": ("21", "23"),
            "D8S1179": ("13", "14"),
            "D21S11": ("29", "30"),
            "D18S51": ("12", "15"),
            "D5S818": ("11", "12"),
            "D13S317": ("11", "12"),
            "D7S820": ("10", "11"),
            "D16S539": ("11", "12"),
            "CSF1PO": ("10", "11"),
            "TH01": ("9.3", "9.3"),
            "TPOX": ("8", "11"),
            "D1S1656": ("14", "17.3"),
            "D2S441": ("11", "12"),
            "D2S1338": ("19", "23"),
            "D10S1248": ("13", "14"),
            "D12S391": ("18", "19"),
            "D19S433": ("13", "14"),
            "D22S1045": ("15", "16"),
            "SE33": ("26.2", "28.2"),
            "Penta D": ("9", "11"),
            "Penta E": ("12", "13"),
            "Amelogenin": ("X", "Y"),
        }

    def test_log_likelihood_additivity_invariant(self, standard_24_locus_profile):
        """
        Strict Biostatistical Invariant:
        |log10(LR_total) - sum_{l=1}^24 log10(LR_l)| < 10^-6
        """
        res = Nist1036PopGenEngine.calculate_multilocus_profile_probability(
            profile=standard_24_locus_profile,
            population="Caucasian",
            theta=0.01,
            use_exact_balding_nichols=True,
        )

        sum_locus_log10 = sum(loc["log10_lr"] for loc in res["locus_results"])
        assert pytest.approx(res["combined_log10_lr"], abs=1e-6) == sum_locus_log10

    def test_multiplicative_product_equivalence(self, standard_24_locus_profile):
        """
        Strict Biostatistical Invariant:
        |LR_total - prod(LR_l)| / LR_total < 10^-6
        """
        res = Nist1036PopGenEngine.calculate_multilocus_profile_probability(
            profile=standard_24_locus_profile,
            population="Caucasian",
            theta=0.01,
            use_exact_balding_nichols=True,
        )

        prod_locus_lr = 1.0
        for loc in res["locus_results"]:
            prod_locus_lr *= loc["locus_lr"]

        assert pytest.approx(res["combined_lr"], rel=1e-6) == prod_locus_lr
        assert pytest.approx(res["combined_rmp"], rel=1e-6) == 1.0 / prod_locus_lr

    def test_reciprocal_hypothesis_balance(self):
        """
        Symmetry Invariant:
        LR(Hp / Hd) * LR(Hd / Hp) = 1.0000000 +/- 1e-6
        """
        p_g, lr_hp, _ = Nist1036PopGenEngine.calculate_genotype_probability(
            locus="TH01", allele1="9.3", allele2="9.3", population="Caucasian", theta=0.01
        )
        lr_hd = p_g  # Under Hd/Hp: P(E|Hd)/P(E|Hp) = P(G)/1.0

        assert pytest.approx(lr_hp * lr_hd, abs=1e-6) == 1.0000000

    def test_iso_17025_expanded_uncertainty(self, standard_24_locus_profile):
        """
        Verify ISO/IEC 17025 Expanded Uncertainty computation (k = 2.00, 95% CI):
        U_95% = 2.00 * u_c(log10_LR) where u_c = 0.035 * sqrt(N_loci).
        """
        res = Nist1036PopGenEngine.calculate_multilocus_profile_probability(
            profile=standard_24_locus_profile,
            population="Caucasian",
            theta=0.01,
        )
        mu = res["measurement_uncertainty"]
        n_loci = res["evaluated_loci_count"]
        expected_uc = 0.035 * math.sqrt(n_loci)
        expected_u95 = 2.00 * expected_uc

        assert pytest.approx(mu["combined_standard_uncertainty_log10"], abs=1e-6) == expected_uc
        assert pytest.approx(mu["expanded_uncertainty_U95"], abs=1e-6) == expected_u95
        assert mu["coverage_factor_k"] == 2.00
        assert mu["ci_95_lower"] <= res["combined_lr"] <= mu["ci_95_upper"]


class TestStepwiseMutationModelSMM:
    """Mathematical validation of Stepwise Mutation Model (SMM) transitions."""

    def test_smm_no_mutation(self):
        """P(m -> m) = 1 - mu = 1 - 0.001 = 0.999."""
        mu = 1e-3
        p = smm_transition_probability(15.0, 15.0, mu=mu, r=0.10)
        assert pytest.approx(p, abs=1e-9) == 0.999

    def test_smm_single_step_mutation(self):
        """
        P(m -> m+1) = (mu/2) * (1-r) * r^0 = (0.001/2) * (1 - 0.10) = 0.0005 * 0.9 = 0.00045.
        """
        mu = 1e-3
        r = 0.10
        p_plus1 = smm_transition_probability(15.0, 16.0, mu=mu, r=r)
        p_minus1 = smm_transition_probability(15.0, 14.0, mu=mu, r=r)

        expected = (mu / 2.0) * (1.0 - r)
        assert pytest.approx(p_plus1, abs=1e-9) == expected
        assert pytest.approx(p_minus1, abs=1e-9) == expected
        assert pytest.approx(p_plus1, abs=1e-9) == 0.00045

    def test_smm_two_step_mutation(self):
        """
        P(m -> m+2) = (mu/2) * (1-r) * r^1 = 0.00045 * 0.10 = 0.000045.
        """
        mu = 1e-3
        r = 0.10
        p_plus2 = smm_transition_probability(15.0, 17.0, mu=mu, r=r)
        expected = (mu / 2.0) * (1.0 - r) * r
        assert pytest.approx(p_plus2, abs=1e-9) == expected
        assert pytest.approx(p_plus2, abs=1e-9) == 0.000045

    def test_smm_geometric_decay_ratio(self):
        """Ratio of step k+1 to step k must equal exactly r = 0.10."""
        mu = 1e-3
        r = 0.10
        p1 = smm_transition_probability(15.0, 16.0, mu=mu, r=r)
        p2 = smm_transition_probability(15.0, 17.0, mu=mu, r=r)
        p3 = smm_transition_probability(15.0, 18.0, mu=mu, r=r)

        assert pytest.approx(p2 / p1, abs=1e-9) == r
        assert pytest.approx(p3 / p2, abs=1e-9) == r

    def test_ibd_coefficients_matrix(self):
        """Verify Ito-Donnelly IBD coefficient sums (k0 + k1 + k2 = 1.0)."""
        for rel, (k0, k1, k2) in IBD_COEFFICIENTS.items():
            assert pytest.approx(k0 + k1 + k2, abs=1e-9) == 1.0, f"IBD sum != 1.0 for {rel}"
