from fastapi import APIRouter, HTTPException, status
from backend.app.api.court_schemas import (
    GenerateCourtTestimonyRequest,
    GenerateCourtTestimonyResponse,
    EvaluativeReportRequest,
    EvaluativeReportResponse,
    DaubertComplianceRequest,
    DaubertComplianceResponse,
)
from backend.node.services.forensic.court.expert_witness_engine import ExpertWitnessEngine
from backend.node.services.forensic.court.evaluative_reporting_engine import (
    DynamicEvaluativeReportingEngine,
)

router = APIRouter(prefix="/forensic/court", tags=["Expert Witness & Judicial Examination Subsystem"])
_TESTIMONY_ENGINE = ExpertWitnessEngine()
_REPORTING_ENGINE = DynamicEvaluativeReportingEngine()


@router.post(
    "/generate-testimony-brief",
    response_model=GenerateCourtTestimonyResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate 7-point judicial testimony brief for expert witness cross-examination",
    description="Transforms bioinformatic results into a structured 7-point testimony brief with Transposed Conditional Fallacy protection.",
)
async def generate_testimony_brief(req: GenerateCourtTestimonyRequest) -> GenerateCourtTestimonyResponse:
    try:
        res = _TESTIMONY_ENGINE.generate_testimony_brief(
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


@router.post(
    "/evaluative-report",
    response_model=EvaluativeReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate ENFSI (2017) 7-tier evaluative verbal scale statement",
    description=(
        "Translates numerical LR = P(E|H_p)/P(E|H_d) into a standardized ENFSI (2017) "
        "evaluative verbal statement (Tier 0 Neutral to Tier 6 Extremely Strong Support). "
        "Symmetrical defense evaluation for LR < 1.0. Bilingual: English & Turkish. "
        "Prosecutor's Fallacy Shield ACTIVE. (Research §4.1, §4.2, VECTOR_P6_03)"
    ),
)
async def evaluative_report(req: EvaluativeReportRequest) -> EvaluativeReportResponse:
    try:
        res = _REPORTING_ENGINE.generate_evaluative_report(
            likelihood_ratio=req.likelihood_ratio,
            hp_proposition=req.hp_proposition,
            hd_proposition=req.hd_proposition,
            language=req.language,
        )
        return EvaluativeReportResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Evaluative report error: {str(e)}")


@router.post(
    "/daubert-compliance",
    response_model=DaubertComplianceResponse,
    status_code=status.HTTP_200_OK,
    summary="Audit Daubert FRE 702 4-pillar and Frye general acceptance compliance",
    description=(
        "Evaluates statutory legal admissibility under Daubert (Federal Rule of Evidence 702) "
        "4-pillar criteria and Frye general acceptance standard. (Research §4.3)"
    ),
)
async def daubert_compliance(req: DaubertComplianceRequest) -> DaubertComplianceResponse:
    try:
        result = _REPORTING_ENGINE.audit_daubert_frye_compliance(
            error_rate=req.error_rate,
            has_peer_reviewed_algorithms=req.has_peer_reviewed_algorithms,
            swgdam_compliant=req.swgdam_compliant,
            iso17025_compliant=req.iso17025_compliant,
        )
        return DaubertComplianceResponse(
            pillar_1_falsifiability=result.pillar_1_falsifiability,
            pillar_2_error_rate=result.pillar_2_error_rate,
            pillar_3_peer_review=result.pillar_3_peer_review,
            pillar_4_standards=result.pillar_4_standards,
            frye_general_acceptance=result.frye_general_acceptance,
            overall_admissible=result.overall_admissible,
            error_rate_bound=result.error_rate_bound,
            prosecutor_fallacy_shield=result.prosecutor_fallacy_shield,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Daubert compliance audit error: {str(e)}")

