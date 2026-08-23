"""
Unit tests for Epigenetic Clock Registry and coefficient catalog.
"""

import pytest
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    ClockGeneration,
    EpigeneticTissueType,
)
from backend.node.services.forensic.epigenetics.clocks.clock_registry import (
    EpigeneticClockRegistry,
    MASTER_CPG_REGISTRY,
)


@pytest.fixture
def registry():
    return EpigeneticClockRegistry()


def test_registry_initialization(registry):
    """Verify registry singleton initialization and core clock counts."""
    clocks = registry.list_clocks()
    assert len(clocks) >= 8

    # Verify key clocks exist
    clock_ids = [c.clock_id for c in clocks]
    assert "horvath_2013" in clock_ids
    assert "hannum_2013" in clock_ids
    assert "phenoage" in clock_ids
    assert "grimage" in clock_ids
    assert "dunedin_pace" in clock_ids
    assert "visage_basic" in clock_ids
    assert "visage_enhanced" in clock_ids
    assert "weidner_3cpg" in clock_ids


def test_horvath_2013_metadata(registry):
    """Verify Horvath 2013 pan-tissue clock parameterization."""
    horvath = registry.get_clock("horvath_2013")
    assert horvath is not None
    assert horvath.generation == ClockGeneration.FIRST_GEN_CHRONO
    assert horvath.has_piecewise_transform is True
    assert horvath.pivot_age == 20.0
    assert horvath.intercept == -1.120000
    assert "cg16867657" in horvath.cpg_weights
    assert horvath.cpg_weights["cg16867657"] == 2.850000  # ELOVL2
    assert horvath.cpg_weights["cg16419235"] == -0.950000  # PENK (negative coefficient)


def test_phenoage_and_grimage_metadata(registry):
    """Verify second-generation biological clocks."""
    phenoage = registry.get_clock("phenoage")
    assert phenoage is not None
    assert phenoage.generation == ClockGeneration.SECOND_GEN_BIOLOGICAL
    assert phenoage.target_variable == "PHENOTYPIC_AGE"
    assert len(phenoage.clinical_components) == 10

    grimage = registry.get_clock("grimage")
    assert grimage is not None
    assert grimage.generation == ClockGeneration.SECOND_GEN_BIOLOGICAL
    assert grimage.cpg_weights["cg05575921"] == -32.500000  # AHRR


def test_visage_enhanced_multiplex_metadata(registry):
    """Verify VISAGE Enhanced 8-marker forensic tool."""
    visage = registry.get_clock("visage_enhanced")
    assert visage is not None
    assert visage.generation == ClockGeneration.FORENSIC_REDUCED
    assert EpigeneticTissueType.WHOLE_BLOOD in visage.primary_tissues
    assert EpigeneticTissueType.BONE in visage.primary_tissues
    assert EpigeneticTissueType.TEETH in visage.primary_tissues
    assert len(visage.cpg_weights) >= 10


def test_master_cpg_probe_retrieval(registry):
    """Verify individual probe metadata lookup."""
    elovl2_probe = registry.get_probe_record("cg16867657")
    assert elovl2_probe is not None
    assert elovl2_probe.gene_symbol == "ELOVL2"
    assert elovl2_probe.chromosome == "chr6"

    fhl2_probe = registry.get_probe_record("cg06639320")
    assert fhl2_probe is not None
    assert fhl2_probe.gene_symbol == "FHL2"


def test_get_required_probes_aggregation(registry):
    """Verify aggregated probe set calculation across multiple clocks."""
    probes = registry.get_required_probes(["visage_basic", "weidner_3cpg"])
    assert "cg16867657" in probes  # From VISAGE Basic
    assert "cg25809905" in probes  # ITGA2B From Weidner
    assert "cg02085975" in probes  # ASPA From Weidner
