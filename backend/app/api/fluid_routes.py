"""
FORENZA Body Fluid Identification API Router.
Exposes endpoints for mRNA Gene Expression Biological Stain Identification
and Co-Extraction Audit under the /forensic/fluid prefix.
"""

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.fluid.profiler import BodyFluidProfiler, StainSampleData, MrnaMarkerExpression
from node.services.forensic.fluid.compatibility import RnaDnaCoExtractor
from .fluid_schemas import (
    FluidIdentifyRequest, FluidIdentifyResponse,
    CoExtractionAuditRequest, CoExtractionAuditResponse,
    BodyFluidProbabilitySchema
)

router = APIRouter(prefix="/forensic/fluid", tags=["Body Fluid Identification & mRNA Profiling"])

_fluid_profiler = BodyFluidProfiler()
_coextractor = RnaDnaCoExtractor()


@router.post(
    "/identify",
    response_model=FluidIdentifyResponse,
    summary="mRNA Biological Body Fluid Identification",
    description="Identifies biological stain origin (Venous Blood, Semen, Saliva, Vaginal Secretions, Menstrual Blood, Urine) from mRNA expression profiles.",
    status_code=status.HTTP_200_OK,
)
async def identify_biological_fluid(body: FluidIdentifyRequest) -> FluidIdentifyResponse:
    try:
        sample_dom = StainSampleData(
            sample_id=body.sample.sample_id,
            mrna_expressions=[
                MrnaMarkerExpression(m.gene_symbol, m.expression_rfu)
                for m in body.sample.mrna_expressions
            ]
        )
        res = _fluid_profiler.identify_body_fluid(sample_dom)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Body fluid identification failed: {str(exc)}"
        )

    return FluidIdentifyResponse(
        sample_id=res.sample_id,
        top_predicted_fluid=res.top_predicted_fluid,
        fluid_probabilities=[
            BodyFluidProbabilitySchema(
                fluid_type=p.fluid_type,
                probability=p.probability,
                primary_markers=p.primary_markers
            )
            for p in res.fluid_probabilities
        ],
        identification_summary=res.identification_summary
    )


@router.post(
    "/co-extraction-audit",
    response_model=CoExtractionAuditResponse,
    summary="RNA/DNA Co-Extraction Audit",
    description="Audits RNA yield and RIN integrity score for STR co-extraction compatibility.",
    status_code=status.HTTP_200_OK,
)
async def audit_co_extraction(body: CoExtractionAuditRequest) -> CoExtractionAuditResponse:
    try:
        res = _coextractor.audit_co_extraction(
            body.sample_id, body.rna_yield_ng_per_ul, body.rin_integrity_score
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Co-extraction audit failed: {str(exc)}"
        )

    return CoExtractionAuditResponse(
        sample_id=res.sample_id,
        rna_yield_ng_per_ul=res.rna_yield_ng_per_ul,
        rin_integrity_score=res.rin_integrity_score,
        str_co_extraction_compatible=res.str_co_extraction_compatible,
        recommended_strategy=res.recommended_strategy,
        audit_summary=res.audit_summary
    )
