"""
FORENZA X-STR Linkage & Female Kinship API — Pydantic v2 Schemas (Module 07).

Covers:
  - Argus X-12 Kinship Evaluation (PHS, Father-Daughter, PGM-GD, Mother-Son, Full Sisters)
  - Kosambi Mapping Function (cM -> r)
  - Linkage Group Cluster Inspection
  - Argus X-12 Panel Metadata
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# ── Genotype & Profile Schemas ───────────────────────────────────────────────

class XSTRGenotypeSchema(BaseModel):
    locus: str = Field(..., description="Locus name in Argus X-12 (e.g. 'DXS10148').", examples=["DXS10148"])
    allele1: float = Field(..., description="Primary allele repeat count.", examples=[12.0])
    allele2: Optional[float] = Field(None, description="Secondary allele repeat count (None for hemizygous males).", examples=[15.0])


class XSTRProfileSchema(BaseModel):
    profile_id: str = Field(..., description="Profile identifier.", examples=["PERSON-A"])
    is_male: bool = Field(..., description="True if male (hemizygous), False if female.", examples=[False])
    loci: Dict[str, XSTRGenotypeSchema] = Field(
        ...,
        description="Map of X-STR locus names to genotype definitions.",
    )


# ── Kinship Evaluation ───────────────────────────────────────────────────────

class XSTRKinshipRequest(BaseModel):
    """
    Request for Argus X-12 12-locus kinship evaluation.
    """
    profile1: XSTRProfileSchema = Field(..., description="First individual profile.")
    profile2: XSTRProfileSchema = Field(..., description="Second individual profile.")
    relationship: str = Field(
        "PATERNAL_HALF_SISTERS",
        description="Kinship relationship to test: 'PATERNAL_HALF_SISTERS', 'FATHER_DAUGHTER', 'PGM_GD', 'MOTHER_SON', 'FULL_SISTERS'.",
        examples=["PATERNAL_HALF_SISTERS"],
    )
    population_frequencies: Optional[Dict[str, float]] = Field(
        None,
        description="Optional allele frequency overrides per locus.",
    )
    custom_intra_r: Optional[float] = Field(
        None,
        ge=0.0,
        le=0.50,
        description="Optional global recombination rate override r.",
        examples=[0.01],
    )


class LinkageGroupResultSchema(BaseModel):
    group_id: str
    chromosomal_band: str
    evaluated_loci: List[str]
    locus_ki_values: Dict[str, float]
    recombination_rates: List[float]
    group_ki: float
    log10_group_ki: float


class XSTRKinshipResponse(BaseModel):
    profile1_id: str
    profile2_id: str
    profile1_male: bool
    profile2_male: bool
    relationship_tested: str
    combined_ki_x: float
    log10_combined_ki_x: float
    evaluated_loci_count: int
    evaluated_clusters_count: int
    linkage_group_results: List[LinkageGroupResultSchema]
    is_excluded: bool
    kinship_verdict: str
    prosecutors_fallacy_shield: str


# ── Kosambi Mapping Function ─────────────────────────────────────────────────

class KosambiRequest(BaseModel):
    genetic_distance_cm: float = Field(
        ...,
        ge=0.0,
        description="Genetic distance in centiMorgans (cM).",
        examples=[18.5],
    )


class KosambiResponse(BaseModel):
    genetic_distance_cm: float
    recombination_fraction_r: float
    formula: str


# ── Panel Metadata ───────────────────────────────────────────────────────────

class XSTRLocusMetadataSchema(BaseModel):
    locus_name: str
    linkage_group: str
    chromosomal_band: str
    physical_position_mb: float
    genetic_map_cm: float
    intra_cluster_r: Optional[float]


class LinkageGroupMetadataSchema(BaseModel):
    group_id: str
    chromosomal_band: str
    loci: List[str]
    recombination_rates: List[float]
    genetic_distances_cm: List[float]


class ArgusX12PanelMetadataResponse(BaseModel):
    panel_name: str
    total_loci: int
    total_linkage_groups: int
    linkage_groups: List[LinkageGroupMetadataSchema]
    loci: List[XSTRLocusMetadataSchema]
