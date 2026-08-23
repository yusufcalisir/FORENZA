"""
FORENZA Forensic Anthropology API Router.
Exposes endpoints for Biological Profile Estimation (Sex, Age, Stature, Population Affinity)
and Skeletal Element Trauma Auditing under the /forensic/anthropology prefix.
"""

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.anthropology.profile import AnthropologyProfileEstimator, MorphometricMeasurements
from node.services.forensic.anthropology.trauma import SkeletalTraumaAuditor, TraumaObservation
from .anthropology_schemas import (
    BiologicalProfileRequest, BiologicalProfileResponse,
    TraumaAuditRequest, TraumaAuditResponse,
    TraumaObservationSchema
)

router = APIRouter(prefix="/forensic/anthropology", tags=["Forensic Anthropology & Biological Profiling"])

_profile_estimator = AnthropologyProfileEstimator()
_trauma_auditor = SkeletalTraumaAuditor()


@router.post(
    "/biological-profile",
    response_model=BiologicalProfileResponse,
    summary="Biological Profile Estimation",
    description="Estimates Sex, Age (Suchey-Brooks), Stature (Trotter-Gleser regression), and Population Affinity from osteological measurements.",
    status_code=status.HTTP_200_OK,
)
async def estimate_biological_profile(body: BiologicalProfileRequest) -> BiologicalProfileResponse:
    try:
        m = MorphometricMeasurements(
            femur_length_mm=body.measurements.femur_length_mm,
            tibia_length_mm=body.measurements.tibia_length_mm,
            pelvic_notch_score=body.measurements.pelvic_notch_score,
            subpubic_angle_deg=body.measurements.subpubic_angle_deg,
            pubic_symphysis_phase=body.measurements.pubic_symphysis_phase,
            cranial_breadth_mm=body.measurements.cranial_breadth_mm,
            cranial_length_mm=body.measurements.cranial_length_mm,
        )
        res = _profile_estimator.estimate_biological_profile(m)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Biological profile estimation failed: {str(exc)}"
        )

    return BiologicalProfileResponse(
        estimated_sex=res.estimated_sex,
        sex_confidence=res.sex_confidence,
        estimated_age_range=res.estimated_age_range,
        estimated_stature_cm=res.estimated_stature_cm,
        stature_margin_error_cm=res.stature_margin_error_cm,
        stature_range_formatted=res.stature_range_formatted,
        population_affinity=res.population_affinity,
        anthropology_summary=res.anthropology_summary
    )


@router.post(
    "/trauma-audit",
    response_model=TraumaAuditResponse,
    summary="Skeletal Element Trauma Audit",
    description="Audits skeletal element lesions and categorizes perimortem trauma mechanisms.",
    status_code=status.HTTP_200_OK,
)
async def audit_skeletal_trauma(body: TraumaAuditRequest) -> TraumaAuditResponse:
    try:
        obs = [
            TraumaObservation(o.element_name, o.trauma_mechanism, o.trauma_timing, o.description)
            for o in body.observations
        ]
        res = _trauma_auditor.audit_trauma_lesions(body.sample_id, body.element_name, obs)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Trauma audit failed: {str(exc)}"
        )

    return TraumaAuditResponse(
        sample_id=res.sample_id,
        element_classified=res.element_classified,
        total_observations_count=res.total_observations_count,
        has_perimortem_trauma=res.has_perimortem_trauma,
        observations=[
            TraumaObservationSchema(
                element_name=o.element_name,
                trauma_mechanism=o.trauma_mechanism,
                trauma_timing=o.trauma_timing,
                description=o.description
            )
            for o in res.observations
        ],
        trauma_summary=res.trauma_summary
    )
