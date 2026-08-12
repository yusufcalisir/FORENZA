from fastapi import APIRouter, HTTPException, status
from backend.app.api.epigenetics_schemas import PredictAgeRequest, PredictAgeResponse
from backend.node.services.forensic.epigenetics.age_engine import EpigeneticClockEngine

router = APIRouter(prefix="/forensic/epigenetics", tags=["Forensic Epigenetics & Age Estimation"])
_AGE_ENGINE = EpigeneticClockEngine()


@router.post(
    "/predict-age",
    response_model=PredictAgeResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict chronological age from CpG methylation ratios with 95% prediction interval",
    description="Applies ElasticNet multivariate regression over CpG site methylation ratios (ELOVL2, FHL2, TRIM59, KLF14, MIR29B2CHG), applies tissue intercept calibration, and computes ISO 17025 95% prediction intervals."
)
async def predict_age(req: PredictAgeRequest) -> PredictAgeResponse:
    try:
        result = _AGE_ENGINE.predict_age(
            cpg_methylation=req.cpg_methylation,
            tissue_type=req.tissue_type,
            chronological_age_known=req.chronological_age_known
        )
        return PredictAgeResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Epigenetic age prediction error: {str(e)}"
        )
