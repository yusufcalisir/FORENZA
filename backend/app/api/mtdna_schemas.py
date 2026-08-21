"""
FORENZA Mitochondrial DNA (mtDNA) Forensics API — Pydantic v2 Schemas (Module 2.3).
Standards Compliance: ISO/IEC 17025:2017, ISFG Recommendations on Forensic mtDNA Testing (2014, 2020),
SWGDAM Interpretation Guidelines for Mitochondrial DNA Analysis.

Research Source: research/ystr_27_mtdna_empop_lineage_research.md §3 & §4.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, ConfigDict


# ── Variant & Profile Schemas ────────────────────────────────────────────────

class MtDNAVariantSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    position: int = Field(..., description="Nucleotide position on rCRS reference (e.g. 16189, 73, 263, 309).", examples=[16189])
    ref_base: str = Field(..., description="Reference base on rCRS.", examples=["T"])
    alt_base: str = Field(..., description="Observed base or IUPAC heteroplasmy code (e.g. 'C', 'Y', 'R').", examples=["C"])
    region: Optional[str] = Field(None, description="Hypervariable region: 'HV1', 'HV2', 'HV3', or 'CR_OTHER'.", examples=["HV1"])
    variant_type: str = Field("SNP", description="Variant type: 'SNP', 'INSERTION', 'DELETION', 'HETEROPLASMY', 'PHP', 'SUBSTITUTION'.", examples=["SNP"])
    insertion_index: Optional[int] = Field(None, description="Index for insertions (e.g. 1 for 309.1C).", examples=[1])
    notation: Optional[str] = Field(None, description="EMPOP formatted notation (e.g. '16189T', '309.1C', '522del').", examples=["16189T"])


class MtDNAProfileSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    profile_id: str = Field(..., description="Identifier for this mitochondrial profile.", examples=["EVIDENCE-01"])
    haplogroup: Optional[str] = Field(None, description="Inferred Phylotree haplogroup (e.g. 'H1a', 'U5b', 'T2').", examples=["H1a"])
    variants: Union[List[MtDNAVariantSchema], List[str]] = Field(..., description="List of sequence variants relative to rCRS.")


# ── Match Evaluation ─────────────────────────────────────────────────────────

class MtDNAMatchRequest(BaseModel):
    """Request for pairwise mtDNA maternal lineage match evaluation."""
    model_config = ConfigDict(protected_namespaces=())

    evidence: Optional[MtDNAProfileSchema] = None
    suspect: Optional[MtDNAProfileSchema] = None
    profile_a: Optional[Dict[str, Any]] = None
    profile_b: Optional[Dict[str, Any]] = None
    variants_a: Optional[List[str]] = None
    variants_b: Optional[List[str]] = None
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
    model_config = ConfigDict(protected_namespaces=())

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
    predicted_haplogroup_a: str
    predicted_haplogroup_b: str
    verbal_predicate_en: str
    verbal_predicate_tr: str
    prosecutors_fallacy_shield: str


# ── EMPOP Upper Bound ─────────────────────────────────────────────────────────

class EMPOPProbabilityRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    k: int = Field(0, ge=0, description="Haplotype count observed in EMPOP database.", examples=[0])
    n_empop: int = Field(48500, ge=100, description="Total size of EMPOP database.", examples=[48500])
    alpha: float = Field(0.05, ge=0.001, le=0.50, description="Significance level (default 0.05 for 95% bound).", examples=[0.05])


class EMPOPProbabilityResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    observed_count_k: int
    database_size_n: int
    alpha: float
    p_upper_bound: float
    maternal_lr: float
    log10_maternal_lr: float
    is_unobserved: bool
    formula: str


# ── Panel Metadata & Catalogs ────────────────────────────────────────────────

class HypervariableRegionSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    name: str
    start_pos: int
    end_pos: int
    total_bases: int
    key_homopolymeric_tracts: List[str]


class MtDNAPanelMetadataResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    reference_genome: str
    genbank_accession: str
    hypervariable_regions: List[HypervariableRegionSchema]
    supported_iupac_codes: Dict[str, str]
    isfg_rules_active: bool


class MtDnaGoldStandardSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    sample_id: str
    coriell_id: str
    nist_designation: Optional[str]
    haplogroup: str
    population: str
    description: str
    variants: List[str]


class MtDnaCaseworkCohortSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    cohort_id: str
    name: str
    relationship: str
    description: str
    expected_verdict: str
    expected_matches_k: int
    database_size_n: int
    expected_min_lr: float
    profile_a_variants: List[str]
    profile_b_variants: List[str]
