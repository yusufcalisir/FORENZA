"""
Pydantic Schemas for FORENZA Machine Learning STR Calling & Fragsifier REST Endpoints.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from node.services.forensic.genomics.ml_str.schemas import (
    PeakSignalMorphology,
    StutterKinetics,
    SequenceComplexity,
    MixtureDynamics,
    FeatureVector24D,
    PeakClassificationResult,
    LocusMLPreFilterReport,
)
from node.services.forensic.genomics.ml_str.isfg_hierarchy import ISFGHierarchicalRepresentation
from node.services.forensic.genomics.ml_str.mcmc_prefilter import MultiLocusPreFilterSummary


class ExtractFeaturesRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    locus_name: str
    peak_id: str
    peak_height: float = Field(..., ge=0.0)
    peak_area: Optional[float] = None
    fwhm: float = Field(1.0, ge=0.1)
    bp_position: float = Field(150.0)
    major_allele_bp: float = Field(150.0)
    major_allele_height: Optional[float] = None
    repeat_unit_len: int = Field(4, ge=2, le=6)
    sequence_string: str = ""
    co_eluting_secondary_rfu: float = 0.0
    analytical_threshold: float = 50.0


class ClassifyPeakRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    feature_vector: Optional[FeatureVector24D] = None
    locus_name: Optional[str] = None
    peak_id: Optional[str] = None
    peak_height: Optional[float] = None
    peak_area: Optional[float] = None
    fwhm: Optional[float] = 1.0
    bp_position: Optional[float] = 150.0
    major_allele_bp: Optional[float] = 150.0
    major_allele_height: Optional[float] = None
    repeat_unit_len: Optional[int] = 4
    sequence_string: Optional[str] = ""
    co_eluting_secondary_rfu: Optional[float] = 0.0
    analytical_threshold: Optional[float] = 50.0



class FilterLocusPeaksRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    locus_name: str
    feature_vectors: List[FeatureVector24D]


class ISFGHierarchyRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    locus_name: str
    sequence_or_bracketed_string: str


class MultiLocusPreFilterRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    case_id: str
    locus_peaks_map: Dict[str, List[FeatureVector24D]]
