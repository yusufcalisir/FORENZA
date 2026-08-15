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

