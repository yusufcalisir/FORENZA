"""
FORENZA Forensic Serology API — Pydantic v2 Schemas.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SerologyPhenotypeSchema(BaseModel):
    sample_id: str = Field(..., examples=["SER-SAMPLE-701"])
    abo_group: str = Field(..., examples=["A", "B", "AB", "O"])
    rh_factor: str = Field(..., examples=["D+", "D-"])
    kell_status: Optional[str] = Field("K-", examples=["K+", "K-"])
    lewis_phenotype: Optional[str] = Field("Lea-b+", examples=["Lea-b+", "Lea+b-"])


class SerologyPhenotypeRequest(BaseModel):
    sample: SerologyPhenotypeSchema


class SerologyPhenotypeResponse(BaseModel):
    sample_id: str
    abo_group: str
    rh_factor: str
    secretor_status: str
    combined_serology_frequency: float
    serology_likelihood_ratio: float
    serology_summary: str


class SerologyDnaIntegrateRequest(BaseModel):
    sample: SerologyPhenotypeSchema
    lr_str: float = Field(..., ge=1.0, examples=[1000000.0])


class SerologyDnaIntegrateResponse(BaseModel):
    sample_id: str
    lr_serology: float
    lr_str: float
    lr_combined: float
    log10_lr_combined: float
    verbal_statement: str
    integration_summary: str
