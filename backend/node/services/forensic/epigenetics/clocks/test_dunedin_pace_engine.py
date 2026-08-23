"""
Unit tests for DunedinPACE Third-Generation Dynamic Pace of Aging Engine.
"""

import pytest
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    MethylationSample,
    EpigeneticTissueType,
)
from backend.node.services.forensic.epigenetics.clocks.dunedin_pace_engine import (
    DunedinPACEEngine,
)


def test_dunedin_pace_velocity_normative_profiles():
    """Verify DunedinPACE output classification for slow, normal, and accelerated aging."""
    # 1. Young, pristine profile
    pristine_sample = MethylationSample(
        sample_id="SAMPLE_PACE_PRISTINE",
        tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
        beta_values={"cg05575921": 0.820, "cg16867657": 0.350, "cg06639320": 0.280},
    )
    pace_pristine = DunedinPACEEngine.calculate_pace_of_aging(pristine_sample, smoking_pack_years=0.0)
    assert pace_pristine["pace_velocity"] <= 1.05
    assert pace_pristine["forensic_admissibility_flag"] is False

    # 2. Accelerated aging profile (heavy smoking + advanced methylation drift)
    accelerated_sample = MethylationSample(
        sample_id="SAMPLE_PACE_ACCEL",
        tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
        beta_values={"cg05575921": 0.400, "cg16867657": 0.550, "cg06639320": 0.480},
    )
    pace_accel = DunedinPACEEngine.calculate_pace_of_aging(accelerated_sample, smoking_pack_years=35.0)
    assert pace_accel["pace_velocity"] > 1.15
    assert pace_accel["classification"] == "ACCELERATED_AGING"
