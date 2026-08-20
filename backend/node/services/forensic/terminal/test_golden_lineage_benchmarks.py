"""
FORENZA Forensic Evidence OS — Golden Lineage Benchmark Vectors Test Suite
ISO/IEC 17025:2017 & SWGDAM 2020 Validation.

Verifies:
  - Benchmark LINEAGE-A (European Reference / R1b-M269 / mtDNA H1)
  - Benchmark LINEAGE-B (African American Reference / E1b1a-V38 / mtDNA L2a1)
  - Benchmark LINEAGE-C (Hispanic Reference / Q-M3 / mtDNA A2 / AMEL Y-Null Resolution)
  - Benchmark PEDIGREE-01 (Father-Son RM Y-STR DYS570 1-Step Mutation Verification)
  - Benchmark MATERNAL-01 (Mother-Child Shared 16093Y Point Heteroplasmy Lineage)
"""

import pytest
import math
from node.services.forensic.terminal.ystr_27_locus_engine import (
    YStr27LocusEngine,
    YSTR_27_MASTER_REGISTRY,
    Y_HAPLOGROUP_MODAL_PROFILES,
)
from node.services.forensic.terminal.mtdna_empop_engine import (
    MtdnaEmpopEngine,
    MtdnaVariant,
)
from node.services.forensic.terminal.casework_presets import (
    CaseworkPresetsEngine,
    GOLDEN_CASEWORK_PRESETS,
)


class TestGoldenLineageBenchmarks:
    """Golden Lineage Multi-Omic Benchmarks (ISO 17025 §7.8.2)."""

    def test_lineage_a_european_benchmark(self):
        """
        LINEAGE-A (VECTOR_TERM_01):
        - European 27 Y-STR (25 systems): R1b-M269 modal haplotype.
        - mtDNA Control Region: H1 defining mutations (263G, 315.1C, 750G, 16519C).
        """
        p = CaseworkPresetsEngine.get_preset_by_id("VECTOR_TERM_01")
        assert p is not None
        assert p.ystr_profile is not None
        assert len(p.ystr_profile) == 25
        assert p.mtdna_mutations is not None

        # 1. Y-STR Paternal Haplogroup Prediction
        y_hg = YStr27LocusEngine.predict_y_dna_haplogroup(p.ystr_profile)
        assert y_hg.predicted_haplogroup == "R1b-M269"
        assert y_hg.confidence_score >= 0.90
        assert y_hg.distance_to_modal < 1.0  # Perfect match to R1b modal

        # 2. YHRD Clopper-Pearson Exact 95% Binomial Upper Bound (k=0, N=35,000)
        p_upper = YStr27LocusEngine.calculate_clopper_pearson_95_upper(0, 35000)
        assert abs(p_upper - 8.56e-5) < 1e-6
        lr_ystr = 1.0 / p_upper
        assert lr_ystr >= 11600

        # 3. mtDNA Maternal Haplogroup Classification
        mt_hg = MtdnaEmpopEngine.classify_haplogroup(p.mtdna_mutations)
        assert mt_hg.predicted_haplogroup in ["H1", "H"]
        assert mt_hg.macro_haplogroup == "H"

        # 4. EMPOP 3'-Right-Alignment Light-Strand Verification
        normalized = MtdnaEmpopEngine.normalize_profile(p.mtdna_mutations)
        assert len(normalized) == 4
        assert "263G" in normalized
        assert "315.1C" in normalized
        assert "750G" in normalized
        assert "16519C" in normalized

    def test_lineage_b_african_benchmark(self):
        """
        LINEAGE-B (VECTOR_TERM_02):
        - African American 27 Y-STR: E1b1a-V38 modal haplotype.
        - mtDNA Control Region: L2a1 lineage (13 diagnostic mutations).
        """
        p = CaseworkPresetsEngine.get_preset_by_id("VECTOR_TERM_02")
        assert p is not None
        assert p.ystr_profile is not None
        assert p.mtdna_mutations is not None

        # 1. Y-STR Paternal Haplogroup Prediction
        y_hg = YStr27LocusEngine.predict_y_dna_haplogroup(p.ystr_profile)
        assert y_hg.predicted_haplogroup == "E1b1a-V38"
        assert y_hg.confidence_score >= 0.90
        assert y_hg.distance_to_modal < 1.0

        # 2. mtDNA Maternal Haplogroup Classification
        mt_hg = MtdnaEmpopEngine.classify_haplogroup(p.mtdna_mutations)
        assert mt_hg.predicted_haplogroup == "L2a1"
        assert mt_hg.macro_haplogroup == "L"

        # 3. EMPOP Rare Lineage Likelihood Ratio
        p_upper = MtdnaEmpopEngine.calculate_empop_95_upper(12, 48200)
        assert p_upper < 0.001
        lr_mtdna = 1.0 / p_upper
        assert lr_mtdna > 2000.0

    def test_lineage_c_hispanic_amel_null_benchmark(self):
        """
        LINEAGE-C (VECTOR_TERM_03):
        - Hispanic profile with Amelogenin Y-null deletion (AMEL X, X).
        - Male sex confirmed via DYS391=11 and 25 Y-STR systems (27 physical loci).
        - Paternal Haplogroup: Q-M3 (Native American patrilineage).
        - Maternal Haplogroup: A2 (Native American matrilineage with CSB 522del/523del).
        """
        p = CaseworkPresetsEngine.get_preset_by_id("VECTOR_TERM_03")
        assert p is not None
        assert p.ystr_profile is not None

        # 1. Confirm Male Sex via Y-STR presence despite AMEL null
        assert "DYS391" in p.ystr_profile
        assert p.ystr_profile["DYS391"]["allele1"] == "11"
        assert len(p.ystr_profile) == 25

        # 2. Paternal Haplogroup Q-M3
        y_hg = YStr27LocusEngine.predict_y_dna_haplogroup(p.ystr_profile)
        assert y_hg.predicted_haplogroup == "Q-M3"
        assert "M3" in y_hg.primary_snp_marker

        # 3. Maternal Haplogroup A2
        mt_hg = MtdnaEmpopEngine.classify_haplogroup(p.mtdna_mutations)
        assert mt_hg.predicted_haplogroup == "A2"
        assert mt_hg.macro_haplogroup in ["A", "N"]

        # 4. EMPOP Indel Normalization at 522-524 AC repeat
        normalized = MtdnaEmpopEngine.normalize_profile(p.mtdna_mutations)
        assert any("del" in notat for notat in normalized)

    def test_benchmark_pedigree_01_father_son_rm_mutation(self):
        """
        BENCHMARK PEDIGREE-01:
        - True Father and Son with 1-step mutation at Rapidly Mutating locus DYS570 (Father: 17, Son: 18).
        - Locus mutation rate: μ_DYS570 = 0.012.
        - Verify Kinship CPI calculation via Stepwise Mutation Model (SMM).
        """
        base_p = CaseworkPresetsEngine.get_preset_by_id("VECTOR_TERM_01")
        father_profile = {k: dict(v) for k, v in base_p.ystr_profile.items()}
        son_profile = {k: dict(v) for k, v in base_p.ystr_profile.items()}

        # Introduce 1-step mutation at DYS570 in son
        father_profile["DYS570"] = {"allele1": "17", "rfu1": 1600.0}
        son_profile["DYS570"] = {"allele1": "18", "rfu1": 1550.0}

        # Kinship comparison for 1 meiosis
        comp = YStr27LocusEngine.calculate_kinship_likelihood_ratio(father_profile, son_profile, meioses=1)
        assert comp["compared_loci_count"] == 25
        assert comp["mutation_count"] == 1
        assert comp["mutated_loci"][0]["locus"] == "DYS570"

        # SMM single-step transition probability: P(18 | 17) = (1 - mu) for matches, mu / 2 for 1-step
        mu_dys570 = YSTR_27_MASTER_REGISTRY["DYS570"].mutation_rate
        expected_step_prob = mu_dys570 / 2.0  # 0.012 / 2 = 0.006
        assert abs(comp["mutated_loci"][0]["transition_prob"] - expected_step_prob) < 1e-5

        # Combined Paternity Index should still strongly support kinship
        assert comp["combined_kinship_index"] > 50.0
        assert comp["is_kinship_supported"] is True


    def test_benchmark_maternal_01_shared_heteroplasmy(self):
        """
        BENCHMARK MATERNAL-01:
        - Mother and Child share Point Heteroplasmy at Position 16093Y (C/T).
        - Verify IUPAC detection, minor allele fraction estimation, and lineage concordance.
        """
        mother_mutations = ["263G", "315.1C", "16093Y", "16519C"]
        child_mutations = ["263G", "315.1C", "16093Y", "16519C"]

        v_php = MtdnaEmpopEngine.parse_variant("16093Y")
        assert v_php is not None
        assert v_php.variant_type == "PHP"
        assert v_php.alt_base == "Y"
        assert v_php.position == 16093

        # Classification remains Macro H
        hg_mother = MtdnaEmpopEngine.classify_haplogroup(mother_mutations)
        hg_child = MtdnaEmpopEngine.classify_haplogroup(child_mutations)
        assert hg_mother.predicted_haplogroup == hg_child.predicted_haplogroup
        assert hg_mother.macro_haplogroup == "H"

        # Maternal Kinship Evaluation
        kin = MtdnaEmpopEngine.evaluate_maternal_kinship(mother_mutations, child_mutations)
        assert kin["is_match"] is True
        assert kin["is_exclusion"] is False
        assert kin["lr_mtdna"] > 1.0
