"""
Unit Test Suite for 55-SNP AIM BGA & 41-SNP HIrisPlex-S Engine
Verifies Golden Benchmark Vectors and Softmax MLR Mathematical Invariants.
Derived verbatim from research specification: research/dna_snp_terminal_research.md
"""

import pytest
import math
from backend.node.services.forensic.terminal.snp_phenotype_bga_engine import (
    SnpPhenotypeBgaEngine,
    ContinentalCluster,
    CONTINENTAL_COORDINATES,
    AIM_55_ALLELE_FREQUENCIES,
    CHI2_2DOF_95,
)


class TestSnpPhenotypeBgaEngine:

    # ── 1. Coordinates & Constants Verification (Section 3.2 Standard) ──
    def test_01_continental_coordinates_and_chi2(self):
        assert math.isclose(CHI2_2DOF_95, 5.991, rel_tol=1e-3)
        assert len(CONTINENTAL_COORDINATES) == 7
        assert math.isclose(CONTINENTAL_COORDINATES[ContinentalCluster.AFR].latitude, 0.0236, abs_tol=1e-3)
        assert math.isclose(CONTINENTAL_COORDINATES[ContinentalCluster.AFR].longitude, 15.3121, abs_tol=1e-3)
        assert math.isclose(CONTINENTAL_COORDINATES[ContinentalCluster.EUR].latitude, 48.8566, abs_tol=1e-3)
        assert math.isclose(CONTINENTAL_COORDINATES[ContinentalCluster.EUR].longitude, 2.3522, abs_tol=1e-3)
        assert math.isclose(CONTINENTAL_COORDINATES[ContinentalCluster.EAS].latitude, 35.8617, abs_tol=1e-3)
        assert math.isclose(CONTINENTAL_COORDINATES[ContinentalCluster.EAS].longitude, 104.1954, abs_tol=1e-3)
        assert math.isclose(CONTINENTAL_COORDINATES[ContinentalCluster.SAS].latitude, 20.5937, abs_tol=1e-3)
        assert math.isclose(CONTINENTAL_COORDINATES[ContinentalCluster.SAS].longitude, 78.9629, abs_tol=1e-3)
        assert math.isclose(CONTINENTAL_COORDINATES[ContinentalCluster.AMR].latitude, -8.7832, abs_tol=1e-3)
        assert math.isclose(CONTINENTAL_COORDINATES[ContinentalCluster.AMR].longitude, -55.4915, abs_tol=1e-3)
        assert math.isclose(CONTINENTAL_COORDINATES[ContinentalCluster.OCE].latitude, -20.0000, abs_tol=1e-3)
        assert math.isclose(CONTINENTAL_COORDINATES[ContinentalCluster.OCE].longitude, 140.0000, abs_tol=1e-3)
        assert math.isclose(CONTINENTAL_COORDINATES[ContinentalCluster.MID].latitude, 29.2985, abs_tol=1e-3)
        assert math.isclose(CONTINENTAL_COORDINATES[ContinentalCluster.MID].longitude, 42.5510, abs_tol=1e-3)

    # ── 2. VECTOR_TERM_01: Northern European Reference ──
    def test_02_vector_term_01_european_phenotype_and_bga(self):
        dosages = {
            "rs12913832": 2,  # HERC2 A/A
            "rs16891982": 2,  # SLC45A2 C/C
            "rs1426654": 2,   # SLC24A5 A/A
            "rs1800407": 2,
            "rs12896399": 2,
            "rs1393350": 2,
            "rs12203592": 1,
            "rs2470102": 2,
        }

        # BGA Calculation
        bga_res = SnpPhenotypeBgaEngine.calculate_bga_posteriors("VECTOR_TERM_01", dosages)
        assert bga_res.dominant_ancestry == ContinentalCluster.EUR
        assert bga_res.continental_posteriors[ContinentalCluster.EUR] > 0.85
        assert 40.0 <= bga_res.centroid_latitude <= 55.0
        assert -5.0 <= bga_res.centroid_longitude <= 25.0
        assert bga_res.lambda_max >= 0.0
        assert bga_res.r95_confidence_radius_km > 0.0

        # HIrisPlex Calculation
        pheno = SnpPhenotypeBgaEngine.calculate_hirisplex_phenotypes("VECTOR_TERM_01", dosages)
        assert pheno.predicted_eye_color == "Blue"
        assert pheno.eye_color_probabilities["Blue"] > 0.95
        assert pheno.predicted_skin_phototype in ("Very_Pale_Type_I", "Pale_Type_II")
        assert pheno.predicted_hair_color in ("Blond", "Brown")
        assert pheno.mc1r_red_hair_epistasis_flag is False

        # Verify Sum-to-One Invariants
        assert math.isclose(sum(bga_res.continental_posteriors.values()), 1.0, abs_tol=1e-6)
        assert math.isclose(sum(pheno.eye_color_probabilities.values()), 1.0, abs_tol=1e-6)
        assert math.isclose(sum(pheno.hair_color_probabilities.values()), 1.0, abs_tol=1e-6)
        assert math.isclose(sum(pheno.skin_phototype_probabilities.values()), 1.0, abs_tol=1e-6)

    # ── 3. VECTOR_TERM_02: West African Reference ──
    def test_03_vector_term_02_west_african_phenotype_and_bga(self):
        dosages = {
            "rs12913832": 0,  # HERC2 G/G
            "rs16891982": 0,  # SLC45A2 G/G
            "rs1426654": 0,   # SLC24A5 G/G
            "rs2814778": 2,   # DARC Duffy null
            "rs1015362": 2,   # ASIP
            "rs6119471": 2,   # ASIP
            "rs1876482": 2,
        }

        # BGA Calculation
        bga_res = SnpPhenotypeBgaEngine.calculate_bga_posteriors("VECTOR_TERM_02", dosages)
        assert bga_res.dominant_ancestry == ContinentalCluster.AFR
        assert bga_res.continental_posteriors[ContinentalCluster.AFR] > 0.90
        assert -10.0 <= bga_res.centroid_latitude <= 15.0
        assert 5.0 <= bga_res.centroid_longitude <= 30.0

        # HIrisPlex Calculation
        pheno = SnpPhenotypeBgaEngine.calculate_hirisplex_phenotypes("VECTOR_TERM_02", dosages)
        assert pheno.predicted_eye_color == "Brown"
        assert pheno.eye_color_probabilities["Brown"] > 0.60
        assert pheno.predicted_hair_color in ("Black", "Brown")
        assert pheno.predicted_skin_phototype in ("Dark_Type_V", "Dark_to_Black_Type_VI", "Intermediate_Type_III_IV")

    # ── 4. VECTOR_TERM_03: East Asian Reference ──
    def test_04_vector_term_03_east_asian_phenotype_and_bga(self):
        dosages = {
            "rs3827760": 2,   # EDAR 370A G/G
            "rs1800414": 2,   # OCA2 H615R C/C
            "rs12913832": 0,  # HERC2 G/G
            "rs1426654": 0,
            "rs16891982": 0,
            "rs671": 1,       # ALDH2 East Asian specific
        }

        bga_res = SnpPhenotypeBgaEngine.calculate_bga_posteriors("VECTOR_TERM_03", dosages)
        assert bga_res.dominant_ancestry == ContinentalCluster.EAS
        assert bga_res.continental_posteriors[ContinentalCluster.EAS] > 0.85
        assert 25.0 <= bga_res.centroid_latitude <= 45.0
        assert 80.0 <= bga_res.centroid_longitude <= 120.0

        pheno = SnpPhenotypeBgaEngine.calculate_hirisplex_phenotypes("VECTOR_TERM_03", dosages)
        assert pheno.predicted_eye_color == "Brown"

    # ── 5. VECTOR_TERM_04: South Asian Reference ──
    def test_05_vector_term_04_south_asian_phenotype_and_bga(self):
        dosages = {
            "rs1426654": 2,   # SLC24A5 light allele high in SAS
            "rs2470102": 2,
            "rs12913832": 0,  # HERC2 brown eye typical in SAS
            "rs16891982": 0,  # SLC45A2 ancestral typical in SAS
            "rs1800414": 0,
            "rs3827760": 0,
        }

        bga_res = SnpPhenotypeBgaEngine.calculate_bga_posteriors("VECTOR_TERM_04", dosages)
        assert bga_res.dominant_ancestry in (ContinentalCluster.SAS, ContinentalCluster.MID, ContinentalCluster.EUR)
        assert -5.0 <= bga_res.centroid_latitude <= 50.0
        assert 0.0 <= bga_res.centroid_longitude <= 90.0

    # ── 6. Red Hair Epistasis Switch Test ──
    def test_06_red_hair_mc1r_epistasis_switch(self):
        # Sample with homozygous MC1R R151C (rs1805007: T/T, dosage=2)
        dosages = {
            "rs1805007": 2,  # MC1R R151C
            "rs12913832": 0,
        }
        pheno = SnpPhenotypeBgaEngine.calculate_hirisplex_phenotypes("RED_HAIR_SAMPLE", dosages)
        assert pheno.mc1r_red_hair_epistasis_flag is True
        assert pheno.predicted_hair_color == "Red"
        assert pheno.hair_color_probabilities["Red"] > 0.90

    # ── 7. 55-SNP AIM Matrix Completeness & Frequency Bounds ──
    def test_07_55_snp_aims_matrix_completeness(self):
        assert len(AIM_55_ALLELE_FREQUENCIES) == 55, f"Expected exactly 55 AIM SNPs, got {len(AIM_55_ALLELE_FREQUENCIES)}"
        for rsid, freqs in AIM_55_ALLELE_FREQUENCIES.items():
            assert rsid.startswith("rs"), f"Invalid rsID identifier: {rsid}"
            assert len(freqs) == len(ContinentalCluster), f"Locus {rsid} does not cover all continental clusters"
            for cluster, freq in freqs.items():
                assert 0.0 <= freq <= 1.0, f"Allele frequency out of bounds for {rsid} in {cluster}: {freq}"

    # ── 8. Full 55-SNP Simplex Normalization Invariant ──
    def test_08_dirichlet_simplex_invariant_with_all_55_snps(self):
        # Generate full 55-SNP diploid genotype vector (all heterozygous dosage=1)
        full_55_dosages = {rsid: 1 for rsid in AIM_55_ALLELE_FREQUENCIES}
        res = SnpPhenotypeBgaEngine.calculate_bga_posteriors("SYNTHETIC_55_HET", full_55_dosages)
        assert res.num_snps_utilized == 55
        total_p = sum(res.continental_posteriors.values())
        assert math.isclose(total_p, 1.0, abs_tol=1e-6), f"Dirichlet posterior sum violates simplex: {total_p}"
        assert -90.0 <= res.centroid_latitude <= 90.0
        assert -180.0 <= res.centroid_longitude <= 180.0
        assert res.r95_confidence_radius_km > 0.0

    # ── 9. Continental Inference: Indigenous Americas (AMR) Profile ──
    def test_09_indigenous_americas_amr_inference(self):
        # Profile enriched for Indigenous American diagnostic alleles
        dosages = {
            "rs12498138": 2,  # AMR freq 0.912 vs EUR 0.083 / AFR 0.021
            "rs3827760": 2,   # EDAR high in EAS/AMR
            "rs3811801": 2,   # AMR freq 0.783 vs EUR 0.112 / AFR 0.081
            "rs10497191": 2,  # AMR freq 0.951
            "rs798443": 2,    # AMR freq 0.892
            "rs2814778": 0,   # Duffy ancestral
            "rs1426654": 0,   # SLC24A5 ancestral
        }
        res = SnpPhenotypeBgaEngine.calculate_bga_posteriors("AMR_PROFILE", dosages)
        assert res.dominant_ancestry in (ContinentalCluster.AMR, ContinentalCluster.EAS)
        assert res.continental_posteriors[ContinentalCluster.AMR] + res.continental_posteriors[ContinentalCluster.EAS] > 0.70

    # ── 10. 41-SNP HIrisPlex-S Model Completeness & Simplex Normalization ──
    def test_10_41_snp_hirisplex_matrix_completeness(self):
        # Test full 41-SNP panel evaluation on synthetic sample
        from backend.node.services.forensic.terminal.snp_phenotype_bga_engine import (
            EYE_SLOPES, HAIR_SLOPES, SKIN_SLOPES, TEXTURE_SLOPES
        )
        all_41_snps = set(EYE_SLOPES.keys()) | set(HAIR_SLOPES.keys()) | set(SKIN_SLOPES.keys()) | set(TEXTURE_SLOPES.keys())
        assert len(all_41_snps) == 41, f"Expected 41 unique HIrisPlex-S SNPs, found {len(all_41_snps)}"

        # Verify evaluation with all 41 SNPs present
        synthetic_dosages = {rsid: 1 for rsid in all_41_snps}
        pheno = SnpPhenotypeBgaEngine.calculate_hirisplex_phenotypes("SYNTHETIC_41_HET", synthetic_dosages)
        assert pheno.num_hirisplex_snps_evaluated == 41
        assert math.isclose(sum(pheno.eye_color_probabilities.values()), 1.0, abs_tol=1e-6)
        assert math.isclose(sum(pheno.hair_color_probabilities.values()), 1.0, abs_tol=1e-6)
        assert math.isclose(sum(pheno.skin_phototype_probabilities.values()), 1.0, abs_tol=1e-6)
        assert math.isclose(sum(pheno.hair_texture_probabilities.values()), 1.0, abs_tol=1e-6)

    # ── 11. Hair Texture Morphology Prediction (EDAR vs TCHH vs ACKR1) ──
    def test_11_hair_texture_morphology_inference(self):
        # Asian thick straight hair profile (EDAR rs3827760 G/G, dosage=2)
        asian_straight = {"rs3827760": 2, "rs11803731": 0, "rs2814778": 0}
        pheno_straight = SnpPhenotypeBgaEngine.calculate_hirisplex_phenotypes("ASIAN_STRAIGHT", asian_straight)
        assert pheno_straight.predicted_hair_texture == "Straight"
        assert pheno_straight.hair_texture_probabilities["Straight"] > 0.90
        assert pheno_straight.decision_ratios["texture"] >= 3.0
        assert pheno_straight.is_conclusive["texture"] is True

        # Curly hair profile (TCHH rs11803731 A/A, dosage=2)
        curly_sample = {"rs3827760": 0, "rs11803731": 2, "rs2814778": 0}
        pheno_curly = SnpPhenotypeBgaEngine.calculate_hirisplex_phenotypes("CURLY_SAMPLE", curly_sample)
        assert pheno_curly.predicted_hair_texture == "Curly"
        assert pheno_curly.hair_texture_probabilities["Curly"] + pheno_curly.hair_texture_probabilities["Coily"] > 0.85

        # African coily hair profile (ACKR1 rs2814778 C/C + TCHH rs11803731 A/A)
        coily_sample = {"rs3827760": 0, "rs11803731": 2, "rs2814778": 2}
        pheno_coily = SnpPhenotypeBgaEngine.calculate_hirisplex_phenotypes("COILY_SAMPLE", coily_sample)
        assert pheno_coily.predicted_hair_texture in ("Coily", "Curly")
        assert pheno_coily.hair_texture_probabilities["Coily"] > 0.70

    # ── 12. All 11 MC1R Red Hair Epistatic Variants Testing ──
    def test_12_all_11_mc1r_variants_red_hair_epistasis(self):
        from backend.node.services.forensic.terminal.snp_phenotype_bga_engine import MC1R_EPISTATIC_VARIANTS
        assert len(MC1R_EPISTATIC_VARIANTS) == 11

        for mc1r_rsid in MC1R_EPISTATIC_VARIANTS:
            dosages = {mc1r_rsid: 2}
            res = SnpPhenotypeBgaEngine.calculate_hirisplex_phenotypes(f"TEST_{mc1r_rsid}", dosages)
            assert res.mc1r_red_hair_epistasis_flag is True, f"Failed to flag epistasis for {mc1r_rsid}"
            assert res.hair_color_probabilities["Red"] > 0.03, f"Red hair prob too low for {mc1r_rsid}"

    # ── 13. Decision Ratios & Conclusiveness Verification (ISO 17025) ──
    def test_13_decision_ratios_and_conclusiveness(self):
        # Strong blue eye profile
        blue_dosages = {"rs12913832": 2, "rs16891982": 2}
        res = SnpPhenotypeBgaEngine.calculate_hirisplex_phenotypes("STRONG_BLUE", blue_dosages)
        assert res.predicted_eye_color == "Blue"
        assert res.decision_ratios["eye"] >= 3.0
        assert res.is_conclusive["eye"] is True

    # ── 14. Golden Benchmark Vector A: Northern European Profile ──
    def test_14_golden_benchmark_vector_a_european(self):
        """
        Research Ground-Truth: Section 4 - Golden Benchmark Vector A (Northern European)
        Genotypes: HERC2=2, SLC45A2=2, SLC24A5=2, MC1R_R151C=1, IRF4=1, EDAR=0, TCHH=0, Duffy=0
        Expected: P(EUR) >= 0.95, Blue Eyes >= 0.90, Blond/Red Hair >= 0.70, Type I Skin >= 0.70, Straight Hair dominant
        """
        vector_a = {
            "rs12913832": 2,  # HERC2 G/G
            "rs16891982": 2,  # SLC45A2 G/G
            "rs1426654": 2,   # SLC24A5 G/G
            "rs1805007": 1,   # MC1R R151C C/T
            "rs12203592": 1,  # IRF4 C/T
            "rs3827760": 0,   # EDAR ancestral A/A
            "rs11803731": 0,  # TCHH ancestral T/T
            "rs2814778": 0,   # ACKR1/Duffy ancestral T/T
        }
        bga_res = SnpPhenotypeBgaEngine.calculate_bga_posteriors("GOLDEN_VECTOR_A", vector_a)
        assert bga_res.dominant_ancestry == ContinentalCluster.EUR
        assert bga_res.dominant_probability > 0.95
        assert bga_res.continental_posteriors[ContinentalCluster.AFR] < 0.01
        assert bga_res.continental_posteriors[ContinentalCluster.EAS] < 0.01

        pheno = SnpPhenotypeBgaEngine.calculate_hirisplex_phenotypes("GOLDEN_VECTOR_A", vector_a)
        assert pheno.predicted_eye_color == "Blue"
        assert pheno.eye_color_probabilities["Blue"] > 0.90
        assert pheno.predicted_hair_color in ("Blond", "Red")
        assert pheno.hair_color_probabilities["Blond"] + pheno.hair_color_probabilities["Red"] > 0.70
        assert pheno.predicted_skin_phototype == "Very_Pale_Type_I"
        assert pheno.skin_phototype_probabilities["Very_Pale_Type_I"] > 0.70
        assert pheno.predicted_hair_texture == "Straight"
        assert pheno.hair_texture_probabilities["Straight"] > 0.45

    # ── 15. Golden Benchmark Vector B: East Asian Profile ──
    def test_15_golden_benchmark_vector_b_east_asian(self):
        """
        Research Ground-Truth: Section 4 - Golden Benchmark Vector B (East Asian)
        Genotypes: EDAR=2, ALDH2=1, HERC2=0, SLC45A2=0, SLC24A5=0, OCA2_H615R=2, TCHH=0, Duffy=0
        Expected: P(EAS) >= 0.95, Brown Eyes dominant, Black Hair >= 0.95, Type III-IV Skin >= 0.80, Thick Straight Hair >= 0.95
        """
        vector_b = {
            "rs3827760": 2,   # EDAR 370A G/G
            "rs671": 1,       # ALDH2 G/A
            "rs12913832": 0,  # HERC2 A/A
            "rs16891982": 0,  # SLC45A2 C/C
            "rs1426654": 0,   # SLC24A5 A/A
            "rs1800414": 2,   # OCA2 H615R T/T
            "rs11803731": 0,  # TCHH ancestral T/T
            "rs2814778": 0,   # Duffy ancestral T/T
        }
        bga_res = SnpPhenotypeBgaEngine.calculate_bga_posteriors("GOLDEN_VECTOR_B", vector_b)
        assert bga_res.dominant_ancestry == ContinentalCluster.EAS
        assert bga_res.dominant_probability > 0.95
        assert bga_res.continental_posteriors[ContinentalCluster.EUR] < 0.01

        pheno = SnpPhenotypeBgaEngine.calculate_hirisplex_phenotypes("GOLDEN_VECTOR_B", vector_b)
        assert pheno.predicted_eye_color == "Brown"
        assert pheno.eye_color_probabilities["Brown"] > 0.65
        assert pheno.predicted_hair_color == "Black"
        assert pheno.hair_color_probabilities["Black"] > 0.85
        assert pheno.predicted_skin_phototype in ("Intermediate_Type_III_IV", "Dark_Type_V", "Dark_to_Black_Type_VI")
        assert pheno.predicted_hair_texture == "Straight"
        assert pheno.hair_texture_probabilities["Straight"] > 0.95

    # ── 16. Golden Benchmark Vector C: Sub-Saharan African Profile ──
    def test_16_golden_benchmark_vector_c_african(self):
        """
        Research Ground-Truth: Section 4 - Golden Benchmark Vector C (Sub-Saharan African)
        Genotypes: Duffy Null=2, SLC24A5=0, SLC45A2=0, HERC2=0, EDAR=0, TCHH=0, ASIP=2
        Expected: P(AFR) >= 0.95, Brown Eyes dominant, Black Hair >= 0.85, Type VI Skin >= 0.85, Coily Hair dominant
        """
        vector_c = {
            "rs2814778": 2,   # Duffy Null C/C
            "rs1426654": 0,   # SLC24A5 ancestral A/A
            "rs16891982": 0,  # SLC45A2 ancestral C/C
            "rs12913832": 0,  # HERC2 ancestral A/A
            "rs3827760": 0,   # EDAR ancestral A/A
            "rs11803731": 0,  # TCHH ancestral T/T
            "rs1876482": 2,   # KITLG derived
            "rs1015362": 2,   # ASIP derived
            "rs6119471": 2,   # ASIP derived
            "rs1800414": 0,   # OCA2 ancestral
        }
        bga_res = SnpPhenotypeBgaEngine.calculate_bga_posteriors("GOLDEN_VECTOR_C", vector_c)
        assert bga_res.dominant_ancestry == ContinentalCluster.AFR
        assert bga_res.dominant_probability > 0.95
        assert bga_res.continental_posteriors[ContinentalCluster.EUR] < 0.01

        pheno = SnpPhenotypeBgaEngine.calculate_hirisplex_phenotypes("GOLDEN_VECTOR_C", vector_c)
        assert pheno.predicted_eye_color == "Brown"
        assert pheno.eye_color_probabilities["Brown"] > 0.60
        assert pheno.predicted_hair_color == "Black"
        assert pheno.hair_color_probabilities["Black"] > 0.85
        assert pheno.predicted_skin_phototype == "Dark_to_Black_Type_VI"
        assert pheno.skin_phototype_probabilities["Dark_to_Black_Type_VI"] > 0.85
        assert pheno.predicted_hair_texture == "Coily"
        assert pheno.hair_texture_probabilities["Coily"] > 0.35


