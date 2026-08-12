import pytest
from backend.node.services.forensic.qc.qc_engine import QualityAssuranceEngine


def test_clean_profile_qc_passed():
    engine = QualityAssuranceEngine()
    res = engine.evaluate_profile_qc(
        negative_control_max_rfu=0.0,
        positive_control_concordant=True
    )
    assert res["overall_qc_verdict"] == "QC_PASSED"
    assert res["action_recommendation"] == "PROCEED_TO_STATISTICAL_INTERPRETATION"
    assert len(res["quality_inspection_matrix"]) == 5


def test_negative_control_contamination_qc_failed():
    engine = QualityAssuranceEngine()
    res = engine.evaluate_profile_qc(
        negative_control_max_rfu=120.0,  # Exogenous contamination peak
        positive_control_concordant=True
    )
    assert res["overall_qc_verdict"] == "QC_FAILED"
    assert "RE_EXTRACTION" in res["action_recommendation"]


def test_positive_control_discordance_qc_failed():
    engine = QualityAssuranceEngine()
    res = engine.evaluate_profile_qc(
        negative_control_max_rfu=0.0,
        positive_control_concordant=False  # Control match failure
    )
    assert res["overall_qc_verdict"] == "QC_FAILED"


def test_stochastic_threshold_warning_review_required():
    engine = QualityAssuranceEngine()
    low_rfu_peaks = [
        {"locus": "D3S1358", "alleles": ["15", "16"], "peak_heights_rfu": [90, 85]}  # < 150 ST
    ]
    res = engine.evaluate_profile_qc(
        loci_peaks=low_rfu_peaks,
        negative_control_max_rfu=0.0,
        positive_control_concordant=True
    )
    assert res["overall_qc_verdict"] == "REVIEW_REQUIRED"
    assert res["stochastic_warning_count"] == 1


def test_heterozygote_imbalance_warning():
    engine = QualityAssuranceEngine()
    imbalanced_peaks = [
        {"locus": "vWA", "alleles": ["16", "17"], "peak_heights_rfu": [1000, 400]}  # Hb = 0.40 < 0.60
    ]
    res = engine.evaluate_profile_qc(
        loci_peaks=imbalanced_peaks,
        negative_control_max_rfu=0.0,
        positive_control_concordant=True
    )
    assert res["overall_qc_verdict"] == "REVIEW_REQUIRED"
    assert res["imbalanced_loci_count"] == 1


def test_empty_loci_peaks_uses_default():
    engine = QualityAssuranceEngine()
    res = engine.evaluate_profile_qc(loci_peaks=[])
    assert res["total_loci_inspected"] == 4
