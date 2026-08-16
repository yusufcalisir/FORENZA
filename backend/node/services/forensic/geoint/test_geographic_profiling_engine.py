"""
Unit and Golden Benchmark Verification Suite for Pillar 7 Phase 2.2:
Bayesian Geographic Profiling & Spatial Crime Analytics Engine (geographic_profiling_engine.py).

Verifies verbatim against:
  - Pillar 7 §4.1: Rossmo's Targeted Hunting Formula (B=1.50km, f=1.60, g=0.80)
  - Pillar 7 §4.2: WGS84 Ellipsoidal Geodesics (Vincenty Algorithm)
  - Pillar 7 §4.3: Canter's Circle Hypothesis (MARAUDER vs COMMUTER) & SDE
  - Pillar 7 §7: VECTOR_GEO_03 Golden Test Vector
  - Pillar 7 §8: ISO/IEC 17025:2017 & ENFSI 7-Tier Reporting Standards
"""

import pytest
import math
from backend.node.services.forensic.geoint.geographic_profiling_engine import (
    GeographicProfilingEngine,
    CrimeSitePoint,
    OffenderMobilityTypology,
    StandardDeviationalEllipse,
    CanterCircleResult,
    GeographicProfileResult,
)


@pytest.fixture
def engine():
    return GeographicProfilingEngine()


class TestGeographicProfilingEngine:

    def test_wgs84_vincenty_geodesic_distance(self, engine: GeographicProfilingEngine):
        """
        Validates WGS84 Vincenty ellipsoidal geodesic calculations against standard geodetic benchmarks (§4.2).
        """
        # Identical point distance should be exactly 0.0 m
        dist_zero = engine.vincenty_geodesic_distance_meters(51.5074, -0.1278, 51.5074, -0.1278)
        assert dist_zero == 0.0

        # London (51.5074 N, -0.1278 W) to Paris (48.8566 N, 2.3522 E) ~ 343.5 km (+- 1 km)
        dist_london_paris = engine.vincenty_geodesic_distance_meters(51.5074, -0.1278, 48.8566, 2.3522)
        assert 340000.0 <= dist_london_paris <= 347000.0

    def test_canter_circle_and_sde(self, engine: GeographicProfilingEngine):
        """
        Validates Canter's Circle diameter and Standard Deviational Ellipse (SDE) orientation (§4.3).
        """
        crimes = [
            CrimeSitePoint(site_id="C1", x_coord_km=2.0, y_coord_km=2.0),
            CrimeSitePoint(site_id="C2", x_coord_km=8.0, y_coord_km=2.0),
            CrimeSitePoint(site_id="C3", x_coord_km=5.0, y_coord_km=8.0),
        ]

        # 1. Canter circle with anchor inside triangle -> MARAUDER
        canter_marauder = engine.compute_canter_circle(crimes, predicted_anchor=(5.0, 4.0))
        assert canter_marauder.typology == OffenderMobilityTypology.MARAUDER
        assert canter_marauder.diameter_km >= 6.0

        # 2. Canter circle with anchor outside -> COMMUTER
        canter_commuter = engine.compute_canter_circle(crimes, predicted_anchor=(20.0, 20.0))
        assert canter_commuter.typology == OffenderMobilityTypology.COMMUTER

        # 3. Standard Deviational Ellipse
        sde = engine.compute_standard_deviational_ellipse(crimes)
        assert sde.center_x_km == 5.0
        assert sde.center_y_km == 4.0
        assert sde.sigma_x_km > 0.0
        assert sde.sigma_y_km > 0.0
        assert sde.area_sq_km > 0.0

    def test_golden_vector_geo_03_rossmo_profiling(self, engine: GeographicProfilingEngine):
        """
        Golden Benchmark Test: VECTOR_GEO_03 (Research Specification §7).

        Input Parameters:
          5 Serial Crime Incident GPS Coordinates in a 20.0 km x 20.0 km bounding sector:
            - C1 = (4.00, 12.00) km
            - C2 = (6.50, 14.20) km
            - C3 = (8.00, 9.50) km
            - C4 = (11.20, 13.00) km
            - C5 = (5.80, 8.10) km

          Model Parameters: Buffer radius B = 1.50 km, decay exponent f = 1.60,
          buffer penalty exponent g = 0.80, grid resolution = 0.10 km (200 x 200 = 40,000 cells).

        Expected Outputs:
          - Peak Probability Anchor Coordinate: (x0, y0) = (6.80 km, 11.40 km)
          - Top 5% Priority Search Polygon Area (S_5%): 14.20 sq km (out of 400.0 sq km total grid area)
          - Search Efficiency Index: SEI = (1 - 14.20 / 400.0) * 100% = 96.45%
          - Offender Mobility: MARAUDER
        """
        crimes = [
            CrimeSitePoint(site_id="C1", x_coord_km=4.00, y_coord_km=12.00),
            CrimeSitePoint(site_id="C2", x_coord_km=6.50, y_coord_km=14.20),
            CrimeSitePoint(site_id="C3", x_coord_km=8.00, y_coord_km=9.50),
            CrimeSitePoint(site_id="C4", x_coord_km=11.20, y_coord_km=13.00),
            CrimeSitePoint(site_id="C5", x_coord_km=5.80, y_coord_km=8.10),
        ]

        result = engine.compute_geographic_profile(
            crimes=crimes,
            case_id="CASE_SERIAL_2026",
            buffer_radius_km=1.50,
            decay_exponent_f=1.60,
            buffer_exponent_g=0.80,
            grid_bounds=(0.0, 20.0, 0.0, 20.0),
            grid_resolution_km=0.10,
        )

        # 1. Peak Probability Anchor Verification
        assert pytest.approx(result.peak_anchor_x_km, 1e-2) == 6.80
        assert pytest.approx(result.peak_anchor_y_km, 1e-2) == 11.40

        # 2. Priority Search Area & Search Efficiency Index Verification
        assert 13.50 <= result.top_5_percent_search_area_sq_km <= 15.00
        assert 96.00 <= result.search_efficiency_index_pct <= 97.00
        assert result.total_grid_area_sq_km == 400.0

        # 3. Offender Typology Verification
        assert result.canter_circle.typology == OffenderMobilityTypology.MARAUDER
        assert result.incident_count == 5

        # 4. Mandatory Prosecutor's Fallacy Shield Verification
        assert "PROSECUTOR'S FALLACY SHIELD" in result.prosecutors_fallacy_shield
        assert "ROSSMO GEOGRAPHIC PROFILING" in result.prosecutors_fallacy_shield

    def test_spatial_prosecutors_fallacy_shield(self, engine: GeographicProfilingEngine):
        """
        Validates ISO 17025 spatial disclaimer language and verbal likelihood scales (§8.2).
        """
        crimes = [
            CrimeSitePoint(site_id="C1", x_coord_km=5.0, y_coord_km=5.0),
            CrimeSitePoint(site_id="C2", x_coord_km=10.0, y_coord_km=10.0),
        ]
        res = engine.compute_geographic_profile(crimes=crimes)

        assert "Arama Verimliliği" in res.enfsi_verbal_statement_tr
        assert "Geographic profiling" in res.enfsi_verbal_statement_en
        assert len(res.probability_density_surface) > 0

    def test_fastapi_geographic_profile_endpoint(self):
        """
        Validates FastAPI endpoint POST /api/v1/forensic/geoint/geographic-profile.
        """
        from fastapi.testclient import TestClient
        from backend.app.main import app

        client = TestClient(app)
        payload = {
            "case_id": "CASE-GEO-2026-SERIAL",
            "crime_sites": [
                {"site_id": "C1", "x_coord_km": 4.00, "y_coord_km": 12.00, "weight": 1.0},
                {"site_id": "C2", "x_coord_km": 6.50, "y_coord_km": 14.20, "weight": 1.0},
                {"site_id": "C3", "x_coord_km": 8.00, "y_coord_km": 9.50, "weight": 1.0},
                {"site_id": "C4", "x_coord_km": 11.20, "y_coord_km": 13.00, "weight": 1.0},
                {"site_id": "C5", "x_coord_km": 5.80, "y_coord_km": 8.10, "weight": 1.0},
            ],
            "buffer_radius_km": 1.50,
            "decay_exponent_f": 1.60,
            "buffer_exponent_g": 0.80,
            "grid_bounds_km": [0.0, 20.0, 0.0, 20.0],
            "grid_resolution_km": 0.10,
        }

        response = client.post("/api/v1/forensic/geoint/geographic-profile", json=payload)
        assert response.status_code == 200
        data = response.json()

        assert data["case_id"] == "CASE-GEO-2026-SERIAL"
        assert data["incident_count"] == 5
        assert pytest.approx(data["peak_anchor_x_km"], 1e-2) == 6.80
        assert pytest.approx(data["peak_anchor_y_km"], 1e-2) == 11.40
        assert 13.50 <= data["top_5_percent_search_area_sq_km"] <= 15.00
        assert 96.00 <= data["search_efficiency_index_pct"] <= 97.00
        assert data["canter_typology"] == "MARAUDER"
        assert len(data["probability_density_surface"]) > 0
        assert "PROSECUTOR'S FALLACY SHIELD" in data["prosecutors_fallacy_shield"]
