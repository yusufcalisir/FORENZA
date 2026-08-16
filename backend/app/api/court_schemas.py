from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class GenerateCourtTestimonyRequest(BaseModel):
    case_id: str = Field(default="CASE-2026-COURT-01")
    sample_id: str = Field(default="SAMPLE-DNA-101")
    expert_witness_id: str = Field(default="EXPERT-01 (Dr. Sarah Connor)")
    log10_lr: float = Field(default=26.0)
    enfsi_verbal_predicate: str = Field(default="EXTREMELY_STRONG_SUPPORT_FOR_INCLUSION")
    total_loci: int = Field(default=24)
    fst_correction: float = Field(default=0.01)
    stochastic_threshold: float = Field(default=150.0)


class TestimonyPillar(BaseModel):
    title: str
    summary: str
    details: str
    fallacy_protection_active: Optional[bool] = None


class GenerateCourtTestimonyResponse(BaseModel):
    testimony_title: str
    case_id: str
    sample_id: str
    expert_witness_id: str
    timestamp: str
    operating_mode: str
    testimony_pillars: List[TestimonyPillar]
    prosecutors_fallacy_shield: str
    testimony_hmac_hash: str
    court_admissible: bool


# ── Module 29: ENFSI Evaluative Reporting ─────────────────────────────────────

class EvaluativeReportRequest(BaseModel):
    likelihood_ratio: float = Field(
        default=3.5e7,
        description="Numerical LR = P(E|H_p) / P(E|H_d); must be > 0.",
    )
    hp_proposition: str = Field(
        default="The DNA evidence originates from the named suspect.",
        description="Prosecution proposition H_p.",
    )
    hd_proposition: str = Field(
        default="The DNA evidence originates from an unknown unrelated person.",
        description="Defense proposition H_d.",
    )
    language: str = Field(
        default="tr",
        description="Language for evaluative statement: 'tr' (Turkish) or 'en' (English).",
    )


class EvaluativeReportResponse(BaseModel):
    likelihood_ratio: float
    log10_likelihood_ratio: float
    effective_lr: float
    is_prosecution_supported: bool
    supported_proposition: str
    opposed_proposition: str
    verbal_tier: int
    log10_tier_min: float
    log10_tier_max: Optional[float]
    phrase_en: str
    phrase_tr: str
    evaluative_statement: str
    language: str
    hp_proposition: str
    hd_proposition: str
    prosecutors_fallacy_shield: str
    reporting_standard: str


# ── Module 29: Daubert / Frye Compliance Audit ────────────────────────────────

class DaubertComplianceRequest(BaseModel):
    error_rate: float = Field(
        default=1e-9,
        description="Observed system error rate; must be ≤ 1e-6 to pass Daubert Pillar 2.",
    )
    has_peer_reviewed_algorithms: bool = Field(
        default=True,
        description="Whether underlying algorithms have peer-reviewed publications.",
    )
    swgdam_compliant: bool = Field(
        default=True,
        description="Whether SWGDAM (2020) QAS compliance is documented.",
    )
    iso17025_compliant: bool = Field(
        default=True,
        description="Whether ISO/IEC 17025:2017 accreditation is in scope.",
    )


class DaubertComplianceResponse(BaseModel):
    pillar_1_falsifiability: bool
    pillar_2_error_rate: bool
    pillar_3_peer_review: bool
    pillar_4_standards: bool
    frye_general_acceptance: bool
    overall_admissible: bool
    error_rate_bound: float
    prosecutor_fallacy_shield: str
