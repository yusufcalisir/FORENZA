"""
FORENZA X-STR Familial Kinship & Linkage Analysis Engine.
Implements X-chromosomal STR marker evaluation across standard Investigator Argus X-12 panels,
linkage group analysis, and X-kinship index (KI_X) calculations for complex relationship testing.

Reference:
  ISFG Recommendations on Forensic Interpretation of X-Chromosomal Markers (2012).
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# Investigator Argus X-12 Linkage Groups (4 clusters of 3 tightly linked markers)
X_STR_LINKAGE_GROUPS: Dict[str, List[str]] = {
    "LG1": ["DXS10148", "DXS10135", "DXS8378"],
    "LG2": ["DXS7132", "DXS10079", "DXS10074"],
    "LG3": ["DXS10101", "DXS10103", "DXS10108"],
    "LG4": ["DXS10146", "DXS10134", "DXS10147"]
}


@dataclass
class XSTRGenotype:
    locus: str
    allele1: float
    allele2: Optional[float] = None   # None for hemizygous males


@dataclass
class XSTRProfile:
    profile_id: str
    is_male: bool
    loci: Dict[str, XSTRGenotype]


@dataclass
class XSTRKinshipResult:
    profile1_id: str
    profile2_id: str
    relationship_tested: str           # 'FATHER_DAUGHTER', 'HALF_SISTERS_PATERNAL', 'MOTHER_SON'
    combined_ki_x: float
    log10_ki_x: float
    evaluated_loci_count: int
    kinship_verdict: str


class XSTREngine:
    """
    Computes X-chromosomal Likelihood Ratios (KI_X) accounting for X-chromosome inheritance patterns.
    - Males are hemizygous (1 X allele). Females are heterozygous/homozygous (2 X alleles).
    - A father transmits his single X chromosome intact to all daughters.
    """

    def calculate_father_daughter_locus_ki(self, father: XSTRGenotype, daughter: XSTRGenotype, p_allele: float = 0.20) -> float:
        """
        Father (male: 1 allele A_f) and Daughter (female: 2 alleles A_d1, A_d2).
        Father MUST pass his X allele A_f to daughter.
        If A_f is in daughter's alleles: KI_l = 1 / (2 * p_f)
        Else: KI_l = 0.0 (Exclusion)
        """
        f_allele = father.allele1
        d_alleles = [daughter.allele1, daughter.allele2] if daughter.allele2 is not None else [daughter.allele1]

        if f_allele in d_alleles:
            return round(1.0 / (2.0 * max(0.001, p_allele)), 4)
        else:
            return 0.0

    def evaluate_x_kinship(
        self,
        profile1: XSTRProfile,
        profile2: XSTRProfile,
        relationship: str = "FATHER_DAUGHTER"
    ) -> XSTRKinshipResult:
        """Evaluates X-STR kinship across shared loci."""
        common = set(profile1.loci.keys()) & set(profile2.loci.keys())
        total_log_ki = 0.0
        evaluated = 0

        for locus in common:
            g1 = profile1.loci[locus]
            g2 = profile2.loci[locus]

            if relationship == "FATHER_DAUGHTER":
                if profile1.is_male and not profile2.is_male:
                    ki_l = self.calculate_father_daughter_locus_ki(g1, g2)
                elif profile2.is_male and not profile1.is_male:
                    ki_l = self.calculate_father_daughter_locus_ki(g2, g1)
                else:
                    ki_l = 1.0
            else:
                ki_l = 1.0

            if ki_l == 0.0:
                total_log_ki = -99.0
                break

            total_log_ki += math.log10(ki_l)
            evaluated += 1

        if total_log_ki < -90.0:
            combined_ki = 0.0
            status_str = "EXCLUSION: X-chromosomal mismatch violates inheritance rules."
        else:
            combined_ki = round(math.pow(10.0, total_log_ki), 2)
            status_str = f"SUPPORTED: Strong X-chromosomal kinship evidence (KI_X = {combined_ki})."

        return XSTRKinshipResult(
            profile1_id=profile1.profile_id,
            profile2_id=profile2.profile_id,
            relationship_tested=relationship,
            combined_ki_x=combined_ki,
            log10_ki_x=round(max(-99.0, total_log_ki), 4),
            evaluated_loci_count=evaluated,
            kinship_verdict=status_str
        )
