"""
FORENZA Machine Learning STR Calling & Fragsifier Ensemble Domain Schemas.
Standard Compliance: ISFG DNA Commission (2016) & Barash et al. (2023).
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class ArtifactClassEnum(str, Enum):
    CLASS_TRUE_ALLELE = "CLASS_TRUE_ALLELE"
    CLASS_BACK_STUTTER = "CLASS_BACK_STUTTER"
    CLASS_FORWARD_STUTTER = "CLASS_FORWARD_STUTTER"
    CLASS_MINUS_2BP_STUTTER = "CLASS_MINUS_2BP_STUTTER"
    CLASS_PLUS_A_ARTIFACT = "CLASS_PLUS_A_ARTIFACT"
    CLASS_SPECTRAL_PULL_UP = "CLASS_SPECTRAL_PULL_UP"
    CLASS_BASE_NOISE_DROP_IN = "CLASS_BASE_NOISE_DROP_IN"


class PeakSignalMorphology(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    peak_height: float = Field(..., ge=0.0, description="RFU or Read Depth")
    peak_area: float = Field(..., ge=0.0, description="Integrated area under peak")
    height_to_area_ratio: float = Field(..., ge=0.0, description="h / A sharpness index")
    signal_to_noise_ratio: float = Field(..., ge=0.0, description="(h - baseline) / sigma")
    peak_skewness: float = Field(0.0, description="Third moment asymmetry")
    fwhm: float = Field(..., ge=0.0, description="Full Width at Half Maximum (bp or pts)")


class StutterKinetics(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    relative_bp_delta: float = Field(..., description="Distance in bp from major allele")
    is_back_stutter_pos: bool = Field(..., description="True if delta == -repeat_len")
    is_forward_stutter_pos: bool = Field(..., description="True if delta == +repeat_len")
    is_double_stutter_pos: bool = Field(..., description="True if delta == -2*repeat_len")
    is_plus_a_pos: bool = Field(..., description="True if delta == +1 bp")
    observed_stutter_ratio: float = Field(0.0, ge=0.0, description="h_candidate / h_major")


class SequenceComplexity(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    shannon_entropy: float = Field(..., ge=0.0, le=2.0, description="Shannon entropy H(S) base 2")
    longest_homopolymer: int = Field(..., ge=1, description="Max consecutive identical bases")
    gc_fraction: float = Field(..., ge=0.0, le=1.0, description="GC content ratio")
    hexamer_divergence: float = Field(0.0, ge=0.0, description="Divergence from canonical hexamers")
    flanking_snp_proximity_bp: float = Field(100.0, ge=0.0, description="Distance to nearest flanking SNP")
    interspersed_spacer_count: int = Field(0, ge=0, description="Number of non-canonical spacers")


class MixtureDynamics(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    heterozygote_balance: float = Field(1.0, ge=0.0, le=1.0, description="h_minor / h_major")
    spectral_pull_up_ratio: float = Field(0.0, ge=0.0, description="Co-eluting peak in adjacent dye")
    locus_amplification_efficiency: float = Field(1.0, ge=0.0, description="Locus RFU / Mean profile RFU")
    degradation_index: float = Field(1.0, ge=0.0, description="Small / Large amplicon yield")
    estimated_minor_contributor_prop: float = Field(0.5, ge=0.0, le=1.0, description="Assigned contributor fraction")
    analytical_threshold_margin: float = Field(..., description="(h - AT) / AT normalized margin")


class FeatureVector24D(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    locus_name: str
    peak_identifier: str
    vector: List[float] = Field(..., min_length=24, max_length=24, description="24-D continuous feature vector")
    morphology: PeakSignalMorphology
    stutter: StutterKinetics
    sequence: SequenceComplexity
    mixture: MixtureDynamics


class PeakClassificationResult(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    locus_name: str
    peak_identifier: str
    predicted_class: ArtifactClassEnum
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    class_posterior_probabilities: Dict[str, float]
    is_true_allele_candidate: bool
    recommended_action: str
    recombined_parent_peak: Optional[str] = None
    subtracted_stutter_rfu: float = 0.0


class LocusMLPreFilterReport(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    locus_name: str
    total_raw_peaks: int
    true_alleles_retained: int
    artifacts_culled: int
    culled_artifacts_breakdown: Dict[str, int]
    clean_candidate_alleles: List[str]
    candidate_probabilities: Dict[str, float]
    mcmc_search_space_reduction_pct: float = Field(..., ge=0.0, le=100.0)
    quality_flag: str
