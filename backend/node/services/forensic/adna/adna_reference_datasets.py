"""
FORENZA Ancient DNA & Degraded Forensic SNP Reference Datasets & Casework Cohorts (Module 2.5).
Standards Compliance: Christopher Columbus Forensic Validation Series (bioRxiv 2025.12.16.694569),
Briggs et al. (2007) Neandertal deamination series, and ISFG Paleogenomics Standards (2021).
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any

from .adna_mathematical_formulation import DegradationRiskTier


@dataclass(frozen=True)
class AdnaCaseworkCohort:
    cohort_id: str
    name: str
    sample_type: str
    description: str
    delta_0: float                     # Terminal 5' C->T deamination probability
    decay_alpha: float                 # Exponential decay rate per nucleotide
    baseline_error: float              # Baseline error rate
    mean_fragment_length: float        # Mean fragment size in bp
    lambda_fragmentation: float        # Fragmentation rate lambda
    contamination_fraction: float      # Modern DNA contamination fraction
    pre_break_purine_fraction: float   # Purine fraction at -1 position
    expected_degradation_tier: DegradationRiskTier
    expected_tech_recommendation: str


ADNA_CASEWORK_COHORTS: Dict[str, AdnaCaseworkCohort] = {
    "BENCHMARK_COLUMBUS_SKELETAL": AdnaCaseworkCohort(
        cohort_id="BENCHMARK_COLUMBUS_SKELETAL",
        name="Christopher Columbus Skeletal Remains Validation Series",
        sample_type="500-Year-Old Skeletal Remains",
        description="Historical forensic validation cohort with high terminal deamination (delta_0=0.38) and severe fragmentation (52.4 bp).",
        delta_0=0.38,
        decay_alpha=0.14,
        baseline_error=0.006,
        mean_fragment_length=52.4,
        lambda_fragmentation=0.0446,
        contamination_fraction=0.05,
        pre_break_purine_fraction=0.72,
        expected_degradation_tier=DegradationRiskTier.SEVERE,
        expected_tech_recommendation="MICRO_SNP_PANEL_40_70BP",
    ),
    "BENCHMARK_BRIGGS_ANCIENT": AdnaCaseworkCohort(
        cohort_id="BENCHMARK_BRIGGS_ANCIENT",
        name="Briggs Ancient Bone Reference Standard",
        sample_type="Archaeological Bone Specimen",
        description="Classical exponential cytosine deamination gradient across first 20 bp (delta_0=0.28, alpha=0.12).",
        delta_0=0.28,
        decay_alpha=0.12,
        baseline_error=0.005,
        mean_fragment_length=48.2,
        lambda_fragmentation=0.0549,
        contamination_fraction=0.02,
        pre_break_purine_fraction=0.69,
        expected_degradation_tier=DegradationRiskTier.SEVERE,
        expected_tech_recommendation="MICRO_SNP_PANEL_40_70BP",
    ),
    "BENCHMARK_CONTAMINATED_ADNA": AdnaCaseworkCohort(
        cohort_id="BENCHMARK_CONTAMINATED_ADNA",
        name="Admixed Modern/Ancient Contaminated Specimen",
        sample_type="Heavily Handled Forensic Bone",
        description="12% modern un-deaminated DNA contamination requiring mathematical subtraction to reveal true damage kinetics.",
        delta_0=0.22,
        decay_alpha=0.11,
        baseline_error=0.005,
        mean_fragment_length=68.5,
        lambda_fragmentation=0.0260,
        contamination_fraction=0.12,
        pre_break_purine_fraction=0.66,
        expected_degradation_tier=DegradationRiskTier.MODERATE,
        expected_tech_recommendation="MINI_STR_OR_NGS_AMPLICONS",
    ),
    "BENCHMARK_WELL_PRESERVED_COLD": AdnaCaseworkCohort(
        cohort_id="BENCHMARK_WELL_PRESERVED_COLD",
        name="High-Latitude Cryo-Preserved Specimen",
        sample_type="Permafrost / Cold Cave Remains",
        description="Well-preserved cold-climate sample with moderate deamination (delta_0=0.08) and mean length 95.0 bp.",
        delta_0=0.08,
        decay_alpha=0.08,
        baseline_error=0.004,
        mean_fragment_length=95.0,
        lambda_fragmentation=0.0154,
        contamination_fraction=0.01,
        pre_break_purine_fraction=0.58,
        expected_degradation_tier=DegradationRiskTier.LOW,
        expected_tech_recommendation="STANDARD_STR_MULTIPLEX",
    ),
    "BENCHMARK_MODERN_CONTROL_NEGATIVE": AdnaCaseworkCohort(
        cohort_id="BENCHMARK_MODERN_CONTROL_NEGATIVE",
        name="Modern Pristine Blood Reference (Negative Control)",
        sample_type="Pristine Whole Blood",
        description="Modern un-deaminated negative control showing flat damage curve (delta_0=0.002) and intact high-molecular-weight DNA.",
        delta_0=0.002,
        decay_alpha=0.01,
        baseline_error=0.002,
        mean_fragment_length=350.0,
        lambda_fragmentation=0.0031,
        contamination_fraction=0.00,
        pre_break_purine_fraction=0.50,
        expected_degradation_tier=DegradationRiskTier.PRISTINE,
        expected_tech_recommendation="FULL_WGS_OR_EXPANDED_CODIS",
    ),
}


class AdnaReferenceDatasets:
    """Service for accessing ancient DNA benchmarks and casework reference cohorts."""

    @staticmethod
    def list_casework_cohorts() -> List[AdnaCaseworkCohort]:
        return list(ADNA_CASEWORK_COHORTS.values())

    @staticmethod
    def get_cohort(cohort_id: str) -> Optional[AdnaCaseworkCohort]:
        return ADNA_CASEWORK_COHORTS.get(cohort_id)
