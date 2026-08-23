"""
FORENZA: Forensic Evidence Operating System
Module: ZK-SNARK Proving Systems - Arithmetic, Verification, Lookup & Transcendental Circuit Gadgets
"""

from .range_check import R1CSConstraint, RangeCheckGadget
from .arithmetic import ScaledMultiplicationGadget
from .division import NonDeterministicDivisionGadget
from .threshold import ThresholdInclusionGadget
from .transcendental import PiecewiseChebyshevLogApproximator
from .lookups import PlookupTableEngine
from .lod_accumulator import MultiLocusLodAccumulator

__all__ = [
    "R1CSConstraint",
    "RangeCheckGadget",
    "ScaledMultiplicationGadget",
    "NonDeterministicDivisionGadget",
    "ThresholdInclusionGadget",
    "PiecewiseChebyshevLogApproximator",
    "PlookupTableEngine",
    "MultiLocusLodAccumulator",
]
