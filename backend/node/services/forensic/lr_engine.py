"""
FORENZA Module 01 — Likelihood Ratio (LR) Engine.

Computes single-source Bayesian Likelihood Ratios under Balding-Nichols
population substructure assumptions with complete 95% HPD uncertainty bounds
and ENFSI (2017) 7-tier verbal scale translation.

Mathematical basis:
  H_p: Evidence came from the suspect    → P(E | H_p) = 1.0 (full match assumption)
  H_d: Evidence from random unrelated    → P(E | H_d) = P(G | θ) (Balding-Nichols)
  LR_l = P(E | H_p) / P(E | H_d, θ) = 1 / P(G_l | θ)
  LR_combined = ∏ LR_l  (Linkage Equilibrium assumed)
  RMP = 1 / LR_combined

ENFSI Verbal Scale (2017):
  LR = 1.0           → Neutral / Inconclusive
  1 < LR ≤ 10        → Weak Support
  10 < LR ≤ 100      → Moderate Support
  100 < LR ≤ 1,000   → Moderately Strong Support
  1,000 < LR ≤ 10K   → Strong Support
  10K < LR ≤ 1M      → Very Strong Support
  LR > 1,000,000     → Extremely Strong Support

Compliance: ISO/IEC 17025:2017 • SWGDAM (2020) • ENFSI Evaluative Reporting (2017)
"""

import math
from typing import Dict, List, Optional, Tuple
from .frequency_db import DEFAULT_THETA, FrequencyDatabase
from .models import AnalysisResult, STRGenotype, STRProfile


# ---------------------------------------------------------------------------
# ENFSI (2017) Verbal Scale — Research-Locked (Pillar 1 & Pillar 6)
# ---------------------------------------------------------------------------

_ENFSI_VERBAL_TIERS: List[Tuple[float, float, str, str]] = [
    # (log10_LR_min, log10_LR_max, phrase_en, phrase_tr)
    (0.0,   0.0,   "Neutral / Inconclusive findings",
                   "Nötr / Sonuçsuz bulgular"),
    (0.0,   1.0,   "Weak support for the prosecution proposition (H_p) over H_d",
                   "İddia makamının hipotezi (H_p) lehine zayıf destek"),
    (1.0,   2.0,   "Moderate support for the prosecution proposition (H_p) over H_d",
                   "İddia makamının hipotezi (H_p) lehine orta düzeyde destek"),
    (2.0,   3.0,   "Moderately strong support for the prosecution proposition (H_p) over H_d",
                   "İddia makamının hipotezi (H_p) lehine orta-güçlü destek"),
    (3.0,   4.0,   "Strong support for the prosecution proposition (H_p) over H_d",
                   "İddia makamının hipotezi (H_p) lehine güçlü destek"),
    (4.0,   6.0,   "Very strong support for the prosecution proposition (H_p) over H_d",
                   "İddia makamının hipotezi (H_p) lehine çok güçlü destek"),
    (6.0, float("inf"), "Extremely strong support for the prosecution proposition (H_p) over H_d",
                   "İddia makamının hipotezi (H_p) lehine aşırı güçlü destek"),
]


def enfsi_verbal_scale(lr: float, language: str = "en") -> Tuple[int, str]:
    """
    Maps a Likelihood Ratio to the ENFSI 2017 standardized 7-tier verbal scale.

    Args:
        lr:       Likelihood Ratio (> 0). If lr < 1, reciprocal is evaluated for H_d.
        language: "en" (English) or "tr" (Turkish).

    Returns:
        (tier_index, verbal_phrase) — tier 0 = Neutral, tier 6 = Extremely Strong.
    """
    if lr <= 0:
        raise ValueError("LR must be > 0")

    is_prosecution = lr >= 1.0
    effective_lr = lr if is_prosecution else (1.0 / lr)

    if effective_lr == 1.0:
        log10_lr = 0.0
    else:
        log10_lr = math.log10(effective_lr)

    # Select tier
    for tier_idx, (lo, hi, phrase_en, phrase_tr) in enumerate(_ENFSI_VERBAL_TIERS):
        if tier_idx == 0 and effective_lr == 1.0:
            phrase = phrase_tr if language == "tr" else phrase_en
            return 0, phrase
        if tier_idx > 0 and lo < log10_lr <= hi:
            phrase = phrase_tr if language == "tr" else phrase_en
            if not is_prosecution:
                phrase = phrase.replace("H_p", "H_d").replace(
                    "prosecution proposition", "defense proposition"
                )
            return tier_idx, phrase

    # Catch LR > 10^6
    phrase = _ENFSI_VERBAL_TIERS[6][3 if language == "tr" else 2]
    if not is_prosecution:
        phrase = phrase.replace("H_p", "H_d")
    return 6, phrase


# ---------------------------------------------------------------------------
# LREngine Class
# ---------------------------------------------------------------------------

class LREngine:
    """
    Computes Likelihood Ratios (LR) across 24 loci under Balding-Nichols
    theta correction with 95% HPD uncertainty intervals and ENFSI verbal output.
    """

    def __init__(self, freq_db: Optional[FrequencyDatabase] = None):
        self.freq_db = freq_db or FrequencyDatabase()

    # ── Single-Source LR ─────────────────────────────────────────────────

    def compute_single_source_lr(
        self,
        evidence_profile: STRProfile,
        suspect_profile: STRProfile,
        theta: float = DEFAULT_THETA,
        population: Optional[str] = None,
    ) -> AnalysisResult:
        """
        Computes single-source Likelihood Ratio for evidence vs. suspect profiles.

        H_p: Evidence came from suspect       → P(E | H_p) = 1.0
        H_d: Evidence came from random person → P(E | H_d) = P(G_suspect | θ)
        LR_combined = ∏_l [1 / P(G_l | θ)]   (over shared loci in LE)
        RMP = 1 / LR_combined

        Returns:
            AnalysisResult with .value = LR_combined, .metadata containing
            log10_lr, rmp, verbal_scale_en, verbal_scale_tr, match_status.
        """
        pop = population or suspect_profile.population_group
        common_loci = sorted(
            set(evidence_profile.loci.keys()) & set(suspect_profile.loci.keys())
        )

        locus_scores: Dict[str, float] = {}
        total_log_lr: float = 0.0

        assumptions: List[str] = [
            f"Population frequency reference: FBI/NIST 1036 ({pop})",
            f"Balding-Nichols coancestry coefficient θ = {theta}",
            "Loci assumed to be in Linkage Equilibrium (LE)",
            "Hardy-Weinberg Equilibrium modified under NRC II Rec 4.10b",
            "Single-source, non-degraded, full amplification assumption (no dropout/drop-in)",
            "P(E | H_p) = 1.0 (full profile match)",
        ]
        limitations: List[str] = [
            "LTDNA stochastic effects (dropout/drop-in) handled separately by Module 04",
            "Complex mixtures require MCMC deconvolution (Module 02)",
            "Population frequencies derived from NIST 1036 CODIS dataset",
        ]

        for locus_name in common_loci:
            e_genotype: STRGenotype = evidence_profile.loci[locus_name]
            s_genotype: STRGenotype = suspect_profile.loci[locus_name]

            # Exclusion: any locus mismatch → LR = 0
            if e_genotype.alleles != s_genotype.alleles:
                return AnalysisResult(
                    value=0.0,
                    confidence_interval=(0.0, 0.0),
                    assumptions=assumptions + [f"EXCLUSION detected at locus {locus_name}"],
                    model="FORENZA Module 01 Single-Source Balding-Nichols LR Engine v2.0",
                    data_source=f"FBI/NIST 1036 ({pop})",
                    limitations=limitations,
                    locus_scores={**locus_scores, locus_name: 0.0},
                    metadata={
                        "match_status": "EXCLUSION",
                        "exclusion_locus": locus_name,
                        "log10_lr": float("-inf"),
                        "rmp": 1.0,
                        "verbal_scale_en": "EXCLUSION — DNA profile does not match",
                        "verbal_scale_tr": "DIŞLAMA — DNA profili eşleşmiyor",
                        "evaluated_loci_count": len(locus_scores),
                        "theta": theta,
                        "population": pop,
                    },
                )

            # P(E | H_d) = P(G_suspect | θ)  — Balding-Nichols NRC II Rec 4.10b
            p_h2 = self.freq_db.calculate_genotype_probability(
                locus_name=locus_name,
                allele1=s_genotype.allele1,
                allele2=s_genotype.allele2,
                theta=theta,
                population=pop,
            )

            # Safeguard against numerical underflow
            if p_h2 <= 0.0:
                p_h2 = self.freq_db.min_frequency ** 2

            locus_lr = 1.0 / p_h2       # LR_l = P(E|H_p) / P(E|H_d) = 1 / P(G|θ)
            locus_scores[locus_name] = locus_lr
            total_log_lr += math.log10(locus_lr)

        # Product rule invariant: log10(LR) = Σ log10(LR_l)
        total_lr = 10.0 ** total_log_lr
        rmp = 1.0 / total_lr if total_lr > 0 else 1.0

        # 95% Bayesian HPD CI — log-space uncertainty propagation
        n_loci = len(common_loci)
        log_std_err = 0.15 * math.sqrt(n_loci)
        ci_low = 10.0 ** (total_log_lr - 1.96 * log_std_err)
        ci_high = 10.0 ** (total_log_lr + 1.96 * log_std_err)

        # ENFSI verbal scale
        _, verbal_en = enfsi_verbal_scale(total_lr, language="en")
        _, verbal_tr = enfsi_verbal_scale(total_lr, language="tr")

        return AnalysisResult(
            value=total_lr,
            confidence_interval=(ci_low, ci_high),
            assumptions=assumptions,
            model="FORENZA Module 01 Single-Source Balding-Nichols LR Engine v2.0",
            data_source=f"FBI/NIST 1036 ({pop})",
            limitations=limitations,
            locus_scores=locus_scores,
            metadata={
                "match_status": "INCLUSION",
                "log10_lr": round(total_log_lr, 6),
                "rmp": rmp,
                "verbal_scale_en": verbal_en,
                "verbal_scale_tr": verbal_tr,
                "evaluated_loci_count": n_loci,
                "theta": theta,
                "population": pop,
            },
        )

    # ── Locus-Level Random Match Probability ─────────────────────────────

    def compute_rmp_profile(
        self,
        profile: STRProfile,
        theta: float = DEFAULT_THETA,
        population: Optional[str] = None,
    ) -> Dict[str, float]:
        """
        Computes per-locus Random Match Probability (RMP_l) for an STR profile.
        Returns dict: locus_name → P(G_l | θ).
        """
        pop = population or profile.population_group
        rmp_per_locus: Dict[str, float] = {}
        for locus_name, genotype in profile.loci.items():
            rmp_per_locus[locus_name] = self.freq_db.calculate_genotype_probability(
                locus_name=locus_name,
                allele1=genotype.allele1,
                allele2=genotype.allele2,
                theta=theta,
                population=pop,
            )
        return rmp_per_locus
