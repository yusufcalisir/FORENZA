"""
Pydantic v2 Schemas for Forensic DNA & SNP Terminal API
Compliant with ISO/IEC 17025:2017 and FBI CODIS NDIS v3.2/v4.0.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Optional, Any


class LocusSTRCallSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    locus_name: str
    allele1: str
    allele2: Optional[str] = None
    rfu1: float = 0.0
    rfu2: Optional[float] = None
    size1: Optional[float] = None
    size2: Optional[float] = None
    is_homozygous: bool = False
    is_dropout: bool = False
    is_imbalanced: bool = False
    heterozygote_balance: Optional[float] = None


class SnpGenotypeCallSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    rsid: str
    genotype: str
    gene: Optional[str] = None
    dosage_value: int = 0
    trait: Optional[str] = None
    read_depth: Optional[int] = None


class IngestTerminalFileRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    file_content: str = Field(..., description="Raw text content of the file (CSV, TSV, XML, VCF, or JSON)")
    file_format: Optional[str] = Field(
        default=None,
        description="Optional explicit format: GeneMapper_CSV | GeneMapper_TSV | CODIS_XML | NGS_VCF | LIMS_JSON | auto"
    )
    sample_id_override: Optional[str] = Field(default=None, description="Optional override for specimen ID")


class IngestTerminalFileResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sample_id: str
    detected_format: str
    chain_of_custody_hash: str
    str_marker_count: int
    snp_marker_count: int
    str_profile: Dict[str, LocusSTRCallSchema]
    snp_profile: Dict[str, SnpGenotypeCallSchema]
    supplementary_markers: Dict[str, Any]
    laboratory_ori: Optional[str] = None
    operator_id: Optional[str] = None


class TerminalPopGenRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    str_profile: Dict[str, Dict[str, Any]] = Field(..., description="STR profile mapping {locus: {allele1: ..., allele2: ...}}")
    population: str = Field(default="Caucasian", description="Reference subpopulation: Caucasian | African_American | Hispanic | Asian")
    theta: float = Field(default=0.01, description="Balding-Nichols coancestry Fst factor (0.01 or 0.03)")


class TerminalPopGenResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    population: str
    coancestry_theta: float
    minimum_allele_freq_pmin: float
    locus_match_probabilities: Dict[str, float]
    combined_match_probability: float
    random_match_probability_reciprocal: float
    log10_lr: float
    enfsi_verbal_scale: str


class TerminalSexDeterminationRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    amelogenin_allele1: str = Field(default="X")
    amelogenin_allele2: Optional[str] = Field(default="Y")
    amelogenin_rfu1: float = Field(default=1500.0)
    amelogenin_rfu2: float = Field(default=1450.0)
    dys391_signal: Optional[str] = Field(default=None)
    sry_status: Optional[str] = Field(default=None)


class TerminalSexDeterminationResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    amelogenin_call: str
    dys391_signal: Optional[str]
    sry_status: Optional[str]
    ystr_signal_present: bool
    sex_classification: str
    prior_y_null_prob_sas: float
    prior_y_null_prob_eur: float
    operational_action: str


class TerminalQualityAssessmentRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    str_profile: Dict[str, Dict[str, Any]] = Field(..., description="STR profile {locus: {allele1, allele2, rfu1, rfu2}}")


class TerminalQualityAssessmentResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    passed_qc: bool
    analytical_threshold_rfu: float
    stochastic_threshold_rfu: float
    heterozygote_balance_threshold: float
    total_loci_count: int
    dropout_loci_count: int
    imbalanced_loci_count: int
    degradation_index: float
    degradation_severity: str
    stochastic_mixture_flag: bool
    recommendations: List[str]


class TerminalBgaRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sample_id: str = Field(default="SAMPLE_BGA")
    genotype_dosages: Dict[str, int] = Field(..., description="Mapping of AIM rsIDs to allele dosage counts (0, 1, or 2)")


class ContinentalPosteriorDetail(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    cluster_code: str
    cluster_name: str
    posterior_probability: float
    reference_latitude: float
    reference_longitude: float


class TerminalBgaResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sample_id: str
    dominant_ancestry: str
    dominant_ancestry_label: str
    dominant_probability: float
    centroid_latitude: float
    centroid_longitude: float
    spatial_variance_lat: float
    spatial_variance_lon: float
    spatial_covariance: float
    lambda_max: float
    r95_confidence_radius_km: float
    num_snps_utilized: int
    continental_breakdown: List[ContinentalPosteriorDetail]


class TerminalHIrisPlexRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sample_id: str = Field(default="SAMPLE_HIRISPLEX")
    genotype_dosages: Dict[str, int] = Field(..., description="Mapping of HIrisPlex rsIDs to effect allele dosage counts (0, 1, or 2)")


class TerminalHIrisPlexResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sample_id: str
    predicted_eye_color: str
    eye_color_probabilities: Dict[str, float]
    predicted_hair_color: str
    hair_color_probabilities: Dict[str, float]
    mc1r_red_hair_epistasis_flag: bool
    predicted_skin_phototype: str
    skin_phototype_probabilities: Dict[str, float]
    num_hirisplex_snps_evaluated: int


class TerminalComprehensiveRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    file_content: Optional[str] = Field(default=None, description="Raw file text to parse")
    str_profile: Optional[Dict[str, Dict[str, Any]]] = Field(default=None, description="Explicit STR profile")
    snp_dosages: Optional[Dict[str, int]] = Field(default=None, description="Explicit SNP dosages for BGA and HIrisPlex")
    population: str = Field(default="Caucasian")
    theta: float = Field(default=0.01)


class TerminalComprehensiveResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sample_id: str
    chain_of_custody_hash: str
    popgen: TerminalPopGenResponse
    sex: TerminalSexDeterminationResponse
    qc: TerminalQualityAssessmentResponse
    bga: TerminalBgaResponse
    hirisplex: TerminalHIrisPlexResponse

