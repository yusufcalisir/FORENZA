"""
FORENZA Forensic Microbiology API — Pydantic v2 Schemas.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from node.services.forensic.microbiology.schemas import (
    TaxonAbundance as DomainTaxonAbundance,
    SampleMicrobiomeProfile,
    ThanatoPmiRequest,
    ThanatoPmiResponse,
    TouchTraceMatchRequest,
    TouchTraceMatchResponse,
    BodyFluidMicrobiomeRequest,
    BodyFluidMicrobiomeResponse,
    SoilCdiTaphonomyRequest,
    SoilCdiTaphonomyResponse
)


class TaxonAbundanceSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    genus_name: str = Field(..., examples=["Cutibacterium", "Streptococcus"])
    phylum_name: str = Field(..., examples=["Actinomycetota", "Bacillota"])
    relative_abundance: float = Field(..., ge=0.0, le=1.0, examples=[0.65])


class MicrobialProfileSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sample_id: str = Field(..., examples=["MIC-SAMPLE-301"])
    sample_type: str = Field("BODY_TRACE", examples=["BODY_TRACE", "SOIL_SWAB"])
    taxa: List[TaxonAbundanceSchema]


class MicrobiologyClassifyRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    profile: MicrobialProfileSchema


class MicrobiologyClassifyResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sample_id: str
    shannon_diversity_index: float
    dominant_genus: str
    dominant_phylum: str
    taxa_count: int
    microbiology_summary: str


class BodySiteOriginRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    profile: MicrobialProfileSchema


class BodySiteOriginResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sample_id: str
    predicted_body_site: str
    site_confidence_score: float
    indicator_species: List[str]
    origin_likelihood_ratio: float
    origin_summary: str


__all__ = [
    "TaxonAbundanceSchema",
    "MicrobialProfileSchema",
    "MicrobiologyClassifyRequest",
    "MicrobiologyClassifyResponse",
    "BodySiteOriginRequest",
    "BodySiteOriginResponse",
    "ThanatoPmiRequest",
    "ThanatoPmiResponse",
    "TouchTraceMatchRequest",
    "TouchTraceMatchResponse",
    "BodyFluidMicrobiomeRequest",
    "BodyFluidMicrobiomeResponse",
    "SoilCdiTaphonomyRequest",
    "SoilCdiTaphonomyResponse"
]
