"""
FORENZA Y-STR Haplotype Forensics & Population Frequency API — Pydantic v2 Schemas (Module 06).

Covers all endpoints:
  - 27-Locus Y-FILER Plus Haplotype Match Evaluation (Inclusion / Exclusion / Mutation)
  - Clopper-Pearson 95% Exact Binomial Upper Bound (k=0 and k>0)
  - Brenner / Surveyor Subpopulation Correction (theta)
  - Discrete Laplace Clonal Clustering Smoothing
  - Minimum Male Contributor Estimation (N_male) from Y-STR Mixture
  - Stepwise Mutation Model (SMM) Father-Son Paternity Discrepancies
  - Panel Metadata Inspection
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# ── Match Evaluation ─────────────────────────────────────────────────────────

class YSTRMatchRequest(BaseModel):
    """
    Request for full 27-locus Y-FILER Plus match evaluation.
    """
    evidence_id: str = Field("EVIDENCE-01", description="Evidence sample identifier.")
    suspect_id: str = Field("SUSPECT-01", description="Suspect sample identifier.")
    evidence_markers: Dict[str, float] = Field(
        ...,
        description="Evidence Y-STR allele map (e.g. {'DYS19': 14.0, 'DYS390': 24.0, ...}).",
        examples=[{"DYS19": 14.0, "DYS389I": 13.0, "DYS390": 24.0, "DYS570": 17.0}],
    )
    suspect_markers: Dict[str, float] = Field(
        ...,
        description="Suspect Y-STR allele map.",
        examples=[{"DYS19": 14.0, "DYS389I": 13.0, "DYS390": 24.0, "DYS570": 17.0}],
    )
    database_count_k: int = Field(
        0,
        ge=0,
        description="Number of times this haplotype was observed in reference database (k). Research §1.1.",
        examples=[0],
    )
    database_size_n: int = Field(
        25000,
        ge=1,
        description="Total database size (N, e.g. 25,000 for Y-HRD). Research §1.1.",
        examples=[25000],
    )
    theta: float = Field(
        0.03,
        ge=0.0,
        le=0.10,
        description="Brenner subpopulation coancestry correction theta (default 0.03).",
        examples=[0.03],
    )


class SMMTransitionSchema(BaseModel):
    locus_name: str
    father_allele: float
    son_allele: float
    step_distance_m: int
    is_mutation: bool
    mutation_rate: float
    transition_probability: float
    log10_transition_probability: float
    mutation_classification: str


class ClopperPearsonSchema(BaseModel):
    observed_count_k: int
    database_size_n: int
    alpha: float
    p_upper: float
    p_lower: float
    point_estimate: float
    lr_upper_bound: float
    log10_lr_upper_bound: float
    method_formula: str


class BrennerSchema(BaseModel):
    observed_count_k: int
    database_size_n: int
    theta: float
    p_brenner: float
    lr_brenner: float
    log10_lr_brenner: float


class YSTRMatchResponse(BaseModel):
    evidence_id: str
    suspect_id: str
    matching_loci_count: int
    total_evaluated_loci: int
    mismatch_loci_count: int
    match_status: str
    database_count_k: int
    database_size_n: int
    theta: float
    clopper_pearson: ClopperPearsonSchema
    brenner: BrennerSchema
    smm_mutations: List[SMMTransitionSchema]
    paternal_lineage_verdict: str
    prosecutors_fallacy_shield: str


# ── Clopper-Pearson Exact Bound ──────────────────────────────────────────────

class ClopperPearsonRequest(BaseModel):
    """
    Request for Clopper-Pearson 95% exact binomial upper bound.
    """
    observed_count_k: int = Field(
        0,
        ge=0,
        description="Observed haplotype count in database (k). Research §1.1.",
        examples=[0],
    )
    database_size_n: int = Field(
        25000,
        ge=1,
        description="Total database size (N). Research §1.1.",
        examples=[25000],
    )
    alpha: float = Field(
        0.05,
        gt=0.0,
        lt=1.0,
        description="Significance level (default 0.05 for 95% confidence).",
        examples=[0.05],
    )


# ── Brenner Subpopulation Correction ─────────────────────────────────────────

class BrennerFrequencyRequest(BaseModel):
    """
    Request for Brenner / Surveyor subpopulation correction.
    """
    observed_count_k: int = Field(
        0,
        ge=0,
        description="Observed haplotype count (k).",
        examples=[0],
    )
    database_size_n: int = Field(
        25000,
        ge=1,
        description="Database size (N).",
        examples=[25000],
    )
    theta: float = Field(
        0.03,
        ge=0.0,
        le=0.10,
        description="Subpopulation coancestry theta (default 0.03).",
        examples=[0.03],
    )


# ── Discrete Laplace Smoothing ───────────────────────────────────────────────

class LaplaceClusterSchema(BaseModel):
    weight: float = Field(..., gt=0.0, description="Cluster prior weight w_c.")
    center_haplotype: Dict[str, float] = Field(..., description="Center haplotype mu_cl for each locus.")
    scale_parameters: Dict[str, float] = Field(..., description="Scale parameter lambda_cl for each locus.")


class DiscreteLaplaceRequest(BaseModel):
    """
    Request for Discrete Laplace clonal clustering frequency estimation.
    """
    haplotype: Dict[str, float] = Field(
        ...,
        description="Target 27-locus Y-STR haplotype.",
        examples=[{"DYS19": 14.0, "DYS389I": 13.0, "DYS390": 24.0}],
    )
    clusters: List[LaplaceClusterSchema] = Field(
        ...,
        min_length=1,
        description="List of clonal clusters with weights, centers, and scales.",
    )


class DiscreteLaplaceResponse(BaseModel):
    haplotype: Dict[str, float]
    num_clusters: int
    haplotype_probability: float
    log10_probability: float
    lr: float
    log10_lr: float


# ── Mixture Deconvolution ───────────────────────────────────────────────────

class YSTRMixtureDeconvRequest(BaseModel):
    """
    Request for minimum male contributor estimation from Y-STR mixture profile.
    """
    locus_alleles: Dict[str, List[float]] = Field(
        ...,
        description="Map of locus names to list of observed alleles in the mixture.",
        examples=[{
            "DYS19": [14.0, 15.0],
            "DYS389I": [13.0, 14.0, 15.0],
            "DYS385a_b": [11.0, 14.0, 15.0, 16.0, 17.0],
        }],
    )


class YSTRMixtureDeconvResponse(BaseModel):
    minimum_male_contributors: int
    locus_with_max_alleles: str
    max_allele_count: int
    multi_copy_locus_flag: bool
    locus_allele_counts: Dict[str, int]
    interpretation: str


# ── Stepwise Mutation Model (SMM) ────────────────────────────────────────────

class SMMTransitionRequest(BaseModel):
    """
    Request for SMM father-son transmission probability at a specific Y-STR locus.
    """
    father_allele: float = Field(..., description="Father's repeat count (a_f).", examples=[14.0])
    son_allele: float = Field(..., description="Son's repeat count (a_s).", examples=[15.0])
    locus_name: str = Field(..., description="Y-STR locus name (e.g. 'DYS570').", examples=["DYS570"])
    p_step: float = Field(0.10, gt=0.0, lt=1.0, description="Step geometric decay parameter p (default 0.10).")


# ── Panel Metadata ───────────────────────────────────────────────────────────

class YSTRLocusMetadataSchema(BaseModel):
    locus_name: str
    sequence_type: str
    mutation_class: str
    mutation_rate: float
    repeat_motif: str
    is_multicopy: bool
    is_rapidly_mutating: bool


class YSTRPanelMetadataResponse(BaseModel):
    panel_name: str
    total_loci: int
    standard_loci_count: int
    rapidly_mutating_loci_count: int
    loci: List[YSTRLocusMetadataSchema]
