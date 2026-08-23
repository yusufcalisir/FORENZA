"""
Unit tests for Lu DNAm GrimAge & GrimAge2 Engine.
"""

import pytest
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    MethylationSample,
    EpigeneticTissueType,
)
from backend.node.services.forensic.epigenetics.clocks.grimage_engine import (
    GrimAgeEngine,
)


def test_dnam_packyrs_surrogate_and_smoking_sensitivity():
    """Verify DNAm surrogate PACKYRS scales inversely with AHRR methylation."""
    # 1. Non-smoker (AHRR beta ~ 0.80)
    non_smoker_betas = {"cg05575921": 0.820, "cg16867657": 0.380}
    surrogates_non = GrimAgeEngine.estimate_surrogate_biomarkers(non_smoker_betas, reported_pack_years=0.0)
    assert surrogates_non["DNAm_PACKYRS"] == 0.0

    # 2. Heavy smoker (AHRR beta ~ 0.45 due to tobacco hypomethylation)
    smoker_betas = {"cg05575921": 0.450, "cg16867657": 0.420}
    surrogates_smoke = GrimAgeEngine.estimate_surrogate_biomarkers(smoker_betas, reported_pack_years=25.0)
    assert surrogates_smoke["DNAm_PACKYRS"] > 20.0
    assert surrogates_smoke["DNAm_PAI1"] > surrogates_non["DNAm_PAI1"]


def test_grimage_prediction_and_mortality_hazard():
    """Verify GrimAge lifespan prediction and hazard ratio."""
    sample = MethylationSample(
        sample_id="SAMPLE_GRIM_01",
        tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
        beta_values={
            "cg05575921": 0.520,  # Smoker AHRR
            "cg16867657": 0.450,  # ELOVL2
            "cg22458158": 0.380,  # FHL2
            "cg14361627": 0.280,  # KLF14
        },
    )

    res = GrimAgeEngine.predict_grimage(
        sample=sample,
        chronological_age=50.0,
        smoking_pack_years=20.0,
        biological_sex="MALE",
    )

    assert res["clock_id"] == "grimage"
    assert res["grimage_age"] > 40.0
    assert res["grimage_acceleration"] is not None
    assert res["mortality_hazard_ratio"] > 0.0
    assert "DNAm_PACKYRS" in res["surrogate_biomarkers"]
    assert res["forensic_admissibility_flag"] is False
