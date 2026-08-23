"""
FORENZA Forensic Biostatistical Engine for MPS STR Analysis.
Calculates Expected Heterozygosity (H_exp), Power of Discrimination (PD),
Match Probability (PM), and Power of Exclusion (PE).
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from .frequency_matrices import SequenceFrequencyMatrixEngine, POPULATION_COHORTS


class LocusBiostatisticsReport(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    locus_name: str
    population: str
    allele_count: int
    expected_heterozygosity: float = Field(..., description="H_exp = 1 - sum(p_i^2)")
    match_probability: float = Field(..., description="PM = sum(p_i^4) + sum_{i<j} 4 p_i^2 p_j^2")
    power_of_discrimination: float = Field(..., description="PD = 1 - PM")
    power_of_exclusion: float = Field(..., description="PE = H_exp^2 * (1 - 2*H_exp*(1-H_exp)^2)")
    exceeds_90pct_heterozygosity: bool = Field(False, description="True if H_exp > 0.90")


class MultiLocusDiversitySummary(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    population: str
    loci_reports: Dict[str, LocusBiostatisticsReport]
    combined_match_probability: float
    combined_power_of_discrimination: float
    loci_exceeding_90pct_count: int
    mean_expected_heterozygosity: float


class ForensicBiostatisticsEngine:
    """
    Computes rigorous forensic biostatistical parameters for sequence-based STR profiles.
    """

    @classmethod
    def calculate_locus_biostatistics(
        cls,
        locus_name: str,
        population: str = "GLOBAL_COMPOSITE"
    ) -> LocusBiostatisticsReport:
        """
        Computes H_exp, PM, PD, and PE for a locus in a specified population.
        """
        freq_dict = SequenceFrequencyMatrixEngine.get_all_frequencies_for_locus(locus_name, population)
        freqs = list(freq_dict.values())
        k = len(freqs)

        # H_exp = 1 - sum(p_i^2)
        sum_p_sq = sum(p ** 2 for p in freqs)
        h_exp = 1.0 - sum_p_sq

        # PM = sum(p_i^4) + sum_{i < j} 4 * p_i^2 * p_j^2
        # Note algebraic identity: PM = 2 * (sum p_i^2)^2 - sum(p_i^4)
        sum_p_fourth = sum(p ** 4 for p in freqs)
        pm = 2.0 * (sum_p_sq ** 2) - sum_p_fourth
        pm = max(1e-15, min(1.0, pm))

        # PD = 1 - PM
        pd = 1.0 - pm

        # PE = H_exp^2 * (1 - 2 * H_exp * (1 - H_exp)^2)
        pe = (h_exp ** 2) * (1.0 - 2.0 * h_exp * ((1.0 - h_exp) ** 2))
        pe = max(0.0, min(1.0, pe))

        return LocusBiostatisticsReport(
            locus_name=locus_name.upper(),
            population=population.upper(),
            allele_count=k,
            expected_heterozygosity=round(h_exp, 4),
            match_probability=round(pm, 6),
            power_of_discrimination=round(pd, 6),
            power_of_exclusion=round(pe, 4),
            exceeds_90pct_heterozygosity=(h_exp >= 0.895)
        )

    @classmethod
    def calculate_multi_locus_summary(
        cls,
        locus_names: List[str],
        population: str = "GLOBAL_COMPOSITE"
    ) -> MultiLocusDiversitySummary:
        """
        Computes combined multi-locus statistical power across all provided loci.
        """
        reports: Dict[str, LocusBiostatisticsReport] = {}
        combined_pm: float = 1.0
        h_exp_list: List[float] = []
        loci_gt_90: int = 0

        for loc in locus_names:
            rep = cls.calculate_locus_biostatistics(loc, population)
            reports[loc.upper()] = rep
            combined_pm *= rep.match_probability
            h_exp_list.append(rep.expected_heterozygosity)
            if rep.exceeds_90pct_heterozygosity:
                loci_gt_90 += 1

        mean_h = sum(h_exp_list) / len(h_exp_list) if h_exp_list else 0.0

        return MultiLocusDiversitySummary(
            population=population.upper(),
            loci_reports=reports,
            combined_match_probability=combined_pm,
            combined_power_of_discrimination=1.0 - combined_pm,
            loci_exceeding_90pct_count=loci_gt_90,
            mean_expected_heterozygosity=round(mean_h, 4)
        )
