"""
Unit and Golden Benchmark Verification Suite for Pillar 7 Module 1.1:
Multi-Isotope Biogeochemical Provenancing Engine (isoscape_provenance_engine.py).

Verifies verbatim against:
  - Pillar 7 §1: Isotope Kinematics, Tissue Fractionations, and Bataille Mixing
  - Pillar 7 §7: VECTOR_GEO_01 Golden Test Vector
  - Pillar 7 §8: ISO/IEC 17025:2017 & ENFSI 7-Tier Reporting Standards
"""

import pytest
import math
from backend.node.services.forensic.geoint.isoscape_provenance_engine import (
    IsoscapeProvenanceEngine,
    IsotopeObservation,
    TissueType,
    CandidateRegion,
    DEFAULT_REFERENCE_REGIONS,
)


@pytest.fixture
def engine():
    return IsoscapeProvenanceEngine()


class TestIsoscapeProvenanceEngine:

    def test_craig_gmwl_and_deuterium_excess(self, engine: IsoscapeProvenanceEngine):
        """
        Validates Craig GMWL (d2H = 8.0 * d18O + 10.0) and Deuterium Excess d = d2H - 8.0 * d18O.
        """
        d18o = -8.50
        expected_d2h = 8.0 * (-8.50) + 10.0  # -68.0 + 10.0 = -58.00 permil
        calculated_d2h = engine.compute_craig_gmwl(d18o)
        assert pytest.approx(calculated_d2h, 1e-4) == expected_d2h

        # Deuterium excess on GMWL should equal exactly +10.0 permil
        d_excess_gmwl = engine.compute_deuterium_excess(calculated_d2h, d18o)
        assert pytest.approx(d_excess_gmwl, 1e-4) == 10.0

        # Custom d2H of -80.0 permil with d18O of -8.50 permil
        # d = -80.0 - 8.0 * (-8.50) = -80.0 + 68.0 = -12.0 permil
        d_excess_custom = engine.compute_deuterium_excess(-80.0, -8.50)
        assert pytest.approx(d_excess_custom, 1e-4) == -12.0

    def test_terzer_wassenaar_precipitation_model(self, engine: IsoscapeProvenanceEngine):
        """
        Validates Terzer-Wassenaar global precipitation regression (§1.1).
        """
        # Test coordinates: Lat 46.85 deg N, Elevation 1250 m, Coast distance 450 km
        d18o_pred = engine.predict_precipitation_d18o(
            latitude=46.850,
            elevation_m=1250.0,
            coast_distance_km=450.0,
        )
        # Verify negative d18O consistent with alpine high-altitude lapse rate (-17.37 permil)
        assert -18.5 < d18o_pred < -16.0

    def test_tooth_enamel_daux_chenery_calibration(self, engine: IsoscapeProvenanceEngine):
        """
        Validates tooth enamel bioapatite direct conversion (§1.2):
          d18O_water = 1.590 * d18O_carb - 48.634 (Chenery & Daux composite).
        """
        d18o_carb = +25.40
        d18o_water, sigma = engine.convert_enamel_carbonate_to_water(d18o_carb)

        # Expected: 1.590 * 25.40 - 48.634 = 40.3860 - 48.6340 = -8.2480 permil
        assert pytest.approx(d18o_water, 1e-4) == -8.2480
        assert sigma == 0.60

        # Test phosphate conversion
        d18o_phos = +16.54
        d18o_w_phos, sig_phos = engine.convert_enamel_phosphate_to_water(d18o_phos)
        # Expected: 1.540 * 16.54 - 33.720 = 25.4716 - 33.720 = -8.2484 permil
        assert pytest.approx(d18o_w_phos, 1e-2) == -8.25
        assert sig_phos == 0.55

    def test_hair_keratin_ehleringer_calibration(self, engine: IsoscapeProvenanceEngine):
        """
        Validates scalp hair keratin regressions (§1.2, Ehleringer et al.):
          d2H_water = (d2H_hair + 26.0) / 0.91
          d18O_water = (d18O_hair - 12.8) / 0.35
        """
        d2h_hair = -78.40
        d18o_hair = +11.80
        d18o_w, d18o_sig, d2h_w, d2h_sig = engine.convert_hair_keratin_to_water(
            delta_2h_hair=d2h_hair, delta_18o_hair=d18o_hair
        )

        # Expected: (-78.40 + 26.0) / 0.91 = -52.40 / 0.91 = -57.5824 permil
        assert pytest.approx(d2h_w, 1e-4) == -57.5824
        assert d2h_sig == 3.50

        # Expected: (11.80 - 12.80) / 0.35 = -1.00 / 0.35 = -2.8571 permil
        assert pytest.approx(d18o_w, 1e-4) == -2.8571
        assert d18o_sig == 0.85

    def test_bataille_strontium_mixing_model(self, engine: IsoscapeProvenanceEngine):
        """
        Validates Bataille multi-source bioavailable strontium mixing (§1.3):
          87Sr/86Sr_bio = fw * 87Sr/86Sr_rock + fp * 87Sr/86Sr_precip + fm * 0.70918
        """
        sr_rock = 0.70820
        sr_precip = 0.70950
        fw = 0.70
        fp = 0.30

        sr_bio = engine.compute_bataille_sr_bioavailable(
            sr_bedrock=sr_rock,
            sr_precip=sr_precip,
            fraction_weathering=fw,
            fraction_precip=fp,
            fraction_marine=0.0,
        )

        expected_sr = (0.70 * 0.70820) + (0.30 * 0.70950)  # 0.49574 + 0.21285 = 0.70859
        assert pytest.approx(sr_bio, 1e-5) == expected_sr

    def test_golden_vector_geo_01_multi_isotope_provenancing(
        self, engine: IsoscapeProvenanceEngine
    ):
        """
        Golden Benchmark Test: VECTOR_GEO_01 (Research Specification §7).

        Inputs:
          - Human scalp hair keratin: d2H_hair = -78.40 ‰, d18O_hair = +11.80 ‰
          - Human tooth enamel bioapatite: 87Sr/86Sr = 0.70882, d18O_carb = +25.40 ‰

        Expected Outputs:
          - Inferred drinking water d18O = -8.25 to -8.50 ± 0.60 ‰
          - Resolved geographic centroid in Swiss Prealps (Lat ~46.85°N, Lon ~8.23°E)
          - 95% spatial confidence radius R_95% in range 50.0 to 120.0 km
          - Likelihood Ratio LR > 10,000 (Very Strong support for source inclusion)
          - ENFSI Tier 5 ("VERY STRONG")
        """
        obs_enamel = IsotopeObservation(
            sample_id="GEO_01_TOOTH",
            tissue_type=TissueType.TOOTH_ENAMEL_CARBONATE,
            delta_18o_permil=25.40,
            sr_87_86_ratio=0.70882,
        )

        obs_hair = IsotopeObservation(
            sample_id="GEO_01_HAIR",
            tissue_type=TissueType.SCALP_HAIR_KERATIN,
            delta_18o_permil=11.80,
            delta_2h_permil=-78.40,
        )

        result = engine.solve_spatial_provenance(
            primary_obs=obs_enamel,
            secondary_obs=obs_hair,
        )

        # 1. Inferred Water Verification
        assert -8.55 <= result.inferred_drinking_water_d18o <= -8.20
        assert result.inferred_drinking_water_d18o_sigma == 0.60
        assert result.inferred_drinking_water_d2h is not None
        assert -58.0 <= result.inferred_drinking_water_d2h <= -57.0

        # 2. Resolved Geographic Centroid Verification (Swiss Prealps vicinity)
        assert 46.5 <= result.resolved_centroid_lat <= 47.5
        assert 7.8 <= result.resolved_centroid_lon <= 8.8
        assert "Swiss Prealps" in result.primary_candidate_region

        # 3. 95% Confidence Radius Verification
        assert 50.0 <= result.confidence_radius_95_km <= 120.0

        # 4. Likelihood Ratio & Evaluative Tier Verification
        assert result.likelihood_ratio >= 10000.0
        assert result.enfsi_verbal_tier in ("TIER_5_VERY_STRONG", "TIER_6_EXTREMELY_STRONG")
        assert "fevkalade güçlü" in result.enfsi_verbal_statement_tr or "çok güçlü" in result.enfsi_verbal_statement_tr

        # 5. Prosecutor's Fallacy Shield Verification
        assert "PROSECUTOR'S FALLACY SHIELD" in result.prosecutors_fallacy_shield
        assert "ISO/IEC 17025:2017" in result.prosecutors_fallacy_shield

    def test_enfsi_verbal_scale_thresholds(self, engine: IsoscapeProvenanceEngine):
        """
        Validates all 7 tiers of the ENFSI verbal likelihood scale in English and Turkish (§8.1).
        """
        tier_ext, en_ext, tr_ext = engine.get_enfsi_verbal_scale(1500000.0)
        assert tier_ext == "TIER_6_EXTREMELY_STRONG"
        assert "fevkalade güçlü" in tr_ext

        tier_vstrong, en_vstrong, tr_vstrong = engine.get_enfsi_verbal_scale(50000.0)
        assert tier_vstrong == "TIER_5_VERY_STRONG"
        assert "çok güçlü" in tr_vstrong

        tier_strong, en_strong, tr_strong = engine.get_enfsi_verbal_scale(5000.0)
        assert tier_strong == "TIER_4_STRONG"
        assert "güçlü derecede" in tr_strong

        tier_modstr, en_modstr, tr_modstr = engine.get_enfsi_verbal_scale(500.0)
        assert tier_modstr == "TIER_3_MODERATELY_STRONG"
        assert "orta-güçlü" in tr_modstr

        tier_mod, en_mod, tr_mod = engine.get_enfsi_verbal_scale(50.0)
        assert tier_mod == "TIER_2_MODERATE"
        assert "orta derecede" in tr_mod

        tier_weak, en_weak, tr_weak = engine.get_enfsi_verbal_scale(5.0)
        assert tier_weak == "TIER_1_WEAK"
        assert "zayıf derecede" in tr_weak

        tier_neutral, en_neutral, tr_neutral = engine.get_enfsi_verbal_scale(0.8)
        assert tier_neutral == "TIER_7_NEUTRAL"
        assert "nötrdür" in tr_neutral

    def test_fastapi_geoint_isoscape_endpoint(self):
        """
        Validates FastAPI endpoint POST /api/v1/forensic/geoint/isoscape-provenance.
        """
        from fastapi.testclient import TestClient
        from backend.app.main import app

        client = TestClient(app)
        payload = {
            "case_id": "CASE-GEO-2026-CH",
            "sample_id": "GEO_01_TOOTH",
            "primary_measurements": {
                "sample_tissue": "TOOTH_ENAMEL_CARBONATE",
                "delta_18o_permil": 25.40,
                "sr_87_86_ratio": 0.70882,
            },
            "secondary_measurements": {
                "sample_tissue": "SCALP_HAIR_KERATIN",
                "delta_18o_permil": 11.80,
                "delta_2h_permil": -78.40,
            },
        }

        response = client.post("/api/v1/forensic/geoint/isoscape-provenance", json=payload)
        assert response.status_code == 200
        data = response.json()

        assert data["case_id"] == "CASE-GEO-2026-CH"
        assert data["sample_id"] == "GEO_01_TOOTH"
        assert -8.55 <= data["inferred_drinking_water_d18o"] <= -8.20
        assert data["inferred_drinking_water_d18o_sigma"] == 0.60
        assert -58.0 <= data["inferred_drinking_water_d2h"] <= -57.0
        assert data["measured_sr_87_86"] == 0.70882
        assert "Swiss Prealps" in data["primary_candidate_region"]
        assert 46.5 <= data["resolved_centroid_lat"] <= 47.5
        assert 7.8 <= data["resolved_centroid_lon"] <= 8.8
        assert 50.0 <= data["confidence_radius_95_km"] <= 120.0
        assert data["likelihood_ratio"] >= 10000.0
        assert data["enfsi_verbal_tier"] in ("TIER_5_VERY_STRONG", "TIER_6_EXTREMELY_STRONG")
        assert len(data["top_candidate_regions"]) >= 1
        assert "PROSECUTOR'S FALLACY SHIELD" in data["prosecutors_fallacy_shield"]
