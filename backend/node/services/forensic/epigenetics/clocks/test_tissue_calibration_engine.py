"""
Unit tests for Multi-Tissue Epigenetic Calibration Engine.
"""

import pytest
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    EpigeneticTissueType,
)
from backend.node.services.forensic.epigenetics.clocks.tissue_calibration_engine import (
    TissueCalibrationEngine,
    TISSUE_CALIBRATION_REGISTRY,
)


def test_tissue_calibration_offsets():
    """Verify research-mandated tissue baseline offsets."""
    # Blood has 0 offset
    assert TissueCalibrationEngine.get_offset_for_tissue(EpigeneticTissueType.WHOLE_BLOOD) == 0.00
    # Saliva/buccal offset +2.45y
    assert TissueCalibrationEngine.get_offset_for_tissue(EpigeneticTissueType.SALIVA_BUCCAL) == 2.45
    # Semen germline hypomethylation offset +18.60y
    assert TissueCalibrationEngine.get_offset_for_tissue(EpigeneticTissueType.SEMEN) == 18.60
    # Bone offset +1.15y
    assert TissueCalibrationEngine.get_offset_for_tissue(EpigeneticTissueType.BONE) == 1.15
    # Teeth offset +0.80y
    assert TissueCalibrationEngine.get_offset_for_tissue(EpigeneticTissueType.TEETH) == 0.80
    # Cartilage offset +0.50y
    assert TissueCalibrationEngine.get_offset_for_tissue(EpigeneticTissueType.CARTILAGE) == 0.50


def test_calibrate_predicted_age_application():
    """Verify application of tissue offsets to raw predicted ages."""
    # Raw semen prediction: uncalibrated 15.0 years -> calibrated 33.60 years
    cal_age, offset, rationale = TissueCalibrationEngine.calibrate_predicted_age(
        uncalibrated_age=15.0,
        tissue_type=EpigeneticTissueType.SEMEN,
    )
    assert cal_age == 33.60
    assert offset == 18.60
    assert "hypomethylation" in rationale
