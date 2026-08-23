"""
FORENZA Epigenetic Clocks & Multimodal PMI Estimation Domain Schemas (Pillar 4 §1-§4).

Provides Pydantic v2 domain models for multi-generation epigenetic clocks,
forensic reduced-marker multiplexes, biological aging biomarkers, taphonomic degradation,
and multimodal post-mortem interval (PMI) estimation.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, ConfigDict


class ClockGeneration(str, Enum):
    """Classification of epigenetic clock paradigms."""
    FIRST_GEN_CHRONO = "FIRST_GEN_CHRONO"          # Horvath 353, Hannum 71, PedBE 84, Zhang 514
    SECOND_GEN_BIOLOGICAL = "SECOND_GEN_BIOLOGICAL" # Levine PhenoAge 513, Lu GrimAge 1030, GrimAge2
    THIRD_GEN_VELOCITY = "THIRD_GEN_VELOCITY"      # DunedinPoAm, DunedinPACE
    FORENSIC_REDUCED = "FORENSIC_REDUCED"          # VISAGE Basic (5), VISAGE Enhanced (8/44), Weidner (3)


class EpigeneticTissueType(str, Enum):
    """Biological fluid/tissue matrices with distinct epigenetic baseline profiles."""
    WHOLE_BLOOD = "WHOLE_BLOOD"
    SALIVA_BUCCAL = "SALIVA_BUCCAL"
    SEMEN = "SEMEN"
    BONE = "BONE"
    TEETH = "TEETH"
    CARTILAGE = "CARTILAGE"
    EPIDERMIS = "EPIDERMIS"
    MULTI_TISSUE = "MULTI_TISSUE"


class EpigeneticPlatform(str, Enum):
    """Analytical measurement platforms for DNA methylation."""
    ILLUMINA_450K = "ILLUMINA_450K"
    ILLUMINA_EPIC = "ILLUMINA_EPIC"
    TARGETED_BISULFITE_MPS = "TARGETED_BISULFITE_MPS"
    BISULFITE_PYROSEQUENCING = "BISULFITE_PYROSEQUENCING"
    SNAPSHOT_SBE = "SNAPSHOT_SBE"


class CpGProbeRecord(BaseModel):
    """Genomic and biocomputational specification for an individual CpG locus."""
    model_config = ConfigDict(protected_namespaces=())

    probe_id: str = Field(..., description="Illumina probe identifier (e.g. cg16867657) or target genomic locus")
    gene_symbol: str = Field(..., description="Associated human gene symbol (e.g. ELOVL2)")
    chromosome: str = Field(..., description="Chromosome location (chr1 - chr22, chrX, chrY)")
    pos_grch37: int = Field(..., description="Genomic coordinate in GRCh37/hg19")
    pos_grch38: int = Field(..., description="Genomic coordinate in GRCh38/hg38")
    target_strand: str = Field(default="+", description="Forward (+) or reverse (-) target strand")
    amplicon_bp: Optional[int] = Field(default=None, description="Multiplex PCR amplicon size in base pairs")
    associated_clocks: List[str] = Field(default_factory=list, description="Clock models utilizing this locus")
    mean_reference_beta: float = Field(default=0.50, ge=0.0, le=1.0, description="Population average baseline beta-value")


class MethylationSample(BaseModel):
    """Quantified DNA methylation values for a biological sample across multiple loci."""
    model_config = ConfigDict(protected_namespaces=())

    sample_id: str = Field(..., description="Unique specimen/evidence identifier")
    tissue_type: EpigeneticTissueType = Field(default=EpigeneticTissueType.WHOLE_BLOOD)
    platform: EpigeneticPlatform = Field(default=EpigeneticPlatform.TARGETED_BISULFITE_MPS)
    beta_values: Dict[str, float] = Field(default_factory=dict, description="Mapping of probe_id -> beta-value in [0.0, 1.0]")
    m_values: Optional[Dict[str, float]] = Field(default=None, description="Mapping of probe_id -> M-value")
    read_counts_c: Optional[Dict[str, int]] = Field(default=None, description="Methylated cytosine read depth count")
    read_counts_t: Optional[Dict[str, int]] = Field(default=None, description="Unmethylated thymine read depth count")
    detection_p_values: Optional[Dict[str, float]] = Field(default=None, description="Array signal detection p-values")
    bisulfite_conversion_efficiency: float = Field(default=0.992, ge=0.0, le=1.0, description="Bisulfite conversion rate")
    input_dna_pg: Optional[float] = Field(default=500.0, ge=0.0, description="Template DNA input in picograms")


class ClockEstimationRequest(BaseModel):
    """Request payload for multi-generation epigenetic age and biological risk analysis."""
    model_config = ConfigDict(protected_namespaces=())

    sample: MethylationSample
    target_clocks: List[str] = Field(
        default=["horvath_2013", "visage_enhanced", "phenoage", "grimage"],
        description="List of clock model IDs to evaluate"
    )
    chronological_age: Optional[float] = Field(default=None, ge=0.0, le=125.0, description="Known calendar age if validating/benchmarking")
    smoking_pack_years: Optional[float] = Field(default=0.0, ge=0.0, description="Tobacco exposure pack-years")
    biological_sex: Optional[str] = Field(default="UNKNOWN", description="MALE, FEMALE, or UNKNOWN")
    clinical_biomarkers: Optional[Dict[str, float]] = Field(
        default=None,
        description="Optional measured clinical lab chemistries (Albumin, Creatinine, Glucose, hsCRP, etc.)"
    )
    jurisdiction: str = Field(default="INTERNATIONAL", description="Legal regulatory framework: GERMANY_STPO, NETHERLANDS, INTERNATIONAL")


class EpigeneticAgeResult(BaseModel):
    """Detailed output for an individual epigenetic chronological clock prediction."""
    model_config = ConfigDict(protected_namespaces=())

    clock_id: str
    clock_name: str
    generation: ClockGeneration
    predicted_age: float = Field(..., description="Estimated chronological age in years")
    raw_age_acceleration: Optional[float] = Field(default=None, description="Delta Age = Predicted - True Age")
    universal_age_accel: Optional[float] = Field(default=None, description="Orthogonal residual AgeAccel (r=0)")
    intrinsic_age_accel: Optional[float] = Field(default=None, description="IEAA adjusted for leukocyte sub-populations")
    extrinsic_age_accel: Optional[float] = Field(default=None, description="EEAA incorporating immunosenescent shifts")
    tissue_offset_applied: float = Field(default=0.0, description="Calibrated tissue baseline offset Delta_tissue in years")
    expanded_uncertainty_95: float = Field(default=3.5, description="ISO/IEC 17025 expanded uncertainty U_95% (+/- years)")
    age_interval_lower: float = Field(..., description="Lower 95% confidence bound")
    age_interval_upper: float = Field(..., description="Upper 95% confidence bound")
    covered_cpgs_count: int
    missing_cpgs_count: int
    imputation_applied: bool = False


class BiologicalAgingResult(BaseModel):
    """Output for second- and third-generation healthspan and biological deterioration metrics."""
    model_config = ConfigDict(protected_namespaces=())

    phenotypic_age: Optional[float] = Field(default=None, description="Levine PhenoAge composite biological age in years")
    phenoage_acceleration: Optional[float] = Field(default=None, description="PhenoAge discrepancy relative to chronological age")
    grimage_age: Optional[float] = Field(default=None, description="Lu GrimAge lifespan & mortality predictor in years")
    grimage_acceleration: Optional[float] = Field(default=None, description="GrimAge acceleration residual")
    grimage_mortality_hazard: Optional[float] = Field(default=None, description="Relative all-cause mortality hazard ratio")
    surrogate_protein_estimates: Dict[str, float] = Field(
        default_factory=dict,
        description="DNAm surrogate biomarkers (DNAm PACKYRS, ADM, B2M, Cystatin C, GDF-15, Leptin, PAI-1, TIMP-1)"
    )
    dunedin_pace_velocity: Optional[float] = Field(
        default=None,
        description="Third-generation dynamic pace of aging (Delta-biological-years / Delta-calendar-year, 1.0 = average)"
    )
    forensic_admissibility_flag: bool = Field(
        default=False,
        description="False for 2nd/3rd gen clocks (inadmissible for direct chronological suspect narrowing)"
    )
    advisory_notes: List[str] = Field(default_factory=list)


class MultimodalPMIRequest(BaseModel):
    """Parameters for comprehensive multi-method Post-Mortem Interval (PMI) deconvolution."""
    model_config = ConfigDict(protected_namespaces=())

    sample_id: str
    discovery_time_epoch: Optional[float] = Field(default=None, description="Timestamp of body discovery")
    ambient_temp_celsius: float = Field(default=20.0, description="Ambient environmental temperature in Celsius")
    rectal_temp_celsius: Optional[float] = Field(default=None, description="Measured core body/rectal temperature")
    body_mass_kg: Optional[float] = Field(default=75.0, description="Body mass in kilograms for Henssge Nomogram")
    clothing_factor: float = Field(default=1.0, description="Clothing thermal insulation factor (1.0 = naked/light, 1.4 = heavy)")
    vitreous_potassium_mmol_l: Optional[float] = Field(default=None, description="Vitreous humor [K+] ion concentration in mmol/L")
    accumulated_degree_days: Optional[float] = Field(default=None, description="Entomological thermal summation (ADD/ADH)")
    rna_degradation_ratio: Optional[float] = Field(default=None, description="Thanatotranscriptomic mRNA/miRNA preservation ratio")
    bacterial_succession_index: Optional[float] = Field(default=None, description="Thanatomicrobiome 16S turnover index")
    dna_methylation_sample: Optional[MethylationSample] = Field(default=None, description="Epigenetic profile for age-at-death")


class TaphonomicPMIResult(BaseModel):
    """Output synthesizing epigenetic stability, age-at-death, and multimodal PMI estimation."""
    model_config = ConfigDict(protected_namespaces=())

    sample_id: str
    epigenetic_age_at_death: float = Field(..., description="Estimated chronological age at the time of somatic death (years)")
    epigenetic_5mc_stability_status: str = Field(
        default="STABLE_ARREST",
        description="STABLE_ARREST (0-120h), MODERATE_DIAGENESIS, or SEVERE_DEAMINATION"
    )
    deamination_index: float = Field(default=0.0, ge=0.0, le=1.0, description="Hydrolytic 5mC -> T transition damage fraction")
    estimated_pmi_hours: float = Field(..., description="Multimodal consensus post-mortem interval estimate in hours")
    pmi_uncertainty_lower_hours: float = Field(..., description="Lower bound of PMI confidence interval (hours)")
    pmi_uncertainty_upper_hours: float = Field(..., description="Upper bound of PMI confidence interval (hours)")
    modalities_used: List[str] = Field(default_factory=list, description="List of active physical/chemical/biological modalities")
    modality_weights: Dict[str, float] = Field(default_factory=dict, description="Bayesian posterior weighting across evidence streams")
    enfsi_evaluative_statement: str = Field(default="", description="Court-admissible evaluative reporting statement")
