from fastapi import APIRouter, HTTPException, status
from backend.app.api.evidence_os_schemas import (
    GetSystemArchitectureResponse, RunUnifiedOsPipelineRequest, RunUnifiedOsPipelineResponse
)
from backend.node.services.forensic.os.evidence_os_orchestrator import ForensicEvidenceOS

router = APIRouter(prefix="/forensic/os", tags=["Forensic Evidence OS Master Architecture"])
_OS = ForensicEvidenceOS()


@router.get(
    "/system-architecture",
    response_model=GetSystemArchitectureResponse,
    status_code=status.HTTP_200_OK,
    summary="Get FORENZA Forensic Evidence OS master system architecture topology",
)
async def get_system_architecture() -> GetSystemArchitectureResponse:
    try:
        res = _OS.get_system_architecture()
        return GetSystemArchitectureResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Architecture retrieval error: {str(e)}")


@router.post(
    "/run-unified-pipeline",
    response_model=RunUnifiedOsPipelineResponse,
    status_code=status.HTTP_200_OK,
    summary="Run end-to-end unified Forensic Evidence OS pipeline across all 6 layers",
)
async def run_unified_pipeline(req: RunUnifiedOsPipelineRequest) -> RunUnifiedOsPipelineResponse:
    try:
        res = _OS.run_unified_pipeline(
            case_id=req.case_id,
            sample_id=req.sample_id,
            primary_analyst=req.primary_analyst,
            technical_reviewer=req.technical_reviewer,
        )
        return RunUnifiedOsPipelineResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unified OS pipeline execution error: {str(e)}")
