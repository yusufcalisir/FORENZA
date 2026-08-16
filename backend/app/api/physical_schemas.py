from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class BloodstainInput(BaseModel):
    stain_id: Optional[str] = Field(default="stain_1", description="Unique stain identifier.")
    x_cm: float = Field(..., description="Stain location X coordinate in cm.")
    y_cm: float = Field(..., description="Stain location Y coordinate in cm.")
    z_cm: float = Field(..., description="Stain location Z coordinate in cm.")
    width_mm: float = Field(..., gt=0.0, description="Stain ellipse width in mm.")
    length_mm: float = Field(..., gt=0.0, description="Stain ellipse length in mm.")
    gamma_degrees: float = Field(..., description="Directional angle gamma in degrees (0 to 360).")


class BpaAreaOfOriginRequest(BaseModel):
    stains: List[BloodstainInput] = Field(
        ...,
        min_length=2,
        description="List of at least 2 bloodstain impact coordinate and geometry measurements."
    )
    apply_drag_gravity_correction: bool = Field(
        default=False,
        description="Flag to apply aerodynamic drag & ballistic gravity curvature correction."
    )


class BpaAreaOfOriginResponse(BaseModel):
    origin: Dict[str, float]
    spatial_error_radius_cm: float
    stains_analyzed: int
    mean_impact_angle_deg: float
    gravity_correction_applied: bool
    orthogonal_residuals_cm: List[float]
    prosecutors_fallacy_shield: str


# ── SEM-EDX Gunshot Residue (GSR) Schemas ─────────────────────────────────────

class GsrParticleInput(BaseModel):
    particle_id: Optional[str] = Field(default="particle_1", description="Identifier for scanned particle.")
    pb_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Lead (Pb) weight percent.")
    ba_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Barium (Ba) weight percent.")
    sb_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Antimony (Sb) weight percent.")
    al_percent: Optional[float] = Field(default=0.0, ge=0.0, le=100.0, description="Aluminum (Al) weight percent.")
    aspect_ratio: float = Field(default=1.0, gt=0.0, description="Morphological aspect ratio (Major/Minor axis).")


class GsrAnalysisRequest(BaseModel):
    particles: List[GsrParticleInput] = Field(
        ...,
        min_length=1,
        description="List of SEM-EDX scanned microscopic particles for ASTM E1588-20 evaluation."
    )


class GsrAnalysisResponse(BaseModel):
    total_particles_scanned: int
    characteristic_particles: int
    consistent_particles: int
    commonly_associated_particles: int
    likelihood_ratio: float
    evidence_strength: str
    classified_particles: List[Dict[str, Any]]
    prosecutors_fallacy_shield: str


# ── 3D Congruent Matching Cells (CMC) Schemas ────────────────────────────────

class CmcCellInput(BaseModel):
    cell_id: Optional[str] = Field(default="cell_1", description="Identifier for 100um x 100um LEA cell.")
    ccf_max: float = Field(..., ge=0.0, le=1.0, description="Peak cross-correlation function value.")
    delta_x_um: float = Field(..., description="Spatial X translation offset in micrometers.")
    delta_y_um: float = Field(..., description="Spatial Y translation offset in micrometers.")
    delta_theta_deg: float = Field(..., description="Angular rotation offset in degrees.")


class CmcMatchingRequest(BaseModel):
    cells: List[CmcCellInput] = Field(
        ...,
        min_length=1,
        description="List of comparison cells across questioned and exemplar firearm striation topographies."
    )
    mean_delta_x_um: float = Field(default=0.0, description="Expected mean X translation offset.")
    mean_delta_y_um: float = Field(default=0.0, description="Expected mean Y translation offset.")
    mean_delta_theta_deg: float = Field(default=0.0, description="Expected mean rotation offset.")


class CmcMatchingResponse(BaseModel):
    total_cells_evaluated: int
    cmc_count: int
    identification_verdict: str
    false_match_probability: str
    ballistic_conclusion: str
    evaluated_cells: List[Dict[str, Any]]
    prosecutors_fallacy_shield: str

