from fastapi import APIRouter, HTTPException, status
from backend.app.api.qc_schemas import (
    EvaluateQcRequest,
    EvaluateQcResponse,
    CalculateUncertaintyBudgetRequest,
    CalculateUncertaintyBudgetResponse,
    ProficiencyZScoreRequest,
    ProficiencyZScoreResponse,
)
from backend.node.services.forensic.qc.qc_engine import QualityAssuranceEngine
from backend.node.services.forensic.qc.measurement_uncertainty_engine import (
    ForensicMeasurementUncertaintyEngine,
    UncertaintyComponent,
)

router = APIRouter(prefix="/forensic/qc", tags=["Forensic QA/QC Gatekeeper"])
_QC = QualityAssuranceEngine()
_UNCERT = ForensicMeasurementUncertaintyEngine()


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


# ── ISO/IEC 17025:2017 Measurement Uncertainty Endpoints (Pillar 6 §3) ───────

@router.post(
    "/uncertainty/calculate-budget",
    response_model=CalculateUncertaintyBudgetResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate GUM Combined and Expanded Measurement Uncertainty Budget",
    description="Computes u_c and U_95% (k=2.00) over 4-component calibration budget (pipet, thermal, qPCR, master mix)."
)
async def calculate_uncertainty_budget(req: CalculateUncertaintyBudgetRequest) -> CalculateUncertaintyBudgetResponse:
    try:
        components = None
        if req.components:
            components = [
                UncertaintyComponent(
                    name=c.name,
                    standard_uncertainty=c.standard_uncertainty,
                    probability_distribution=c.probability_distribution,
                    sensitivity_coefficient=c.sensitivity_coefficient,
                    description=c.description,
                )
                for c in req.components
            ]

        res = _UNCERT.calculate_uncertainty_budget(
            nominal_concentration=req.nominal_concentration,
            components=components,
            correlations=req.correlations,
            coverage_factor=req.coverage_factor,
        )
        return CalculateUncertaintyBudgetResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Uncertainty budget calculation error: {str(e)}")


@router.post(
    "/uncertainty/proficiency-z-score",
    response_model=ProficiencyZScoreResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Laboratory Proficiency Testing Consensus z-Score",
    description="Classifies lab performance into SATISFACTORY (|z|<=2.0), QUESTIONABLE, or UNSATISFACTORY (|z|>=3.0)."
)
async def evaluate_proficiency_z_score(req: ProficiencyZScoreRequest) -> ProficiencyZScoreResponse:
    try:
        res = _UNCERT.evaluate_proficiency_z_score(
            lab_measured_value=req.lab_measured_value,
            consensus_mean=req.consensus_mean,
            consensus_std=req.consensus_std,
        )
        return ProficiencyZScoreResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Proficiency z-score evaluation error: {str(e)}")

