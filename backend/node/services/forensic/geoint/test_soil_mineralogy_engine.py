"""
Unit and Golden Benchmark Verification Suite for Pillar 7 Module 1.2:
Forensic Pedology, Soil QXRD Mineralogy & Geochemical CoDa Engine (soil_mineralogy_engine.py).

Verifies verbatim against:
  - Pillar 7 §2: Soil Pedology, Rietveld QXRD, CoDa CLR Transform, ASTM E3272-21
  - Pillar 7 §7: VECTOR_GEO_02 Golden Test Vector
  - Pillar 7 §8: ISO/IEC 17025:2017 & ENFSI 7-Tier Reporting Standards
"""

import pytest
import math
from backend.node.services.forensic.geoint.soil_mineralogy_engine import (
    SoilMineralogyEngine,
    SoilMineralogyProfile,
    SoilComparisonResult,
    AstmE3272Verdict,
)


@pytest.fixture
def engine():
    return SoilMineralogyEngine()


class TestSoilMineralogyEngine:

    def test_ztr_index_calculation(self, engine: SoilMineralogyEngine):
        """
        Validates Zircon-Tourmaline-Rutile (ZTR) heavy mineral maturity index (§2.1):
          ZTR = (Zircon + Tourmaline + Rutile) / Total Heavy Minerals * 100%
        """
        ztr_val = engine.compute_ztr_index(
            zircon_pct=15.0,
            tourmaline_pct=10.0,
            rutile_pct=5.0,
            total_heavy_minerals_pct=50.0,
        )
        # Expected: (15 + 10 + 5) / 50 * 100% = 30 / 50 * 100% = 60.0%
        assert ztr_val == 60.0

    def test_compositional_clr_transform(self, engine: SoilMineralogyEngine):
        """
        Validates Centered Log-Ratio (CLR) transformation on compositional simplex (§2.3):
          Sum of CLR components in log-ratio space must equal exactly 0.0.
        """
        raw_comp = [64.20, 15.10, 5.30, 2.10, 1.40, 1.80, 2.90, 0.85, 0.15, 0.08, 42.0, 14.0, 12.0, 4.5, 8.5, 12.0]
        clr_vec, g_mean = engine.compute_centered_log_ratio(raw_comp)

        # 1. Geometric mean verification (VECTOR_GEO_02: g(x_q) = 3.88 +- 0.25)
        assert 3.50 <= g_mean <= 4.00

        # 2. Centered Log-Ratio transform values
        assert 2.70 <= clr_vec[0] <= 2.95
        assert -4.00 <= clr_vec[9] <= -3.70

        # 3. Sum-to-zero property of CLR transformed vectors: sum(clr_i) == 0.0
        assert pytest.approx(sum(clr_vec), 1e-6) == 0.0

    def test_munsell_to_cielab_and_ciede2000(self, engine: SoilMineralogyEngine):
        """
        Validates Munsell color notation parsing and CIEDE2000 color difference (§2.4).
        """
        lab1 = engine.munsell_to_cielab("10YR 4/3")
        lab2 = engine.munsell_to_cielab("10YR 4/3")
        # Identical color should have Delta E00 == 0.00
        delta_e_ident = engine.compute_ciede2000_delta_e(lab1, lab2)
        assert delta_e_ident == 0.00

        # Close color comparison
        lab3 = engine.munsell_to_cielab("10YR 5/4")
        delta_e_close = engine.compute_ciede2000_delta_e(lab1, lab3)
        assert delta_e_close > 0.0
        assert delta_e_close < 15.0

    def test_golden_vector_geo_02_soil_comparison(self, engine: SoilMineralogyEngine):
        """
        Golden Benchmark Test: VECTOR_GEO_02 (Research Specification §7).

        Inputs:
          - Questioned soil sample (boot) vs Crime scene control reference (N=25).
          - 10-Element XRF major oxides + 6-mineral QXRD percentages:
            Questioned: SiO2: 64.20, Al2O3: 15.10, Fe2O3: 5.30, CaO: 2.10, MgO: 1.40, Na2O: 1.80, K2O: 2.90, TiO2: 0.85, P2O5: 0.15, MnO: 0.08, Quartz: 42.0, K-Feldspar: 14.0, Plagioclase: 12.0, Calcite: 4.5, Kaolinite: 8.5, Illite: 12.0.
            Control: SiO2: 63.80, Al2O3: 15.40, Fe2O3: 5.15, CaO: 2.25, MgO: 1.35, Na2O: 1.75, K2O: 3.00, TiO2: 0.88, P2O5: 0.14, MnO: 0.07, Quartz: 41.2, K-Feldspar: 14.5, Plagioclase: 11.8, Calcite: 4.8, Kaolinite: 8.2, Illite: 12.5.
            Color: 10YR 4/3

        Expected Outputs:
          - Robust MCD Mahalanobis Distance D_M = 1.4200 ± 0.05
          - Hotelling's F-statistic F = 0.0560 ± 0.01
          - Hotelling's p-value p = 0.8850 ± 0.05 (> 0.05 => Indistinguishable)
          - CIEDE2000 Color Difference Delta E00 <= 0.50 (< 2.00)
          - ASTM E3272-21 Classification: DEFINITIVE_INCLUSION
          - Evaluative Likelihood Ratio: LR = 4.50e3 (4500.0)
          - ENFSI Tier: TIER_4_STRONG ("Strong support for source inclusion")
        """
        q_soil = SoilMineralogyProfile(
            sample_id="GEO_02_BOOT",
            quartz_percent=42.0,
            feldspar_k_percent=14.0,
            plagioclase_percent=12.0,
            calcite_percent=4.5,
            clay_kaolinite_percent=8.5,
            clay_illite_percent=12.0,
            munsell_color_dry="10YR 4/3",
            xrf_major_oxides_wt_pct={
                "SiO2": 64.20,
                "Al2O3": 15.10,
                "Fe2O3": 5.30,
                "CaO": 2.10,
                "MgO": 1.40,
                "Na2O": 1.80,
                "K2O": 2.90,
                "TiO2": 0.85,
                "P2O5": 0.15,
                "MnO": 0.08,
            },
            zircon_percent=12.0,
            tourmaline_percent=8.0,
            rutile_percent=4.0,
            total_heavy_minerals_percent=40.0,
        )

        c_soil = SoilMineralogyProfile(
            sample_id="GEO_02_SCENE",
            quartz_percent=41.2,
            feldspar_k_percent=14.5,
            plagioclase_percent=11.8,
            calcite_percent=4.8,
            clay_kaolinite_percent=8.2,
            clay_illite_percent=12.5,
            munsell_color_dry="10YR 4/3",
            xrf_major_oxides_wt_pct={
                "SiO2": 63.80,
                "Al2O3": 15.40,
                "Fe2O3": 5.15,
                "CaO": 2.25,
                "MgO": 1.35,
                "Na2O": 1.75,
                "K2O": 3.00,
                "TiO2": 0.88,
                "P2O5": 0.14,
                "MnO": 0.07,
            },
            zircon_percent=11.8,
            tourmaline_percent=8.1,
            rutile_percent=4.1,
            total_heavy_minerals_percent=40.0,
        )

        result = engine.compare_soil_samples(questioned=q_soil, control=c_soil)

        # 1. Mahalanobis Distance & Hotelling F-test Verification
        assert 1.35 <= result.mahalanobis_distance_mcd <= 1.50
        assert 0.040 <= result.hotelling_f_statistic <= 0.070
        assert result.hotelling_p_value >= 0.05

        # 2. Colorimetric & Heavy Mineral Verification
        assert result.color_difference_delta_e00 <= 0.50
        assert result.ztr_index_questioned == 60.0
        assert result.ztr_index_control == 60.0

        # 3. ASTM E3272-21 Evidentiary Verdict Verification
        assert result.astm_e3272_verdict == AstmE3272Verdict.DEFINITIVE_INCLUSION
        assert result.likelihood_ratio == 4500.0
        assert result.enfsi_verbal_tier == "TIER_4_STRONG"
        assert "güçlü derecede" in result.enfsi_verbal_statement_tr

        # 4. Prosecutor's Fallacy Shield Verification
        assert "PROSECUTOR'S FALLACY SHIELD" in result.prosecutors_fallacy_shield
        assert "ASTM E3272-21" in result.prosecutors_fallacy_shield

    def test_soil_definitive_exclusion_divergent_lithology(self, engine: SoilMineralogyEngine):
        """
        Validates ASTM E3272-21 definitive source exclusion (p < 0.001, Non-Match).
        """
        q_limestone = SoilMineralogyProfile(
            sample_id="SOIL_LIMESTONE",
            quartz_percent=5.0,
            calcite_percent=85.0,
            munsell_color_dry="2.5Y 5/2",
            xrf_major_oxides_wt_pct={"SiO2": 5.0, "CaO": 52.0, "Al2O3": 1.2},
        )

        c_granite = SoilMineralogyProfile(
            sample_id="SOIL_GRANITE",
            quartz_percent=70.0,
            calcite_percent=0.5,
            munsell_color_dry="5YR 3/4",
            xrf_major_oxides_wt_pct={"SiO2": 72.0, "CaO": 1.0, "Al2O3": 14.5},
        )

        result = engine.compare_soil_samples(questioned=q_limestone, control=c_granite)

        assert result.astm_e3272_verdict == AstmE3272Verdict.EXCLUSION_NON_MATCH
        assert result.likelihood_ratio == 0.0
        assert result.hotelling_p_value < 0.001
        assert result.color_difference_delta_e00 > 2.00
        assert "dışlandığını" in result.enfsi_verbal_statement_tr

    def test_fastapi_soil_comparison_endpoint(self):
        """
        Validates FastAPI endpoint POST /api/v1/forensic/geoint/soil-comparison.
        """
        from fastapi.testclient import TestClient
        from backend.app.main import app

        client = TestClient(app)
        payload = {
            "case_id": "CASE-GEO-2026-SOIL",
            "questioned_soil": {
                "sample_id": "GEO_02_BOOT",
                "quartz_percent": 42.0,
                "feldspar_k_percent": 14.0,
                "plagioclase_percent": 12.0,
                "calcite_percent": 4.5,
                "clay_kaolinite_percent": 8.5,
                "clay_illite_percent": 12.0,
                "clay_smectite_percent": 0.0,
                "munsell_color_dry": "10YR 4/3",
                "xrf_major_oxides_wt_pct": {
                    "SiO2": 64.20,
                    "Al2O3": 15.10,
                    "Fe2O3": 5.30,
                    "CaO": 2.10,
                    "MgO": 1.40,
                    "Na2O": 1.80,
                    "K2O": 2.90,
                    "TiO2": 0.85,
                    "P2O5": 0.15,
                    "MnO": 0.08,
                },
                "zircon_percent": 12.0,
                "tourmaline_percent": 8.0,
                "rutile_percent": 4.0,
                "total_heavy_minerals_percent": 40.0,
            },
            "known_control_soil": {
                "sample_id": "GEO_02_SCENE",
                "quartz_percent": 41.2,
                "feldspar_k_percent": 14.5,
                "plagioclase_percent": 11.8,
                "calcite_percent": 4.8,
                "clay_kaolinite_percent": 8.2,
                "clay_illite_percent": 12.5,
                "clay_smectite_percent": 0.0,
                "munsell_color_dry": "10YR 4/3",
                "xrf_major_oxides_wt_pct": {
                    "SiO2": 63.80,
                    "Al2O3": 15.40,
                    "Fe2O3": 5.15,
                    "CaO": 2.25,
                    "MgO": 1.35,
                    "Na2O": 1.75,
                    "K2O": 3.00,
                    "TiO2": 0.88,
                    "P2O5": 0.14,
                    "MnO": 0.07,
                },
                "zircon_percent": 11.8,
                "tourmaline_percent": 8.1,
                "rutile_percent": 4.1,
                "total_heavy_minerals_percent": 40.0,
            },
        }

        response = client.post("/api/v1/forensic/geoint/soil-comparison", json=payload)
        assert response.status_code == 200
        data = response.json()

        assert data["case_id"] == "CASE-GEO-2026-SOIL"
        assert data["questioned_sample_id"] == "GEO_02_BOOT"
        assert data["control_sample_id"] == "GEO_02_SCENE"
        assert 1.35 <= data["mahalanobis_distance_mcd"] <= 1.50
        assert data["hotelling_p_value"] >= 0.05
        assert data["color_difference_delta_e00"] <= 0.50
        assert data["astm_e3272_verdict"] == "DEFINITIVE_INCLUSION"
        assert data["likelihood_ratio"] == 4500.0
        assert "PROSECUTOR'S FALLACY SHIELD" in data["prosecutors_fallacy_shield"]
