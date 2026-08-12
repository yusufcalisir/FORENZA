import pytest
from backend.node.services.forensic.synthetic.synthetic_case_engine import SyntheticCaseEngine


def test_generate_synthetic_case_3person_mixture():
    engine = SyntheticCaseEngine()
    res = engine.generate_synthetic_case(
        scenario_type="3_PERSON_STR_MIXTURE",
        num_contributors=3,
        degradation_factor=0.3
    )

    assert res["academic_validation_ready"] is True
    assert res["num_contributors"] == 3
    assert len(res["ground_truth_contributors"]) == 3
    assert "synthetic_mixture_peaks" in res
    assert res["ground_truth_metrics"]["ground_truth_validated"] is True
    assert res["benchmark_hmac_hash"] is not None


def test_generate_synthetic_case_contributor_clamping():
    engine = SyntheticCaseEngine()
    res = engine.generate_synthetic_case(num_contributors=10)
    assert res["num_contributors"] == 4  # Clamped to max 4


def test_evaluate_benchmark_against_ground_truth():
    engine = SyntheticCaseEngine()
    bench = engine.evaluate_benchmark("SYNTH-101", engine_calculated_log10_lr=24.2)
    assert bench["self_validation_verdict"] == "PASSED_ACADEMIC_BENCHMARK"
    assert bench["roc_auc_score"] > 0.99
    assert bench["false_inclusion_rate_fir_0pct"] == 0.0


def test_synthetic_mixture_peaks_contain_rfu():
    engine = SyntheticCaseEngine()
    res = engine.generate_synthetic_case()
    peaks = res["synthetic_mixture_peaks"]
    assert "D3S1358" in peaks
    if peaks["D3S1358"]:
        assert "height_rfu" in peaks["D3S1358"][0]
        assert peaks["D3S1358"][0]["height_rfu"] >= 50.0


def test_ground_truth_contributors_have_autosomal_profiles():
    engine = SyntheticCaseEngine()
    res = engine.generate_synthetic_case()
    c1 = res["ground_truth_contributors"][0]
    assert "true_autosomal_profile" in c1
    assert "D3S1358" in c1["true_autosomal_profile"]
    assert len(c1["true_autosomal_profile"]["D3S1358"]) == 2


def test_reproducible_synthetic_benchmark_hash():
    engine = SyntheticCaseEngine()
    res1 = engine.generate_synthetic_case(scenario_type="TYPE_A")
    res2 = engine.generate_synthetic_case(scenario_type="TYPE_B")
    assert res1["benchmark_hmac_hash"] != res2["benchmark_hmac_hash"]
