"""
Unit tests for Multi-Proving System Engines (Groth16, PLONK, Halo2, VOLE).
"""

import pytest
from backend.node.services.forensic.zk.schemas import (
    ProvingSystemType,
    EllipticCurveGroup,
    ZKProofInstance,
    ZKWitnessData,
)
from backend.node.services.forensic.zk.engines.groth16_engine import Groth16Engine
from backend.node.services.forensic.zk.engines.plonk_engine import PlonkEngine
from backend.node.services.forensic.zk.engines.halo2_engine import Halo2Engine
from backend.node.services.forensic.zk.engines.vole_engine import VoleEngine


@pytest.fixture
def sample_instance_and_witness():
    instance = ZKProofInstance(
        case_id_hash="0xcase998877",
        claimed_lr_threshold=1e6,
        claimed_lr_threshold_quantized=65536000000,
        merkle_root="0xmerkle1234",
        locus_count=24,
        scale_s=16,
    )
    witness = ZKWitnessData(
        sample_id="SUSPECT_A",
        suspect_genotypes={"TH01": (9.3, 9.3)},
        evidence_peak_heights={"TH01": {9.3: 2000.0}},
        true_likelihood_ratio=2.5e6,
        numerator_quantized=163840000,
        denominator_quantized=65536,
        quotient_advice=163840000000,
        remainder_advice=0,
    )
    return instance, witness


def test_groth16_proof_synthesis_and_verification(sample_instance_and_witness):
    instance, witness = sample_instance_and_witness
    engine = Groth16Engine()

    proof, latency = engine.synthesize_proof(instance, witness)
    assert proof.proof_size_bytes == 128
    assert proof.curve == EllipticCurveGroup.BN254

    res = engine.verify_proof(instance, proof)
    assert res.is_valid is True
    assert res.proving_system == ProvingSystemType.GROTH16
    assert res.pairing_residual_verified is True
    assert "Tier 6" in res.enfsi_tier


def test_plonk_kzg_proof_synthesis_and_verification(sample_instance_and_witness):
    instance, witness = sample_instance_and_witness
    engine = PlonkEngine()

    proof, latency = engine.synthesize_proof(instance, witness)
    assert proof.proof_size_bytes == 576
    assert len(proof.wire_commitments) == 3

    res = engine.verify_proof(instance, proof)
    assert res.is_valid is True
    assert res.proving_system == ProvingSystemType.PLONK_KZG
    assert res.pairing_residual_verified is True


def test_halo2_ultraplonk_proof_synthesis_and_verification(sample_instance_and_witness):
    instance, witness = sample_instance_and_witness
    engine = Halo2Engine()

    proof, latency = engine.synthesize_proof(instance, witness)
    assert proof["proof_size_bytes"] == 800
    assert proof["lookup_table_valid"] is True

    res = engine.verify_proof(instance, proof)
    assert res.is_valid is True
    assert res.proving_system == ProvingSystemType.HALO2_KZG


def test_vole_designated_verifier_synthesis_and_verification(sample_instance_and_witness):
    instance, witness = sample_instance_and_witness
    engine = VoleEngine()

    proof_stream, latency = engine.synthesize_stream_proof(instance, witness)
    assert proof_stream["system"] == "VOLE_EMP"
    assert len(proof_stream["vector_a"]) == 4

    res = engine.verify_stream_proof(instance, proof_stream)
    assert res.is_valid is True
    assert res.proving_system == ProvingSystemType.VOLE_EMP
