"""
FORENZA Mitochondrial DNA (mtDNA) Maternal Lineage Engine.
Implements mtDNA hypervariable region variant calling across HV1 (16024–16365),
HV2 (73–340), and HV3 (438–574) aligned against Revised Cambridge Reference Sequence (rCRS, AC_000021.2).

Reference:
  EMPOP Mitochondrial DNA Database Standards & SWGDAM mtDNA Interpretation Guidelines (2019).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class MtDnaVariant:
    position: int                      # e.g. 16189
    ref_allele: str                    # e.g. 'C'
    alt_allele: str                    # e.g. 'T'
    region: str                        # 'HV1', 'HV2', 'HV3'


@dataclass
class MtDnaProfile:
    profile_id: str
    haplogroup: Optional[str]          # e.g. 'H1a', 'U5b', 'L2a'
    variants: List[MtDnaVariant]

    def format_rcrs_string(self) -> str:
        """Formats variants in standard EMPOP notation (e.g. 16189T 16223C 263G)."""
        return " ".join(f"{v.position}{v.alt_allele}" for v in sorted(self.variants, key=lambda x: x.position))


@dataclass
class MtDnaMatchResult:
    evidence_id: str
    suspect_id: str
    evidence_rcrs: str
    suspect_rcrs: str
    differing_positions_count: int
    match_status: str                  # 'CANNOT_BE_EXCLUDED', 'INCONCLUSIVE', 'EXCLUDED'
    maternal_lineage_verdict: str


class MtDnaEngine:
    """
    Evaluates mtDNA sequence identity across HV1/HV2/HV3 regions in accordance with SWGDAM guidelines.
    - 0 differences: Cannot be excluded (Same maternal lineage).
    - 1 difference: Inconclusive (Possible heteroplasmy or point mutation).
    - 2+ differences: Excluded (Different maternal lineages).
    """

    def evaluate_mtdna_match(self, evidence: MtDnaProfile, suspect: MtDnaProfile) -> MtDnaMatchResult:
        ev_set = {(v.position, v.alt_allele) for v in evidence.variants}
        sus_set = {(v.position, v.alt_allele) for v in suspect.variants}

        diffs = len(ev_set.symmetric_difference(sus_set))

        if diffs == 0:
            status = "CANNOT_BE_EXCLUDED"
            verdict = "Maternal Lineage Match: Evidence and suspect share identical mtDNA sequence."
        elif diffs == 1:
            status = "INCONCLUSIVE"
            verdict = "Single nucleotide difference observed. Cannot confirm or exclude maternal relationship due to potential heteroplasmy."
        else:
            status = "EXCLUDED"
            verdict = f"Maternal Lineage Exclusion: {diffs} nucleotide differences exclude shared maternal origin."

        return MtDnaMatchResult(
            evidence_id=evidence.profile_id,
            suspect_id=suspect.profile_id,
            evidence_rcrs=evidence.format_rcrs_string(),
            suspect_rcrs=suspect.format_rcrs_string(),
            differing_positions_count=diffs,
            match_status=status,
            maternal_lineage_verdict=verdict
        )
