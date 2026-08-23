"""
Unit Tests for Genetic Map Interpolator & Recombination Distances.
"""

import pytest
from backend.node.services.forensic.genomics.fgg.genetic_map import FGGGeneticMap


class TestFGGGeneticMap:
    """Tests cM interpolation and chromosome genetic length invariants."""

    def test_total_autosomal_length(self):
        # Total autosomal length should be ~3545.92 cM (within standard band 3500-3650 cM)
        total_cm = FGGGeneticMap.TOTAL_AUTOSOMAL_CM
        assert 3500.0 <= total_cm <= 3650.0
        assert round(total_cm, 2) == 3545.92

    def test_chromosome_length_retrieval(self):
        assert FGGGeneticMap.get_chromosome_length_cm("1") == 286.27
        assert FGGGeneticMap.get_chromosome_length_cm("chr1") == 286.27
        assert FGGGeneticMap.get_chromosome_length_cm("22") == 74.11
        assert FGGGeneticMap.get_chromosome_length_cm("invalid") == 0.0

    def test_monotonic_interpolation(self):
        # bp_to_cm must be monotonically non-decreasing
        cm1 = FGGGeneticMap.bp_to_cm("1", 1000000)
        cm2 = FGGGeneticMap.bp_to_cm("1", 50000000)
        cm3 = FGGGeneticMap.bp_to_cm("1", 200000000)
        assert 0.0 < cm1 < cm2 < cm3 <= 286.27

    def test_segment_length_distance(self):
        # 100 Mb on Chromosome 1 (~248.96 Mb max -> ~115 cM)
        seg_cm = FGGGeneticMap.get_segment_length_cm("1", 10000000, 110000000)
        assert 100.0 <= seg_cm <= 130.0
