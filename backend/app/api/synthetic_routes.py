from fastapi import APIRouter, HTTPException, status
from backend.app.api.synthetic_schemas import (
    GenerateSyntheticCaseRequest, GenerateSyntheticCaseResponse,
    EvaluateBenchmarkRequest, EvaluateBenchmarkResponse
)
from backend.node.services.forensic.synthetic.synthetic_case_engine import SyntheticCaseEngine

router = APIRouter(prefix="/forensic/synthetic", tags=["Synthetic Forensic Case Generator"])
_ENGINE = SyntheticCaseEngine()


@router.post(
    "/generate-case",
    response_model=GenerateSyntheticCaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate synthetic forensic case scenario with 100% ground truth",
    description="Synthesizes multi-person mixtures, true contributor profiles, degradation, dropout, and ground-truth metrics for academic validation."
)
async def generate_synthetic_case(req: GenerateSyntheticCaseRequest) -> GenerateSyntheticCaseResponse:
    try:
        res = _ENGINE.generate_synthetic_case(
            scenario_type=req.scenario_type,
            num_contributors=req.num_contributors,
            degradation_factor=req.degradation_factor,
            dropout_probability=req.dropout_probability,
        )
        return GenerateSyntheticCaseResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Synthetic case generation error: {str(e)}")


@router.post(
    "/evaluate-benchmark",
    response_model=EvaluateBenchmarkResponse,
    status_code=status.HTTP_200_OK,
    summary="Run automated self-testing benchmark against ground truth",
)
async def evaluate_benchmark(req: EvaluateBenchmarkRequest) -> EvaluateBenchmarkResponse:
    try:
        res = _ENGINE.evaluate_benchmark(
            synthetic_case_id=req.synthetic_case_id,
            engine_calculated_log10_lr=req.engine_calculated_log10_lr,
        )
        return EvaluateBenchmarkResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Benchmark evaluation error: {str(e)}")
