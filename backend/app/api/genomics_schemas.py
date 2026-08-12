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
