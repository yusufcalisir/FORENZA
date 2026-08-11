"""
FORENZA Forensic Microbiology API — Pydantic v2 Schemas.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class TaxonAbundanceSchema(BaseModel):
    genus_name: str = Field(..., examples=["Cutibacterium", "Streptococcus"])
    phylum_name: str = Field(..., examples=["Actinomycetota", "Bacillota"])
    relative_abundance: float = Field(..., ge=0.0, le=1.0, examples=[0.65])


class MicrobialProfileSchema(BaseModel):
    sample_id: str = Field(..., examples=["MIC-SAMPLE-301"])
    sample_type: str = Field("BODY_TRACE", examples=["BODY_TRACE", "SOIL_SWAB"])
    taxa: List[TaxonAbundanceSchema]


class MicrobiologyClassifyRequest(BaseModel):
    profile: MicrobialProfileSchema


class MicrobiologyClassifyResponse(BaseModel):
    sample_id: str
    shannon_diversity_index: float
    dominant_genus: str
    dominant_phylum: str
    taxa_count: int
    microbiology_summary: str


class BodySiteOriginRequest(BaseModel):
    profile: MicrobialProfileSchema


class BodySiteOriginResponse(BaseModel):
    sample_id: str
    predicted_body_site: str
    site_confidence_score: float
    indicator_species: List[str]
    origin_likelihood_ratio: float
    origin_summary: str
