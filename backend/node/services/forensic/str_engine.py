"""
FORENZA Module 01 — STR Profile Engine (24-Locus Expanded Multiplex).

Validates, parses, and manages the expanded 24-locus GlobalFiler-equivalent
STR multiplex (CODIS 20 + SE33 + Penta D + Penta E + Amelogenin).

Mathematical basis:
  - 24-locus completeness validation aligned with Pillar 1 §1.1
  - Allele ordering normalization (allele1 ≤ allele2) for consistent hashing
  - CODIS 20 legacy subset compatibility maintained

Compliance: ISO/IEC 17025:2017 • SWGDAM (2020) • ISFG (2006, 2012, 2016)
"""

from typing import Dict, List, Set, Tuple
from .models import STRGenotype, STRProfile, SampleType
from .frequency_db import CODIS_20_LOCI, LOCI_24

# ── 24-Locus Panel (Pillar 1 §1.1) ─────────────────────────────────────────
LOCI_24_SET: Set[str] = set(LOCI_24)

# CODIS 20 legacy set for backward compatibility
CODIS_20_SET: Set[str] = set(CODIS_20_LOCI)


class STREngine:
    """
    Core STR Profile ingestion, validation, and comparative matching engine
    for the 24-locus expanded autosomal multiplex.
    """

    @staticmethod
    def create_profile_from_dict(
        profile_id: str,
        loci_data: Dict[str, Tuple[float, float]],
        population_group: str = "Caucasian",
        sample_type: SampleType = SampleType.SINGLE_SOURCE,
    ) -> STRProfile:
        """
        Constructs and validates a STRProfile from a raw dict mapping.
        Normalizes locus names to UPPER case and ensures allele ordering
        (allele1 ≤ allele2) for canonical representation.
        """
        loci: Dict[str, STRGenotype] = {}
        for locus_name, alleles in loci_data.items():
            clean_name = locus_name.strip().upper()
            if len(alleles) != 2:
                raise ValueError(
                    f"Locus {locus_name} must contain exactly 2 alleles, got {len(alleles)}"
                )
            a1, a2 = float(alleles[0]), float(alleles[1])
            # Canonical allele ordering: allele1 ≤ allele2
            loci[clean_name] = STRGenotype(
                locus_name=clean_name,
                allele1=min(a1, a2),
                allele2=max(a1, a2),
            )
        return STRProfile(
            profile_id=profile_id,
            loci=loci,
            sample_type=sample_type,
            population_group=population_group,
        )

    @staticmethod
    def validate_24locus_completeness(profile: STRProfile) -> Tuple[bool, List[str]]:
        """
        Checks profile completeness against the full 24-locus multiplex panel.
        Returns (is_complete, list_of_missing_loci).
        """
        missing_loci = [locus for locus in LOCI_24 if locus not in profile.loci]
        is_complete = len(missing_loci) == 0
        return is_complete, missing_loci

    @staticmethod
    def validate_codis_completeness(profile: STRProfile) -> Tuple[bool, List[str]]:
        """
        Checks profile completeness against the CODIS 20 core loci standard.
        Returns (is_complete, list_of_missing_loci).
        """
        missing_loci = [locus for locus in CODIS_20_SET if locus not in profile.loci]
        is_complete = len(missing_loci) == 0
        return is_complete, missing_loci

    @staticmethod
    def compare_profiles(
        profile1: STRProfile,
        profile2: STRProfile,
    ) -> Dict[str, Tuple[bool, Tuple[float, float], Tuple[float, float]]]:
        """
        Compares two STR profiles locus-by-locus across all shared loci.
        Returns dict: locus_name → (is_exact_match, genotype1_alleles, genotype2_alleles).
        """
        common_loci = set(profile1.loci.keys()) & set(profile2.loci.keys())
        comparison: Dict[str, Tuple[bool, Tuple[float, float], Tuple[float, float]]] = {}
        for locus in sorted(common_loci):
            g1 = profile1.loci[locus]
            g2 = profile2.loci[locus]
            is_match = g1.alleles == g2.alleles
            comparison[locus] = (is_match, g1.alleles, g2.alleles)
        return comparison

    @staticmethod
    def count_shared_loci(profile1: STRProfile, profile2: STRProfile) -> int:
        """Returns the count of loci shared between two profiles."""
        return len(set(profile1.loci.keys()) & set(profile2.loci.keys()))

    @staticmethod
    def get_profile_summary(profile: STRProfile) -> Dict[str, object]:
        """Returns a summary metadata dict for the given profile."""
        is_24, missing_24 = STREngine.validate_24locus_completeness(profile)
        is_codis, missing_codis = STREngine.validate_codis_completeness(profile)
        return {
            "profile_id": profile.profile_id,
            "locus_count": profile.locus_count,
            "population_group": profile.population_group,
            "sample_type": profile.sample_type.value,
            "is_24locus_complete": is_24,
            "is_codis20_complete": is_codis,
            "missing_24locus": missing_24,
            "missing_codis20": missing_codis,
            "typed_loci": sorted(profile.loci.keys()),
        }
