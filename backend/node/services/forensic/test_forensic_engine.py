"""
Unit Test Suite for FORENZA Core Forensic Engine (Phase 1 Validation).
Verifies STR profile creation, CODIS completeness, Likelihood Ratio calculation,
and Kinship Index computations.
"""

import pytest
from backend.node.services.forensic.models import (
    KinshipRelationship,
    SampleType,
    STRGenotype,
    STRProfile,
)
from backend.node.services.forensic.str_engine import STREngine
from backend.node.services.forensic.frequency_db import FrequencyDatabase
from backend.node.services.forensic.lr_engine import LREngine
from backend.node.services.forensic.kinship_engine import KinshipEngine


def test_str_profile_creation():
    loci_data = {
        "TH01": (6.0, 9.3),
        "CSF1PO": (10.0, 11.0),
        "FGA": (20.0, 22.0),
    }
    profile = STREngine.create_profile_from_dict("SUSPECT-01", loci_data)
    assert profile.profile_id == "SUSPECT-01"
    assert profile.locus_count == 3
    assert profile.get_locus("TH01").alleles == (6.0, 9.3)


def test_codis_completeness():
    sample_data = {
        "CSF1PO": (10, 11), "FGA": (20, 22), "TH01": (6, 9.3), "TPOX": (8, 11), "VWA": (14, 17),
        "D3S1358": (14, 16), "D5S818": (11, 12), "D7S820": (9, 10), "D8S1179": (12, 13), "D13S317": (11, 12),
        "D16S539": (11, 12), "D18S51": (13, 14), "D21S11": (28, 29), "D1S1656": (14, 15), "D2S1338": (17, 19),
        "D10S1248": (13, 14), "D12S391": (18, 19), "D19S433": (13, 14), "D22S1045": (15, 16), "AMEL": (1, 2)
    }
    profile = STREngine.create_profile_from_dict("FULL-CODIS", sample_data)
    is_complete, missing = STREngine.validate_codis_completeness(profile)
    assert is_complete is True
    assert len(missing) == 0


def test_lr_engine_inclusion():
    loci_data = {
        "TH01": (6.0, 9.3),
        "FGA": (20.0, 22.0),
        "CSF1PO": (10.0, 11.0),
    }
    evidence = STREngine.create_profile_from_dict("EVIDENCE-01", loci_data)
    suspect = STREngine.create_profile_from_dict("SUSPECT-01", loci_data)

    lr_engine = LREngine()
    result = lr_engine.compute_single_source_lr(evidence, suspect, theta=0.01)

    assert result.value > 10.0  # High LR for matching profile
    assert result.metadata["match_status"] == "INCLUSION"
    assert result.confidence_interval[0] < result.value < result.confidence_interval[1]

    # Invariant: Combined LR must mathematically equal product of locus LRs (in log-space)
    import math
    sum_log_locus = sum(math.log10(score) for score in result.locus_scores.values())
    assert abs(math.log10(result.value) - sum_log_locus) < 1e-6
    assert abs(result.value - (10.0 ** sum_log_locus)) < 1e-4


def test_lr_engine_exclusion():
    evidence_data = {"TH01": (6.0, 9.3), "FGA": (20.0, 22.0)}
    suspect_data = {"TH01": (7.0, 8.0), "FGA": (20.0, 22.0)}  # Mismatch at TH01

    evidence = STREngine.create_profile_from_dict("EVIDENCE-01", evidence_data)
    suspect = STREngine.create_profile_from_dict("SUSPECT-02", suspect_data)

    lr_engine = LREngine()
    result = lr_engine.compute_single_source_lr(evidence, suspect)

    assert result.value == 0.0
    assert result.metadata["match_status"] == "EXCLUSION"


def test_kinship_engine_parent_child():
    child_data = {"TH01": (6.0, 9.3), "FGA": (20.0, 22.0)}
    alleged_father_data = {"TH01": (9.3, 10.0), "FGA": (22.0, 24.0)}

    child = STREngine.create_profile_from_dict("CHILD-01", child_data)
    father = STREngine.create_profile_from_dict("FATHER-01", alleged_father_data)

    kinship_engine = KinshipEngine()
    result = kinship_engine.compute_kinship_index(child, father, KinshipRelationship.PARENT_CHILD)

    assert result.value > 1.0
    assert result.metadata["posterior_probability"] > 0.5
