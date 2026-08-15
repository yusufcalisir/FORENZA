"""
FORENZA Forensic DNA Phenotyping API — Pydantic v2 Schemas.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SNPInputSchema(BaseModel):
    rsid: str = Field(..., examples=["rs12913832"], description="dbSNP identifier")
    dosage: int = Field(..., ge=0, le=2, description="Effect allele count: 0, 1, or 2")


class PhenotypeRequest(BaseModel):
    """Request body for POST /forensic/phenotype."""
    snps: List[SNPInputSchema] = Field(
        ..., min_length=1,
        description="List of SNP dosage calls. Include as many HIrisPlex-S panel SNPs as available."
    )


class TraitPrediction(BaseModel):
    most_likely: str
    confidence: float
    probabilities: Dict[str, float]


class PhenotypeResponse(BaseModel):
    """Response body for POST /forensic/phenotype."""
    eye_colour: TraitPrediction
    hair_colour: TraitPrediction
    skin_tone: TraitPrediction
    ancestry: TraitPrediction
    snp_count_evaluated: int
    model_version: str
    limitations: List[str]


# ── Module 11 HIrisPlex-S Schemas ─────────────────────────────────────────────

class EyeColorResultSchema(BaseModel):
    probabilities: Dict[str, float]
    predicted_class: str
    confidence: float
    missing_loci_count: int
    imputed_loci_count: int


class HairColorResultSchema(BaseModel):
    probabilities: Dict[str, float]
    predicted_class: str
    confidence: float
    shade_probabilities: Dict[str, float]
    predicted_shade: str
    missing_loci_count: int


class SkinPhototypeResultSchema(BaseModel):
    probabilities: Dict[str, float]
    fitzpatrick_type: str
    predicted_class: str
    confidence: float
    missing_loci_count: int


class HIrisPlexSPredictionRequest(BaseModel):
    snp_dosages: Dict[str, float] = Field(
        ...,
        description="Map of rsID to dosage (0, 1, or 2).",
        examples=[{"rs12913832": 2, "rs16891982": 2, "rs1426654": 2, "rs1805007": 1}],
    )
    enable_imputation: bool = Field(True, description="Impute missing panel SNPs with global population mean dosages.")


class HIrisPlexSPredictionResponse(BaseModel):
    eye_color: EyeColorResultSchema
    hair_color: HairColorResultSchema
    skin_phototype: SkinPhototypeResultSchema
    total_snps_assayed: int
    missingness_ratio: float
    prosecutors_fallacy_shield: str


# ── Module 12 55-AIM BGA & Live GIS Schemas ───────────────────────────────────

class ConfidenceEllipseSchema(BaseModel):
    semi_major_deg: float
    semi_minor_deg: float
    semi_major_km: float
    semi_minor_km: float
    tilt_angle_deg: float


class GISCoordinatesSchema(BaseModel):
    latitude: float
    longitude: float
    formatted_coords: str
    nearest_centroid: str
    confidence_ellipse: ConfidenceEllipseSchema


class AIMPredictionRequest(BaseModel):
    snp_dosages: Dict[str, float] = Field(
        ...,
        description="Map of rsID to dosage (0, 1, or 2).",
        examples=[{"rs2814778": 2, "rs1426654": 0, "rs10424031": 2}],
    )


class AIMPredictionResponse(BaseModel):
    proportions: Dict[str, float]
    dominant_population: str
    dominant_proportion: float
    admixture_classification: str
    shannon_entropy: float
    simpson_diversity: float
    assayed_snps_count: int
    gis_projection: GISCoordinatesSchema
    prosecutors_fallacy_shield: str


# ── Module 13 Craniofacial Morphometrics & 3D Landmark Schemas ───────────────

class Point3DSchema(BaseModel):
    x: float = Field(..., description="Left (-X) to Right (+X) coordinate in mm")
    y: float = Field(..., description="Posterior (-Y) to Anterior (+Y) coordinate in mm")
    z: float = Field(..., description="Inferior (-Z) to Superior (+Z) coordinate in mm")


class CephalometricLandmarksSchema(BaseModel):
    nasion: Point3DSchema
    pronasale: Point3DSchema
    subnasale: Point3DSchema
    alare_left: Point3DSchema
    alare_right: Point3DSchema
    labiale_superius: Point3DSchema
    menton: Point3DSchema


class FacialIndicesSchema(BaseModel):
    morphological_facial_height_mm: float
    alar_breadth_mm: float
    nasal_height_mm: float
    nasal_projection_mm: float
    facial_index_ratio: float
    facial_typology: str


class CraniofacialReconstructionRequest(BaseModel):
    snp_dosages: Dict[str, float] = Field(
        ...,
        description="Map of rsID to dosage (0, 1, or 2) for PAX3, PAX9, PRDM16, DCHS2, PCDH15.",
        examples=[{"rs974448": 2, "rs12882923": 1, "rs11130635": 2, "rs13289": 0, "rs7559252": 2}],
    )


class CraniofacialReconstructionResponse(BaseModel):
    landmarks: CephalometricLandmarksSchema
    indices: FacialIndicesSchema
    assayed_loci_count: int
    prosecutors_fallacy_shield: str



