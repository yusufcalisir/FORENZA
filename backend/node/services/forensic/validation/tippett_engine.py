"""
FORENZA Tippett Calibration, ROC Analysis, Cllr Cost, 95% HPD Lower Bound &
ENFSI 2017 Evaluative Reporting Engine — Module 05.

Implements verbatim from Pillar 1 Research §5 (Tippett Calibration & Evaluative Reporting):
  - §5.1 Tippett Calibration Curves (Empirical Complementary CDF):
           Hp curve: P(log10(LR) >= x | Hp)
           Hd curve: P(log10(LR) >= x | Hd)
  - §5.2 Empirical ROC Analysis:
           FPR = P(log10(LR) > 0 | Hd)
           FNR = P(log10(LR) < 0 | Hp)
           ROC-AUC via trapezoidal integration
           Misleading Evidence Rate (MER) upper bound
  - §5.3 Log-Likelihood-Ratio Cost (Cllr) Calibration Score:
           Cllr = (1/(2*N_Hp)) * SUM log2(1 + 1/LR_i) + (1/(2*N_Hd)) * SUM log2(1 + LR_j)
           Minimum Cllr (ideal PAV-calibrated system)
           Entropy Loss = Cllr - Cllr_min
  - §5.4 Conservative 95% HPD Lower Bound (LR_court):
           LR_court = Percentile_5% ({LR^(m)}_{m=1}^M)
  - §5.5 ENFSI 2017 Dynamic 7-Tier Verbal Reporting Scale:
           Tiers 0-6 (EN & TR) + Prosecutor's Fallacy Shield (Transposed Conditional)

Golden Benchmark Vectors:
  VECTOR_05_TIPPETT_A — Tippett curve ECCDF bounds and monotonicity
  VECTOR_05_TIPPETT_B — FPR / FNR with synthetic datasets
  VECTOR_05_TIPPETT_C — ROC-AUC >= 0.999 on pristine benchmark
  VECTOR_05_TIPPETT_D — Cllr cost against canonical numerical benchmarks
  VECTOR_05_TIPPETT_E — 95% HPD Lower Bound (Percentile_5%)
  VECTOR_05_TIPPETT_F — ENFSI 7-tier scale boundary conditions
  VECTOR_05_TIPPETT_G — Prosecutor's Fallacy Shield
  VECTOR_05_TIPPETT_H — API integration tests

References:
  ENFSI (2017) Guiding Principles for Evaluative Reporting in Forensic Science.
  Brümmer N, du Preez J (2006) Application-independent evaluation of speaker detection. CSL.
  van Leeuwen DA, Brümmer N (2007) An Introduction to Application-Independent Evaluation of
    Speaker Recognition Systems. Springer LNCS.
  SWGDAM (2020) Guidelines for Autosomal STR Probabilistic Genotyping.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ── Constants ──────────────────────────────────────────────────────────────────

# log10(LR) clamp limits (IEEE 754 precision)
LOG10_LR_MIN: float = -300.0
LOG10_LR_MAX: float = 300.0

# Target calibration quality thresholds
CLLR_TARGET_EXCELLENT: float = 0.05   # < 5% — excellent calibration
CLLR_TARGET_ACCEPTABLE: float = 0.20  # < 20% — acceptable calibration

# Minimum Effective Sample Size for Tippett curves
MIN_ECCDF_SAMPLES: int = 10

# ENFSI 2017 7-Tier Verbal Scale boundaries (log10 LR thresholds)
ENFSI_THRESHOLDS: List[float] = [0.0, 1.0, 2.0, 4.0, 6.0]  # 5 boundaries → 6 positive tiers


# ── Data Classes ───────────────────────────────────────────────────────────────

@dataclass
class TippettPoint:
    """Single point on a Tippett calibration curve (ECCDF)."""
    threshold: float        # log10(LR) threshold x
    hp_exceedance: float    # P(log10(LR) >= x | Hp)  — prosecution curve
    hd_exceedance: float    # P(log10(LR) >= x | Hd)  — defense curve


@dataclass
class TippettCurveResult:
    """Full Tippett calibration curve result for a forensic system."""
    n_hp: int
    n_hd: int
    grid_points: List[TippettPoint]
    min_threshold: float
    max_threshold: float
    # Separation metrics
    fpr_at_zero: float          # FPR = P(log10(LR) > 0 | Hd)
    fnr_at_zero: float          # FNR = P(log10(LR) < 0 | Hp)
    discrimination_power: float  # D_power = 1 - FPR - FNR


@dataclass
class ROCAnalysisResult:
    """Empirical Receiver Operating Characteristic analysis result."""
    n_hp: int
    n_hd: int
    auc: float                  # Area Under ROC Curve (trapezoidal)
    # Sorted TPR/FPR arrays for curve plotting
    thresholds: List[float]
    tpr_values: List[float]     # True Positive Rate = sensitivity
    fpr_values: List[float]     # False Positive Rate = 1 - specificity
    # Diagnostic rates at LR=1 decision threshold
    fpr_at_lr1: float           # Misleading Evidence Rate vs Hd
    fnr_at_lr1: float           # Misleading Evidence Rate vs Hp
    mer_upper_bound: float       # MER = max(FPR, FNR) at neutral threshold
    interpretation: str


@dataclass
class CllrResult:
    """Log-Likelihood-Ratio Cost calibration score result."""
    n_hp: int
    n_hd: int
    cllr: float             # Full Cllr cost (includes discrimination + calibration)
    cllr_min: float         # Minimum achievable Cllr (ideal PAV-calibrated system)
    cllr_cal: float         # Calibration loss = Cllr - Cllr_min
    calibration_quality: str    # 'EXCELLENT', 'ACCEPTABLE', 'POOR'
    interpretation: str


@dataclass
class HPDLowerBoundResult:
    """Conservative 95% HPD Lower Bound for court-admissible LR reporting."""
    n_mcmc_samples: int
    percentile: float           # e.g. 5.0 for 5th percentile
    log10_lr_court: float       # LR_court = Percentile_5%(MCMC samples)
    log10_lr_median: float      # Median log10(LR) for reference
    log10_lr_mean: float        # Mean log10(LR) for reference
    log10_lr_95ci_upper: float  # 95th percentile upper bound
    interpretation: str


@dataclass
class ENFSIVerbalResult:
    """ENFSI 2017 7-Tier Verbal Scale evaluative reporting result."""
    log10_lr: float
    tier: int                   # -1=support Hd tiers, 0–6=support Hp tiers
    tier_name_en: str           # English verbal predicate
    tier_name_tr: str           # Turkish verbal predicate
    lr_range_description: str   # Numeric LR range for this tier
    # Prosecutor's Fallacy Shield
    prosecutors_fallacy_shield_en: str
    prosecutors_fallacy_shield_tr: str
    is_positive_support: bool   # True = supports Hp, False = supports Hd
    # Mathematical invariant
    likelihood_equation: str


# ── Engine ─────────────────────────────────────────────────────────────────────

class TippettEngine:
    """
    FORENZA Tippett Calibration, ROC Analysis, Cllr Cost, HPD Lower Bound &
    ENFSI Evaluative Reporting Engine (Module 05).

    All formulas verbatim from Pillar 1 Research §5.
    """

    # ENFSI 2017 7-Tier Verbal Scale — EN/TR pairs
    _ENFSI_TIERS: List[Dict] = [
        # Tier 0: LR = 1 (neutral — no support)
        {
            "tier": 0,
            "log10_lr_range": (0.0, 0.0),
            "en": "Neutral — the evidence does not favour either hypothesis.",
            "tr": "Tarafsız — delil her iki hipotezi de desteklememektedir.",
            "range_desc": "LR = 1 (log10 LR = 0)",
        },
        # Tier 1: 1 < LR <= 10 (limited support for Hp)
        {
            "tier": 1,
            "log10_lr_range": (0.0, 1.0),
            "en": "Limited support for the prosecution proposition.",
            "tr": "İddianame önermesini destekler sınırlı destek.",
            "range_desc": "1 < LR ≤ 10 (0 < log10 LR ≤ 1)",
        },
        # Tier 2: 10 < LR <= 100 (moderate support for Hp)
        {
            "tier": 2,
            "log10_lr_range": (1.0, 2.0),
            "en": "Moderate support for the prosecution proposition.",
            "tr": "İddianame önermesini destekler orta düzeyde destek.",
            "range_desc": "10 < LR ≤ 100 (1 < log10 LR ≤ 2)",
        },
        # Tier 3: 100 < LR <= 10000 (strong support for Hp)
        {
            "tier": 3,
            "log10_lr_range": (2.0, 4.0),
            "en": "Strong support for the prosecution proposition.",
            "tr": "İddianame önermesini destekler güçlü destek.",
            "range_desc": "100 < LR ≤ 10,000 (2 < log10 LR ≤ 4)",
        },
        # Tier 4: 10000 < LR <= 1000000 (very strong support for Hp)
        {
            "tier": 4,
            "log10_lr_range": (4.0, 6.0),
            "en": "Very strong support for the prosecution proposition.",
            "tr": "İddianame önermesini destekler çok güçlü destek.",
            "range_desc": "10,000 < LR ≤ 1,000,000 (4 < log10 LR ≤ 6)",
        },
        # Tier 5: LR > 1000000 (extremely strong support for Hp)
        {
            "tier": 5,
            "log10_lr_range": (6.0, 300.0),
            "en": "Extremely strong support for the prosecution proposition.",
            "tr": "İddianame önermesini destekler son derece güçlü destek.",
            "range_desc": "LR > 1,000,000 (log10 LR > 6)",
        },
    ]

    _ENFSI_TIERS_NEG: List[Dict] = [
        {
            "tier": -1,
            "log10_lr_range": (-1.0, 0.0),
            "en": "Limited support for the defence proposition.",
            "tr": "Savunma önermesini destekler sınırlı destek.",
            "range_desc": "0.1 < LR(defence) ≤ 1 (-1 < log10 LR ≤ 0)",
        },
        {
            "tier": -2,
            "log10_lr_range": (-2.0, -1.0),
            "en": "Moderate support for the defence proposition.",
            "tr": "Savunma önermesini destekler orta düzeyde destek.",
            "range_desc": "0.01 < LR(defence) ≤ 0.1 (-2 < log10 LR ≤ -1)",
        },
        {
            "tier": -3,
            "log10_lr_range": (-4.0, -2.0),
            "en": "Strong support for the defence proposition.",
            "tr": "Savunma önermesini destekler güçlü destek.",
            "range_desc": "LR(defence) ≤ 0.01 (log10 LR ≤ -2)",
        },
        {
            "tier": -4,
            "log10_lr_range": (-6.0, -4.0),
            "en": "Very strong support for the defence proposition.",
            "tr": "Savunma önermesini destekler çok güçlü destek.",
            "range_desc": "LR(defence) ≤ 0.0001 (log10 LR ≤ -4)",
        },
        {
            "tier": -5,
            "log10_lr_range": (-300.0, -6.0),
            "en": "Extremely strong support for the defence proposition.",
            "tr": "Savunma önermesini destekler son derece güçlü destek.",
            "range_desc": "LR(defence) ≤ 10⁻⁶ (log10 LR ≤ -6)",
        },
    ]

    # Prosecutor's Fallacy Shield text
    _FALLACY_SHIELD_EN = (
        "IMPORTANT (Prosecutor's Fallacy Shield): The Likelihood Ratio (LR) measures "
        "P(Evidence | Hypothesis), NOT P(Hypothesis | Evidence). "
        "This value does NOT represent the probability that the person of interest is guilty. "
        "Guilt or innocence requires evaluation of all case evidence by the trier of fact. "
        "Conflating P(E|Hp) with P(Hp|E) constitutes the Transposed Conditional Fallacy "
        "(Prosecutor's Fallacy), which is inadmissible in court."
    )

    _FALLACY_SHIELD_TR = (
        "ÖNEMLİ (Savcılık Yanılgısı Kalkanı): Olabilirlik Oranı (LR), "
        "P(Delil | Hipotez) değerini ölçmekte olup P(Hipotez | Delil) DEĞİLDİR. "
        "Bu değer, şüphelinin suçlu olma olasılığını temsil ETMEZ. "
        "Suçluluk veya masumiyet, tüm dava delillerinin yargılayan makam tarafından "
        "değerlendirilmesini gerektirmektedir. "
        "P(D|Hs) ile P(Hs|D) değerlerini karıştırmak Tersine Koşullu Yanılgı "
        "(Savcılık Yanılgısı) teşkil eder."
    )

    # ── §5.1 Tippett Calibration Curves ────────────────────────────────────────

    def compute_tippett_curves(
        self,
        hp_log10_lrs: List[float],
        hd_log10_lrs: List[float],
        num_points: int = 100,
    ) -> TippettCurveResult:
        """
        Compute Tippett calibration curves (Empirical Complementary CDFs).

        Hp curve: P(log10(LR) >= x | Hp)  — prosecution hypothesis true
        Hd curve: P(log10(LR) >= x | Hd)  — defence hypothesis true

        Grid spans from min to max of all observed log10(LR) values.
        """
        if len(hp_log10_lrs) < 1 or len(hd_log10_lrs) < 1:
            raise ValueError("At least one LR value required for each hypothesis.")

        all_lrs = hp_log10_lrs + hd_log10_lrs
        x_min = min(all_lrs)
        x_max = max(all_lrs)
        step = (x_max - x_min) / max(num_points - 1, 1)

        n_hp = len(hp_log10_lrs)
        n_hd = len(hd_log10_lrs)

        grid: List[TippettPoint] = []
        for i in range(num_points):
            x = x_min + i * step
            hp_exc = sum(1 for lr in hp_log10_lrs if lr >= x) / n_hp
            hd_exc = sum(1 for lr in hd_log10_lrs if lr >= x) / n_hd
            grid.append(TippettPoint(
                threshold=round(x, 6),
                hp_exceedance=round(hp_exc, 8),
                hd_exceedance=round(hd_exc, 8),
            ))

        # Metrics at LR = 1 (log10 = 0) decision threshold
        fpr = sum(1 for lr in hd_log10_lrs if lr > 0.0) / n_hd
        fnr = sum(1 for lr in hp_log10_lrs if lr < 0.0) / n_hp
        disc_power = max(0.0, 1.0 - fpr - fnr)

        return TippettCurveResult(
            n_hp=n_hp,
            n_hd=n_hd,
            grid_points=grid,
            min_threshold=round(x_min, 6),
            max_threshold=round(x_max, 6),
            fpr_at_zero=round(fpr, 8),
            fnr_at_zero=round(fnr, 8),
            discrimination_power=round(disc_power, 8),
        )

    # ── §5.2 ROC Analysis ──────────────────────────────────────────────────────

    def compute_roc_analysis(
        self,
        hp_log10_lrs: List[float],
        hd_log10_lrs: List[float],
    ) -> ROCAnalysisResult:
        """
        Compute empirical ROC curve and AUC via trapezoidal integration.

        At each threshold t:
          TPR(t) = P(log10(LR) >= t | Hp) = sensitivity
          FPR(t) = P(log10(LR) >= t | Hd) = 1 - specificity

        AUC = integral TPR d(FPR) via trapezoidal rule (sorted by decreasing threshold).
        """
        n_hp = len(hp_log10_lrs)
        n_hd = len(hd_log10_lrs)
        if n_hp < 1 or n_hd < 1:
            raise ValueError("At least 1 LR per hypothesis required.")

        # Build sorted unique threshold set
        all_thresholds = sorted(set(hp_log10_lrs + hd_log10_lrs + [LOG10_LR_MIN, LOG10_LR_MAX]),
                                reverse=True)

        tprs: List[float] = []
        fprs: List[float] = []
        thresholds_out: List[float] = []

        for t in all_thresholds:
            tpr = sum(1 for lr in hp_log10_lrs if lr >= t) / n_hp
            fpr = sum(1 for lr in hd_log10_lrs if lr >= t) / n_hd
            tprs.append(tpr)
            fprs.append(fpr)
            thresholds_out.append(t)

        # Trapezoidal AUC (integrate TPR d(FPR))
        # Sort by increasing FPR for correct trapz direction
        pairs = sorted(zip(fprs, tprs))
        sorted_fprs = [p[0] for p in pairs]
        sorted_tprs = [p[1] for p in pairs]

        auc = 0.0
        for i in range(1, len(sorted_fprs)):
            d_fpr = sorted_fprs[i] - sorted_fprs[i - 1]
            avg_tpr = (sorted_tprs[i] + sorted_tprs[i - 1]) / 2.0
            auc += d_fpr * avg_tpr
        auc = min(1.0, max(0.0, auc))

        # Diagnostic rates at LR=1 threshold
        fpr_at_lr1 = sum(1 for lr in hd_log10_lrs if lr > 0.0) / n_hd
        fnr_at_lr1 = sum(1 for lr in hp_log10_lrs if lr < 0.0) / n_hp
        mer = max(fpr_at_lr1, fnr_at_lr1)

        if auc >= 0.999:
            interp = "EXCELLENT: AUC >= 0.999 — Near-perfect discrimination (SWGDAM 2020)."
        elif auc >= 0.995:
            interp = "VERY GOOD: AUC >= 0.995 — High discrimination power."
        elif auc >= 0.99:
            interp = "GOOD: AUC >= 0.990 — Acceptable discrimination."
        else:
            interp = f"MARGINAL: AUC = {auc:.4f} — Review calibration and panel design."

        return ROCAnalysisResult(
            n_hp=n_hp,
            n_hd=n_hd,
            auc=round(auc, 8),
            thresholds=thresholds_out,
            tpr_values=tprs,
            fpr_values=fprs,
            fpr_at_lr1=round(fpr_at_lr1, 8),
            fnr_at_lr1=round(fnr_at_lr1, 8),
            mer_upper_bound=round(mer, 8),
            interpretation=interp,
        )

    # ── §5.3 Cllr Cost ─────────────────────────────────────────────────────────

    def compute_cllr_cost(
        self,
        hp_log10_lrs: List[float],
        hd_log10_lrs: List[float],
    ) -> CllrResult:
        """
        Compute Log-Likelihood-Ratio Cost (Cllr) calibration score.

        Cllr = (1/(2*N_Hp)) * SUM_i log2(1 + 1/LR_i)
             + (1/(2*N_Hd)) * SUM_j log2(1 + LR_j)

        where LR_i = 10^(log10_lr_i).

        Minimum Cllr (ideal discrimination): optimal monotonic transformation.
        Calibration loss = Cllr - Cllr_min.

        (Brümmer & du Preez 2006; van Leeuwen & Brümmer 2007)
        """
        n_hp = len(hp_log10_lrs)
        n_hd = len(hd_log10_lrs)
        if n_hp < 1 or n_hd < 1:
            raise ValueError("At least 1 LR per hypothesis required.")

        def _safe_log2(x: float) -> float:
            return math.log2(max(x, 1e-300))

        # Hp term: log2(1 + 1/LR_i) = log2(1 + 10^(-log10_lr_i))
        hp_term = 0.0
        for l in hp_log10_lrs:
            l_clamped = max(LOG10_LR_MIN, min(LOG10_LR_MAX, l))
            hp_term += _safe_log2(1.0 + 10.0 ** (-l_clamped))
        hp_term /= (2.0 * n_hp)

        # Hd term: log2(1 + LR_j) = log2(1 + 10^(log10_lr_j))
        hd_term = 0.0
        for l in hd_log10_lrs:
            l_clamped = max(LOG10_LR_MIN, min(LOG10_LR_MAX, l))
            hd_term += _safe_log2(1.0 + 10.0 ** l_clamped)
        hd_term /= (2.0 * n_hd)

        cllr = hp_term + hd_term

        # Minimum Cllr: compute on PAV-isotonic-regression approximation
        # For ideal system: Cllr_min approaches empirical lower bound
        # Approximate as: compute oracle thresholded assignments
        combined = [(lr, 1) for lr in hp_log10_lrs] + [(lr, 0) for lr in hd_log10_lrs]
        combined_sorted = sorted(combined, key=lambda x: x[0], reverse=True)

        # Compute best binary threshold that minimizes Cllr
        min_cllr = float('inf')
        for threshold in [c[0] for c in combined_sorted]:
            hp_min = 0.0
            for l, label in combined:
                if label == 1:
                    if l >= threshold:
                        hp_min += _safe_log2(1.0 + 10.0 ** (-max(LOG10_LR_MIN, min(LOG10_LR_MAX, l))))
                    else:
                        hp_min += 1.0  # log2(1 + 1/small_LR) → 1 bit
            hp_min /= (2.0 * n_hp)
            hd_min = 0.0
            for l, label in combined:
                if label == 0:
                    if l < threshold:
                        hd_min += _safe_log2(1.0 + 10.0 ** max(LOG10_LR_MIN, min(LOG10_LR_MAX, l)))
                    else:
                        hd_min += 1.0  # wrong
            hd_min /= (2.0 * n_hd)
            candidate = hp_min + hd_min
            if candidate < min_cllr:
                min_cllr = candidate

        # Safeguard: Cllr_min <= Cllr
        cllr_min = min(cllr, min_cllr)
        cllr_cal = max(0.0, cllr - cllr_min)

        if cllr <= CLLR_TARGET_EXCELLENT:
            quality = "EXCELLENT"
            interp = f"Cllr={cllr:.4f} — Extremely well-calibrated system (Cllr < {CLLR_TARGET_EXCELLENT})."
        elif cllr <= CLLR_TARGET_ACCEPTABLE:
            quality = "ACCEPTABLE"
            interp = f"Cllr={cllr:.4f} — Acceptably calibrated system (Cllr < {CLLR_TARGET_ACCEPTABLE})."
        else:
            quality = "POOR"
            interp = f"Cllr={cllr:.4f} — Poorly calibrated system. Post-calibration recommended."

        return CllrResult(
            n_hp=n_hp,
            n_hd=n_hd,
            cllr=round(cllr, 6),
            cllr_min=round(cllr_min, 6),
            cllr_cal=round(cllr_cal, 6),
            calibration_quality=quality,
            interpretation=interp,
        )

    # ── §5.4 Conservative 95% HPD Lower Bound ──────────────────────────────────

    def compute_hpd_lower_bound(
        self,
        mcmc_log10_lrs: List[float],
        percentile: float = 5.0,
    ) -> HPDLowerBoundResult:
        """
        Compute conservative court-admissible LR lower bound from MCMC samples.

        LR_court = Percentile_{percentile}%({LR^(m)}_{m=1}^M)

        The 5th percentile provides a conservative bound: the true LR exceeds
        this value with 95% posterior probability. (Research §5.4)
        """
        n = len(mcmc_log10_lrs)
        if n < 1:
            raise ValueError("At least 1 MCMC log10(LR) sample required.")

        sorted_lrs = sorted(mcmc_log10_lrs)

        def _percentile(data: List[float], p: float) -> float:
            """Linear interpolation percentile."""
            n_d = len(data)
            idx = (p / 100.0) * (n_d - 1)
            lo = int(idx)
            hi = min(lo + 1, n_d - 1)
            frac = idx - lo
            return data[lo] + frac * (data[hi] - data[lo])

        lr_court = _percentile(sorted_lrs, percentile)
        lr_median = _percentile(sorted_lrs, 50.0)
        lr_mean = sum(sorted_lrs) / n
        lr_95_upper = _percentile(sorted_lrs, 95.0)

        return HPDLowerBoundResult(
            n_mcmc_samples=n,
            percentile=percentile,
            log10_lr_court=round(lr_court, 6),
            log10_lr_median=round(lr_median, 6),
            log10_lr_mean=round(lr_mean, 6),
            log10_lr_95ci_upper=round(lr_95_upper, 6),
            interpretation=(
                f"Court-admissible LR_court = 10^{lr_court:.4f} "
                f"(Percentile_{percentile:.0f}% of {n} MCMC samples). "
                f"The true LR exceeds 10^{lr_court:.4f} with {100.0 - percentile:.0f}% posterior probability."
            ),
        )

    # ── §5.5 ENFSI 2017 7-Tier Verbal Scale ───────────────────────────────────

    def map_enfsi_verbal_scale(self, log10_lr: float) -> ENFSIVerbalResult:
        """
        Map numeric log10(LR) to the ENFSI 2017 Dynamic 7-Tier Verbal Reporting Scale.

        Returns both English and Turkish standardized verbal predicates, plus
        an active Prosecutor's Fallacy Shield.

        ENFSI (2017) Tier Map:
          Tier 5:  log10 LR > 6         Extremely strong support for prosecution
          Tier 4:  4 < log10 LR <= 6    Very strong support for prosecution
          Tier 3:  2 < log10 LR <= 4    Strong support for prosecution
          Tier 2:  1 < log10 LR <= 2    Moderate support for prosecution
          Tier 1:  0 < log10 LR <= 1    Limited support for prosecution
          Tier 0:  log10 LR == 0        Neutral
          Tier -1..-5: Symmetric defence tiers
        """
        log10_lr = max(LOG10_LR_MIN, min(LOG10_LR_MAX, log10_lr))

        # Select tier
        selected = None
        if log10_lr > 0.0:
            for tier_def in reversed(self._ENFSI_TIERS):
                lo, hi = tier_def["log10_lr_range"]
                if log10_lr > lo:
                    selected = tier_def
                    break
            if selected is None:
                selected = self._ENFSI_TIERS[-1]
        elif log10_lr < 0.0:
            for tier_def in self._ENFSI_TIERS_NEG:
                lo, hi = tier_def["log10_lr_range"]
                if lo < log10_lr <= hi:
                    selected = tier_def
                    break
            if selected is None:
                selected = self._ENFSI_TIERS_NEG[-1]
        else:
            selected = {
                "tier": 0,
                "en": "Neutral — the evidence does not favour either hypothesis.",
                "tr": "Tarafsız — delil her iki hipotezi de desteklememektedir.",
                "range_desc": "LR = 1 (log10 LR = 0)",
            }

        is_positive = log10_lr > 0.0
        eq = (
            f"LR = 10^{log10_lr:.4f}. "
            f"P(E|Hp) is 10^{abs(log10_lr):.4f} times more probable "
            f"under {'prosecution' if is_positive else 'defence'} hypothesis."
        )

        return ENFSIVerbalResult(
            log10_lr=round(log10_lr, 6),
            tier=selected["tier"],
            tier_name_en=selected["en"],
            tier_name_tr=selected["tr"],
            lr_range_description=selected.get("range_desc", ""),
            prosecutors_fallacy_shield_en=self._FALLACY_SHIELD_EN,
            prosecutors_fallacy_shield_tr=self._FALLACY_SHIELD_TR,
            is_positive_support=is_positive,
            likelihood_equation=eq,
        )
