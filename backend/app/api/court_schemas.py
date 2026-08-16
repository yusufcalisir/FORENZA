from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class GenerateCourtTestimonyRequest(BaseModel):
    case_id: str = Field(default="CASE-2026-COURT-01")
    sample_id: str = Field(default="SAMPLE-DNA-101")
    expert_witness_id: str = Field(default="EXPERT-01 (Dr. Sarah Connor)")
    log10_lr: float = Field(default=26.0)
    enfsi_verbal_predicate: str = Field(default="EXTREMELY_STRONG_SUPPORT_FOR_INCLUSION")
    total_loci: int = Field(default=24)
    fst_correction: float = Field(default=0.01)
    stochastic_threshold: float = Field(default=150.0)


class TestimonyPillar(BaseModel):
    title: str
    summary: str
    details: str
    fallacy_protection_active: Optional[bool] = None


class GenerateCourtTestimonyResponse(BaseModel):
    testimony_title: str
    case_id: str
    sample_id: str
    expert_witness_id: str
    timestamp: str
    operating_mode: str
    testimony_pillars: List[TestimonyPillar]
    prosecutors_fallacy_shield: str
    testimony_hmac_hash: str
    court_admissible: bool


# ── Module 29: ENFSI Evaluative Reporting ─────────────────────────────────────

class EvaluativeReportRequest(BaseModel):
    likelihood_ratio: float = Field(
        default=3.5e7,
        description="Numerical LR = P(E|H_p) / P(E|H_d); must be > 0.",
    )
    hp_proposition: str = Field(
        default="The DNA evidence originates from the named suspect.",
        description="Prosecution proposition H_p.",
    )
    hd_proposition: str = Field(
        default="The DNA evidence originates from an unknown unrelated person.",
        description="Defense proposition H_d.",
    )
    language: str = Field(
        default="tr",
        description="Language for evaluative statement: 'tr' (Turkish) or 'en' (English).",
    )


class EvaluativeReportResponse(BaseModel):
    likelihood_ratio: float
    log10_likelihood_ratio: float
    effective_lr: float
    is_prosecution_supported: bool
    supported_proposition: str
    opposed_proposition: str
    verbal_tier: int
    log10_tier_min: float
    log10_tier_max: Optional[float]
    phrase_en: str
    phrase_tr: str
    evaluative_statement: str
    language: str
    hp_proposition: str
    hd_proposition: str
    prosecutors_fallacy_shield: str
    reporting_standard: str


# ── Module 29: Daubert / Frye Compliance Audit ────────────────────────────────

class DaubertComplianceRequest(BaseModel):
    error_rate: float = Field(
        default=1e-9,
        description="Observed system error rate; must be ≤ 1e-6 to pass Daubert Pillar 2.",
    )
    has_peer_reviewed_algorithms: bool = Field(
        default=True,
        description="Whether underlying algorithms have peer-reviewed publications.",
    )
    swgdam_compliant: bool = Field(
        default=True,
        description="Whether SWGDAM (2020) QAS compliance is documented.",
    )
    iso17025_compliant: bool = Field(
        default=True,
        description="Whether ISO/IEC 17025:2017 accreditation is in scope.",
    )


class DaubertComplianceResponse(BaseModel):
    pillar_1_falsifiability: bool
    pillar_2_error_rate: bool
    pillar_3_peer_review: bool
    pillar_4_standards: bool
    frye_general_acceptance: bool
    overall_admissible: bool
    error_rate_bound: float
    prosecutor_fallacy_shield: str


# ── Module 30: 3D Spatial Crime Scene Reconstruction ──────────────────────────

class SE3TransformRequest(BaseModel):
    """SE(3) Special Euclidean 3D coordinate transformation request."""
    x_local: List[float] = Field(
        default=[1.0, 0.0, 0.0],
        description="Input point in local sensor coordinates [x, y, z] (m).",
        min_length=3, max_length=3,
    )
    roll_phi_deg: float = Field(
        default=0.0,
        description="Roll angle φ around X-axis [degrees].",
    )
    pitch_theta_deg: float = Field(
        default=0.0,
        description="Pitch angle θ around Y-axis [degrees].",
    )
    yaw_psi_deg: float = Field(
        default=0.0,
        description="Yaw angle ψ around Z-axis [degrees].",
    )
    translation: List[float] = Field(
        default=[0.0, 0.0, 0.0],
        description="Translation vector T = [tx, ty, tz] (m).",
        min_length=3, max_length=3,
    )


class SE3TransformResponse(BaseModel):
    x_local: List[float]
    x_scene: List[float]
    rotation_matrix: List[List[float]]
    translation_vector: List[float]
    roll_phi_rad: float
    pitch_theta_rad: float
    yaw_psi_rad: float
    orthogonality_residual: float
    det_residual: float


class ConfidenceEllipsoidRequest(BaseModel):
    """95% volumetric confidence ellipsoid request (§5.2)."""
    centroid_mu: List[float] = Field(
        default=[0.0, 0.0, 0.0],
        description="Scene centroid (x, y, z) [m].",
        min_length=3, max_length=3,
    )
    covariance_matrix: List[List[float]] = Field(
        default=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
        description="3×3 symmetric positive-definite spatial covariance Sigma [m^2].",
    )


class ConfidenceEllipsoidResponse(BaseModel):
    centroid_mu: List[float]
    semi_axis_a: float
    semi_axis_b: float
    semi_axis_c: float
    volume_m3: float
    eigenvectors: List[List[float]]
    eigenvalues: List[float]
    chi2_threshold: float


class LidarPoint(BaseModel):
    label: str = Field(default="LIDAR-PT")
    coords: List[float] = Field(default=[0.0, 0.0, 0.0], min_length=3, max_length=3)


class BallisticsVector(BaseModel):
    origin: List[float] = Field(default=[0.0, 0.0, 0.0], min_length=3, max_length=3)
    direction: List[float] = Field(default=[1.0, 0.0, 0.0], min_length=3, max_length=3)


class ReconstructSceneRequest(BaseModel):
    """Full multi-modal crime scene 3D reconstruction request."""
    scene_id: str = Field(default="SCENE-2026-001")
    lidar_points: List[LidarPoint] = Field(default=[])
    bpa_origins: List[List[float]] = Field(
        default=[],
        description="List of 3D BPA area-of-origin points [m].",
    )
    ballistics_vectors: List[BallisticsVector] = Field(default=[])
    dna_landmarks: List[List[float]] = Field(
        default=[],
        description="List of (x, y, z) biological landmark positions [m].",
    )


class SensorPointOut(BaseModel):
    sensor_type: str
    label: str
    x_scene: List[float]
    precision_m: float


class ReconstructSceneResponse(BaseModel):
    scene_id: str
    sensor_points: List[SensorPointOut]
    bpa_origins: List[List[float]]
    scene_centroid: List[float]
    scene_bounding_box: Dict[str, List[float]]
    point_to_plane_residual: float
    n_sensors: int
