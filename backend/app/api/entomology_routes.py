"""
FORENZA Forensic Entomology API Router.
Exposes endpoints for Minimum Postmortem Interval (PMI_min) calculation via ADH thermal models
and Insect Succession Auditing under the /forensic/entomology prefix.
"""

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.entomology.pmi import EntomologyPmiEstimator
from node.services.forensic.entomology.succession import InsectSuccessionAuditor, ArthropodOccurrence
from .entomology_schemas import (
    EntomologyPmiRequest, EntomologyPmiResponse,
    SuccessionAuditRequest, SuccessionAuditResponse
)

router = APIRouter(prefix="/forensic/entomology", tags=["Forensic Entomology & PMI Estimation"])

_pmi_estimator = EntomologyPmiEstimator()
_succession_auditor = InsectSuccessionAuditor()


@router.post(
    "/pmi",
    response_model=EntomologyPmiResponse,
    summary="Minimum Postmortem Interval (PMI_min) Estimation",
    description="Calculates minimum elapsed time since colonization using Accumulated Degree Hours (ADH) thermal development models.",
    status_code=status.HTTP_200_OK,
)
async def estimate_entomology_pmi(body: EntomologyPmiRequest) -> EntomologyPmiResponse:
    try:
        res = _pmi_estimator.estimate_pmi(
            species_name=body.species_name,
            stage=body.development_stage,
            mean_ambient_temp_celsius=body.mean_ambient_temp_celsius
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Entomology PMI estimation failed: {str(exc)}"
        )

    return EntomologyPmiResponse(
        species_name=res.species_name,
        development_stage=res.development_stage,
        mean_ambient_temp_celsius=res.mean_ambient_temp_celsius,
        effective_temp_celsius=res.effective_temp_celsius,
        required_adh=res.required_adh,
        estimated_pmi_hours=res.estimated_pmi_hours,
        estimated_pmi_days=res.estimated_pmi_days,
        pmi_formatted_range=res.pmi_formatted_range,
        entomology_summary=res.entomology_summary
    )


@router.post(
    "/succession",
    response_model=SuccessionAuditResponse,
    summary="Arthropod Succession Wave Audit",
    description="Audits arthropod community waves to infer decomposition stage and time window.",
    status_code=status.HTTP_200_OK,
)
async def audit_arthropod_succession(body: SuccessionAuditRequest) -> SuccessionAuditResponse:
    try:
        occ = [
            ArthropodOccurrence(o.family_name, o.species_observed, o.abundance_score)
            for o in body.occurrences
        ]
        res = _succession_auditor.audit_succession_wave(body.sample_id, occ)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Succession audit failed: {str(exc)}"
        )

    return SuccessionAuditResponse(
        sample_id=res.sample_id,
        inferred_decomposition_stage=res.inferred_decomposition_stage,
        typical_timeframe_days=res.typical_timeframe_days,
        observed_families=res.observed_families,
        succession_summary=res.succession_summary
    )
