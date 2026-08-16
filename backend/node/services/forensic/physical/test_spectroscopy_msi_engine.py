r"""
Unit & Integration Tests for FORENZA Trace Spectroscopy & MSI Engine — Module 24.

Tests verbatim from Pillar 5 Research §4 & §6:
  - §4.1 Targeted Multispectral Wavelength Bands (365nm UV-A, 415nm Soret, 450nm Blue, 850nm NIR)
  - §4.2 ATR-FTIR & Raman Trace Spectral Matching (Hit Quality Index — HQI)

Golden Benchmarks:
  - VECTOR_24_SPEC_A through H
"""

import pytest
import math
from typing import List, Dict, Any
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.physical.spectroscopy_msi_engine import (
    TraceSpectroscopyMsiEngine,
    FIBER_REFERENCE_LIBRARY,
    MSI_WAVELENGTH_BANDS,
)
from app.api.physical_routes import router as physical_router

_app = FastAPI()
_app.include_router(physical_router, prefix="/api/v1")
client = TestClient(_app)

engine = TraceSpectroscopyMsiEngine()


# ── VECTOR_24_SPEC_A — Polyester (PET) HQI Match (>= 95%) ─────────────────────

class TestVector24SpecA:
    """Verifies Polyester (PET) synthetic spectrum matches reference library with HQI >= 95%."""

    def test_polyester_hqi_match(self):
        # Generate synthetic polyester spectrum with minor noise
        ref_lib = engine._generate_default_reference_vectors(100)
        pet_ref = ref_lib["Polyester"]
        sample_pet = [val + 0.01 for val in pet_ref]  # Minor baseline noise

        hqi = engine.compute_hqi(sample_pet, pet_ref)
        assert hqi >= 95.0

        match_res = engine.match_trace_spectrum(sample_pet)
        assert match_res["top_match"]["material_name"] == "Polyester"
        assert match_res["top_match"]["classification"] == "POSITIVE_SPECTRAL_MATCH"
        assert "SWGMAT" in match_res["prosecutors_fallacy_shield"]


# ── VECTOR_24_SPEC_B — Nylon-6,6 Amide Peaks Match (>= 95%) ──────────────────

class TestVector24SpecB:
    """Verifies Nylon-6,6 Amide I/II spectrum matches with HQI >= 95%."""

    def test_nylon_hqi_match(self):
        ref_lib = engine._generate_default_reference_vectors(100)
        nylon_ref = ref_lib["Nylon-6,6"]
        sample_nylon = [val * 1.05 for val in nylon_ref]  # Scaling amplitude variation

        hqi = engine.compute_hqi(sample_nylon, nylon_ref)
        assert hqi >= 99.0

        match_res = engine.match_trace_spectrum(sample_nylon)
        assert match_res["top_match"]["material_name"] == "Nylon-6,6"
        assert match_res["top_match"]["classification"] == "POSITIVE_SPECTRAL_MATCH"


# ── VECTOR_24_SPEC_C — Acrylic PAN Nitrile Peak Match (>= 95%) ────────────────

class TestVector24SpecC:
    """Verifies Acrylic PAN nitrile peak spectrum matches with HQI >= 95%."""

    def test_acrylic_hqi_match(self):
        ref_lib = engine._generate_default_reference_vectors(100)
        acrylic_ref = ref_lib["Acrylic"]
        sample_acrylic = [val for val in acrylic_ref]

        match_res = engine.match_trace_spectrum(sample_acrylic)
        assert match_res["top_match"]["material_name"] == "Acrylic"
        assert match_res["top_match"]["hqi_score_percent"] == 100.0


# ── VECTOR_24_SPEC_D — Degraded / Weathered Trace Spectrum (75% <= HQI < 90%) ─

class TestVector24SpecD:
    """Verifies weathered/contaminated spectrum yields PROBABLE_MATCH_DEGRADED."""

    def test_degraded_spectrum_classification(self):
        ref_lib = engine._generate_default_reference_vectors(100)
        cotton_ref = ref_lib["Cotton"]
        # Add high background noise reducing correlation
        noisy_cotton = [val + 0.35 for val in cotton_ref]

        hqi = engine.compute_hqi(noisy_cotton, cotton_ref)
        assert 75.0 <= hqi < 90.0

        match_res = engine.match_trace_spectrum(noisy_cotton)
        assert match_res["top_match"]["material_name"] == "Cotton"
        assert match_res["top_match"]["classification"] == "PROBABLE_MATCH_DEGRADED"


# ── VECTOR_24_SPEC_E — Dissimilar Material Exclusion (HQI < 50%) ──────────────

class TestVector24SpecE:
    """Verifies dissimilar polymer spectrum is excluded (HQI < 50%)."""

    def test_dissimilar_polymer_exclusion(self):
        ref_lib = engine._generate_default_reference_vectors(100)
        acrylic_ref = ref_lib["Acrylic"]
        wool_ref = ref_lib["Wool"]

        hqi = engine.compute_hqi(acrylic_ref, wool_ref)
        assert hqi < 50.0


# ── VECTOR_24_SPEC_F — Zero Energy / Dimension Mismatch Validation ───────────

class TestVector24SpecF:
    """Verifies input validation on zero energy vectors and dimension mismatch."""

    def test_zero_vector_raises(self):
        zero_vec = [0.0] * 50
        ref_vec = [1.0] * 50
        with pytest.raises(ValueError, match="Zero-energy spectrum"):
            engine.compute_hqi(zero_vec, ref_vec)

    def test_dimension_mismatch_raises(self):
        vec_a = [1.0] * 50
        vec_b = [1.0] * 60
        with pytest.raises(ValueError, match="Dimension mismatch"):
            engine.compute_hqi(vec_a, vec_b)


# ── VECTOR_24_SPEC_G — Multispectral Optical Band Simulation ──────────────────

class TestVector24SpecG:
    """Verifies 4-band MSI contrast mechanisms across UV-A, Soret, Blue, and NIR."""

    def test_msi_optical_contrast_simulation(self):
        # 1. 415 nm Soret peak absorption for bloodstain
        res_soret = engine.simulate_msi_optical_response("Latent Bloodstain", 415)
        assert res_soret["predicted_contrast_index"] >= 0.95
        assert res_soret["is_optimal_forensic_band"] is True
        assert "Soret" in res_soret["band_info"]["band_name"]

        # 2. 365 nm UV-A fluorescence for semen/saliva
        res_uva = engine.simulate_msi_optical_response("Semen Stain", 365)
        assert res_uva["predicted_contrast_index"] >= 0.95
        assert "Fluorescence" in res_uva["band_info"]["phenomenon"]

        # 3. 850 nm NIR transmission for dark fabric blood/GSR
        res_nir = engine.simulate_msi_optical_response("Blood on Black Denim", 850)
        assert res_nir["predicted_contrast_index"] >= 0.90
        assert "Near-Infrared" in res_nir["band_info"]["band_name"]


# ── VECTOR_24_SPEC_H — FastAPI Endpoint Integration Tests ─────────────────────

class TestVector24SpecH:
    """Verifies FastAPI /forensic/physical MSI and Spectroscopy endpoints."""

    def test_api_msi_endpoint(self):
        payload = {
            "evidence_type": "Latent Bloodstain",
            "active_wavelength_nm": 415
        }
        resp = client.post("/api/v1/forensic/physical/msi-optical-analysis", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_optimal_forensic_band"] is True
        assert data["predicted_contrast_index"] >= 0.95

    def test_api_ftir_endpoint(self):
        ref_lib = engine._generate_default_reference_vectors(100)
        payload = {
            "sample_spectrum": ref_lib["Polyester"]
        }
        resp = client.post("/api/v1/forensic/physical/ftir-raman-hqi-match", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["top_match"]["material_name"] == "Polyester"
        assert data["top_match"]["hqi_score_percent"] == 100.0
