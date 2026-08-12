from fastapi import APIRouter, HTTPException, status
from backend.app.api.iso_report_schemas import CompileIsoReportRequest, CompileIsoReportResponse
from backend.node.services.forensic.reports.iso_report_compiler import IsoReportCompiler

router = APIRouter(prefix="/forensic/reports", tags=["Court-Admissible ISO 17025 Forensic Report Generator"])
_COMPILER = IsoReportCompiler()


@router.post(
    "/compile-iso-certificate",
    response_model=CompileIsoReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Compile court-admissible 8-section ISO 17025 forensic certificate report",
    description="Enforces mathematical immutability over likelihood ratios and ENFSI scale predicates, compiling full LIMS provenance, measurement uncertainty U95%, and dual digital signatures."
)
async def compile_iso_certificate(req: CompileIsoReportRequest) -> CompileIsoReportResponse:
    try:
        res = _COMPILER.compile_iso_certificate(
            case_id=req.case_id,
            sample_id=req.sample_id,
            investigator_name=req.investigator_name,
            primary_analyst_id=req.primary_analyst_id,
            technical_reviewer_id=req.technical_reviewer_id,
            likelihood_ratio=req.likelihood_ratio,
            log10_lr=req.log10_lr,
            enfsi_verbal_predicate=req.enfsi_verbal_predicate,
            qc_verdict=req.qc_verdict,
            human_decision=req.human_decision,
            override_reason=req.override_reason,
        )
        return CompileIsoReportResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"ISO report compilation error: {str(e)}")
