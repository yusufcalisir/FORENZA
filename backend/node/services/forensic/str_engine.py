"""
FORENZA STR Profile Engine.
Validates, parses, and manages CODIS 20 core loci STR profiles.
"""

from typing import Dict, List, Set, Tuple
from .models import STRGenotype, STRProfile, SampleType

CODIS_20_LOCI: Set[str] = {
    "CSF1PO", "FGA", "TH01", "TPOX", "VWA",
    "D3S1358", "D5S818", "D7S820", "D8S1179", "D13S317",
    "D16S539", "D18S51", "D21S11", "D1S1656", "D2S1338",
    "D10S1248", "D12S391", "D19S433", "D22S1045", "AMEL"
}


class STREngine:
    """Core STR Profile ingestion, validation, and comparative matching engine."""

    @staticmethod
    def create_profile_from_dict(
        profile_id: str,
        loci_data: Dict[str, Tuple[float, float]],
        population_group: str = "Caucasian",
        sample_type: SampleType = SampleType.SINGLE_SOURCE
    ) -> STRProfile:
        """Constructs and validates an STRProfile from raw dictionary mapping."""
        loci: Dict[str, STRGenotype] = {}
        for locus_name, alleles in loci_data.items():
            clean_name = locus_name.strip().upper()
            if len(alleles) != 2:
                raise ValueError(f"Locus {locus_name} must contain exactly 2 alleles, got {len(alleles)}")
            loci[clean_name] = STRGenotype(
                locus_name=clean_name,
                allele1=float(alleles[0]),
                allele2=float(alleles[1])
            )
        return STRProfile(
            profile_id=profile_id,
            loci=loci,
            sample_type=sample_type,
            population_group=population_group
        )

    @staticmethod
    def validate_codis_completeness(profile: STRProfile) -> Tuple[bool, List[str]]:
        """Checks profile completeness against the CODIS 20 core loci standard."""
        missing_loci = [locus for locus in CODIS_20_LOCI if locus not in profile.loci]
        is_complete = len(missing_loci) == 0
        return is_complete, missing_loci

    @staticmethod
    def compare_profiles(
        profile1: STRProfile,
        profile2: STRProfile
    ) -> Dict[str, Tuple[bool, Tuple[float, float], Tuple[float, float]]]:
        """
        Compares two STR profiles locus-by-locus.
        Returns dict mapping locus_name -> (is_exact_match, profile1_genotype, profile2_genotype).
        """
        common_loci = set(profile1.loci.keys()) & set(profile2.loci.keys())
        comparison: Dict[str, Tuple[bool, Tuple[float, float], Tuple[float, float]]] = {}
        for locus in common_loci:
            g1 = profile1.loci[locus]
            g2 = profile2.loci[locus]
            is_match = g1.alleles == g2.alleles
            comparison[locus] = (is_match, g1.alleles, g2.alleles)
        return comparison
