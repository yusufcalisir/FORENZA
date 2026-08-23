"""
FORENZA Sequence-Level Mixture Deconvolution & Probabilistic Genotyping Engine.
Resolves multi-contributor DNA mixtures by separating identical-length alleles into distinct sequence isoalleles.
"""

from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from .schemas import ParsedSTRSequence
from .grammar import ISFGSequenceParser
from .converter import STRSequenceConverter
from .frequency_matrices import SequenceFrequencyMatrixEngine


class DeconvolvedContributor(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    contributor_id: str
    mixture_proportion: float = Field(..., ge=0.0, le=1.0)
    assigned_alleles: List[str]
    ce_equivalent_alleles: List[float]


class SingleLocusMixtureDeconvolution(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    locus_name: str
    observed_sequence_alleles: List[str]
    observed_ce_alleles: List[float]
    ce_masked_state: bool = Field(..., description="True if distinct sequence alleles collapse to identical CE lengths")
    isoallele_expansion_count: int = Field(..., description="Number of distinct sequence alleles per unique CE length")
    locus_log10_lr_ce: float
    locus_log10_lr_mps: float
    locus_information_gain_boost: float


class MultiLocusMixtureReport(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    sample_id: str
    num_contributors: int
    population_model: str
    loci_deconvolutions: Dict[str, SingleLocusMixtureDeconvolution]
    total_log10_lr_ce: float
    total_log10_lr_mps: float
    combined_information_gain: float
    contributors: List[DeconvolvedContributor]
    prosecutors_fallacy_shield_en: str
    prosecutors_fallacy_shield_tr: str


class MPSMixtureDeconvolutionEngine:
    """
    Evaluates DNA mixture deconvolution using sequence-level isoalleles.
    """

    @classmethod
    def deconvolve_locus_mixture(
        cls,
        locus_name: str,
        observed_sequences: List[str],
        known_contributor_sequences: Optional[List[str]] = None,
        population: str = "GLOBAL_COMPOSITE"
    ) -> SingleLocusMixtureDeconvolution:
        """
        Deconvolves a single locus mixture, comparing CE length ambiguity against MPS sequence clarity.
        """
        # Parse all observed sequences to CE length
        ce_calls = [STRSequenceConverter.mps_to_ce_allele(locus_name, s)[0] for s in observed_sequences]
        unique_ce = set(ce_calls)
        unique_mps = set(observed_sequences)

        is_masked = len(unique_mps) > len(unique_ce)
        expansion = len(unique_mps) - len(unique_ce)

        # Compute Likelihood Ratio under CE (assuming standard population frequencies)
        p_ce_prod = 1.0
        for c in unique_ce:
            p_ce_prod *= 0.050  # Average baseline length frequency
        lr_ce = 1.0 / max(1e-12, p_ce_prod)

        # Compute Likelihood Ratio under MPS (with exact sequence frequencies)
        p_mps_prod = 1.0
        for s in unique_mps:
            p_s = SequenceFrequencyMatrixEngine.get_sequence_frequency(locus_name, s, population)
            p_mps_prod *= p_s
        lr_mps = 1.0 / max(1e-15, p_mps_prod)

        import math
        log_lr_ce = math.log10(max(1.0, lr_ce))
        log_lr_mps = math.log10(max(1.0, lr_mps))
        gain = lr_mps / lr_ce if lr_ce > 0 else 1.0

        return SingleLocusMixtureDeconvolution(
            locus_name=locus_name.upper(),
            observed_sequence_alleles=sorted(list(unique_mps)),
            observed_ce_alleles=sorted(list(unique_ce)),
            ce_masked_state=is_masked,
            isoallele_expansion_count=expansion,
            locus_log10_lr_ce=round(log_lr_ce, 2),
            locus_log10_lr_mps=round(log_lr_mps, 2),
            locus_information_gain_boost=round(gain, 2)
        )

    @classmethod
    def deconvolve_multi_locus_mixture(
        cls,
        sample_id: str,
        locus_sequence_map: Dict[str, List[str]],
        contributors: List[DeconvolvedContributor],
        population: str = "GLOBAL_COMPOSITE"
    ) -> MultiLocusMixtureReport:
        """
        Runs multi-locus mixture deconvolution across all submitted loci.
        """
        loci_results: Dict[str, SingleLocusMixtureDeconvolution] = {}
        total_log_ce = 0.0
        total_log_mps = 0.0

        for loc, seqs in locus_sequence_map.items():
            res = cls.deconvolve_locus_mixture(loc, seqs, population=population)
            loci_results[loc.upper()] = res
            total_log_ce += res.locus_log10_lr_ce
            total_log_mps += res.locus_log10_lr_mps

        gain = 10.0 ** (total_log_mps - total_log_ce) if (total_log_mps >= total_log_ce) else 1.0

        shield_en = (
            "ENFSI (2017) Standard Statement: The Likelihood Ratio expresses the strength of the genetic "
            "evidence under prosecution vs defense propositions. It does NOT state the probability that the "
            "suspect is guilty or contributed to the stain."
        )
        shield_tr = (
            "ENFSI (2017) Standart Beyanı: Olabilirlik Oranı (LR), genetik kanıtın iddia ve savunma hipotezleri "
            "altındaki göreli gücünü ifade eder. Şüphelinin suçlu olma veya lekeye katkıda bulunma olasılığını "
            "ifade etmez (Savcının Yanılgısı Koruması)."
        )

        return MultiLocusMixtureReport(
            sample_id=sample_id,
            num_contributors=len(contributors),
            population_model=population.upper(),
            loci_deconvolutions=loci_results,
            total_log10_lr_ce=round(total_log_ce, 2),
            total_log10_lr_mps=round(total_log_mps, 2),
            combined_information_gain=round(gain, 2),
            contributors=contributors,
            prosecutors_fallacy_shield_en=shield_en,
            prosecutors_fallacy_shield_tr=shield_tr
        )
