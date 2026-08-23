"""
Unit tests for ZK-SNARK Proving Systems - Domain Schemas & Pydantic v2 Models.
"""

import pytest
from backend.node.services.forensic.zk.schemas import (
    ProvingSystemType,
    EllipticCurveGroup,
    FixedPointConfig,
    EllipticCurvePoint,
    Groth16Proof,
    PlonkProof,
    ZKProofInstance,
    ZKWitnessData,
    ZKVerificationResult,
    SMTSoundnessReport,
    CeremonyParticipant,
    CeremonyTranscript,
)


def test_fixed_point_config_schema():
    cfg = FixedPointConfig(scale_s=16, max_bitwidth_b=64)
    assert cfg.scale_s == 16
    assert cfg.max_bitwidth_b == 64
    assert cfg.field_modulus_r == 21888242871839275222246405745257275088548364400416034343698204186575808495617


def test_elliptic_curve_point_schema():
    p1 = EllipticCurvePoint(x=1, y=2, is_infinity=False, group="G1")
    assert p1.x == 1
    assert p1.y == 2
    assert not p1.is_infinity


def test_groth16_proof_schema():
    pa = EllipticCurvePoint(x=10, y=20, group="G1")
    pb = EllipticCurvePoint(x=[30, 31], y=[40, 41], group="G2")
    pc = EllipticCurvePoint(x=50, y=60, group="G1")
    proof = Groth16Proof(a=pa, b=pb, c=pc, curve=EllipticCurveGroup.BN254)
    assert proof.proof_size_bytes == 128
    assert proof.a.x == 10


def test_zk_proof_instance_and_witness_schema():
    inst = ZKProofInstance(
        case_id_hash="0xabcd1234",
        claimed_lr_threshold=1000000.0,
        claimed_lr_threshold_quantized=65536000000,
        merkle_root="0x99887766",
        locus_count=24,
        scale_s=16
    )
    assert inst.locus_count == 24
    assert inst.claimed_lr_threshold == 1000000.0

    witness = ZKWitnessData(
        sample_id="SAMPLE_001",
        suspect_genotypes={"TH01": (9.3, 9.3), "D21S11": (28.0, 30.0)},
        evidence_peak_heights={"TH01": {9.3: 1500.0}},
        true_likelihood_ratio=2500000.0,
        numerator_quantized=163840000,
        denominator_quantized=65536,
        quotient_advice=163840000000,
        remainder_advice=0
    )
    assert witness.sample_id == "SAMPLE_001"
    assert witness.true_likelihood_ratio == 2500000.0


def test_zk_verification_result_schema():
    res = ZKVerificationResult(
        is_valid=True,
        proving_system=ProvingSystemType.GROTH16,
        pairing_residual_verified=True,
        range_checks_passed=True,
        claimed_threshold_satisfied=True,
        verification_latency_ms=1.45,
        audit_hash="0xdeadbeef",
        enfsi_tier="Tier 6: Extremely Strong Support"
    )
    assert res.is_valid is True
    assert res.proving_system == ProvingSystemType.GROTH16


def test_ceremony_transcript_schema():
    p1 = CeremonyParticipant(
        participant_id="Auditor-01",
        contribution_index=1,
        accumulator_hash="0xhash1",
        dlog_proof_of_knowledge="0xproof1"
    )
    transcript = CeremonyTranscript(
        ceremony_name="Perpetual Powers of Tau",
        participant_count=1,
        participants=[p1],
        final_srs_hash="0xroot",
        is_transcript_valid=True
    )
    assert transcript.participant_count == 1
    assert transcript.is_transcript_valid is True
