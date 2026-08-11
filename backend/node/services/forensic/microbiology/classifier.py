"""
FORENZA Forensic Microbiology & 16S rRNA Taxonomic Classifier Engine.
Analyzes 16S rRNA hypervariable regions (V3-V4) and fungal ITS barcode relative abundance profiles.
Computes Shannon Diversity Index (H') and Bray-Curtis dissimilarity:
  D_Bray-Curtis = 1 - 2 * sum(min(u_i, v_i)) / sum(u_i + v_i)

Reference:
  Hampton-Marcell et al. (2017) Considerations for the use of microbial forensics in criminal investigations.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class TaxonAbundance:
    genus_name: str                    # e.g. 'Cutibacterium', 'Streptococcus', 'Lactobacillus', 'Bacteroides'
    phylum_name: str                   # e.g. 'Actinomycetota', 'Bacillota', 'Bacteroidota'
    relative_abundance: float          # Proportional abundance (0.0 to 1.0)


@dataclass
class MicrobialProfileData:
    sample_id: str
    sample_type: str                   # 'BODY_TRACE', 'SOIL_SWAB', 'TOUCH_SURFACE'
    taxa: List[TaxonAbundance]


@dataclass
class MicrobialClassificationResult:
    sample_id: str
    shannon_diversity_index: float     # H' diversity metric
    dominant_genus: str
    dominant_phylum: str
    taxa_count: int
    microbiology_summary: str


class ForensicMicrobiologyEngine:
    """
    Classifies 16S rRNA microbial community compositions and diversity metrics.
    """

    def classify_microbial_profile(self, profile: MicrobialProfileData) -> MicrobialClassificationResult:
        taxa_cnt = len(profile.taxa)

        # Shannon Diversity Index H' = - sum(p_i * ln(p_i))
        h_prime = 0.0
        max_abund = 0.0
        dom_genus = "Unknown"
        dom_phylum = "Unknown"

        for t in profile.taxa:
            p = t.relative_abundance
            if p > 0.0:
                h_prime -= p * math.log(p)
            if p > max_abund:
                max_abund = p
                dom_genus = t.genus_name
                dom_phylum = t.phylum_name

        h_prime_round = round(h_prime, 4)

        summary = f"Microbial Classification for {profile.sample_id}: Dominant genus = {dom_genus} ({dom_phylum}, {int(max_abund*100)}%), Shannon H' = {h_prime_round}."

        return MicrobialClassificationResult(
            sample_id=profile.sample_id,
            shannon_diversity_index=h_prime_round,
            dominant_genus=dom_genus,
            dominant_phylum=dom_phylum,
            taxa_count=taxa_cnt,
            microbiology_summary=summary
        )

    def compute_bray_curtis_distance(self, profile1: MicrobialProfileData, profile2: MicrobialProfileData) -> float:
        """Computes Bray-Curtis dissimilarity between two microbial community profiles."""
        map1 = {t.genus_name: t.relative_abundance for t in profile1.taxa}
        map2 = {t.genus_name: t.relative_abundance for t in profile2.taxa}

        all_genera = set(map1.keys()).union(set(map2.keys()))

        sum_min = 0.0
        sum_total = 0.0

        for g in all_genera:
            u = map1.get(g, 0.0)
            v = map2.get(g, 0.0)
            sum_min += min(u, v)
            sum_total += u + v

        if sum_total == 0.0:
            return 0.0

        dissimilarity = 1.0 - (2.0 * sum_min / sum_total)
        return round(max(0.0, min(1.0, dissimilarity)), 4)
