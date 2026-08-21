"""
Unit tests for Craniofacial Reference Standards (Module 3.3).
"""

import pytest
from backend.node.services.forensic.phenotyping.cranio_mathematical_formulation import (
    CraniofacialMathematicalFormulation,
)
from backend.node.services.forensic.phenotyping.cranio_reference_datasets import (
    CRANIOFACIAL_STANDARDS,
)


def test_standards_registry_completeness():
    expected_keys = [
        "NA12878_CEU_EUROPEAN",
        "NA19240_YRI_AFRICAN",
        "NA18507_CHB_EAST_ASIAN",
        "MALE_HIGH_DIMORPHISM",
        "FEMALE_GRACILE_STANDARD",
    ]
    for k in expected_keys:
        assert k in CRANIOFACIAL_STANDARDS


def test_na12878_european_leptorrhine_standard():
    std = CRANIOFACIAL_STANDARDS["NA12878_CEU_EUROPEAN"]
    lm = CraniofacialMathematicalFormulation.reconstruct_cephalometric_landmarks(
        std.snp_dosages, sex=std.sex, age_years=std.age_years
    )
    indices = CraniofacialMathematicalFormulation.compute_anthropological_indices(lm, sex=std.sex)

    assert "LEPTORRHINE" in indices.nasal_typology
    assert indices.nasal_index < 70.0


def test_na19240_african_platyrrhine_standard():
    std = CRANIOFACIAL_STANDARDS["NA19240_YRI_AFRICAN"]
    lm = CraniofacialMathematicalFormulation.reconstruct_cephalometric_landmarks(
        std.snp_dosages, sex=std.sex, age_years=std.age_years
    )
    indices = CraniofacialMathematicalFormulation.compute_anthropological_indices(lm, sex=std.sex)

    assert "PLATYRRHINE" in indices.nasal_typology
    assert indices.nasal_index >= 75.0


def test_na18507_east_asian_mesorrhine_standard():
    std = CRANIOFACIAL_STANDARDS["NA18507_CHB_EAST_ASIAN"]
    lm = CraniofacialMathematicalFormulation.reconstruct_cephalometric_landmarks(
        std.snp_dosages, sex=std.sex, age_years=std.age_years
    )
    indices = CraniofacialMathematicalFormulation.compute_anthropological_indices(lm, sex=std.sex)

    assert "MESORRHINE" in indices.nasal_typology
    assert 70.0 <= indices.nasal_index <= 84.9
