"""
Unit tests for Taphonomic Epigenetic Kinetics & Post-Mortem Arrest Engine.
"""

import pytest
from backend.node.services.forensic.epigenetics.clocks.taphonomy_engine import (
    TaphonomyEngine,
)


def test_post_mortem_enzymatic_arrest_and_5mc_stability():
    """Verify rapid catalytic arrest and high 5mC covalent stability over 0-120 hours."""
    # 1. Immediate post-mortem (2 hours)
    metrics_2h = TaphonomyEngine.evaluate_post_mortem_epigenetic_stability(
        estimated_pmi_hours=2.0,
        ambient_temperature_c=20.0,
    )
    assert metrics_2h.enzymatic_arrest_status == "COMPLETE_ENZYMATIC_ARREST"
    assert metrics_2h.five_mc_preservation_fraction > 0.999
    assert metrics_2h.epigenetic_clock_reliability == "HIGH_CONFIDENCE_AGE_AT_DEATH"

    # 2. 72 hours post-mortem at 20C
    metrics_72h = TaphonomyEngine.evaluate_post_mortem_epigenetic_stability(
        estimated_pmi_hours=72.0,
        ambient_temperature_c=20.0,
    )
    assert metrics_72h.five_mc_preservation_fraction > 0.995
    assert metrics_72h.deamination_drift_fraction < 0.005
    assert metrics_72h.epigenetic_clock_reliability == "HIGH_CONFIDENCE_AGE_AT_DEATH"
    assert "Age-at-Death" in metrics_72h.biological_rationale


def test_arrhenius_deamination_rate_temperature_dependence():
    """Verify temperature-dependent increase in hydrolytic deamination rate."""
    k_10c = TaphonomyEngine.calculate_deamination_rate(10.0)
    k_20c = TaphonomyEngine.calculate_deamination_rate(20.0)
    k_37c = TaphonomyEngine.calculate_deamination_rate(37.0)

    # Reaction kinetics strictly accelerate with temperature
    assert k_10c < k_20c < k_37c


def test_deamination_drift_correction_filter():
    """Verify deamination noise filtering on degraded post-mortem betas."""
    observed = {"cg16867657": 0.450, "cg06639320": 0.320}
    corrected = TaphonomyEngine.correct_deamination_drift(
        observed_betas=observed,
        pmi_hours=96.0,
        temperature_c=22.0,
    )

    # Corrected value compensates for slight spontaneous hydrolytic deamination
    assert corrected["cg16867657"] >= observed["cg16867657"]
    assert corrected["cg06639320"] >= observed["cg06639320"]
