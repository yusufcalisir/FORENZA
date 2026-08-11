"""
FORENZA Forensic DNA Phenotyping — Domain Models.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class EyeColour(str, Enum):
    BLUE = "blue"
    INTERMEDIATE = "intermediate"
    BROWN = "brown"


class HairColour(str, Enum):
    BLACK = "black"
    BROWN = "brown"
    BLONDE = "blonde"
    RED = "red"


class SkinTone(str, Enum):
    """Fitzpatrick phototype scale (I–VI)."""
    VERY_PALE = "very_pale"       # I
    PALE = "pale"                 # II
    INTERMEDIATE = "intermediate" # III
    OLIVE = "olive"               # IV
    BROWN = "brown"               # V
    DARK_BROWN = "dark_brown"     # VI


class Ancestry(str, Enum):
    EUROPEAN = "European"
    AFRICAN = "African"
    EAST_ASIAN = "East_Asian"
    SOUTH_ASIAN = "South_Asian"
    ADMIXED = "Admixed"


@dataclass(frozen=True)
class SNPInput:
    """
    A single SNP genotype call.
    rsid: dbSNP identifier (e.g. 'rs12913832')
    dosage: count of the effect allele (0, 1, or 2)
    """
    rsid: str
    dosage: int  # 0, 1, or 2

    def __post_init__(self):
        if self.dosage not in (0, 1, 2):
            raise ValueError(f"SNP dosage must be 0, 1, or 2 — got {self.dosage} for {self.rsid}")


@dataclass
class TraitProbability:
    """Predicted probability distribution across trait categories."""
    trait: str
    probabilities: Dict[str, float]       # category → probability (sum = 1.0)
    most_likely: str                       # category with highest probability
    confidence: float                      # probability of the most likely category

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trait": self.trait,
            "probabilities": {k: round(v, 4) for k, v in self.probabilities.items()},
            "most_likely": self.most_likely,
            "confidence": round(self.confidence, 4),
        }


@dataclass
class PhenotypeReport:
    """Complete forensic phenotype prediction report."""
    eye_colour: TraitProbability
    hair_colour: TraitProbability
    skin_tone: TraitProbability
    ancestry: TraitProbability
    snp_count_evaluated: int
    model_version: str = "HIrisPlex-S v1.0 (Walsh et al. 2018)"
    limitations: List[str] = field(default_factory=lambda: [
        "Predictions are probabilistic estimates, not deterministic conclusions",
        "Accuracy depends on SNP panel completeness and population of origin",
        "Environmental factors (e.g. tanning) are not modelled",
        "Result must be interpreted by a qualified forensic expert",
    ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "eye_colour": self.eye_colour.to_dict(),
            "hair_colour": self.hair_colour.to_dict(),
            "skin_tone": self.skin_tone.to_dict(),
            "ancestry": self.ancestry.to_dict(),
            "snp_count_evaluated": self.snp_count_evaluated,
            "model_version": self.model_version,
            "limitations": self.limitations,
        }
