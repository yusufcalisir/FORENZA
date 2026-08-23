"""
FORENZA Evidence Image Analysis & BPA API Router.
Exposes endpoints for Stain Morphometry Analysis (arcsin W/L impact angle) and Human Analyst Verification Sign-off
under the /forensic/bpa prefix.
"""

import time
from fastapi import APIRouter, HTTPException, status

from node.services.forensic.bpa.analyzer import BloodstainPatternAnalyzer
from .bpa_schemas import (
    AnalyzeStainRequest, AnalyzeStainResponse,
    VerifyAnalystRequest,
    BloodstainMorphometrySchema, AnalystVerificationSchema
)

router = APIRouter(prefix="/forensic/bpa", tags=["Evidence Image Analysis & BPA"])

_bpa_analyzer = BloodstainPatternAnalyzer()


@router.post(
    "/analyze-stain",
    response_model=AnalyzeStainResponse,
    summary="Analyze Bloodstain Morphometry & Impact Angle",
    description="Calculates stain minor/major axis morphometry, trigonometric impact angle (alpha = arcsin(W/L)), and initial pattern classification.",
    status_code=status.HTTP_200_OK,
)
async def analyze_stain(body: AnalyzeStainRequest) -> AnalyzeStainResponse:
    try:
        res = _bpa_analyzer.analyze_stain(body.stain_id, body.width_mm, body.length_mm)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"BPA stain morphometry analysis failed: {str(exc)}"
        )

    return AnalyzeStainResponse(
        stain_id=res.stain_id,
        morphometry=BloodstainMorphometrySchema(
            stain_id=res.morphometry.stain_id,
            width_mm=res.morphometry.width_mm,
            length_mm=res.morphometry.length_mm,
            ellipse_aspect_ratio=res.morphometry.ellipse_aspect_ratio,
            impact_angle_deg=res.morphometry.impact_angle_deg
        ),
        predicted_pattern=res.predicted_pattern,
        review_status=res.review_status,
        verification_record=None,
        bpa_summary=res.bpa_summary
    )


@router.post(
    "/verify-analyst",
    response_model=AnalyzeStainResponse,
    summary="Human Analyst Verification & Certification Sign-Off",
    description="Records human analyst verification decision, notes, and digital sign-off for BPA pattern classification.",
    status_code=status.HTTP_200_OK,
)
async def verify_analyst(body: VerifyAnalystRequest) -> AnalyzeStainResponse:
    try:
        initial_res = _bpa_analyzer.analyze_stain(body.stain_id, body.width_mm, body.length_mm)
        now = time.time()
        certified_res = _bpa_analyzer.verify_analysis(
            analysis_result=initial_res,
            analyst_id=body.analyst_id,
            decision=body.decision,
            final_pattern=body.final_pattern,
            analyst_notes=body.analyst_notes,
            timestamp_utc=now
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Analyst verification sign-off failed: {str(exc)}"
        )

    vr = certified_res.verification_record
    vr_schema = AnalystVerificationSchema(
        analyst_id=vr.analyst_id,
        verification_timestamp_utc=vr.verification_timestamp_utc,
        decision=vr.decision,
        final_pattern_classification=vr.final_pattern_classification,
        analyst_notes=vr.analyst_notes
    ) if vr else None

    return AnalyzeStainResponse(
        stain_id=certified_res.stain_id,
        morphometry=BloodstainMorphometrySchema(
            stain_id=certified_res.morphometry.stain_id,
            width_mm=certified_res.morphometry.width_mm,
            length_mm=certified_res.morphometry.length_mm,
            ellipse_aspect_ratio=certified_res.morphometry.ellipse_aspect_ratio,
            impact_angle_deg=certified_res.morphometry.impact_angle_deg
        ),
        predicted_pattern=certified_res.predicted_pattern,
        review_status=certified_res.review_status,
        verification_record=vr_schema,
        bpa_summary=certified_res.bpa_summary
    )
