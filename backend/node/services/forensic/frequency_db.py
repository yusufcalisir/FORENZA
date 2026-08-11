"""
FORENZA Allele Frequency Database & Balding-Nichols Population Substructure Engine.
Implements NIST/FBI 2024 allele frequency distributions across CODIS 20 core loci
with minimum frequency bounds and Balding-Nichols theta correction.
"""

from typing import Dict, Optional, Tuple

DEFAULT_MIN_FREQUENCY: float = 0.001
DEFAULT_THETA: float = 0.01  # NRC II recommended default theta for intragroup

# NIST/FBI population allele frequency table (subset representation for CODIS 20 loci)
# Frequencies normalized per locus per ethnic group
POPULATION_FREQUENCIES: Dict[str, Dict[str, Dict[float, float]]] = {
    "Caucasian": {
        "CSF1PO": {10.0: 0.252, 11.0: 0.315, 12.0: 0.341, 13.0: 0.068, 9.0: 0.024},
        "FGA": {19.0: 0.062, 20.0: 0.128, 21.0: 0.185, 22.0: 0.198, 23.0: 0.154, 24.0: 0.141, 25.0: 0.082, 26.0: 0.050},
        "TH01": {6.0: 0.231, 7.0: 0.190, 8.0: 0.084, 9.0: 0.154, 9.3: 0.335, 10.0: 0.006},
        "TPOX": {8.0: 0.542, 9.0: 0.118, 10.0: 0.052, 11.0: 0.248, 12.0: 0.040},
        "VWA": {14.0: 0.098, 15.0: 0.112, 16.0: 0.201, 17.0: 0.274, 18.0: 0.205, 19.0: 0.089, 20.0: 0.021},
        "D3S1358": {14.0: 0.134, 15.0: 0.252, 16.0: 0.231, 17.0: 0.208, 18.0: 0.162, 19.0: 0.013},
        "D5S818": {10.0: 0.051, 11.0: 0.342, 12.0: 0.358, 13.0: 0.149, 14.0: 0.095, 9.0: 0.005},
        "D7S820": {8.0: 0.158, 9.0: 0.132, 10.0: 0.264, 11.0: 0.201, 12.0: 0.195, 13.0: 0.050},
        "D8S1179": {10.0: 0.084, 11.0: 0.065, 12.0: 0.145, 13.0: 0.328, 14.0: 0.208, 15.0: 0.131, 16.0: 0.039},
        "D13S317": {8.0: 0.112, 9.0: 0.078, 10.0: 0.054, 11.0: 0.312, 12.0: 0.278, 13.0: 0.141, 14.0: 0.025},
        "D16S539": {9.0: 0.108, 10.0: 0.085, 11.0: 0.304, 12.0: 0.318, 13.0: 0.162, 14.0: 0.023},
        "D18S51": {12.0: 0.138, 13.0: 0.125, 14.0: 0.174, 15.0: 0.152, 16.0: 0.139, 17.0: 0.118, 18.0: 0.068, 19.0: 0.042, 20.0: 0.021, 11.0: 0.023},
        "D21S11": {27.0: 0.045, 28.0: 0.162, 29.0: 0.215, 30.0: 0.238, 31.0: 0.072, 31.2: 0.108, 32.2: 0.121, 33.2: 0.039},
        "D1S1656": {12.0: 0.118, 13.0: 0.064, 14.0: 0.105, 15.0: 0.162, 16.0: 0.138, 17.0: 0.184, 17.3: 0.165, 18.3: 0.064},
        "D2S1338": {17.0: 0.201, 18.0: 0.072, 19.0: 0.134, 20.0: 0.128, 21.0: 0.039, 22.0: 0.045, 23.0: 0.115, 24.0: 0.148, 25.0: 0.118},
        "D10S1248": {12.0: 0.028, 13.0: 0.285, 14.0: 0.364, 15.0: 0.201, 16.0: 0.102, 17.0: 0.020},
        "D12S391": {17.0: 0.102, 18.0: 0.194, 19.0: 0.145, 20.0: 0.138, 21.0: 0.118, 22.0: 0.105, 23.0: 0.098, 24.0: 0.062, 25.0: 0.038},
        "D19S433": {12.0: 0.098, 13.0: 0.252, 14.0: 0.341, 15.0: 0.162, 15.2: 0.078, 16.0: 0.052, 16.2: 0.017},
        "D22S1045": {11.0: 0.082, 14.0: 0.045, 15.0: 0.354, 16.0: 0.382, 17.0: 0.118, 18.0: 0.019},
        "AMEL": {1.0: 0.50, 2.0: 0.50}  # X=1, Y=2 notation
    }
}


class FrequencyDatabase:
    """Manages locus allele frequency lookups with floor minimums and Balding-Nichols theta correction."""

    def __init__(self, default_population: str = "Caucasian", min_frequency: float = DEFAULT_MIN_FREQUENCY):
        self.default_population = default_population
        self.min_frequency = min_frequency

    @property
    def supported_populations(self) -> list:
        return list(POPULATION_FREQUENCIES.keys())

    def get_frequency(self, locus_name: str, allele_value: float, population: Optional[str] = None) -> float:
        """Retrieves bounded frequency for a locus allele."""
        pop = population or self.default_population
        pop_db = POPULATION_FREQUENCIES.get(pop, POPULATION_FREQUENCIES["Caucasian"])
        locus_db = pop_db.get(locus_name.upper(), {})
        freq = locus_db.get(allele_value, self.min_frequency)
        return max(freq, self.min_frequency)

    def calculate_genotype_probability(
        self,
        locus_name: str,
        allele1: float,
        allele2: float,
        theta: float = DEFAULT_THETA,
        population: Optional[str] = None
    ) -> float:
        """
        Calculates Balding-Nichols theta-corrected genotype probability P(G | theta).
        Implements NRC II Recommendation 4.10b.
        """
        p1 = self.get_frequency(locus_name, allele1, population)
        p2 = self.get_frequency(locus_name, allele2, population)

        if allele1 == allele2:
            # Homozygote Balding-Nichols formulation:
            # P(A_i A_i | theta) = [2*theta + (1-theta)*p_i] * [theta + (1-theta)*p_i] / [(1+theta)*(1+2*theta)]
            num = (2 * theta + (1 - theta) * p1) * (theta + (1 - theta) * p1)
            den = (1 + theta) * (1 + 2 * theta)
            return num / den
        else:
            # Heterozygote Balding-Nichols formulation:
            # P(A_i A_j | theta) = 2 * [theta + (1-theta)*p_i] * [theta + (1-theta)*p_j] / [(1+theta)*(1+2*theta)]
            num = 2 * (theta + (1 - theta) * p1) * (theta + (1 - theta) * p2)
            den = (1 + theta) * (1 + 2 * theta)
            return num / den
