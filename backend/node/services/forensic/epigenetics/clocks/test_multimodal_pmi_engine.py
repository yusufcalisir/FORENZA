"""
Unit tests for Multimodal Post-Mortem Interval (PMI) Bayesian Fusion Engine.
"""

import pytest
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    MultimodalPMIRequest,
)
from backend.node.services.forensic.epigenetics.clocks.multimodal_pmi_engine import (
    MultimodalPMIEngine,
)


def test_henssge_thermometry_cooling_curve():
    """Verify Henssge double-exponential model for body temperature cooling."""
    # Body cooled from 37.2C down to 30.5C at ambient 18.0C (should be around ~8-12 hours)
    est = MultimodalPMIEngine.calculate_henssge_thermometry(
        rectal_temp_c=30.5,
        ambient_temp_c=18.0,
        body_mass_kg=75.0,
        clothing_factor=1.0,
    )

    assert est.modality == "HENSSGE_THERMOMETRY"
    assert 6.0 <= est.pmi_point_hours <= 16.0
    assert est.standard_error_hours > 0.0


def test_vitreous_potassium_madea_model():
    """Verify Madea vitreous potassium linear diffusion calculation."""
    # K+ = 10.0 mmol/L -> PMI = 5.26 * 10.0 - 27.10 = 25.5 hours
    est = MultimodalPMIEngine.calculate_vitreous_potassium(potassium_mmol_l=10.0)

    assert est.modality == "VITREOUS_POTASSIUM"
    assert abs(est.pmi_point_hours - 25.5) < 0.1
    assert est.standard_error_hours == 5.35


def test_joint_bayesian_multimodal_pmi_fusion():
    """Verify joint Bayesian fusion across thermometry, vitreous K+, and entomology."""
    req = MultimodalPMIRequest(
        sample_id="CASE_PMI_FUSION_01",
        rectal_temp_celsius=28.0,       # Thermometry suggests ~14-18h
        ambient_temp_celsius=18.0,
        body_mass_kg=70.0,
        clothing_factor=1.0,
        vitreous_potassium_mmol_l=8.5,   # Madea suggests ~17.6h
        accumulated_degree_days=10.5,     # Entomology
    )

    res = MultimodalPMIEngine.fuse_multimodal_pmi(req)

    assert res.estimated_pmi_hours > 10.0
    assert res.pmi_uncertainty_lower_hours < res.estimated_pmi_hours < res.pmi_uncertainty_upper_hours
    assert len(res.modalities_used) == 3
    assert res.epigenetic_5mc_stability_status == "STABLE_ARREST"
    assert "Age-at-Death" in res.enfsi_evaluative_statement
