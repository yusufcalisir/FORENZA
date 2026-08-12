import pytest
from backend.node.services.forensic.epigenetics import (
    EpigeneticClockEngine,
    TissueDeconvolutionEngine,
    LifestyleEpigeneticEngine,
)


def test_tissue_deconvolution_pure_blood_sample():
    engine = TissueDeconvolutionEngine()
    blood_tdmr = {
        "tDMR_BLOOD_01": 0.90,
        "tDMR_BUCCAL_01": 0.10,
        "tDMR_SALIVA_01": 0.12,
        "tDMR_SEMEN_01": 0.05,
        "tDMR_EPITHELIAL_01": 0.08,
        "tDMR_BONE_01": 0.06,
    }
    result = engine.deconvolve_sample(blood_tdmr)
    assert result["top_predicted_tissue"] == "BLOOD"
    assert result["top_tissue_probability"] > 0.50
    assert result["lr_tissue"] > 1.0
    assert "BLOOD" in result["tissue_probabilities"]


def test_tissue_deconvolution_pure_semen_sample():
    engine = TissueDeconvolutionEngine()
    semen_tdmr = {
        "tDMR_BLOOD_01": 0.05,
        "tDMR_BUCCAL_01": 0.05,
        "tDMR_SALIVA_01": 0.04,
        "tDMR_SEMEN_01": 0.95,
        "tDMR_EPITHELIAL_01": 0.06,
        "tDMR_BONE_01": 0.05,
    }
    result = engine.deconvolve_sample(semen_tdmr)
    assert result["top_predicted_tissue"] == "SEMEN"
    assert result["top_tissue_probability"] > 0.80


def test_lifestyle_smoking_heavy_smoker():
    engine = LifestyleEpigeneticEngine()
    result = engine.analyze_lifestyle_profile(ahrr_cg05575921_beta=0.40)
    assert result["smoking_status"] == "CURRENT_HEAVY_SMOKER"
    assert result["smoking_probability"] >= 0.80
    assert result["estimated_pack_years"] > 10.0


def test_lifestyle_smoking_non_smoker():
    engine = LifestyleEpigeneticEngine()
    result = engine.analyze_lifestyle_profile(ahrr_cg05575921_beta=0.88)
    assert result["smoking_status"] == "NON_SMOKER"
    assert result["estimated_pack_years"] == 0.0


def test_lifestyle_circadian_phase_nocturnal():
    engine = LifestyleEpigeneticEngine()
    result = engine.analyze_lifestyle_profile(per2_beta=0.80, bmal1_beta=0.40)
    assert result["circadian_phase"] == "NOCTURNAL_PEAK_NIGHT"
    assert "22:00" in result["estimated_tod_window"]


def test_lifestyle_invalid_ahrr_beta():
    engine = LifestyleEpigeneticEngine()
    with pytest.raises(ValueError, match="must be within"):
        engine.analyze_lifestyle_profile(ahrr_cg05575921_beta=1.50)
