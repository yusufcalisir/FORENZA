"""
FORENZA Validation Metrics Engine.
Computes Accuracy, Sensitivity (TPR), Specificity (TNR), False Inclusion Rate (FIR),
False Exclusion Rate (FER), and RMSE(log10 LR) for validation reporting.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class ValidationResult:
    """Single LR evaluation outcome record."""
    pair_id: str
    pair_type: str
    log10_lr: float
    is_true_match: bool       # Ground truth: profiles from same source?
    called_match: bool        # Decision at threshold


@dataclass
class MetricsSummary:
    """Aggregated binary classification metrics for an LR decision threshold."""
    threshold_log10_lr: float
    n_true_match: int
    n_true_unrelated: int
    true_positives: int       # Match called, truly same source
    false_negatives: int      # Non-match called, truly same source (false exclusion)
    true_negatives: int       # Non-match called, truly different source
    false_positives: int      # Match called, truly different source (false inclusion)

    @property
    def sensitivity(self) -> float:
        """TPR = TP / (TP + FN)"""
        denom = self.true_positives + self.false_negatives
        return self.true_positives / denom if denom else 0.0

    @property
    def specificity(self) -> float:
        """TNR = TN / (TN + FP)"""
        denom = self.true_negatives + self.false_positives
        return self.true_negatives / denom if denom else 0.0

    @property
    def false_inclusion_rate(self) -> float:
        """FIR = FP / (FP + TN)  — proportion of unrelated pairs incorrectly included"""
        denom = self.false_positives + self.true_negatives
        return self.false_positives / denom if denom else 0.0

    @property
    def false_exclusion_rate(self) -> float:
        """FER = FN / (FN + TP)  — proportion of true-match pairs incorrectly excluded"""
        denom = self.false_negatives + self.true_positives
        return self.false_negatives / denom if denom else 0.0

    @property
    def accuracy(self) -> float:
        total = self.true_positives + self.true_negatives + self.false_positives + self.false_negatives
        return (self.true_positives + self.true_negatives) / total if total else 0.0

    def to_dict(self) -> Dict:
        return {
            "threshold_log10_lr": self.threshold_log10_lr,
            "n_true_match": self.n_true_match,
            "n_true_unrelated": self.n_true_unrelated,
            "accuracy": round(self.accuracy, 6),
            "sensitivity_tpr": round(self.sensitivity, 6),
            "specificity_tnr": round(self.specificity, 6),
            "false_inclusion_rate": round(self.false_inclusion_rate, 8),
            "false_exclusion_rate": round(self.false_exclusion_rate, 6),
            "true_positives": self.true_positives,
            "true_negatives": self.true_negatives,
            "false_positives": self.false_positives,
            "false_negatives": self.false_negatives,
        }


class MetricsEngine:
    """Computes LR-based binary classification metrics for a given decision threshold."""

    @staticmethod
    def evaluate(
        results: List[ValidationResult],
        threshold_log10_lr: float = 0.0
    ) -> MetricsSummary:
        """
        Evaluates classification performance at a given log10(LR) threshold.
        Decision: called_match = True if log10(LR) >= threshold.
        """
        tp = fp = tn = fn = 0
        n_match = sum(1 for r in results if r.is_true_match)
        n_unrelated = sum(1 for r in results if not r.is_true_match)

        for r in results:
            called = r.log10_lr >= threshold_log10_lr
            if called and r.is_true_match:
                tp += 1
            elif called and not r.is_true_match:
                fp += 1
            elif not called and r.is_true_match:
                fn += 1
            else:
                tn += 1

        return MetricsSummary(
            threshold_log10_lr=threshold_log10_lr,
            n_true_match=n_match,
            n_true_unrelated=n_unrelated,
            true_positives=tp,
            false_negatives=fn,
            true_negatives=tn,
            false_positives=fp,
        )

    @staticmethod
    def rmse_log10_lr(
        results: List[ValidationResult],
        expected_log10_lr_for_match: float = 10.0,
        expected_log10_lr_for_nonmatch: float = -5.0
    ) -> float:
        """
        Calculates RMSE of log10(LR) versus ground-truth expected values.
        Measures systematic calibration bias.
        """
        errors = []
        for r in results:
            expected = expected_log10_lr_for_match if r.is_true_match else expected_log10_lr_for_nonmatch
            errors.append((r.log10_lr - expected) ** 2)
        return math.sqrt(sum(errors) / len(errors)) if errors else 0.0

    @staticmethod
    def roc_curve(
        results: List[ValidationResult],
        thresholds: Optional[List[float]] = None
    ) -> List[Tuple[float, float, float]]:
        """
        Generates ROC curve points (threshold, FPR=1-TNR, TPR=Sensitivity).
        Returns list of (threshold, fpr, tpr) tuples sorted by threshold descending.
        """
        if thresholds is None:
            log_values = sorted(set(r.log10_lr for r in results), reverse=True)
            thresholds = log_values

        roc_points: List[Tuple[float, float, float]] = []
        for t in thresholds:
            m = MetricsEngine.evaluate(results, threshold_log10_lr=t)
            fpr = 1.0 - m.specificity
            tpr = m.sensitivity
            roc_points.append((t, fpr, tpr))

        return roc_points
