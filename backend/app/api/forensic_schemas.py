"""
FORENZA Forensic API — Pydantic v2 Request / Response Schemas.
Strict input validation for LR, kinship, and validation endpoints.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field, model_validator


# ── Shared sub-types ─────────────────────────────────────────────────────────

class LocusGenotypeInput(BaseModel):
    """Allele pair for a single CODIS locus. Accepts int or float repeat units."""
    locus: str = Field(..., examples=["TH01"], description="CODIS locus name")
    allele1: float = Field(..., gt=0, description="First allele repeat unit")
    allele2: float = Field(..., gt=0, description="Second allele repeat unit")


class ProfileInput(BaseModel):
    """Complete STR profile for one individual."""
    profile_id: str = Field(..., min_length=1, max_length=64)
    loci: List[LocusGenotypeInput] = Field(..., min_length=3,
        description="Minimum 3 loci required; CODIS 20 recommended")
    population_group: str = Field("Caucasian",
        description="Population reference: Caucasian | AfricanAmerican | Hispanic | Asian")


# ── LR endpoint ──────────────────────────────────────────────────────────────

class LRRequest(BaseModel):
    """Request body for POST /forensic/lr."""
    evidence_profile: ProfileInput
    suspect_profile: ProfileInput
    theta: float = Field(0.01, ge=0.0, le=0.10,
        description="Balding-Nichols coancestry coefficient θ (NRC II Rec 4.10b)")
    population: Optional[str] = Field(None,
        description="Override population for frequency lookup (default: suspect_profile.population_group)")


class ConfidenceInterval(BaseModel):
    low: float
    high: float


class LRResponse(BaseModel):
    """Response body for POST /forensic/lr."""
    match_status: str          # "INCLUSION" | "EXCLUSION"
    lr_value: float
    log10_lr: float
    confidence_interval: ConfidenceInterval
    evaluated_loci: int
    locus_scores: Dict[str, float]
    assumptions: List[str]
    limitations: List[str]
    model: str
    data_source: str


# ── Kinship endpoint ─────────────────────────────────────────────────────────

class KinshipRequest(BaseModel):
    """Request body for POST /forensic/kinship."""
    profile1: ProfileInput
    profile2: ProfileInput
    relationship: str = Field("parent_child",
        description="parent_child | full_sibling | half_sibling | unrelated")
    theta: float = Field(0.01, ge=0.0, le=0.10)
    population: Optional[str] = None

    @model_validator(mode="after")
    def validate_relationship(self) -> "KinshipRequest":
        valid = {"parent_child", "full_sibling", "half_sibling", "unrelated"}
        if self.relationship not in valid:
            raise ValueError(f"relationship must be one of {valid}")
        return self


class KinshipResponse(BaseModel):
    """Response body for POST /forensic/kinship."""
    relationship: str
    ki_value: float
    log10_ki: float
    confidence_interval: ConfidenceInterval
    posterior_probability: float
    evaluated_loci: int
    locus_scores: Dict[str, float]
    assumptions: List[str]
    limitations: List[str]
    model: str
    data_source: str


# ── Validation endpoint ───────────────────────────────────────────────────────

class ValidationRequest(BaseModel):
    """Request body for POST /forensic/validate (runs internal validation simulation)."""
    n_per_type: int = Field(100, ge=10, le=2000,
        description="Number of profile pairs per relationship type (10–2000)")
    population: str = Field("Caucasian")
    theta: float = Field(0.01, ge=0.0, le=0.10)
    seed: int = Field(42)


class ValidationResponse(BaseModel):
    """Response body for POST /forensic/validate."""
    run_id: str
    population: str
    n_pairs_per_type: int
    elapsed_seconds: float
    accuracy: float
    sensitivity_tpr: float
    specificity_tnr: float
    false_inclusion_rate: float
    false_exclusion_rate: float
    rmse_log10_lr: float
    per_type_mean_log10_lr: Dict[str, float]
    tippett_sample: Dict[str, Any]
    model: str
