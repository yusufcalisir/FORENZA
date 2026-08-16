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


# ── Forensic Entomology Schemas ──────────────────────────────────────────────

class HourlyTemperatureInput(BaseModel):
    hour_index: Optional[int] = Field(default=0, description="Sequential hour index.")
    timestamp_iso: Optional[str] = Field(default=None, description="ISO timestamp of weather record.")
    temperature_c: float = Field(..., description="Ambient air temperature in degrees Celsius.")


class EntomologyPmiRequest(BaseModel):
    species_name: str = Field(
        default="Lucilia sericata",
        description="Scientific name of collected Dipteran species."
    )
    development_stage: str = Field(
        default="3rd Instar Feeding",
        description="Oldest developmental stage identified on the body."
    )
    hourly_temperatures: List[HourlyTemperatureInput] = Field(
        ...,
        min_length=1,
        description="Hourly ambient temperatures leading up to the sample collection time (chronologically ascending)."
    )
    delta_t_mass: float = Field(
        default=0.0,
        ge=0.0,
        le=5.0,
        description="Larval aggregate metabolic heating offset in degrees Celsius (+1.5°C to +3.5°C)."
    )
    sampling_time_iso: Optional[str] = Field(
        default=None,
        description="ISO 8601 timestamp when insect specimens were collected."
    )


class EntomologyPmiResponse(BaseModel):
    species: str
    development_stage: str
    t_base_c: float
    target_adh: float
    accumulated_adh: float
    pmi_min_hours: float
    pmi_min_days: float
    colonisation_timestamp: Optional[str] = None
    delta_t_mass_applied_c: float
    is_target_adh_satisfied: bool
    hours_integrated: int
    warning: Optional[str] = None
    prosecutors_fallacy_shield: str


# ── Multispectral Imaging & Trace Spectroscopy Schemas ───────────────────────

class MsiAnalysisRequest(BaseModel):
    evidence_type: str = Field(
        default="Latent Bloodstain",
        description="Type of questioned biological or physical evidence."
    )
    active_wavelength_nm: int = Field(
        default=415,
        ge=300,
        le=1000,
        description="Selected optical excitation/transmission wavelength in nanometers."
    )


class MsiAnalysisResponse(BaseModel):
    evidence_type: str
    wavelength_nm: int
    band_info: Dict[str, Any]
    predicted_contrast_index: float
    is_optimal_forensic_band: bool


class TraceSpectroscopyRequest(BaseModel):
    sample_spectrum: List[float] = Field(
        ...,
        min_length=10,
        description="Intensity vector across ATR-FTIR or Raman wavenumbers (400 to 4000 cm^-1)."
    )
    wavenumbers_cm_1: Optional[List[float]] = Field(
        default=None,
        description="Optional list of corresponding wavenumber calibration points."
    )


class TraceSpectroscopyResponse(BaseModel):
    top_match: Optional[Dict[str, Any]]
    library_matches: List[Dict[str, Any]]
    points_evaluated: int
    prosecutors_fallacy_shield: str



