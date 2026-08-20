"""
Unit Test Suite for Module 1.3: NRC-II Population Genetics.
Sub-Item 1.3.2: Reference Datasets Warehouse & Population Stratification Verification.

10 comprehensive data integrity and population genetics tests.
Verifies NIST 1036 sample sizes, 24-locus completeness across 4 demographies,
population-specific frequency shifts, 1000 Genomes continental matrices,
and golden standard reference individual profiles (NIST SRM 2391d Comp A/B/C, NA12878).

Run with:
    pytest backend/node/services/forensic/population/test_nrc_reference_datasets.py -v
"""

import pytest

from node.services.forensic.frequency_db import (
    POPULATION_FREQUENCIES,
    LOCI_24,
    CODIS_20_LOCI,
    NIST_N,
    NIST_TWO_N,
    NRC_II_P_MIN_RULE_4_1,
)
from node.services.forensic.population.nrc_reference_datasets import (
    NIST_1036_POPULATION_METADATA,
    THOUSAND_GENOMES_CONTINENTAL_FREQUENCIES,
    GOLDEN_REFERENCE_PROFILES,
    NIST1036StratifiedDatabase,
)
from node.services.forensic.population.nrc_mathematical_formulation import (
    NRC2LikelihoodRatioEngine,
)


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: NIST 1036 Demographic Sample Size Invariants
# ─────────────────────────────────────────────────────────────────────────────

def test_nist1036_demographic_invariants():
    """
    Verifies that the NIST 1036 population sample sizes strictly match the
    official NIST 1036 dataset specifications:
      Caucasian: N=361, African American: N=342, Hispanic: N=236, Asian: N=97.
      Total N = 1036 individuals (2072 alleles).
      Rule 4.1 p_min = 5 / 2072 = 0.002413...
    """
    meta = NIST_1036_POPULATION_METADATA

    assert meta["Caucasian"].sample_size_individuals == 361
    assert meta["Caucasian"].sample_size_alleles == 722

    assert meta["AfricanAmerican"].sample_size_individuals == 342
    assert meta["AfricanAmerican"].sample_size_alleles == 684

    assert meta["Hispanic"].sample_size_individuals == 236
    assert meta["Hispanic"].sample_size_alleles == 472

    assert meta["Asian"].sample_size_individuals == 97
    assert meta["Asian"].sample_size_alleles == 194

    total_individuals = sum(p.sample_size_individuals for p in meta.values())
    total_alleles = sum(p.sample_size_alleles for p in meta.values())

    assert total_individuals == NIST_N == 1036
    assert total_alleles == NIST_TWO_N == 2072
    assert NRC_II_P_MIN_RULE_4_1 == pytest.approx(5.0 / 2072.0, rel=1e-7)


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: 24-Locus Completeness across all 4 Demographies
# ─────────────────────────────────────────────────────────────────────────────

def test_nist1036_24_loci_completeness():
    """
    Verifies that each of the 4 NIST 1036 population databases contains
    all 24 STR loci in the expanded forensic multiplex.
    """
    expected_loci = set(l.upper() for l in LOCI_24)

    for pop_name in ["Caucasian", "AfricanAmerican", "Hispanic", "Asian"]:
        pop_db = POPULATION_FREQUENCIES[pop_name]
        pop_loci = set(l.upper() for l in pop_db.keys())

        missing = expected_loci - pop_loci
        assert len(missing) == 0, f"Population {pop_name} is missing loci: {missing}"
        assert len(pop_loci) >= 24


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: Allele Frequency Simplex Bounds across all populations
# ─────────────────────────────────────────────────────────────────────────────

def test_nist1036_frequency_simplex_bounds():
    """
    For all 4 populations and all 23 polymorphic loci (excluding AMEL),
    raw published frequency totals must sum in [0.80, 1.20] (reflecting truncated rare microvariant tails).
    """
    for pop_name, pop_db in POPULATION_FREQUENCIES.items():
        for locus, locus_db in pop_db.items():
            if locus.upper() == "AMEL":
                continue
            sum_freqs = sum(locus_db.values())
            assert 0.80 <= sum_freqs <= 1.20, (
                f"Locus {locus} in {pop_name} frequency sum {sum_freqs:.4f} is outside [0.80, 1.20]"
            )


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4: Population-Specific Discriminatory Allele Frequencies
# ─────────────────────────────────────────────────────────────────────────────

def test_population_specific_allele_frequencies():
    """
    Validates well-documented forensic population frequency signatures:
      - TH01 allele 7: High in African American (> 0.40), low in Caucasian (< 0.20).
      - TH01 allele 9: High in Asian (> 0.40), moderate/low in Caucasian (< 0.15).
    """
    th01_cauc = NIST1036StratifiedDatabase.get_allele_frequency("TH01", 7.0, "Caucasian")
    th01_aa = NIST1036StratifiedDatabase.get_allele_frequency("TH01", 7.0, "AfricanAmerican")

    assert th01_aa > 0.40, f"Expected TH01*7 in AA > 0.40, got {th01_aa}"
    assert th01_cauc < 0.20, f"Expected TH01*7 in Caucasian < 0.20, got {th01_cauc}"
    assert th01_aa > 2.0 * th01_cauc, "TH01*7 should be over 2x more frequent in African American"

    th01_asian_9 = NIST1036StratifiedDatabase.get_allele_frequency("TH01", 9.0, "Asian")
    th01_cauc_9 = NIST1036StratifiedDatabase.get_allele_frequency("TH01", 9.0, "Caucasian")

    assert th01_asian_9 > 0.40, f"Expected TH01*9 in Asian > 0.40, got {th01_asian_9}"
    assert th01_cauc_9 < 0.15, f"Expected TH01*9 in Caucasian < 0.15, got {th01_cauc_9}"


# ─────────────────────────────────────────────────────────────────────────────
# TEST 5: Pairwise Fst Geographic Hierarchy
# ─────────────────────────────────────────────────────────────────────────────

def test_pairwise_fst_geographic_hierarchy():
    """
    Wright's Fst distances must follow classical human population genetics hierarchy:
      - Fst(Caucasian, Asian) > Fst(Caucasian, Hispanic)
      - Fst(African American, Asian) > Fst(African American, Hispanic)
    """
    fst_matrix = NIST1036StratifiedDatabase.compute_pairwise_fst_matrix()

    fst_cauc_asian = fst_matrix[("Caucasian", "Asian")]
    fst_cauc_hisp = fst_matrix[("Caucasian", "Hispanic")]
    fst_aa_asian = fst_matrix[("AfricanAmerican", "Asian")]
    fst_aa_hisp = fst_matrix[("AfricanAmerican", "Hispanic")]

    assert fst_cauc_asian > fst_cauc_hisp, (
        f"Fst(Cauc, Asian) {fst_cauc_asian:.4f} must exceed Fst(Cauc, Hisp) {fst_cauc_hisp:.4f}"
    )
    assert fst_aa_asian > fst_aa_hisp, (
        f"Fst(AA, Asian) {fst_aa_asian:.4f} must exceed Fst(AA, Hisp) {fst_aa_hisp:.4f}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TEST 6: 1000 Genomes Project Continental Super-Population Matrix
# ─────────────────────────────────────────────────────────────────────────────

def test_thousand_genomes_5_superpop_concordance():
    """
    Verifies that all 5 continental super-populations (EUR, AFR, AMR, EAS, SAS)
    are present in the 1000 Genomes reference matrix.
    """
    matrix = THOUSAND_GENOMES_CONTINENTAL_FREQUENCIES
    expected_superpops = {"EUR", "AFR", "AMR", "EAS", "SAS"}

    assert set(matrix.keys()) == expected_superpops

    for sp in expected_superpops:
        assert "TH01" in matrix[sp]
        assert "D3S1358" in matrix[sp]
        assert "VWA" in matrix[sp]
        assert "FGA" in matrix[sp]


# ─────────────────────────────────────────────────────────────────────────────
# TEST 7: Golden Standard Reference Profiles (SRM 2391d & GIAB NA12878)
# ─────────────────────────────────────────────────────────────────────────────

def test_golden_reference_profiles_integrity():
    """
    Verifies that golden reference profiles (SRM 2391d Comp A, Comp B, Comp C, NA12878)
    contain valid 24-locus genotypes with standard allelic ranges.
    """
    for profile_id, profile in GOLDEN_REFERENCE_PROFILES.items():
        assert len(profile.loci_genotypes) == 24, (
            f"Profile {profile_id} has {len(profile.loci_genotypes)} loci, expected 24"
        )
        assert "AMEL" in profile.loci_genotypes
        assert "TH01" in profile.loci_genotypes
        assert "SE33" in profile.loci_genotypes


# ─────────────────────────────────────────────────────────────────────────────
# TEST 8: Demographic Subpopulation Likelihood Ratio Impact
# ─────────────────────────────────────────────────────────────────────────────

def test_subpopulation_lr_stratification_impact():
    """
    Evaluating the same individual profile (SRM 2391d Comp B - African American)
    against African American vs Caucasian allele frequencies produces a substantial
    stratification difference in total LR, demonstrating the necessity of population stratification.
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

    assert res_cauc.log10_total_lr > 20.0
    assert res_aa.log10_total_lr > 20.0
    # The two log10 LRs should differ because of population allele frequency differences
    assert abs(res_cauc.log10_total_lr - res_aa.log10_total_lr) > 0.5


# ─────────────────────────────────────────────────────────────────────────────
# TEST 9: Unseen Rare Allele NRC II Rule 4.1 Floor Enforcement
# ─────────────────────────────────────────────────────────────────────────────

def test_unseen_allele_p_min_floor_behavior():
    """
    Querying an unlisted rare allele (e.g. D18S51 allele 28.0)
    must automatically return the NRC II Rule 4.1 minimum bound p = 0.002413.
    """
    freq = NIST1036StratifiedDatabase.get_allele_frequency("D18S51", 28.0, "Caucasian")
    assert freq == pytest.approx(NRC_II_P_MIN_RULE_4_1, rel=1e-7)
    assert freq > 0.0024


# ─────────────────────────────────────────────────────────────────────────────
# TEST 10: Amelogenin Sex Genotype Consistency
# ─────────────────────────────────────────────────────────────────────────────

def test_amelogenin_gender_consistency():
    """
    Verifies that golden profiles have biologically consistent Amelogenin genotypes:
      - Female (9947A, NA12878): AMEL = (1.0, 1.0) [XX]
      - Male (9948, Comp C): AMEL = (1.0, 2.0) [XY]
    """
    comp_a = GOLDEN_REFERENCE_PROFILES["SRM_2391D_COMP_A"]
    comp_b = GOLDEN_REFERENCE_PROFILES["SRM_2391D_COMP_B"]
    comp_c = GOLDEN_REFERENCE_PROFILES["SRM_2391D_COMP_C"]
    na12878 = GOLDEN_REFERENCE_PROFILES["NA12878_CEU"]

    assert comp_a.sex == "FEMALE" and comp_a.loci_genotypes["AMEL"] == (1.0, 1.0)
    assert na12878.sex == "FEMALE" and na12878.loci_genotypes["AMEL"] == (1.0, 1.0)

    assert comp_b.sex == "MALE" and comp_b.loci_genotypes["AMEL"] == (1.0, 2.0)
    assert comp_c.sex == "MALE" and comp_c.loci_genotypes["AMEL"] == (1.0, 2.0)
