from fastapi import APIRouter, HTTPException, status
from backend.app.api.court_schemas import GenerateCourtTestimonyRequest, GenerateCourtTestimonyResponse
from backend.node.services.forensic.court.expert_witness_engine import ExpertWitnessEngine

router = APIRouter(prefix="/forensic/court", tags=["Expert Witness & Judicial Examination Subsystem"])
_ENGINE = ExpertWitnessEngine()


@router.post(
    "/generate-testimony-brief",
    response_model=GenerateCourtTestimonyResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate 7-point judicial testimony brief for expert witness cross-examination",
    description="Transforms bioinformatic results into a structured 7-point testimony brief with Transposed Conditional Fallacy protection."
)
async def generate_testimony_brief(req: GenerateCourtTestimonyRequest) -> GenerateCourtTestimonyResponse:
    try:
        res = _ENGINE.generate_testimony_brief(
            case_id=req.case_id,
            sample_id=req.sample_id,
            expert_witness_id=req.expert_witness_id,
            log10_lr=req.log10_lr,
            enfsi_verbal_predicate=req.enfsi_verbal_predicate,
            total_loci=req.total_loci,
            fst_correction=req.fst_correction,
            stochastic_threshold=req.stochastic_threshold,
        )
        return GenerateCourtTestimonyResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Expert witness testimony error: {str(e)}")
