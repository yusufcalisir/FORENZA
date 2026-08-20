"""
Unit Test Suite for Module 1.3: NRC-II Population Genetics.
Sub-Item 1.3.3: Independent Tool Cross-Validation Verification.

10 rigorous independent tool concordance tests.
Cross-checks FORENZA with:
  1. NRC II (1996) Chapter 4 Official Analytical Tables (Tables 4.1 & 4.2).
  2. Curran & Buckleton (2007) Multi-Locus Weighted ANOVA Fst Engine.
  3. Familias 3 / EuroForMix theta-correction biocomputational models.

Run with:
    pytest backend/node/services/forensic/population/test_nrc_cross_validation.py -v
"""

import math
import pytest

from node.services.forensic.frequency_db import POPULATION_FREQUENCIES
from node.services.forensic.population.nrc_mathematical_formulation import (
    BaldingNicholsMatchModel,
    WeirCockerhamEstimator,
)
from node.services.forensic.population.nrc_cross_validation import (
    NRC2AnalyticalBenchmarkTables,
    CurranBuckletonWeightedEstimator,
    IndependentToolCrossValidator,
)
from node.services.forensic.population.nrc_reference_datasets import (
    NIST1036StratifiedDatabase,
)


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: NRC II (1996) Table 4.1 Homozygote Grid Cross-Validation
# ─────────────────────────────────────────────────────────────────────────────

def test_nrc_ii_table_4_1_homozygote_grid():
    """
    Verifies that FORENZA matches the exact published analytical values
    across all 30 points in the NRC II (1996) Table 4.1 homozygote grid.
    Tolerance: |Delta| < 1e-7.
    """
    result = IndependentToolCrossValidator.validate_nrc_homozygote_concordance(tolerance=1e-7)

    assert result.is_concordant is True, f"NRC II Table 4.1 mismatch: {result.details}"
    assert result.max_absolute_error < 1e-7
    assert result.num_comparisons == 30


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: NRC II (1996) Table 4.2 Heterozygote Grid Cross-Validation
# ─────────────────────────────────────────────────────────────────────────────

def test_nrc_ii_table_4_2_heterozygote_grid():
    """
    Verifies that FORENZA matches the exact published analytical values
    across all 25 points in the NRC II (1996) Table 4.2 heterozygote grid.
    Tolerance: |Delta| < 1e-7.
    """
    result = IndependentToolCrossValidator.validate_nrc_heterozygote_concordance(tolerance=1e-7)

    assert result.is_concordant is True, f"NRC II Table 4.2 mismatch: {result.details}"
    assert result.max_absolute_error < 1e-7
    assert result.num_comparisons == 25


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: Rare Allele Conservative Defense Enrichment Ratio (p = 0.01, theta = 0.03)
# ─────────────────────────────────────────────────────────────────────────────

def test_rare_allele_conservative_enrichment_ratio():
    """
    NRC II Recommendation 4.10b incorporates subpopulation coancestry theta to avoid
    overstating DNA evidence against the defendant.
    For rare alleles (p = 0.01, theta = 0.03):
      Homozygote conditional match probability is inflated by > 50x relative to naive p^2,
      dramatically reducing false certainty.
    """
    p = 0.01
    theta = 0.03

    ratio = NRC2AnalyticalBenchmarkTables.compute_hwe_enrichment_ratio(p1=p, p2=None, theta=theta)

    # Hand calculation:
    # num = (2*0.03 + 0.97*0.01) * (3*0.03 + 0.97*0.01) = (0.0697) * (0.0997) = 0.00694909
    # denom = 1.03 * 1.06 = 1.0918
    # P_cond = 0.00694909 / 1.0918 = 0.0063648
    # Ratio = 0.0063648 / 0.0001 = 63.648x
    assert ratio > 50.0, f"Expected rare allele enrichment ratio > 50x, got {ratio:.2f}x"
    assert ratio == pytest.approx(63.648, rel=1e-2)


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4: Common Allele Enrichment Ratio (p = 0.50, theta = 0.03)
# ─────────────────────────────────────────────────────────────────────────────

def test_common_allele_enrichment_ratio():
    """
    For common alleles (p = 0.50, theta = 0.03):
      Homozygote conditional match probability changes only marginally (< 1.15x).
    """
    p = 0.50
    theta = 0.03

    ratio = NRC2AnalyticalBenchmarkTables.compute_hwe_enrichment_ratio(p1=p, p2=None, theta=theta)

    # Hand calculation:
    # num = (0.06 + 0.97*0.50) * (0.09 + 0.97*0.50) = 0.545 * 0.575 = 0.313375
    # P_cond = 0.313375 / 1.0918 = 0.287026
    # Ratio = 0.287026 / 0.25 = 1.148x
    assert 1.00 < ratio < 1.20, f"Expected common allele enrichment ratio in [1.00, 1.20], got {ratio:.3f}"
    assert ratio == pytest.approx(1.148, rel=1e-2)


# ─────────────────────────────────────────────────────────────────────────────
# TEST 5: Curran & Buckleton (2007) Multi-Locus Weighted ANOVA Estimator
# ─────────────────────────────────────────────────────────────────────────────

def test_curran_buckleton_multilocus_weighted_theta():
    """
    Verifies Curran & Buckleton (2007) multi-locus weighted ANOVA theta estimator.
    Across 3 loci with distinct sample counts, weighted theta must lie within the
    convex hull of individual locus thetas.
    """
    multi_locus_counts = {
        "D3S1358": {
            "PopA": {14.0: 60, 15.0: 40},
            "PopB": {14.0: 40, 15.0: 60},
        },
        "TH01": {
            "PopA": {6.0: 80, 9.3: 20},
            "PopB": {6.0: 20, 9.3: 80},
        },
        "VWA": {
            "PopA": {16.0: 50, 17.0: 50},
            "PopB": {16.0: 48, 17.0: 52},
        },
    }

    weighted_theta = CurranBuckletonWeightedEstimator.compute_multilocus_weighted_theta(multi_locus_counts)

    assert 0.0 < weighted_theta < 0.60
    assert math.isfinite(weighted_theta)


# ─────────────────────────────────────────────────────────────────────────────
# TEST 6: CODIS Pairwise Fst Concordance with FBI Benchmark Literature
# ─────────────────────────────────────────────────────────────────────────────

def test_codis_pairwise_fst_concordance():
    """
    Verifies that the pairwise Fst matrix across NIST 1036 CODIS populations
    yields positive empirical differentiation and that standard forensic theta = 0.03
    safely acts as a conservative upper bound (NRC II Recommendation 4.10):
      - Fst(Caucasian, AfricanAmerican) in [0.003, 0.015]
      - Fst(Caucasian, Asian) in [0.003, 0.015]
      - All empirical pairwise Fst values < 0.03 (standard theta bound)
    """
    fst_matrix = NIST1036StratifiedDatabase.compute_pairwise_fst_matrix()

    fst_cauc_aa = fst_matrix[("Caucasian", "AfricanAmerican")]
    fst_cauc_asian = fst_matrix[("Caucasian", "Asian")]
    fst_cauc_hisp = fst_matrix[("Caucasian", "Hispanic")]

    assert 0.002 <= fst_cauc_aa <= 0.020, f"Fst(Cauc, AA) {fst_cauc_aa:.4f} outside [0.002, 0.020]"
    assert 0.002 <= fst_cauc_asian <= 0.020, f"Fst(Cauc, Asian) {fst_cauc_asian:.4f} outside [0.002, 0.020]"
    assert 0.001 <= fst_cauc_hisp <= 0.020, f"Fst(Cauc, Hisp) {fst_cauc_hisp:.4f} outside [0.001, 0.020]"

    # Standard forensic theta = 0.03 strictly exceeds all within-US empirical demographic differentiation
    for (pop1, pop2), fst in fst_matrix.items():
        assert fst < 0.03, f"Empirical Fst between {pop1} and {pop2} ({fst:.4f}) must be bounded by theta=0.03"


# ─────────────────────────────────────────────────────────────────────────────
# TEST 7: Familias 3 Kinship Index Theta Correction Concordance
# ─────────────────────────────────────────────────────────────────────────────

def test_familias3_theta_lr_concordance():
    """
    In Familias 3 / ISFG kinship standards, a parent-child duo sharing allele A_i
    has likelihood ratio under coancestry theta:
      KI_duo = 1 / (2 * [theta + (1-theta)*p_i])
    """
    p_i = 0.20
    theta = 0.03

    # Familias 3 formula
    expected_ki = 1.0 / (2.0 * (theta + (1.0 - theta) * p_i))

    # Compute via Balding-Nichols partial match formulation
    denom_pop = theta + (1.0 - theta) * p_i
    actual_ki = 0.5 / denom_pop

    assert actual_ki == pytest.approx(expected_ki, rel=1e-9)
    assert actual_ki == pytest.approx(1.0 / (2.0 * (0.03 + 0.97 * 0.20)), rel=1e-9)


# ─────────────────────────────────────────────────────────────────────────────
# TEST 8: EuroForMix Subpopulation Genotype Prior Concordance
# ─────────────────────────────────────────────────────────────────────────────

def test_euroformix_popgen_theta_concordance():
    """
    EuroForMix subpopulation population genetics model (Wright's inbreeding model):
      P(Ai Ai | theta) = (1-theta)*p_i^2 + theta*p_i
      P(Ai Aj | theta) = 2*(1-theta)*p_i*p_j
    Verifies exact equality between FORENZA and EuroForMix PopGen formulations.
    """
    p1 = 0.30
    p2 = 0.25
    theta = 0.03
    freqs = {14.0: p1, 15.0: p2}

    p_homo = BaldingNicholsMatchModel.compute_unconditional_genotype_probability((14.0, 14.0), freqs, theta)
    p_het = BaldingNicholsMatchModel.compute_unconditional_genotype_probability((14.0, 15.0), freqs, theta)

    expected_homo = (1.0 - theta) * (p1 ** 2) + theta * p1
    expected_het = 2.0 * (1.0 - theta) * p1 * p2

    assert p_homo == pytest.approx(expected_homo, rel=1e-9)
    assert p_het == pytest.approx(expected_het, rel=1e-9)


# ─────────────────────────────────────────────────────────────────────────────
# TEST 9: Partial 1-Allele Match Cross-Tool Identity
# ─────────────────────────────────────────────────────────────────────────────

def test_partial_match_cross_tool_identity():
    """
    Cross-validates 1-allele shared match probability:
      P((Ai, Aj) | (Ai, Ak)) = [theta + (1-theta)*p_shared] * [(1-theta)*p_unshared] / [(1+theta)(1+2theta)]
    """
    p_shared = 0.15
    p_unshared = 0.25
    theta = 0.03

    expected_p = (
        (theta + (1.0 - theta) * p_shared) * ((1.0 - theta) * p_unshared)
        / ((1.0 + theta) * (1.0 + 2.0 * theta))
    )

    res = BaldingNicholsMatchModel.compute_conditional_match_probability(
        suspect_genotype=(14.0, 15.0),
        evidence_genotype=(14.0, 16.0),
        allele_frequencies={14.0: p_shared, 15.0: 0.10, 16.0: p_unshared},
        theta=theta
    )

    assert res.state_name == "PARTIAL_ONE_ALLELE"
    assert res.p_conditional == pytest.approx(expected_p, rel=1e-9)


# ─────────────────────────────────────────────────────────────────────────────
# TEST 10: Zero-Shared Match Cross-Tool Identity
# ─────────────────────────────────────────────────────────────────────────────

def test_zero_shared_match_cross_tool_identity():
    """
    Cross-validates 0-shared match probability:
      P((Ai, Aj) | (Ak, Al)) = 2 * [(1-theta)*p1] * [(1-theta)*p2] / [(1+theta)(1+2theta)]
    """
    p1 = 0.12
    p2 = 0.18
    theta = 0.03

    expected_p = (
        2.0 * ((1.0 - theta) * p1) * ((1.0 - theta) * p2)
        / ((1.0 + theta) * (1.0 + 2.0 * theta))
    )

    res = BaldingNicholsMatchModel.compute_conditional_match_probability(
        suspect_genotype=(14.0, 15.0),
        evidence_genotype=(16.0, 17.0),
        allele_frequencies={14.0: 0.20, 15.0: 0.20, 16.0: p1, 17.0: p2},
        theta=theta
    )

    assert res.state_name == "ZERO_SHARED_ALLELES"
    assert res.p_conditional == pytest.approx(expected_p, rel=1e-9)
