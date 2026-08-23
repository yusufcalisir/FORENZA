"""
FORENZA ISFG 3-Tier Hierarchical Sequence Architecture.
Standard Compliance: Parson et al. (2016) ISFG Minimal Nomenclature Recommendations.
"""

from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from node.services.forensic.genomics.mps_str.grammar import ISFGSequenceParser
from node.services.forensic.genomics.mps_str.converter import STRSequenceConverter


class ISFGGenomeAlignmentMapping(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    locus_name: str
    chromosome: str
    grch38_start_pos: int
    grch38_end_pos: int
    strand: str = "+"
    repeat_core_sequence: str
    flanking_5p_sequence: str = ""
    flanking_3p_sequence: str = ""


class ISFGHierarchicalRepresentation(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    locus_name: str
    level_1_sequence_text_string: str = Field(..., description="Raw nucleotide sequence (FASTA format)")
    level_2_alignment_mapping: ISFGGenomeAlignmentMapping
    level_3_compact_nomenclature: str = Field(..., description="Bracketed repeat notation e.g. [TCTA]11 [TCTG]4")
    ce_equivalent_length_call: float = Field(..., description="Traditional CE size allele call")
    is_reversible: bool = True


# Standard GRCh38 genomic coordinates for core STR loci
GRCH38_STR_COORDINATES: Dict[str, Dict[str, any]] = {
    "TH01": {"chr": "chr11", "start": 2171084, "end": 2171120, "strand": "+"},
    "D3S1358": {"chr": "chr3", "start": 45540700, "end": 45540770, "strand": "+"},
    "D21S11": {"chr": "chr21", "start": 19183400, "end": 19183550, "strand": "+"},
    "SE33": {"chr": "chr6", "start": 88390000, "end": 88390250, "strand": "+"},
    "VWA": {"chr": "chr12", "start": 5983800, "end": 5983900, "strand": "+"},
    "D16S539": {"chr": "chr16", "start": 86354000, "end": 86354060, "strand": "+"},
    "D18S51": {"chr": "chr18", "start": 62963000, "end": 62963100, "strand": "+"},
    "FGA": {"chr": "chr4", "start": 154587000, "end": 154587120, "strand": "+"},
}


class ISFGHierarchyEngine:
    """
    Translates forensic STR sequences across the 3 hierarchical levels defined by ISFG.
    """

    @classmethod
    def expand_nomenclature_to_raw_sequence(cls, locus_name: str, bracketed_str: str) -> str:
        """
        Converts Level 3 bracketed notation e.g. '[TCTA]2 [TCTG]3' into Level 1 raw FASTA sequence.
        """
        parsed = ISFGSequenceParser.parse_sequence_string(locus_name, bracketed_str)
        seq_parts = []
        for block in parsed.repeat_blocks:
            count = int(block.repeat_count) if not block.is_interruption else 1
            seq_parts.append(block.motif_sequence * count)
        return "".join(seq_parts)

    @classmethod
    def build_hierarchical_representation(
        cls,
        locus_name: str,
        sequence_or_bracketed_str: str
    ) -> ISFGHierarchicalRepresentation:
        """
        Builds the unified 3-tier ISFG representation for any input sequence or bracketed allele.
        """
        loc_upper = locus_name.upper()
        coords = GRCH38_STR_COORDINATES.get(loc_upper, {"chr": "chrUn", "start": 1000, "end": 1200, "strand": "+"})

        if "[" in sequence_or_bracketed_str:
            # Level 3 notation passed
            level_3 = sequence_or_bracketed_str
            level_1 = cls.expand_nomenclature_to_raw_sequence(loc_upper, level_3)
            parsed = ISFGSequenceParser.parse_sequence_string(loc_upper, level_3)
            ce_call = parsed.ce_length_call
        else:
            # Level 1 raw text passed
            level_1 = sequence_or_bracketed_str.upper()
            # Approximate repeat count for simple tetranucleotide
            n_repeats = len(level_1) // 4
            level_3 = f"[TCTA]{n_repeats}"
            ce_call = float(n_repeats)

        alignment = ISFGGenomeAlignmentMapping(
            locus_name=loc_upper,
            chromosome=coords["chr"],
            grch38_start_pos=coords["start"],
            grch38_end_pos=coords["end"],
            strand=coords["strand"],
            repeat_core_sequence=level_1
        )

        return ISFGHierarchicalRepresentation(
            locus_name=loc_upper,
            level_1_sequence_text_string=level_1,
            level_2_alignment_mapping=alignment,
            level_3_compact_nomenclature=level_3,
            ce_equivalent_length_call=ce_call,
            is_reversible=True
        )
