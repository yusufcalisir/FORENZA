"""
Unit & Integration Tests for FORENZA X-STR Linkage & Female Kinship Analysis — Module 07.

Tests verbatim from Pillar 2 Research §2:
  - §2.1 Investigator Argus X-12 Panel & 4 Linkage Groups (LG1-LG4)
  - §2.1 Kosambi Mapping Function (d_cM -> r)
  - §2.2 Complex Female Pedigree Kinship Likelihood Ratios (KI_X):
           Father-Daughter, Paternal Half-Sisters (PHS), PGM-GD, Mother-Son, Full Sisters

Golden Benchmark Vectors:
  VECTOR_P2_02     — Paternal Half-Sisters (PHS) Analysis across LG1-LG4:
                     Obligate paternal allele sharing, mean intra-LG r = 0.01
                     Combined KI_X ≈ 1.854e5, log10(KI_X) ≈ 5.268
  VECTOR_07_XSTR_A — Argus X-12 12-locus metadata & 4 linkage groups completeness
  VECTOR_07_XSTR_B — Kosambi mapping function limits & exact points
  VECTOR_07_XSTR_C — Father-Daughter hemizygous transmission & exclusion
  VECTOR_07_XSTR_D — Paternal Half-Sisters (PHS) intra-cluster linkage correction
  VECTOR_07_XSTR_E — PGM-GD 50% linkage decay
  VECTOR_07_XSTR_F — Mother-Son heterozygous (0.5/p) vs homozygous (1.0/p)
  VECTOR_07_XSTR_G — Multi-cluster product rule log-space invariant
  VECTOR_07_XSTR_H — API integration across all endpoints
"""

import math
from typing import Dict, List, Optional, Tuple
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


from node.services.forensic.dna.xstr_engine import (
    XSTREngine,
    XSTRGenotype,
    XSTRProfile,
    ARGUS_X12_LINKAGE_GROUPS,
    ARGUS_X12_LOCI,
    normalize_xstr_locus_name,
)
from app.api.xstr_routes import router as xstr_router

_app = FastAPI()
_app.include_router(xstr_router, prefix="/api/v1")
client = TestClient(_app)

engine = XSTREngine()


# ── Benchmark Argus X-12 12-Locus Profiles ───────────────────────────────────

def make_argus_x12_phs_sisters(paternal_alleles: Dict[str, float], maternal1: Dict[str, float], maternal2: Dict[str, float]) -> Tuple[XSTRProfile, XSTRProfile]:
    """Generates two paternal half-sisters sharing the specified paternal X haplotype."""
    s1_loci: Dict[str, XSTRGenotype] = {}
    s2_loci: Dict[str, XSTRGenotype] = {}

    for loc, pat_a in paternal_alleles.items():
        mat1_a = maternal1.get(loc, pat_a + 2.0)
        mat2_a = maternal2.get(loc, pat_a + 3.0)
        s1_loci[loc] = XSTRGenotype(loc, pat_a, mat1_a)
        s2_loci[loc] = XSTRGenotype(loc, pat_a, mat2_a)

    s1 = XSTRProfile("SISTER-1", is_male=False, loci=s1_loci)
    s2 = XSTRProfile("SISTER-2", is_male=False, loci=s2_loci)
    return s1, s2


# Standard 12 Argus X-12 loci list
ARGUS_12_LOCI_LIST = [
    "DXS10148", "DXS10135", "DXS8378",   # LG1
    "DXS7132",  "DXS10074", "DXS10079",  # LG2
    "DXS10103", "HPRTB",    "DXS10101",  # LG3
    "DXS10146", "DXS10134", "DXS7423",   # LG4
]


# ── VECTOR_P2_02 — Golden Ground-Truth Benchmark ──────────────────────────────

class TestVectorP202:
    """
    VECTOR_P2_02 Golden Ground-Truth Benchmark (Research §6 Artifact D).
    Paternal half-sisters (PHS) analysis across LG1–LG4.
    Obligate paternal allele sharing across all 12 loci, mean intra-LG r = 0.01, empirical p_a = 0.3616.
    Expected: Combined KI_X ≈ 1.854e5, log10(KI_X) ≈ 5.268.
    """

    def test_vector_p2_02_analytical_formula(self):
        # Single locus PHS KI: (1 - r) * (1/p) + r = (0.99 / 0.3616) + 0.01 = 2.7480
        r = 0.01
        p = 0.361608
        ki_l = ((1.0 - r) * (1.0 / p)) + r
        assert ki_l == pytest.approx(2.748, abs=1e-3)

        # 12 loci: (2.7480)^12 ≈ 1.854e5, log10 ≈ 5.268
        combined_ki = math.pow(ki_l, 12)
        log10_ki = math.log10(combined_ki)

        assert combined_ki == pytest.approx(1.854e5, rel=1e-2)
        assert log10_ki == pytest.approx(5.268, abs=1e-3)

    def test_vector_p2_02_engine_evaluation(self):
        pat_alleles = {loc: 10.0 for loc in ARGUS_12_LOCI_LIST}
        mat1 = {loc: 12.0 for loc in ARGUS_12_LOCI_LIST}
        mat2 = {loc: 14.0 for loc in ARGUS_12_LOCI_LIST}

        s1, s2 = make_argus_x12_phs_sisters(pat_alleles, mat1, mat2)
        pop_freqs = {loc: 0.361608 for loc in ARGUS_12_LOCI_LIST}

        res = engine.evaluate_xstr_kinship(
            profile1=s1,
            profile2=s2,
            relationship="PATERNAL_HALF_SISTERS",
            population_frequencies=pop_freqs,
            custom_intra_r=0.01,
        )

        assert res.evaluated_loci_count == 12
        assert res.evaluated_clusters_count == 4
        assert res.is_excluded is False
        assert res.combined_ki_x == pytest.approx(1.854e5, rel=1e-2)
        assert res.log10_combined_ki_x == pytest.approx(5.268, abs=1e-3)
        assert "Strong Support" in res.kinship_verdict



# ── VECTOR_07_XSTR_A — Panel Metadata & Linkage Groups Completeness ───────────

class TestVector07XSTRA:
    """Verifies Argus X-12 12-locus panel metadata and 4 linkage groups."""

    def test_total_loci_count_is_12(self):
        assert len(ARGUS_X12_LOCI) == 12

    def test_linkage_groups_count_is_4(self):
        assert len(ARGUS_X12_LINKAGE_GROUPS) == 4
        assert set(ARGUS_X12_LINKAGE_GROUPS.keys()) == {"LG1", "LG2", "LG3", "LG4"}

    def test_each_linkage_group_has_3_loci(self):
        for grp_id, meta in ARGUS_X12_LINKAGE_GROUPS.items():
            assert len(meta.loci) == 3, f"{grp_id} has {len(meta.loci)} loci, expected 3"
            assert len(meta.recombination_rates) == 2
            assert len(meta.genetic_distances_cm) == 3

    def test_locus_name_normalization(self):
        assert normalize_xstr_locus_name("dxs10148") == "DXS10148"
        assert normalize_xstr_locus_name("DXS-10135") == "DXS10135"
        assert normalize_xstr_locus_name("HPRTB") == "HPRTB"


# ── VECTOR_07_XSTR_B — Kosambi Mapping Function ───────────────────────────────

class TestVector07XSTRB:
    """Kosambi mapping function mathematical verification."""

    def test_kosambi_zero_distance(self):
        # r(0) = 0.5 * tanh(0) = 0.0
        assert engine.kosambi_map_function(0.0) == 0.0

    def test_kosambi_at_50_cm(self):
        # r(50 cM) = 0.5 * tanh(1.0) = 0.5 * 0.761594 = 0.380797
        r = engine.kosambi_map_function(50.0)
        expected = 0.5 * math.tanh(1.0)
        assert r == pytest.approx(expected, abs=1e-6)

    def test_kosambi_infinite_distance_limit(self):
        # lim_{d -> infty} r(d) = 0.50 (Mendelian independent assortment)
        r = engine.kosambi_map_function(1000.0)
        assert r == pytest.approx(0.50, abs=1e-4)

    def test_kosambi_monotonic_increasing(self):
        distances = [0.0, 5.0, 10.0, 20.0, 50.0, 100.0]
        r_values = [engine.kosambi_map_function(d) for d in distances]
        for i in range(1, len(r_values)):
            assert r_values[i] > r_values[i - 1]


# ── VECTOR_07_XSTR_C — Father-Daughter Transmission & Exclusion Logic ──────────

class TestVector07XSTRC:
    """Father-Daughter (Duo) hemizygous transmission and exclusion tests."""

    def test_father_daughter_match(self):
        # Father: hemizygous 14.0; Daughter: 14.0/16.0
        father = XSTRGenotype("DXS10148", 14.0)
        daughter = XSTRGenotype("DXS10148", 14.0, 16.0)
        ki = engine.calculate_father_daughter_ki(father, daughter, p_allele=0.10)
        # KI = 1 / p = 1 / 0.10 = 10.0
        assert ki == pytest.approx(10.0, abs=1e-5)

    def test_father_daughter_exclusion_zero_ki(self):
        # Father: hemizygous 14.0; Daughter: 15.0/16.0 (does not have 14.0)
        father = XSTRGenotype("DXS10148", 14.0)
        daughter = XSTRGenotype("DXS10148", 15.0, 16.0)
        ki = engine.calculate_father_daughter_ki(father, daughter, p_allele=0.10)
        assert ki == 0.0

    def test_father_daughter_full_profile_evaluation(self):
        father_loci = {loc: XSTRGenotype(loc, 12.0) for loc in ARGUS_12_LOCI_LIST}
        daughter_loci = {loc: XSTRGenotype(loc, 12.0, 15.0) for loc in ARGUS_12_LOCI_LIST}

        p_father = XSTRProfile("FATHER", is_male=True, loci=father_loci)
        p_daughter = XSTRProfile("DAUGHTER", is_male=False, loci=daughter_loci)

        res = engine.evaluate_xstr_kinship(
            profile1=p_father,
            profile2=p_daughter,
            relationship="FATHER_DAUGHTER",
            population_frequencies={loc: 0.10 for loc in ARGUS_12_LOCI_LIST},
        )
        assert res.is_excluded is False
        # Combined KI = 10^12 = 1.0e12
        assert res.combined_ki_x == pytest.approx(1.0e12, rel=1e-3)
        assert res.log10_combined_ki_x == pytest.approx(12.0, abs=1e-3)


# ── VECTOR_07_XSTR_D — Paternal Half-Sisters (PHS) Linkage Correction ─────────

class TestVector07XSTRD:
    """Paternal Half-Sisters (PHS) intra-cluster linkage tests."""

    def test_phs_higher_r_reduces_ki(self):
        """As intra-cluster recombination r increases, PHS KI decreases toward uninformative."""
        s1 = XSTRGenotype("DXS10148", 10.0, 12.0)
        s2 = XSTRGenotype("DXS10148", 10.0, 14.0)

        ki_tight = engine.calculate_phs_locus_ki(s1, s2, recombination_r=0.001, p_allele=0.10)
        ki_loose = engine.calculate_phs_locus_ki(s1, s2, recombination_r=0.05, p_allele=0.10)
        ki_unlinked = engine.calculate_phs_locus_ki(s1, s2, recombination_r=0.50, p_allele=0.10)

        assert ki_tight > ki_loose > ki_unlinked
        # At r=0: KI = 1/p = 10.0; at r=0.50: KI = 0.5 * 10 + 0.5 = 5.5
        assert ki_unlinked == pytest.approx(5.5, abs=1e-5)


# ── VECTOR_07_XSTR_E — Paternal Grandmother - Granddaughter (PGM-GD) ──────────

class TestVector07XSTRE:
    """PGM-GD kinship tests."""

    def test_pgm_gd_shared_paternal_allele(self):
        # Shared allele: KI = 0.5 * (1/p) + 0.5 = 0.5 * 10.0 + 0.5 = 5.5
        pgm = XSTRGenotype("DXS10148", 10.0, 12.0)
        gd = XSTRGenotype("DXS10148", 10.0, 14.0)
        ki = engine.calculate_pgm_gd_ki(pgm, gd, p_allele=0.10)
        assert ki == pytest.approx(5.5, abs=1e-5)

    def test_pgm_gd_unshared_allele(self):
        # No shared allele: KI = 0.5
        pgm = XSTRGenotype("DXS10148", 10.0, 12.0)
        gd = XSTRGenotype("DXS10148", 13.0, 14.0)
        ki = engine.calculate_pgm_gd_ki(pgm, gd, p_allele=0.10)
        assert ki == pytest.approx(0.5, abs=1e-5)


# ── VECTOR_07_XSTR_F — Mother-Son (MS) Heterozygous vs Homozygous Likelihoods ──

class TestVector07XSTRF:
    """Mother-Son kinship tests."""

    def test_mother_son_heterozygous_mother(self):
        # Mother 10.0/12.0, Son 10.0 -> KI = 0.5 / p = 0.5 / 0.10 = 5.0
        mother = XSTRGenotype("DXS10148", 10.0, 12.0)
        son = XSTRGenotype("DXS10148", 10.0)
        ki = engine.calculate_mother_son_ki(mother, son, p_allele=0.10)
        assert ki == pytest.approx(5.0, abs=1e-5)

    def test_mother_son_homozygous_mother(self):
        # Mother 10.0/10.0, Son 10.0 -> KI = 1.0 / p = 1.0 / 0.10 = 10.0
        mother = XSTRGenotype("DXS10148", 10.0, 10.0)
        son = XSTRGenotype("DXS10148", 10.0)
        ki = engine.calculate_mother_son_ki(mother, son, p_allele=0.10)
        assert ki == pytest.approx(10.0, abs=1e-5)

    def test_mother_son_exclusion_zero_ki(self):
        # Mother 10.0/12.0, Son 14.0 -> Son does not have mother's allele -> KI = 0.0
        mother = XSTRGenotype("DXS10148", 10.0, 12.0)
        son = XSTRGenotype("DXS10148", 14.0)
        ki = engine.calculate_mother_son_ki(mother, son, p_allele=0.10)
        assert ki == 0.0


# ── VECTOR_07_XSTR_G — Multi-Cluster Product Rule Invariant ───────────────────

class TestVector07XSTRG:
    """Verifies that log10(Combined KI_X) = sum_g log10(KI_LG_g) exactly."""

    def test_product_rule_log_space_preservation(self):
        pat_alleles = {loc: 10.0 for loc in ARGUS_12_LOCI_LIST}
        mat1 = {loc: 12.0 for loc in ARGUS_12_LOCI_LIST}
        mat2 = {loc: 14.0 for loc in ARGUS_12_LOCI_LIST}

        s1, s2 = make_argus_x12_phs_sisters(pat_alleles, mat1, mat2)
        res = engine.evaluate_xstr_kinship(s1, s2, relationship="PATERNAL_HALF_SISTERS")

        sum_log_lg = sum(lg.log10_group_ki for lg in res.linkage_group_results)
        assert abs(res.log10_combined_ki_x - sum_log_lg) < 1e-4


# ── VECTOR_07_XSTR_H — API Integration Tests ──────────────────────────────────

class TestVector07XSTRH:
    """API integration tests across all Module 07 endpoints."""

    def test_api_panel_metadata_returns_12_loci_and_4_groups(self):
        resp = client.get("/api/v1/forensic/lineage/xstr/panel-metadata")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_loci"] == 12
        assert data["total_linkage_groups"] == 4

    def test_api_kosambi_map(self):
        payload = {"genetic_distance_cm": 50.0}
        resp = client.post("/api/v1/forensic/lineage/xstr/kosambi-map", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        expected_r = 0.5 * math.tanh(1.0)
        assert data["recombination_fraction_r"] == pytest.approx(expected_r, abs=1e-5)

    def test_api_evaluate_kinship_phs_vector_p2_02(self):
        loci_dict_s1 = {
            loc: {"locus": loc, "allele1": 10.0, "allele2": 12.0}
            for loc in ARGUS_12_LOCI_LIST
        }
        loci_dict_s2 = {
            loc: {"locus": loc, "allele1": 10.0, "allele2": 14.0}
            for loc in ARGUS_12_LOCI_LIST
        }

        payload = {
            "profile1": {"profile_id": "SISTER-1", "is_male": False, "loci": loci_dict_s1},
            "profile2": {"profile_id": "SISTER-2", "is_male": False, "loci": loci_dict_s2},
            "relationship": "PATERNAL_HALF_SISTERS",
            "population_frequencies": {loc: 0.361608 for loc in ARGUS_12_LOCI_LIST},
            "custom_intra_r": 0.01,
        }


        resp = client.post("/api/v1/forensic/lineage/xstr/evaluate-kinship", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["combined_ki_x"] == pytest.approx(1.854e5, rel=1e-2)
        assert data["log10_combined_ki_x"] == pytest.approx(5.268, abs=1e-3)
        assert data["is_excluded"] is False
        assert len(data["linkage_group_results"]) == 4
        assert len(data["prosecutors_fallacy_shield"]) > 50
