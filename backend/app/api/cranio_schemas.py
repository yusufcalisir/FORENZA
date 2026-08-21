"""
Pydantic v2 Schemas for 3D Craniofacial Morphometry & Anthropological Landmarks (Module 3.3).
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field


class Point3DSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    x: float = Field(..., description="Left (-X) to Right (+X) relative to sagittal midline (mm)")
    y: float = Field(..., description="Posterior (-Y) to Anterior (+Y) (mm)")
    z: float = Field(..., description="Inferior (-Z) to Superior (+Z) (mm)")


class CephalometricLandmarksSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    nasion: Point3DSchema
    pronasale: Point3DSchema
    subnasale: Point3DSchema
    alare_left: Point3DSchema
    alare_right: Point3DSchema
    labiale_superius: Point3DSchema
    menton: Point3DSchema
    zygion_left: Point3DSchema
    zygion_right: Point3DSchema
    cheilion_left: Point3DSchema
    cheilion_right: Point3DSchema


class AnthropologicalIndicesSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    nasal_height_mm: float
    alar_breadth_mm: float
    nasal_index: float
    nasal_typology: str
    morphological_facial_height_mm: float
    bizygomatic_breadth_mm: float
    morphological_facial_index: float
    facial_typology: str
    nasal_bridge_elevation_index: float
    facial_convexity_angle_deg: float
    mandibular_breadth_mm: float
    sexual_dimorphism_offset_mm: float


class CraniofacialPredictionRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    snp_dosages: Dict[str, Union[int, float]] = Field(
        ...,
        description="Dictionary mapping morphometric SNP rsIDs to allele dosages (0, 1, or 2)",
        json_schema_extra={"example": {"rs974448": 1, "rs12882923": 0, "rs11130635": 2, "rs13289": 0, "rs7559252": 1}},
    )
    sex: str = Field(
        default="FEMALE",
        description="Biological sex ('MALE' or 'FEMALE') for dimorphic scaling",
    )
    age_years: float = Field(
        default=25.0,
        description="Chronological or estimated biological age in years",
    )


class CraniofacialPredictionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    landmarks: CephalometricLandmarksSchema
    indices: AnthropologicalIndicesSchema
    assayed_loci_count: int
    prosecutors_fallacy_shield: str
    validation_status: str = "VERIFIED"


class ProcrustesAlignmentRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    landmarks_target: List[List[float]] = Field(
        ..., description="(k, 3) matrix of target 3D landmark coordinates"
    )
    landmarks_source: List[List[float]] = Field(
        ..., description="(k, 3) matrix of source 3D landmark coordinates to superimpose"
    )


class ProcrustesAlignmentResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    centroid_size_target: float
    centroid_size_source: float
    procrustes_distance: float
    rmsd_mm: float
    rotation_matrix: List[List[float]]
    translation_vector: List[float]
    aligned_matrix: List[List[float]]
