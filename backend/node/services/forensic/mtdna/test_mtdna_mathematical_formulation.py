"""
Unit Test Suite for FORENZA mtDNA Mathematical Formulation Engine (Module 2.3).
Validates variant parsing, ISFG 3'-right-alignment normalizer, IUPAC point heteroplasmy,
and Clopper-Pearson 95% database bounds.
"""

import pytest
import math

from node.services.forensic.mtdna.mtdna_mathematical_formulation import (
    MtDnaMathematicalFormulation,
    MtDnaVariant,
    MTDNA_CONTROL_REGION_DOMAINS,
    MTDNA_IUPAC_CODES,
    PhyloTreeHaplogroupPredictor,
)


class TestControlRegionDomains:
    """Verifies D-Loop control region domain metadata."""

    def test_domains_registered(self):
        assert len(MTDNA_CONTROL_REGION_DOMAINS) == 7
        assert "HV1" in MTDNA_CONTROL_REGION_DOMAINS
        assert "HV2" in MTDNA_CONTROL_REGION_DOMAINS
        assert "HV3" in MTDNA_CONTROL_REGION_DOMAINS

    def test_domain_coordinate_boundaries(self):
        hv1 = MTDNA_CONTROL_REGION_DOMAINS["HV1"]
        assert hv1.start_pos == 16024
        assert hv1.end_pos == 16365

        hv2 = MTDNA_CONTROL_REGION_DOMAINS["HV2"]
        assert hv2.start_pos == 73
        assert hv2.end_pos == 340

        hv3 = MTDNA_CONTROL_REGION_DOMAINS["HV3"]
        assert hv3.start_pos == 438
        assert hv3.end_pos == 574


class TestVariantParsingAndISFGRightAlignment:
    """Verifies ISFG nomenclature parsing and 3'-right-alignment rules."""

    def test_parse_substitution_and_php(self):
        v1 = MtDnaMathematicalFormulation.parse_variant_string("263G")
        assert v1.position == 263
        assert v1.variant_base == "G"
        assert v1.variant_type == "SUBSTITUTION"

        v2 = MtDnaMathematicalFormulation.parse_variant_string("16189Y")
        assert v2.position == 16189
        assert v2.variant_base == "Y"
        assert v2.variant_type == "PHP"

    def test_parse_insertions_and_deletions(self):
        v_ins = MtDnaMathematicalFormulation.parse_variant_string("309.1C")
        assert v_ins.position == 309
        assert v_ins.insertion_index == 1
        assert v_ins.variant_base == "C"
        assert v_ins.variant_type == "INSERTION"

        v_del = MtDnaMathematicalFormulation.parse_variant_string("522del")
        assert v_del.position == 522
        assert v_del.variant_type == "DELETION"

    def test_isfg_right_alignment_shifts_homopolymers(self):
        """HV2 poly-C 308.1C must be right-shifted to 309.1C."""
        raw_v = MtDnaVariant(
            position=308,
            ref_base="",
            variant_base="C",
            variant_type="INSERTION",
            insertion_index=1,
        )
        aligned = MtDnaMathematicalFormulation.apply_isfg_right_alignment([raw_v])
        assert len(aligned) == 1
        assert aligned[0].position == 309
        assert aligned[0].formatted_call == "309.1C"


class TestIupacPointHeteroplasmyAndPairwiseMatching:
    """Verifies IUPAC base compatibility and pairwise lineage decisions."""

    def test_iupac_compatibility(self):
        assert MtDnaMathematicalFormulation.are_bases_compatible("Y", "C") is True
        assert MtDnaMathematicalFormulation.are_bases_compatible("Y", "T") is True
        assert MtDnaMathematicalFormulation.are_bases_compatible("Y", "A") is False
        assert MtDnaMathematicalFormulation.are_bases_compatible("R", "G") is True
        assert MtDnaMathematicalFormulation.are_bases_compatible("R", "A") is True
        assert MtDnaMathematicalFormulation.are_bases_compatible("R", "T") is False

    def test_pairwise_exact_match(self):
        vars_a = [
            MtDnaMathematicalFormulation.parse_variant_string("263G"),
            MtDnaMathematicalFormulation.parse_variant_string("315.1C"),
            MtDnaMathematicalFormulation.parse_variant_string("16519C"),
        ]
        vars_b = [
            MtDnaMathematicalFormulation.parse_variant_string("263G"),
            MtDnaMathematicalFormulation.parse_variant_string("315.1C"),
            MtDnaMathematicalFormulation.parse_variant_string("16519C"),
        ]
        res = MtDnaMathematicalFormulation.evaluate_pairwise_lineage(vars_a, vars_b)
        assert res.verdict == "MATCH"
        assert res.is_concordant is True
        assert res.homoplasmic_differences_count == 0
        assert res.maternal_lr > 10000.0

    def test_pairwise_heteroplasmy_match(self):
        """Sample A with 16189Y and Sample B with 16189C must match."""
        vars_a = [
            MtDnaMathematicalFormulation.parse_variant_string("263G"),
            MtDnaMathematicalFormulation.parse_variant_string("16189Y"),
        ]
        vars_b = [
            MtDnaMathematicalFormulation.parse_variant_string("263G"),
            MtDnaMathematicalFormulation.parse_variant_string("16189C"),
        ]
        res = MtDnaMathematicalFormulation.evaluate_pairwise_lineage(vars_a, vars_b)
        assert res.verdict == "MATCH"
        assert res.heteroplasmic_shared_count == 1
        assert res.homoplasmic_differences_count == 0

    def test_pairwise_swgdam_two_difference_exclusion(self):
        """2 homoplasmic differences must trigger definitive exclusion (LR = 0.0)."""
        vars_a = [
            MtDnaMathematicalFormulation.parse_variant_string("263G"),
            MtDnaMathematicalFormulation.parse_variant_string("73G"),
            MtDnaMathematicalFormulation.parse_variant_string("16189C"),
        ]
        vars_b = [
            MtDnaMathematicalFormulation.parse_variant_string("263G"),
            # Missing 73G and 16189C -> 2 differences
        ]
        res = MtDnaMathematicalFormulation.evaluate_pairwise_lineage(vars_a, vars_b)
        assert res.verdict == "EXCLUSION"
        assert res.is_concordant is False
        assert res.homoplasmic_differences_count == 2
        assert res.maternal_lr == 0.0
        assert res.log10_maternal_lr == -300.0


class TestClopperPearsonBounds:
    """Verifies Clopper-Pearson frequency bounds."""

    def test_k0_bound_calculation(self):
        p_up = MtDnaMathematicalFormulation.compute_clopper_pearson_bound(k=0, n=48500)
        assert abs(p_up - 6.1764e-5) < 1e-7

    def test_k_positive_bound_monotonic(self):
        p0 = MtDnaMathematicalFormulation.compute_clopper_pearson_bound(k=0, n=48500)
        p1 = MtDnaMathematicalFormulation.compute_clopper_pearson_bound(k=1, n=48500)
        p10 = MtDnaMathematicalFormulation.compute_clopper_pearson_bound(k=10, n=48500)
        assert p0 < p1 < p10
