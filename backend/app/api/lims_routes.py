from fastapi import APIRouter, HTTPException, status
from backend.app.api.lims_schemas import (
    CreateCaseRequest,
    CreateCaseResponse,
    AccessionSampleRequest,
    AccessionSampleResponse,
    RecordWorkflowStepRequest,
    RecordWorkflowStepResponse,
    ChainOfCustodyResponse,
)
from backend.node.services.forensic.lims.workflow_tracker import LimsWorkflowTracker

router = APIRouter(prefix="/forensic/lims", tags=["LIMS-Lite Sample Accessioning & Workflow"])
_LIMS = LimsWorkflowTracker()


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
