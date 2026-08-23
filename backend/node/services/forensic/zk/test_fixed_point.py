"""
Unit tests for Scaled Fixed-Point Quantization Engine (S=16/32).
"""

import pytest
import math
from backend.node.services.forensic.zk.fixed_point import FixedPointEngine
from backend.node.services.forensic.zk.finite_field import BN254_SCALAR_FIELD_R


def test_fixed_point_initialization_scales():
    fp16 = FixedPointEngine(scale_s=16)
    assert fp16.scale_factor == 65536
    assert fp16.precision_bound == 1.0 / 65536

    fp32 = FixedPointEngine(scale_s=32)
    assert fp32.scale_factor == 4294967296
    assert fp32.precision_bound == 1.0 / 4294967296

    with pytest.raises(ValueError):
        _ = FixedPointEngine(scale_s=15)


def test_quantize_dequantize_roundtrip_precision_bound():
    fp = FixedPointEngine(scale_s=16)
    test_values = [0.0, 1.0, 12.3456, 0.00241, 1000000.5, 3.1415926535]

    for val in test_values:
        rec, err, within_bound = fp.compute_quantization_error(val)
        assert within_bound is True
        assert err <= (1.0 / 65536.0 + 1e-12)


def test_scaled_multiplication_remainder_invariance():
    fp = FixedPointEngine(scale_s=16)
    x = 2.5
    y = 4.0
    x_hat = fp.quantize(x)
    y_hat = fp.quantize(y)

    z_hat, r = fp.multiply_scaled(x_hat, y_hat)
    # Reconstructed z should be ~ 10.0
    z_rec = fp.dequantize(z_hat)
    assert abs(z_rec - 10.0) < 1e-3
    assert 0 <= r < fp.scale_factor


def test_scaled_division_gadget_invariant():
    fp = FixedPointEngine(scale_s=16)
    # Likelihood Ratio: N = 250000, D = 50 => LR = 5000
    n = 250000.0
    d = 50.0
    n_hat = fp.quantize(n)
    d_hat = fp.quantize(d)

    quotient_hat, r = fp.divide_scaled(n_hat, d_hat)
    lr_rec = fp.dequantize(quotient_hat)
    assert abs(lr_rec - 5000.0) < 1e-2
    # Invariant: 0 <= r < d_hat
    assert 0 <= r < d_hat


def test_vector_quantization_roundtrip():
    fp = FixedPointEngine(scale_s=32)
    vec = [0.05, 0.25, 0.70, 1e-6, 12345.6789]
    q_vec = fp.quantize_vector(vec)
    rec_vec = fp.dequantize_vector(q_vec)

    for orig, rec in zip(vec, rec_vec):
        assert abs(orig - rec) <= (1.0 / (2**32) + 1e-12)
