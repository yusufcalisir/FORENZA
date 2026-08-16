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


# ── ISO/IEC 17025:2017 Measurement Uncertainty Schemas (Pillar 6 §3) ─────────

class UncertaintyComponentInput(BaseModel):
    name: str = Field(..., description="Name of uncertainty component (e.g. Micro-Pipette Volume).")
    standard_uncertainty: float = Field(..., ge=0.0, description="Standard uncertainty u_i in ng/uL.")
    probability_distribution: str = Field(default="NORMAL", description="Probability distribution: NORMAL, RECTANGULAR, TRIANGULAR.")
    sensitivity_coefficient: float = Field(default=1.00, description="Sensitivity coefficient c_i = df/dx_i.")
    description: Optional[str] = Field(default=None, description="Metrological description of the uncertainty contributor.")


class CalculateUncertaintyBudgetRequest(BaseModel):
    nominal_concentration: float = Field(
        ...,
        ge=0.0,
        description="Measured quantitative DNA concentration in ng/uL."
    )
    components: Optional[List[UncertaintyComponentInput]] = Field(
        default=None,
        description="Optional custom uncertainty components. If omitted, canonical 4-component budget is used."
    )
    correlations: Optional[Dict[str, float]] = Field(
        default=None,
        description="Optional correlation coefficients r_ij between component pairs (key format 'compA:compB')."
    )
    coverage_factor: float = Field(
        default=2.00,
        gt=0.0,
        description="Coverage factor k for expanded uncertainty (k=2.00 for 95.45% confidence)."
    )


class ComponentDetailOutput(BaseModel):
    component_name: str
    standard_uncertainty: float
    sensitivity_coefficient: float
    probability_distribution: str
    variance_contribution: float
    percentage_contribution: float
    description: Optional[str] = None


class ReportedIntervalOutput(BaseModel):
    lower_bound: float
    upper_bound: float
    formatted_interval: str


class CalculateUncertaintyBudgetResponse(BaseModel):
    nominal_concentration: float
    combined_standard_uncertainty: float
    expanded_uncertainty: float
    coverage_factor: float
    confidence_level: str
    reported_interval: ReportedIntervalOutput
    total_variance: float
    component_count: int
    components: List[ComponentDetailOutput]
    prosecutors_fallacy_shield: str


class ProficiencyZScoreRequest(BaseModel):
    lab_measured_value: float = Field(..., description="Laboratory measured DNA concentration (x_lab in ng/uL).")
    consensus_mean: float = Field(..., description="Proficiency testing consensus mean (mu_consensus in ng/uL).")
    consensus_std: float = Field(..., gt=0.0, description="Proficiency testing consensus standard deviation (sigma_consensus in ng/uL).")


class ProficiencyZScoreResponse(BaseModel):
    lab_measured_value: float
    consensus_mean: float
    consensus_std: float
    z_score: float
    absolute_z_score: float
    performance_tier: str
    verdict: str
    is_compliant: bool

