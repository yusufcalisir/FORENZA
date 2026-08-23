"""
Genomic Coordinate Liftover & Forward Top-Strand Allele Normalizer.

Standardizes forensic SNP coordinates between GRCh37 and GRCh38 assemblies,
enforcing Watson-Crick forward (+) top-strand allele orientations.
"""

from typing import Dict, Tuple, Optional
from backend.node.services.forensic.genomics.bga.schemas import GenomicAssemblyEnum
from backend.node.services.forensic.genomics.bga.panel_registry import AIMPanelRegistry


class BGALiftoverNormalizer:
    """Normalizes coordinate systems and strand orientations for AIM SNPs."""

    COMPLEMENT_MAP = {
        "A": "T", "T": "A",
        "C": "G", "G": "C",
        "N": "N", "-": "-",
        "0": "0", ".": "."
    }

    IUPAC_TO_ALLELES = {
        "R": ("A", "G"),
        "Y": ("C", "T"),
        "S": ("C", "G"),
        "W": ("A", "T"),
        "K": ("G", "T"),
        "M": ("A", "C"),
    }

    @classmethod
    def normalize_chromosome(cls, chrom_str: str) -> str:
        """Strip 'chr' prefix and canonicalize chromosome identifier."""
        c = chrom_str.strip().upper()
        if c.startswith("CHR"):
            c = c[3:]
        return c

    @classmethod
    def complement_allele(cls, allele: str) -> str:
        """Return the Watson-Crick reverse complement of a nucleotide allele."""
        return "".join(cls.COMPLEMENT_MAP.get(b.upper(), b) for b in allele.strip().upper())

    @classmethod
    def normalize_genotype_strand(
        cls,
        rs_id: str,
        observed_a1: str,
        observed_a2: str
    ) -> Tuple[str, str, float]:
        """
        Normalize genotype call to forward top strand relative to reference/alternate alleles.
        Returns: (normalized_a1, normalized_a2, dosage_alt)
        """
        locus = AIMPanelRegistry.get_locus(rs_id)
        a1 = observed_a1.strip().upper()
        a2 = observed_a2.strip().upper()

        if a1 in ("-", "0", ".", "N") or a2 in ("-", "0", ".", "N"):
            return ("-", "-", 0.0)

        if not locus:
            # Fallback when locus is uncatalogued
            dosage = 0.0
            return (a1, a2, dosage)

        ref = locus.ref_allele.upper()
        alt = locus.alt_allele.upper()

        valid_forward = {ref, alt}
        comp_ref = cls.complement_allele(ref)
        comp_alt = cls.complement_allele(alt)
        valid_reverse = {comp_ref, comp_alt}

        # Check if observed alleles are already forward
        if a1 in valid_forward and a2 in valid_forward:
            norm_a1, norm_a2 = sorted([a1, a2])
            dosage = float((norm_a1 == alt) + (norm_a2 == alt))
            return (norm_a1, norm_a2, dosage)

        # Check if observed alleles are reverse strand and need flipping
        if a1 in valid_reverse and a2 in valid_reverse:
            flipped_a1 = cls.complement_allele(a1)
            flipped_a2 = cls.complement_allele(a2)
            norm_a1, norm_a2 = sorted([flipped_a1, flipped_a2])
            dosage = float((norm_a1 == alt) + (norm_a2 == alt))
            return (norm_a1, norm_a2, dosage)

        # Unknown / ambiguous strand mapping fallback
        dosage = 0.0
        return (a1, a2, dosage)

    @classmethod
    def liftover_position(
        cls,
        rs_id: str,
        from_assembly: GenomicAssemblyEnum,
        to_assembly: GenomicAssemblyEnum
    ) -> Optional[int]:
        """Translate physical position between GRCh37 and GRCh38 for registered AIM loci."""
        locus = AIMPanelRegistry.get_locus(rs_id)
        if not locus:
            return None

        if from_assembly == to_assembly:
            return locus.position_grch38 if to_assembly == GenomicAssemblyEnum.GRCH38 else locus.position_grch37

        if from_assembly == GenomicAssemblyEnum.GRCH37 and to_assembly == GenomicAssemblyEnum.GRCH38:
            return locus.position_grch38
        elif from_assembly == GenomicAssemblyEnum.GRCH38 and to_assembly == GenomicAssemblyEnum.GRCH37:
            return locus.position_grch37

        return locus.position_grch38
