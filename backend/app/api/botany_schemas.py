"""
FORENZA Forensic Botany API — Pydantic v2 Schemas.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class BotanicalSpecimenSchema(BaseModel):
    specimen_id: str = Field(..., examples=["BOT-SAMPLE-501"])
    sample_type: str = Field("POLLEN_GRAIN", examples=["POLLEN_GRAIN", "LEAF_FRAGMENT", "WOOD"])
    rbcl_sequence: Optional[str] = Field(None, examples=["ATCGGTTACGAATTCCGCTA"])
    matk_sequence: Optional[str] = Field(None, examples=["CGTTACGATTCGATCGATCG"])
    pollen_aperture_type: Optional[str] = Field(None, examples=["TRICOLPATE", "TRIPORATE"])
    exine_ornamentation: Optional[str] = Field(None, examples=["RETICULATE", "ECHINATE"])


class BotanyIdentifyRequest(BaseModel):
    specimen: BotanicalSpecimenSchema


class BotanicalHitSchema(BaseModel):
    species_name: str
    family_name: str
    dna_similarity_score: float
    pollen_morphology_match: bool
    confidence_verdict: str


class BotanyIdentifyResponse(BaseModel):
    specimen_id: str
    sample_type: str
    top_species_hits: List[BotanicalHitSchema]
    botany_summary: str


class PlantAssemblageSchema(BaseModel):
    species_name: str = Field(..., examples=["Pinus sylvestris"])
    abundance_percentage: float = Field(..., ge=0.0, le=100.0, examples=[65.0])


class HabitatInferenceRequest(BaseModel):
    sample_id: str = Field(..., examples=["BOT-HABITAT-101"])
    assemblage: List[PlantAssemblageSchema]


class HabitatInferenceResponse(BaseModel):
    sample_id: str
    inferred_habitat_type: str
    geographic_association: str
    seasonal_bloom_window: str
    habitat_match_lr: float
    habitat_summary: str
