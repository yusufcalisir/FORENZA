"""
Forensic Genetic Genealogy (FGG / IGG) Pydantic Schemas.

Compliant with SWGDAM FGG (2023), US DOJ Interim Policy (2019), and ISO/IEC 17025:2017.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class PlatformFormatEnum(str, Enum):
    """Supported dense SNP array, WGS, and DTC raw format types."""
    ILLUMINA_GDA = "ILLUMINA_GDA"              # Illumina Global Diversity Array (~1.8M SNPs)
    ILLUMINA_GSA = "ILLUMINA_GSA"              # Illumina Global Screening Array (~650k-750k SNPs)
    THERMO_AXIOM_PMDA = "THERMO_AXIOM_PMDA"    # Thermo Fisher Axiom PMDA (~850k SNPs)
    TWENTY_THREE_AND_ME_V5 = "TWENTY_THREE_AND_ME_V5" # 23andMe v5 format
    TWENTY_THREE_AND_ME_V4 = "TWENTY_THREE_AND_ME_V4" # 23andMe v4 format
    ANCESTRY_DNA = "ANCESTRY_DNA"              # AncestryDNA tab-delimited format
    FAMILY_TREE_DNA_CSV = "FAMILY_TREE_DNA_CSV"# FamilyTreeDNA CSV format
    GEDMATCH_CSV = "GEDMATCH_CSV"              # GEDmatch CSV format
    VCF_WGS_PHASED = "VCF_WGS_PHASED"          # Whole Genome Sequencing 30x-60x VCF 4.2/4.3
    VCF_LOW_PASS_IMPUTED = "VCF_LOW_PASS_IMPUTED"# Low-pass 1x-3x imputed VCF
    UNKNOWN = "UNKNOWN"


class GenotypeStateEnum(int, Enum):
    """
    2-bit packed genotype state representation.
    00_2 = 0 : Homozygous Reference (0/0)
    01_2 = 1 : Heterozygous (0/1 or 1/0)
    10_2 = 2 : Missing / No-Call (./. or --)
    11_2 = 3 : Homozygous Alternate (1/1)
    """
    HOM_REF = 0
    HET = 1
    NO_CALL = 2
    HOM_ALT = 3


class IBDStateEnum(int, Enum):
    """Identity-by-Descent state."""
    IBD0 = 0   # 0 alleles shared IBD
    IBD1 = 1   # 1 allele shared IBD
    IBD2 = 2   # 2 alleles shared IBD (both copies identical)


class IBDSegment(BaseModel):
    """Contiguous chromosomal segment shared Identical-by-Descent."""
    model_config = ConfigDict(protected_namespaces=())

    chromosome: str = Field(..., description="Chromosome name (1-22)")
    start_bp: int = Field(..., description="Physical start base-pair coordinate (GRCh38)")
    end_bp: int = Field(..., description="Physical end base-pair coordinate (GRCh38)")
    start_cm: float = Field(..., description="Genetic map start position in centimorgans (cM)")
    end_cm: float = Field(..., description="Genetic map end position in centimorgans (cM)")
    length_cm: float = Field(..., description="Segment genetic length in centimorgans (cM)")
    snp_count: int = Field(..., description="Number of SNPs in this segment")
    density_snps_per_cm: float = Field(..., description="SNP density: snp_count / length_cm")
    ibd_state: IBDStateEnum = Field(default=IBDStateEnum.IBD1, description="IBD sharing state (IBD1 or IBD2)")


class PairwiseIBDResult(BaseModel):
    """Complete pairwise IBD and kinship summary between two individuals."""
    model_config = ConfigDict(protected_namespaces=())

    sample_a_id: str
    sample_b_id: str
    total_shared_cm: float = Field(..., description="Total qualifying IBD segment length (sum of segments >= 7.0 cM)")
    longest_segment_cm: float = Field(..., description="Longest single contiguous shared IBD segment length")
    segment_count: int = Field(..., description="Total number of qualifying IBD segments")
    segments: List[IBDSegment] = Field(default_factory=list, description="List of detected IBD segments")
    cotterman_k0: float = Field(..., description="Estimated Cotterman k0 (probability of 0 alleles IBD)")
    cotterman_k1: float = Field(..., description="Estimated Cotterman k1 (probability of 1 allele IBD)")
    cotterman_k2: float = Field(..., description="Estimated Cotterman k2 (probability of 2 alleles IBD)")
    kinship_phi: float = Field(..., description="Kinship coefficient: Phi = 0.5*k2 + 0.25*k1")
    wright_r: float = Field(..., description="Wright's coefficient of relationship: r = 2*Phi = k2 + 0.5*k1")
    king_phi: float = Field(..., description="KING-robust admixed kinship estimate")
    qualifying_segments_count: int = Field(..., description="Count of segments passing the 7 cM threshold")


class KinshipDegreeEnum(str, Enum):
    """Forensic Genealogical Relationship Degree taxonomy."""
    DEGREE_0_TWIN_SELF = "DEGREE_0_TWIN_SELF"                    # Monozygotic Twin / Self / Duplicate
    DEGREE_1_PARENT_CHILD = "DEGREE_1_PARENT_CHILD"              # Parent / Child (100% IBD1)
    DEGREE_1_FULL_SIBLING = "DEGREE_1_FULL_SIBLING"              # Full Sibling (~25% IBD2, 50% IBD1)
    DEGREE_2_HALF_SIB_AVUNCULAR = "DEGREE_2_HALF_SIB_AVUNCULAR"  # Half-Sibling / Grandparent / Uncle-Aunt-Niece-Nephew
    DEGREE_3_FIRST_COUSIN = "DEGREE_3_FIRST_COUSIN"              # 1st Cousin (1C)
    DEGREE_4_1C1R_HALF_1C = "DEGREE_4_1C1R_HALF_1C"              # 1st Cousin Once Removed (1C1R) / Half-1C
    DEGREE_5_SECOND_COUSIN = "DEGREE_5_SECOND_COUSIN"            # 2nd Cousin (2C)
    DEGREE_6_THIRD_COUSIN = "DEGREE_6_THIRD_COUSIN"              # 3rd Cousin (3C)
    DEGREE_7_FOURTH_COUSIN_DISTANT = "DEGREE_7_FOURTH_COUSIN_DISTANT" # 4th Cousin (4C) / Distant Genealogical Match
    UNRELATED = "UNRELATED"                                      # Unrelated (< 15 cM)


class RelationshipCandidate(BaseModel):
    """Ranked relationship candidate with posterior probability."""
    model_config = ConfigDict(protected_namespaces=())

    degree: KinshipDegreeEnum
    relationship_label: str
    probability: float = Field(..., description="Posterior probability under Shared cM model (0.0 to 1.0)")
    expected_mean_cm: float
    typical_cm_range_min: float
    typical_cm_range_max: float
    description: str


class KinshipClassificationResult(BaseModel):
    """Comprehensive relationship classification and endogamy evaluation."""
    model_config = ConfigDict(protected_namespaces=())

    sample_a_id: str
    sample_b_id: str
    raw_shared_cm: float
    adjusted_shared_cm: float = Field(..., description="Shared cM adjusted for background endogamy / pedigree collapse")
    longest_segment_cm: float
    segment_count: int
    endogamy_roh_score_a: float = Field(..., description="Inbreeding coefficient F_ROH for sample A")
    endogamy_roh_score_b: float = Field(..., description="Inbreeding coefficient F_ROH for sample B")
    endogamy_adjustment_applied_cm: float
    top_candidate: RelationshipCandidate
    all_candidates: List[RelationshipCandidate] = Field(default_factory=list)
    bivariate_morphology_note: str = Field(..., description="Morphological note on L_max vs segment count resolution")
    is_endogamy_suspected: bool = Field(default=False)


class SexEnum(str, Enum):
    """Biological sex classification."""
    MALE = "MALE"
    FEMALE = "FEMALE"
    UNKNOWN = "UNKNOWN"


class PedigreeNode(BaseModel):
    """A single node (individual) in the reconstructed pedigree DAG."""
    model_config = ConfigDict(protected_namespaces=())

    node_id: str
    label: str
    sex: SexEnum = SexEnum.UNKNOWN
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    is_genotyped: bool = False
    y_haplogroup: Optional[str] = None
    mtdna_haplogroup: Optional[str] = None
    generation_index: int = Field(default=0, description="Generational depth (0 = target, -1 = parents, -2 = grandparents)")
    parents: List[str] = Field(default_factory=list, description="Parent node IDs")
    children: List[str] = Field(default_factory=list, description="Child node IDs")


class PedigreeEdge(BaseModel):
    """Directed edge in the pedigree graph."""
    model_config = ConfigDict(protected_namespaces=())

    source_id: str = Field(..., description="Parent node ID")
    target_id: str = Field(..., description="Child node ID")
    relationship_type: str = Field(default="PARENT_CHILD")


class MRCACluster(BaseModel):
    """Most Recent Common Ancestor (MRCA) triangulated cluster."""
    model_config = ConfigDict(protected_namespaces=())

    cluster_id: str
    mrca_couple_label: str
    shared_matches_ids: List[str]
    overlapping_chromosome: str
    start_bp: int
    end_bp: int
    overlap_length_cm: float
    estimated_generation_depth: int
    uniparental_lineage_status: str = "CONCORDANT"


class PedigreeReconstructionResult(BaseModel):
    """Complete multi-generational reconstructed pedigree tree."""
    model_config = ConfigDict(protected_namespaces=())

    target_sample_id: str
    nodes: List[PedigreeNode] = Field(default_factory=list)
    edges: List[PedigreeEdge] = Field(default_factory=list)
    mrca_clusters: List[MRCACluster] = Field(default_factory=list)
    composite_log_likelihood: float = Field(..., description="Bonsai composite log-likelihood score")
    generation_depth: int
    pruned_branches_count: int = 0
    investigative_leads_summary: str


class QualifyingOffenseEnum(str, Enum):
    """Statutory qualifying offenses authorized for FGG under US DOJ & State statutes."""
    HOMICIDE = "HOMICIDE"
    SEXUAL_ASSAULT = "SEXUAL_ASSAULT"
    KIDNAPPING_AGGRAVATED = "KIDNAPPING_AGGRAVATED"
    UNIDENTIFIED_HUMAN_REMAINS_UHR = "UNIDENTIFIED_HUMAN_REMAINS_UHR"
    NON_QUALIFYING_PROPERTY_CRIME = "NON_QUALIFYING_PROPERTY_CRIME"


class JurisdictionStatuteEnum(str, Enum):
    """Governing statutory frameworks for FGG investigations."""
    US_DOJ_INTERIM_2019 = "US_DOJ_INTERIM_2019"
    US_MARYLAND_TITLE_17 = "US_MARYLAND_TITLE_17"
    US_MONTANA_MCA_44_4_503 = "US_MONTANA_MCA_44_4_503"
    US_UTAH_SB_156 = "US_UTAH_SB_156"
    EU_GDPR_LED_2016_680 = "EU_GDPR_LED_2016_680"
    SWEDEN_POLISEN_2025 = "SWEDEN_POLISEN_2025"


class LegalComplianceCase(BaseModel):
    """Case parameters for statutory FGG legal validation."""
    model_config = ConfigDict(protected_namespaces=())

    case_id: str
    jurisdiction: JurisdictionStatuteEnum = JurisdictionStatuteEnum.US_DOJ_INTERIM_2019
    offense_type: QualifyingOffenseEnum
    is_codis_exhausted: bool = Field(..., description="Must be True: Traditional CODIS search yielded no match")
    prosecutor_authorization_id: Optional[str] = None
    judicial_warrant_ref: Optional[str] = None
    destruction_plan_mandated: bool = False
    destruction_plan_certified: bool = False
    opt_in_matches_only_enforced: bool = True


class LegalComplianceValidation(BaseModel):
    """Validation outcome for FGG legal compliance and lead governance."""
    model_config = ConfigDict(protected_namespaces=())

    case_id: str
    is_compliant: bool
    violations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    lead_disclaimer_notice: str
    audit_record_hash: str


class SNPRecord(BaseModel):
    """Single Nucleotide Polymorphism record."""
    model_config = ConfigDict(protected_namespaces=())

    rsid: str = Field(..., description="dbSNP Reference SNP identifier (e.g. rs12345)")
    chromosome: str = Field(..., description="Chromosome identifier (1-22, X, Y, MT)")
    position_bp: int = Field(..., description="1-based physical base pair coordinate in GRCh38")
    allele1: str = Field(..., description="First observed base allele (A, C, G, T or -)")
    allele2: str = Field(..., description="Second observed base allele (A, C, G, T or -)")
    genotype_call: str = Field(..., description="Two-character concatenated genotype call (e.g. 'AA', 'CT', '--')")
    genotype_state: GenotypeStateEnum = Field(..., description="2-bit enumerated genotype state")
    genetic_pos_cm: Optional[float] = Field(default=None, description="Interpolated genetic map position in centimorgans (cM)")


class BitwiseGenotypeBlock(BaseModel):
    """Compressed 2-bit packed genotype array for a specific chromosome."""
    model_config = ConfigDict(protected_namespaces=())

    chromosome: str
    snp_count: int
    packed_bytes_hex: str = Field(..., description="Hexadecimal string of 2-bit packed bytes (4 SNPs per byte)")
    positions_bp: List[int] = Field(default_factory=list, description="Array of physical bp positions")
    genetic_positions_cm: List[float] = Field(default_factory=list, description="Array of genetic cM coordinates")
    rsids: List[str] = Field(default_factory=list, description="Array of rsIDs")


class ProfileQCReport(BaseModel):
    """Comprehensive Quality Control and sample degradation evaluation."""
    model_config = ConfigDict(protected_namespaces=())

    total_snps_evaluated: int
    called_snps: int
    missing_snps: int
    call_rate_percentage: float = Field(..., description="Sample call rate: (called / total) * 100")
    heterozygosity_rate_percentage: float = Field(..., description="Heterozygosity rate: (het / called) * 100")
    is_call_rate_valid: bool = Field(..., description="True if call rate >= 95.0% (ISO 17025 standard)")
    degradation_warning: bool = Field(..., description="True if severe call rate loss (< 90.0%) detected")
    contamination_warning: bool = Field(..., description="True if heterozygosity is abnormally elevated (> 35.0%)")
    detected_platform: PlatformFormatEnum
    assembly_version: str = Field(default="GRCh38")


class IngestedFGGProfile(BaseModel):
    """Complete ingested, normalized, and bitwise-packed FGG profile."""
    model_config = ConfigDict(protected_namespaces=())

    profile_id: str
    source_filename: str
    platform: PlatformFormatEnum
    assembly_version: str = "GRCh38"
    qc_report: ProfileQCReport
    chromosome_blocks: Dict[str, BitwiseGenotypeBlock] = Field(default_factory=dict)
