"""
Unit tests for Epigenetic Data Transformer, bijective mappings, and QC engine.
"""

import pytest
import math
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    MethylationSample,
    EpigeneticTissueType,
    EpigeneticPlatform,
)
from backend.node.services.forensic.epigenetics.clocks.data_transformer import (
    EpigeneticDataTransformer,
)


def test_bijective_beta_m_transformation():
    """Verify exact bijective inverse mapping: beta -> M -> beta."""
    test_betas = [0.05, 0.20, 0.50, 0.75, 0.95]
    for b_orig in test_betas:
        m_val = EpigeneticDataTransformer.beta_to_m_value(b_orig)
        b_reconstructed = EpigeneticDataTransformer.m_to_beta_value(m_val)
        assert abs(b_orig - b_reconstructed) < 1e-6


def test_intensities_to_beta_with_offset():
    """Verify beta calculation from fluorescent intensities with alpha=100."""
    m_int = 4000.0
    u_int = 6000.0
    # beta = 4000 / (4000 + 6000 + 100) = 4000 / 10100 = 0.3960396
    beta = EpigeneticDataTransformer.intensities_to_beta(m_int, u_int, alpha=100.0)
    expected = 4000.0 / 10100.0
    assert abs(beta - expected) < 1e-5


def test_mps_read_depth_to_beta():
    """Verify MPS read count fractions and depth sufficiency."""
    # Sufficient depth: C=45, T=55 -> depth=100, beta=0.45
    beta, depth, is_valid = EpigeneticDataTransformer.read_counts_to_beta(45, 55)
    assert beta == 0.45
    assert depth == 100
    assert is_valid is True

    # Insufficient depth (<20x)
    beta_low, depth_low, is_valid_low = EpigeneticDataTransformer.read_counts_to_beta(5, 5)
    assert beta_low == 0.50
    assert depth_low == 10
    assert is_valid_low is False


def test_sample_qc_and_imputation():
    """Verify sample QC processing, p-value filtering, and locus imputation."""
    sample = MethylationSample(
        sample_id="SAMPLE_QC_01",
        tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
        platform=EpigeneticPlatform.ILLUMINA_450K,
        beta_values={
            "cg16867657": 0.42,  # ELOVL2
            "cg06639320": 0.35,  # FHL2
            "cg99999999": 0.50,  # Noisy probe
        },
        detection_p_values={
            "cg16867657": 0.0001,
            "cg06639320": 0.005,
            "cg99999999": 0.08,  # > 0.01 -> Should be masked
        },
        bisulfite_conversion_efficiency=0.994,
    )

    required_probes = {"cg16867657", "cg06639320", "cg16419235"}  # PENK is missing
    processed_betas, qc_meta = EpigeneticDataTransformer.process_and_qc_sample(
        sample=sample,
        required_probes=required_probes,
        auto_impute=True,
    )

    assert qc_meta["bisulfite_pass"] is True
    assert qc_meta["masked_p_value_count"] == 1  # cg99999999 was masked
    assert "cg99999999" not in processed_betas
    assert processed_betas["cg16867657"] == 0.42
    assert processed_betas["cg06639320"] == 0.35
    assert "cg16419235" in processed_betas  # PENK was imputed
    assert "cg16419235" in qc_meta["imputed_probes"]
    assert abs(processed_betas["cg16419235"] - 0.245) < 1e-4  # Default reference mean for PENK
