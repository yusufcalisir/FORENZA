"""
FORENZA Touch DNA & Low-Template API — Pydantic v2 Schemas.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class AnalyzeLtdnaRequest(BaseModel):
    sample_id: str = Field(..., examples=["TOUCH-HANDLE-001"])
    substrate_type: str = Field(..., examples=["TEXTURED_NON_POROUS", "SMOOTH_NON_POROUS", "POROUS_FABRIC"])
    input_mass_pg: float = Field(..., gt=0.0, examples=[80.0])
    lambda_dropout: float = Field(0.05, gt=0.0, examples=[0.05])


class SubstrateEfficiencySchema(BaseModel):
    substrate_type: str
    efficiency_factor: float
    input_mass_pg: float
    recovered_mass_pg: float


class StochasticDropoutSchema(BaseModel):
    recovered_mass_pg: float
    dropout_probability_pd: float
    dropin_probability_pc: float
    peak_imbalance_ratio: float


class AnalyzeLtdnaResponse(BaseModel):
    sample_id: str
    substrate: SubstrateEfficiencySchema
    stochastic_model: StochasticDropoutSchema
    is_low_template: bool
    ltdna_summary: str


class ContributorDeconvRequest(BaseModel):
    sample_id: str = Field(..., examples=["TOUCH-HANDLE-001"])
    num_contributors: int = Field(..., ge=1, le=4, examples=[2])
    recovered_mass_pg: float = Field(..., gt=0.0, examples=[32.0])


class ContributorDeconvResponse(BaseModel):
    sample_id: str
    num_contributors: int
    deconvolution_status: str
    mixture_proportions: Dict[str, float]
    mcmc_acceptance_rate: float
    log10_lr: float
