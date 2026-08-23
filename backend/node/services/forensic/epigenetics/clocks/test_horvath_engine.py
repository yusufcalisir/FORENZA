"""
Unit tests for Horvath First-Generation Epigenetic Clock Engine.
"""

import pytest
import math
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    MethylationSample,
    EpigeneticTissueType,
    EpigeneticPlatform,
)
from backend.node.services.forensic.epigenetics.clocks.horvath_engine import (
    HorvathEpigeneticEngine,
)


def test_piecewise_transformation_continuity_at_pivot():
    """Verify exact continuous behavior of F(Age) at pivot boundary Age = 20.0."""
    f_left = HorvathEpigeneticEngine.transform_age_forward(20.0 - 1e-9)
    f_pivot = HorvathEpigeneticEngine.transform_age_forward(20.0)
    f_right = HorvathEpigeneticEngine.transform_age_forward(20.0 + 1e-9)

    assert abs(f_pivot - 0.0) < 1e-6
    assert abs(f_left - f_right) < 1e-6


def test_piecewise_inverse_bijection():
    """Verify exact inverse link bijection: F^-1(F(Age)) == Age."""
    test_ages = [0.5, 5.0, 12.0, 19.9, 20.0, 25.0, 45.0, 70.0, 95.0]
    for age in test_ages:
        y_trans = HorvathEpigeneticEngine.transform_age_forward(age)
        age_reconstructed = HorvathEpigeneticEngine.transform_age_inverse(y_trans)
        assert abs(age - age_reconstructed) < 1e-5


def test_horvath_pan_tissue_prediction_adult():
    """Verify Horvath 2013 prediction on typical adult multi-tissue profile."""
    sample = MethylationSample(
        sample_id="ADULT_BLOOD_40Y",
        tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
        beta_values={
            "cg16867657": 0.40,  # ELOVL2
            "cg06639320": 0.32,  # FHL2
            "cg16419235": 0.22,  # PENK (hypomethylated)
            "cg04523812": 0.28,  # TRIM59
            "cg07955995": 0.22,  # KLF14
            "cg17861230": 0.35,  # PDE4C
        },
    )

    res = HorvathEpigeneticEngine.predict_age(
        sample=sample,
        clock_id="horvath_2013",
        chronological_age=42.0,
    )

    assert res.predicted_age > 20.0
    assert 30.0 <= res.predicted_age <= 55.0
    assert res.raw_age_acceleration is not None
    assert res.age_interval_lower < res.predicted_age < res.age_interval_upper
    assert res.covered_cpgs_count == 6


def test_pedbe_pediatric_buccal_prediction():
    """Verify PedBE clock prediction for a young child (< 20 years)."""
    sample = MethylationSample(
        sample_id="PEDIATRIC_SALIVA_8Y",
        tissue_type=EpigeneticTissueType.SALIVA_BUCCAL,
        beta_values={
            "cg02228185": 0.15,  # Low MIR29B2CHG in young children
            "cg09809672": 0.18,  # Low EDARADD
            "cg16867657": 0.12,  # Low ELOVL2
        },
    )

    res = HorvathEpigeneticEngine.predict_age(
        sample=sample,
        clock_id="pedbe_2019",
        chronological_age=8.0,
    )

    assert res.predicted_age < 20.0
    assert res.predicted_age >= 0.0
    assert abs(res.raw_age_acceleration) < 10.0
