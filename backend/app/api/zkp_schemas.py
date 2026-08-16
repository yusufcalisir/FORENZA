from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class WitnessCommitmentRequest(BaseModel):
    loci_alleles: Dict[str, List[float]] = Field(
        ...,
        description="Private witness genotype STR alleles by locus name."
    )
    salt_hex: Optional[str] = Field(
        default=None,
        description="Optional 256-bit hexadecimal cryptographic salt."
    )


class WitnessCommitmentResponse(BaseModel):
    commitment_hex: str
    commitment_field_int: str
    salt_hex: str
    total_loci: int
    total_alleles: int


class SynthesizeZkProofRequest(BaseModel):
    suspect_loci: Dict[str, List[float]] = Field(
        ...,
        description="Suspect STR alleles by locus."
    )
    evidence_loci: Dict[str, List[float]] = Field(
        ...,
        description="Evidentiary STR alleles by locus."
    )
    match_threshold: int = Field(
        default=40,
        ge=1,
        description="Minimum number of matching alleles required."
    )
    suspect_salt_hex: Optional[str] = Field(
        default=None,
        description="Optional salt for suspect witness commitment."
    )
    evidence_salt_hex: Optional[str] = Field(
        default=None,
        description="Optional salt for evidence commitment."
    )


class Groth16ProofPayload(BaseModel):
    pi_a: List[str]
    pi_b: List[List[str]]
    pi_c: List[str]
    protocol: str = "groth16"
    curve: str = "bn254"


class SynthesizeZkProofResponse(BaseModel):
    proof: Groth16ProofPayload
    public_signals: List[str]
    evidence_commitment: str
    suspect_commitment: str
    match_threshold: int
    soundness_error: str


class VerifyPairingProofRequest(BaseModel):
    proof: Groth16ProofPayload = Field(..., description="Groth16 G1/G2 proof coordinates.")
    public_signals: List[str] = Field(..., min_length=3, description="Public signals: [H(G_E), M_thresh, H(G_S)].")


class VerifyPairingProofResponse(BaseModel):
    is_valid: bool
    verdict: str
    soundness_bound: str
    evaluated_public_signals: Optional[Dict[str, Any]] = None
    prosecutors_fallacy_shield: str
