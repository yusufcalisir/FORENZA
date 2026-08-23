"""
FORENZA ISFG STR Sequence Grammar Parser & EBNF Tokenizer.
Standard Compliance: Parson et al. (2016) ISFG recommendations for STR sequence nomenclature.
"""

import re
from typing import List, Tuple, Optional
from .schemas import MotifBlock, FlankingVariant, ParsedSTRSequence, VariantType
from .flanking_catalog import find_flanking_variant_by_rsid


class ISFGSequenceParser:
    """
    Deterministic parser for ISFG-compliant forensic STR sequence strings.
    Parses bracketed motifs, non-bracketed spacer nucleotides, and 5'/3' flanking annotations.
    """

    # Matches bracketed motif e.g. [TCTA]12 or [CTTT]8.2
    MOTIF_BLOCK_REGEX = re.compile(r"\[([A-Za-z]+)\]([0-9]+(?:\.[0-9]+)?)")
    # Matches plain intervening nucleotide sequences e.g. TA, TCA, CTTC, TT
    INTERVENING_SEQ_REGEX = re.compile(r"^[A-Za-z]+$")
    # Matches flanking variant annotations e.g. rs9362477[C>T], rs369314007[delTTTT], rs1452632862[delT]
    FLANKING_ANN_REGEX = re.compile(r"(rs\d+)\[(?:([A-Za-z]+)>([A-Za-z]+)|(del|ins)([A-Za-z]+))\]")

    @classmethod
    def parse_sequence_string(cls, locus_name: str, raw_seq: str) -> ParsedSTRSequence:
        """
        Parses a complete sequence string into a structured ParsedSTRSequence object.
        Handles flanking annotations separated by underscores '_'.
        """
        cleaned = raw_seq.strip()
        parts = cleaned.split("_")
        
        flanking_5p: List[FlankingVariant] = []
        flanking_3p: List[FlankingVariant] = []
        repeat_part: str = ""

        if len(parts) == 1:
            repeat_part = parts[0]
        elif len(parts) == 2:
            # Could be 5p_repeat or repeat_3p
            if "rs" in parts[0].lower():
                flanking_5p = cls._parse_flanking_tokens(parts[0])
                repeat_part = parts[1]
            else:
                repeat_part = parts[0]
                flanking_3p = cls._parse_flanking_tokens(parts[1])
        elif len(parts) >= 3:
            flanking_5p = cls._parse_flanking_tokens(parts[0])
            repeat_part = "_".join(parts[1:-1])  # Middle components
            flanking_3p = cls._parse_flanking_tokens(parts[-1])

        # Tokenize repeat region
        repeat_blocks, total_bp, ce_length = cls._tokenize_repeat_region(locus_name, repeat_part)

        # Check if complex repeat
        is_complex = len(repeat_blocks) > 1 or any(b.is_interruption for b in repeat_blocks)

        return ParsedSTRSequence(
            locus_name=locus_name.upper(),
            raw_sequence_string=cleaned,
            repeat_blocks=repeat_blocks,
            flanking_5p_variants=flanking_5p,
            flanking_3p_variants=flanking_3p,
            ce_length_call=ce_length,
            repeat_bp_length=total_bp,
            is_complex_repeat=is_complex
        )

    @classmethod
    def _parse_flanking_tokens(cls, token_str: str) -> List[FlankingVariant]:
        """Parses semicolon or comma-separated flanking annotations."""
        variants: List[FlankingVariant] = []
        tokens = token_str.replace(",", ";").split(";")
        
        for tok in tokens:
            tok = tok.strip()
            if not tok:
                continue
            m = cls.FLANKING_ANN_REGEX.search(tok)
            if m:
                rs_id = m.group(1)
                ref_sub = m.group(2)
                alt_sub = m.group(3)
                indel_type = m.group(4)
                indel_seq = m.group(5)
                
                cataloged = find_flanking_variant_by_rsid(rs_id)
                pos = cataloged.position_relative if cataloged else 0
                pop_note = cataloged.population_note if cataloged else None

                if indel_type == "del":
                    var = FlankingVariant(
                        rs_id=rs_id,
                        position_relative=pos,
                        ref_allele=indel_seq,
                        alt_allele="",
                        variant_type=VariantType.DELETION,
                        population_note=pop_note
                    )
                elif indel_type == "ins":
                    var = FlankingVariant(
                        rs_id=rs_id,
                        position_relative=pos,
                        ref_allele="",
                        alt_allele=indel_seq,
                        variant_type=VariantType.INSERTION,
                        population_note=pop_note
                    )
                else:
                    var = FlankingVariant(
                        rs_id=rs_id,
                        position_relative=pos,
                        ref_allele=ref_sub if ref_sub else (cataloged.ref_allele if cataloged else "N"),
                        alt_allele=alt_sub if alt_sub else (cataloged.alt_allele if cataloged else "N"),
                        variant_type=VariantType.SNP,
                        population_note=pop_note
                    )
                variants.append(var)
            elif "rs" in tok.lower():
                # Direct rsID lookup without bracket notation
                rs_only = tok.strip()
                cataloged = find_flanking_variant_by_rsid(rs_only)
                if cataloged:
                    variants.append(cataloged)
        return variants

    @classmethod
    def _tokenize_repeat_region(cls, locus_name: str, repeat_str: str) -> Tuple[List[MotifBlock], int, float]:
        """
        Tokenizes space-separated motif blocks and intervening spacer sequences.
        Computes total base pair length and CE repeat length call.
        """
        tokens = [t.strip() for t in repeat_str.split() if t.strip()]
        blocks: List[MotifBlock] = []
        total_bp: int = 0
        total_repeats: float = 0.0

        for tok in tokens:
            m = cls.MOTIF_BLOCK_REGEX.match(tok)
            if m:
                motif = m.group(1).upper()
                count = float(m.group(2))
                bp_len = int(len(motif) * count)
                total_bp += bp_len
                total_repeats += count
                blocks.append(MotifBlock(
                    motif_sequence=motif,
                    repeat_count=count,
                    is_interruption=False
                ))
            elif cls.INTERVENING_SEQ_REGEX.match(tok):
                # Intervening spacer e.g. TA, TCA, CTTC, TT
                spacer = tok.upper()
                bp_len = len(spacer)
                total_bp += bp_len
                # Fractional repeat contribution based on standard tetranucleotide (or trinucleotide/pentanucleotide) unit
                unit_size = cls._get_canonical_repeat_unit_size(locus_name)
                partial_repeat = bp_len / unit_size
                total_repeats += partial_repeat
                blocks.append(MotifBlock(
                    motif_sequence=spacer,
                    repeat_count=round(partial_repeat, 3),
                    is_interruption=True
                ))

        # Calculate exact CE length call
        ce_length = cls._compute_ce_length(locus_name, total_bp, total_repeats)
        return blocks, total_bp, ce_length

    @staticmethod
    def _get_canonical_repeat_unit_size(locus_name: str) -> int:
        """Returns the canonical base pair size of the repeat motif for a locus."""
        trinucleotides = {"D22S1045"}
        pentanucleotides = {"PENTA_D", "PENTA_E", "PENTAD", "PENTAE"}
        hexanucleotides = {"DYS391"}  # DYS391 is tetranucleotide [TCTA]

        loc = locus_name.upper().replace(" ", "").replace("_", "")
        if loc in trinucleotides:
            return 3
        elif "PENTA" in loc:
            return 5
        return 4  # Default standard tetranucleotide

    @classmethod
    def _compute_ce_length(cls, locus_name: str, total_bp: int, raw_repeat_sum: float) -> float:
        """
        Converts total base pair length and repeat sum into standard forensic CE allele call.
        Rounds microvariants to 1 decimal place (e.g. .1, .2, .3).
        """
        unit = cls._get_canonical_repeat_unit_size(locus_name)
        full_repeats = total_bp // unit
        rem_bp = total_bp % unit

        if rem_bp == 0:
            return float(full_repeats)
        else:
            return float(f"{full_repeats}.{rem_bp}")
