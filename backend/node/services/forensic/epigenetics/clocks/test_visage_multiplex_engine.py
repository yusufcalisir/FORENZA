"""
Unit tests for VISAGE and Forensic Reduced-Marker Multiplex Engine.
"""

import pytest
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    MethylationSample,
    EpigeneticTissueType,
    EpigeneticPlatform,
)
from backend.node.services.forensic.epigenetics.clocks.visage_multiplex_engine import (
    VISAGEMultiplexEngine,
)


def test_visage_basic_mlr_prediction():
    """Verify VISAGE Basic 5-CpG power MLR model."""
    sample = MethylationSample(
        sample_id="VISAGE_BASIC_SAMPLE",
        tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
        beta_values={
            "cg16867657": 0.45,  # ELOVL2
            "cg06639320": 0.35,  # FHL2
            "cg16419235": 0.20,  # PENK
            "cg04523812": 0.30,  # TRIM59
            "cg07955995": 0.25,  # KLF14
        },
    )

    res = VISAGEMultiplexEngine.predict_visage_basic_mlr(
        sample=sample,
        chronological_age=38.0,
        tissue_offset=0.0,
    )

    assert res.clock_id == "visage_basic"
    assert 25.0 <= res.predicted_age <= 50.0
    assert res.expanded_uncertainty_95 > 0.0
    assert res.age_interval_lower < res.predicted_age < res.age_interval_upper


def test_visage_enhanced_trace_dna_sensitivity():
    """Verify VISAGE Enhanced tool precision with normal vs. ultra-low trace input (18 pg)."""
    # 1. Normal template (500 pg)
    sample_normal = MethylationSample(
        sample_id="VISAGE_NORM",
        tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
        input_dna_pg=500.0,
        beta_values={
            "cg16867657": 0.42, "cg24724428": 0.45, "cg21572722": 0.38,
            "cg06639320": 0.32, "cg22458158": 0.30, "cg16419235": 0.22,
            "cg04523812": 0.28, "cg04084157": 0.27, "cg07955995": 0.22,
            "cg14361627": 0.23, "cg02228185": 0.46, "cg17861230": 0.34,
            "cg02085975": 0.53, "cg09809672": 0.42,
        },
    )
    res_norm = VISAGEMultiplexEngine.predict_visage_enhanced(sample_normal, chronological_age=40.0)

    # 2. Ultra-low trace template (18 pg)
    sample_trace = MethylationSample(
        sample_id="VISAGE_TRACE_18PG",
        tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
        input_dna_pg=18.0,
        beta_values=sample_normal.beta_values,
    )
    res_trace = VISAGEMultiplexEngine.predict_visage_enhanced(sample_trace, chronological_age=40.0)

    assert abs(res_norm.predicted_age - res_trace.predicted_age) < 1e-4
    # Trace input (< 50 pg) expands the uncertainty interval
    assert res_trace.expanded_uncertainty_95 > res_norm.expanded_uncertainty_95


def test_weidner_3cpg_blood_model():
    """Verify Weidner 3-CpG pyrosequencing blood model."""
    sample = MethylationSample(
        sample_id="WEIDNER_SAMPLE",
        tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
        beta_values={
            "cg02085975": 0.52,  # ASPA
            "cg25809905": 0.48,  # ITGA2B
            "cg17861230": 0.33,  # PDE4C
        },
    )

    res = VISAGEMultiplexEngine.predict_weidner_3cpg(
        sample=sample,
        chronological_age=45.0,
    )

    assert res.clock_id == "weidner_3cpg"
    assert 35.0 <= res.predicted_age <= 70.0
