"""
FORENZA: Forensic Evidence Operating System
Module: ZK-SNARK Proving Systems - Domain Schemas & Pydantic v2 Models

Source of Truth: research/zk_snark_proving_systems_verifiable_forensic_computation_research.md
ISO/IEC 17025:2017 & Circom/Groth16/PLONK/Halo2 Verifiable Computation Standards.
"""

from typing import List, Dict, Optional, Tuple, Any, Union
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class ProvingSystemType(str, Enum):
    GROTH16 = "GROTH16"
    PLONK_KZG = "PLONK_KZG"
    HALO2_KZG = "HALO2_KZG"
    HALO2_IPA = "HALO2_IPA"
    ZK_STARK = "ZK_STARK"
    PLONKY2 = "PLONKY2"
    NOVA_IVC = "NOVA_IVC"
    VOLE_EMP = "VOLE_EMP"


class EllipticCurveGroup(str, Enum):
    BN254 = "BN254"
    BLS12_381 = "BLS12_381"
    PASTA_PALLAS = "PASTA_PALLAS"
    GOLDILOCKS = "GOLDILOCKS"


class FixedPointConfig(BaseModel):
    """Configuration for scaled fixed-point numerical quantization."""
    model_config = ConfigDict(protected_namespaces=(), populate_by_name=True)

    scale_s: int = Field(default=16, ge=8, le=64, description="Fixed-point scaling bit parameter (e.g. S=16 or S=32)")
    max_bitwidth_b: int = Field(default=64, ge=16, le=128, description="Maximum expected bit-width to prevent field overflow")
    field_modulus_r: int = Field(
        default=21888242871839275222246405745257275088548364400416034343698204186575808495617,
        description="Galois field modulus r (default: BN254 scalar field)"
    )


class EllipticCurvePoint(BaseModel):
    """Affine coordinate point in G1 or G2 group."""
    model_config = ConfigDict(protected_namespaces=(), populate_by_name=True)

    x: Union[int, str, float, List[Union[int, str, float]]] = Field(..., description="x-coordinate (int/hex for G1, [x0, x1] for G2 in F_q^2)")
    y: Union[int, str, float, List[Union[int, str, float]]] = Field(..., description="y-coordinate (int/hex for G1, [y0, y1] for G2 in F_q^2)")
    is_infinity: bool = Field(default=False, description="Point at infinity indicator")
    group: str = Field(default="G1", description="Group identifier (G1, G2, GT)")


class Groth16Proof(BaseModel):
    """Groth16 3-element succinct proof tuple pi = (A in G1, B in G2, C in G1)."""
    model_config = ConfigDict(protected_namespaces=(), populate_by_name=True)

    a: EllipticCurvePoint = Field(..., description="A group element in G1 (64 bytes uncompressed / 32 bytes compressed)")
    b: EllipticCurvePoint = Field(..., description="B group element in G2 (128 bytes uncompressed / 64 bytes compressed)")
    c: EllipticCurvePoint = Field(..., description="C group element in G1 (64 bytes uncompressed / 32 bytes compressed)")
    curve: EllipticCurveGroup = Field(default=EllipticCurveGroup.BN254)
    proof_size_bytes: int = Field(default=128, description="Serialized proof footprint in bytes")


class PlonkProof(BaseModel):
    """PLONK / KZG polynomial commitment proof."""
    model_config = ConfigDict(protected_namespaces=(), populate_by_name=True)

    wire_commitments: List[EllipticCurvePoint] = Field(default_factory=list, description="Wire commitments a(X), b(X), c(X)")
    grand_product_z: EllipticCurvePoint = Field(..., description="Grand product copy constraint permutation commitment")
    quotient_split_t: List[EllipticCurvePoint] = Field(default_factory=list, description="Quotient polynomial split commitments")
    kzg_opening_proof: EllipticCurvePoint = Field(..., description="KZG opening evaluation proof W_z in G1")
    proof_size_bytes: int = Field(default=576, description="Serialized PLONK-KZG proof size in bytes")


class ZKProofInstance(BaseModel):
    """Public instance data known to the verifier."""
    model_config = ConfigDict(protected_namespaces=(), populate_by_name=True)

    case_id_hash: str = Field(..., description="Hex SHA-256 / Blake3 hash of forensic case metadata")
    claimed_lr_threshold: float = Field(..., ge=0.0, description="Claimed Likelihood Ratio threshold (e.g. M_thresh = 1e6)")
    claimed_lr_threshold_quantized: Union[int, float, str] = Field(..., description="Scaled integer representation floor(M_thresh * 2^S)")
    merkle_root: str = Field(..., description="Hex 32-byte Merkle root of reference allele database")
    locus_count: int = Field(default=24, ge=1, le=100, description="Number of evaluated forensic loci")
    scale_s: int = Field(default=16, description="Fixed-point scaling factor used in circuit")


class ZKWitnessData(BaseModel):
    """Private witness data known strictly to the prover."""
    model_config = ConfigDict(protected_namespaces=(), populate_by_name=True)

    sample_id: str = Field(..., description="Confidential forensic sample identifier")
    suspect_genotypes: Dict[str, Tuple[float, float]] = Field(..., description="Private suspect allele calls per locus")
    evidence_peak_heights: Dict[str, Dict[float, float]] = Field(..., description="Electropherogram RFU peak heights per locus")
    true_likelihood_ratio: float = Field(..., ge=0.0, description="Computed continuous Likelihood Ratio")
    numerator_quantized: Union[int, float, str] = Field(..., description="Quantized numerator N_hat")
    denominator_quantized: Union[int, float, str] = Field(..., description="Quantized denominator D_hat")
    quotient_advice: Union[int, float, str] = Field(..., description="Non-deterministic quotient advice LR_hat")
    remainder_advice: Union[int, float, str] = Field(..., description="Non-deterministic remainder advice r")



class ZKVerificationResult(BaseModel):
    """Formal verification verdict of a zero-knowledge proof."""
    model_config = ConfigDict(protected_namespaces=(), populate_by_name=True)

    is_valid: bool = Field(..., description="True if proof satisfies all algebraic pairing and range constraints")
    proving_system: ProvingSystemType = Field(...)
    curve: EllipticCurveGroup = Field(default=EllipticCurveGroup.BN254)
    pairing_residual_verified: bool = Field(..., description="Pairing equality check confirmation")
    range_checks_passed: bool = Field(..., description="All remainder and quotient range constraints passed")
    claimed_threshold_satisfied: bool = Field(..., description="Confirms LR_hat >= M_thresh_hat without privacy leakage")
    verification_latency_ms: float = Field(..., ge=0.0, description="Verification latency in milliseconds")
    audit_hash: str = Field(..., description="Immutable HMAC-SHA256 hash of verification transaction")
    enfsi_tier: str = Field(..., description="ENFSI 2017 verbal reporting level (e.g. Tier 6: Extremely Strong Support)")


class SMTSoundnessReport(BaseModel):
    """Formal SMT-based circuit soundness verification report."""
    model_config = ConfigDict(protected_namespaces=(), populate_by_name=True)

    circuit_name: str = Field(..., description="Name/identifier of audited arithmetic circuit")
    is_sound: bool = Field(..., description="True if circuit is proven strictly free of under-constrained signals")
    uniqueness_verified: bool = Field(..., description="Output and intermediate signals are uniquely determined by inputs")
    unconstrained_signals: List[str] = Field(default_factory=list, description="List of detected under-constrained signal names (if any)")
    false_match_vulnerability_detected: bool = Field(default=False)
    solver_used: str = Field(default="Z3 / QED2 SMT Solver")
    audit_timestamp: str = Field(...)


class CeremonyParticipant(BaseModel):
    """Participant record in 1-of-N MPC Trusted Setup."""
    model_config = ConfigDict(protected_namespaces=(), populate_by_name=True)

    participant_id: str = Field(...)
    contribution_index: int = Field(..., ge=1)
    accumulator_hash: str = Field(..., description="SHA-256 hash of updated [tau^j] accumulator")
    dlog_proof_of_knowledge: str = Field(..., description="Zero-knowledge proof of exponent knowledge")
    verified: bool = Field(default=True)


class CeremonyTranscript(BaseModel):
    """Complete cryptographic transcript of 1-of-N MPC Trusted Setup."""
    model_config = ConfigDict(protected_namespaces=(), populate_by_name=True)

    ceremony_name: str = Field(..., description="e.g. Perpetual Powers of Tau / Hermez Phase 1")
    max_degree: int = Field(default=268435456, description="Maximum supported polynomial degree (e.g. 2^28)")
    participant_count: int = Field(..., ge=1)
    participants: List[CeremonyParticipant] = Field(default_factory=list)
    final_srs_hash: str = Field(..., description="Cryptographic root hash of finalized public parameters")
    is_transcript_valid: bool = Field(..., description="True if whole hash chain and dlog proofs verify")
