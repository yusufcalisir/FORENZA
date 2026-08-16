"""
Unit & Integration Tests for FORENZA Forensic Entomology Engine — Module 23.

Tests verbatim from Pillar 5 Research §3 & §6:
  - §3.1 Accumulated Thermal Energy Models (ADD / ADH)
  - §3.2 Dipteran Species Calibration Parameters (*L. sericata*, *C. vicina*, *C. albiceps*, *P. regina*)
  - §3.2 Larval Mass Thermal Self-Heating Correction (+1.5°C to +3.5°C)

Golden Benchmarks:
  - VECTOR_23_ENTO_A through H
"""

import pytest
from typing import List, Dict, Any
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.physical.entomology_engine import (
    ForensicEntomologyEngine,
    DIPTERAN_SPECIES_DATABASE,
)
from app.api.physical_routes import router as physical_router

_app = FastAPI()
_app.include_router(physical_router, prefix="/api/v1")
client = TestClient(_app)

engine = ForensicEntomologyEngine()


# ── VECTOR_23_ENTO_A — Lucilia sericata 3rd Instar Feeding (1254.5 ADH) ────────

class TestVector23EntoA:
    """Verifies Lucilia sericata 3rd Instar Feeding stage ADH requirement (1254.5 ADH)."""

    def test_lucilia_sericata_3rd_instar_feeding(self):
        stage_adh = engine.calculate_adh_for_stage("Lucilia sericata", "3rd Instar Feeding")
        assert stage_adh == 1254.5

        # Create constant 20°C temperature profile (T - T_base = 20 - 9 = 11 ADH/hour)
        # Expected hours: 1254.5 / 11 = 114.045 hours
        temps = [{"temperature_c": 20.0} for _ in range(120)]
        res = engine.estimate_pmi_min(
            species_name="Lucilia sericata",
            development_stage="3rd Instar Feeding",
            hourly_temperatures=temps,
            delta_t_mass=0.0
        )

        assert res["is_target_adh_satisfied"] is True
        assert abs(res["pmi_min_hours"] - (1254.5 / 11.0)) < 0.1
        assert "EAFE / NAFEA" in res["prosecutors_fallacy_shield"]


# ── VECTOR_23_ENTO_B — Calliphora vicina Cold-Adapted (T_base = 3.0°C) ─────────

class TestVector23EntoB:
    """Verifies Calliphora vicina baseline of 3.0°C and Egg stage 450.0 ADH."""

    def test_calliphora_vicina_cold_adaptation(self):
        info = engine.get_species_info("Calliphora vicina")
        assert info["t_base"] == 3.0
        assert info["stages_adh"]["Egg"] == 450.0

        # At 8°C (T - T_base = 8 - 3 = 5 ADH/hour), 450 ADH requires exactly 90 hours
        temps = [{"temperature_c": 8.0} for _ in range(100)]
        res = engine.estimate_pmi_min(
            species_name="Calliphora vicina",
            development_stage="Egg",
            hourly_temperatures=temps,
        )

        assert res["is_target_adh_satisfied"] is True
        assert abs(res["pmi_min_hours"] - 90.0) < 0.1
        assert abs(res["pmi_min_days"] - 3.75) < 0.05


# ── VECTOR_23_ENTO_C — Below-Threshold Temperature Dormancy ───────────────────

class TestVector23EntoC:
    """Verifies temperatures below T_base yield 0 ADH increment."""

    def test_below_threshold_zero_adh(self):
        # L. sericata T_base is 9.0°C. Feed 5°C temperatures.
        temps = [{"temperature_c": 5.0} for _ in range(50)]
        res = engine.estimate_pmi_min(
            species_name="Lucilia sericata",
            development_stage="Egg",
            hourly_temperatures=temps,
        )

        assert res["accumulated_adh"] == 0.0
        assert res["is_target_adh_satisfied"] is False


# ── VECTOR_23_ENTO_D — Larval Mass Metabolic Self-Heating Correction ─────────

class TestVector23EntoD:
    """Verifies delta_t_mass (+2.5°C) accelerates development and reduces estimated PMI hours."""

    def test_larval_mass_self_heating_acceleration(self):
        temps = [{"temperature_c": 19.0} for _ in range(150)]

        # Without mass heating (T_eff = 19°C -> 10 ADH/h)
        res_no_mass = engine.estimate_pmi_min(
            species_name="Lucilia sericata",
            development_stage="2nd Instar",  # 800 ADH -> 80 hours
            hourly_temperatures=temps,
            delta_t_mass=0.0
        )

        # With +2.5°C mass heating (T_eff = 21.5°C -> 12.5 ADH/h -> 64 hours)
        res_with_mass = engine.estimate_pmi_min(
            species_name="Lucilia sericata",
            development_stage="2nd Instar",
            hourly_temperatures=temps,
            delta_t_mass=2.5
        )

        assert res_no_mass["pmi_min_hours"] > res_with_mass["pmi_min_hours"]
        assert abs(res_with_mass["pmi_min_hours"] - (800.0 / 12.5)) < 0.1


# ── VECTOR_23_ENTO_E — Calendar Timestamp Back-Projection ─────────────────────

class TestVector23EntoE:
    """Verifies colonisation timestamp calculation from ISO sampling time."""

    def test_colonisation_timestamp_calculation(self):
        temps = [{"temperature_c": 29.0} for _ in range(30)]  # 29 - 9 = 20 ADH/h
        # L. sericata Egg = 240 ADH -> exactly 12 hours
        res = engine.estimate_pmi_min(
            species_name="Lucilia sericata",
            development_stage="Egg",
            hourly_temperatures=temps,
            sampling_time_iso="2026-08-16T15:00:00Z"
        )

        assert res["is_target_adh_satisfied"] is True
        assert abs(res["pmi_min_hours"] - 12.0) < 0.1
        assert res["colonisation_timestamp"] is not None
        assert "2026-08-16T03:00:00" in res["colonisation_timestamp"]


# ── VECTOR_23_ENTO_F — Invalid Species / Stage Validation ─────────────────────

class TestVector23EntoF:
    """Verifies rejection of unsupported species or development stages."""

    def test_invalid_species_raises(self):
        with pytest.raises(ValueError, match="Unsupported species"):
            engine.calculate_adh_for_stage("Musca domestica", "Egg")

    def test_invalid_stage_raises(self):
        with pytest.raises(ValueError, match="Unknown development stage"):
            engine.calculate_adh_for_stage("Lucilia sericata", "Super Instar")


# ── VECTOR_23_ENTO_G — Insufficient Historical Weather Data ───────────────────

class TestVector23EntoG:
    """Verifies proper warning when weather history is shorter than required ADH."""

    def test_insufficient_weather_history(self):
        # Need 5000 ADH for Pupae, but only give 5 hours at 20°C (55 ADH)
        temps = [{"temperature_c": 20.0} for _ in range(5)]
        res = engine.estimate_pmi_min(
            species_name="Lucilia sericata",
            development_stage="Pupae",
            hourly_temperatures=temps,
        )

        assert res["is_target_adh_satisfied"] is False
        assert "warning" in res
        assert res["accumulated_adh"] == 55.0


# ── VECTOR_23_ENTO_H — FastAPI Endpoint Integration Tests ─────────────────────

class TestVector23EntoH:
    """Verifies FastAPI /forensic/physical/entomology-pmi-estimation endpoint."""

    def test_api_entomology_endpoint(self):
        payload = {
            "species_name": "Chrysomya albiceps",
            "development_stage": "1st Instar",
            "hourly_temperatures": [
                {"hour_index": i, "temperature_c": 25.2}
                for i in range(60)  # T_base = 10.2 -> 15.0 ADH/h. 1st Instar = 740 ADH -> ~49.3 hours
            ],
            "delta_t_mass": 0.0,
            "sampling_time_iso": "2026-08-16T12:00:00Z"
        }
        resp = client.post("/api/v1/forensic/physical/entomology-pmi-estimation", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["species"] == "Chrysomya albiceps"
        assert data["target_adh"] == 740.0
        assert data["is_target_adh_satisfied"] is True
        assert abs(data["pmi_min_hours"] - (740.0 / 15.0)) < 0.2
