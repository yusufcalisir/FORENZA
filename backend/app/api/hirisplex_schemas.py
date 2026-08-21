"""
FORENZA HIrisPlex-S DNA Pigmentation Forensics Schemas (Module 3.1).
Compliant with Pydantic v2 and ConfigDict(protected_namespaces=()).
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class HIrisPlexPredictRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    genotype_dosages: Dict[str, float] = Field(
        ...,
        examples=[{"rs12913832": 2.0, "rs16891982": 2.0, "rs1426654": 2.0, "rs1805007": 1.0}],
        description="Assayed SNP dosage map (0.0, 1.0, 2.0).",
    )
    enable_imputation: bool = Field(
        True,
        description="Enable population mean dosage imputation for missing loci.",
    )


class PhenotypeTraitResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    domain: str
    probabilities: Dict[str, float]
    predicted_class: str
    confidence: float
    is_simplex_valid: bool
    missing_loci_count: int
    imputed_loci_count: int
    uncertainty_penalty_applied: bool


class HIrisPlexFullResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    eye_color: PhenotypeTraitResponse
    hair_color: PhenotypeTraitResponse
    hair_shade: Dict[str, float]
    skin_phototype: PhenotypeTraitResponse
    hair_morphology: PhenotypeTraitResponse
    total_snps_assayed: int
    total_snps_missing: int
    global_confidence_score: float
    prosecutors_fallacy_shield: str


class HIrisPlexStandardResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    standard_id: str
    name: str
    population: str
    description: str
    genotype_dosages: Dict[str, float]
    expected_eye_class: str
    min_eye_confidence: float
    expected_hair_class: str
    min_hair_confidence: float
    expected_skin_class: str
    min_skin_confidence: float
    expected_morphology: str


class HIrisPlexCrossValResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    tool_name: str
    benchmark_name: str
    computed_probability: float
    expected_probability: float
    absolute_residual: float
    is_concordant: bool
    description: str


class HIrisPlexShieldResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    has_phenotype_disclaimer: bool
    prosecutors_fallacy_shield_active: bool
    disclaimer_text_en: str
    disclaimer_text_tr: str
