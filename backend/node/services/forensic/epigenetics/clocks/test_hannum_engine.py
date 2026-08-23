"""
Unit tests for Hannum First-Generation Blood Epigenetic Clock Engine.
"""

import pytest
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    MethylationSample,
    EpigeneticTissueType,
)
from backend.node.services.forensic.epigenetics.clocks.hannum_engine import (
    HannumEpigeneticEngine,
)


def test_hannum_blood_prediction_adult():
    """Verify Hannum 2013 prediction on adult blood sample."""
    sample = MethylationSample(
        sample_id="HANNUM_TEST_SAMPLE",
        tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
        beta_values={
            "cg06639320": 0.35,  # FHL2
            "cg16867657": 0.40,  # ELOVL2
            "cg04523812": 0.30,  # TRIM59
            "cg07955995": 0.25,  # KLF14
        },
    )

    res = HannumEpigeneticEngine.predict_age(
        sample=sample,
        chronological_age=50.0,
        tissue_offset=0.0,
    )

    assert res.clock_id == "hannum_2013"
    assert res.predicted_age > 30.0
    assert res.raw_age_acceleration is not None
    assert res.age_interval_lower < res.predicted_age < res.age_interval_upper
    assert res.expanded_uncertainty_95 > 0.0
