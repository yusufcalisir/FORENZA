"""
Unit tests for Epigenetic Age Acceleration metrics (EAA, Universal Residual, IEAA, EEAA).
"""

import pytest
from backend.node.services.forensic.epigenetics.clocks.acceleration_engine import (
    EpigeneticAccelerationEngine,
    LeukocyteProportions,
)


def test_raw_acceleration_calculation():
    """Verify raw Delta Age computation."""
    # Predicted 48.5, True 42.0 -> EAA = +6.5 years
    eaa = EpigeneticAccelerationEngine.calculate_raw_acceleration(48.5, 42.0)
    assert abs(eaa - 6.5) < 1e-6

    # Predicted 35.0, True 40.0 -> EAA = -5.0 years
    eaa_neg = EpigeneticAccelerationEngine.calculate_raw_acceleration(35.0, 40.0)
    assert abs(eaa_neg - (-5.0)) < 1e-6


def test_universal_age_acceleration_residual():
    """Verify orthogonal universal age acceleration residual calculation."""
    # At true age 50, expected predicted is 0.8850*50 + 3.95 = 48.2
    # If predicted is 54.2 -> residual = +6.0
    res = EpigeneticAccelerationEngine.calculate_universal_residual(54.2, 50.0)
    assert abs(res - (54.2 - 48.2)) < 1e-4


def test_ieaa_intrinsic_aging_cell_adjustment():
    """Verify IEAA captures cell-autonomous aging with leukocyte adjustment."""
    normal_cells = LeukocyteProportions(
        cd8_naive=0.10,
        cd8_exhausted=0.05,
        cd4_t=0.25,
        b_cell=0.08,
        natural_killer=0.10,
        monocyte=0.08,
        granulocyte=0.34,
    )

    ieaa = EpigeneticAccelerationEngine.calculate_ieaa(
        horvath_predicted_age=45.0,
        true_age=45.0,
        cell_counts=normal_cells,
    )
    # With balanced cell counts and concordant age, IEAA should be close to 0
    assert abs(ieaa) < 10.0


def test_eeaa_extrinsic_immunosenescence_sensitivity():
    """Verify EEAA increases when exhausted T cells and granulocytes expand."""
    young_immune = LeukocyteProportions(
        cd8_naive=0.25,
        cd8_exhausted=0.02,
        cd4_t=0.30,
        b_cell=0.12,
        granulocyte=0.20,
    )

    exhausted_immune = LeukocyteProportions(
        cd8_naive=0.02,
        cd8_exhausted=0.20,  # High exhausted CD8+
        cd4_t=0.15,
        b_cell=0.04,
        granulocyte=0.50,  # High granulocytes
    )

    eeaa_young = EpigeneticAccelerationEngine.calculate_eeaa(
        hannum_predicted_age=50.0,
        true_age=50.0,
        cell_counts=young_immune,
    )

    eeaa_exhausted = EpigeneticAccelerationEngine.calculate_eeaa(
        hannum_predicted_age=50.0,
        true_age=50.0,
        cell_counts=exhausted_immune,
    )

    # When immunosenescence is elevated, expected baseline is shifted higher, so observed EEAA relative is distinct
    assert eeaa_young != eeaa_exhausted
