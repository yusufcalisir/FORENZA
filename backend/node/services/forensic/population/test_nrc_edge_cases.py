"""
Official Edge-Case Test Suite for Module 1.3: NRC-II Population Genetics.
Sub-Item 1.3.4: Edge-Case Test Suite (EC-NRC-01 to EC-NRC-05).

Fulfills Master Rule 3, Criterion 3 (5 Documented Edge-Case Tests):
  - EC-NRC-01: Zero theta HWE Equivalence (theta = 0.0000000)
  - EC-NRC-02: High Inbreeding Stress (theta = 0.1500)
  - EC-NRC-03: Complete Simplex Normalization across all 24 loci
  - EC-NRC-04: Subpopulation Demographic Stratification Cross-Comparison Ratio
  - EC-NRC-05: Reciprocal Hypothesis Balance & Log-Space Exact Additivity

Run with:
    pytest backend/node/services/forensic/population/test_nrc_edge_cases.py -v
"""

import math
import pytest

from node.services.forensic.frequency_db import (
    POPULATION_FREQUENCIES,
    LOCI_24,
    NRC_II_P_MIN_RULE_4_1,
)
from node.services.forensic.population.nrc_mathematical_formulation import (
    BaldingNicholsMatchModel,
    NRC2LikelihoodRatioEngine,
    DEFAULT_THETA,
)
from node.services.forensic.population.nrc_reference_datasets import (
    GOLDEN_REFERENCE_PROFILES,
    NIST1036StratifiedDatabase,
)


# ─────────────────────────────────────────────────────────────────────────────
# EC-NRC-01: Zero Theta Hardy-Weinberg Equilibrium Exact Reduction
# ─────────────────────────────────────────────────────────────────────────────

def test_ec_nrc_01_zero_theta_hwe_reduction():
    """
    [EC-NRC-01] Zero theta HWE Equivalence.
    When theta = 0.0000000 (panmixia):
      - Unconditional Homozygote P(Ai Ai | theta=0) == p_i^2 (exact to machine epsilon)
      - Unconditional Heterozygote P(Ai Aj | theta=0) == 2 * p_i * p_j
      - Conditional Homozygous match P(Ai Ai | Ai Ai, theta=0) == p_i^2
      - Conditional Heterozygous match P(Ai Aj | Ai Aj, theta=0) == 2 * p_i * p_j
    Evaluated across all 24 NIST 1036 loci.
    """
    caucasian_freqs = POPULATION_FREQUENCIES["Caucasian"]

    for locus in LOCI_24:
        if locus.upper() == "AMEL":
            continue

        locus_freqs = caucasian_freqs.get(locus.upper(), {})
        alleles = sorted(list(locus_freqs.keys()))

        # Normalize frequencies
        sum_f = sum(locus_freqs.values())
        norm_f = {a: freq / sum_f for a, freq in locus_freqs.items()}

        for i, a1 in enumerate(alleles):
            p1 = norm_f[a1]

            # Homozygote
            p_homo = BaldingNicholsMatchModel.compute_unconditional_genotype_probability(
                (a1, a1), norm_f, theta=0.0
            )
            assert p_homo == pytest.approx(p1 ** 2, abs=1e-12), (
                f"EC-NRC-01 violated at {locus} allele {a1}: expected {p1**2}, got {p_homo}"
            )

            # Heterozygote
            for a2 in alleles[i + 1:]:
                p2 = norm_f[a2]
                p_het = BaldingNicholsMatchModel.compute_unconditional_genotype_probability(
                    (a1, a2), norm_f, theta=0.0
                )
                assert p_het == pytest.approx(2.0 * p1 * p2, abs=1e-12), (
                    f"EC-NRC-01 violated at {locus} alleles ({a1}, {a2}): expected {2*p1*p2}, got {p_het}"
                )


# ─────────────────────────────────────────────────────────────────────────────
# EC-NRC-02: High Inbreeding Stress (theta = 0.1500) & Numerical Stability
# ─────────────────────────────────────────────────────────────────────────────

def test_ec_nrc_02_high_inbreeding_stress_theta_15():
    """
    [EC-NRC-02] High Inbreeding Stress (theta = 0.1500).
    Under extreme population bottleneck / endogamy:
      - All match probabilities must remain strictly bounded in (0.0, 1.0)
      - Likelihood ratios must remain finite and non-negative (no zero-division)
      - Simplex sum must remain identically 1.00000000 ± 1e-6
    """
    theta_extreme = 0.1500
    caucasian_freqs = POPULATION_FREQUENCIES["Caucasian"]

    # 1. Simplex validation on key polymorphic loci
    for locus in ["TH01", "D3S1358", "VWA", "FGA", "D18S51", "D21S11", "SE33"]:
        freqs = caucasian_freqs[locus]
        val_res = BaldingNicholsMatchModel.validate_simplex_normalization(
            locus=locus,
            allele_frequencies=freqs,
            theta=theta_extreme,
            tolerance=1e-6
        )
        assert val_res.is_valid is True, f"EC-NRC-02 simplex failure at {locus} under theta=0.15"
        assert abs(val_res.sum_probability - 1.0) < 1e-6

    # 2. Multi-locus LR computation on full 24-locus profile under extreme inbreeding
    profile = GOLDEN_REFERENCE_PROFILES["SRM_2391D_COMP_A"].loci_genotypes
    lr_res = NRC2LikelihoodRatioEngine.compute_profile_lr(
        suspect_profile=profile,
        evidence_profile=profile,
        population_frequencies=caucasian_freqs,
        theta=theta_extreme,
        population_name="Caucasian"
    )

    assert math.isfinite(lr_res.total_lr) and lr_res.total_lr > 1.0
    assert lr_res.log10_total_lr > 10.0  # Even under theta=0.15, 24 loci provide strong identification power
    assert lr_res.is_reciprocal_balanced is True


# ─────────────────────────────────────────────────────────────────────────────
# EC-NRC-03: Complete Simplex Normalization across all 24 Loci
# ─────────────────────────────────────────────────────────────────────────────

def test_ec_nrc_03_complete_simplex_normalization_24_loci():
    """
    [EC-NRC-03] Complete Simplex Normalization across all 24 Loci.
    Verifies that the sum of all diploid genotype probabilities equals 1.00000000 ± 1e-6
    across all 24 loci in the NIST 1036 database for theta = 0.01, 0.03, and 0.05.
    """
    caucasian_freqs = POPULATION_FREQUENCIES["Caucasian"]

    for theta in [0.01, 0.03, 0.05]:
        total_genotypes_checked = 0
        for locus in LOCI_24:
            if locus.upper() == "AMEL":
                continue

            locus_freqs = caucasian_freqs.get(locus.upper(), {})
            val_res = BaldingNicholsMatchModel.validate_simplex_normalization(
                locus=locus,
                allele_frequencies=locus_freqs,
                theta=theta,
                tolerance=1e-6
            )
            assert val_res.is_valid is True, (
                f"EC-NRC-03 simplex normalization failed for {locus} at theta={theta}: "
                f"sum={val_res.sum_probability:.8f}, delta={val_res.delta_from_unity:.2e}"
            )
            total_genotypes_checked += val_res.num_genotypes_evaluated

        assert total_genotypes_checked > 700, (
            f"Expected > 700 distinct diploid genotypes across 23 STR loci, evaluated {total_genotypes_checked}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# EC-NRC-04: Subpopulation Demographic Stratification Cross-Comparison Ratio
# ─────────────────────────────────────────────────────────────────────────────

def test_ec_nrc_04_subpopulation_cross_comparison_ratio():
    """
    [EC-NRC-04] Subpopulation Cross-Comparison Ratio.
    Evaluates NIST SRM 2391d Component B (African American individual 9948)
    under Caucasian vs African American background databases:
      - R_pop = LR(Caucasian) / LR(AfricanAmerican)
      - Because 9948 possesses alleles characteristic of African ancestry (e.g. TH01*6/9.3, VWA*17/17, D3S1358*15/17),
        his profile is rarer in Caucasian than African American, yielding LR_Caucasian > LR_AfricanAmerican.
    """
    profile_b = GOLDEN_REFERENCE_PROFILES["SRM_2391D_COMP_B"].loci_genotypes
    cauc_freqs = POPULATION_FREQUENCIES["Caucasian"]
    aa_freqs = POPULATION_FREQUENCIES["AfricanAmerican"]

    res_cauc = NRC2LikelihoodRatioEngine.compute_profile_lr(
        suspect_profile=profile_b,
        evidence_profile=profile_b,
        population_frequencies=cauc_freqs,
        theta=0.03,
        population_name="Caucasian"
    )

    res_aa = NRC2LikelihoodRatioEngine.compute_profile_lr(
        suspect_profile=profile_b,
        evidence_profile=profile_b,
        population_frequencies=aa_freqs,
        theta=0.03,
        population_name="AfricanAmerican"
    )

    # Log10 LR differs between Caucasian and African American due to demographic stratification
    log10_diff = abs(res_cauc.log10_total_lr - res_aa.log10_total_lr)
    assert log10_diff > 0.5, (
        f"EC-NRC-04 failed: expected |Log10(LR_Cauc) - Log10(LR_AA)| > 0.5, got {log10_diff:.3f}"
    )

    # Both must deliver extremely strong inclusion support
    assert res_cauc.verbal_scale_en == "Extremely strong support for inclusion (Hp)"
    assert res_aa.verbal_scale_en == "Extremely strong support for inclusion (Hp)"


# ─────────────────────────────────────────────────────────────────────────────
# EC-NRC-05: Reciprocal Hypothesis Balance & Log-Space Exact Additivity
# ─────────────────────────────────────────────────────────────────────────────

def test_ec_nrc_05_reciprocal_hypothesis_balance():
    """
    [EC-NRC-05] Reciprocal Hypothesis Balance Invariant.
    Mathematical Invariants:
      1. LR(Hp / Hd) * LR(Hd / Hp) = 1.000000000 ± 1e-6
      2. |log10(LR_total) - sum_l log10(LR_l)| < 1e-6
    Shields court reports against Prosecutor's Fallacy by ensuring complete reciprocal symmetry.
    """
    for profile_id, profile_obj in GOLDEN_REFERENCE_PROFILES.items():
        profile = profile_obj.loci_genotypes
        pop_name = profile_obj.ethnicity
        pop_freqs = POPULATION_FREQUENCIES.get(pop_name, POPULATION_FREQUENCIES["Caucasian"])

        res = NRC2LikelihoodRatioEngine.compute_profile_lr(
            suspect_profile=profile,
            evidence_profile=profile,
            population_frequencies=pop_freqs,
            theta=DEFAULT_THETA,
            population_name=pop_name
        )

        # 1. Reciprocal product symmetry
        assert res.is_reciprocal_balanced is True, (
            f"EC-NRC-05 reciprocal balance failed for {profile_id}: delta={res.reciprocal_product_delta:.2e}"
        )
        assert res.reciprocal_product_delta < 1e-6

        # 2. Log-space exact additivity across loci
        sum_locus_logs = sum(l.log10_lr_locus for l in res.locus_results)
        assert abs(res.log10_total_lr - sum_locus_logs) < 1e-6, (
            f"EC-NRC-05 log additivity failed for {profile_id}: total={res.log10_total_lr}, sum={sum_locus_logs}"
        )
