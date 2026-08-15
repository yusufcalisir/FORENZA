"""
FORENZA Mitochondrial DNA (mtDNA) Forensics API — Pydantic v2 Schemas (Module 08).

Covers:
  - mtDNA Control Region Alignment & ISFG Right-Alignment
  - IUPAC Heteroplasmy Modeling
  - EMPOP Database Exact Binomial Bounds
  - Maternal Likelihood Ratio & Evaluative Match Analysis
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# ── Variant & Profile Schemas ────────────────────────────────────────────────

class MtDNAVariantSchema(BaseModel):
    position: int = Field(..., description="Nucleotide position on rCRS reference (e.g. 16189, 73, 263, 309).", examples=[16189])
    ref_base: str = Field(..., description="Reference base on rCRS.", examples=["T"])
    alt_base: str = Field(..., description="Observed base or IUPAC heteroplasmy code (e.g. 'C', 'Y', 'R').", examples=["C"])
    region: Optional[str] = Field(None, description="Hypervariable region: 'HV1', 'HV2', 'HV3', or 'CR_OTHER'.", examples=["HV1"])
    variant_type: str = Field("SNP", description="Variant type: 'SNP', 'INSERTION', 'DELETION', 'HETEROPLASMY'.", examples=["SNP"])
    insertion_index: Optional[int] = Field(None, description="Index for insertions (e.g. 1 for 309.1C).", examples=[1])
    notation: Optional[str] = Field(None, description="EMPOP formatted notation (e.g. '16189T', '309.1C', '522del').", examples=["16189T"])


class MtDNAProfileSchema(BaseModel):
    profile_id: str = Field(..., description="Identifier for this mitochondrial profile.", examples=["EVIDENCE-01"])
    haplogroup: Optional[str] = Field(None, description="Inferred Phylotree haplogroup (e.g. 'H1a', 'U5b', 'T2').", examples=["H1a"])
    variants: List[MtDNAVariantSchema] = Field(..., description="List of sequence variants relative to rCRS.")


# ── Match Evaluation ─────────────────────────────────────────────────────────

class MtDNAMatchRequest(BaseModel):
    """
    Request for pairwise mtDNA maternal lineage match evaluation.
    """
    evidence: MtDNAProfileSchema = Field(..., description="Questioned / evidence sample profile.")
    suspect: MtDNAProfileSchema = Field(..., description="Known / reference sample profile.")
    n_empop: int = Field(
        48500,
        ge=100,
        description="EMPOP representative database sample size (default: 48,500).",
        examples=[48500],
    )
    empop_observed_k: int = Field(
        0,
        ge=0,
        description="Number of times this exact haplotype was observed in EMPOP (0 for rare / novel).",
        examples=[0],
    )


class MtDNAMatchResponse(BaseModel):
    sample1_id: str
    sample2_id: str
    sample1_empop_string: str
    sample2_empop_string: str
    shared_variants: List[str]
    sample1_unique_variants: List[str]
    sample2_unique_variants: List[str]
    point_heteroplasmies_detected: List[str]
    differing_positions_count: int
    match_status: str
    empop_frequency_bound: float
    maternal_lr: float
    log10_maternal_lr: float
    maternal_lineage_verdict: str
    prosecutors_fallacy_shield: str


# ── EMPOP Upper Bound ─────────────────────────────────────────────────────────

class EMPOPProbabilityRequest(BaseModel):
    k: int = Field(0, ge=0, description="Haplotype count observed in EMPOP database.", examples=[0])
    n_empop: int = Field(48500, ge=100, description="Total size of EMPOP database.", examples=[48500])
    alpha: float = Field(0.05, ge=0.001, le=0.50, description="Significance level (default 0.05 for 95% bound).", examples=[0.05])


class EMPOPProbabilityResponse(BaseModel):
    observed_count_k: int
    database_size_n: int
    alpha: float
    p_upper_bound: float
    maternal_lr: float
    log10_maternal_lr: float
    is_unobserved: bool
    formula: str


# ── Panel Metadata ───────────────────────────────────────────────────────────

class HypervariableRegionSchema(BaseModel):
    name: str
    start_pos: int
    end_pos: int
    total_bases: int
    key_homopolymeric_tracts: List[str]


class MtDNAPanelMetadataResponse(BaseModel):
    reference_genome: str
    genbank_accession: str
    hypervariable_regions: List[HypervariableRegionSchema]
    supported_iupac_codes: Dict[str, str]
    isfg_rules_active: bool
