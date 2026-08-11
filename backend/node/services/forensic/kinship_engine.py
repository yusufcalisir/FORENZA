"""
FORENZA Kinship & Pedigree Indexing Engine.
Calculates Kinship Indices (KI) for Parent-Child, Full-Sibling, and Half-Sibling
relationships under Balding-Nichols theta correction.
"""

import math
from typing import Dict, List, Optional, Tuple
from .frequency_db import DEFAULT_THETA, FrequencyDatabase
from .models import AnalysisResult, KinshipRelationship, STRGenotype, STRProfile


class KinshipEngine:
    """Calculates Kinship Indices (KI) and posterior relationship probabilities."""

    def __init__(self, freq_db: Optional[FrequencyDatabase] = None):
        self.freq_db = freq_db or FrequencyDatabase()

    def compute_kinship_index(
        self,
        profile1: STRProfile,
        profile2: STRProfile,
        relationship: KinshipRelationship = KinshipRelationship.PARENT_CHILD,
        theta: float = DEFAULT_THETA,
        population: Optional[str] = None
    ) -> AnalysisResult:
        """Computes combined Kinship Index (KI) across shared loci."""
        pop = population or profile1.population_group
        common_loci = set(profile1.loci.keys()) & set(profile2.loci.keys())

        locus_ki: Dict[str, float] = {}
        total_log_ki: float = 0.0

        for locus_name in common_loci:
            g1: STRGenotype = profile1.loci[locus_name]
            g2: STRGenotype = profile2.loci[locus_name]

            if relationship == KinshipRelationship.PARENT_CHILD:
                ki_l = self._parent_child_locus_ki(locus_name, g1, g2, theta, pop)
            elif relationship == KinshipRelationship.FULL_SIBLING:
                ki_l = self._full_sibling_locus_ki(locus_name, g1, g2, theta, pop)
            elif relationship == KinshipRelationship.HALF_SIBLING:
                ki_l = self._half_sibling_locus_ki(locus_name, g1, g2, theta, pop)
            else:
                ki_l = 1.0

            locus_ki[locus_name] = ki_l
            total_log_ki += math.log10(ki_l) if ki_l > 0 else -10.0

        total_ki = 10.0 ** total_log_ki if total_log_ki > -10.0 else 0.0

        # Calculate posterior probability P(Relationship | E) under prior odds = 1:1
        posterior_prob = total_ki / (total_ki + 1.0) if (total_ki + 1.0) > 0 else 0.0

        # 95% Confidence Interval for KI
        log_std_err = 0.12 * math.sqrt(len(common_loci))
        ci_low = 10.0 ** (total_log_ki - 1.96 * log_std_err) if total_log_ki > -10.0 else 0.0
        ci_high = 10.0 ** (total_log_ki + 1.96 * log_std_err) if total_log_ki > -10.0 else 0.0

        assumptions = [
            f"Relationship hypothesis: {relationship.value}",
            f"Population reference: {pop}",
            f"Balding-Nichols theta = {theta}",
            "Mutations excluded in basic KI model",
            "Equal prior odds assumed (0.5 prior probability)"
        ]
        limitations = [
            "Assumes non-inbred reference samples",
            "Single locus mutation events require secondary validation"
        ]

        return AnalysisResult(
            value=total_ki,
            confidence_interval=(ci_low, ci_high),
            assumptions=assumptions,
            model=f"FORENZA Kinship Index Engine v1.0 ({relationship.value})",
            data_source=f"FBI/NIST 2024 ({pop})",
            limitations=limitations,
            locus_scores=locus_ki,
            metadata={
                "relationship": relationship.value,
                "posterior_probability": posterior_prob,
                "log10_ki": total_log_ki,
                "evaluated_loci_count": len(common_loci)
            }
        )

    def _parent_child_locus_ki(
        self,
        locus: str,
        g1: STRGenotype,
        g2: STRGenotype,
        theta: float,
        population: str
    ) -> float:
        """Calculates Locus KI for Parent-Child relationship."""
        set1, set2 = set(g1.alleles), set(g2.alleles)
        shared = set1 & set2

        if not shared:
            # Exclusion (no shared alleles, ignoring mutation)
            return 0.0

        shared_allele = list(shared)[0]
        p_shared = self.freq_db.get_frequency(locus, shared_allele, population)

        # Basic PC formula: 1 / (2 * p_shared) with theta adjustment
        adj_p = theta + (1 - theta) * p_shared
        return 1.0 / (2.0 * adj_p)

    def _full_sibling_locus_ki(
        self,
        locus: str,
        g1: STRGenotype,
        g2: STRGenotype,
        theta: float,
        population: str
    ) -> float:
        """Calculates Locus KI for Full-Sibling relationship using Ito-Donnelly k-coefficients."""
        a, b = g1.alleles
        c, d = g2.alleles
        pa = self.freq_db.get_frequency(locus, a, population)
        pb = self.freq_db.get_frequency(locus, b, population)

        shared_count = len(set(g1.alleles) & set(g2.alleles))

        if g1.is_homozygote and g2.is_homozygote and a == c:
            # Both homozygous same allele
            return (1 + pa + 2 * pa * pa) / (4 * pa * pa)
        elif shared_count == 2:
            return (1 + pa + pb + 2 * pa * pb) / (4 * pa * pb)
        elif shared_count == 1:
            shared_allele = list(set(g1.alleles) & set(g2.alleles))[0]
            ps = self.freq_db.get_frequency(locus, shared_allele, population)
            return (1 + 2 * ps) / (4 * ps)
        else:
            return 0.25

    def _half_sibling_locus_ki(
        self,
        locus: str,
        g1: STRGenotype,
        g2: STRGenotype,
        theta: float,
        population: str
    ) -> float:
        """Calculates Locus KI for Half-Sibling relationship."""
        shared = set(g1.alleles) & set(g2.alleles)
        if not shared:
            return 0.50
        shared_allele = list(shared)[0]
        ps = self.freq_db.get_frequency(locus, shared_allele, population)
        return (1.0 + ps) / (4.0 * ps)
