"""
FORENZA Batch Processing API — Pydantic v2 Schemas.
"""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field
from .forensic_schemas import ProfileInput


class BatchItemSchema(BaseModel):
    item_id: str = Field(..., examples=["PAIR-001"])
    evidence: ProfileInput
    suspect: ProfileInput
    population: str = Field("Caucasian")


class BatchSubmitRequest(BaseModel):
    """Request body for POST /batch/submit."""
    items: List[BatchItemSchema] = Field(..., min_length=1)
    concurrency: int = Field(4, ge=1, le=16)


class BatchSubmitResponse(BaseModel):
    job_id: str
    status: str
    total_items: int
    submitted_timestamp: float
    message: str


class BatchMetricsSchema(BaseModel):
    total_inclusions: int
    total_exclusions: int
    total_errors: int
    hit_rate_percentage: float
    mean_log10_lr: float


class BatchItemResultSchema(BaseModel):
    item_id: str
    processed_timestamp: float
    match_status: str
    lr_value: float
    log10_lr: float
    error_message: Optional[str] = None


class BatchJobResponse(BaseModel):
    job_id: str
    status: str
    total_items: int
    processed_items: int
    progress_percentage: float
    submitted_timestamp: float
    completed_timestamp: Optional[float] = None
    metrics: BatchMetricsSchema
    results: List[BatchItemResultSchema]
