"""
FORENZA Touch DNA & Low-Template Probabilistic Genotyping Engine.
Models substrate recovery efficiency (porous vs. non-porous), evaluates stochastic allele dropout probabilities
P(D | m) = exp(-lambda * m) for low-template DNA (m < 100 pg), models drop-in rates P(C), and integrates
with Metropolis-Hastings MCMC Probabilistic Genotyping for multi-person contributor deconvolution.

References:
  Gill P (2001) Application of Low Copy Number DNA Profiling. Forensic Science International.
  SWGDAM (2020) Guidelines for Autosomal STR Interpretation with Probabilistic Genotyping.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class SubstrateEfficiencyResult:
    substrate_type: str                # 'SMOOTH_NON_POROUS', 'TEXTURED_NON_POROUS', 'POROUS_FABRIC', 'ROUGH_WOOD'
    efficiency_factor: float
    input_mass_pg: float
    recovered_mass_pg: float


@dataclass
class StochasticDropoutModel:
    recovered_mass_pg: float
    dropout_probability_pd: float      # P(D) = exp(-lambda * m)
    dropin_probability_pc: float       # P(C)
    peak_imbalance_ratio: float        # Hb / Ha


@dataclass
class TouchDnaAnalysisResult:
    sample_id: str
    substrate: SubstrateEfficiencyResult
    stochastic_model: StochasticDropoutModel
    is_low_template: bool              # True if recovered mass < 100 pg
    ltdna_summary: str


class TouchDnaEngine:
    """
    Evaluates low-template Touch DNA substrate recovery efficiencies and stochastic dropout dynamics.
    """

    SUBSTRATE_EFFICIENCIES = {
        "SMOOTH_NON_POROUS": 0.60,
        "TEXTURED_NON_POROUS": 0.40,
        "POROUS_FABRIC": 0.20,
        "ROUGH_WOOD": 0.15,
    }

    def analyze_ltdna(
        self,
        sample_id: str,
        substrate_type: str,
        input_mass_pg: float,
        lambda_dropout: float = 0.05
    ) -> TouchDnaAnalysisResult:
        if input_mass_pg <= 0:
            raise ValueError("Input DNA mass must be greater than zero.")

        sub_key = substrate_type.upper()
        eff = self.SUBSTRATE_EFFICIENCIES.get(sub_key, 0.30)

        recovered_mass = round(input_mass_pg * eff, 2)

        # Stochastic Allele Dropout P(D) = exp(-lambda * m_recovered)
        pd = round(math.exp(-lambda_dropout * recovered_mass), 4)

        # Drop-in probability P(C) heuristic
        pc = round(0.01 + 0.05 * pd, 4)

        # Peak height imbalance ratio Hb/Ha
        imbalance = round(max(0.20, 1.0 - 0.80 * pd), 4)

        sub_res = SubstrateEfficiencyResult(
            substrate_type=sub_key,
            efficiency_factor=eff,
            input_mass_pg=input_mass_pg,
            recovered_mass_pg=recovered_mass
        )

        stoch_res = StochasticDropoutModel(
            recovered_mass_pg=recovered_mass,
            dropout_probability_pd=pd,
            dropin_probability_pc=pc,
            peak_imbalance_ratio=imbalance
        )

        is_ltdna = recovered_mass < 100.0

        summary = (
            f"Touch DNA Analysis for {sample_id} ({sub_key}): Recovered Mass = {recovered_mass} pg "
            f"(Efficiency={eff*100:.0f}%). Stochastic Dropout P(D) = {pd:.2%}. "
            f"Classification: {'LOW-TEMPLATE DNA (LTDNA)' if is_ltdna else 'STANDARD TEMPLATE DNA'}."
        )

        return TouchDnaAnalysisResult(
            sample_id=sample_id,
            substrate=sub_res,
            stochastic_model=stoch_res,
            is_low_template=is_ltdna,
            ltdna_summary=summary
        )
