"""
Pydantic v2 Request & Response Schemas for Geo-Forensic Intelligence (Pillar 7).
Configured with ConfigDict(protected_namespaces=()) to eliminate warnings.
"""

from typing import List, Optional, Dict, Any, Literal, Tuple
from pydantic import BaseModel, Field, ConfigDict


# ── Multi-Isotope Provenancing Schemas (Module 1.1) ───────────────────────────

class IsotopeMeasurementInput(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    delta_18o_permil: Optional[float] = Field(None, description="Oxygen delta value in permil (VSMOW).")
    delta_2h_permil: Optional[float] = Field(None, description="Hydrogen delta value in permil (VSMOW).")
    sr_87_86_ratio: Optional[float] = Field(None, description="Strontium 87Sr/86Sr isotope ratio.")
    delta_13c_permil: Optional[float] = Field(None, description="Carbon delta value in permil (VPDB).")
    delta_15n_permil: Optional[float] = Field(None, description="Nitrogen delta value in permil (AIR).")
    pb_206_207_ratio: Optional[float] = Field(None, description="Lead 206Pb/207Pb ratio.")
    sample_tissue: Literal[
        "TOOTH_ENAMEL_CARBONATE",
        "TOOTH_ENAMEL_PHOSPHATE",
        "SCALP_HAIR_KERATIN",
        "BONE_BIOAPATITE",
        "DRINKING_WATER",
        "BULK_ORGANIC",
    ] = Field(..., description="Type of biological or physical tissue analyzed.")


class MultiIsotopeProvenanceRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    case_id: str = Field(..., description="Unique case identifier.")
    sample_id: str = Field(..., description="Questioned primary sample identifier.")
    primary_measurements: IsotopeMeasurementInput = Field(..., description="Primary tissue isotope observations.")
    secondary_measurements: Optional[IsotopeMeasurementInput] = Field(None, description="Optional secondary tissue observations (e.g. hair keratin or tooth enamel).")


class CandidateRegionDto(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    region_id: str
    name: str
    country: str
    latitude: float
    longitude: float
    posterior_probability: float
    isoscape_d18o_mean: float
    isoscape_sr_87_86_mean: float


class MultiIsotopeProvenanceResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    case_id: str
    sample_id: str
    inferred_drinking_water_d18o: float
    inferred_drinking_water_d18o_sigma: float
    inferred_drinking_water_d2h: Optional[float]
    inferred_drinking_water_d2h_sigma: Optional[float]
    deuterium_excess_permil: Optional[float]
    measured_sr_87_86: Optional[float]
    resolved_centroid_lat: float
    resolved_centroid_lon: float
    confidence_radius_95_km: float
    likelihood_ratio: float
    primary_candidate_region: str
    top_candidate_regions: List[CandidateRegionDto]
    enfsi_verbal_tier: str
    enfsi_verbal_statement_en: str
    enfsi_verbal_statement_tr: str
    prosecutors_fallacy_shield: str


# ── Forensic Soil Pedology & CoDa Schemas (Module 1.2) ─────────────────────────

class SoilMineralogyInput(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sample_id: str = Field(..., description="Unique soil specimen identifier.")
    quartz_percent: float = Field(..., ge=0.0, le=100.0, description="Quartz mineral wt% from QXRD.")
    feldspar_k_percent: float = Field(..., ge=0.0, le=100.0, description="Potassium feldspar wt% from QXRD.")
    plagioclase_percent: float = Field(..., ge=0.0, le=100.0, description="Plagioclase feldspar wt% from QXRD.")
    calcite_percent: float = Field(0.0, ge=0.0, le=100.0, description="Calcite carbonate wt% from QXRD.")
    clay_kaolinite_percent: float = Field(0.0, ge=0.0, le=100.0, description="Kaolinite clay wt% from QXRD.")
    clay_illite_percent: float = Field(0.0, ge=0.0, le=100.0, description="Illite clay wt% from QXRD.")
    clay_smectite_percent: float = Field(0.0, ge=0.0, le=100.0, description="Smectite/Montmorillonite wt% from QXRD.")
    dolomite_percent: float = Field(0.0, ge=0.0, le=100.0, description="Dolomite carbonate wt% from QXRD.")
    chlorite_percent: float = Field(0.0, ge=0.0, le=100.0, description="Chlorite wt% from QXRD.")
    zircon_percent: float = Field(0.0, ge=0.0, le=100.0, description="Zircon heavy mineral wt%.")
    tourmaline_percent: float = Field(0.0, ge=0.0, le=100.0, description="Tourmaline heavy mineral wt%.")
    rutile_percent: float = Field(0.0, ge=0.0, le=100.0, description="Rutile heavy mineral wt%.")
    total_heavy_minerals_percent: float = Field(0.0, ge=0.0, le=100.0, description="Total heavy minerals fraction wt%.")
    munsell_color_dry: str = Field("10YR 4/3", description="Munsell dry soil color notation.")
    xrf_major_oxides_wt_pct: Dict[str, float] = Field(default_factory=dict, description="ED-XRF major oxides wt% (SiO2, Al2O3, Fe2O3, etc.).")
    xrf_trace_ppm: Dict[str, float] = Field(default_factory=dict, description="Diagnostic trace element concentrations in ppm (Ti, Zr, Rb, Sr, etc.).")


class SoilComparisonRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    case_id: str = Field(..., description="Unique casework tracking identifier.")
    questioned_soil: SoilMineralogyInput = Field(..., description="Questioned soil trace from evidence (boots, vehicle, clothing).")
    known_control_soil: SoilMineralogyInput = Field(..., description="Known reference control soil collected from crime scene.")


class SoilComparisonResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    case_id: str
    questioned_sample_id: str
    control_sample_id: str
    clr_questioned: List[float]
    clr_control: List[float]
    mahalanobis_distance_mcd: float
    hotelling_f_statistic: float
    hotelling_p_value: float
    color_difference_delta_e00: float
    ztr_index_questioned: float
    ztr_index_control: float
    ztr_index_difference: float
    astm_e3272_verdict: Literal["DEFINITIVE_INCLUSION", "INCONCLUSIVE_SUPPORT", "EXCLUSION_NON_MATCH"]
    likelihood_ratio: float
    enfsi_verbal_tier: str
    enfsi_verbal_statement_en: str
    enfsi_verbal_statement_tr: str
    prosecutors_fallacy_shield: str


# ── Forensic Palynology & Environmental eDNA Schemas (Module 2.1) ─────────────

class PalynologySampleInput(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sample_id: str = Field(..., description="Unique sample identifier (e.g. jacket trace, footwear).")
    raw_taxon_counts: Dict[str, int] = Field(..., description="Raw palynomorph grain counts by botanical taxon.")


class EdnaProfileInput(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    target_locus: Literal["16S_V4", "ITS", "16S_V4_ITS"] = Field("16S_V4_ITS", description="Amplicon locus analyzed.")
    asv_relative_abundances: Dict[str, float] = Field(default_factory=dict, description="Microbial/fungal ASV percentages.")


class PalynologyEdnaAnalysisRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    case_id: str = Field(..., description="Unique case tracking identifier.")
    questioned_sample: PalynologySampleInput = Field(..., description="Questioned palynological trace from evidence.")
    known_control_sample: PalynologySampleInput = Field(..., description="Known reference vegetation control.")
    edna_asv_profile: Optional[EdnaProfileInput] = Field(None, description="Optional soil eDNA metagenomic profile.")


class PalynologyEdnaAnalysisResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    case_id: str
    questioned_sample_id: str
    control_sample_id: str
    bray_curtis_dissimilarity: float
    cosine_spectral_similarity: float
    canberra_distance: float
    questioned_primary_biome: str
    questioned_biome_confidence: float
    questioned_canopy_coverage_pct: float
    control_primary_biome: str
    control_biome_confidence: float
    control_canopy_coverage_pct: float
    diagnostic_indicator_taxa: List[str]
    edna_predicted_latitude: Optional[float]
    edna_predicted_longitude: Optional[float]
    edna_confidence_radius_km: Optional[float]
    likelihood_ratio: float
    enfsi_verbal_tier: str
    enfsi_verbal_statement_en: str
    enfsi_verbal_statement_tr: str
    prosecutors_fallacy_shield: str


# ── Bayesian Geographic Profiling Schemas (Module 2.2) ─────────────────────────

class CrimeIncidentInput(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    site_id: str = Field(..., description="Crime incident identifier (e.g. C1, C2).")
    x_coord_km: float = Field(..., description="X Cartesian grid coordinate in km.")
    y_coord_km: float = Field(..., description="Y Cartesian grid coordinate in km.")
    latitude: Optional[float] = Field(None, description="Optional WGS84 latitude.")
    longitude: Optional[float] = Field(None, description="Optional WGS84 longitude.")
    weight: float = Field(1.0, ge=0.1, le=10.0, description="Crime site evidentiary weight multiplier.")


class GeographicProfileRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    case_id: str = Field(..., description="Serial casework tracking ID.")
    crime_sites: List[CrimeIncidentInput] = Field(..., min_length=1, description="List of linked crime incident sites.")
    buffer_radius_km: float = Field(1.50, ge=0.1, le=10.0, description="Rossmo buffer zone radius in km (B).")
    decay_exponent_f: float = Field(1.60, ge=0.5, le=3.0, description="Distance decay exponent outside buffer (f).")
    buffer_exponent_g: float = Field(0.80, ge=0.2, le=2.0, description="Buffer penalty decay exponent inside buffer (g).")
    grid_bounds_km: List[float] = Field(default=[0.0, 20.0, 0.0, 20.0], description="Bounding box [min_x, max_x, min_y, max_y] in km.")
    grid_resolution_km: float = Field(0.10, ge=0.05, le=1.0, description="Discrete grid step resolution in km.")


class GeographicProfileResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    case_id: str
    incident_count: int
    peak_anchor_x_km: float
    peak_anchor_y_km: float
    top_5_percent_search_area_sq_km: float
    total_grid_area_sq_km: float
    search_efficiency_index_pct: float
    canter_typology: Literal["MARAUDER", "COMMUTER"]
    canter_circle_diameter_km: float
    sde_center_x_km: float
    sde_center_y_km: float
    sde_rotation_angle_deg: float
    probability_density_surface: List[List[float]]
    likelihood_ratio: float
    enfsi_verbal_tier: str
    enfsi_verbal_statement_en: str
    enfsi_verbal_statement_tr: str
    prosecutors_fallacy_shield: str


# ── Multi-Criteria Evidence Fusion Schemas (Module 3.1) ───────────────────────

class EvidenceLayerWeightInput(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    layer_id: str = Field(..., description="Evidence layer unique identifier.")
    modality_name: str = Field(..., description="Modality (ISOTOPE_ISOSCAPE, SOIL_CODA, PALYNOLOGY_EDNA, ROSSMO_GEO_PROFILE).")
    likelihood_matrix: List[List[float]] = Field(..., description="2D raster grid of continuous likelihood scores.")
    weight: float = Field(1.0, ge=0.0, le=5.0, description="User or model evidentiary weighting factor.")
    modality_likelihood_ratio: float = Field(1.0, ge=1.0, description="Standalone modality Likelihood Ratio.")


class GeoEvidenceFusionRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    case_id: str = Field(..., description="Case tracking ID.")
    layers: List[EvidenceLayerWeightInput] = Field(..., min_length=1, description="List of evidence raster layers to fuse.")
    prior_surface: Optional[List[List[float]]] = Field(None, description="Optional prior geographic probability surface (P0).")
    grid_bounds_km: List[float] = Field(default=[0.0, 20.0, 0.0, 20.0], description="Bounding box [min_x, max_x, min_y, max_y] in km.")
    grid_resolution_km: float = Field(0.50, ge=0.05, le=5.0, description="Raster grid cell resolution in km.")


class FusedSpatialHotspotDto(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    hotspot_id: str
    centroid_x_km: float
    centroid_y_km: float
    centroid_lat: Optional[float]
    centroid_lon: Optional[float]
    bounding_radius_km: float
    posterior_density_mass_pct: float
    primary_associated_modality: str


class GeoEvidenceFusionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    case_id: str
    grid_dimensions: Tuple[int, int]
    fused_probability_surface: List[List[float]]
    peak_posterior_coord_km: Tuple[float, float]
    search_area_50pct_sq_km: float
    search_area_5pct_sq_km: float
    total_grid_area_sq_km: float
    search_efficiency_index_pct: float
    top_spatial_hotspots: List[FusedSpatialHotspotDto]
    fused_likelihood_ratio: float
    enfsi_verbal_tier: str
    enfsi_verbal_statement_en: str
    enfsi_verbal_statement_tr: str
    prosecutors_fallacy_shield: str
