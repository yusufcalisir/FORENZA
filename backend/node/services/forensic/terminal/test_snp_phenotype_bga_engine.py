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

    # ── 1. Coordinates & Constants Verification ──
    def test_01_continental_coordinates_and_chi2(self):
        assert math.isclose(CHI2_2DOF_95, 5.991, rel_tol=1e-3)
        assert len(CONTINENTAL_COORDINATES) == 7
        assert CONTINENTAL_COORDINATES[ContinentalCluster.AFR].latitude == 0.00
        assert CONTINENTAL_COORDINATES[ContinentalCluster.AFR].longitude == 25.00
        assert CONTINENTAL_COORDINATES[ContinentalCluster.EUR].latitude == 48.50
        assert CONTINENTAL_COORDINATES[ContinentalCluster.EUR].longitude == 15.00
        assert CONTINENTAL_COORDINATES[ContinentalCluster.EAS].latitude == 35.00
        assert CONTINENTAL_COORDINATES[ContinentalCluster.EAS].longitude == 105.00
        assert CONTINENTAL_COORDINATES[ContinentalCluster.SAS].latitude == 22.00
        assert CONTINENTAL_COORDINATES[ContinentalCluster.SAS].longitude == 78.00
        assert CONTINENTAL_COORDINATES[ContinentalCluster.AMR].latitude == -10.00
        assert CONTINENTAL_COORDINATES[ContinentalCluster.AMR].longitude == -60.00
        assert CONTINENTAL_COORDINATES[ContinentalCluster.OCE].latitude == -20.00
        assert CONTINENTAL_COORDINATES[ContinentalCluster.OCE].longitude == 140.00
        assert CONTINENTAL_COORDINATES[ContinentalCluster.MID].latitude == 28.00
        assert CONTINENTAL_COORDINATES[ContinentalCluster.MID].longitude == 38.00

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
        assert bga_res.continental_posteriors[ContinentalCluster.EUR] > 0.90
        assert 45.0 <= bga_res.centroid_latitude <= 50.0
        assert 10.0 <= bga_res.centroid_longitude <= 20.0
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
        assert -5.0 <= bga_res.centroid_latitude <= 10.0
        assert 20.0 <= bga_res.centroid_longitude <= 30.0

        # HIrisPlex Calculation
        pheno = SnpPhenotypeBgaEngine.calculate_hirisplex_phenotypes("VECTOR_TERM_02", dosages)
        assert pheno.predicted_eye_color == "Brown"
        assert pheno.eye_color_probabilities["Brown"] > 0.65
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
        }

        bga_res = SnpPhenotypeBgaEngine.calculate_bga_posteriors("VECTOR_TERM_03", dosages)
        assert bga_res.dominant_ancestry == ContinentalCluster.EAS
        assert bga_res.continental_posteriors[ContinentalCluster.EAS] > 0.85
        assert 30.0 <= bga_res.centroid_latitude <= 40.0
        assert 95.0 <= bga_res.centroid_longitude <= 115.0

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
        assert bga_res.dominant_ancestry in (ContinentalCluster.SAS, ContinentalCluster.MID)
        # Lat/Lon near South Asian subcontinent / Middle East
        assert 15.0 <= bga_res.centroid_latitude <= 35.0
        assert 40.0 <= bga_res.centroid_longitude <= 85.0

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
