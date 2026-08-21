"""
Unit tests for Pure Craniofacial Mathematical Formulation (Module 3.3).
"""

import math
import numpy as np
import pytest

from backend.node.services.forensic.phenotyping.cranio_mathematical_formulation import (
    CraniofacialMathematicalFormulation,
    CephalometricLandmarks,
    AnthropologicalIndices,
    Point3D,
    CRANIOFACIAL_LOCI,
)


def test_primary_loci_registry():
    assert "rs974448" in CRANIOFACIAL_LOCI
    assert "rs12882923" in CRANIOFACIAL_LOCI
    assert "rs11130635" in CRANIOFACIAL_LOCI
    assert "rs13289" in CRANIOFACIAL_LOCI
    assert "rs7559252" in CRANIOFACIAL_LOCI
    assert len(CRANIOFACIAL_LOCI) == 5


def test_reconstruct_cephalometric_landmarks_zero_dosage():
    dosages = {rs: 0 for rs in CRANIOFACIAL_LOCI}
    lm = CraniofacialMathematicalFormulation.reconstruct_cephalometric_landmarks(dosages, sex="FEMALE")

    # Midline landmarks must have x = 0.00
    assert lm.nasion.x == 0.00
    assert lm.pronasale.x == 0.00
    assert lm.subnasale.x == 0.00
    assert lm.labiale_superius.x == 0.00
    assert lm.menton.x == 0.00

    # Bilateral paired landmarks must be mirror symmetric across x=0
    assert lm.alare_left.x == -lm.alare_right.x
    assert lm.zygion_left.x == -lm.zygion_right.x
    assert lm.cheilion_left.x == -lm.cheilion_right.x

    # Check baseline coordinates
    assert abs(lm.nasion.y - 12.40) < 1e-4
    assert abs(lm.nasion.z - 45.20) < 1e-4
    assert abs(lm.pronasale.y - 48.50) < 1e-4
    assert abs(lm.subnasale.y - 38.20) < 1e-4
    assert abs(lm.menton.y - 18.20) < 1e-4
    assert abs(lm.menton.z - (-68.50)) < 1e-4


def test_additive_dosage_modulation():
    dosages = {"rs974448": 2, "rs12882923": 2, "rs11130635": 2, "rs13289": 2, "rs7559252": 2}
    lm = CraniofacialMathematicalFormulation.reconstruct_cephalometric_landmarks(dosages, sex="FEMALE")

    # Nasion y = 12.4 + 1.25 * 2 = 14.90
    assert abs(lm.nasion.y - 14.90) < 1e-4
    # Nasion z = 45.2 + 0.85 * 2 = 46.90
    assert abs(lm.nasion.z - 46.90) < 1e-4
    # Pronasale y = 48.5 + 2.10 * 2 - 1.45 * 2 = 48.5 + 4.20 - 2.90 = 49.80
    assert abs(lm.pronasale.y - 49.80) < 1e-4
    # Subnasale y = 38.2 - 1.10 * 2 = 36.00
    assert abs(lm.subnasale.y - 36.00) < 1e-4
    # Menton y = 18.2 + 1.85 * 2 = 21.90
    assert abs(lm.menton.y - 21.90) < 1e-4


def test_anthropological_indices_computation():
    dosages = {"rs974448": 1, "rs12882923": 1, "rs11130635": 1, "rs13289": 1, "rs7559252": 1}
    lm = CraniofacialMathematicalFormulation.reconstruct_cephalometric_landmarks(dosages, sex="FEMALE")
    indices = CraniofacialMathematicalFormulation.compute_anthropological_indices(lm, sex="FEMALE")

    assert indices.nasal_height_mm > 0
    assert indices.alar_breadth_mm > 0
    assert indices.nasal_index > 0
    assert indices.morphological_facial_height_mm > 0
    assert indices.bizygomatic_breadth_mm > 0
    assert indices.morphological_facial_index > 0
    assert indices.facial_convexity_angle_deg > 0


def test_generalized_procrustes_superposition_identity():
    dosages = {"rs974448": 1, "rs12882923": 0, "rs11130635": 2, "rs13289": 0, "rs7559252": 1}
    lm = CraniofacialMathematicalFormulation.reconstruct_cephalometric_landmarks(dosages, sex="FEMALE")
    mat = lm.to_matrix()

    # Aligning a matrix to itself should yield zero RMSD
    res = CraniofacialMathematicalFormulation.generalized_procrustes_superposition(mat, mat)
    assert res.rmsd_mm < 1e-6
    assert res.procrustes_distance < 1e-6
    assert abs(res.centroid_size_1 - res.centroid_size_2) < 1e-6
