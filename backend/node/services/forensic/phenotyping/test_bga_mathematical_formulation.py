"""
Unit Tests for FORENZA 55-SNP AIM BGA Mathematical Formulation Engine (Module 3.2).
"""

import math
import pytest
from node.services.forensic.phenotyping.bga_mathematical_formulation import (
    BGAMathematicalFormulation,
    CONTINENTAL_CENTROIDS,
    POPULATION_KEYS,
    KIDD_55_AIMS_MATRIX,
)


class TestBGAMathematicalFormulation:
    """Verifies pure mathematical operations of BGA-55."""

    def test_hardy_weinberg_genotype_log_likelihood(self):
        # f = 0.50 -> P(g=0) = 0.25, P(g=1) = 0.50, P(g=2) = 0.25
        ll0 = BGAMathematicalFormulation.genotype_log_likelihood(0, 0.50)
        ll1 = BGAMathematicalFormulation.genotype_log_likelihood(1, 0.50)
        ll2 = BGAMathematicalFormulation.genotype_log_likelihood(2, 0.50)

        assert abs(math.exp(ll0) - 0.25) < 1e-4
        assert abs(math.exp(ll1) - 0.50) < 1e-4
        assert abs(math.exp(ll2) - 0.25) < 1e-4

    def test_sum_to_one_simplex_invariant_across_random_dosages(self):
        dosages = {
            "rs2814778": 1,
            "rs1426654": 2,
            "rs16891982": 0,
            "rs3827760": 1,
            "rs1800414": 0,
            "rs1229984": 2,
        }
        res = BGAMathematicalFormulation.estimate_continental_admixture(dosages)
        assert res.is_simplex_valid is True
        assert abs(sum(res.proportions.values()) - 1.0) <= 1e-5

    def test_geodesic_centroid_projection_and_bounds(self):
        # Pure European weights
        eur_props = {"EUR": 1.0, "AFR": 0.0, "EAS": 0.0, "SAS": 0.0, "AMR": 0.0, "MID": 0.0}
        gis_eur = BGAMathematicalFormulation.project_geodesic_centroid(eur_props)

        assert abs(gis_eur.latitude - 48.50) < 0.1
        assert abs(gis_eur.longitude - 15.20) < 0.1
        assert "European" in gis_eur.nearest_centroid

        # Latitude and longitude must strictly respect earth physical boundaries
        assert -90.0 <= gis_eur.latitude <= 90.0
        assert -180.0 <= gis_eur.longitude <= 180.0

    def test_confidence_ellipse_geometry(self):
        # Mixed population should yield wider confidence ellipse than pure
        pure_props = {"EUR": 1.0, "AFR": 0.0, "EAS": 0.0, "SAS": 0.0, "AMR": 0.0, "MID": 0.0}
        admixed_props = {"EUR": 0.5, "AFR": 0.5, "EAS": 0.0, "SAS": 0.0, "AMR": 0.0, "MID": 0.0}

        pure_gis = BGAMathematicalFormulation.project_geodesic_centroid(pure_props)
        admix_gis = BGAMathematicalFormulation.project_geodesic_centroid(admixed_props)

        assert admix_gis.confidence_ellipse.semi_major_km > pure_gis.confidence_ellipse.semi_major_km
        assert admix_gis.confidence_ellipse.semi_major_deg > 0.0

    def test_empty_dosages_yields_uniform_prior(self):
        res = BGAMathematicalFormulation.estimate_continental_admixture({})
        assert res.assayed_snps_count == 0
        assert res.admixture_classification == "UNINFORMATIVE"
        for p in res.proportions.values():
            assert abs(p - (1.0 / len(POPULATION_KEYS))) < 1e-4
