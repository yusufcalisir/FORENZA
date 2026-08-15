"""
FORENZA Ancient DNA & Degraded Forensic SNP Damage Kinetics / Human ID (HID) Engine — Module 10.

Implements verbatim from Pillar 2 Research §5:
  - §5.1 Post-Mortem Damage Kinetics (MapDamage / Briggs Model):
           delta_k = delta_0 * (1 - delta_0)^(k - 1)  or  delta_k = delta_0 * exp(-alpha * (k - 1))
           P(L) = lambda * exp(-lambda * (L - L_min))
  - §5.2 Low-Coverage Forensic SNP Genotype Likelihood (GL):
           P(D | G) = prod_{r=1}^R [ sum_{g in G} P(g | G) * ((1 - e_r - d_r)*I(b_r=g) + (e_r + d_r)*I(b_r!=g)) ]
           P(G | D) = P(D | G)*P(G) / sum_{G'} P(D | G')*P(G')
           LR_SNP = prod_{m=1}^M [ P(D_m | G_S,m) / (sum_G P(D_m | G)*P(G)) ]
  - §5.1, §5.2 Skeletal Remains Degradation Index & Multi-Modal Human ID (HID) Synthesis:
           DI = RFU_small / RFU_large, LCN threshold (<100 pg)

References:
  Jónsson H et al. (2013) mapDamage2.0: fast approximate Bayesian statistical inference of damage features in high-throughput sequencing data.
  Briggs AW et al. (2007) Patterns of damage in genomic DNA sequences from a Neandertal.
  ISFG Recommendations on Multi-Modal DNA Evidence Synthesis for Unknown Remains (2021).
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class MapDamageProfile:
    """MapDamage cytosine deamination parameters and computed kinetics curve."""
    delta_0: float                     # Terminal 5' C->T deamination probability (e.g. 0.25)
    decay_alpha: float                 # Exponential decay rate per nucleotide distance (default: 0.10)
    max_position: int                  # Max distance from termini (default: 25 bp)
    damage_curve: Dict[int, float]     # Map of position k -> delta_k


@dataclass
class FragmentationProfile:
    """Ancient/degraded DNA exponential fragmentation length distribution."""
    lambda_param: float                # Rate parameter lambda (e.g. 0.025)
    l_min: float                       # Minimum detectable fragment length in bp (e.g. 30.0)
    mean_length: float                 # Expected mean length: 1/lambda + L_min (e.g. 70.0 bp)
    median_length: float               # Median fragment length: ln(2)/lambda + L_min
    cdf_at_100bp: float                # Fraction of fragments shorter than 100 bp (dropout risk)


@dataclass
class SNPGenotypeLikelihoodResult:
    """Low-coverage genotype likelihood and posterior probabilities for a single SNP."""
    locus_id: str
    ref_allele: str
    alt_allele: str
    read_count: int
    raw_likelihoods: Dict[str, float]      # Likelihood P(D | G) for AA, AB, BB
    log10_likelihoods: Dict[str, float]
    posterior_probabilities: Dict[str, float]  # Normalized P(G | D)
    called_genotype: str
    is_damage_compensated: bool
    deamination_risk_flag: bool


@dataclass
class MultiSNPLRResult:
    """Cumulative forensic Likelihood Ratio across a micro-multiplex panel of SNPs."""
    total_snps: int
    cumulative_lr: float
    log10_cumulative_lr: float
    per_locus_lr: Dict[str, float]
    prosecutors_fallacy_shield: str


@dataclass
class SkeletalDegradationAuditResult:
    """Audit of skeletal remains PCR degradation and LCN stochastic thresholds."""
    profile_id: str
    degradation_index: float           # RFU_small / RFU_large
    small_loci_rfu: float
    large_loci_rfu: float
    dna_input_pg: Optional[float]
    is_lcn_sample: bool                # True if DNA input < 100pg or mean RFU < 150
    long_amplicon_dropout_risk: str    # 'SEVERE', 'MODERATE', 'LOW'
    recommended_technology: str        # 'MICRO_SNP_PANEL_40_70BP', 'MINI_STR', 'STANDARD_STR'
    stochastic_warning: Optional[str]


# ── Engine ─────────────────────────────────────────────────────────────────────

class AncientDNAEngine:
    """
    FORENZA Ancient DNA & Degraded Forensic SNP Damage / HID Engine (Module 10).

    Implements verbatim from Pillar 2 Research §5.
    """

    # ── §5.1 MapDamage Post-Mortem Deamination Kinetics ───────────────────────

    @staticmethod
    def compute_mapdamage_deamination_rate(
        k: int,
        delta_0: float = 0.25,
        decay_alpha: float = 0.10,
    ) -> float:
        """
        Computes the position-dependent cytosine deamination probability at distance k from 5' termini:

        delta_k = delta_0 * exp(-decay_alpha * (k - 1))

        (Research §5.1; MapDamage / Briggs model)
        """
        if k < 1:
            raise ValueError(f"Distance from terminus k must be >= 1, got {k}")
        d0 = max(0.0, min(1.0, delta_0))
        delta_k = d0 * math.exp(-decay_alpha * (k - 1.0))
        return min(1.0, max(0.0, delta_k))

    def generate_mapdamage_profile(
        self,
        delta_0: float = 0.25,
        decay_alpha: float = 0.10,
        max_position: int = 25,
    ) -> MapDamageProfile:
        """Generates the full MapDamage deamination curve across positions 1..max_position."""
        curve = {}
        for k in range(1, max_position + 1):
            curve[k] = round(self.compute_mapdamage_deamination_rate(k, delta_0, decay_alpha), 6)

        return MapDamageProfile(
            delta_0=delta_0,
            decay_alpha=decay_alpha,
            max_position=max_position,
            damage_curve=curve,
        )

    # ── §5.1 Exponential Fragmentation Length Distribution ────────────────────

    @staticmethod
    def compute_fragmentation_distribution(
        lambda_param: float = 0.025,
        l_min: float = 30.0,
    ) -> FragmentationProfile:
        """
        Computes ancient DNA exponential fragmentation length distribution:

        P(L) = lambda * exp(-lambda * (L - L_min))
        F(L) = 1 - exp(-lambda * (L - L_min))
        Mean Length = 1 / lambda + L_min

        (Research §5.1)
        """
        if lambda_param <= 0.0 or l_min < 0.0:
            raise ValueError(f"Invalid fragmentation parameters: lambda={lambda_param}, l_min={l_min}")

        mean_l = (1.0 / lambda_param) + l_min
        median_l = (math.log(2.0) / lambda_param) + l_min
        # Fraction of fragments < 100 bp (critical STR dropout threshold)
        cdf_100 = 1.0 - math.exp(-lambda_param * max(0.0, 100.0 - l_min)) if 100.0 >= l_min else 0.0

        return FragmentationProfile(
            lambda_param=lambda_param,
            l_min=l_min,
            mean_length=round(mean_l, 2),
            median_length=round(median_l, 2),
            cdf_at_100bp=round(cdf_100, 4),
        )

    # ── §5.2 Low-Coverage Forensic SNP Genotype Likelihood ($GL$) ─────────────

    def compute_low_coverage_snp_likelihood(
        self,
        locus_id: str,
        read_bases: List[str],
        read_positions: List[int],
        ref_allele: str = "C",
        alt_allele: str = "T",
        delta_0: float = 0.25,
        decay_alpha: float = 0.10,
        sequencing_error_rate: float = 0.01,
        prior_genotypes: Optional[Dict[str, float]] = None,
    ) -> SNPGenotypeLikelihoodResult:
        """
        Computes low-coverage SNP genotype likelihoods incorporating MapDamage C->T deamination:

        P(D | G) = prod_{r=1}^R [ sum_{g in G} P(g | G) * ((1 - e_r - d_r)*I(b_r=g) + (e_r + d_r)*I(b_r!=g)) ]

        (Research §5.2)
        """
        if len(read_bases) != len(read_positions):
            raise ValueError("read_bases and read_positions must have identical length.")

        genotypes = ["AA", "AB", "BB"]  # AA = Homozygous Ref, AB = Heterozygous, BB = Homozygous Alt
        raw_likelihoods = {g: 1.0 for g in genotypes}

        deamination_flag = False

        for b, k in zip(read_bases, read_positions):
            base_upper = b.upper()
            # Deamination occurs primarily on C->T transitions
            is_potential_deamination = (ref_allele.upper() == "C" and base_upper == "T") or (ref_allele.upper() == "G" and base_upper == "A")
            delta_k = self.compute_mapdamage_deamination_rate(k, delta_0, decay_alpha) if is_potential_deamination else 0.0

            if delta_k > 0.05:
                deamination_flag = True

            e = sequencing_error_rate

            for g in genotypes:
                if g == "AA":
                    # True underlying allele is Ref (A)
                    if base_upper == ref_allele.upper():
                        p_base = (1.0 - delta_k) * (1.0 - e)
                    else:
                        p_base = delta_k + e
                elif g == "BB":
                    # True underlying allele is Alt (B)
                    if base_upper == alt_allele.upper():
                        p_base = 1.0 - e
                    else:
                        p_base = e
                else:  # "AB"
                    # 50% chance Ref allele, 50% chance Alt allele
                    p_ref = (1.0 - delta_k) * (1.0 - e) if base_upper == ref_allele.upper() else (delta_k + e)
                    p_alt = (1.0 - e) if base_upper == alt_allele.upper() else e
                    p_base = 0.5 * p_ref + 0.5 * p_alt

                raw_likelihoods[g] *= max(1e-12, p_base)

        # Prior probabilities (default uniform 1/3 if not provided)
        priors = prior_genotypes or {"AA": 1.0 / 3.0, "AB": 1.0 / 3.0, "BB": 1.0 / 3.0}
        unnorm_posteriors = {g: raw_likelihoods[g] * priors.get(g, 1.0 / 3.0) for g in genotypes}
        total_p = sum(unnorm_posteriors.values())

        if total_p > 0:
            posteriors = {g: unnorm_posteriors[g] / total_p for g in genotypes}
        else:
            posteriors = {g: 1.0 / 3.0 for g in genotypes}

        # Called genotype is argmax posterior
        called_gt = max(posteriors.keys(), key=lambda g: posteriors[g])

        log10_l = {
            g: math.log10(raw_likelihoods[g]) if raw_likelihoods[g] > 0 else -float("inf")
            for g in genotypes
        }

        return SNPGenotypeLikelihoodResult(
            locus_id=locus_id,
            ref_allele=ref_allele.upper(),
            alt_allele=alt_allele.upper(),
            read_count=len(read_bases),
            raw_likelihoods={g: round(raw_likelihoods[g], 8) for g in genotypes},
            log10_likelihoods={g: round(log10_l[g], 5) for g in genotypes},
            posterior_probabilities={g: round(posteriors[g], 6) for g in genotypes},
            called_genotype=called_gt,
            is_damage_compensated=True,
            deamination_risk_flag=deamination_flag,
        )

    # ── §5.2 Multi-SNP Likelihood Ratio Computation ───────────────────────────

    def compute_multi_snp_lr(
        self,
        snp_results: List[SNPGenotypeLikelihoodResult],
        suspect_genotypes: Dict[str, str],
        population_genotype_frequencies: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> MultiSNPLRResult:
        """
        Computes cumulative Forensic Likelihood Ratio across a micro-multiplex SNP panel:

        LR_SNP = prod_{m=1}^M [ P(D_m | G_S,m) / (sum_G P(D_m | G) * P(G)) ]

        (Research §5.2)
        """
        per_locus = {}
        cum_lr = 1.0

        for res in snp_results:
            locus = res.locus_id
            g_s = suspect_genotypes.get(locus, res.called_genotype)

            # Likelihood under Prosecution Hypothesis (Suspect is source)
            p_d_given_gs = res.raw_likelihoods.get(g_s, 1e-12)

            # Likelihood under Defense Hypothesis (Unrelated unknown contributor)
            default_pop = {"AA": 0.25, "AB": 0.50, "BB": 0.25}
            pop_freq = population_genotype_frequencies.get(locus, default_pop) if population_genotype_frequencies else default_pop

            p_d_defense = sum(
                res.raw_likelihoods.get(g, 1e-12) * pop_freq.get(g, 1.0 / 3.0)
                for g in ["AA", "AB", "BB"]
            )

            locus_lr = p_d_given_gs / max(1e-15, p_d_defense)
            per_locus[locus] = round(locus_lr, 4)
            cum_lr *= locus_lr

        cum_lr = max(1e-15, cum_lr)
        log10_cum = math.log10(cum_lr)

        shield = (
            "IMPORTANT (Degraded Forensic SNP Legal Shield): Low-coverage micro-multiplex SNP panels "
            "(40–70 bp amplicons) employ position-dependent MapDamage deamination compensation to prevent "
            "artifactual C->T transition bias. Individual locus likelihoods are synthesized under the product rule."
        )

        return MultiSNPLRResult(
            total_snps=len(snp_results),
            cumulative_lr=round(cum_lr, 4),
            log10_cumulative_lr=round(log10_cum, 5),
            per_locus_lr=per_locus,
            prosecutors_fallacy_shield=shield,
        )

    # ── §5.1 Skeletal Degradation Index Audit ──────────────────────────────────

    @staticmethod
    def audit_skeletal_degradation(
        profile_id: str,
        small_loci_rfu: float = 1200.0,
        large_loci_rfu: float = 350.0,
        dna_input_pg: Optional[float] = None,
    ) -> SkeletalDegradationAuditResult:
        """
        Audits skeletal remains PCR degradation index and LCN thresholds:
        - DI = RFU_small / RFU_large
        - DI >= 2.5: Severe degradation -> Micro-SNP panel (<70 bp) recommended
        - 1.5 <= DI < 2.5: Moderate degradation -> MiniSTR panel (<200 bp)
        - DI < 1.5: Low degradation -> Standard STR typing
        - LCN Sample: DNA input < 100 pg or mean RFU < 150

        (Research §5.1, §5.2)
        """
        large_rfu = max(1.0, large_loci_rfu)
        small_rfu = max(1.0, small_loci_rfu)
        di = small_rfu / large_rfu

        is_lcn = (dna_input_pg is not None and dna_input_pg < 100.0) or (large_rfu < 150.0 and small_rfu < 150.0)

        if di >= 2.5:
            risk = "SEVERE"
            tech = "MICRO_SNP_PANEL_40_70BP"
            warn = "Severe degradation detected (DI >= 2.5): Long amplicons (>300 bp) experience complete dropout. Micro-SNP short amplicons mandated."
        elif di >= 1.5:
            risk = "MODERATE"
            tech = "MINI_STR"
            warn = "Moderate degradation detected (1.5 <= DI < 2.5): Partial long-amplicon dropout risk."
        else:
            risk = "LOW"
            tech = "STANDARD_STR"
            warn = None

        if is_lcn and warn:
            warn += " Sample input is Low-Copy Number (LCN < 100 pg); extreme stochastic allele dropout expected."
        elif is_lcn:
            warn = "Sample input is Low-Copy Number (LCN < 100 pg); stochastic threshold active."

        return SkeletalDegradationAuditResult(
            profile_id=profile_id,
            degradation_index=round(di, 3),
            small_loci_rfu=small_rfu,
            large_loci_rfu=large_rfu,
            dna_input_pg=dna_input_pg,
            is_lcn_sample=is_lcn,
            long_amplicon_dropout_risk=risk,
            recommended_technology=tech,
            stochastic_warning=warn,
        )
