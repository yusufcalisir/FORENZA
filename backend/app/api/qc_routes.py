from fastapi import APIRouter, HTTPException, status
from backend.app.api.qc_schemas import EvaluateQcRequest, EvaluateQcResponse
from backend.node.services.forensic.qc.qc_engine import QualityAssuranceEngine

router = APIRouter(prefix="/forensic/qc", tags=["Forensic QA/QC Gatekeeper"])
_QC = QualityAssuranceEngine()


@router.post(
    "/evaluate-profile",
    response_model=EvaluateQcResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate genetic evidence QA/QC metrics and assign ISO 17025 verdict",
    description="Evaluates negative control integrity, positive control concordance, heterozygote balance (Hb), and stochastic thresholds."
)
async def evaluate_profile_qc(req: EvaluateQcRequest) -> EvaluateQcResponse:
    try:
        loci_dicts = None
        if req.loci_peaks:
            loci_dicts = [l.model_dump() for l in req.loci_peaks]

        res = _QC.evaluate_profile_qc(
            loci_peaks=loci_dicts,
            negative_control_max_rfu=req.negative_control_max_rfu,
            positive_control_concordant=req.positive_control_concordant,
            sample_id=req.sample_id,
        )
        return EvaluateQcResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"QA/QC evaluation error: {str(e)}")
