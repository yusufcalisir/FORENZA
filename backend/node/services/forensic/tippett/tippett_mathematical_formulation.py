"""
FORENZA Forensic Evidence Operating System
Pillar 1 — Module 1.5: Tippett Plot ROC Calibration & Misleading Evidence Lab
Sub-Item 1.5.1: Mathematical Formulation

Derives exclusively and verbatim from:
  - Pillar 1 Research Specification (research/pillar_1_probabilistic_genotyping_research.md §5, §6, Artifact D)
  - ENFSI (2017) Guiding Principles for Evaluative Reporting in Forensic Science
  - SWGDAM (2020) Guidelines for Autosomal STR Probabilistic Genotyping Validation
  - Brümmer N, du Preez J (2006) Application-independent evaluation of speaker detection. CSL.
  - Ramos D, Gonzalez-Rodriguez J (2013) Reliable calculation of Cllr. FSI.
  - Royall R (1997) Statistical Evidence: A Likelihood Paradigm. Chapman & Hall.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Sequence, Any

import numpy as np

# ===========================================================================
# 1. Exact Biocomputational Constants (Pillar 1 Research §5)
# ===========================================================================

LOG10_LR_MIN: float = -300.0
LOG10_LR_MAX: float = 300.0

CLLR_TARGET_EXCELLENT: float = 0.05    # < 5% — Excellent forensic calibration
CLLR_TARGET_ACCEPTABLE: float = 0.20   # < 20% — Acceptable for casework reporting
MIN_ECCDF_SAMPLES: int = 10            # Minimum sample size for reliable empirical CDF
ROYALL_MISLEADING_BOUND_EXPONENT: float = 6.0  # log10(LR) = 6.0 threshold (LR = 10^6)


# ===========================================================================
# 2. Result Data Structures
# ===========================================================================

@dataclass(frozen=True)
class TippettPoint:
    """Single point on a Tippett calibration curve (ECCDF)."""
    threshold: float          # log10(LR) threshold x
    hp_exceedance: float      # P(log10(LR) >= x | Hp)  — prosecution curve
    hd_exceedance: float      # P(log10(LR) >= x | Hd)  — defense curve


@dataclass(frozen=True)
class TippettCurveResult:
    """Full Tippett calibration curve evaluation."""
    n_hp: int
    n_hd: int
    grid_points: Tuple[TippettPoint, ...]
    min_threshold: float
    max_threshold: float
    # Separation and diagnostic rates at neutral decision boundary (x = 0.0)
    fpr_at_zero: float            # FPR = P(log10(LR) > 0 | Hd)
    fnr_at_zero: float            # FNR = P(log10(LR) < 0 | Hp)
    discrimination_power: float   # D_power = 1 - FPR - FNR
    is_monotonic_hp: bool         # Strict non-increasing check
    is_monotonic_hd: bool         # Strict non-increasing check


@dataclass(frozen=True)
class ROCAnalysisResult:
    """Receiver Operating Characteristic (ROC) analysis result."""
    n_hp: int
    n_hd: int
    auc: float                    # Area Under ROC Curve (Mann-Whitney U / Trapezoidal)
    thresholds: Tuple[float, ...]
    tpr_values: Tuple[float, ...] # True Positive Rate (Sensitivity)
    fpr_values: Tuple[float, ...] # False Positive Rate (1 - Specificity)
    fpr_at_neutral: float         # Rate of misleading evidence against Hd (log10 LR > 0)
    fnr_at_neutral: float         # Rate of misleading evidence against Hp (log10 LR < 0)
    separation_index: float       # AUC - 0.5 (scaled [0, 0.5])
    interpretation: str           # Forensic diagnostic assessment


@dataclass(frozen=True)
class CllrCostResult:
    """Log-Likelihood-Ratio Cost (Cllr) information-theoretic calibration score."""
    n_hp: int
    n_hd: int
    cllr_raw: float               # Raw empirical Cllr score
    cllr_min: float               # Minimum achievable Cllr after PAV isotonic calibration
    cllr_cal: float               # Calibration loss (entropy penalty) = cllr_raw - cllr_min
    discrimination_loss: float    # cllr_min
    calibration_loss: float       # cllr_cal
    calibration_grade: str        # 'EXCELLENT', 'ACCEPTABLE', 'MISCALIBRATED', 'UNINFORMATIVE'


@dataclass(frozen=True)
class HPDLowerBoundResult:
    """Conservative 95% Highest Posterior Density (HPD) / Percentile Lower Bound."""
    n_samples: int
    mean_log10_lr: float
    median_log10_lr: float
    std_log10_lr: float
    lower_bound_5pct: float       # 5th percentile (95% conservative lower bound)
    upper_bound_95pct: float      # 95th percentile
    court_admissible_lr: float    # 10^(lower_bound_5pct)
    prosecutor_shield_active: bool


# ===========================================================================
# 3. Core Mathematical Formulation Class
# ===========================================================================

class TippettMathematicalFormulation:
    """
    Core mathematical engine for Tippett Plot ROC Calibration, Misleading Evidence,
    Log-Likelihood-Ratio Cost (Cllr), and 95% HPD Lower Bound.
    """

    # ── 3.1 Tippett Calibration Curves (ECCDF) ────────────────────────────

    @staticmethod
    def compute_tippett_curve(
        hp_log10_lrs: Sequence[float],
        hd_log10_lrs: Sequence[float],
        n_points: int = 100,
        min_threshold: Optional[float] = None,
        max_threshold: Optional[float] = None,
    ) -> TippettCurveResult:
        """
        Compute Empirical Complementary Cumulative Distribution Functions (ECCDF):
          Tippett_{H_p}(x) = P(log10(LR) >= x | H_p)
          Tippett_{H_d}(x) = P(log10(LR) >= x | H_d)

        Enforces strict non-increasing monotonicity invariant:
          x_1 < x_2 ==> Tippett(x_1) >= Tippett(x_2)
        """
        if len(hp_log10_lrs) < MIN_ECCDF_SAMPLES or len(hd_log10_lrs) < MIN_ECCDF_SAMPLES:
            raise ValueError(
                f"Insufficient samples: N_Hp={len(hp_log10_lrs)}, N_Hd={len(hd_log10_lrs)} "
                f"(minimum required is {MIN_ECCDF_SAMPLES})"
            )

        hp_arr = np.array(hp_log10_lrs, dtype=np.float64)
        hd_arr = np.array(hd_log10_lrs, dtype=np.float64)

        # Clamping to avoid numerical extremes
        hp_arr = np.clip(hp_arr, LOG10_LR_MIN, LOG10_LR_MAX)
        hd_arr = np.clip(hd_arr, LOG10_LR_MIN, LOG10_LR_MAX)

        all_lrs = np.concatenate([hp_arr, hd_arr])
        min_val = min_threshold if min_threshold is not None else float(np.min(all_lrs))
        max_val = max_threshold if max_threshold is not None else float(np.max(all_lrs))

        if min_val >= max_val:
            min_val -= 1.0
            max_val += 1.0

        grid = np.linspace(min_val, max_val, n_points)
        points: List[TippettPoint] = []

        n_hp = len(hp_arr)
        n_hd = len(hd_arr)

        for x in grid:
            # P(log10(LR) >= x | Hp)
            hp_exc = float(np.sum(hp_arr >= x)) / n_hp
            # P(log10(LR) >= x | Hd)
            hd_exc = float(np.sum(hd_arr >= x)) / n_hd
            points.append(
                TippettPoint(
                    threshold=round(float(x), 4),
                    hp_exceedance=round(hp_exc, 6),
                    hd_exceedance=round(hd_exc, 6),
                )
            )

        # Check monotonicity
        is_mono_hp = all(
            points[i].hp_exceedance >= points[i + 1].hp_exceedance
            for i in range(len(points) - 1)
        )
        is_mono_hd = all(
            points[i].hd_exceedance >= points[i + 1].hd_exceedance
            for i in range(len(points) - 1)
        )

        # Error rates at neutral decision threshold x = 0.0 (LR = 1.0)
        fpr_at_zero = float(np.sum(hd_arr > 0.0)) / n_hd
        fnr_at_zero = float(np.sum(hp_arr < 0.0)) / n_hp
        d_power = max(0.0, min(1.0, 1.0 - fpr_at_zero - fnr_at_zero))

        return TippettCurveResult(
            n_hp=n_hp,
            n_hd=n_hd,
            grid_points=tuple(points),
            min_threshold=round(min_val, 4),
            max_threshold=round(max_val, 4),
            fpr_at_zero=round(fpr_at_zero, 6),
            fnr_at_zero=round(fnr_at_zero, 6),
            discrimination_power=round(d_power, 6),
            is_monotonic_hp=is_mono_hp,
            is_monotonic_hd=is_mono_hd,
        )

    # ── 3.2 Non-Parametric ROC Analysis & Mann-Whitney U AUC ─────────────

    @staticmethod
    def compute_roc_analysis(
        hp_log10_lrs: Sequence[float],
        hd_log10_lrs: Sequence[float],
        n_thresholds: int = 100,
    ) -> ROCAnalysisResult:
        """
        Compute Receiver Operating Characteristic (ROC) curve and Area Under Curve (AUC).

        Exact Mann-Whitney U formulation:
          AUC = (1 / (N_Hp * N_Hd)) * SUM SUM [ I(Hp_i > Hd_j) + 0.5 * I(Hp_i == Hd_j) ]
        """
        if len(hp_log10_lrs) < MIN_ECCDF_SAMPLES or len(hd_log10_lrs) < MIN_ECCDF_SAMPLES:
            raise ValueError("Insufficient samples for ROC analysis.")

        hp_arr = np.array(hp_log10_lrs, dtype=np.float64)
        hd_arr = np.array(hd_log10_lrs, dtype=np.float64)

        n_hp = len(hp_arr)
        n_hd = len(hd_arr)

        # Exact Mann-Whitney U calculation for AUC
        # Vectorized pair comparison: hp[:, None] > hd[None, :]
        greater = np.sum(hp_arr[:, None] > hd_arr[None, :])
        equal = np.sum(hp_arr[:, None] == hd_arr[None, :])
        auc = float(greater + 0.5 * equal) / (n_hp * n_hd)
        auc = max(0.0, min(1.0, auc))

        # Build ROC curve points across sorted threshold continuum
        all_thresholds = np.linspace(
            float(min(np.min(hp_arr), np.min(hd_arr))),
            float(max(np.max(hp_arr), np.max(hd_arr))),
            n_thresholds,
        )

        tpr_list: List[float] = []
        fpr_list: List[float] = []

        for tau in all_thresholds:
            tpr = float(np.sum(hp_arr >= tau)) / n_hp
            fpr = float(np.sum(hd_arr >= tau)) / n_hd
            tpr_list.append(round(tpr, 6))
            fpr_list.append(round(fpr, 6))

        # Rates at neutral decision threshold tau = 0.0
        fpr_neutral = float(np.sum(hd_arr > 0.0)) / n_hd
        fnr_neutral = float(np.sum(hp_arr < 0.0)) / n_hp

        # Qualitative interpretation
        if auc >= 0.999:
            interpretation = "Perfect Forensic Discrimination (AUC >= 0.999)"
        elif auc >= 0.950:
            interpretation = "High Forensic Discrimination (0.950 <= AUC < 0.999)"
        elif auc >= 0.850:
            interpretation = "Moderate Forensic Discrimination (0.850 <= AUC < 0.950)"
        else:
            interpretation = "Weak / Compromised Discrimination (AUC < 0.850)"

        return ROCAnalysisResult(
            n_hp=n_hp,
            n_hd=n_hd,
            auc=round(auc, 6),
            thresholds=tuple(round(float(t), 4) for t in all_thresholds),
            tpr_values=tuple(tpr_list),
            fpr_values=tuple(fpr_list),
            fpr_at_neutral=round(fpr_neutral, 6),
            fnr_at_neutral=round(fnr_neutral, 6),
            separation_index=round(max(0.0, auc - 0.5), 6),
            interpretation=interpretation,
        )

    # ── 3.3 Log-Likelihood-Ratio Cost (Cllr) & PAV Calibration ────────────

    @staticmethod
    def compute_cllr_cost(
        hp_log10_lrs: Sequence[float],
        hd_log10_lrs: Sequence[float],
    ) -> CllrCostResult:
        """
        Compute Log-Likelihood-Ratio Cost (Cllr) information-theoretic calibration metric.

        Formula (Brümmer & du Preez 2006, Ramos & Gonzalez-Rodriguez 2013):
          Cllr = (1 / (2 * N_Hp)) * SUM log2(1 + 10^(-log10_LR_i))
               + (1 / (2 * N_Hd)) * SUM log2(1 + 10^(+log10_LR_j))

        Decomposes Cllr into Cllr_min (discrimination loss via PAV) and Cllr_cal (calibration loss).
        """
        if len(hp_log10_lrs) < MIN_ECCDF_SAMPLES or len(hd_log10_lrs) < MIN_ECCDF_SAMPLES:
            raise ValueError("Insufficient samples for Cllr computation.")

        hp_arr = np.array(hp_log10_lrs, dtype=np.float64)
        hd_arr = np.array(hd_log10_lrs, dtype=np.float64)

        n_hp = len(hp_arr)
        n_hd = len(hd_arr)

        # Raw Cllr calculation
        # log2(1 + 10^(-x)) = log2(1 + e^(-x * ln(10))) = ln(1 + e^(-x * ln10)) / ln(2)
        # Using np.log1p and np.exp for numerical stability
        ln10 = math.log(10.0)
        ln2 = math.log(2.0)

        # For Hp: log2(1 + 10^(-x))
        hp_penalty = np.zeros_like(hp_arr)
        for idx, val in enumerate(hp_arr):
            arg = -val * ln10
            if arg > 700:
                hp_penalty[idx] = -val * math.log2(10.0)
            elif arg < -50:
                hp_penalty[idx] = math.exp(arg) / ln2
            else:
                hp_penalty[idx] = math.log1p(math.exp(arg)) / ln2

        # For Hd: log2(1 + 10^(+x))
        hd_penalty = np.zeros_like(hd_arr)
        for idx, val in enumerate(hd_arr):
            arg = val * ln10
            if arg > 700:
                hd_penalty[idx] = val * math.log2(10.0)
            elif arg < -50:
                hd_penalty[idx] = math.exp(arg) / ln2
            else:
                hd_penalty[idx] = math.log1p(math.exp(arg)) / ln2

        cllr_raw = float(0.5 * (np.mean(hp_penalty) + np.mean(hd_penalty)))

        # Pool Adjacent Violators (PAV) Isotonic Regression for Cllr_min
        cllr_min = TippettMathematicalFormulation._compute_cllr_min_pav(hp_arr, hd_arr)
        cllr_cal = max(0.0, cllr_raw - cllr_min)

        # Grading
        if cllr_raw < CLLR_TARGET_EXCELLENT:
            grade = "EXCELLENT"
        elif cllr_raw < CLLR_TARGET_ACCEPTABLE:
            grade = "ACCEPTABLE"
        elif cllr_raw < 1.00:
            grade = "MISCALIBRATED"
        else:
            grade = "UNINFORMATIVE"

        return CllrCostResult(
            n_hp=n_hp,
            n_hd=n_hd,
            cllr_raw=round(cllr_raw, 6),
            cllr_min=round(cllr_min, 6),
            cllr_cal=round(cllr_cal, 6),
            discrimination_loss=round(cllr_min, 6),
            calibration_loss=round(cllr_cal, 6),
            calibration_grade=grade,
        )

    @staticmethod
    def _compute_cllr_min_pav(hp_lrs: np.ndarray, hd_lrs: np.ndarray) -> float:
        """
        Computes minimum Cllr (Cllr_min) via Pool Adjacent Violators (PAV) algorithm.
        """
        n_hp = len(hp_lrs)
        n_hd = len(hd_lrs)

        scores = np.concatenate([hp_lrs, hd_lrs])
        labels = np.concatenate([np.ones(n_hp, dtype=np.float64), np.zeros(n_hd, dtype=np.float64)])

        # Sort by score ascending
        order = np.argsort(scores)
        y = labels[order].copy()
        w = np.ones_like(y)

        # PAV algorithm
        # Pool adjacent violators until monotonic non-decreasing
        i = 0
        while i < len(y) - 1:
            if y[i] > y[i + 1]:
                # Violator found: merge blocks
                total_w = w[i] + w[i + 1]
                avg_y = (y[i] * w[i] + y[i + 1] * w[i + 1]) / total_w
                y[i] = avg_y
                w[i] = total_w
                y = np.delete(y, i + 1)
                w = np.delete(w, i + 1)
                if i > 0:
                    i -= 1
            else:
                i += 1

        # Evaluate Cllr under optimal calibrated probabilities P(Hp | x)
        # Prior odds P(Hp)/P(Hd) = 1.0 (log prior odds = 0)
        # Optimal posterior log-odds = ln(p / (1 - p))
        eps = 1e-15
        cal_hp_penalties = []
        cal_hd_penalties = []

        # Map back to original elements
        # For simplicity and robust numerical stability:
        # P_optimal in [eps, 1 - eps]
        for p_val, weight in zip(y, w):
            p_clamped = max(eps, min(1.0 - eps, p_val))
            log_lr_opt = math.log10(p_clamped / (1.0 - p_clamped))
            # Fraction of true Hp in this block
            k_hp = p_val * weight
            k_hd = (1.0 - p_val) * weight

            arg_hp = -log_lr_opt * math.log(10.0)
            arg_hd = log_lr_opt * math.log(10.0)

            pen_hp = (math.log1p(math.exp(arg_hp)) / math.log(2.0)) if arg_hp < 50 else -log_lr_opt * math.log2(10.0)
            pen_hd = (math.log1p(math.exp(arg_hd)) / math.log(2.0)) if arg_hd < 50 else log_lr_opt * math.log2(10.0)

            cal_hp_penalties.append(k_hp * pen_hp)
            cal_hd_penalties.append(k_hd * pen_hd)

        cllr_min = float(0.5 * (sum(cal_hp_penalties) / n_hp + sum(cal_hd_penalties) / n_hd))
        return max(0.0, cllr_min)

    # ── 3.4 Conservative 95% HPD Lower Bound ──────────────────────────────

    @staticmethod
    def compute_95_hpd_lower_bound(
        log10_lrs: Sequence[float],
        alpha: float = 0.05,
    ) -> HPDLowerBoundResult:
        """
        Compute conservative court-admissible 5th percentile lower bound:
          LR_court = Percentile_5% ({log10(LR)^(m)})
        """
        if len(log10_lrs) == 0:
            raise ValueError("Empty sample array for HPD lower bound computation.")

        arr = np.array(log10_lrs, dtype=np.float64)
        n = len(arr)

        mean_val = float(np.mean(arr))
        median_val = float(np.median(arr))
        std_val = float(np.std(arr, ddof=1)) if n > 1 else 0.0

        pct_lower = float(np.percentile(arr, alpha * 100.0))
        pct_upper = float(np.percentile(arr, (1.0 - alpha) * 100.0))

        clamped_lower = max(LOG10_LR_MIN, min(LOG10_LR_MAX, pct_lower))
        court_lr = math.pow(10.0, clamped_lower)

        return HPDLowerBoundResult(
            n_samples=n,
            mean_log10_lr=round(mean_val, 4),
            median_log10_lr=round(median_val, 4),
            std_log10_lr=round(std_val, 4),
            lower_bound_5pct=round(pct_lower, 4),
            upper_bound_95pct=round(pct_upper, 4),
            court_admissible_lr=court_lr,
            prosecutor_shield_active=True,
        )

    # ── 3.5 Royall Misleading Evidence Rate Evaluator ─────────────────────

    @staticmethod
    def evaluate_misleading_evidence_rate(
        hd_log10_lrs: Sequence[float],
        threshold_log10: float = ROYALL_MISLEADING_BOUND_EXPONENT,
    ) -> Dict[str, Any]:
        """
        Verify Royall's Inequality for rate of misleading evidence under Hd:
          P(LR >= 10^k | Hd) <= 10^(-k)
        """
        if len(hd_log10_lrs) == 0:
            raise ValueError("Empty non-donor array.")

        hd_arr = np.array(hd_log10_lrs, dtype=np.float64)
        n = len(hd_arr)

        count_exceed = int(np.sum(hd_arr >= threshold_log10))
        empirical_rate = float(count_exceed) / n
        theoretical_bound = math.pow(10.0, -threshold_log10)
        bound_satisfied = empirical_rate <= (theoretical_bound + 1e-9)

        return {
            "n_non_donors": n,
            "threshold_log10": threshold_log10,
            "threshold_lr_point": math.pow(10.0, threshold_log10),
            "count_exceeding": count_exceed,
            "empirical_rate": round(empirical_rate, 8),
            "theoretical_royall_bound": theoretical_bound,
            "bound_satisfied": bound_satisfied,
        }
