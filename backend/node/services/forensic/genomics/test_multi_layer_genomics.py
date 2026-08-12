import pytest
from backend.node.services.forensic.genomics.multi_layer_engine import MultiLayerGenomicsEngine


def test_standard_5_layer_genomic_synthesis():
    engine = MultiLayerGenomicsEngine()
    result = engine.synthesize_genomic_layers(
        lr_str=1.0e12,
        lr_snp=1.0e3,
        lr_mtdna=1.0e2,
        lr_y_str=1.0e4,
        lr_wgs=1.0e5
    )
    assert result["log10_joint_likelihood_ratio"] == 26.0
    assert result["enfsi_verbal_predicate"] == "EXTREMELY_STRONG_SUPPORT_FOR_INCLUSION"
    assert result["active_layer_count"] == 5
    assert result["joint_exclusion_probability"] > 0.99999


def test_single_layer_str_only_synthesis():
    engine = MultiLayerGenomicsEngine()
    result = engine.synthesize_genomic_layers(
        lr_str=1.0e6,
        lr_snp=1.0,
        lr_mtdna=1.0,
        lr_y_str=1.0,
        lr_wgs=1.0
    )
    assert result["log10_joint_likelihood_ratio"] == 6.0
    assert result["active_layer_count"] == 1
    assert result["enfsi_verbal_predicate"] == "EXTREMELY_STRONG_SUPPORT_FOR_INCLUSION"


def test_exclusion_layer_synthesis():
    engine = MultiLayerGenomicsEngine()
    result = engine.synthesize_genomic_layers(
        lr_str=1.0e12,
        lr_snp=0.0001,  # Exclusion in SNP layer
        lr_mtdna=1.0e2,
        lr_y_str=1.0e4,
        lr_wgs=1.0e5
    )
    assert result["log10_joint_likelihood_ratio"] == 19.0
    assert len(result["genomic_layers"]) == 5


def test_zero_or_negative_lr_clamped():
    engine = MultiLayerGenomicsEngine()
    result = engine.synthesize_genomic_layers(lr_str=0.0)
    assert result["log10_joint_likelihood_ratio"] < 20.0


def test_all_unobserved_layers():
    engine = MultiLayerGenomicsEngine()
    result = engine.synthesize_genomic_layers(
        lr_str=1.0, lr_snp=1.0, lr_mtdna=1.0, lr_y_str=1.0, lr_wgs=1.0
    )
    assert result["log10_joint_likelihood_ratio"] == 0.0
    assert result["active_layer_count"] == 0
    assert result["enfsi_verbal_predicate"] == "LIMITED_SUPPORT_FOR_INCLUSION"


def test_joint_exclusion_probability_calculation():
    engine = MultiLayerGenomicsEngine()
    result = engine.synthesize_genomic_layers(pe_str=0.90, pe_snp=0.50)
    # Non-exclusion prod = (1 - 0.90) * (1 - 0.50) = 0.10 * 0.50 = 0.05
    # Joint PE = 1 - 0.05 = 0.95
    assert result["joint_exclusion_probability"] >= 0.95
