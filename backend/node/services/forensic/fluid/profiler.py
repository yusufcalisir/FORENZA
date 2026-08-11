"""
FORENZA Body Fluid Identification Engine via mRNA Gene Expression Profiling.
Classifies biological stains (Venous Blood, Semen, Saliva, Vaginal Secretions, Menstrual Blood, Urine, Sweat)
using cell-type specific mRNA markers and multinomial logit probability distributions.

References:
  Juusola & Ballantyne (2005) Messenger RNA profiling for identification of body fluids.
  Haas et al. (2021) EDNAP European DNA Profiling Group mRNA profiling standards.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class MrnaMarkerExpression:
    gene_symbol: str                   # e.g. 'HBA1', 'PRM1', 'HTN3', 'CYP2B7P1', 'MMP7', 'SLC14A2'
    expression_rfu: float              # Relative fluorescence intensity / transcript abundance


@dataclass
class StainSampleData:
    sample_id: str
    mrna_expressions: List[MrnaMarkerExpression]


@dataclass
class BodyFluidProbability:
    fluid_type: str                    # 'VENOUS_BLOOD', 'SEMEN', 'SALIVA', 'VAGINAL_SECRETION', 'MENSTRUAL_BLOOD', 'URINE'
    probability: float                 # Posterior probability (0.0 to 1.0)
    primary_markers: List[str]


@dataclass
class FluidIdentificationResult:
    sample_id: str
    top_predicted_fluid: str
    fluid_probabilities: List[BodyFluidProbability]
    identification_summary: str


# Cell-type specific marker mapping
FLUID_MARKER_MAP = {
    "VENOUS_BLOOD": ["HBA1", "HBB"],
    "SEMEN": ["PRM1", "PRM2", "KLK3"],
    "SALIVA": ["HTN3", "STATH"],
    "VAGINAL_SECRETION": ["CYP2B7P1", "MYOZ1"],
    "MENSTRUAL_BLOOD": ["MMP7", "MMP11"],
    "URINE": ["SLC14A2", "UMOD"],
}


class BodyFluidProfiler:
    """
    Classifies biological stain fluid origin from mRNA gene expression profiles.
    """

    def identify_body_fluid(self, sample: StainSampleData) -> FluidIdentificationResult:
        expr_map = {m.gene_symbol.upper(): m.expression_rfu for m in sample.mrna_expressions}

        scores: Dict[str, float] = {}

        for fluid, markers in FLUID_MARKER_MAP.items():
            s = sum(expr_map.get(mk, 0.0) for mk in markers)
            scores[fluid] = max(0.0, s)

        # Softmax normalization: P(Fluid_k) = exp(S_k) / sum(exp(S_j))
        max_score = max(scores.values()) if scores else 0.0
        exp_sum = 0.0
        exp_vals: Dict[str, float] = {}

        for fluid, s in scores.items():
            # Scale score for numeric stability
            scaled = (s / (max_score + 1.0)) * 5.0
            ev = math.exp(scaled)
            exp_vals[fluid] = ev
            exp_sum += ev

        probs: List[BodyFluidProbability] = []
        for fluid, ev in exp_vals.items():
            p = round(ev / max(1e-9, exp_sum), 4)
            probs.append(BodyFluidProbability(
                fluid_type=fluid,
                probability=p,
                primary_markers=FLUID_MARKER_MAP[fluid]
            ))

        probs.sort(key=lambda x: x.probability, reverse=True)
        top_fluid = probs[0].fluid_type

        summary = f"Body Fluid Identification for {sample.sample_id}: Top predicted fluid = {top_fluid} (P={probs[0].probability*100}%)."

        return FluidIdentificationResult(
            sample_id=sample.sample_id,
            top_predicted_fluid=top_fluid,
            fluid_probabilities=probs,
            identification_summary=summary
        )
