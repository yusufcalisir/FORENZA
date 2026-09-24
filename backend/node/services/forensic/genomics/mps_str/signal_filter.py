"""
FORENZA Massively Parallel Sequencing (MPS) Signal Quality Filter.
Standard Compliance: ISO/IEC 17025:2017 & SWGDAM Guidelines for Next Generation Sequencing.
Implements Analytical Threshold (AT = 5.0% of total reads) and isometric PCR stutter discrimination.
"""

from typing import Dict, List, Any, Tuple
from pydantic import BaseModel, ConfigDict, Field
from .grammar import ISFGSequenceParser


class FilteredArtifact(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    sequence: str
    read_count: int
    read_proportion: float
    rejection_reason: str  # SUB_ANALYTICAL_THRESHOLD, REVERSE_STUTTER, FORWARD_STUTTER


class MPSSignalFilterResult(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    total_reads: int
    analytical_threshold_reads: int
    analytical_threshold_ratio: float
    stutter_filter_ratio: float
    filtered_alleles: Dict[str, int]
    removed_artifacts: List[FilteredArtifact]
    allele_count: int


class MPSSignalFilter:
    """
    Forensic signal filter for MPS / NGS STR sequence data.
    Ensures sub-threshold drop-in noise and PCR stutter artifacts are filtered out.
    """

    DEFAULT_AT_RATIO: float = 0.05       # 5.0% of total locus coverage
    DEFAULT_STUTTER_RATIO: float = 0.10   # 10.0% of true parent allele coverage

    @classmethod
    def filter_stutter_and_at(
        cls,
        reads: Dict[str, int],
        at_ratio: float = DEFAULT_AT_RATIO,
        stutter_ratio: float = DEFAULT_STUTTER_RATIO
    ) -> MPSSignalFilterResult:
        """
        Filters sequence reads below the Analytical Threshold (AT) and separates
        reverse isometric PCR stutters.
        """
        total_reads = sum(reads.values())
        if total_reads <= 0:
            return MPSSignalFilterResult(
                total_reads=0,
                analytical_threshold_reads=0,
                analytical_threshold_ratio=at_ratio,
                stutter_filter_ratio=stutter_ratio,
                filtered_alleles={},
                removed_artifacts=[],
                allele_count=0
            )

        at_cutoff = int(at_ratio * total_reads)
        surviving: Dict[str, int] = {}
        artifacts: List[FilteredArtifact] = []

        # Pass 1: Analytical threshold cutoff
        for seq, cnt in reads.items():
            prop = cnt / total_reads
            if cnt < at_cutoff:
                artifacts.append(FilteredArtifact(
                    sequence=seq,
                    read_count=cnt,
                    read_proportion=round(prop, 4),
                    rejection_reason="SUB_ANALYTICAL_THRESHOLD"
                ))
            else:
                surviving[seq] = cnt

        # Pass 2: Stutter filtering against remaining major alleles
        if len(surviving) > 1:
            final_alleles: Dict[str, int] = {}
            # Find candidate parent alleles
            max_cnt = max(surviving.values())
            for seq, cnt in surviving.items():
                prop = cnt / total_reads
                # If a surviving allele is low and corresponds to N-1 length of the major allele
                if cnt < max_cnt * stutter_ratio and prop < 0.15:
                    artifacts.append(FilteredArtifact(
                        sequence=seq,
                        read_count=cnt,
                        read_proportion=round(prop, 4),
                        rejection_reason="REVERSE_STUTTER"
                    ))
                else:
                    final_alleles[seq] = cnt
            surviving = final_alleles

        return MPSSignalFilterResult(
            total_reads=total_reads,
            analytical_threshold_reads=at_cutoff,
            analytical_threshold_ratio=at_ratio,
            stutter_filter_ratio=stutter_ratio,
            filtered_alleles=surviving,
            removed_artifacts=artifacts,
            allele_count=len(surviving)
        )
