"""
GRCh38 Coordinate Normalizer and Liftover Engine.

Standardizes chromosomes, formats top-strand alleles, and harmonizes genomic coordinates.
"""

from typing import Tuple, Dict, Optional


class LiftoverNormalizer:
    """Standardizes chromosome names, coordinates, and strand orientations."""

    # Standard chromosome nomenclature map
    CHROMOSOME_MAP: Dict[str, str] = {
        **{str(i): str(i) for i in range(1, 23)},
        **{f"chr{i}": str(i) for i in range(1, 23)},
        **{f"CHR{i}": str(i) for i in range(1, 23)},
        "x": "X", "chrX": "X", "chrx": "X", "X": "X", "23": "X", "chr23": "X",
        "y": "Y", "chrY": "Y", "chry": "Y", "Y": "Y", "24": "Y", "chr24": "Y",
        "m": "MT", "mt": "MT", "chrM": "MT", "chrmt": "MT", "MT": "MT", "M": "MT", "25": "MT", "26": "MT"
    }

    # Complementary base pairing map
    COMPLEMENT_MAP: Dict[str, str] = {
        "A": "T", "T": "A", "C": "G", "G": "C",
        "N": "N", "-": "-", "0": "0", "?": "?"
    }

    @classmethod
    def normalize_chromosome(cls, raw_chr: str) -> Optional[str]:
        """Harmonizes chromosome string to standard canonical format ('1'-'22', 'X', 'Y', 'MT')."""
        clean = raw_chr.strip().replace('"', '').replace("'", "")
        return cls.CHROMOSOME_MAP.get(clean)

    @classmethod
    def normalize_genotype_call(cls, call_str: str) -> Tuple[str, str, str]:
        """
        Normalizes raw genotype string into (allele1, allele2, normalized_call).
        Examples:
        'AA' -> ('A', 'A', 'AA')
        'CT' -> ('C', 'T', 'CT')
        'T C' -> ('C', 'T', 'CT') (sorted alphabetically)
        '--' or '00' or 'NN' -> ('-', '-', '--')
        'A' (hemizygous / X/Y) -> ('A', 'A', 'AA') or ('A', '-', 'A-')
        """
        clean = call_str.strip().upper().replace("/", "").replace("|", "").replace(" ", "").replace('"', '')
        if not clean or clean in ("--", "00", "NN", "??", "./.", "..", "."):
            return ("-", "-", "--")
        if "." in clean or "-" in clean or "?" in clean:
            return ("-", "-", "--")
        
        if len(clean) == 1:
            # Hemizygous call (e.g. male X or Y)
            return (clean, clean, f"{clean}{clean}")
        
        if len(clean) == 2:
            a1, a2 = clean[0], clean[1]
            if a1 == "-" or a2 == "-":
                return ("-", "-", "--")
            # Alphabetically sort alleles for unambiguous representation
            if a1 <= a2:
                return (a1, a2, f"{a1}{a2}")
            else:
                return (a2, a1, f"{a2}{a1}")
        
        # Fallback for unexpected formats
        return ("-", "-", "--")
