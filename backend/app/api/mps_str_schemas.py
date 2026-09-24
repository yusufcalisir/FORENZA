"""
FORENZA MPS STR REST API: Pydantic v2 Schemas.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, ConfigDict, Field

from node.services.forensic.genomics.mps_str.schemas import (
    ParsedSTRSequence,
    SingleLocusMPSGenotype,
    GenotypeProfileMPS,
)
from node.services.forensic.genomics.mps_str.se33_engine import (
    SE33GenotypeAnalysisReport
)
from node.services.forensic.genomics.mps_str.mixture_deconvolution import (
    MultiLocusMixtureReport,
    DeconvolvedContributor
)
from node.services.forensic.genomics.mps_str.biostatistics import (
    LocusBiostatisticsReport,
    MultiLocusDiversitySummary
)
from node.services.forensic.genomics.mps_str.linkage_guard import (
    SyntenicPairKinshipAudit,
    FlankingRescueReport
)
from node.services.forensic.genomics.mps_str.signal_filter import (
    MPSSignalFilterResult,
    FilteredArtifact
)
from node.services.forensic.genomics.mps_str.frequency_matrices import (
    LocusRegistryItem
)


class ParseSequenceRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    locus_name: str = Field(..., examples=["SE33", "D3S1358", "TH01"])
    sequence_string: str = Field(..., examples=["CTTC [CTTT]17_rs9362477[C>T]"])


class AnalyzeSE33Request(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sequence_alleles: Optional[List[str]] = Field(
        None,
        examples=[[
            "CTTC [CTTT]17_rs9362477[C>T]",
            "CTTC [CTTT]10 TT [CTTT]16_rs1277875566[T>C]"
        ]]
    )
    sequence_1: Optional[str] = None
    sequence_2: Optional[str] = None
    sample_id: Optional[str] = None
    population: str = Field("GLOBAL_COMPOSITE", examples=["CAUCASIAN", "AFRICAN_AMERICAN", "GLOBAL_COMPOSITE"])


class AnalyzeGenotypeRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    locus_name: str = Field(..., examples=["SE33", "D3S1358", "VWA"])
    sequence_alleles: List[str] = Field(..., examples=[["[TCTA]11 [TCTG]4 [TCTA]1", "[TCTA]11 [TCTG]4 [TCTA]2"]])
    population: str = Field("GLOBAL_COMPOSITE")


class AnalyzeGenotypeReport(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    locus_name: str
    ce_genotype: str
    mps_genotype: str
    ce_single_locus_lr: float
    mps_single_locus_lr: float
    information_gain_ratio: float
    is_fully_concordant: bool
    quality_assurance_notes: List[str]


class MixtureDeconvolutionRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sample_id: str = Field(..., examples=["MIX_SAMPLE_101"])
    locus_sequence_map: Dict[str, List[str]]
    contributors: List[DeconvolvedContributor]
    population: str = Field("GLOBAL_COMPOSITE")


class BiostatisticsRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    locus_names: List[str] = Field(..., examples=[["SE33", "D3S1358", "D21S11", "VWA", "TH01"]])
    population: str = Field("GLOBAL_COMPOSITE")


class SyntenicLinkageRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    d6s1043_lr: float = Field(..., ge=0.0, examples=[150.0])
    se33_lr: float = Field(..., ge=0.0, examples=[3200.0])
    apply_single_locus_fallback: bool = Field(True)


class FlankingRescueRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sample_id: str = Field("VECTOR_MPS_04", examples=["VECTOR_MPS_04"])
    observed_sequences: List[str] = Field(
        ...,
        examples=[["[TCTA]11 [TCTG]4 [TCTA]1", "[TCTA]11 [TCTG]4 [TCTA]2_rs771794429[G>A]"]]
    )
    apparent_ce_call: float = Field(14.0, examples=[14.0])


class FilterStutterRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    reads: Dict[str, int] = Field(..., examples=[{"CTTC [CTTT]17": 2800, "CTTC [CTTT]16": 160, "[CTTT]18": 1040}])
    analytical_threshold_ratio: float = Field(0.05, ge=0.0, le=0.50)
    stutter_threshold_ratio: float = Field(0.10, ge=0.0, le=0.50)


__all__ = [
    "ParseSequenceRequest",
    "AnalyzeSE33Request",
    "AnalyzeGenotypeRequest",
    "AnalyzeGenotypeReport",
    "MixtureDeconvolutionRequest",
    "BiostatisticsRequest",
    "SyntenicLinkageRequest",
    "FlankingRescueRequest",
    "FilterStutterRequest",
]
