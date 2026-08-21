"""
Pydantic v2 schemas for FORENZA Biogeographic Ancestry (BGA-55) Engine (Module 3.2).
"""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field


class BGAPredictionRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    snp_dosages: Dict[str, float] = Field(
        ...,
        description="Dictionary mapping rsID string to additive effect allele dosage in [0.0, 2.0].",
        examples=[{"rs1426654": 2.0, "rs16891982": 2.0, "rs2814778": 0.0}]
    )
    populations: Optional[List[str]] = Field(
        default=None,
        description="Optional subset of target continental populations (defaults to EUR, AFR, EAS, SAS, AMR, MID)."
    )


class BGAConfidenceEllipseSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    semi_major_deg: float
    semi_minor_deg: float
    semi_major_km: float
    semi_minor_km: float
    tilt_angle_deg: float


class BGAGISCoordinatesSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    latitude: float
    longitude: float
    formatted_coords: str
    nearest_centroid: str
    confidence_ellipse: BGAConfidenceEllipseSchema


class BGAPosteriorResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    proportions: Dict[str, float]
    log_likelihoods: Dict[str, float]
    dominant_population: str
    dominant_proportion: float
    admixture_classification: str
    shannon_entropy: float
    simpson_diversity: float
    assayed_snps_count: int
    is_simplex_valid: bool


class BGAFullAnalysisResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    admixture: BGAPosteriorResponse
    gis: BGAGISCoordinatesSchema
    prosecutors_fallacy_shield: str


class BGAGoldenStandardSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    standard_id: str
    name: str
    population: str
    description: str
    genotype_dosages: Dict[str, float]
    expected_dominant_pop: str
    min_dominant_proportion: float
    expected_lat_bounds: List[float]
    expected_lng_bounds: List[float]
    expected_classification: str


class BGACrossValidationSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    tool_name: str
    benchmark_name: str
    computed_proportion: float
    expected_proportion: float
    absolute_residual: float
    is_concordant: bool
    description: str


class BGAReportingShieldSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    disclaimer_text_en: str
    disclaimer_text_tr: str
    has_bga_disclaimer: bool
    prosecutors_fallacy_shield_active: bool
