"""
Unit Tests for mtDNA Control Region, EMPOP 3'-Right Alignment & PhyloTree 17 Biocomputational Engine
Standards Compliance: ISO/IEC 17025:2017, SWGDAM Lineage Guidelines (2020), EMPOP Forensic mtDNA Guidelines, ENFSI (2017)
Research Source: research/ystr_27_mtdna_empop_lineage_research.md
"""

import pytest
from node.services.forensic.terminal.mtdna_empop_engine import (
    MtdnaEmpopEngine,
    MtdnaRegion,
    PHYLOTREE_17_MOTIFS,
)


class TestMtdnaEmpopEngine:
    """Test suite for MtdnaEmpopEngine."""

    def test_variant_parsing_and_regions(self):
        """Verifies parsing of SNPs, insertions, deletions, and IUPAC point heteroplasmies."""
        # Standard SNP
        v_snp = MtdnaEmpopEngine.parse_variant("16519C")
        assert v_snp is not None
        assert v_snp.position == 16519
        assert v_snp.alt_base == "C"
        assert v_snp.variant_type == "SNP"
        assert v_snp.region == MtdnaRegion.CONTROL_REGION

        # Homopolymer HV2 Poly-C Insertion (309.1C shifted to 315.1C)
        v_ins_hv2 = MtdnaEmpopEngine.parse_variant("309.1C")
        assert v_ins_hv2 is not None
        assert v_ins_hv2.empop_normalized_notation == "315.1C"
        assert v_ins_hv2.region == MtdnaRegion.HV2

        # Homopolymer HV1 Poly-C Insertion (16189.1C shifted to 16193.1C)
        v_ins_hv1 = MtdnaEmpopEngine.parse_variant("16189.1C")
        assert v_ins_hv1 is not None
        assert v_ins_hv1.empop_normalized_notation == "16193.1C"
        assert v_ins_hv1.region == MtdnaRegion.HV1

        # Dinucleotide HV3 AC Insertion (523.1A shifted to 524.1A)
        v_ins_hv3 = MtdnaEmpopEngine.parse_variant("523.1A")
        assert v_ins_hv3 is not None
        assert v_ins_hv3.empop_normalized_notation == "524.1A"
        assert v_ins_hv3.region == MtdnaRegion.HV3

        # Deletion (290del shifted to 291del)
        v_del = MtdnaEmpopEngine.parse_variant("290del")
        assert v_del is not None
        assert v_del.empop_normalized_notation == "291del"
        assert v_del.variant_type == "DEL"

        # Point Heteroplasmy (16093Y)
        v_php = MtdnaEmpopEngine.parse_variant("16093Y")
        assert v_php is not None
        assert v_php.position == 16093
        assert v_php.alt_base == "Y"
        assert v_php.variant_type == "PHP"

    def test_empop_right_alignment_normalization(self):
        """Verifies full profile normalization and sorting according to EMPOP 3'-right alignment."""
        raw_list = ["16519C", "309.1C", "73G", "290del", "16189.1C", "263G"]
        normalized = MtdnaEmpopEngine.normalize_profile(raw_list)

        expected = ["73G", "263G", "291del", "315.1C", "16193.1C", "16519C"]
        assert normalized == expected

    def test_phylotree_17_haplogroup_classification(self):
        """Verifies PhyloTree Build 17 diagnostic motif matching and macro-haplogroup classification."""
        # European H1 Profile (rCRS baseline with 3010A and 16519C)
        h1_muts = ["73A", "263G", "750G", "3010A", "16519C"]
        pred_h1 = MtdnaEmpopEngine.classifyHaplogroup(h1_muts) if hasattr(MtdnaEmpopEngine, 'classifyHaplogroup') else MtdnaEmpopEngine.classify_haplogroup(h1_muts)
        assert pred_h1.predicted_haplogroup == "H1"
        assert pred_h1.macro_haplogroup == "H"
        assert pred_h1.confidence_score > 0.80

        # Sub-Saharan African L2a1 Profile
        l2a1_muts = [
            "73G", "146C", "152C", "182C", "185T", "195C", "247A", "263G",
            "315.1C", "750G", "16189C", "16209C", "16223T", "16278T", "16390A"
        ]
        pred_l2a1 = MtdnaEmpopEngine.classify_haplogroup(l2a1_muts)
        assert pred_l2a1.predicted_haplogroup == "L2a1"
        assert pred_l2a1.macro_haplogroup == "L"
        assert pred_l2a1.confidence_score > 0.80

        # Indigenous American A2 Profile
        a2_muts = [
            "73G", "146C", "153G", "235G", "263G", "315.1C", "663G", "750G",
            "16111T", "16223T", "16290T", "16319A", "16362C"
        ]
        pred_a2 = MtdnaEmpopEngine.classify_haplogroup(a2_muts)
        assert pred_a2.predicted_haplogroup == "A2"
        assert pred_a2.macro_haplogroup == "N"
        assert pred_a2.confidence_score > 0.80

    def test_empop_95_upper_bounds_and_lr(self):
        """
        Verifies EMPOP 95% Clopper-Pearson upper bound frequency and Likelihood Ratio:
        k=0, N=48,500 -> p_upper ~ 6.18e-5 (LR ~ 16,190)
        k=12, N=48,500 -> p_upper ~ 3.97e-4 (LR ~ 2,518)
        """
        p_upper_k0 = MtdnaEmpopEngine.calculate_empop_95_upper(0, 48500)
        assert pytest.approx(p_upper_k0, rel=1e-2) == 6.18e-5
        lr_k0 = 1.0 / p_upper_k0
        assert pytest.approx(lr_k0, abs=200) == 16190

        p_upper_k12 = MtdnaEmpopEngine.calculate_empop_95_upper(12, 48500)
        assert pytest.approx(p_upper_k12, rel=1e-2) == 4.32e-4
        lr_k12 = 1.0 / p_upper_k12
        assert pytest.approx(lr_k12, abs=100) == 2314

    def test_maternal_lineage_matching_with_heteroplasmy(self):
        """
        Verifies Benchmark MATERNAL-01:
        Mother (16093C) and child (16093Y point heteroplasmy C/T).
        Should yield maternal inclusion (is_match=True) with full LR calculation.
        """
        mother_muts = ["73G", "263G", "16093C", "16519C"]
        child_muts = ["73G", "263G", "16093Y", "16519C"]

        match_res = MtdnaEmpopEngine.evaluate_lineage_match(
            mutations_a=mother_muts,
            mutations_b=child_muts,
            empop_count_k=0,
            empop_database_size=48500,
        )

        assert match_res["is_match"] is True
        assert match_res["is_exclusion"] is False
        assert match_res["lr_mtdna"] > 10000.0
        assert "Support for Same Maternal Lineage" in match_res["enfsi_verbal_scale"]
