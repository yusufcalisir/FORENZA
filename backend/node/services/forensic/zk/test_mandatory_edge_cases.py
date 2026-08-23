"""
FORENZA: Forensic Evidence Operating System
Module: ZK-SNARK Proving Systems - 5 Mandatory ISO/IEC 17025 Edge Cases (EC-ZK-01 to EC-ZK-05)

Source of Truth: research/zk_snark_proving_systems_verifiable_forensic_computation_research.md
Strict Validation of Remainder Bounds, Field Wrap-Around Resistance, Precision Invariants, SMT Soundness & Setup Transcripts.
"""

import pytest
from backend.node.services.forensic.zk.gadgets.range_check import RangeCheckGadget, R1CSConstraint
from backend.node.services.forensic.zk.gadgets.division import NonDeterministicDivisionGadget
from backend.node.services.forensic.zk.fixed_point import FixedPointEngine
from backend.node.services.forensic.zk.smt_soundness import SMTCircuitSoundnessAnalyzer
from backend.node.services.forensic.zk.ceremony_validator import CeremonyTranscriptValidator
from backend.node.services.forensic.zk.schemas import CeremonyTranscript, CeremonyParticipant
from backend.node.services.forensic.zk.finite_field import BN254_SCALAR_FIELD_R


def test_edge_case_1_remainder_boundary_saturation():
    """
    EC-ZK-01: Remainder Upper Bound Saturation
    Validates that r = D_hat - 1 satisfies constraint (slack = 0), while r = D_hat strictly fails.
    """
    gadget = NonDeterministicDivisionGadget(scale_s=16, max_bitwidth_b=64)
    d_hat = 10000

    # Case A: Boundary saturation r = D_hat - 1 (slack = 0)
    # N * 2^S = LR * D + (D - 1) => dividend = LR * D + D - 1
    lr_hat = 50
    r_sat = d_hat - 1
    dividend = lr_hat * d_hat + r_sat
    # Simulate valid witness assignment at exact boundary
    slack_sat = (d_hat - 1 - r_sat)  # == 0
    assert slack_sat == 0
    rc_slack = RangeCheckGadget(bitwidth=64)
    assert rc_slack.verify_assignment(slack_sat) is True

    # Case B: Remainder overflow r = D_hat => slack = -1 (field wrap-around r - 1)
    slack_overflow = (d_hat - 1 - d_hat) % BN254_SCALAR_FIELD_R
    # Verify that slack_overflow is huge (close to r) and strictly fails bitwidth 64 range check
    assert slack_overflow > (1 << 64)
    assert rc_slack.verify_assignment(slack_overflow) is False


def test_edge_case_2_field_modular_wraparound_underflow_resistance():
    """
    EC-ZK-02: Field Modular Wrap-Around Underflow Attack Resistance
    Ensures that an adversary attempting to inject negative dividends or quotient values
    modulo r cannot pass the 64-bit decomposition range checks.
    """
    rc = RangeCheckGadget(bitwidth=64)
    modulus = BN254_SCALAR_FIELD_R

    # Adversary tries negative quotient: -5 = r - 5 (mod r)
    fake_negative_quotient = (modulus - 5) % modulus
    assert fake_negative_quotient > (1 << 64)
    assert rc.verify_assignment(fake_negative_quotient) is False

    # Bit decomposition synthesize_witness must raise ValueError
    with pytest.raises(ValueError):
        _ = rc.synthesize_witness(fake_negative_quotient, prefix="underflow_test")


def test_edge_case_3_scale_boundary_precision_conservation():
    """
    EC-ZK-03: Scale Boundary Precision Invariant
    Validates that scaling parameters S=16 and S=32 preserve analytical bounds:
    |x_rec - x| <= 2^-S.
    """
    fp16 = FixedPointEngine(scale_s=16)
    fp32 = FixedPointEngine(scale_s=32)

    val = 0.12345678901234

    rec16, err16, ok16 = fp16.compute_quantization_error(val)
    rec32, err32, ok32 = fp32.compute_quantization_error(val)

    assert ok16 is True
    assert ok32 is True
    assert err16 <= (1.0 / (2**16) + 1e-12)
    assert err32 <= (1.0 / (2**32) + 1e-12)
    # S=32 error must be significantly smaller than S=16 error
    assert err32 < err16


def test_edge_case_4_under_constrained_signal_attack_interception():
    """
    EC-ZK-04: Under-Constrained Signal Interception
    Formal SMT analyzer intercepts missing constraints on intermediate advice signals.
    """
    analyzer = SMTCircuitSoundnessAnalyzer()

    # Honest constraint: (x) * (y) = (z)
    c1 = R1CSConstraint(a_terms={"x": 1}, b_terms={"y": 1}, c_terms={"z": 1})

    # Malicious circuit omits constraint on suspect match signal 'MATCH_FLAG'
    report = analyzer.audit_circuit_soundness(
        circuit_name="UnconstrainedMatchCircuit",
        constraints=[c1],
        public_signals={"MATCH_FLAG"},
        private_signals={"x", "y", "z"},
    )

    assert report.is_sound is False
    assert "MATCH_FLAG" in report.unconstrained_signals
    assert report.uniqueness_verified is False


def test_edge_case_5_corrupted_ceremony_transcript_rejection():
    """
    EC-ZK-05: Corrupted Ceremony Transcript Rejection
    Ensures that broken hash chains, invalid indices, or empty participants in 1-of-N MPC are strictly rejected.
    """
    validator = CeremonyTranscriptValidator()

    # Corrupted: out-of-order contribution index
    p1 = CeremonyParticipant(
        participant_id="Participant-1",
        contribution_index=2,  # Invalid: starts at 2 instead of 1
        accumulator_hash="0xabcdef1234567890abcdef1234567890",
        dlog_proof_of_knowledge="0xproof1234567890abcdef1234567890",
    )
    transcript = CeremonyTranscript(
        ceremony_name="CorruptedCeremony",
        participant_count=1,
        participants=[p1],
        final_srs_hash="0xabcdef1234567890abcdef1234567890",
        is_transcript_valid=True,
    )

    is_valid, errors = validator.verify_transcript(transcript)
    assert is_valid is False
    assert any("index" in e.lower() for e in errors)
