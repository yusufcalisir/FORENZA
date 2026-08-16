import pytest
from backend.node.services.forensic.epigenetics import (
    EpigeneticClockEngine,
    TissueDeconvolutionEngine,
    LifestyleEpigeneticEngine,
)


def test_tissue_deconvolution_pure_blood_sample():
    engine = TissueDeconvolutionEngine()
    blood_tdmr = {
        "cg09652652": 0.12,
        "cg19406367": 0.15,
        "cg17610929": 0.91,
        "cg23521140": 0.85,
        "cg26763284": 0.89,
        "cg23576855": 0.84,
        "cg00399818": 0.82,
        "cg04382942": 0.88,
        "cg11624633": 0.86,
        "cg00854446": 0.82,
        "cg18063373": 0.80,
        "cg07823520": 0.90,
    }
    result = engine.deconvolve_sample(blood_tdmr)
    assert result["top_predicted_tissue"] == "BLOOD"
    assert result["top_tissue_probability"] > 0.80
    assert result["lr_tissue"] > 1.0
    assert "BLOOD" in result["tissue_probabilities"]


def test_tissue_deconvolution_pure_semen_sample():
    engine = TissueDeconvolutionEngine()
    semen_tdmr = {
        "cg09652652": 0.88,
        "cg19406367": 0.92,
        "cg17610929": 0.04,
        "cg23521140": 0.08,
        "cg26763284": 0.05,
        "cg23576855": 0.89,
        "cg00399818": 0.86,
        "cg04382942": 0.91,
        "cg11624633": 0.89,
        "cg00854446": 0.94,
        "cg18063373": 0.92,
        "cg07823520": 0.95,
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
