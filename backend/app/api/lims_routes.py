from fastapi import APIRouter, HTTPException, status
from backend.app.api.lims_schemas import (
    CreateCaseRequest,
    CreateCaseResponse,
    AccessionSampleRequest,
    AccessionSampleResponse,
    RecordWorkflowStepRequest,
    RecordWorkflowStepResponse,
    ChainOfCustodyResponse,
    MerkleBuildTreeRequest,
    MerkleBuildTreeResponse,
    MerkleGenerateProofRequest,
    MerkleGenerateProofResponse,
    MerkleVerifyProofRequest,
    MerkleVerifyProofResponse,
)
from backend.node.services.forensic.lims.workflow_tracker import LimsWorkflowTracker
from backend.node.services.forensic.lims.merkle_ledger_engine import ForensicMerkleLedgerEngine, CustodyEvent

router = APIRouter(prefix="/forensic/lims", tags=["LIMS-Lite Sample Accessioning & Workflow"])
_LIMS = LimsWorkflowTracker()
_MERKLE = ForensicMerkleLedgerEngine()


@router.post(
    "/case/create",
    response_model=CreateCaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new forensic case in LIMS",
)
async def create_case(req: CreateCaseRequest) -> CreateCaseResponse:
    try:
        res = _LIMS.create_case(
            case_id=req.case_id,
            investigator_name=req.investigator_name,
            jurisdiction=req.jurisdiction,
        )
        return CreateCaseResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/sample/accession",
    response_model=AccessionSampleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Accession a biological evidence sample under a registered case",
)
async def accession_sample(req: AccessionSampleRequest) -> AccessionSampleResponse:
    try:
        res = _LIMS.accession_sample(
            case_id=req.case_id,
            sample_id=req.sample_id,
            evidence_type=req.evidence_type,
            collector_name=req.collector_name,
        )
        return AccessionSampleResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/workflow/step",
    response_model=RecordWorkflowStepResponse,
    status_code=status.HTTP_200_OK,
    summary="Record analytical workflow step with HMAC audit signature & reagent lot",
)
async def record_workflow_step(req: RecordWorkflowStepRequest) -> RecordWorkflowStepResponse:
    try:
        res = _LIMS.record_workflow_step(
            sample_id=req.sample_id,
            step_name=req.step_name,
            operator_id=req.operator_id,
            instrument_id=req.instrument_id,
            reagent_lot=req.reagent_lot,
            protocol_version=req.protocol_version,
            step_result=req.step_result,
            pass_qc=req.pass_qc,
        )
        return RecordWorkflowStepResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/chain-of-custody/{sample_id}",
    response_model=ChainOfCustodyResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve chain of custody history and verify HMAC hash chain integrity",
)
async def get_chain_of_custody(sample_id: str) -> ChainOfCustodyResponse:
    try:
        res = _LIMS.get_chain_of_custody(sample_id=sample_id)
        return ChainOfCustodyResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ── Cryptographic Merkle Tree Ledger Endpoints (Pillar 6 §1) ─────────────────

@router.post(
    "/merkle/build-tree",
    response_model=MerkleBuildTreeResponse,
    status_code=status.HTTP_200_OK,
    summary="Build Cryptographic Binary Merkle Tree Over Custody Events",
    description="Chains custody events via SHA-256 leaves, performs pairwise balanced reduction, and computes root commitment."
)
async def build_merkle_tree(req: MerkleBuildTreeRequest) -> MerkleBuildTreeResponse:
    try:
        events = [
            CustodyEvent(
                event_id=e.event_id,
                timestamp_iso=e.timestamp_iso,
                officer_id=e.officer_id,
                sample_barcode=e.sample_barcode,
                location_id=e.location_id,
                action_type=e.action_type,
                notes=e.notes,
            )
            for e in req.events
        ]
        res = _MERKLE.build_merkle_tree(events)
        return MerkleBuildTreeResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Merkle tree build error: {str(e)}")


@router.post(
    "/merkle/generate-proof",
    response_model=MerkleGenerateProofResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate O(log2 N) Merkle Inclusion Proof (Audit Path)",
    description="Generates minimal cryptographic sibling audit path for courtroom evidence inclusion verification."
)
async def generate_merkle_proof(req: MerkleGenerateProofRequest) -> MerkleGenerateProofResponse:
    try:
        events = [
            CustodyEvent(
                event_id=e.event_id,
                timestamp_iso=e.timestamp_iso,
                officer_id=e.officer_id,
                sample_barcode=e.sample_barcode,
                location_id=e.location_id,
                action_type=e.action_type,
                notes=e.notes,
            )
            for e in req.events
        ]
        res = _MERKLE.generate_inclusion_proof(events, req.target_event_index)
        return MerkleGenerateProofResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Merkle proof generation error: {str(e)}")


@router.post(
    "/merkle/verify-proof",
    response_model=MerkleVerifyProofResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify Merkle Inclusion Proof Integrity",
    description="Reconstructs root from leaf hash and sibling path to evaluate evidence authenticity and detect tampering."
)
async def verify_merkle_proof(req: MerkleVerifyProofRequest) -> MerkleVerifyProofResponse:
    try:
        steps_dict = [{"sibling_hash": s.sibling_hash, "direction": s.direction} for s in req.proof_path]
        res = _MERKLE.verify_inclusion_proof(
            leaf_hash=req.leaf_hash,
            proof_path=steps_dict,
            expected_root=req.expected_root,
        )
        return MerkleVerifyProofResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Merkle proof verification error: {str(e)}")

