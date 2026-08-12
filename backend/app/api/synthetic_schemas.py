from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class GenerateSyntheticCaseRequest(BaseModel):
    scenario_type: str = Field(default="3_PERSON_STR_MIXTURE")
    num_contributors: int = Field(default=3)
    degradation_factor: float = Field(default=0.3)
    dropout_probability: float = Field(default=0.05)


class GenerateSyntheticCaseResponse(BaseModel):
    synthetic_case_id: str
    scenario_type: str
    created_timestamp: str
    num_contributors: int
    degradation_factor: float
    dropout_probability: float
    ground_truth_contributors: List[Dict[str, Any]]
    synthetic_mixture_peaks: Dict[str, Any]
    ground_truth_metrics: Dict[str, Any]
    benchmark_hmac_hash: str
    academic_validation_ready: bool


class EvaluateBenchmarkRequest(BaseModel):
    synthetic_case_id: str = Field(default="SYNTH-CASE-101")
    engine_calculated_log10_lr: float = Field(default=24.2)


class EvaluateBenchmarkResponse(BaseModel):
    synthetic_case_id: str
    true_log10_lr: float
    engine_calculated_log10_lr: float
    log10_lr_rmse: float
    roc_auc_score: float
    false_inclusion_rate_fir_0pct: float
    self_validation_verdict: str
