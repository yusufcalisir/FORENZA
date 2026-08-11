"""
FORENZA Y-STR Paternal Lineage & Haplotype Analysis Engine.
Implements Y-chromosomal STR haplotype matching across standard 23-locus Y-FILER / PowerPlex Y23 panels,
Haplotype Counting Method, and 95% Clopper-Pearson upper frequency confidence bounds.

Reference:
  SWGDAM Interpretation Guidelines for Y-Chromosome STR Testing (2014).
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# Standard 23 Y-STR Core Markers
Y_STR_CORE_LOCI: List[str] = [
    "DYS19", "DYS385A", "DYS385B", "DYS389I", "DYS389II", "DYS390",
    "DYS391", "DYS392", "DYS393", "DYS437", "DYS438", "DYS439",
    "DYS448", "DYS456", "DYS458", "DYS635", "Y-GATA-H4",
    "DYS481", "DYS533", "DYS570", "DYS576", "DYS643", "DYS549"
]


@dataclass
class YSTRHaplotype:
    haplotype_id: str
    markers: Dict[str, float]          # Marker -> allele (e.g. DYS19 -> 14.0)

    def count_matching_markers(self, other: "YSTRHaplotype") -> Tuple[int, int]:
        """Returns (matching_markers_count, evaluated_loci_count)."""
        common = set(self.markers.keys()) & set(other.markers.keys())
        matches = sum(1 for m in common if self.markers[m] == other.markers[m])
        return matches, len(common)


@dataclass
class YSTRMatchResult:
    evidence_id: str
    suspect_id: str
    matching_loci_count: int
    evaluated_loci_count: int
    haplotype_match_status: str        # 'INCLUSION', 'EXCLUSION', 'PARTIAL_MATCH'
    database_count: int                # Observed frequency in database (e.g. x)
    database_size_n: int               # Total database haplotypes (N)
    haplotype_frequency_estimate: float
    upper_bound_95_ci: float           # 95% Clopper-Pearson upper bound p_upper = 1 - (0.05)^(1/N) for x=0
    paternal_lineage_verdict: str


class YSTREngine:
    """
    Computes Y-STR paternal lineage match probabilities using the SWGDAM Haplotype Counting Method.
    """

    def __init__(self, default_database_n: int = 2500):
        self.default_database_n = default_database_n

    def compute_clopper_pearson_upper_bound(self, x: int, n: int, confidence: float = 0.95) -> float:
        """
        Computes 95% Clopper-Pearson upper bound for haplotype frequency p:
        If x = 0 (unobserved in database): p_upper = 1 - (1 - confidence)^(1 / n)
        For 95% confidence and x=0: p_upper = 1 - 0.05^(1/n)
        """
        if x == 0:
            return round(1.0 - math.pow(1.0 - confidence, 1.0 / n), 6)
        else:
            # Normal approximation upper bound for x > 0
            p_hat = x / n
            z = 1.96
            se = math.sqrt((p_hat * (1 - p_hat)) / n)
            return round(min(1.0, p_hat + z * se), 6)

    def evaluate_ystr_match(
        self,
        evidence: YSTRHaplotype,
        suspect: YSTRHaplotype,
        database_count: int = 0,
        database_size_n: Optional[int] = None
    ) -> YSTRMatchResult:
        """Evaluates Y-STR haplotype match and computes paternal lineage match probability."""
        n = database_size_n or self.default_database_n
        matches, total = evidence.count_matching_markers(suspect)

        if total == 0:
            status = "INCONCLUSIVE"
            verdict = "No overlapping Y-STR markers to evaluate."
        elif matches == total:
            status = "INCLUSION"
            verdict = "Paternal Lineage Match: Evidence and suspect share identical Y-STR haplotype."
        elif matches >= total - 1 and total >= 12:
            status = "PARTIAL_MATCH"
            verdict = "Single locus mutation or partial degradation detected in paternal lineage."
        else:
            status = "EXCLUSION"
            verdict = "Paternal Lineage Exclusion: Y-STR haplotype mismatch eliminates suspect or paternal lineage."

        freq_est = database_count / n
        upper_ci = self.compute_clopper_pearson_upper_bound(database_count, n)

        return YSTRMatchResult(
            evidence_id=evidence.haplotype_id,
            suspect_id=suspect.haplotype_id,
            matching_loci_count=matches,
            evaluated_loci_count=total,
            haplotype_match_status=status,
            database_count=database_count,
            database_size_n=n,
            haplotype_frequency_estimate=round(freq_est, 6),
            upper_bound_95_ci=upper_ci,
            paternal_lineage_verdict=verdict
        )
