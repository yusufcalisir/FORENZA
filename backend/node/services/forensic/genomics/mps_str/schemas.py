"""
FORENZA Massively Parallel Sequencing (MPS/NGS) STR Analysis — Pydantic v2 Schemas.
Standard Compliance: ISFG Recommendations on STR Sequence Nomenclature & ISO/IEC 17025:2017.
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, ConfigDict, Field


class VariantType(str, Enum):
    SNP = "SNP"
    DELETION = "DELETION"
    INSERTION = "INSERTION"


class FlankingVariant(BaseModel):
    """Represents a single nucleotide polymorphism or indel in 5' or 3' flanking regions."""
    model_config = ConfigDict(protected_namespaces=())

    rs_id: str = Field(..., description="dbSNP accession ID (e.g. rs9362477, rs771794429)")
    position_relative: int = Field(..., description="Base pair position relative to repeat motif (+ or -)")
    ref_allele: str = Field(..., description="Reference nucleotide sequence")
    alt_allele: str = Field(..., description="Observed variant nucleotide sequence")
    variant_type: VariantType = Field(VariantType.SNP, description="Type of variation (SNP, DELETION, INSERTION)")
    population_note: Optional[str] = Field(None, description="Known population specificity or bias")


class MotifBlock(BaseModel):
    """Represents a single repeated or intervening motif unit within an STR repeat region."""
    model_config = ConfigDict(protected_namespaces=())

    motif_sequence: str = Field(..., description="Core nucleotide sequence of repeat unit (e.g. TCTA, CTTT)")
    repeat_count: float = Field(..., description="Number of consecutive tandem repeats (integer or microvariant decimal)")
    is_interruption: bool = Field(False, description="True if this block is a partial/intervening non-standard spacer")


class ParsedSTRSequence(BaseModel):
    """Fully parsed and structured ISFG-compliant sequence-based STR allele."""
    model_config = ConfigDict(protected_namespaces=())

    locus_name: str = Field(..., description="Forensic locus identifier (e.g. SE33, D21S11, vWA)")
    raw_sequence_string: str = Field(..., description="Original raw sequence or ISFG formatted string")
    repeat_blocks: List[MotifBlock] = Field(default_factory=list, description="Ordered list of motif blocks")
    flanking_5p_variants: List[FlankingVariant] = Field(default_factory=list, description="5' flanking variants")
    flanking_3p_variants: List[FlankingVariant] = Field(default_factory=list, description="3' flanking variants")
    
    # CE backward compatibility fields
    ce_length_call: float = Field(..., description="Equivalent CE length-based allele call (e.g. 18, 27.2, 9.3)")
    repeat_bp_length: int = Field(..., description="Total length of repeat region in base pairs")
    
    # Isoallele metadata
    isoallele_tag: Optional[str] = Field(None, description="Short tag distinguishing isoalleles of same length (e.g. 18a, 18b)")
    is_complex_repeat: bool = Field(False, description="True if compound or complex repeat architecture")


class SingleLocusMPSGenotype(BaseModel):
    """Sequence-based diploid or hemizygous genotype at a single forensic locus."""
    model_config = ConfigDict(protected_namespaces=())

    locus_name: str
    alleles: List[ParsedSTRSequence]
    is_heterozygous: bool
    ce_genotype_string: str = Field(..., description="CE representation (e.g. '18, 27.2')")
    mps_genotype_string: str = Field(..., description="Full ISFG sequence representation")
    quality_flags: List[str] = Field(default_factory=list, description="QA/QC flags e.g. FLANKING_DELETION_RESOLVED")


class GenotypeProfileMPS(BaseModel):
    """Complete 28-marker multi-locus sequence-based forensic profile."""
    model_config = ConfigDict(protected_namespaces=())

    sample_id: str
    sample_type: str = Field("SINGLE_SOURCE", description="SINGLE_SOURCE, MIXTURE, REFERENCE_STANDARD")
    loci: Dict[str, SingleLocusMPSGenotype]
    total_loci_count: int
    ce_concordance_rate: float = Field(1.0, description="Concordance with CE length calls (0.0 to 1.0)")
    population_prior: Optional[str] = Field("GLOBAL", description="AfAm, Cauc, Hisp, Kor, GLOBAL")


__all__ = [
    "VariantType",
    "FlankingVariant",
    "MotifBlock",
    "ParsedSTRSequence",
    "SingleLocusMPSGenotype",
    "GenotypeProfileMPS",
]
