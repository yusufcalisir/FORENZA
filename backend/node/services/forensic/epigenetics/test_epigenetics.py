import pytest
from backend.node.services.forensic.epigenetics.age_engine import EpigeneticClockEngine


def test_standard_blood_epigenetic_age_prediction():
    engine = EpigeneticClockEngine()
    cpg_data = {
        "ELOVL2": 0.45,
        "FHL2": 0.35,
        "TRIM59": 0.25,
        "KLF14": 0.60,
        "MIR29B2CHG": 0.30
    }
    result = engine.predict_age(cpg_data, tissue_type="BLOOD")
    assert "estimated_age_years" in result
    assert result["estimated_age_years"] > 15.0
    assert result["prediction_interval_lower"] < result["estimated_age_years"]
    assert result["prediction_interval_upper"] > result["estimated_age_years"]
    assert result["tissue_type"] == "BLOOD"
    assert result["expanded_uncertainty_95"] == 6.4


def test_buccal_tissue_intercept_offset():
    engine = EpigeneticClockEngine()
    cpg_data = {
        "ELOVL2": 0.40,
        "FHL2": 0.30,
        "TRIM59": 0.20,
        "KLF14": 0.50,
        "MIR29B2CHG": 0.25
    }
    res_blood = engine.predict_age(cpg_data, tissue_type="BLOOD")
    res_buccal = engine.predict_age(cpg_data, tissue_type="BUCCAL")
    assert res_buccal["estimated_age_years"] > res_blood["estimated_age_years"]
    assert res_buccal["tissue_offset_applied"] == 1.2


def test_age_acceleration_delta_calculation():
    engine = EpigeneticClockEngine()
    cpg_data = {
        "ELOVL2": 0.70,
        "FHL2": 0.60,
        "TRIM59": 0.50,
        "KLF14": 0.20,
        "MIR29B2CHG": 0.50
    }
    result = engine.predict_age(cpg_data, tissue_type="BLOOD", chronological_age_known=30.0)
    assert result["age_acceleration_delta"] is not None
    assert result["age_acceleration_delta"] > 5.0
    assert result["aging_status"] == "ACCELERATED_BIOLOGICAL_AGING"


def test_cpg_beta_validation_bounds():
    engine = EpigeneticClockEngine()
    invalid_cpg = {"ELOVL2": 1.45}  # Beta > 1.0 invalid
    with pytest.raises(ValueError, match="must be within"):
        engine.predict_age(invalid_cpg)


def test_empty_cpg_dictionary_rejected():
    engine = EpigeneticClockEngine()
    with pytest.raises(ValueError, match="cannot be empty"):
        engine.predict_age({})
