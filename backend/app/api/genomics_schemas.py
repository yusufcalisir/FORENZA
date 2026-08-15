from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class MultiLayerGenomicsRequest(BaseModel):
    lr_str: float = Field(default=1.0e12, description="Likelihood Ratio for Autosomal STR (CODIS 24 loci)")
    lr_snp: float = Field(default=1.0e3, description="Likelihood Ratio for Forensic SNP (Phenotype/Ancestry)")
    lr_mtdna: float = Field(default=1.0e2, description="Likelihood Ratio for Maternal Lineage mtDNA")
    lr_y_str: float = Field(default=1.0e4, description="Likelihood Ratio for Paternal Lineage Y-STR")
    lr_wgs: float = Field(default=1.0e5, description="Likelihood Ratio for Whole-Genome Sequencing (WGS)")
    pe_str: float = Field(default=0.999999, description="Probability of Exclusion for STR")
    pe_snp: float = Field(default=0.995, description="Probability of Exclusion for SNP")
    pe_mtdna: float = Field(default=0.990, description="Probability of Exclusion for mtDNA")
    pe_y_str: float = Field(default=0.998, description="Probability of Exclusion for Y-STR")
    pe_wgs: float = Field(default=0.9999, description="Probability of Exclusion for WGS")


class GenomicLayerDetail(BaseModel):
    layer_name: str
    likelihood_ratio: float
    log10_lr: float
    exclusion_probability: float
    status: str


class MultiLayerGenomicsResponse(BaseModel):
    joint_likelihood_ratio: float
    log10_joint_likelihood_ratio: float
    joint_exclusion_probability: float
    enfsi_verbal_predicate: str
    active_layer_count: int
    genomic_layers: List[GenomicLayerDetail]
    architecture_provenance: str


class LocusDeconvolutionDetail(BaseModel):
    locus: str
    major_genotype: List[float]
    minor_genotype: List[float]
    posterior_probability: float
    log_likelihood: float


class DeconvolveMixtureRequest(BaseModel):
    observed_peaks: Dict[str, Dict[str, float]] = Field(
        ...,
        examples=[{"TH01": {"6.0": 700.0, "9.3": 300.0}}],
        description="Observed EPG peaks {locus: {allele_str: rfu_height}}"
    )
    num_contributors: int = Field(default=2, ge=2, le=4, description="Number of mixture contributors (2, 3, or 4)")
    model_engine: str = Field(default="STRmix", description="Continuous likelihood engine: STRmix | EuroForMix")
    n_burn: int = Field(default=1000, ge=100, le=50000, description="MCMC burn-in iterations")
    n_sample: int = Field(default=3000, ge=200, le=100000, description="MCMC retained sampling iterations")
    n_chains: int = Field(default=3, ge=1, le=8, description="Number of parallel MCMC chains")
    suspect_profile: Optional[List[List[float]]] = Field(
        default=None,
        description="Optional suspect genotype list [(a1, a2)] per locus for H_p numerator calculation"
    )


class DeconvolveMixtureResponse(BaseModel):
    num_contributors: int
    model_engine: str
    log10_lr: float
    lr_value: float
    hpd95_lower: float
    hpd95_upper: float
    posterior_mixture_weights: List[float]
    posterior_degradation_slopes: List[float]
    r_hat_max: float
    ess_min: float
    mcmc_converged: bool
    major_contributor_identified: bool
    locus_deconvolutions: List[LocusDeconvolutionDetail]
    verbal_scale_en: str
    verbal_scale_tr: str
    assumptions: List[str]

