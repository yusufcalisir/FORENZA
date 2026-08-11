"""
FORENZA Dual Serology + DNA Evidence Fusion Evaluator.
Fuses classical serology Likelihood Ratio (LR_serology) with 24-locus autosomal STR Likelihood Ratio (LR_STR):
  LR_combined = LR_serology * LR_STR
  log10(LR_combined) = log10(LR_serology) + log10(LR_STR)

Reference:
  Inman & Rudin (2000) Principles and Practice of Criminalistics.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from .serology import SerologicalEvaluationResult


@dataclass
class DualEvidenceIntegrationResult:
    sample_id: str
    lr_serology: float
    lr_str: float
    lr_combined: float
    log10_lr_combined: float
    verbal_statement: str
    integration_summary: str


class SerologyDnaIntegrator:
    """
    Fuses classical serology and molecular STR DNA evidence using independent product rule.
    """

    def integrate_serology_and_dna(
        self,
        sample_id: str,
        serology_result: SerologicalEvaluationResult,
        lr_str: float
    ) -> DualEvidenceIntegrationResult:
        lr_ser = serology_result.serology_likelihood_ratio
        lr_comb = round(lr_ser * lr_str, 2)
        log10_comb = round(math.log10(max(1.0, lr_comb)), 4)

        if lr_comb >= 1e6:
            verbal = "Extremely strong support for prosecution hypothesis (Hp)"
        elif lr_comb >= 1e4:
            verbal = "Very strong support for prosecution hypothesis (Hp)"
        elif lr_comb >= 100.0:
            verbal = "Strong support for prosecution hypothesis (Hp)"
        else:
            verbal = "Moderate support for prosecution hypothesis (Hp)"

        summary = (
            f"Dual Evidence Integration for {sample_id}: "
            f"LR_serology = {lr_ser}, LR_STR = {lr_str:.2e} -> LR_combined = {lr_comb:.2e} "
            f"(log10_LR = {log10_comb})."
        )

        return DualEvidenceIntegrationResult(
            sample_id=sample_id,
            lr_serology=lr_ser,
            lr_str=lr_str,
            lr_combined=lr_comb,
            log10_lr_combined=log10_comb,
            verbal_statement=verbal,
            integration_summary=summary
        )
