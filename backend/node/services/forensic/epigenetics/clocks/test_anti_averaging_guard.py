"""
Unit tests for Anti-Averaging Fallacy Guard.
"""

import pytest
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    EpigeneticAgeResult,
    ClockGeneration,
)
from backend.node.services.forensic.epigenetics.clocks.anti_averaging_guard import (
    AntiAveragingGuard,
)


def test_anti_averaging_consensus_and_exclusion():
    """Verify consensus excludes second-generation biological metrics from calendar age."""
    horvath_res = EpigeneticAgeResult(
        clock_id="horvath_2013",
        clock_name="Horvath Pan-Tissue Clock (2013)",
        generation=ClockGeneration.FIRST_GEN_CHRONO,
        predicted_age=42.0,
        expanded_uncertainty_95=3.6,
        age_interval_lower=38.4,
        age_interval_upper=45.6,
        covered_cpgs_count=6,
        missing_cpgs_count=0,
    )

    visage_res = EpigeneticAgeResult(
        clock_id="visage_enhanced",
        clock_name="VISAGE Enhanced 8-Marker Tool (2021)",
        generation=ClockGeneration.FORENSIC_REDUCED,
        predicted_age=41.5,
        expanded_uncertainty_95=3.2,
        age_interval_lower=38.3,
        age_interval_upper=44.7,
        covered_cpgs_count=14,
        missing_cpgs_count=0,
    )

    pheno_res = {
        "dnam_phenoage": 52.4,  # Accelerated by disease
        "pheno_acceleration": 10.4,
    }

    grim_res = {
        "grimage_age": 55.8,    # Accelerated by smoking
        "grimage_acceleration": 13.8,
        "mortality_hazard_ratio": 2.14,
    }

    consensus = AntiAveragingGuard.evaluate_multi_clock_consensus(
        clock_results=[horvath_res, visage_res],
        pheno_result=pheno_res,
        grim_result=grim_res,
    )

    # 1. Consensus age MUST be weighted exclusively over Horvath & VISAGE (around ~41.7), NOT pulled up to ~48
    assert 40.5 <= consensus["consensus_chronological_age"] <= 43.0
    assert consensus["anti_averaging_protection"]["status"] == "ENFORCED"
    assert "phenoage" not in consensus["chronological_clocks_included"]
    assert "grimage" not in consensus["chronological_clocks_included"]
    assert "biological_healthspan_intelligence" in consensus
