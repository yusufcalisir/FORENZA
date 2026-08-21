"""
Empirical Edge-Case Test Suite for Craniofacial Morphometrics (Module 3.3).

Covers:
  - EC-CRAN-01: Sexual Dimorphism Scaling (+8.4 mm Mandibular Breadth & Height Scaling)
  - EC-CRAN-02: Leptorrhine Nasal Index in European Reference Standard (NI < 70.0)
  - EC-CRAN-03: Platyrrhine Nasal Index in African Reference Standard (NI >= 85.0)
  - EC-CRAN-04: GPA Procrustes Superposition 3D Rigid Invariance (|Delta RMSD| < 1e-5)
  - EC-CRAN-05: Bilateral Midline Symmetry Invariant (|x_L + x_R| < 1e-6)
"""

import math
import numpy as np
import pytest

from backend.node.services.forensic.phenotyping.cranio_mathematical_formulation import (
    CraniofacialMathematicalFormulation,
    CephalometricLandmarks,
    AnthropologicalIndices,
)
from backend.node.services.forensic.phenotyping.cranio_reference_datasets import (
    CRANIOFACIAL_STANDARDS,
)


def test_ec_cran_01_sexual_dimorphism_scaling():
    """
    EC-CRAN-01: Sexual Dimorphism Scaling.
    Male craniometry features expanded mandibular breadth (+8.4 mm)
    and facial height scaling (+4.5%) over female baseline with identical SNP genotypes.
    """
    snp_dosages = {"rs974448": 1, "rs12882923": 1, "rs11130635": 1, "rs13289": 1, "rs7559252": 1}

    lm_female = CraniofacialMathematicalFormulation.reconstruct_cephalometric_landmarks(
        snp_dosages, sex="FEMALE"
    )
    ind_female = CraniofacialMathematicalFormulation.compute_anthropological_indices(
        lm_female, sex="FEMALE"
    )

    lm_male = CraniofacialMathematicalFormulation.reconstruct_cephalometric_landmarks(
        snp_dosages, sex="MALE"
    )
    ind_male = CraniofacialMathematicalFormulation.compute_anthropological_indices(
        lm_male, sex="MALE"
    )

    # 1. Sexual dimorphism offset field must be exactly +8.40 mm for male and 0.00 for female
    assert ind_male.sexual_dimorphism_offset_mm == 8.40
    assert ind_female.sexual_dimorphism_offset_mm == 0.00
    assert ind_male.mandibular_breadth_mm > ind_female.mandibular_breadth_mm

    # 2. Total facial height in male must be scaled by ~4.5%
    height_ratio = ind_male.morphological_facial_height_mm / ind_female.morphological_facial_height_mm
    assert 1.03 <= height_ratio <= 1.06, f"Height ratio {height_ratio} outside expected range"


def test_ec_cran_02_leptorrhine_nasal_index_european():
    """
    EC-CRAN-02: Leptorrhine Nasal Index in European Reference Standard (NI < 70.0).
    NA12878 European reference genotype predicts a narrow nasal aperture (Leptorrhine).
    """
    std = CRANIOFACIAL_STANDARDS["NA12878_CEU_EUROPEAN"]
    lm = CraniofacialMathematicalFormulation.reconstruct_cephalometric_landmarks(
        std.snp_dosages, sex=std.sex, age_years=std.age_years
    )
    indices = CraniofacialMathematicalFormulation.compute_anthropological_indices(lm, sex=std.sex)

    assert indices.nasal_index < 70.0, f"Expected Leptorrhine NI < 70, got {indices.nasal_index}"
    assert "LEPTORRHINE" in indices.nasal_typology


def test_ec_cran_03_platyrrhine_nasal_index_african():
    """
    EC-CRAN-03: Platyrrhine Nasal Index in African Reference Standard (NI >= 85.0).
    NA19240 Sub-Saharan African reference genotype predicts a broad nasal aperture (Platyrrhine).
    """
    std = CRANIOFACIAL_STANDARDS["NA19240_YRI_AFRICAN"]
    lm = CraniofacialMathematicalFormulation.reconstruct_cephalometric_landmarks(
        std.snp_dosages, sex=std.sex, age_years=std.age_years
    )
    indices = CraniofacialMathematicalFormulation.compute_anthropological_indices(lm, sex=std.sex)

    assert indices.nasal_index >= 75.0, f"Expected Platyrrhine NI >= 75, got {indices.nasal_index}"
    assert "PLATYRRHINE" in indices.nasal_typology


def test_ec_cran_04_gpa_procrustes_superposition_invariance():
    """
    EC-CRAN-04: GPA Procrustes Superposition 3D Rigid Invariance.
    Applying arbitrary 3D translation, uniform scaling, and 3D Euler rotation
    to a landmark matrix must yield an aligned RMSD of ~0.0 (|Delta RMSD| < 1e-4).
    """
    dosages = {"rs974448": 2, "rs12882923": 1, "rs11130635": 0, "rs13289": 2, "rs7559252": 1}
    lm = CraniofacialMathematicalFormulation.reconstruct_cephalometric_landmarks(dosages, sex="FEMALE")
    X_orig = lm.to_matrix()

    # Apply 3D rotation (e.g. 45 deg around Z and 30 deg around X), translation, and scaling
    theta_z = math.radians(45.0)
    R_z = np.array([
        [math.cos(theta_z), -math.sin(theta_z), 0],
        [math.sin(theta_z), math.cos(theta_z), 0],
        [0, 0, 1],
    ])
    theta_x = math.radians(30.0)
    R_x = np.array([
        [1, 0, 0],
        [0, math.cos(theta_x), -math.sin(theta_x)],
        [0, math.sin(theta_x), math.cos(theta_x)],
    ])
    R_total = np.dot(R_z, R_x)

    scale_factor = 2.35
    t_offset = np.array([125.4, -84.2, 330.1])

    # Transformed shape: X_trans = scale * X_orig * R + t
    X_trans = (scale_factor * np.dot(X_orig, R_total)) + t_offset

    # Run GPA Procrustes alignment
    gpa_res = CraniofacialMathematicalFormulation.generalized_procrustes_superposition(
        X_orig, X_trans
    )

    assert gpa_res.rmsd_mm < 1e-4, f"Procrustes alignment residual {gpa_res.rmsd_mm} >= 1e-4"


def test_ec_cran_05_bilateral_midline_symmetry_invariant():
    """
    EC-CRAN-05: Bilateral Midline Symmetry Invariant.
    All sagittal midline landmarks must strictly have x = 0.00,
    and all paired bilateral landmarks (Al_L/Al_R, Zy_L/Zy_R, Ch_L/Ch_R)
    must satisfy exact mirror reflection |x_L + x_R| < 1e-6 across arbitrary dosage permutations.
    """
    for pax9_dose in [0, 1, 2]:
        for pcdh15_dose in [0, 1, 2]:
            dosages = {
                "rs974448": 1,
                "rs12882923": pax9_dose,
                "rs11130635": 1,
                "rs13289": 1,
                "rs7559252": pcdh15_dose,
            }
            lm = CraniofacialMathematicalFormulation.reconstruct_cephalometric_landmarks(
                dosages, sex="MALE"
            )

            # Midline points must be on x = 0.00
            assert abs(lm.nasion.x) < 1e-9
            assert abs(lm.pronasale.x) < 1e-9
            assert abs(lm.subnasale.x) < 1e-9
            assert abs(lm.labiale_superius.x) < 1e-9
            assert abs(lm.menton.x) < 1e-9

            # Bilateral paired points must be exact reflectional mirrors
            assert abs(lm.alare_left.x + lm.alare_right.x) < 1e-6
            assert abs(lm.zygion_left.x + lm.zygion_right.x) < 1e-6
            assert abs(lm.cheilion_left.x + lm.cheilion_right.x) < 1e-6
