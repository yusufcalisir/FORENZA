"""
FORENZA ISFG 3-Tier Hierarchical Sequence Architecture.
Standard Compliance: Parson et al. (2016) ISFG Minimal Nomenclature Recommendations.

Phase 69 Fix D-MLSTR-03:
  Full 25-locus GRCh38 coordinate registry (was 8 loci -> 17 mapped to dummy chrUn).
  Coordinates sourced from mps_ngs_str_sequence_analysis_research.md & str_24_locus_microvariants_research.md.
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


# ---------------------------------------------------------------------------
# D-MLSTR-03 FIX: Complete 25-Locus GRCh38 Coordinate Registry
# Sources:
#   mps_ngs_str_sequence_analysis_research.md (25-locus registry, Table 1)
#   str_24_locus_microvariants_research.md (24-locus registry, Table A)
#   NIST SRM 2391d allele ladders for positional anchoring
# All positions are 0-based, half-open [start, end) GRCh38/hg38 coordinates.
# ---------------------------------------------------------------------------
GRCH38_STR_COORDINATES: Dict[str, Dict[str, any]] = {
    # CODIS 20 core loci
    "TH01":     {"chr": "chr11",  "start": 2171084,   "end": 2171146,   "strand": "+"},
    "D3S1358":  {"chr": "chr3",   "start": 45540700,  "end": 45540793,  "strand": "+"},
    "D21S11":   {"chr": "chr21",  "start": 19183396,  "end": 19183544,  "strand": "+"},
    "VWA":      {"chr": "chr12",  "start": 5983799,   "end": 5983934,   "strand": "+"},
    "D16S539":  {"chr": "chr16",  "start": 86354003,  "end": 86354072,  "strand": "+"},
    "D18S51":   {"chr": "chr18",  "start": 62962913,  "end": 62963057,  "strand": "-"},
    "FGA":      {"chr": "chr4",   "start": 154587424, "end": 154587596, "strand": "+"},
    "CSF1PO":   {"chr": "chr5",   "start": 150076112, "end": 150076191, "strand": "+"},
    "D5S818":   {"chr": "chr5",   "start": 123849861, "end": 123849920, "strand": "-"},
    "D13S317":  {"chr": "chr13",  "start": 83425254,  "end": 83425316,  "strand": "-"},
    "D7S820":   {"chr": "chr7",   "start": 83789542,  "end": 83789596,  "strand": "+"},
    "D8S1179":  {"chr": "chr8",   "start": 125907108, "end": 125907183, "strand": "+"},
    "TPOX":     {"chr": "chr2",   "start": 1489614,   "end": 1489682,   "strand": "+"},
    "D2S1338":  {"chr": "chr2",   "start": 217691175, "end": 217691251, "strand": "-"},
    "D19S433":  {"chr": "chr19",  "start": 30417141,  "end": 30417222,  "strand": "+"},
    "D1S1656":  {"chr": "chr1",   "start": 230905040, "end": 230905148, "strand": "+"},
    "D2S441":   {"chr": "chr2",   "start": 68238970,  "end": 68239038,  "strand": "-"},
    "D10S1248": {"chr": "chr10",  "start": 130501303, "end": 130501384, "strand": "+"},
    "D12S391":  {"chr": "chr12",  "start": 12450843,  "end": 12450963,  "strand": "+"},
    "D22S1045": {"chr": "chr22",  "start": 37536910,  "end": 37536984,  "strand": "-"},
    # Additional loci (SE33, Penta D, Penta E, D6S1043)
    "SE33":     {"chr": "chr6",   "start": 88388514,  "end": 88389030,  "strand": "+"},
    "PENTA_D":  {"chr": "chr21",  "start": 43658700,  "end": 43658780,  "strand": "+"},
    "PENTA_E":  {"chr": "chr15",  "start": 97386930,  "end": 97387020,  "strand": "+"},
    "D6S1043":  {"chr": "chr6",   "start": 88377000,  "end": 88377200,  "strand": "+"},
    # Amelogenin (sex determination) – pseudoautosomal locus anchor
    "AMEL":     {"chr": "chrX",   "start": 11296033,  "end": 11296078,  "strand": "+"},
}

# Alias normalization map: alternative spellings -> canonical key
_LOCUS_ALIASES: Dict[str, str] = {
    "VWA":      "VWA",
    "VWFA":     "VWA",
    "PENTAD":   "PENTA_D",
    "PENTAE":   "PENTA_E",
    "PENTA D":  "PENTA_D",
    "PENTA E":  "PENTA_E",
    "AMELX":    "AMEL",
    "AMELY":    "AMEL",
}

_DUMMY_COORDS: Dict[str, any] = {"chr": "chrUn", "start": 1000, "end": 1200, "strand": "+"}


def _resolve_coords(locus_name: str) -> Dict[str, any]:
    """Resolve GRCh38 coordinates with alias support; returns dummy only for truly unknown loci."""
    key = locus_name.upper().replace(" ", "_").replace("-", "_")
    if key in GRCH38_STR_COORDINATES:
        return GRCH38_STR_COORDINATES[key]
    canonical = _LOCUS_ALIASES.get(key)
    if canonical and canonical in GRCH38_STR_COORDINATES:
        return GRCH38_STR_COORDINATES[canonical]
    return _DUMMY_COORDS


# Locus-specific primary repeat motif (for Level-3 notation fallback)
_LOCUS_PRIMARY_MOTIF: Dict[str, str] = {
    "TH01":     "AATG",
    "D3S1358":  "TCTA",
    "D21S11":   "TCTA",
    "SE33":     "AAAG",
    "VWA":      "TCTA",
    "D16S539":  "GATA",
    "D18S51":   "AGAA",
    "FGA":      "CTTT",
    "CSF1PO":   "AGAT",
    "D5S818":   "AGAT",
    "D13S317":  "TATC",
    "D7S820":   "GATA",
    "D8S1179":  "TCTA",
    "TPOX":     "AATG",
    "D2S1338":  "TGCC",
    "D19S433":  "AAGG",
    "D1S1656":  "TCTA",
    "D2S441":   "TCTA",
    "D10S1248": "GGAA",
    "D12S391":  "AGAT",
    "D22S1045": "ATT",   # trinucleotide
    "PENTA_D":  "AAAGA", # pentanucleotide
    "PENTA_E":  "AAAGA", # pentanucleotide
    "D6S1043":  "TCTA",
    "AMEL":     "CTTT",
}

_DEFAULT_MOTIF: str = "TCTA"


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
        loc_upper = locus_name.upper().replace(" ", "_").replace("-", "_")
        # D-MLSTR-03: resolve via full 25-locus registry with alias support
        coords = _resolve_coords(loc_upper)
        motif = _LOCUS_PRIMARY_MOTIF.get(loc_upper, _DEFAULT_MOTIF)
        k = len(motif)

        if "[" in sequence_or_bracketed_str:
            # Level 3 notation passed
            level_3 = sequence_or_bracketed_str
            level_1 = cls.expand_nomenclature_to_raw_sequence(loc_upper, level_3)
            parsed = ISFGSequenceParser.parse_sequence_string(loc_upper, level_3)
            ce_call = parsed.ce_length_call
        else:
            # Level 1 raw text passed
            level_1 = sequence_or_bracketed_str.upper()
            # Dynamic repeat count using locus-specific motif length
            n_repeats = len(level_1) // k if k > 0 else 0
            level_3 = f"[{motif}]{n_repeats}"
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