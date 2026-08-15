"""
FORENZA Core Forensic Data Models.
Provides immutable, type-safe structures for STR alleles, loci, genotypes,
profiles, hypothesis definitions, and analysis results with uncertainty reporting.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class SampleType(str, Enum):
    SINGLE_SOURCE = "single_source"
    MIXTURE_2_PERSON = "mixture_2_person"
    MIXTURE_3_PERSON = "mixture_3_person"
    PARTIAL_PROFILE = "partial_profile"


class KinshipRelationship(str, Enum):
    PARENT_CHILD = "parent_child"
    FULL_SIBLING = "full_sibling"
    HALF_SIBLING = "half_sibling"
    AVUNCULAR = "avuncular"               # Uncle/Aunt – Nephew/Niece (k0=0.50, k1=0.50, k2=0)
    GRANDPARENT = "grandparent"           # Grandparent – Grandchild  (k0=0.50, k1=0.50, k2=0)
    FIRST_COUSIN = "first_cousin"         # First cousins             (k0=0.75, k1=0.25, k2=0)
    UNRELATED = "unrelated"               # Unrelated individuals     (k0=1.00, k1=0.00, k2=0)


@dataclass(frozen=True)
class STRAllele:
    """Represents a single STR allele call with optional peak height (RFU)."""
    value: float
    height_rfu: Optional[float] = None
    is_stutter: bool = False

    def __post_init__(self):
        if self.value < 0:
            raise ValueError(f"Allele value must be non-negative: {self.value}")


@dataclass(frozen=True)
class STRLocus:
    """Represents an STR locus containing observed alleles."""
    name: str
    alleles: Tuple[STRAllele, ...]

    @property
    def is_homozygote(self) -> bool:
        if len(self.alleles) == 1:
            return True
        if len(self.alleles) == 2:
            return self.alleles[0].value == self.alleles[1].value
        return False

    @property
    def allele_values(self) -> Tuple[float, ...]:
        return tuple(a.value for a in self.alleles)


@dataclass(frozen=True)
class STRGenotype:
    """Represents a validated 2-allele genotype for a single locus."""
    locus_name: str
    allele1: float
    allele2: float

    @property
    def is_homozygote(self) -> bool:
        return self.allele1 == self.allele2

    @property
    def alleles(self) -> Tuple[float, float]:
        return (min(self.allele1, self.allele2), max(self.allele1, self.allele2))


@dataclass
class STRProfile:
    """Represents a complete forensic DNA profile across multiple loci."""
    profile_id: str
    loci: Dict[str, STRGenotype]
    sample_type: SampleType = SampleType.SINGLE_SOURCE
    population_group: str = "Caucasian"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_locus(self, locus_name: str) -> Optional[STRGenotype]:
        return self.loci.get(locus_name.upper())

    def add_genotype(self, genotype: STRGenotype) -> None:
        self.loci[genotype.locus_name.upper()] = genotype

    @property
    def locus_count(self) -> int:
        return len(self.loci)


@dataclass(frozen=True)
class Hypothesis:
    """Represents a proposition pair for Likelihood Ratio evaluation."""
    hp_description: str  # Prosecution hypothesis
    hd_description: str  # Defense hypothesis
    hp_contributors: Tuple[str, ...]
    hd_contributors: Tuple[str, ...]


@dataclass
class AnalysisResult:
    """
    Forensic Analysis Result model enforcing complete uncertainty reporting
    and assumptions log for court admissibility.
    """
    value: float  # Point estimate (LR or KI)
    confidence_interval: Tuple[float, float]  # e.g., (95% HPD low, 95% HPD high)
    assumptions: List[str]
    model: str  # Computational model name
    data_source: str  # Population frequency database reference
    limitations: List[str]
    locus_scores: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "confidence_interval": {
                "low": self.confidence_interval[0],
                "high": self.confidence_interval[1],
            },
            "assumptions": self.assumptions,
            "model": self.model,
            "data_source": self.data_source,
            "limitations": self.limitations,
            "locus_scores": self.locus_scores,
            "metadata": self.metadata,
        }
