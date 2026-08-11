"""
Unit Test Suite for FORENZA Validation Lab (Phase 3).
Tests synthetic dataset generation, metrics engine, and end-to-end validation run.
"""

import pytest
from backend.node.services.forensic.validation.synthetic_data import (
    SyntheticDataGenerator, PairType
)
from backend.node.services.forensic.validation.metrics import (
    MetricsEngine, ValidationResult
)
from backend.node.services.forensic.validation.validator import ValidationRunner


# ── 3.1 Synthetic Generator ──────────────────────────────────────────────────

def test_synthetic_generator_true_match():
    gen = SyntheticDataGenerator(seed=42)
    pair = gen.generate_true_match_pair("TEST_TM")
    assert pair.pair_type == PairType.TRUE_MATCH
    # Both profiles must be identical at every locus
    for locus in pair.profile1.loci:
        assert pair.profile1.loci[locus].alleles == pair.profile2.loci[locus].alleles


def test_synthetic_generator_parent_child():
    gen = SyntheticDataGenerator(seed=42)
    pair = gen.generate_parent_child_pair("TEST_PC")
    assert pair.pair_type == PairType.PARENT_CHILD
    # Child must share at least one allele with parent at every locus
    for locus in pair.profile1.loci:
        if locus not in pair.profile2.loci:
            continue
        parent_alleles = set(pair.profile1.loci[locus].alleles)
        child_alleles = set(pair.profile2.loci[locus].alleles)
        assert len(parent_alleles & child_alleles) >= 1, (
            f"No shared allele at locus {locus}: parent={parent_alleles} child={child_alleles}"
        )


def test_synthetic_generator_dropout():
    gen = SyntheticDataGenerator(seed=42)
    pair = gen.generate_dropout_profile("TEST_DO", dropout_rate=1.0)
    assert pair.pair_type == PairType.DROPOUT_PARTIAL
    # With 100% dropout rate, all heterozygous loci should appear homozygous in P2
    for locus in pair.profile2.loci:
        g2 = pair.profile2.loci[locus]
        assert g2.is_homozygote, f"Expected homozygote at {locus} after 100% dropout"


def test_dataset_generation_counts():
    gen = SyntheticDataGenerator(seed=0)
    dataset = gen.generate_dataset(n_per_type=50)
    for pt in [PairType.TRUE_MATCH, PairType.TRUE_UNRELATED,
               PairType.PARENT_CHILD, PairType.FULL_SIBLING, PairType.DROPOUT_PARTIAL]:
        assert len(dataset[pt]) == 50, f"Expected 50 pairs for {pt}, got {len(dataset[pt])}"


# ── 3.2 Metrics Engine ───────────────────────────────────────────────────────

def test_metrics_perfect_classifier():
    """All true-match pairs have high LR, all unrelated have low LR → perfect classification."""
    results = (
        [ValidationResult(f"TM_{i}", "true_match", 8.0, True, True) for i in range(100)] +
        [ValidationResult(f"UR_{i}", "true_unrelated", -4.0, False, False) for i in range(100)]
    )
    m = MetricsEngine.evaluate(results, threshold_log10_lr=0.0)
    assert m.accuracy == 1.0
    assert m.sensitivity == 1.0
    assert m.specificity == 1.0
    assert m.false_inclusion_rate == 0.0
    assert m.false_exclusion_rate == 0.0


def test_metrics_fir_at_full_false_inclusion():
    """All unrelated pairs incorrectly called match → FIR = 1.0."""
    results = [ValidationResult(f"UR_{i}", "true_unrelated", 5.0, False, True) for i in range(50)]
    m = MetricsEngine.evaluate(results, threshold_log10_lr=0.0)
    assert m.false_inclusion_rate == 1.0


def test_rmse_log10_lr():
    """RMSE is 0 when all predictions exactly match expected LR targets."""
    results = (
        [ValidationResult(f"TM_{i}", "true_match", 10.0, True, True) for i in range(50)] +
        [ValidationResult(f"UR_{i}", "true_unrelated", -5.0, False, False) for i in range(50)]
    )
    rmse = MetricsEngine.rmse_log10_lr(results, 10.0, -5.0)
    assert rmse == 0.0


# ── 3.3 End-to-End Validation Run ───────────────────────────────────────────

def test_validation_runner_smoke():
    """Runs a small validation (50 pairs/type) and checks report structure."""
    runner = ValidationRunner(population="Caucasian", theta=0.01, seed=42)
    report = runner.run(n_per_type=50, run_id="SMOKE_TEST")

    assert report.run_id == "SMOKE_TEST"
    assert report.n_pairs_per_type == 50
    assert report.elapsed_seconds > 0
    assert 0.0 <= report.match_metrics["accuracy"] <= 1.0
    assert 0.0 <= report.match_metrics["false_inclusion_rate"] <= 1.0
    assert report.rmse_match_log10_lr >= 0.0
    assert "true_donor_curve_n" in report.tippett_data
    assert PairType.TRUE_MATCH.value in report.per_type_mean_log10_lr
    assert PairType.TRUE_UNRELATED.value in report.per_type_mean_log10_lr
    # True-match mean LR should be >> true-unrelated mean LR
    assert (report.per_type_mean_log10_lr[PairType.TRUE_MATCH.value] >
            report.per_type_mean_log10_lr[PairType.TRUE_UNRELATED.value])
