from fastapi import APIRouter, HTTPException, status
from backend.app.api.review_schemas import SubmitReviewRequest, SubmitReviewResponse, GetReviewAuditResponse
from backend.node.services.forensic.review.human_review_engine import HumanReviewEngine

router = APIRouter(prefix="/forensic/review", tags=["Human Analyst Review & Governance"])
_REVIEW = HumanReviewEngine()


@router.post(
    "/submit-decision",
    response_model=SubmitReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit human analyst review decision with dual sign-off & override rationale logging",
)
async def submit_analyst_decision(req: SubmitReviewRequest) -> SubmitReviewResponse:
    try:
        res = _REVIEW.submit_analyst_decision(
            sample_id=req.sample_id,
            ai_recommendation=req.ai_recommendation,
            human_decision=req.human_decision,
            primary_analyst_id=req.primary_analyst_id,
            technical_reviewer_id=req.technical_reviewer_id,
            override_reason=req.override_reason,
            final_verdict=req.final_verdict,
        )
        return SubmitReviewResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Human review submission error: {str(e)}")


@router.get(
    "/audit-history/{sample_id}",
    response_model=GetReviewAuditResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve review decision audit history and verify HMAC hash chain integrity",
)
async def get_audit_history(sample_id: str) -> GetReviewAuditResponse:
    try:
        res = _REVIEW.get_audit_history(sample_id=sample_id)
        return GetReviewAuditResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
