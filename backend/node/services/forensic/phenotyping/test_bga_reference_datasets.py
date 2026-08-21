"""
Unit Tests for FORENZA BGA-55 Certified Reference Standards (Module 3.2).
"""

import pytest
from node.services.forensic.phenotyping.bga_reference_datasets import (
    BGAReferenceDatasets,
    BGA_GOLDEN_STANDARDS,
)
from node.services.forensic.phenotyping.bga_mathematical_formulation import (
    BGAMathematicalFormulation,
)


class TestBGAReferenceDatasets:
    """Verifies all 5 registered certified reference standards."""

    def test_five_standards_registered(self):
        stds = BGAReferenceDatasets.list_standards()
        assert len(stds) == 5

    def test_na12878_ceu_european_standard(self):
        std = BGAReferenceDatasets.get_standard("NA12878_CEU_EUROPEAN")
        res = BGAMathematicalFormulation.analyze_full_bga_profile(std.genotype_dosages)

        assert res.admixture.dominant_population == std.expected_dominant_pop
        assert res.admixture.dominant_proportion >= std.min_dominant_proportion
        assert std.expected_lat_bounds[0] <= res.gis.latitude <= std.expected_lat_bounds[1]
        assert std.expected_lng_bounds[0] <= res.gis.longitude <= std.expected_lng_bounds[1]

    def test_na19240_yri_african_standard(self):
        std = BGAReferenceDatasets.get_standard("NA19240_YRI_AFRICAN")
        res = BGAMathematicalFormulation.analyze_full_bga_profile(std.genotype_dosages)

        assert res.admixture.dominant_population == std.expected_dominant_pop
        assert res.admixture.dominant_proportion >= std.min_dominant_proportion
        assert std.expected_lat_bounds[0] <= res.gis.latitude <= std.expected_lat_bounds[1]
        assert std.expected_lng_bounds[0] <= res.gis.longitude <= std.expected_lng_bounds[1]

    def test_na18507_chb_east_asian_standard(self):
        std = BGAReferenceDatasets.get_standard("NA18507_CHB_EAST_ASIAN")
        res = BGAMathematicalFormulation.analyze_full_bga_profile(std.genotype_dosages)

        assert res.admixture.dominant_population == std.expected_dominant_pop
        assert res.admixture.dominant_proportion >= std.min_dominant_proportion
        assert std.expected_lat_bounds[0] <= res.gis.latitude <= std.expected_lat_bounds[1]
        assert std.expected_lng_bounds[0] <= res.gis.longitude <= std.expected_lng_bounds[1]

    def test_hg002_aj_mediterranean_standard(self):
        std = BGAReferenceDatasets.get_standard("HG002_AJ_MEDITERRANEAN")
        res = BGAMathematicalFormulation.analyze_full_bga_profile(std.genotype_dosages)

        assert res.admixture.dominant_population == std.expected_dominant_pop
        assert res.admixture.dominant_proportion >= std.min_dominant_proportion
        assert std.expected_lat_bounds[0] <= res.gis.latitude <= std.expected_lat_bounds[1]
        assert std.expected_lng_bounds[0] <= res.gis.longitude <= std.expected_lng_bounds[1]
