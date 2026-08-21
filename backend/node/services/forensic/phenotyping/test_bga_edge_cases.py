"""
Edge-Case Test Suite for FORENZA 55-SNP AIM Biogeographic Ancestry Engine (Module 3.2).

Covers all 5 Documented Verification Edge Cases:
  - EC-BGA-01: Pure European Reference Standard NA12878
  - EC-BGA-02: Pure Sub-Saharan African Reference Standard NA19240
  - EC-BGA-03: Pure East Asian Reference Standard NA18507
  - EC-BGA-04: 50/50 Balanced EUR/AFR Synthetic Admixture
  - EC-BGA-05: Geodesic Physical Bounds & Probability Simplex Invariants
"""

import math
import pytest
from node.services.forensic.phenotyping.bga_mathematical_formulation import (
    BGAMathematicalFormulation,
    POPULATION_KEYS,
    KIDD_55_AIMS_MATRIX,
)
from node.services.forensic.phenotyping.bga_reference_datasets import (
    BGAReferenceDatasets,
)


class TestVectorBGAEdgeCases:
    """Rigorous verification of EC-BGA-01 through EC-BGA-05."""

    def test_ec_bga_01_pure_european_na12878(self):
        """EC-BGA-01: Pure European NA12878 assigns Q_EUR >= 0.95 with European GIS."""
        std = BGAReferenceDatasets.get_standard("NA12878_CEU_EUROPEAN")
        res = BGAMathematicalFormulation.analyze_full_bga_profile(std.genotype_dosages)

        assert res.admixture.dominant_population == "EUR"
        assert res.admixture.proportions["EUR"] >= 0.95
        assert res.admixture.admixture_classification == "HOMOGENEOUS"
        assert 40.0 <= res.gis.latitude <= 55.0
        assert 5.0 <= res.gis.longitude <= 25.0
        assert "European" in res.gis.nearest_centroid

    def test_ec_bga_02_pure_african_na19240(self):
        """EC-BGA-02: Pure Sub-Saharan African NA19240 assigns Q_AFR >= 0.98 with African GIS."""
        std = BGAReferenceDatasets.get_standard("NA19240_YRI_AFRICAN")
        res = BGAMathematicalFormulation.analyze_full_bga_profile(std.genotype_dosages)

        assert res.admixture.dominant_population == "AFR"
        assert res.admixture.proportions["AFR"] >= 0.98
        assert res.admixture.admixture_classification == "HOMOGENEOUS"
        assert -5.0 <= res.gis.latitude <= 15.0
        assert 10.0 <= res.gis.longitude <= 35.0
        assert "African" in res.gis.nearest_centroid

    def test_ec_bga_03_pure_east_asian_na18507(self):
        """EC-BGA-03: Pure East Asian NA18507 assigns Q_EAS >= 0.95 with East Asian GIS."""
        std = BGAReferenceDatasets.get_standard("NA18507_CHB_EAST_ASIAN")
        res = BGAMathematicalFormulation.analyze_full_bga_profile(std.genotype_dosages)

        assert res.admixture.dominant_population == "EAS"
        assert res.admixture.proportions["EAS"] >= 0.95
        assert res.admixture.admixture_classification == "HOMOGENEOUS"
        assert 25.0 <= res.gis.latitude <= 45.0
        assert 90.0 <= res.gis.longitude <= 125.0
        assert "East Asian" in res.gis.nearest_centroid

    def test_ec_bga_04_balanced_synthetic_admixture(self):
        """EC-BGA-04: 50/50 Balanced Synthetic Admixture standard resolves intermediate proportions."""
        std = BGAReferenceDatasets.get_standard("ADMIXED_EUR_AFR_SYNTHETIC")
        res = BGAMathematicalFormulation.analyze_full_bga_profile(std.genotype_dosages)

        # EUR and AFR should both be significant (> 0.25)
        assert res.admixture.proportions["EUR"] >= 0.25
        assert res.admixture.proportions["AFR"] >= 0.25
        # The sum of EUR + AFR should explain the overwhelming majority of ancestry (> 0.80)
        assert (res.admixture.proportions["EUR"] + res.admixture.proportions["AFR"]) >= 0.80
        assert res.admixture.admixture_classification in ["BI_ADMIXED", "MULTI_ADMIXED"]

    def test_ec_bga_05_geodesic_bounds_and_simplex_invariants(self):
        """EC-BGA-05: Extreme dosage permutations maintain coordinate physical bounds and sum-to-one simplex."""
        # Extreme vectors: all 0s, all 1s, all 2s, alternating
        for extreme_dosage in [0.0, 1.0, 2.0]:
            dosages = {snp_id: extreme_dosage for snp_id in list(KIDD_55_AIMS_MATRIX.keys())[:30]}
            res = BGAMathematicalFormulation.analyze_full_bga_profile(dosages)

            # 1. Simplex invariant
            assert abs(sum(res.admixture.proportions.values()) - 1.0) <= 1e-5
            assert res.admixture.is_simplex_valid is True

            # 2. Geodesic coordinate bounds
            assert -90.0 <= res.gis.latitude <= 90.0
            assert -180.0 <= res.gis.longitude <= 180.0

            # 3. Confidence ellipse non-negativity
            assert res.gis.confidence_ellipse.semi_major_deg >= 0.0
            assert res.gis.confidence_ellipse.semi_minor_deg >= 0.0
            assert res.gis.confidence_ellipse.semi_major_km >= 0.0
            assert res.gis.confidence_ellipse.semi_minor_km >= 0.0
