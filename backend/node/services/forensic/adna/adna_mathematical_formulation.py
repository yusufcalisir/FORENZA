"""
FORENZA Ancient DNA & Degraded Forensic SNP Damage Kinetics Engine (Module 2.5).
Pure Mathematical & Biocomputational Formulation Engine.

Standards & Research References:
  - Pillar 2 Research §5: Ancient/Degraded DNA Damage Kinetics.
  - Briggs AW et al. (2007) Patterns of damage in genomic DNA sequences from a Neandertal. PNAS 104(37):14616-14621.
  - Jónsson H et al. (2013) mapDamage2.0: Fast approximate Bayesian statistical inference of damage features. Bioinformatics 29(13):1682-1684.
  - ISFG Recommendations on Multi-Modal DNA Evidence Synthesis for Unknown Skeletal Remains (2021).
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any


class DegradationRiskTier(str, Enum):
    SEVERE = "SEVERE"          # Mean length < 60 bp or DI > 10.0
    MODERATE = "MODERATE"      # Mean length 60-90 bp or DI 3.0-10.0
    LOW = "LOW"                # Mean length > 90 bp or DI < 3.0
    PRISTINE = "PRISTINE"      # Modern control, no damage detected


@dataclass(frozen=True)
class MapDamageCurveResult:
    """Computed position-dependent deamination curves for 5' C->T and 3' G->A."""
    delta_0: float                     # Terminal 5' C->T deamination probability
    decay_alpha: float                 # Exponential decay rate per nucleotide distance
    baseline_error: float              # Baseline sequencing error / non-terminal rate
    max_position: int                  # Max distance from termini (default 25 bp)
    curve_5p_c_to_t: Dict[int, float]  # Position (1..25) -> delta_k
    curve_3p_g_to_a: Dict[int, float]  # Position (1..25) -> delta_k


@dataclass(frozen=True)
class FragmentationStats:
    """Fragment length distribution statistics."""
    lambda_param: float                # Rate parameter lambda
    l_min: float                       # Minimum detectable fragment length in bp
    mean_length: float                 # Expected mean length: 1/lambda + L_min
    median_length: float               # Median length: ln(2)/lambda + L_min
    fraction_below_100bp: float        # Fraction of fragments shorter than 100 bp
    degradation_tier: DegradationRiskTier
    recommended_technology: str


@dataclass(frozen=True)
class SNPGenotypeLikelihoodResult:
    """Damage-aware low-coverage SNP genotype likelihood and posterior probabilities."""
    locus_id: str
    ref_allele: str
    alt_allele: str
    read_count: int
    raw_likelihoods: Dict[str, float]          # P(D | G) for AA, AB, BB
    log10_likelihoods: Dict[str, float]        # log10 P(D | G)
    posterior_probabilities: Dict[str, float]  # Normalized P(G | D)
    called_genotype: str
    is_damage_compensated: bool
    deamination_risk_flag: bool


@dataclass(frozen=True)
class MultiSNPLRResult:
    """Cumulative Likelihood Ratio across a micro-multiplex panel of forensic SNPs."""
    total_snps: int
    cumulative_lr: float
    log10_cumulative_lr: float
    per_locus_lr: Dict[str, float]
    prosecutors_fallacy_shield: str


@dataclass(frozen=True)
class ContaminationCorrectionResult:
    """Modern DNA contaminant subtraction from observed damage curve."""
    contamination_fraction: float
    observed_terminal_damage: float
    modern_terminal_damage: float
    true_ancient_terminal_damage: float
    corrected_curve: Dict[int, float]


class AdnaMathematicalFormulation:
    """
    Pure biocomputational engine for ancient & degraded DNA damage kinetics,
    fragmentation modeling, damage-aware genotype calling, and contaminant subtraction.
    """

    # ── 1. Briggs Post-Mortem Deamination Kinetics ───────────────────────────

    @staticmethod
    def compute_deamination_rate(
        k: int,
        delta_0: float = 0.25,
        decay_alpha: float = 0.10,
        baseline: float = 0.005,
    ) -> float:
        """
        Calculates position-dependent cytosine deamination probability at distance k from 5' end.
        Formula: delta_k = delta_0 * exp(-decay_alpha * (k - 1)) + baseline
        """
        if k < 1:
            raise ValueError(f"Position k must be >= 1, got {k}")
        if not (0.0 <= delta_0 <= 1.0):
            raise ValueError(f"delta_0 must be in [0, 1], got {delta_0}")
        if decay_alpha < 0:
            raise ValueError(f"decay_alpha must be non-negative, got {decay_alpha}")

        decayed = delta_0 * math.exp(-decay_alpha * (k - 1))
        return min(1.0, decayed + baseline)

    @classmethod
    def generate_mapdamage_curves(
        cls,
        delta_0: float = 0.25,
        decay_alpha: float = 0.10,
        baseline: float = 0.005,
        max_position: int = 25,
        g_to_a_ratio: float = 1.0,
    ) -> MapDamageCurveResult:
        """
        Generates full 5' C->T and 3' G->A deamination curves up to max_position.
        """
        c_to_t: Dict[int, float] = {}
        g_to_a: Dict[int, float] = {}

        for k in range(1, max_position + 1):
            rate_5p = cls.compute_deamination_rate(k, delta_0, decay_alpha, baseline)
            rate_3p = min(1.0, rate_5p * g_to_a_ratio)
            c_to_t[k] = round(rate_5p, 6)
            g_to_a[k] = round(rate_3p, 6)

        return MapDamageCurveResult(
            delta_0=delta_0,
            decay_alpha=decay_alpha,
            baseline_error=baseline,
            max_position=max_position,
            curve_5p_c_to_t=c_to_t,
            curve_3p_g_to_a=g_to_a,
        )

    # ── 2. Fragment Length Distribution ──────────────────────────────────────

    @staticmethod
    def compute_exponential_fragmentation(
        lambda_param: float = 0.025,
        l_min: float = 30.0,
    ) -> FragmentationStats:
        """
        Computes exponential fragment length distribution stats:
        Mean length: 1 / lambda + L_min
        Median length: ln(2) / lambda + L_min
        CDF(100 bp): 1 - exp(-lambda * (100 - L_min))
        """
        if lambda_param <= 0:
            raise ValueError(f"lambda_param must be positive, got {lambda_param}")
        if l_min < 0:
            raise ValueError(f"l_min must be non-negative, got {l_min}")

        mean_len = (1.0 / lambda_param) + l_min
        median_len = (math.log(2.0) / lambda_param) + l_min

        if 100.0 >= l_min:
            cdf_100 = 1.0 - math.exp(-lambda_param * (100.0 - l_min))
        else:
            cdf_100 = 0.0

        if mean_len < 60.0:
            tier = DegradationRiskTier.SEVERE
            tech = "MICRO_SNP_PANEL_40_70BP"
        elif mean_len < 90.0:
            tier = DegradationRiskTier.MODERATE
            tech = "MINI_STR_OR_NGS_AMPLICONS"
        elif mean_len < 150.0:
            tier = DegradationRiskTier.LOW
            tech = "STANDARD_STR_MULTIPLEX"
        else:
            tier = DegradationRiskTier.PRISTINE
            tech = "FULL_WGS_OR_EXPANDED_CODIS"

        return FragmentationStats(
            lambda_param=lambda_param,
            l_min=l_min,
            mean_length=round(mean_len, 2),
            median_length=round(median_len, 2),
            fraction_below_100bp=round(cdf_100, 4),
            degradation_tier=tier,
            recommended_technology=tech,
        )

    # ── 3. Low-Coverage Damage-Aware SNP Genotype Likelihood ──────────────────

    @classmethod
    def compute_damage_aware_snp_likelihood(
        cls,
        locus_id: str,
        ref_allele: str,
        alt_allele: str,
        read_bases: List[str],
        read_positions: List[int],
        delta_0: float = 0.25,
        decay_alpha: float = 0.10,
        sequencing_error_rate: float = 0.01,
        prior_p_ref: float = 0.50,
    ) -> SNPGenotypeLikelihoodResult:
        """
        Computes damage-compensated genotype likelihoods P(D | G) and posteriors P(G | D)
        for genotypes AA (ref/ref), AB (ref/alt), and BB (alt/alt).
        """
        if len(read_bases) != len(read_positions):
            raise ValueError("read_bases and read_positions must have identical lengths")

        ref = ref_allele.upper()
        alt = alt_allele.upper()
        genotypes = ["AA", "AB", "BB"]
        likelihoods = {"AA": 1.0, "AB": 1.0, "BB": 1.0}

        deamination_risk = (ref == "C" and alt == "T") or (ref == "G" and alt == "A")

        for b_raw, k in zip(read_bases, read_positions):
            b = b_raw.upper()
            pos = max(1, k)
            delta_k = cls.compute_deamination_rate(pos, delta_0, decay_alpha, baseline=0.0) if deamination_risk else 0.0
            e = sequencing_error_rate

            # P(b | G, k)
            # For AA (ref/ref):
            if b == ref:
                p_aa = (1.0 - delta_k) * (1.0 - e)
            elif b == alt and deamination_risk:
                p_aa = delta_k * (1.0 - e) + (1.0 - delta_k) * (e / 3.0)
            else:
                p_aa = e / 3.0

            # For BB (alt/alt):
            if b == alt:
                p_bb = 1.0 - e
            else:
                p_bb = e / 3.0

            # For AB (ref/alt):
            p_ab = 0.5 * p_aa + 0.5 * p_bb

            likelihoods["AA"] *= max(1e-9, p_aa)
            likelihoods["AB"] *= max(1e-9, p_ab)
            likelihoods["BB"] *= max(1e-9, p_bb)

        # Bayesian Priors (HWE assuming allele frequency prior_p_ref)
        p_a = prior_p_ref
        p_b = 1.0 - p_a
        priors = {"AA": p_a * p_a, "AB": 2.0 * p_a * p_b, "BB": p_b * p_b}

        # Posteriors P(G | D)
        unnorm_posteriors = {g: likelihoods[g] * priors[g] for g in genotypes}
        total_p = sum(unnorm_posteriors.values())
        posteriors = {g: (unnorm_posteriors[g] / total_p) if total_p > 0 else 0.333333 for g in genotypes}

        best_g = max(posteriors, key=lambda g: posteriors[g])
        log_likes = {g: (math.log10(likelihoods[g]) if likelihoods[g] > 0 else -300.0) for g in genotypes}

        return SNPGenotypeLikelihoodResult(
            locus_id=locus_id,
            ref_allele=ref,
            alt_allele=alt,
            read_count=len(read_bases),
            raw_likelihoods={g: round(likelihoods[g], 8) for g in genotypes},
            log10_likelihoods={g: round(log_likes[g], 4) for g in genotypes},
            posterior_probabilities={g: round(posteriors[g], 6) for g in genotypes},
            called_genotype=best_g,
            is_damage_compensated=deamination_risk,
            deamination_risk_flag=deamination_risk,
        )

    # ── 4. Multi-SNP Forensic Likelihood Ratio ───────────────────────────────

    @classmethod
    def compute_multi_snp_lr(
        cls,
        snp_results: List[SNPGenotypeLikelihoodResult],
        suspect_genotypes: Dict[str, str],
        allele_freqs: Optional[Dict[str, float]] = None,
    ) -> MultiSNPLRResult:
        """
        Computes cumulative LR across a panel of SNPs:
        LR_SNP = prod_{m=1}^M [ P(D_m | G_S,m) / sum_G P(D_m | G)*P(G) ]
        """
        cum_lr = 1.0
        per_locus_lr: Dict[str, float] = {}

        for snp in snp_results:
            locus = snp.locus_id
            g_s = suspect_genotypes.get(locus, "AA")
            freq_a = allele_freqs.get(locus, 0.50) if allele_freqs else 0.50
            freq_b = 1.0 - freq_a

            priors = {"AA": freq_a * freq_a, "AB": 2.0 * freq_a * freq_b, "BB": freq_b * freq_b}

            p_d_given_gs = snp.raw_likelihoods.get(g_s, 1e-9)
            denom = sum(snp.raw_likelihoods.get(g, 1e-9) * priors[g] for g in ["AA", "AB", "BB"])

            locus_lr = (p_d_given_gs / denom) if denom > 0 else 1.0
            per_locus_lr[locus] = round(locus_lr, 4)
            cum_lr *= locus_lr

        log10_cum = math.log10(cum_lr) if cum_lr > 0 else -300.0

        shield = (
            "ISFG (2021) Paleogenomics Evaluative Reporting Shield: Likelihood ratios incorporate "
            "position-dependent cytosine deamination error modeling. Standalone identification requires "
            "cumulative LR >= 10^6."
        )

        return MultiSNPLRResult(
            total_snps=len(snp_results),
            cumulative_lr=round(cum_lr, 4),
            log10_cumulative_lr=round(log10_cum, 4),
            per_locus_lr=per_locus_lr,
            prosecutors_fallacy_shield=shield,
        )

    # ── 5. Modern Contaminant Subtraction Model ───────────────────────────────

    @classmethod
    def subtract_modern_contamination(
        cls,
        observed_curve: Dict[int, float],
        contamination_fraction: float = 0.12,
        modern_terminal_rate: float = 0.002,
    ) -> ContaminationCorrectionResult:
        """
        Subtracts modern un-deaminated DNA contamination:
        D_ancient(i) = (D_obs(i) - c * D_modern) / (1 - c)
        """
        if not (0.0 <= contamination_fraction < 1.0):
            raise ValueError(f"contamination_fraction must be in [0, 1), got {contamination_fraction}")

        c = contamination_fraction
        corrected: Dict[int, float] = {}

        for k, d_obs in observed_curve.items():
            d_anc = (d_obs - (c * modern_terminal_rate)) / (1.0 - c)
            corrected[k] = round(max(0.0, min(1.0, d_anc)), 6)

        obs_term = observed_curve.get(1, 0.25)
        true_term = corrected.get(1, 0.25)

        return ContaminationCorrectionResult(
            contamination_fraction=c,
            observed_terminal_damage=obs_term,
            modern_terminal_damage=modern_terminal_rate,
            true_ancient_terminal_damage=true_term,
            corrected_curve=corrected,
        )

    # ── 6. Pre-Break Purine Excess ───────────────────────────────────────────

    @staticmethod
    def compute_pre_break_purine_excess(
        purine_minus1_count: int,
        total_reads: int,
    ) -> Tuple[float, bool]:
        """
        Evaluates depurination pre-break excess (A/G at position -1 relative to 5' break site).
        Ancient DNA typically exhibits purine fraction >= 0.65 (65%).
        """
        if total_reads <= 0:
            return 0.50, False

        frac = purine_minus1_count / float(total_reads)
        is_ancient = frac >= 0.65
        return round(frac, 4), is_ancient
