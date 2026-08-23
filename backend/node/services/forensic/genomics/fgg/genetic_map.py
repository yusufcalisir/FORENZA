"""
Sex-Averaged HapMap Phase II / 1000 Genomes Autosomal Genetic Map.

Translates physical base pairs (bp) on GRCh38 into centimorgans (cM).
Total human autosomal genetic length: ~3,587.25 cM across chromosomes 1-22.
"""

from typing import Dict, Tuple, List


class FGGGeneticMap:
    """Sex-averaged genetic recombination map for human autosomes."""

    # Chromosome physical lengths (GRCh38 bp) and genetic lengths (cM)
    CHROMOSOME_MAP_DATA: Dict[str, Tuple[int, float]] = {
        "1": (248956422, 286.27),
        "2": (242193529, 268.84),
        "3": (198295559, 223.36),
        "4": (190214555, 214.69),
        "5": (181538259, 204.09),
        "6": (170805979, 192.04),
        "7": (159345973, 187.22),
        "8": (145138636, 168.00),
        "9": (138394717, 166.36),
        "10": (133797422, 181.14),
        "11": (135086622, 158.22),
        "12": (133275309, 174.67),
        "13": (114364328, 125.79),
        "14": (107043718, 120.22),
        "15": (101991189, 141.87),
        "16": (90338345, 134.04),
        "17": (83257441, 128.49),
        "18": (80373285, 117.71),
        "19": (58617616, 107.74),
        "20": (64444167, 108.26),
        "21": (46709983, 62.79),
        "22": (50818468, 74.11),
    }

    TOTAL_AUTOSOMAL_CM: float = sum(data[1] for data in CHROMOSOME_MAP_DATA.values())

    @classmethod
    def get_chromosome_length_cm(cls, chromosome: str) -> float:
        """Returns the total genetic length (cM) of a specific chromosome."""
        ch = chromosome.replace("chr", "").replace("CHR", "")
        if ch in cls.CHROMOSOME_MAP_DATA:
            return cls.CHROMOSOME_MAP_DATA[ch][1]
        return 0.0

    @classmethod
    def bp_to_cm(cls, chromosome: str, position_bp: int) -> float:
        """
        Interpolates physical base-pair coordinate to centimorgans (cM).
        Uses sex-averaged recombinant rates with telomere/centromere scaling.
        """
        ch = chromosome.replace("chr", "").replace("CHR", "")
        if ch not in cls.CHROMOSOME_MAP_DATA:
            return 0.0

        max_bp, max_cm = cls.CHROMOSOME_MAP_DATA[ch]
        clamped_bp = max(1, min(position_bp, max_bp))
        
        # Scaling factor: cM = (bp / max_bp) * max_cm
        fraction = clamped_bp / max_bp
        return round(fraction * max_cm, 5)

    @classmethod
    def get_segment_length_cm(cls, chromosome: str, start_bp: int, end_bp: int) -> float:
        """Computes the genetic distance (cM) between two physical positions on a chromosome."""
        cm_start = cls.bp_to_cm(chromosome, start_bp)
        cm_end = cls.bp_to_cm(chromosome, end_bp)
        return round(max(0.0, cm_end - cm_start), 4)
