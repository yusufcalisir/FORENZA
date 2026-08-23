"""
Unit tests for ISO/IEC 17025 GUM Metrological Uncertainty Budget Engine.
"""

import pytest
from backend.node.services.forensic.epigenetics.clocks.uncertainty_budget import (
    UncertaintyBudgetEngine,
)


def test_standard_metrological_uncertainty_budget():
    """Verify ISO 17025 expanded uncertainty with standard template mass (500 pg)."""
    budget = UncertaintyBudgetEngine.compute_expanded_uncertainty(
        base_mae=3.20,
        input_dna_pg=500.0,
        bisulfite_efficiency=0.994,
        missing_loci_ratio=0.0,
        leverage_distance=0.04,
    )

    assert budget.coverage_factor_k == 2.00
    assert budget.model_residual_sd > 3.0
    assert budget.expanded_uncertainty_u95 > budget.combined_standard_uncertainty
    # Standard 95% expanded interval should be around 8.0 - 9.0 years with k=2.00
    assert 6.0 <= budget.expanded_uncertainty_u95 <= 12.0
    assert budget.template_mass_penalty == 0.0


def test_trace_dna_and_degraded_efficiency_penalty():
    """Verify uncertainty budget expansion when template is trace (<50 pg) or bisulfite efficiency is reduced."""
    budget_trace = UncertaintyBudgetEngine.compute_expanded_uncertainty(
        base_mae=3.20,
        input_dna_pg=20.0,  # Trace input
        bisulfite_efficiency=0.986,  # Slightly low conversion
        missing_loci_ratio=0.20,  # 20% missing loci
        leverage_distance=0.15,
    )

    assert budget_trace.template_mass_penalty > 0.0
    assert budget_trace.sequencing_depth_uncertainty > 0.0
    # Trace/degraded conditions must strictly increase U_95%
    assert budget_trace.expanded_uncertainty_u95 > 8.5
