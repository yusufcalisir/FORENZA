"""
FORENZA Validation Lab Runner.
Orchestrates the full 10,000-profile simulation pipeline:
  1. Generate synthetic dataset (balanced across relationship types)
  2. Run LR engine on each pair
  3. Compute Accuracy / Sensitivity / Specificity / FIR / FER / RMSE
  4. Build Tippett calibration curves
  5. Export JSON summary report
"""

import json
import math
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from ..frequency_db import FrequencyDatabase
from ..lr_engine import LREngine
from ..kinship_engine import KinshipEngine
from ..models import KinshipRelationship
from ..probabilistic.mcmc import CalibrationEngine
from .synthetic_data import PairType, SyntheticDataGenerator, SyntheticPair
from .metrics import MetricsEngine, MetricsSummary, ValidationResult


@dataclass
class ValidationReport:
    """Complete validation run summary."""
    run_id: str
    population: str
    n_pairs_per_type: int
    elapsed_seconds: float
    match_metrics: Dict[str, Any]           # Metrics for true-match vs true-unrelated
    kinship_metrics: Dict[str, Any]         # Metrics for parent-child classification
    rmse_match_log10_lr: float
    tippett_data: Dict[str, Any]
    per_type_mean_log10_lr: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "population": self.population,
            "n_pairs_per_type": self.n_pairs_per_type,
            "elapsed_seconds": round(self.elapsed_seconds, 3),
            "match_metrics": self.match_metrics,
            "kinship_metrics": self.kinship_metrics,
            "rmse_match_log10_lr": round(self.rmse_match_log10_lr, 4),
            "tippett_data": self.tippett_data,
            "per_type_mean_log10_lr": {k: round(v, 4) for k, v in self.per_type_mean_log10_lr.items()},
            "metadata": self.metadata,
        }


class ValidationRunner:
    """Runs the full SWGDAM/PCAST-aligned validation simulation."""

    def __init__(
        self,
        population: str = "Caucasian",
        theta: float = 0.01,
        seed: int = 42
    ):
        self.population = population
        self.theta = theta
        self.freq_db = FrequencyDatabase(default_population=population)
        self.lr_engine = LREngine(freq_db=self.freq_db)
        self.kinship_engine = KinshipEngine(freq_db=self.freq_db)
        self.generator = SyntheticDataGenerator(population=population, seed=seed)

    def _compute_lr_result(self, pair: SyntheticPair, is_true_match: bool) -> ValidationResult:
        """Computes LR for a profile pair and wraps it as a ValidationResult."""
        result = self.lr_engine.compute_single_source_lr(
            evidence_profile=pair.profile1,
            suspect_profile=pair.profile2,
            theta=self.theta,
            population=self.population
        )
        lr_val = result.value
        if lr_val <= 0:
            log10_lr = -10.0
        else:
            log10_lr = math.log10(lr_val)

        return ValidationResult(
            pair_id=pair.pair_id,
            pair_type=pair.pair_type.value,
            log10_lr=log10_lr,
            is_true_match=is_true_match,
            called_match=log10_lr >= 0.0  # Neutral threshold: LR >= 1
        )

    def run(self, n_per_type: int = 1000, run_id: str = "VAL_RUN_001") -> ValidationReport:
        """
        Executes the full validation simulation.
        n_per_type: profiles per relationship type (1000 → 5000 total pairs)
        """
        t_start = time.time()

        print(f"[validator] Generating synthetic dataset ({n_per_type} pairs/type)...")
        dataset = self.generator.generate_dataset(n_per_type=n_per_type)

        # ── LR evaluation ───────────────────────────────────────────────────
        match_results: List[ValidationResult] = []
        per_type_log_lrs: Dict[str, List[float]] = {pt.value: [] for pt in PairType}

        # True-match pairs
        for pair in dataset[PairType.TRUE_MATCH]:
            r = self._compute_lr_result(pair, is_true_match=True)
            match_results.append(r)
            per_type_log_lrs[PairType.TRUE_MATCH.value].append(r.log10_lr)

        # True-unrelated pairs
        for pair in dataset[PairType.TRUE_UNRELATED]:
            r = self._compute_lr_result(pair, is_true_match=False)
            match_results.append(r)
            per_type_log_lrs[PairType.TRUE_UNRELATED.value].append(r.log10_lr)

        # Dropout partial profiles (treated as true-match ground truth)
        for pair in dataset[PairType.DROPOUT_PARTIAL]:
            r = self._compute_lr_result(pair, is_true_match=True)
            per_type_log_lrs[PairType.DROPOUT_PARTIAL.value].append(r.log10_lr)

        # ── Kinship LR evaluation ────────────────────────────────────────────
        kinship_results: List[ValidationResult] = []

        for pair in dataset[PairType.PARENT_CHILD]:
            ki_result = self.kinship_engine.compute_kinship_index(
                pair.profile1, pair.profile2,
                relationship=KinshipRelationship.PARENT_CHILD,
                theta=self.theta
            )
            ki_val = ki_result.value
            log10_ki = math.log10(ki_val) if ki_val > 0 else -10.0
            kinship_results.append(ValidationResult(
                pair_id=pair.pair_id,
                pair_type=pair.pair_type.value,
                log10_lr=log10_ki,
                is_true_match=True,
                called_match=log10_ki >= 0.0
            ))
            per_type_log_lrs[PairType.PARENT_CHILD.value].append(log10_ki)

        # Unrelated as kinship negatives
        for pair in dataset[PairType.TRUE_UNRELATED][:n_per_type]:
            ki_result = self.kinship_engine.compute_kinship_index(
                pair.profile1, pair.profile2,
                relationship=KinshipRelationship.PARENT_CHILD,
                theta=self.theta
            )
            ki_val = ki_result.value
            log10_ki = math.log10(ki_val) if ki_val > 0 else -10.0
            kinship_results.append(ValidationResult(
                pair_id=pair.pair_id + "_KIN",
                pair_type="unrelated_as_nonparent",
                log10_lr=log10_ki,
                is_true_match=False,
                called_match=log10_ki >= 0.0
            ))

        # ── Metrics computation ──────────────────────────────────────────────
        match_metrics_summary = MetricsEngine.evaluate(match_results, threshold_log10_lr=0.0)
        kinship_metrics_summary = MetricsEngine.evaluate(kinship_results, threshold_log10_lr=0.0)
        rmse = MetricsEngine.rmse_log10_lr(match_results)

        # ── Tippett calibration ──────────────────────────────────────────────
        donor_lrs = [10.0 ** r.log10_lr for r in match_results if r.is_true_match and r.log10_lr > -9]
        nondonor_lrs = [10.0 ** r.log10_lr for r in match_results if not r.is_true_match and r.log10_lr > -9]
        tippett = CalibrationEngine.generate_tippett_curve(
            donor_lrs=donor_lrs[:500],  # Subsample for report size
            nondonor_lrs=nondonor_lrs[:500]
        )

        # ── Per-type mean log10(LR) ──────────────────────────────────────────
        per_type_means: Dict[str, float] = {}
        for pt, vals in per_type_log_lrs.items():
            if vals:
                per_type_means[pt] = sum(vals) / len(vals)

        elapsed = time.time() - t_start
        print(f"[validator] Run complete in {elapsed:.2f}s | "
              f"Accuracy={match_metrics_summary.accuracy:.4f} | "
              f"FIR={match_metrics_summary.false_inclusion_rate:.2e} | "
              f"FER={match_metrics_summary.false_exclusion_rate:.4f}")

        return ValidationReport(
            run_id=run_id,
            population=self.population,
            n_pairs_per_type=n_per_type,
            elapsed_seconds=elapsed,
            match_metrics=match_metrics_summary.to_dict(),
            kinship_metrics=kinship_metrics_summary.to_dict(),
            rmse_match_log10_lr=rmse,
            tippett_data={
                "true_donor_curve_n": len(tippett["true_donor_curve"]),
                "non_donor_curve_n": len(tippett["non_donor_curve"]),
                "donor_curve_sample": tippett["true_donor_curve"][:10],
                "nondonor_curve_sample": tippett["non_donor_curve"][:10],
            },
            per_type_mean_log10_lr=per_type_means,
            metadata={
                "theta": self.theta,
                "seed": self.generator.seed,
                "model": "FORENZA Validation Runner v1.0"
            }
        )

    def export_report(self, report: ValidationReport, output_path: str) -> None:
        """Serializes the ValidationReport to a JSON file."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2)
        print(f"[validator] Report written to {output_path}")
