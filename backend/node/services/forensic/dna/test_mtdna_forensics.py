"""
Unit & Integration Tests for FORENZA mtDNA Control Region Forensics & EMPOP Engine — Module 08.

Tests verbatim from Pillar 2 Research §3:
  - §3.1 Control Region Hypervariable Alignment (HV1: 16024–16365, HV2: 73–340, HV3: 438–574)
  - §3.1 ISFG 3' Right-Alignment for Homopolymeric Poly-C Tracts (16189.1C, 309.1C, 522del)
  - §3.2 Point Heteroplasmy (PHP) & IUPAC Ambiguity Codes (Y, R, W, S, K, M)
  - §3.2 EMPOP Exact Binomial Upper Bound (Clopper-Pearson 95%) & Maternal LR
  - §3.2 Pairwise Maternal Concordance Rules (0 diffs = Match, 1 diff = Inconclusive, >= 2 = Exclusion)

Benchmark Vectors:
  VECTOR_08_MTDNA_A — Hypervariable regions (HV1/HV2/HV3) ranges and classification
  VECTOR_08_MTDNA_B — ISFG 3' right-alignment rules (16189.1C, 309.1C, 522del)
  VECTOR_08_MTDNA_C — IUPAC point heteroplasmy mappings and compatibility
  VECTOR_08_MTDNA_D — EMPOP k=0 exact binomial upper bound & monotonic decrease with N
  VECTOR_08_MTDNA_E — EMPOP k>0 exact Beta quantile bounds and ordering
  VECTOR_08_MTDNA_F — Pairwise maternal identity (0 differences -> CANNOT_BE_EXCLUDED)
  VECTOR_08_MTDNA_G — Single difference (INCONCLUSIVE) and >=2 differences (EXCLUDED)
  VECTOR_08_MTDNA_H — API integration across all endpoints
"""

import math
from typing import Dict, List, Optional, Tuple
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.dna.mtdna_engine import (
    MtDNAEngine,
    MtDNAVariant,
    MtDNAProfile,
    HV1_RANGE,
    HV2_RANGE,
    HV3_RANGE,
    IUPAC_HETEROPLASMY_MAP,
    bases_to_iupac,
    are_iupac_bases_compatible,
    get_region_for_position,
)
from app.api.mtdna_routes import router as mtdna_router

_app = FastAPI()
_app.include_router(mtdna_router, prefix="/api/v1")
client = TestClient(_app)

engine = MtDNAEngine()


# ── VECTOR_08_MTDNA_A — Hypervariable Regions & Boundaries ────────────────────

class TestVector08MtDNAA:
    """Verifies HV1, HV2, and HV3 control region definitions."""

    def test_hv_region_boundaries(self):
        assert HV1_RANGE == (16024, 16365)
        assert HV2_RANGE == (73, 340)
        assert HV3_RANGE == (438, 574)

    def test_get_region_for_position(self):
        assert get_region_for_position(16189) == "HV1"
        assert get_region_for_position(16024) == "HV1"
        assert get_region_for_position(16365) == "HV1"
        assert get_region_for_position(73) == "HV2"
        assert get_region_for_position(263) == "HV2"
        assert get_region_for_position(340) == "HV2"
        assert get_region_for_position(438) == "HV3"
        assert get_region_for_position(522) == "HV3"
        assert get_region_for_position(574) == "HV3"
        assert get_region_for_position(1000) == "CR_OTHER"


# ── VECTOR_08_MTDNA_B — ISFG 3' Right-Alignment Rules ─────────────────────────

class TestVector08MtDNAB:
    """Verifies ISFG 3' right-alignment for homopolymeric C-tracts and repeats."""

    def test_hv2_309_c_insertion_alignment(self):
        # Unaligned 308.1C is normalized to ISFG 309.1C
        v = MtDNAVariant(position=308, ref_base="", alt_base="C", region="HV2", variant_type="INSERTION", insertion_index=1)
        aligned = engine.apply_isfg_right_alignment([v])
        assert len(aligned) == 1
        assert aligned[0].position == 309
        assert aligned[0].notation == "309.1C"

    def test_hv1_16189_c_insertion_alignment(self):
        # Unaligned 16188.1C is normalized to ISFG 16189.1C
        v = MtDNAVariant(position=16188, ref_base="", alt_base="C", region="HV1", variant_type="INSERTION", insertion_index=1)
        aligned = engine.apply_isfg_right_alignment([v])
        assert len(aligned) == 1
        assert aligned[0].position == 16189
        assert aligned[0].notation == "16189.1C"

    def test_standard_snp_unaffected(self):
        v = MtDNAVariant(position=263, ref_base="A", alt_base="G", region="HV2", variant_type="SNP")
        aligned = engine.apply_isfg_right_alignment([v])
        assert len(aligned) == 1
        assert aligned[0].position == 263
        assert aligned[0].notation == "263G"


# ── VECTOR_08_MTDNA_C — IUPAC Point Heteroplasmy (PHP) ────────────────────────

class TestVector08MtDNAC:
    """Verifies IUPAC point heteroplasmy mapping and compatibility logic."""

    def test_bases_to_iupac(self):
        assert bases_to_iupac(["C", "T"]) == "Y"
        assert bases_to_iupac(["A", "G"]) == "R"
        assert bases_to_iupac(["A", "T"]) == "W"
        assert bases_to_iupac(["C", "G"]) == "S"
        assert bases_to_iupac(["G", "T"]) == "K"
        assert bases_to_iupac(["A", "C"]) == "M"
        assert bases_to_iupac(["A"]) == "A"
        assert bases_to_iupac(["C"]) == "C"

    def test_iupac_compatibility(self):
        # Y (C/T) is compatible with C, T, and Y
        assert are_iupac_bases_compatible("Y", "C") is True
        assert are_iupac_bases_compatible("Y", "T") is True
        assert are_iupac_bases_compatible("Y", "Y") is True
        # Y (C/T) is incompatible with A and G
        assert are_iupac_bases_compatible("Y", "A") is False
        assert are_iupac_bases_compatible("Y", "G") is False
        # R (A/G) vs S (C/G) share G
        assert are_iupac_bases_compatible("R", "S") is True


# ── VECTOR_08_MTDNA_D — EMPOP k=0 Exact Binomial Upper Bound ──────────────────

class TestVector08MtDNAD:
    """Verifies EMPOP exact binomial upper bound for unobserved haplotypes (k=0)."""

    def test_k0_formula_exact(self):
        # N = 48500, alpha = 0.05
        # p_upper = 1 - (0.05)^(1 / 48501)
        res = engine.calculate_empop_match_probability(k=0, n_empop=48500, alpha=0.05)
        expected_p = 1.0 - math.pow(0.05, 1.0 / 48501.0)
        assert res.p_upper_bound == pytest.approx(expected_p, rel=1e-5)
        assert res.is_unobserved is True
        # Maternal LR = 1 / p_upper
        assert res.maternal_lr == pytest.approx(1.0 / expected_p, rel=1e-3)
        assert res.log10_maternal_lr == pytest.approx(math.log10(1.0 / expected_p), abs=1e-3)

    def test_k0_p_upper_decreases_with_n(self):
        p_10k = engine.calculate_empop_match_probability(k=0, n_empop=10000).p_upper_bound
        p_25k = engine.calculate_empop_match_probability(k=0, n_empop=25000).p_upper_bound
        p_48k = engine.calculate_empop_match_probability(k=0, n_empop=48500).p_upper_bound

        assert p_10k > p_25k > p_48k


# ── VECTOR_08_MTDNA_E — EMPOP k>0 Beta Quantile Bounds ────────────────────────

class TestVector08MtDNAE:
    """Verifies EMPOP exact Beta quantile bounds for observed haplotypes (k>0)."""

    def test_k_greater_than_zero_ordering(self):
        p_k0 = engine.calculate_empop_match_probability(k=0, n_empop=48500).p_upper_bound
        p_k1 = engine.calculate_empop_match_probability(k=1, n_empop=48500).p_upper_bound
        p_k5 = engine.calculate_empop_match_probability(k=5, n_empop=48500).p_upper_bound
        p_k50 = engine.calculate_empop_match_probability(k=50, n_empop=48500).p_upper_bound

        assert p_k0 < p_k1 < p_k5 < p_k50

    def test_k_equals_n_boundary(self):
        res = engine.calculate_empop_match_probability(k=1000, n_empop=1000)
        assert res.p_upper_bound == 1.0


# ── VECTOR_08_MTDNA_F — Pairwise Maternal Identity Match (0 Diffs) ────────────

class TestVector08MtDNAF:
    """Verifies pairwise maternal concordance for identical sequences (0 diffs)."""

    def test_identical_haplotype_cannot_be_excluded(self):
        v1 = [
            MtDNAVariant(73, "A", "G", "HV2", "SNP"),
            MtDNAVariant(263, "A", "G", "HV2", "SNP"),
            MtDNAVariant(315, "", "C", "HV2", "INSERTION", 1),
            MtDNAVariant(16189, "T", "C", "HV1", "SNP"),
        ]
        v2 = [
            MtDNAVariant(73, "A", "G", "HV2", "SNP"),
            MtDNAVariant(263, "A", "G", "HV2", "SNP"),
            MtDNAVariant(315, "", "C", "HV2", "INSERTION", 1),
            MtDNAVariant(16189, "T", "C", "HV1", "SNP"),
        ]

        p_ev = MtDNAProfile("EVIDENCE", haplogroup="H1", variants=v1)
        p_sus = MtDNAProfile("SUSPECT", haplogroup="H1", variants=v2)

        res = engine.evaluate_mtdna_maternal_match(p_ev, p_sus, n_empop=48500, empop_observed_k=0)

        assert res.match_status == "CANNOT_BE_EXCLUDED"
        assert res.differing_positions_count == 0
        assert res.maternal_lr > 10000.0
        assert "Maternal Lineage Match" in res.maternal_lineage_verdict
        assert len(res.prosecutors_fallacy_shield) > 50

    def test_compatible_heteroplasmy_treated_as_match(self):
        # Evidence has heteroplasmy 16189Y (C/T), suspect has homoplasmy 16189C
        v1 = [MtDNAVariant(16189, "T", "Y", "HV1", "HETEROPLASMY")]
        v2 = [MtDNAVariant(16189, "T", "C", "HV1", "SNP")]

        p_ev = MtDNAProfile("EVIDENCE", variants=v1)
        p_sus = MtDNAProfile("SUSPECT", variants=v2)

        res = engine.evaluate_mtdna_maternal_match(p_ev, p_sus)
        assert res.differing_positions_count == 0
        assert res.match_status == "CANNOT_BE_EXCLUDED"
        assert len(res.point_heteroplasmies_detected) > 0


# ── VECTOR_08_MTDNA_G — Inconclusive (1 Diff) & Exclusion (>=2 Diffs) ─────────

class TestVector08MtDNAG:
    """Verifies SWGDAM rules: 1 diff = Inconclusive, >= 2 diffs = Exclusion."""

    def test_single_difference_is_inconclusive(self):
        v1 = [
            MtDNAVariant(73, "A", "G", "HV2", "SNP"),
            MtDNAVariant(263, "A", "G", "HV2", "SNP"),
        ]
        v2 = [
            MtDNAVariant(73, "A", "G", "HV2", "SNP"),
            MtDNAVariant(263, "A", "G", "HV2", "SNP"),
            MtDNAVariant(16189, "T", "C", "HV1", "SNP"),  # 1 extra difference
        ]

        p_ev = MtDNAProfile("EVIDENCE", variants=v1)
        p_sus = MtDNAProfile("SUSPECT", variants=v2)

        res = engine.evaluate_mtdna_maternal_match(p_ev, p_sus)
        assert res.differing_positions_count == 1
        assert res.match_status == "INCONCLUSIVE"
        assert res.maternal_lr == 1.0
        assert res.log10_maternal_lr == 0.0
        assert "Inconclusive" in res.maternal_lineage_verdict

    def test_two_differences_is_exclusion(self):
        v1 = [
            MtDNAVariant(73, "A", "G", "HV2", "SNP"),
            MtDNAVariant(263, "A", "G", "HV2", "SNP"),
        ]
        v2 = [
            MtDNAVariant(73, "A", "A", "HV2", "SNP"),       # Diff 1
            MtDNAVariant(16189, "T", "C", "HV1", "SNP"),   # Diff 2 & 3
        ]

        p_ev = MtDNAProfile("EVIDENCE", variants=v1)
        p_sus = MtDNAProfile("SUSPECT", variants=v2)

        res = engine.evaluate_mtdna_maternal_match(p_ev, p_sus)
        assert res.differing_positions_count >= 2
        assert res.match_status == "EXCLUDED"
        assert res.maternal_lr == 0.0
        assert res.log10_maternal_lr == -999.0
        assert "Exclusion" in res.maternal_lineage_verdict


# ── VECTOR_08_MTDNA_H — API Integration Tests ──────────────────────────────────

class TestVector08MtDNAH:
    """API integration tests across all Module 08 endpoints."""

    def test_api_panel_metadata(self):
        resp = client.get("/api/v1/forensic/lineage/mtdna/panel-metadata")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["hypervariable_regions"]) == 3
        assert "NC_012920.1" in data["genbank_accession"]
        assert data["isfg_rules_active"] is True

    def test_api_empop_upper_bound_k0(self):
        payload = {"k": 0, "n_empop": 48500, "alpha": 0.05}
        resp = client.post("/api/v1/forensic/lineage/mtdna/empop-upper-bound", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_unobserved"] is True
        assert data["p_upper_bound"] > 0
        assert data["maternal_lr"] > 10000.0

    def test_api_evaluate_maternal_match_inclusion(self):
        payload = {
            "evidence": {
                "profile_id": "EV-01",
                "haplogroup": "H1a",
                "variants": [
                    {"position": 73, "ref_base": "A", "alt_base": "G", "region": "HV2", "variant_type": "SNP"},
                    {"position": 263, "ref_base": "A", "alt_base": "G", "region": "HV2", "variant_type": "SNP"},
                ],
            },
            "suspect": {
                "profile_id": "SUS-01",
                "haplogroup": "H1a",
                "variants": [
                    {"position": 73, "ref_base": "A", "alt_base": "G", "region": "HV2", "variant_type": "SNP"},
                    {"position": 263, "ref_base": "A", "alt_base": "G", "region": "HV2", "variant_type": "SNP"},
                ],
            },
            "n_empop": 48500,
            "empop_observed_k": 0,
        }
        resp = client.post("/api/v1/forensic/lineage/mtdna/evaluate-maternal-match", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["match_status"] == "CANNOT_BE_EXCLUDED"
        assert data["differing_positions_count"] == 0
        assert data["maternal_lr"] > 10000.0
        assert len(data["prosecutors_fallacy_shield"]) > 50
