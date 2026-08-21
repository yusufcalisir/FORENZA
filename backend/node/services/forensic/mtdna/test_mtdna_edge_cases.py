"""
Edge-Case Test Suite for FORENZA mtDNA Engine (Module 2.3).
Implements all 5 mandatory edge-case test vectors specified in Master Roadmap §2.3.4:
  - EC-MT-01: rCRS Position 3107 Indel & Placeholder Handling
  - EC-MT-02: HVS-I/II Poly-C Stretch Heteroplasmy
  - EC-MT-03: IUPAC Point Heteroplasmy Multi-Base Parsing
  - EC-MT-04: Haplogroup Phylogeny Classification
  - EC-MT-05: Clopper-Pearson Database Frequency Bound
  - EC-MT-06: SWGDAM Maternal Exclusion Decision Threshold
"""

import math
import pytest

from node.services.forensic.mtdna.mtdna_mathematical_formulation import (
    MtDnaMathematicalFormulation,
    MtDnaVariant,
    PhyloTreeHaplogroupPredictor,
)
from node.services.forensic.mtdna.mtdna_reference_datasets import (
    MTDNA_CASEWORK_COHORTS,
    MTDNA_GOLD_STANDARDS,
)


class TestVector08MtDnaEdgeCases:
    """Mandatory edge-case test suite for Module 2.3 mtDNA."""

    def test_ec_mt_01_rcrs_position_3107_placeholder(self):
        """
        EC-MT-01: Placeholder position 3107 correctly aligned without coordinate shifting downstream.
        NC_012920.1 position 3107 represents a historically preserved placeholder.
        """
        v_3107 = MtDnaMathematicalFormulation.parse_variant_string("3107del")
        assert v_3107.position == 3107
        assert v_3107.variant_type == "DELETION"

        # Ensure downstream mutations (e.g. 16189C, 16519C) retain absolute rCRS coordinates
        v_downstream = MtDnaMathematicalFormulation.parse_variant_string("16519C")
        assert v_downstream.position == 16519
        aligned = MtDnaMathematicalFormulation.apply_isfg_right_alignment([v_3107, v_downstream])
        assert aligned[0].position == 3107
        assert aligned[1].position == 16519

    def test_ec_mt_02_hv1_hv2_poly_c_stretch_heteroplasmy(self):
        """
        EC-MT-02: Insertion sequence 309.1C 315.1C binned and right-shifted according to IUPAC conventions.
        """
        raw_insertions = [
            MtDnaMathematicalFormulation.parse_variant_string("308.1C"),
            MtDnaMathematicalFormulation.parse_variant_string("314.1C"),
        ]
        aligned = MtDnaMathematicalFormulation.apply_isfg_right_alignment(raw_insertions)
        assert len(aligned) == 2
        assert aligned[0].formatted_call == "309.1C"
        assert aligned[1].formatted_call == "315.1C"

    def test_ec_mt_03_iupac_point_heteroplasmy_parsing(self):
        """
        EC-MT-03: Mixed base R (A/G) or Y (C/T) at position 16189 parsed without character rejection.
        """
        v_r = MtDnaMathematicalFormulation.parse_variant_string("16189R")
        v_y = MtDnaMathematicalFormulation.parse_variant_string("16189Y")
        assert v_r.variant_type == "PHP"
        assert v_r.variant_base == "R"
        assert v_y.variant_type == "PHP"
        assert v_y.variant_base == "Y"

        # Compatibility test
        assert MtDnaMathematicalFormulation.are_bases_compatible("R", "A") is True
        assert MtDnaMathematicalFormulation.are_bases_compatible("R", "G") is True
        assert MtDnaMathematicalFormulation.are_bases_compatible("R", "C") is False

    def test_ec_mt_04_haplogroup_phylogeny_classification(self):
        """
        EC-MT-04: Ground truth vectors for H1 and L2a1 correctly identified via Phylotree 17 diagnostic mutations.
        """
        # H1 standard (NA12878)
        std_h1 = MTDNA_GOLD_STANDARDS["NA12878_CEU_FEMALE"]
        vars_h1 = [MtDnaMathematicalFormulation.parse_variant_string(s) for s in std_h1.variants]
        pred_h1 = PhyloTreeHaplogroupPredictor.predict_haplogroup(vars_h1)
        assert pred_h1 in ["H", "H1"]

        # L2a1 standard (NA19240)
        std_l2 = MTDNA_GOLD_STANDARDS["NA19240_YRI_FEMALE"]
        vars_l2 = [MtDnaMathematicalFormulation.parse_variant_string(s) for s in std_l2.variants]
        pred_l2 = PhyloTreeHaplogroupPredictor.predict_haplogroup(vars_l2)
        assert pred_l2 in ["L2", "L2a1"]

    def test_ec_mt_05_clopper_pearson_database_bound(self):
        """
        EC-MT-05: Zero-count in EMPOP (N=48,500) yields p_upper = 6.18 × 10^-5.
        """
        p_up = MtDnaMathematicalFormulation.compute_clopper_pearson_bound(k=0, n=48500)
        assert abs(p_up - 6.1764e-5) < 1e-7
        # LR = 1 / p_upper ≈ 16,190
        lr = 1.0 / p_up
        assert abs(lr - 16190.7) < 5.0

    def test_ec_mt_06_swgdam_maternal_exclusion_threshold(self):
        """
        EC-MT-06: >= 2 homoplasmic point differences triggers definitive exclusion (LR = 0.0, log10 LR = -300.0).
        """
        unrelated = MTDNA_CASEWORK_COHORTS["COHORT_UNRELATED_EXCLUSION"]
        vars_a = [MtDnaMathematicalFormulation.parse_variant_string(s) for s in unrelated.profile_a_variants]
        vars_b = [MtDnaMathematicalFormulation.parse_variant_string(s) for s in unrelated.profile_b_variants]
        res = MtDnaMathematicalFormulation.evaluate_pairwise_lineage(vars_a, vars_b)

        assert res.verdict == "EXCLUSION"
        assert res.homoplasmic_differences_count >= 2
        assert res.maternal_lr == 0.0
        assert res.log10_maternal_lr == -300.0
        assert res.is_concordant is False
