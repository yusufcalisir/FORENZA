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
