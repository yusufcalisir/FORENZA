"""
FORENZA Ancient DNA & Degraded Forensic SNP API — Pydantic v2 Schemas (Module 2.5).
Standards Compliance: ISFG Recommendations (2021), mapDamage 2.0 (2013), Briggs et al. (2007).
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class MapDamageProfileRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    delta_0: float = Field(0.25, ge=0.0, le=1.0, description="Terminal 5' C->T deamination probability (0.0 to 1.0).", examples=[0.25])
    decay_alpha: float = Field(0.10, ge=0.0, le=2.0, description="Exponential decay rate per nucleotide distance.", examples=[0.10])
    baseline_error: float = Field(0.005, ge=0.0, le=0.1, description="Sequencing baseline error rate.", examples=[0.005])
    max_position: int = Field(25, ge=5, le=50, description="Maximum distance in bp from terminal ends.", examples=[25])
    g_to_a_ratio: float = Field(1.0, ge=0.5, le=1.5, description="3' G->A / 5' C->T deamination symmetry ratio.", examples=[1.0])


class MapDamageProfileResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    delta_0: float
    decay_alpha: float
    baseline_error: float
    max_position: int
    curve_5p_c_to_t: Dict[int, float]
    curve_3p_g_to_a: Dict[int, float]
    deamination_summary: str


class FragmentationRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    lambda_param: float = Field(0.025, gt=0.0, le=1.0, description="Exponential fragmentation rate lambda.", examples=[0.025])
    l_min: float = Field(30.0, ge=0.0, le=100.0, description="Minimum detectable fragment length in bp.", examples=[30.0])


class FragmentationResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    lambda_param: float
    l_min: float
    mean_length: float
    median_length: float
    fraction_below_100bp: float
    degradation_tier: str
    recommended_technology: str


class SNPLikelihoodRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    locus_id: str = Field("rs1800407", description="SNP Marker Identifier (rsID).", examples=["rs1800407"])
    ref_allele: str = Field("C", description="Reference allele (A, C, G, T).", examples=["C"])
    alt_allele: str = Field("T", description="Alternative allele (A, C, G, T).", examples=["T"])
    read_bases: List[str] = Field(..., description="Observed base calls across sequencing reads.", examples=[["T", "T", "C"]])
    read_positions: List[int] = Field(..., description="Position of each base from 5' fragment terminus.", examples=[[1, 2, 15]])
    delta_0: float = Field(0.25, ge=0.0, le=1.0, description="Terminal deamination rate delta_0.", examples=[0.25])
    decay_alpha: float = Field(0.10, ge=0.0, le=2.0, description="Exponential decay rate.", examples=[0.10])
    sequencing_error_rate: float = Field(0.01, ge=0.0, le=0.1, description="Per-base sequencing error rate.", examples=[0.01])
    prior_p_ref: float = Field(0.50, ge=0.01, le=0.99, description="Population reference allele frequency.", examples=[0.50])


class SNPLikelihoodResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    locus_id: str
    ref_allele: str
    alt_allele: str
    read_count: int
    raw_likelihoods: Dict[str, float]
    log10_likelihoods: Dict[str, float]
    posterior_probabilities: Dict[str, float]
    called_genotype: str
    is_damage_compensated: bool
    deamination_risk_flag: bool


class ContaminationRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    observed_curve: Dict[int, float] = Field(..., description="Observed deamination rate map (k -> delta_k).")
    contamination_fraction: float = Field(0.12, ge=0.0, le=0.90, description="Estimated modern DNA contamination proportion (0.0 to 0.90).", examples=[0.12])
    modern_terminal_rate: float = Field(0.002, ge=0.0, le=0.05, description="Modern un-deaminated baseline terminal rate.", examples=[0.002])


class ContaminationResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    contamination_fraction: float
    observed_terminal_damage: float
    modern_terminal_damage: float
    true_ancient_terminal_damage: float
    corrected_curve: Dict[int, float]


class PurineExcessRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    purine_minus1_count: int = Field(..., ge=0, description="Count of purines (A or G) at -1 position.", examples=[720])
    total_reads: int = Field(..., gt=0, description="Total number of evaluated sequencing reads.", examples=[1000])


class PurineExcessResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    purine_fraction: float
    is_ancient_depurination_signature: bool
    threshold_fraction: float = 0.65


class AdnaCaseworkCohortSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    cohort_id: str
    name: str
    sample_type: str
    description: str
    delta_0: float
    decay_alpha: float
    baseline_error: float
    mean_fragment_length: float
    lambda_fragmentation: float
    contamination_fraction: float
    pre_break_purine_fraction: float
    expected_degradation_tier: str
    expected_tech_recommendation: str
