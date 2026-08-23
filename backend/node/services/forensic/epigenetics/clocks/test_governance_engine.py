"""
Unit tests for Epigenetic Governance & Judicial Evaluative Reporting Engine.
"""

import pytest
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    EpigeneticAgeResult,
    BiologicalAgingResult,
    ClockGeneration,
)
from backend.node.services.forensic.epigenetics.clocks.governance_engine import (
    EpigeneticGovernanceEngine,
)


def test_judicial_admissibility_and_enfsi_statement():
    """Verify ENFSI statement generation, admissibility filtering, and StPO compliance."""
    visage_res = EpigeneticAgeResult(
        clock_id="visage_enhanced",
        clock_name="VISAGE Enhanced 8-Marker Tool (2021)",
        generation=ClockGeneration.FORENSIC_REDUCED,
        predicted_age=34.5,
        expanded_uncertainty_95=3.2,
        age_interval_lower=31.3,
        age_interval_upper=37.7,
        covered_cpgs_count=14,
        missing_cpgs_count=0,
    )

    bio_res = BiologicalAgingResult(
        phenotypic_age=42.0,
        grimage_age=44.5,
        dunedin_pace_velocity=1.25,
    )

    # 1. Under German StPO jurisdiction
    report_de = EpigeneticGovernanceEngine.evaluate_judicial_admissibility(
        sample_id="CASE_SUSPECT_01",
        clock_results=[visage_res],
        biological_result=bio_res,
        jurisdiction="GERMANY_STPO",
    )

    assert report_de.admissible_chronological_age == 34.5
    assert "visage_enhanced" in report_de.approved_clocks_used
    assert "phenoage" in report_de.disallowed_clocks_excluded
    assert "grimage" in report_de.disallowed_clocks_excluded
    assert "dunedin_pace" in report_de.disallowed_clocks_excluded
    assert report_de.enfsi_tier_level >= 5
    assert "81e" in report_de.statutory_compliance_status
    assert "PROSECUTOR'S FALLACY" in report_de.prosecutors_fallacy_shield
    assert len(report_de.enfsi_statement_tr) > 20
