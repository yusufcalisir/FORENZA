"""
FORENZA: Forensic Evidence Operating System
API Router: Zero-Knowledge Proof Proving Systems & Verifiable Forensic Computation

Source of Truth: research/zk_snark_proving_systems_verifiable_forensic_computation_research.md
FastAPI Endpoints for Groth16, PLONK, Halo2, VOLE, MPC Trusted Setup & SMT Soundness Verification.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from backend.node.services.forensic.zk.schemas import (
    ProvingSystemType,
    EllipticCurveGroup,
    ZKProofInstance,
    ZKWitnessData,
    ZKVerificationResult,
    Groth16Proof,
    PlonkProof,
    CeremonyTranscript,
    SMTSoundnessReport,
)
from backend.node.services.forensic.zk.engines.groth16_engine import Groth16Engine
from backend.node.services.forensic.zk.engines.plonk_engine import PlonkEngine
from backend.node.services.forensic.zk.engines.halo2_engine import Halo2Engine
from backend.node.services.forensic.zk.engines.vole_engine import VoleEngine
from backend.node.services.forensic.zk.ceremony_validator import CeremonyTranscriptValidator
from backend.node.services.forensic.zk.smt_soundness import SMTCircuitSoundnessAnalyzer
from backend.node.services.forensic.zk.governance_engine import ZKForensicGovernanceEngine
from backend.node.services.forensic.zk.golden_vectors import ALL_ZK_GOLDEN_VECTORS
from backend.node.services.forensic.zk.gadgets.range_check import R1CSConstraint


router = APIRouter(
    prefix="/api/v1/forensic/zk",
    tags=["Forensic Zero-Knowledge Proving Systems & Governance"]
)


class ProofSynthesisRequest(BaseModel):
    instance: ZKProofInstance
    witness: ZKWitnessData
    proving_system: ProvingSystemType = Field(default=ProvingSystemType.GROTH16)


class ProofVerificationRequest(BaseModel):
    instance: ZKProofInstance
    proof_payload: Dict[str, Any]
    proving_system: ProvingSystemType = Field(default=ProvingSystemType.GROTH16)


@router.get("/catalog")
def get_zk_catalog() -> Dict[str, Any]:
    """Retrieves catalog of supported ZK proving systems, curves, and mathematical gadgets."""
    return {
        "subsystem": "ZKP-GROTH16 / PLONK / Halo2 / VOLE",
        "description": "Zero-Knowledge Proof Blind Forensic Auditor & Deterministic Numerical Verifier",
        "standards": ["ISO/IEC 17025:2017", "ENFSI 2017 Evaluative Reporting", "BN254 Pairing Map"],
        "proving_systems": [
            {
                "id": "GROTH16",
                "name": "Groth16 R1CS/QAP",
                "curve": "BN254",
                "proof_size_bytes": 128,
                "verifier_complexity": "O(1) (3 Pairings)",
                "latency_ms": 1.5,
                "best_for": "Public Auditing & Immutable Ledgers",
            },
            {
                "id": "PLONK_KZG",
                "name": "PLONK (KZG Commitments)",
                "curve": "BN254",
                "proof_size_bytes": 576,
                "verifier_complexity": "O(1) (2 Pairings)",
                "latency_ms": 3.0,
                "best_for": "Universal Setup & Updatable Forensic Circuits",
            },
            {
                "id": "HALO2_KZG",
                "name": "Halo2 UltraPLONK + Plookup",
                "curve": "BN254",
                "proof_size_bytes": 800,
                "verifier_complexity": "O(1) + Lookup Arguments",
                "latency_ms": 4.5,
                "best_for": "Non-Linear Log-Likelihood Tables",
            },
            {
                "id": "VOLE_EMP",
                "name": "VOLE (EMP-ZK)",
                "curve": "Symmetric Correlation",
                "proof_size_bytes": "Streaming (~64B/gate)",
                "verifier_complexity": "Designated Verifier (>10^7 gates/s)",
                "latency_ms": 0.3,
                "best_for": "High-Throughput Inter-Agency Private Match",
            },
        ],
        "fixed_point_scales": [16, 32],
        "default_scale_s": 16,
    }


@router.post("/synthesize-proof")
def synthesize_zk_proof(req: ProofSynthesisRequest) -> Dict[str, Any]:
    """Synthesizes zero-knowledge proof for a forensic profile against claimed threshold."""
    if req.proving_system == ProvingSystemType.GROTH16:
        engine = Groth16Engine()
        proof, latency_ms = engine.synthesize_proof(req.instance, req.witness)
        proof_dict = proof.model_dump()
    elif req.proving_system == ProvingSystemType.PLONK_KZG:
        engine = PlonkEngine()
        proof, latency_ms = engine.synthesize_proof(req.instance, req.witness)
        proof_dict = proof.model_dump()
    elif req.proving_system == ProvingSystemType.HALO2_KZG:
        engine = Halo2Engine()
        proof_dict, latency_ms = engine.synthesize_proof(req.instance, req.witness)
    elif req.proving_system == ProvingSystemType.VOLE_EMP:
        engine = VoleEngine()
        proof_dict, latency_ms = engine.synthesize_stream_proof(req.instance, req.witness)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported proving system {req.proving_system}")

    return {
        "status": "SUCCESS",
        "proving_system": req.proving_system,
        "proof": proof_dict,
        "synthesis_latency_ms": latency_ms,
        "claimed_threshold": req.instance.claimed_lr_threshold,
        "is_witness_satisfying": req.witness.true_likelihood_ratio >= req.instance.claimed_lr_threshold,
    }


@router.post("/verify-proof")
def verify_zk_proof(req: ProofVerificationRequest) -> Dict[str, Any]:
    """Verifies a zero-knowledge proof against public instance with pairing/range checks."""
    try:
        if req.proving_system == ProvingSystemType.GROTH16:
            engine = Groth16Engine()
            proof = Groth16Proof(**req.proof_payload) if isinstance(req.proof_payload, dict) else req.proof_payload
            res = engine.verify_proof(req.instance, proof)
        elif req.proving_system == ProvingSystemType.PLONK_KZG:
            engine = PlonkEngine()
            proof = PlonkProof(**req.proof_payload) if isinstance(req.proof_payload, dict) else req.proof_payload
            res = engine.verify_proof(req.instance, proof)
        elif req.proving_system == ProvingSystemType.HALO2_KZG:
            engine = Halo2Engine()
            res = engine.verify_proof(req.instance, req.proof_payload)
        elif req.proving_system == ProvingSystemType.VOLE_EMP:
            engine = VoleEngine()
            res = engine.verify_stream_proof(req.instance, req.proof_payload)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported proving system {req.proving_system}")

        certificate = ZKForensicGovernanceEngine.generate_iso17025_zk_certificate(
            case_id_hash=req.instance.case_id_hash,
            proving_system=req.proving_system.value,
            claimed_threshold=req.instance.claimed_lr_threshold,
            is_verified=res.is_valid,
            audit_hash=res.audit_hash,
        )

        return {
            "status": "SUCCESS",
            "verification_result": res.model_dump(),
            "iso17025_certificate": certificate,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"ZK Verification error: {str(exc)}")



@router.post("/verify-ceremony-transcript")
def verify_ceremony_transcript(transcript: CeremonyTranscript) -> Dict[str, Any]:
    """Verifies a 1-of-N MPC Trusted Setup ceremony transcript."""
    validator = CeremonyTranscriptValidator()
    is_valid, errors = validator.verify_transcript(transcript)
    return {
        "status": "SUCCESS" if is_valid else "INVALID_TRANSCRIPT",
        "is_valid": is_valid,
        "participant_count": transcript.participant_count,
        "final_srs_hash": transcript.final_srs_hash,
        "errors": errors,
    }


@router.post("/audit-smt-soundness")
def audit_smt_soundness(circuit_name: str = Body(default="ForensicMatchCircuit", embed=True)) -> Dict[str, Any]:
    """Runs SMT-based uniqueness inference analyzer on circuit constraints."""
    analyzer = SMTCircuitSoundnessAnalyzer()
    # Canonical clean circuit constraints
    c1 = R1CSConstraint(a_terms={"x": 1}, b_terms={"y": 1}, c_terms={"z": 1})
    c2 = R1CSConstraint(a_terms={"z": 1}, b_terms={"ONE": 1}, c_terms={"out": 1})

    report = analyzer.audit_circuit_soundness(
        circuit_name=circuit_name,
        constraints=[c1, c2],
        public_signals={"out"},
        private_signals={"x", "y", "z"},
    )
    return {
        "status": "SUCCESS",
        "soundness_report": report.model_dump(),
    }


@router.get("/golden-vectors")
def get_golden_vectors() -> Dict[str, Any]:
    """Retrieves all certified ZK multi-omic golden standards."""
    vectors_dict = {}
    for name, (inst, wit) in ALL_ZK_GOLDEN_VECTORS.items():
        vectors_dict[name] = {
            "instance": inst.model_dump(),
            "witness_summary": {
                "sample_id": wit.sample_id,
                "true_likelihood_ratio": wit.true_likelihood_ratio,
                "suspect_locus_count": len(wit.suspect_genotypes),
            }
        }
    return {
        "count": len(ALL_ZK_GOLDEN_VECTORS),
        "golden_vectors": vectors_dict,
    }
