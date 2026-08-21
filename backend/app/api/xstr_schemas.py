"""
FORENZA X-STR Linkage & Female Kinship API — Pydantic v2 Schemas (Module 2.2).
Standards Compliance: ISO/IEC 17025:2017, ISFG Recommendations on X-STR Testing (2012),
ENFSI Evaluative Reporting (2017).

Research Source: research/pillar_2_lineage_kinship_research.md §2.1 & §2.2.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, ConfigDict


# ── Genotype & Profile Schemas ───────────────────────────────────────────────

class XSTRGenotypeSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    locus: str = Field(..., description="Locus name in Argus X-12 (e.g. 'DXS10148').", examples=["DXS10148"])
    allele1: float = Field(..., description="Primary allele repeat count.", examples=[12.0])
    allele2: Optional[float] = Field(None, description="Secondary allele repeat count (None for hemizygous males).", examples=[15.0])


class XSTRProfileSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    profile_id: str = Field(..., description="Profile identifier.", examples=["PERSON-A"])
    is_male: bool = Field(..., description="True if male (hemizygous), False if female.", examples=[False])
    loci: Dict[str, Union[XSTRGenotypeSchema, List[float], float, str]] = Field(
        ...,
        description="Map of X-STR locus names to genotype definitions or allele arrays.",
    )


# ── Kinship Evaluation Schemas ───────────────────────────────────────────────

class XSTRKinshipRequest(BaseModel):
    """Request for Argus X-12 12-locus kinship evaluation."""
    model_config = ConfigDict(protected_namespaces=())

    profile1: Optional[XSTRProfileSchema] = None
    profile2: Optional[XSTRProfileSchema] = None
    profile_a: Optional[Dict[str, Any]] = None
    profile_b: Optional[Dict[str, Any]] = None
    sex_a: str = Field("FEMALE", description="Sex of Person A ('FEMALE' or 'MALE').")
    sex_b: str = Field("FEMALE", description="Sex of Person B ('FEMALE' or 'MALE').")
    relationship: str = Field(
        "PATERNAL_HALF_SISTERS",
        description="Kinship relationship: 'PATERNAL_HALF_SISTERS', 'FATHER_DAUGHTER', 'PATERNAL_GRANDMOTHER_GRANDDAUGHTER', 'MOTHER_SON', 'FULL_SISTERS', 'UNRELATED'.",
        examples=["PATERNAL_HALF_SISTERS"],
    )
    population_frequencies: Optional[Dict[str, Any]] = Field(
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
    model_config = ConfigDict(protected_namespaces=())

    group_id: str
    chromosomal_band: str
    evaluated_loci: List[str]
    locus_ki_values: Dict[str, float]
    recombination_rates: List[float]
    group_ki: float
    log10_group_ki: float


class XSTRKinshipResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

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
    verbal_predicate_en: str
    verbal_predicate_tr: str
    prosecutors_fallacy_shield: str


# ── Kosambi Mapping Function ─────────────────────────────────────────────────

class KosambiRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    genetic_distance_cm: float = Field(
        ...,
        ge=0.0,
        description="Genetic distance in centiMorgans (cM).",
        examples=[18.5],
    )


class KosambiResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    genetic_distance_cm: float
    recombination_fraction_r: float
    formula: str


# ── Panel Metadata & Catalogs ────────────────────────────────────────────────

class XSTRLocusMetadataSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    locus_name: str
    linkage_group: str
    chromosomal_band: str
    physical_position_mb: float
    genetic_map_cm: float
    intra_cluster_r: Optional[float]


class LinkageGroupMetadataSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    group_id: str
    chromosomal_band: str
    loci: List[str]
    recombination_rates: List[float]
    genetic_distances_cm: List[float]


class ArgusX12PanelMetadataResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    panel_name: str
    total_loci: int
    total_linkage_groups: int
    linkage_groups: List[LinkageGroupMetadataSchema]
    loci: List[XSTRLocusMetadataSchema]


class XStrPopulationMetadataSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    code: str
    name: str
    sample_size_n: int
    citation: str
    description: str


class XStrGoldStandardSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    sample_id: str
    coriell_id: str
    nist_designation: Optional[str]
    sex: str
    population: str
    description: str
    x_str_genotypes: Dict[str, List[float]]


class XStrCaseworkCohortSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    cohort_id: str
    name: str
    relationship: str
    sex_a: str
    sex_b: str
    description: str
    expected_matching_loci: int
    expected_min_ki: float
    profile_a: Dict[str, List[float]]
    profile_b: Dict[str, List[float]]
