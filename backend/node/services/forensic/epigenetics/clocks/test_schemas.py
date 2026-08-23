"""
Unit tests for Epigenetic Clocks Pydantic v2 schemas and domain models.
"""

import pytest
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    ClockGeneration,
    EpigeneticTissueType,
    EpigeneticPlatform,
    CpGProbeRecord,
    MethylationSample,
    ClockEstimationRequest,
    EpigeneticAgeResult,
    BiologicalAgingResult,
    TaphonomicPMIResult,
    MultimodalPMIRequest,
)


def test_cpg_probe_record_validation():
    """Verify CpG probe schema validation and coordinate definitions."""
    probe = CpGProbeRecord(
        probe_id="cg16867657",
        gene_symbol="ELOVL2",
        chromosome="chr6",
        pos_grch37=11044631,
        pos_grch38=11044634,
        target_strand="+",
        amplicon_bp=267,
        associated_clocks=["horvath_2013", "visage_enhanced"],
        mean_reference_beta=0.385,
    )
    assert probe.probe_id == "cg16867657"
    assert probe.gene_symbol == "ELOVL2"
    assert probe.pos_grch38 == 11044634
    assert 0.0 <= probe.mean_reference_beta <= 1.0


def test_methylation_sample_schema():
    """Verify sample payload creation with beta values and MPS counts."""
    sample = MethylationSample(
        sample_id="SAMPLE_EPI_001",
        tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
        platform=EpigeneticPlatform.TARGETED_BISULFITE_MPS,
        beta_values={"cg16867657": 0.42, "cg06639320": 0.31},
        read_counts_c={"cg16867657": 420, "cg06639320": 310},
        read_counts_t={"cg16867657": 580, "cg06639320": 690},
        bisulfite_conversion_efficiency=0.995,
        input_dna_pg=25.0,
    )
    assert sample.sample_id == "SAMPLE_EPI_001"
    assert sample.input_dna_pg == 25.0
    assert sample.beta_values["cg16867657"] == 0.42


def test_clock_estimation_request_schema():
    """Verify complete clock estimation request model."""
    sample = MethylationSample(
        sample_id="SAMPLE_TEST",
        tissue_type=EpigeneticTissueType.SALIVA_BUCCAL,
        beta_values={"cg16867657": 0.35},
    )
    req = ClockEstimationRequest(
        sample=sample,
        target_clocks=["horvath_2013", "visage_enhanced"],
        chronological_age=35.0,
        smoking_pack_years=5.0,
        biological_sex="FEMALE",
        jurisdiction="GERMANY_STPO",
    )
    assert req.chronological_age == 35.0
    assert req.jurisdiction == "GERMANY_STPO"
    assert len(req.target_clocks) == 2


def test_epigenetic_age_and_biological_results():
    """Verify age prediction and biological aging results structures."""
    age_res = EpigeneticAgeResult(
        clock_id="horvath_2013",
        clock_name="Horvath Pan-Tissue Clock (2013)",
        generation=ClockGeneration.FIRST_GEN_CHRONO,
        predicted_age=42.4,
        raw_age_acceleration=2.4,
        universal_age_accel=1.8,
        tissue_offset_applied=0.0,
        expanded_uncertainty_95=3.2,
        age_interval_lower=39.2,
        age_interval_upper=45.6,
        covered_cpgs_count=6,
        missing_cpgs_count=0,
    )
    assert age_res.predicted_age == 42.4
    assert age_res.age_interval_lower == 39.2

    bio_res = BiologicalAgingResult(
        phenotypic_age=45.2,
        phenoage_acceleration=3.2,
        grimage_age=46.8,
        grimage_mortality_hazard=1.28,
        dunedin_pace_velocity=1.12,
        forensic_admissibility_flag=False,
    )
    assert bio_res.phenotypic_age == 45.2
    assert bio_res.forensic_admissibility_flag is False


def test_taphonomic_pmi_result_schema():
    """Verify taphonomic PMI model structure."""
    taph = TaphonomicPMIResult(
        sample_id="BONE_REMAINS_01",
        epigenetic_age_at_death=58.5,
        epigenetic_5mc_stability_status="STABLE_ARREST",
        deamination_index=0.04,
        estimated_pmi_hours=48.0,
        pmi_uncertainty_lower_hours=36.0,
        pmi_uncertainty_upper_hours=60.0,
        modalities_used=["Henssge_Thermometry", "Vitreous_Potassium", "Epigenetic_Stability"],
    )
    assert taph.epigenetic_age_at_death == 58.5
    assert taph.estimated_pmi_hours == 48.0
