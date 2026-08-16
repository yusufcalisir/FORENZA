from fastapi import APIRouter, HTTPException, status
import math
from backend.app.api.court_schemas import (
    GenerateCourtTestimonyRequest,
    GenerateCourtTestimonyResponse,
    EvaluativeReportRequest,
    EvaluativeReportResponse,
    DaubertComplianceRequest,
    DaubertComplianceResponse,
    SE3TransformRequest,
    SE3TransformResponse,
    ConfidenceEllipsoidRequest,
    ConfidenceEllipsoidResponse,
    ReconstructSceneRequest,
    ReconstructSceneResponse,
    SensorPointOut,
)
from backend.node.services.forensic.court.expert_witness_engine import ExpertWitnessEngine
from backend.node.services.forensic.court.evaluative_reporting_engine import (
    DynamicEvaluativeReportingEngine,
)
from backend.node.services.forensic.court.spatial_reconstruction_engine import (
    SpatialReconstructionEngine,
)

router = APIRouter(prefix="/forensic/court", tags=["Expert Witness & Judicial Examination Subsystem"])
_TESTIMONY_ENGINE = ExpertWitnessEngine()
_REPORTING_ENGINE = DynamicEvaluativeReportingEngine()
_SPATIAL_ENGINE = SpatialReconstructionEngine()


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


# ── Module 30: 3D Spatial Crime Scene Reconstruction Endpoints ────────────────

@router.post(
    "/spatial/transform-se3",
    response_model=SE3TransformResponse,
    status_code=status.HTTP_200_OK,
    summary="Apply SE(3) rigid-body transformation to a 3D point",
    description=(
        "Transforms local sensor coordinates X_local to global scene datum X_scene "
        "via X_scene = R(phi,theta,psi)·X_local + T, where R = R_z(psi)·R_y(theta)·R_x(phi). "
        "(Research §5.1, VECTOR_30_SPATIAL_A–C)"
    ),
)
async def transform_se3(req: SE3TransformRequest) -> SE3TransformResponse:
    try:
        result = SpatialReconstructionEngine.transform_se3(
            x_local=tuple(req.x_local),
            roll_phi_rad=math.radians(req.roll_phi_deg),
            pitch_theta_rad=math.radians(req.pitch_theta_deg),
            yaw_psi_rad=math.radians(req.yaw_psi_deg),
            translation=tuple(req.translation),
        )
        return SE3TransformResponse(
            x_local=list(result.x_local),
            x_scene=list(result.x_scene),
            rotation_matrix=result.rotation_matrix,
            translation_vector=list(result.translation_vector),
            roll_phi_rad=result.roll_phi_rad,
            pitch_theta_rad=result.pitch_theta_rad,
            yaw_psi_rad=result.yaw_psi_rad,
            orthogonality_residual=result.orthogonality_residual,
            det_residual=result.det_residual,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"SE(3) transform error: {str(e)}")


@router.post(
    "/spatial/confidence-ellipsoid",
    response_model=ConfidenceEllipsoidResponse,
    status_code=status.HTTP_200_OK,
    summary="Compute 95% volumetric confidence ellipsoid from 3×3 spatial covariance",
    description=(
        "Computes 95% confidence ellipsoid: (X-mu)^T·Sigma^-1·(X-mu) <= chi2_{3,0.95}≈7.815. "
        "Via eigendecomposition: a=sqrt(lambda_1*7.815), b=sqrt(lambda_2*7.815), c=sqrt(lambda_3*7.815). "
        "Volume V=(4/3)*pi*a*b*c. (Research §5.2, VECTOR_30_SPATIAL_D)"
    ),
)
async def confidence_ellipsoid(req: ConfidenceEllipsoidRequest) -> ConfidenceEllipsoidResponse:
    try:
        result = SpatialReconstructionEngine.calculate_95ci_ellipsoid(
            centroid_mu=tuple(req.centroid_mu),
            covariance_matrix=req.covariance_matrix,
        )
        return ConfidenceEllipsoidResponse(
            centroid_mu=list(result.centroid_mu),
            semi_axis_a=result.semi_axis_a,
            semi_axis_b=result.semi_axis_b,
            semi_axis_c=result.semi_axis_c,
            volume_m3=result.volume_m3,
            eigenvectors=result.eigenvectors,
            eigenvalues=list(result.eigenvalues),
            chi2_threshold=result.chi2_threshold,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Confidence ellipsoid error: {str(e)}")


@router.post(
    "/spatial/reconstruct-scene",
    response_model=ReconstructSceneResponse,
    status_code=status.HTTP_200_OK,
    summary="Fuse multi-modal forensic evidence into unified 3D crime scene reconstruction",
    description=(
        "Registers LiDAR points (±0.002 m), BPA origins (±0.012 m), ballistics vectors (±0.005 m), "
        "and DNA landmarks (±0.008 m) into a common scene coordinate frame. Returns centroid, bounding "
        "box, and point-to-plane residual energy. (Research §5.1, VECTOR_30_SPATIAL_E)"
    ),
)
async def reconstruct_scene(req: ReconstructSceneRequest) -> ReconstructSceneResponse:
    try:
        lidar_dicts = [{"label": lp.label, "coords": lp.coords} for lp in req.lidar_points]
        bv_dicts = [{"origin": bv.origin, "direction": bv.direction} for bv in req.ballistics_vectors]
        result = SpatialReconstructionEngine.fuse_multimodal_scene_evidence(
            scene_id=req.scene_id,
            lidar_points=lidar_dicts,
            bpa_origins=[tuple(p) for p in req.bpa_origins],
            ballistics_vectors=bv_dicts,
            dna_landmarks=[tuple(p) for p in req.dna_landmarks],
        )
        return ReconstructSceneResponse(
            scene_id=result.scene_id,
            sensor_points=[
                SensorPointOut(
                    sensor_type=sp.sensor_type,
                    label=sp.label,
                    x_scene=list(sp.x_scene),
                    precision_m=sp.precision_m,
                )
                for sp in result.sensor_points
            ],
            bpa_origins=[list(o) for o in result.bpa_origins],
            scene_centroid=list(result.scene_centroid),
            scene_bounding_box={
                k: list(v) for k, v in result.scene_bounding_box.items()
            },
            point_to_plane_residual=result.point_to_plane_residual,
            n_sensors=result.n_sensors,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Scene reconstruction error: {str(e)}")
