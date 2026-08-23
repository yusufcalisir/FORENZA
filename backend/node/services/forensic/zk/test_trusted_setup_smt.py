"""
Unit tests for Trusted Setup MPC Coordinator, Transcript Validator, and SMT Soundness Analyzer.
"""

import pytest
from backend.node.services.forensic.zk.trusted_setup import MPCTrustedSetupCoordinator
from backend.node.services.forensic.zk.ceremony_validator import CeremonyTranscriptValidator
from backend.node.services.forensic.zk.smt_soundness import SMTCircuitSoundnessAnalyzer
from backend.node.services.forensic.zk.gadgets.range_check import R1CSConstraint


def test_mpc_trusted_setup_and_transcript_validation():
    coordinator = MPCTrustedSetupCoordinator(max_degree=128)

    # 3 Participants contribute sequentially
    p1 = coordinator.contribute(participant_id="Node-Alpha", secret_entropy=111)
    p2 = coordinator.contribute(participant_id="Node-Beta", secret_entropy=222)
    p3 = coordinator.contribute(participant_id="Auditor-Gamma", secret_entropy=333)

    assert len(coordinator.participants) == 3
    assert p1.contribution_index == 1
    assert p2.contribution_index == 2
    assert p3.contribution_index == 3

    # Finalize ceremony
    transcript = coordinator.finalize_ceremony(ceremony_name="FORENZA-MPC-2026")
    assert transcript.participant_count == 3
    assert transcript.is_transcript_valid is True

    # Validate transcript
    validator = CeremonyTranscriptValidator()
    is_valid, errors = validator.verify_transcript(transcript)
    assert is_valid is True
    assert len(errors) == 0


def test_ceremony_transcript_tampering_detection():
    coordinator = MPCTrustedSetupCoordinator(max_degree=64)
    coordinator.contribute(participant_id="Node-1", secret_entropy=123)
    coordinator.contribute(participant_id="Node-2", secret_entropy=456)
    transcript = coordinator.finalize_ceremony()

    # Tamper with the SRS root hash
    transcript.final_srs_hash = "0xTAMPERED_HASH_1234567890"

    validator = CeremonyTranscriptValidator()
    is_valid, errors = validator.verify_transcript(transcript)
    assert is_valid is False
    assert any("mismatch" in e for e in errors)


def test_smt_circuit_soundness_analyzer_clean_circuit():
    analyzer = SMTCircuitSoundnessAnalyzer()
    c1 = R1CSConstraint(a_terms={"x": 1}, b_terms={"y": 1}, c_terms={"z": 1})
    c2 = R1CSConstraint(a_terms={"z": 1}, b_terms={"ONE": 1}, c_terms={"out": 1})

    report = analyzer.audit_circuit_soundness(
        circuit_name="TestCleanCircuit",
        constraints=[c1, c2],
        public_signals={"out"},
        private_signals={"x", "y", "z"},
    )
    assert report.is_sound is True
    assert report.uniqueness_verified is True
    assert len(report.unconstrained_signals) == 0
    assert report.false_match_vulnerability_detected is False


def test_smt_circuit_soundness_analyzer_detects_under_constrained_signal():
    analyzer = SMTCircuitSoundnessAnalyzer()
    # Missing constraint on LR_free
    c1 = R1CSConstraint(a_terms={"x": 1}, b_terms={"y": 1}, c_terms={"z": 1})

    report = analyzer.audit_circuit_soundness(
        circuit_name="VulnerableCircuit",
        constraints=[c1],
        public_signals={"out"},
        private_signals={"x", "y", "z", "LR_free"},  # LR_free never constrained!
    )
    assert report.is_sound is False
    assert report.uniqueness_verified is False
    assert "LR_free" in report.unconstrained_signals
    assert report.false_match_vulnerability_detected is True
