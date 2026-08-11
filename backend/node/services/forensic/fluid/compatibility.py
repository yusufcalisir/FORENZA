"""
FORENZA RNA/DNA Co-Extraction & STR Compatibility Auditor.
Audits RNA yield, R_28S/18S ribosomal integrity ratio, and downstream STR co-extraction compatibility.

Reference:
  Bowden et al. (2011) Direct co-extraction of DNA and RNA from forensic stains.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class CoExtractionAuditResult:
    sample_id: str
    rna_yield_ng_per_ul: float
    rin_integrity_score: float         # RNA Integrity Number (1.0 to 10.0)
    str_co_extraction_compatible: bool
    recommended_strategy: str
    audit_summary: str


class RnaDnaCoExtractor:
    """
    Audits co-extracted RNA and DNA sample quality for combined body fluid & STR analysis.
    """

    def audit_co_extraction(self, sample_id: str, rna_yield: float, rin: float) -> CoExtractionAuditResult:
        is_compatible = rna_yield >= 0.5 and rin >= 5.0

        if rin >= 7.0:
            strategy = "OPTIMAL_CO_EXTRACTION: Full high-resolution mRNA profiling & 24-locus STR amplification."
        elif rin >= 4.0:
            strategy = "MODERATE_INTEGRITY: Short-amplicon Mini-mRNA profiling recommended."
        else:
            strategy = "DEGRADED_RNA: Recommend MiniSTR DNA amplification; mRNA markers may exhibit dropout."

        summary = f"Co-Extraction Audit for {sample_id}: RNA yield = {rna_yield} ng/µL, RIN = {rin}. STR Compatible = {is_compatible}."

        return CoExtractionAuditResult(
            sample_id=sample_id,
            rna_yield_ng_per_ul=rna_yield,
            rin_integrity_score=rin,
            str_co_extraction_compatible=is_compatible,
            recommended_strategy=strategy,
            audit_summary=summary
        )
