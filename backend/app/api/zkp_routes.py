from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from backend.app.api.zkp_schemas import (
    WitnessCommitmentRequest,
    WitnessCommitmentResponse,
    SynthesizeZkProofRequest,
    SynthesizeZkProofResponse,
    VerifyPairingProofRequest,
    VerifyPairingProofResponse,
)
from backend.node.services.forensic.security.zkp_auditor_engine import (
    ZkpBlindAuditorEngine,
    GenotypeWitness,
)

router = APIRouter(prefix="/forensic/zkp", tags=["ZKP Blind Forensic Auditor (Pillar 6 §2)"])
_ZKP_ENGINE = ZkpBlindAuditorEngine()


@router.post(
    "/witness-commitment",
    response_model=WitnessCommitmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Compute Poseidon Commitment for Private Genotype Witness",
    description="Synthesizes Poseidon hash H(G) = Poseidon(G || Salt) over BN254 scalar field to conceal raw alleles."
)
async def compute_witness_commitment(req: WitnessCommitmentRequest) -> WitnessCommitmentResponse:
    try:
        res = _ZKP_ENGINE.compute_poseidon_commitment(
            loci_alleles=req.loci_alleles,
            salt_hex=req.salt_hex,
        )
        return WitnessCommitmentResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Witness commitment error: {str(e)}")


@router.post(
    "/synthesize-proof",
    response_model=SynthesizeZkProofResponse,
    status_code=status.HTTP_200_OK,
    summary="Synthesize Groth16 zk-SNARK STR Match Proof",
    description="Evaluates R1CS locus equality gadgets and threshold score, producing BN254 G1/G2 proof coordinates."
)
async def synthesize_zkp_proof(req: SynthesizeZkProofRequest) -> SynthesizeZkProofResponse:
    try:
        witness = GenotypeWitness(
            loci_alleles=req.suspect_loci,
            salt_hex=req.suspect_salt_hex,
        )
        res = _ZKP_ENGINE.synthesize_groth16_proof(
            suspect_witness=witness,
            evidence_alleles=req.evidence_loci,
            match_threshold=req.match_threshold,
            evidence_salt_hex=req.evidence_salt_hex,
        )
        return SynthesizeZkProofResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Proof synthesis error: {str(e)}")


@router.post(
    "/verify-pairing",
    response_model=VerifyPairingProofResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify Groth16 Bilinear Pairing on BN254 Curve",
    description="Evaluates e(A, B) * e(-alpha, beta) * e(-sum x_i K_i, gamma) * e(-C, delta) = 1_GT with soundness error < 10^-75."
)
async def verify_pairing_proof(req: VerifyPairingProofRequest) -> VerifyPairingProofResponse:
    try:
        res = _ZKP_ENGINE.verify_bilinear_pairing(
            proof=req.proof.model_dump(),
            public_signals=req.public_signals,
        )
        return VerifyPairingProofResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Pairing verification error: {str(e)}")
