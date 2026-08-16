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
