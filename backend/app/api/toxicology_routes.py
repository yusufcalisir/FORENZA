"""
FORENZA Forensic Toxicology API Router.
Exposes endpoints for Quantitative Drug Screening (ISO 17025 Measurement Uncertainty)
and Ethanol Widmark Pharmacokinetics / PMR Auditing under the /forensic/toxicology prefix.
"""

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.toxicology.classifier import ForensicToxicologyEngine, ToxicologicalAnalyte
from node.services.forensic.toxicology.pharmacokinetics import EthanolWidmarkAuditor
from .toxicology_schemas import (
    ToxicologyScreenRequest, ToxicologyScreenResponse,
    WidmarkBacRequest, WidmarkBacResponse,
    AnalyteReportSchema
)

router = APIRouter(prefix="/forensic/toxicology", tags=["Forensic Toxicology & Pharmacokinetics"])

_tox_engine = ForensicToxicologyEngine()
_widmark_auditor = EthanolWidmarkAuditor()


@router.post(
    "/screen",
    response_model=ToxicologyScreenResponse,
    summary="Quantitative Drug & Metabolite Screening",
    description="Evaluates analyte concentrations against reference toxicological ranges (Therapeutic, Toxic, Fatal) with ISO 17025 expanded measurement uncertainty.",
    status_code=status.HTTP_200_OK,
)
async def screen_toxicological_analytes(body: ToxicologyScreenRequest) -> ToxicologyScreenResponse:
    try:
        analytes_dom = [
            ToxicologicalAnalyte(
                analyte_name=a.analyte_name,
                matrix_type=a.matrix_type,
                measured_concentration=a.measured_concentration,
                unit=a.unit,
                u_cal_rel=a.u_cal_rel if a.u_cal_rel is not None else 0.03,
                u_rep_rel=a.u_rep_rel if a.u_rep_rel is not None else 0.04,
                u_matrix_rel=a.u_matrix_rel if a.u_matrix_rel is not None else 0.02,
            )
            for a in body.analytes
        ]
        res = _tox_engine.screen_analytes(body.sample_id, analytes_dom)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Toxicological screening failed: {str(exc)}"
        )

    return ToxicologyScreenResponse(
        sample_id=res.sample_id,
        analyte_reports=[
            AnalyteReportSchema(
                analyte_name=r.analyte_name,
                matrix_type=r.matrix_type,
                measured_concentration=r.measured_concentration,
                expanded_uncertainty_95=r.expanded_uncertainty_95,
                concentration_formatted=r.concentration_formatted,
                toxicological_classification=r.toxicological_classification,
                reference_range_description=r.reference_range_description
            )
            for r in res.analyte_reports
        ],
        toxicology_summary=res.toxicology_summary
    )


@router.post(
    "/bac-widmark",
    response_model=WidmarkBacResponse,
    summary="Ethanol Widmark BAC Pharmacokinetics & PMR Audit",
    description="Models Blood Alcohol Concentration clearance over time and audits Postmortem Redistribution (PMR) ratio.",
    status_code=status.HTTP_200_OK,
)
async def calculate_widmark_bac(body: WidmarkBacRequest) -> WidmarkBacResponse:
    try:
        res = _widmark_auditor.calculate_widmark_bac(
            sample_id=body.sample_id,
            bac_initial=body.bac_initial_g_per_dl,
            elapsed_hours=body.elapsed_hours,
            beta=body.elimination_rate_beta if body.elimination_rate_beta is not None else 0.015,
            c_cardiac=body.c_cardiac,
            c_peripheral=body.c_peripheral
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Widmark BAC calculation failed: {str(exc)}"
        )

    return WidmarkBacResponse(
        sample_id=res.sample_id,
        bac_initial_g_per_dl=res.bac_initial_g_per_dl,
        elapsed_hours=res.elapsed_hours,
        elimination_rate_beta=res.elimination_rate_beta,
        bac_current_g_per_dl=res.bac_current_g_per_dl,
        time_to_sobriety_hours=res.time_to_sobriety_hours,
        pmr_ratio=res.pmr_ratio,
        pmr_interpretation=res.pmr_interpretation,
        widmark_summary=res.widmark_summary
    )
