"""
Unit Tests for Y-STR 27-Locus (Yfiler Plus) & RM Y-STR Lineage Biocomputational Engine
Standards Compliance: ISO/IEC 17025:2017, SWGDAM Lineage Guidelines (2020), ENFSI Evaluative Reporting (2017)
Research Source: research/ystr_27_mtdna_empop_lineage_research.md
"""

import pytest
from node.services.forensic.terminal.ystr_27_locus_engine import (
    YStr27LocusEngine,
    YSTR_27_MASTER_REGISTRY,
    YSTR_27_LOCI_ORDER,
    RM_YSTR_LOCI_SET,
    YStrMutationClass,
)


class TestYStr27LocusEngine:
    """Test suite for YStr27LocusEngine."""

    def test_27_loci_master_registry_integrity(self):
        """Verifies that all 27 Yfiler Plus loci across 25 multiplex systems are accurately cataloged."""
        assert len(YSTR_27_MASTER_REGISTRY) == 25
        assert len(YSTR_27_LOCI_ORDER) == 25

        # Verify physical locus count equals 27 (23 single-copy + 2x2 multi-copy)
        total_physical_loci = sum(2 if v.is_multi_copy else 1 for v in YSTR_27_MASTER_REGISTRY.values())
        assert total_physical_loci == 27

        # Exactly 7 RM Y-STRs (6 single-copy + 1 multi-copy DYF387S1a/b)
        rm_loci = [k for k, v in YSTR_27_MASTER_REGISTRY.items() if v.is_rapidly_mutating]
        assert len(rm_loci) == 6  # 5 single RM + 1 multi-copy RM = 6 entries in dictionary
        assert set(rm_loci) == RM_YSTR_LOCI_SET

        # Multi-copy loci
        multi_loci = [k for k, v in YSTR_27_MASTER_REGISTRY.items() if v.is_multi_copy]
        assert set(multi_loci) == {"DYS385a/b", "DYF387S1a/b"}

        # Check every locus has valid coordinates and mutation rates
        for locus_name, meta in YSTR_27_MASTER_REGISTRY.items():
            assert meta.grch38_start > 0
            assert meta.grch38_end > meta.grch38_start
            assert meta.amplicon_max_bp > meta.amplicon_min_bp
            assert meta.mutation_rate > 0.0
            assert 0.50 <= meta.stepwise_param_r <= 1.0

    def test_dys389_nested_repeat_decoupling(self):
        """
        Verifies mathematical decoupling of nested DYS389 repeats:
        DYS389.2_pure = DYS389II_total - DYS389I
        """
        dys389i, dys389_2_pure = YStr27LocusEngine.decouple_dys389(13.0, 29.0)
        assert dys389i == 13.0
        assert dys389_2_pure == 16.0

        dys389i_b, dys389_2_pure_b = YStr27LocusEngine.decouple_dys389(14.0, 31.0)
        assert dys389i_b == 14.0
        assert dys389_2_pure_b == 17.0

    def test_multi_copy_phr_evaluation(self):
        """
        Verifies Peak Height Ratio (PHR) calculations for DYS385a/b and DYF387S1a/b:
        PHR = min(RFU1, RFU2) / max(RFU1, RFU2) >= 0.50
        """
        # Balanced single-source profile
        phr_bal, is_bal, flag = YStr27LocusEngine.evaluate_multi_copy_phr(
            "DYS385a/b", [1800.0, 2000.0], threshold=0.50
        )
        assert is_bal is True
        assert pytest.approx(phr_bal, abs=1e-3) == 0.90
        assert flag is None

        # Imbalanced profile (< 0.50)
        phr_imbal, is_bal_imbal, flag_imbal = YStr27LocusEngine.evaluate_multi_copy_phr(
            "DYF387S1a/b", [600.0, 2400.0], threshold=0.50
        )
        assert is_bal_imbal is False
        assert pytest.approx(phr_imbal, abs=1e-3) == 0.25
        assert flag_imbal is not None
        assert "Imbalance warning" in flag_imbal

    def test_clopper_pearson_95_upper_bounds(self):
        """
        Verifies exact Clopper-Pearson 95% Binomial Upper Bounds:
        k=0, N=35,000 -> 8.56e-5 (1 in 11,682)
        k=1, N=35,000 -> 1.59e-4 (1 in 6,281)
        k=5, N=35,000 -> 3.33e-4 (1 in 2,999)
        """
        p_upper_k0 = YStr27LocusEngine.calculate_clopper_pearson_95_upper(0, 35000)
        assert pytest.approx(p_upper_k0, rel=1e-2) == 8.56e-5
        assert pytest.approx(1.0 / p_upper_k0, abs=50) == 11682

        p_upper_k1 = YStr27LocusEngine.calculate_clopper_pearson_95_upper(1, 35000)
        assert pytest.approx(p_upper_k1, rel=1e-2) == 1.59e-4
        assert pytest.approx(1.0 / p_upper_k1, abs=50) == 6281

        p_upper_k5 = YStr27LocusEngine.calculate_clopper_pearson_95_upper(5, 35000)
        assert pytest.approx(p_upper_k5, rel=1e-2) == 3.33e-4

    def test_brenner_subpopulation_correction(self):
        """
        Verifies Brenner theta-correction:
        p_Brenner = (k + theta) / (N + theta)
        """
        p_bren_k0 = YStr27LocusEngine.calculate_brenner_frequency(0, 35000, theta=0.02)
        assert pytest.approx(p_bren_k0, rel=1e-3) == 0.02 / 35000.02

        p_bren_k1 = YStr27LocusEngine.calculate_brenner_frequency(1, 35000, theta=0.02)
        assert pytest.approx(p_bren_k1, rel=1e-3) == 1.02 / 35000.02

    def test_bayesian_y_dna_haplogroup_prediction(self):
        """Verifies Bayesian Y-DNA haplogroup prediction across major continental lineages."""
        # European R1b Profile
        r1b_profile = {
            "DYS393": 13, "DYS390": 24, "DYS19": 14, "DYS391": 11,
            "DYS385a/b": [11, 14], "DYS438": 12, "DYS439": 12, "DYS437": 15,
            "DYS481": 22, "DYS533": 12, "DYS458": 17, "DYS456": 15,
            "DYS635": 23, "YGATAH4": 12, "DYS389I": 13, "DYS389II": 29,
            "DYS448": 19, "DYS570": 17, "DYS576": 18, "DYS627": 15,
        }
        pred_r1b = YStr27LocusEngine.predict_y_dna_haplogroup(r1b_profile)
        assert pred_r1b.predicted_haplogroup == "R1b-M269"
        assert pred_r1b.confidence_score > 0.80
        assert "M269" in pred_r1b.primary_snp_marker

        # African American E1b1a Profile
        e1b1a_profile = {
            "DYS393": 15, "DYS390": 21, "DYS19": 15, "DYS391": 10,
            "DYS385a/b": [15, 16], "DYS439": 11, "DYS438": 10, "DYS437": 16,
            "DYS481": 25, "DYS389I": 14, "DYS389II": 31, "DYS570": 19,
        }
        pred_e1b1a = YStr27LocusEngine.predict_y_dna_haplogroup(e1b1a_profile)
        assert pred_e1b1a.predicted_haplogroup == "E1b1a-V38"
        assert pred_e1b1a.confidence_score > 0.75

        # Native American / Hispanic Q-M3 Profile
        q_profile = {
            "DYS393": 13, "DYS390": 24, "DYS19": 13, "DYS391": 10,
            "DYS385a/b": [12, 13], "DYS438": 10, "DYS437": 14, "DYS439": 12,
            "DYS389I": 13, "DYS389II": 30, "DYS570": 16, "DYS458": 17.2,
            "DYS627": 20.2, "DYS518": 36, "DYS449": 28,
        }
        pred_q = YStr27LocusEngine.predict_y_dna_haplogroup(q_profile)
        assert pred_q.predicted_haplogroup == "Q-M3"
        assert pred_q.confidence_score > 0.70

    def test_smm_kinship_father_son_single_step_mutation(self):
        """
        Verifies Benchmark PEDIGREE-01:
        Father and son with 26 matching loci and a 1-step repeat mutation at DYS570 (Father 17, Son 18).
        Expected Combined Kinship Index (CPI) ~ 61.97.
        """
        father_profile = {
            "DYS19": 14, "DYS389I": 13, "DYS389II": 29, "DYS390": 24, "DYS391": 11,
            "DYS392": 13, "DYS393": 13, "DYS385a/b": [11, 14], "DYS437": 15, "DYS438": 12,
            "DYS439": 12, "DYS448": 19, "DYS456": 15, "DYS458": 17, "DYS635": 23,
            "YGATAH4": 12, "DYS460": 11, "DYS481": 22, "DYS533": 12, "DYS570": 17,
            "DYS576": 18, "DYS627": 15, "DYS518": 38, "DYS449": 30, "DYF387S1a/b": [35, 37],
        }

        son_profile = dict(father_profile)
        son_profile["DYS570"] = 18  # 1-step mutation at RM locus

        kinship_res = YStr27LocusEngine.calculate_smm_kinship_index(
            profile_a=father_profile,
            profile_b=son_profile,
            meioses=1,
            database_size=35000,
        )

        assert kinship_res["compared_loci_count"] == 25
        assert kinship_res["mutation_count"] == 1
        assert kinship_res["mutated_loci"][0]["locus"] == "DYS570"
        assert kinship_res["mutated_loci"][0]["steps"] == 1
        assert kinship_res["mutated_loci"][0]["is_rapidly_mutating"] is True

        # CPI = P(Son | Father) / P(Son_unrelated) ~ 0.005305 / 8.56e-5 = 61.97
        assert pytest.approx(kinship_res["combined_kinship_index"], abs=5.0) == 61.97
        assert kinship_res["is_kinship_supported"] is True

    def test_male_mixture_deconvolution(self):
        """Verifies N_male mixture deconvolution algorithm."""
        # Single source
        single_source = {
            "DYS19": ["14"],
            "DYS389I": ["13"],
            "DYS385a/b": ["11", "14"],
            "DYF387S1a/b": ["35", "37"],
        }
        res_single = YStr27LocusEngine.deconvolute_male_mixture(single_source)
        assert res_single["n_male_min"] == 1
        assert res_single["is_mixture"] is False

        # 3-Contributor male mixture (5 alleles at DYF387S1a/b -> ceil(5/2) = 3)
        mixture_3m = {
            "DYS19": ["14", "15", "16"],  # 3 alleles
            "DYS389I": ["12", "13", "14"],  # 3 alleles
            "DYF387S1a/b": ["34", "35", "36", "37", "38"],  # 5 alleles
        }
        res_mix = YStr27LocusEngine.deconvolute_male_mixture(mixture_3m)
        assert res_mix["n_male_min"] == 3
        assert res_mix["is_mixture"] is True
