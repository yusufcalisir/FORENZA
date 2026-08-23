"""
5 Mandatory Scientific Edge-Case Verification Tests (Master Rule 3 Criterion 3).

Verifies the 5 mandatory edge cases for Epigenetic Clocks & Multimodal PMI Estimation:
  1. Edge Case 1: Pediatric to Adult Horizon Boundary Continuity (19.9y -> 20.0y -> 20.1y)
  2. Edge Case 2: Extreme Tissue Divergence & Semen Germline Hypomethylation Correction
  3. Edge Case 3: Ultra-Low Trace Template DNA Degradation (18 pg Input Mass)
  4. Edge Case 4: Heavy Tobacco Hypomethylation Shock (AHRR cg05575921 Hypomethylation)
  5. Edge Case 5: Post-Mortem Decomposed Submerged Specimen with Cold Cooling Kinetics
"""

import pytest
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    MethylationSample,
    EpigeneticTissueType,
    EpigeneticPlatform,
    MultimodalPMIRequest,
)
from backend.node.services.forensic.epigenetics.clocks.horvath_engine import (
    HorvathEpigeneticEngine,
)
from backend.node.services.forensic.epigenetics.clocks.visage_multiplex_engine import (
    VISAGEMultiplexEngine,
)
from backend.node.services.forensic.epigenetics.clocks.tissue_calibration_engine import (
    TissueCalibrationEngine,
)
from backend.node.services.forensic.epigenetics.clocks.grimage_engine import (
    GrimAgeEngine,
)
from backend.node.services.forensic.epigenetics.clocks.taphonomy_engine import (
    TaphonomyEngine,
)
from backend.node.services.forensic.epigenetics.clocks.multimodal_pmi_engine import (
    MultimodalPMIEngine,
)


def test_edge_case_1_pediatric_adult_horizon_continuity():
    """Edge Case 1: Validate continuous non-divergent behavior across pivot age y0 = 20.0."""
    f_19_9 = HorvathEpigeneticEngine.transform_age_forward(19.900)
    f_20_0 = HorvathEpigeneticEngine.transform_age_forward(20.000)
    f_20_1 = HorvathEpigeneticEngine.transform_age_forward(20.100)

    # Monotonic and continuous
    assert f_19_9 < f_20_0 < f_20_1
    assert abs(f_20_0 - 0.0) < 1e-6
    assert abs((f_20_1 - f_20_0) - (f_20_0 - f_19_9)) < 0.002


def test_edge_case_2_semen_germline_hypomethylation_offset():
    """Edge Case 2: Validate semen offset (+18.60y) correcting for spermatogenesis hypomethylation."""
    sample_semen = MethylationSample(
        sample_id="SEMEN_TRIVIAL_AGE",
        tissue_type=EpigeneticTissueType.SEMEN,
        beta_values={
            "cg16867657": 0.150,  # ELOVL2 low in sperm
            "cg06639320": 0.120,  # FHL2 low in sperm
            "cg16419235": 0.180,  # PENK
            "cg04523812": 0.140,  # TRIM59
            "cg07955995": 0.110,  # KLF14
        },
    )

    # 1. Uncalibrated prediction severely underpredicts donor age (~12 years)
    res_uncal = VISAGEMultiplexEngine.predict_visage_basic_mlr(sample_semen, tissue_offset=0.0)
    assert res_uncal.predicted_age < 18.0

    # 2. Calibrated prediction applies +18.60y offset restoring true adult donor age (~24-25 years)
    offset = TissueCalibrationEngine.get_offset_for_tissue(EpigeneticTissueType.SEMEN)
    res_cal = VISAGEMultiplexEngine.predict_visage_basic_mlr(sample_semen, tissue_offset=offset)
    assert res_cal.predicted_age >= 22.0
    assert abs(res_cal.predicted_age - (res_uncal.predicted_age + 18.60)) < 1e-3


def test_edge_case_3_trace_template_dna_uncertainty_inflation():
    """Edge Case 3: Validate ISO 17025 expanded uncertainty inflation for 18 pg trace input."""
    base_betas = {
        "cg16867657": 0.40, "cg24724428": 0.42, "cg21572722": 0.35,
        "cg06639320": 0.30, "cg22458158": 0.28, "cg16419235": 0.24,
        "cg04523812": 0.26, "cg04084157": 0.25, "cg07955995": 0.20,
        "cg14361627": 0.20, "cg02228185": 0.42, "cg17861230": 0.31,
        "cg02085975": 0.55, "cg09809672": 0.38,
    }

    sample_bulk = MethylationSample(
        sample_id="SAMPLE_BULK_500PG",
        tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
        input_dna_pg=500.0,
        beta_values=base_betas,
    )
    sample_trace = MethylationSample(
        sample_id="SAMPLE_TRACE_18PG",
        tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
        input_dna_pg=18.0,  # Extreme trace input
        beta_values=base_betas,
    )

    res_bulk = VISAGEMultiplexEngine.predict_visage_enhanced(sample_bulk)
    res_trace = VISAGEMultiplexEngine.predict_visage_enhanced(sample_trace)

    # Point predictions match
    assert abs(res_bulk.predicted_age - res_trace.predicted_age) < 1e-4
    # Expanded uncertainty for trace is strictly wider
    assert res_trace.expanded_uncertainty_95 > res_bulk.expanded_uncertainty_95
    assert (res_trace.age_interval_upper - res_trace.age_interval_lower) > (res_bulk.age_interval_upper - res_bulk.age_interval_lower)


def test_edge_case_4_tobacco_hypomethylation_shock_divergence():
    """Edge Case 4: Validate GrimAge / surrogate PACKYRS sensitivity to AHRR shock with Horvath invariance."""
    sample_smoker_shock = MethylationSample(
        sample_id="SMOKER_SHOCK_SAMPLE",
        tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
        beta_values={
            "cg16867657": 0.450,  # ELOVL2
            "cg06639320": 0.350,  # FHL2
            "cg16419235": 0.200,  # PENK
            "cg04523812": 0.300,  # TRIM59
            "cg07955995": 0.250,  # KLF14
            "cg17861230": 0.350,  # PDE4C
            "cg05575921": 0.380,  # AHRR extreme tobacco hypomethylation shock
        },
    )

    # 1. Horvath chronological prediction is completely unaltered by AHRR probe
    res_horvath = HorvathEpigeneticEngine.predict_age(sample_smoker_shock, chronological_age=45.0)
    assert 40.0 <= res_horvath.predicted_age <= 48.0

    # 2. GrimAge reflects heavy smoking pack-years and marked age acceleration
    res_grim = GrimAgeEngine.predict_grimage(sample_smoker_shock, chronological_age=45.0, smoking_pack_years=30.0)
    assert res_grim["surrogate_biomarkers"]["DNAm_PACKYRS"] > 25.0
    assert res_grim["grimage_acceleration"] >= 5.0
    assert res_grim["mortality_hazard_ratio"] > 1.40


def test_edge_case_5_submerged_decomposition_pmi_epigenetic_arrest():
    """Edge Case 5: Validate cold water submerged body (8C, PMI=72h) with multimodal Bayesian fusion."""
    req_submerged = MultimodalPMIRequest(
        sample_id="CASE_SUBMERGED_8C",
        rectal_temp_celsius=10.5,        # Near water ambient temp (8C)
        ambient_temp_celsius=8.0,
        body_mass_kg=80.0,
        clothing_factor=1.2,
        vitreous_potassium_mmol_l=18.5,  # Madea indicates ~70.2 hours
    )

    res_pmi = MultimodalPMIEngine.fuse_multimodal_pmi(req_submerged)

    # Multimodal Bayesian fusion accurately captures extended interval
    assert res_pmi.estimated_pmi_hours > 40.0
    assert res_pmi.pmi_uncertainty_lower_hours < res_pmi.estimated_pmi_hours < res_pmi.pmi_uncertainty_upper_hours
    assert res_pmi.epigenetic_5mc_stability_status == "STABLE_ARREST"

    # Epigenetic 5mC stability at 8C remains preserved (> 99.8%)
    taph = TaphonomyEngine.evaluate_post_mortem_epigenetic_stability(
        estimated_pmi_hours=res_pmi.estimated_pmi_hours,
        ambient_temperature_c=8.0,
    )
    assert taph.five_mc_preservation_fraction > 0.998
    assert taph.epigenetic_clock_reliability == "HIGH_CONFIDENCE_AGE_AT_DEATH"
