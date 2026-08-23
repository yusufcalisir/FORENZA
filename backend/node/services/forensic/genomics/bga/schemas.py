"""
Pydantic Schemas and Domain Types for Forensic Biogeographical Ancestry (BGA) & AIMs.

Compliant with ISFG (2020), ENFSI (2017), VISAGE Consortium, and FROG-kb specifications.
"""

from enum import Enum
from typing import Dict, List, Optional, Set, Any
from pydantic import BaseModel, Field, ConfigDict


class AIMPanelTypeEnum(str, Enum):
    """Supported Ancestry Informative Marker (AIM) and Microhaplotype panels."""
    KIDD_55 = "KIDD_55"
    PRECISION_ID_165 = "PRECISION_ID_165"
    EUROFORGEN_128 = "EUROFORGEN_128"
    VISAGE_BASIC_153 = "VISAGE_BASIC_153"
    VISAGE_ENHANCED = "VISAGE_ENHANCED"
    MICROHAPLOTYPE_74 = "MICROHAPLOTYPE_74"
    MICROHAPLOTYPE_153 = "MICROHAPLOTYPE_153"
    CUSTOM = "CUSTOM"


class PlatformFormatEnum(str, Enum):
    """Genotype data source platform or file serialization format."""
    AMPLISEQ_TSV = "AMPLISEQ_TSV"
    FORENSEQ_VCF = "FORENSEQ_VCF"
    SNAPSHOT_CE_TABLE = "SNAPSHOT_CE_TABLE"
    MICROARRAY_23ANDME = "MICROARRAY_23ANDME"
    MICROARRAY_ANCESTRYDNA = "MICROARRAY_ANCESTRYDNA"
    MICROARRAY_FTDNA = "MICROARRAY_FTDNA"
    WGS_VCF_4_2 = "WGS_VCF_4_2"
    UNKNOWN = "UNKNOWN"


class GenomicAssemblyEnum(str, Enum):
    """Human reference genome assembly coordinate builds."""
    GRCH37 = "GRCh37"
    GRCH38 = "GRCh38"


class QCStatusEnum(str, Enum):
    """Sample Quality Control verdict status."""
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


class JurisdictionCodeEnum(str, Enum):
    """Statutory forensic jurisdictions and legal governance frameworks."""
    GERMANY_STPO = "GERMANY_STPO"              # German § 81e StPO (Phenotyping YES, BGA BANNED)
    NETHERLANDS_SV = "NETHERLANDS_SV"          # Dutch Art. 151a Sv (Examining magistrate check)
    UK_PACE = "UK_PACE"                        # UK PACE 1984 & BFEG (Intelligence only)
    USA_FOURTH_AMENDMENT = "USA_FOURTH_AMENDMENT" # US Police Lead Generation
    ISFG_INTERNATIONAL = "ISFG_INTERNATIONAL"  # ISFG / ENFSI Evaluative Reporting


class GovernanceComplianceResult(BaseModel):
    """Statutory Legal Compliance Report and Redaction Record."""
    model_config = ConfigDict(protected_namespaces=())

    jurisdiction: JurisdictionCodeEnum
    is_phenotyping_authorized: bool = True
    is_ancestry_authorized: bool = True
    ancestry_redacted: bool = False
    redaction_statutory_notice: Optional[str] = None
    magistrate_authorization_status: Optional[str] = None
    prosecutors_fallacy_shield: str
    reporting_classification: str = "INVESTIGATIVE_LEAD_ONLY"



class ReferenceSystemEnum(str, Enum):
    """Supported population genomics reference databases."""
    ONE_THOUSAND_GENOMES_26 = "ONE_THOUSAND_GENOMES_26"
    GNOMAD_V4_9POP = "GNOMAD_V4_9POP"
    HGDP_CEPH_54 = "HGDP_CEPH_54"
    SGDP_142 = "SGDP_142"
    FROG_KB_5POP = "FROG_KB_5POP"


class ContinentalSuperPopEnum(str, Enum):
    """Continental and sub-continental biogeographical ancestry reference clusters."""
    EUR = "EUR"  # European (North, South, Finnish, Central)
    AFR = "AFR"  # African (Sub-Saharan, West, East)
    EAS = "EAS"  # East Asian
    SAS = "SAS"  # South Asian
    AMR = "AMR"  # Indigenous / Admixed American
    MID = "MID"  # Middle Eastern / North African
    OCE = "OCE"  # Oceanian
    ASJ = "ASJ"  # Ashkenazi Jewish
    OTH = "OTH"  # Other / Admixed


class PopulationFrequencyEntry(BaseModel):
    """Single population allele frequency record."""
    model_config = ConfigDict(protected_namespaces=())

    population_code: str = Field(..., description="Standard population or super-population code")
    reference_system: ReferenceSystemEnum = Field(..., description="Source reference database")
    ref_frequency: float = Field(..., description="Reference allele frequency (0.0 - 1.0)")
    alt_frequency: float = Field(..., description="Alternate allele frequency (0.0 - 1.0)")
    sample_size_n: int = Field(default=100, description="Effective diploid sample size")


class PopulationAlleleFrequencies(BaseModel):
    """Collection of population frequencies for a specific locus."""
    model_config = ConfigDict(protected_namespaces=())

    locus_id: str = Field(..., description="rsID or microhaplotype ID")
    frequencies_by_pop: Dict[str, PopulationFrequencyEntry] = Field(default_factory=dict)


class LocusInformativenessReport(BaseModel):
    """Calculated Rosenberg informativeness In and Wright Fst metrics for an AIM locus."""
    model_config = ConfigDict(protected_namespaces=())

    locus_id: str
    reference_system: ReferenceSystemEnum
    rosenberg_in_nats: float = Field(..., description="Informativeness for assignment In (nats)")
    rosenberg_in_bits: float = Field(..., description="Informativeness for assignment In (bits/shannons)")
    wright_fst: float = Field(..., description="Wright's fixation index Fst (0.0 - 1.0)")
    mean_ref_frequency: float
    mean_alt_frequency: float
    population_frequencies: Dict[str, float] = Field(default_factory=dict, description="ALT allele frequencies by pop")


class PCACoordinatesResult(BaseModel):
    """Singular Value Decomposition / PCA Eigenvector Coordinates."""
    model_config = ConfigDict(protected_namespaces=())

    sample_id: str
    pc1: float = Field(..., description="First Principal Component score")
    pc2: float = Field(..., description="Second Principal Component score")
    pc3: float = Field(default=0.0, description="Third Principal Component score")
    variance_explained_ratio: List[float] = Field(default_factory=list, description="Variance explained by top PCs")


class ProcrustesGISResult(BaseModel):
    """Orthogonal Procrustes 3D Geodesic WGS84 Geographic Projection."""
    model_config = ConfigDict(protected_namespaces=())

    sample_id: str
    centroid_latitude: float = Field(..., description="WGS84 latitude (-90.0 to +90.0)")
    centroid_longitude: float = Field(..., description="WGS84 longitude (-180.0 to +180.0)")
    semi_major_axis_km: float = Field(..., description="95% confidence semi-major axis (km)")
    semi_minor_axis_km: float = Field(..., description="95% confidence semi-minor axis (km)")
    ellipse_tilt_degrees: float = Field(..., description="Ellipse orientation angle from North (degrees)")
    nearest_reference_population: str = Field(..., description="Closest reference cluster centroid")
    procrustes_residual_distance: float = Field(default=0.0, description="Frobenius residual norm distance")


class EyeColorPrediction(BaseModel):
    """HIrisPlex 6-SNP Eye Color Probabilities."""
    model_config = ConfigDict(protected_namespaces=())

    blue_probability: float
    brown_probability: float
    intermediate_probability: float
    predicted_category: str
    herc2_gate_status: str = "PRESENT"


class HairColorPrediction(BaseModel):
    """HIrisPlex 22-SNP Hair Color and Shade Probabilities."""
    model_config = ConfigDict(protected_namespaces=())

    blond_probability: float
    brown_probability: float
    red_probability: float
    black_probability: float
    predicted_color: str
    shade_light_probability: float
    shade_dark_probability: float
    predicted_shade: str
    mc1r_loss_of_function_count: int = 0


class SkinColorPrediction(BaseModel):
    """HIrisPlex-S 36-SNP 5-Phototype Skin Pigmentation Probabilities."""
    model_config = ConfigDict(protected_namespaces=())

    very_pale_probability: float
    pale_probability: float
    intermediate_probability: float
    dark_probability: float
    dark_to_black_probability: float
    predicted_category: str


class PhenotypePredictionResult(BaseModel):
    """Unified HIrisPlex-S 41-SNP Complete Phenotypic Assessment."""
    model_config = ConfigDict(protected_namespaces=())

    sample_id: str
    eye_color: EyeColorPrediction
    hair_color: HairColorPrediction
    skin_color: SkinColorPrediction
    phenotype_summary: str





class AIMLocus(BaseModel):
    """Registry definition for an individual Ancestry Informative Marker SNP."""
    model_config = ConfigDict(protected_namespaces=())

    rs_id: str = Field(..., description="dbSNP reference rsID")
    chromosome: str = Field(..., description="Autosomal chromosome (1-22)")
    position_grch38: int = Field(..., description="1-based physical coordinate on GRCh38/hg38")
    position_grch37: Optional[int] = Field(None, description="1-based physical coordinate on GRCh37/hg19")
    ref_allele: str = Field(..., description="Reference allele on forward top strand")
    alt_allele: str = Field(..., description="Alternate allele on forward top strand")
    gene_symbol: Optional[str] = Field(None, description="Associated gene symbol")
    panel_memberships: Set[AIMPanelTypeEnum] = Field(default_factory=set, description="Panels containing this locus")
    informativeness_in: Optional[float] = Field(None, description="Global Rosenberg assignment informativeness In")
    is_phenotypic_pleiotropic: bool = Field(default=False, description="True if also active in HIrisPlex-S")


class MicrohaplotypeLocus(BaseModel):
    """Registry definition for a forensic microhaplotype (multi-SNP locus <300 bp)."""
    model_config = ConfigDict(protected_namespaces=())

    mh_id: str = Field(..., description="Standardized Microhaplotype ID (e.g. mh01KK-001)")
    chromosome: str = Field(..., description="Autosomal chromosome (1-22)")
    start_bp: int = Field(..., description="1-based start physical position on GRCh38")
    end_bp: int = Field(..., description="1-based end physical position on GRCh38")
    length_bp: int = Field(..., description="Physical span in base pairs (<300 bp)")
    constituent_snps: List[str] = Field(..., description="List of ordered constituent dbSNP rsIDs")
    known_haplotypes: List[str] = Field(default_factory=list, description="Known population phase configurations")


class GenotypeCall(BaseModel):
    """Individual locus genotype call."""
    model_config = ConfigDict(protected_namespaces=())

    locus_id: str = Field(..., description="rsID or microhaplotype ID")
    allele_1: str = Field(..., description="First observed allele (e.g. 'A', 'G', or haplotype string)")
    allele_2: str = Field(..., description="Second observed allele")
    is_heterozygous: bool = Field(..., description="True if allele_1 != allele_2")
    dosage_alt: float = Field(default=0.0, description="Count of ALT alleles in {0.0, 1.0, 2.0}")
    quality_score: Optional[float] = Field(None, description="Read depth or genotype quality score")


class IngestedBGASample(BaseModel):
    """Normalized ingested biological sample containing multi-locus genotype calls."""
    model_config = ConfigDict(protected_namespaces=())

    sample_id: str = Field(..., description="Unique sample identifier")
    detected_platform: PlatformFormatEnum = Field(..., description="Auto-detected platform format")
    primary_panel: AIMPanelTypeEnum = Field(..., description="Primary detected or assigned AIM panel")
    assembly: GenomicAssemblyEnum = Field(default=GenomicAssemblyEnum.GRCH38, description="Genomic reference build")
    genotypes: Dict[str, GenotypeCall] = Field(default_factory=dict, description="Genotype calls keyed by locus ID")
    total_loci_assayed: int = Field(default=0, description="Total expected loci in assigned panel")
    called_loci_count: int = Field(default=0, description="Number of successfully called non-missing loci")
    call_rate: float = Field(default=0.0, description="Percentage of called loci (0.0 - 100.0%)")
    heterozygosity_rate: float = Field(default=0.0, description="Heterozygosity percentage across called SNPs")
    qc_status: QCStatusEnum = Field(default=QCStatusEnum.PASS, description="QC outcome status")
    qc_flags: List[str] = Field(default_factory=list, description="Quality alert and warning messages")


class AdmixtureProportionResult(BaseModel):
    """Estimated biogeographical ancestry proportions and assignment telemetry."""
    model_config = ConfigDict(protected_namespaces=())

    sample_id: str
    panel_type: AIMPanelTypeEnum
    superpop_proportions: Dict[ContinentalSuperPopEnum, float] = Field(..., description="Continuous Q-matrix fractions (sum=1.0)")
    top_assigned_population: ContinentalSuperPopEnum = Field(..., description="Top maximum likelihood continental group")
    bayes_factor_vs_second: float = Field(default=1.0, description="Bayes factor ratio of top vs runner-up population")
    shannon_entropy: float = Field(default=0.0, description="Admixture diversity Shannon entropy H(Q)")
    simpson_diversity: float = Field(default=0.0, description="Simpson diversity index D")
    pca_coordinates: List[float] = Field(default_factory=list, description="Top 3 PC coordinates [PC1, PC2, PC3]")
    wgs84_centroid_lat: float = Field(default=0.0, description="Estimated WGS84 Geodesic latitude")
    wgs84_centroid_lng: float = Field(default=0.0, description="Estimated WGS84 Geodesic longitude")
    spatial_covariance_semi_major_km: float = Field(default=0.0, description="95% confidence ellipse semi-major axis (km)")
    spatial_covariance_semi_minor_km: float = Field(default=0.0, description="95% confidence ellipse semi-minor axis (km)")
    spatial_ellipse_tilt_deg: float = Field(default=0.0, description="Confidence ellipse orientation angle (degrees)")
    enfsi_verbal_statement: str = Field(default="", description="Calibrated ENFSI 2017 verbal reporting statement")
