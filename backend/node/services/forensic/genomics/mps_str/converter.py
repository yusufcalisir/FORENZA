"""
FORENZA Bi-directional CE <-> MPS Sequence Converter.
Ensures universal backward compatibility between NGS sequence alleles and legacy CE databases.
"""

from typing import Dict, List, Optional, Tuple
from .schemas import ParsedSTRSequence, SingleLocusMPSGenotype
from .grammar import ISFGSequenceParser
from .flanking_catalog import find_flanking_variant_by_rsid


class STRSequenceConverter:
    """
    Handles bi-directional translation and reconciliation between
    Massively Parallel Sequencing (MPS) and Capillary Electrophoresis (CE).
    """

    # Map of known 4-bp flanking deletions causing +1 repeat shift in short-amplicon MPS vs CE
    SE33_FLANKING_DELETIONS = {"rs369314007", "rs1371483225"}

    @classmethod
    def mps_to_ce_allele(cls, locus_name: str, sequence_string: str) -> Tuple[float, List[str]]:
        """
        Converts an ISFG sequence string to the official CE length call.
        Applies automated reconciliation for known flanking deletions (e.g. SE33 4-bp deletions).
        """
        parsed = ISFGSequenceParser.parse_sequence_string(locus_name, sequence_string)
        ce_call = parsed.ce_length_call
        flags: List[str] = []

        # Check for SE33 4-bp deletion reconciliation
        if locus_name.upper() == "SE33":
            all_flanking_ids = {
                v.rs_id.lower()
                for v in (parsed.flanking_5p_variants + parsed.flanking_3p_variants)
            }
            if any(d in all_flanking_ids for d in cls.SE33_FLANKING_DELETIONS):
                # 4-bp deletion between CE and MPS primer sites causes MPS to appear 1 repeat larger.
                # Reconcile back to official CE size by subtracting 1 full repeat (4 bp)
                adjusted_ce = round(ce_call - 1.0, 1)
                flags.append(f"SE33_4BP_FLANKING_DELETION_RECONCILED: MPS {ce_call} -> CE {adjusted_ce}")
                ce_call = adjusted_ce

        return ce_call, flags

    @classmethod
    def build_single_locus_genotype(
        cls,
        locus_name: str,
        sequence_strings: List[str]
    ) -> SingleLocusMPSGenotype:
        """
        Constructs a complete SingleLocusMPSGenotype from 1 or 2 sequence strings.
        """
        parsed_alleles: List[ParsedSTRSequence] = []
        ce_calls: List[float] = []
        all_flags: List[str] = []

        for seq in sequence_strings:
            parsed = ISFGSequenceParser.parse_sequence_string(locus_name, seq)
            ce_val, flags = cls.mps_to_ce_allele(locus_name, seq)
            parsed.ce_length_call = ce_val
            parsed_alleles.append(parsed)
            ce_calls.append(ce_val)
            all_flags.extend(flags)

        is_het = len(parsed_alleles) > 1 and (
            parsed_alleles[0].raw_sequence_string != parsed_alleles[1].raw_sequence_string
        )

        ce_str = ", ".join(f"{c:g}" for c in sorted(ce_calls))
        mps_str = " / ".join(p.raw_sequence_string for p in parsed_alleles)

        return SingleLocusMPSGenotype(
            locus_name=locus_name.upper(),
            alleles=parsed_alleles,
            is_heterozygous=is_het,
            ce_genotype_string=ce_str,
            mps_genotype_string=mps_str,
            quality_flags=all_flags
        )

    @classmethod
    def check_ce_mps_concordance(
        cls,
        locus_name: str,
        ce_call: float,
        mps_sequence: str
    ) -> bool:
        """
        Verifies if an observed CE length call is 100% concordant with the MPS sequence.
        """
        derived_ce, _ = cls.mps_to_ce_allele(locus_name, mps_sequence)
        return abs(derived_ce - ce_call) < 1e-4
