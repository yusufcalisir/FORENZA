"""
FORENZA: Forensic Evidence Operating System
Module: ZK-SNARK Proving Systems - Scaled Fixed-Point Quantization Engine

Source of Truth: research/zk_snark_proving_systems_verifiable_forensic_computation_research.md
Deterministic Numerical Quantization (Scale S=16/32) with Bounded Remainders and Invariant Tracking.
"""

from typing import Tuple, Dict, Any, List, Optional
import math
from .schemas import FixedPointConfig
from .finite_field import BN254_SCALAR_FIELD_R, FieldElement


class FixedPointEngine:
    """
    Scaled Fixed-Point Arithmetic & Quantization Engine.
    Enforces x_hat = floor(x * 2^S) mod r with strict remainder tracking.
    """

    def __init__(self, scale_s: int = 16, modulus: int = BN254_SCALAR_FIELD_R):
        if scale_s not in (8, 16, 24, 32, 48, 64):
            raise ValueError(f"Unsupported fixed-point scale S={scale_s}. Allowed: 8, 16, 24, 32, 48, 64")
        self.scale_s = scale_s
        self.scale_factor = 1 << scale_s  # 2^S
        self.modulus = modulus
        self.precision_bound = 1.0 / self.scale_factor  # 2^-S

    def quantize(self, value: float) -> int:
        """
        Quantizes real float value x into integer x_hat = floor(x * 2^S) mod r.
        Handles negative values via two's complement modulo r.
        """
        if math.isnan(value) or math.isinf(value):
            raise ValueError("Cannot quantize NaN or Infinite value")

        scaled_val = int(math.floor(value * self.scale_factor))
        return scaled_val % self.modulus

    def dequantize(self, quantized_val: int) -> float:
        """
        Reconstructs real float from quantized integer x_hat.
        Detects field wrap-around for negative values.
        """
        # If value is in upper half of field, treat as negative
        if quantized_val > (self.modulus >> 1):
            signed_val = quantized_val - self.modulus
        else:
            signed_val = quantized_val

        return float(signed_val) / float(self.scale_factor)

    def multiply_scaled(self, x_hat: int, y_hat: int) -> Tuple[int, int]:
        """
        Multiplies two scaled fixed-point numbers:
        x_hat * y_hat = z_hat * 2^S + r
        Returns (z_hat, r) where 0 <= r < 2^S.
        """
        # Treat as signed integers if necessary
        signed_x = x_hat if x_hat <= (self.modulus >> 1) else x_hat - self.modulus
        signed_y = y_hat if y_hat <= (self.modulus >> 1) else y_hat - self.modulus

        product = signed_x * signed_y
        quotient = product // self.scale_factor
        remainder = product % self.scale_factor

        z_hat = quotient % self.modulus
        r = remainder % self.modulus
        return z_hat, r

    def divide_scaled(self, numerator_hat: int, denominator_hat: int) -> Tuple[int, int]:
        """
        Non-deterministic division gadget helper:
        numerator_hat * 2^S = quotient_hat * denominator_hat + r
        Returns (quotient_hat, r) where 0 <= r < denominator_hat.
        """
        if denominator_hat == 0 or denominator_hat % self.modulus == 0:
            raise ZeroDivisionError("Division by zero in scaled fixed-point division")

        # Unsigned representation for non-negative likelihood ratios
        dividend = numerator_hat * self.scale_factor
        quotient = dividend // denominator_hat
        remainder = dividend % denominator_hat

        quotient_hat = quotient % self.modulus
        r = remainder % self.modulus

        # Enforce invariant: 0 <= r < denominator_hat
        assert 0 <= remainder < denominator_hat, f"Division remainder invariant violated: r={remainder}, D={denominator_hat}"
        return quotient_hat, r

    def quantize_vector(self, values: List[float]) -> List[int]:
        """Quantizes an entire vector of continuous floats."""
        return [self.quantize(v) for v in values]

    def dequantize_vector(self, quantized_values: List[int]) -> List[float]:
        """Dequantizes an entire vector of integers back to floats."""
        return [self.dequantize(q) for q in quantized_values]

    def compute_quantization_error(self, original_val: float) -> Tuple[float, float, bool]:
        """
        Returns (reconstructed_val, absolute_error, is_within_bound).
        Invariant: absolute_error <= 2^-S.
        """
        q = self.quantize(original_val)
        rec = self.dequantize(q)
        err = abs(rec - original_val)
        is_within_bound = err <= (self.precision_bound + 1e-12)
        return rec, err, is_within_bound
