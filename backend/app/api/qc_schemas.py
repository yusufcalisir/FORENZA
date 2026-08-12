from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class LocusPeakInput(BaseModel):
    locus: str = Field(default="D3S1358")
    alleles: List[str] = Field(default=["15", "16"])
    peak_heights_rfu: List[float] = Field(default=[1200.0, 1150.0])


class EvaluateQcRequest(BaseModel):
    sample_id: str = Field(default="SAMPLE-DNA-01")
    negative_control_max_rfu: float = Field(default=0.0, description="Max RFU in Negative Control")
    positive_control_concordant: bool = Field(default=True, description="Positive Control match status")
    loci_peaks: Optional[List[LocusPeakInput]] = Field(default=None)


class QualityMatrixDimension(BaseModel):
    dimension: str
    status: str
    metric: str
    threshold: str


class LocusQcDetail(BaseModel):
    locus: str
    alleles: List[str]
    peak_heights_rfu: List[float]
    heterozygote_balance_hb: float
    min_rfu: float
    locus_status: str


class EvaluateQcResponse(BaseModel):
    sample_id: str
    overall_qc_verdict: str
    action_recommendation: str
    quality_inspection_matrix: List[QualityMatrixDimension]
    locus_qc_details: List[LocusQcDetail]
    total_loci_inspected: int
    imbalanced_loci_count: int
    stochastic_warning_count: int
    iso_17025_provenance: str
