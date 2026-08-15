"""
Unit & Integration Tests for FORENZA Craniofacial Morphometrics & 3D Shape Space Reconstruction — Module 13.

Tests verbatim from Pillar 3 Research §3:
  - §3.1 Primary Craniofacial Predictor Loci (PAX3, PAX9, PRDM16, DCHS2, PCDH15)
  - §3.2 3D Cephalometric Landmark Reconstruction Equations (N, Prn, Sn, Al_L, Al_R, Ls, Me in mm)
  - Clinical Facial Indices & Typology (I_F, Facial Height, Alar Breadth, Nasal Projection)
  - Bilateral Midline Symmetry & Vertical Z-Monotonicity Invariants

Golden Benchmarks:
  - VECTOR_13_MORPHO_A through H
"""

import math
from typing import Any, Dict
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.phenotyping.morphometrics_engine import (
    MorphometricsEngine,
    Point3D,
    CephalometricLandmarks,
    FacialIndices,
)
from app.api.phenotype_routes import router as phenotype_router

_app = FastAPI()
_app.include_router(phenotype_router, prefix="/api/v1")
client = TestClient(_app)

engine = MorphometricsEngine()


# ── VECTOR_13_MORPHO_A — Baseline Reference 3D Landmark Geometry ──────────────

class TestVector13MorphoA:
    """Verifies baseline reference geometry when all effect dosages are 0."""

    def test_baseline_reference_coordinates(self):
        lm = engine.reconstruct_3d_landmarks({})

        # Exact baseline constants from Research §3.2
        assert lm.nasion.x == 0.00
        assert lm.nasion.y == pytest.approx(12.40, abs=1e-3)
        assert lm.nasion.z == pytest.approx(45.20, abs=1e-3)

        assert lm.pronasale.x == 0.00
        assert lm.pronasale.y == pytest.approx(48.50, abs=1e-3)
        assert lm.pronasale.z == pytest.approx(12.10, abs=1e-3)

        assert lm.subnasale.x == 0.00
        assert lm.subnasale.y == pytest.approx(38.20, abs=1e-3)
        assert lm.subnasale.z == pytest.approx(-2.50, abs=1e-3)

        assert lm.alare_left.x == pytest.approx(-18.50, abs=1e-3)
        assert lm.alare_left.y == pytest.approx(36.10, abs=1e-3)
        assert lm.alare_left.z == pytest.approx(2.10, abs=1e-3)

        assert lm.alare_right.x == pytest.approx(18.50, abs=1e-3)
        assert lm.alare_right.y == pytest.approx(36.10, abs=1e-3)
        assert lm.alare_right.z == pytest.approx(2.10, abs=1e-3)

        assert lm.labiale_superius.x == 0.00
        assert lm.labiale_superius.y == pytest.approx(34.50, abs=1e-3)
        assert lm.labiale_superius.z == pytest.approx(-12.40, abs=1e-3)

        assert lm.menton.x == 0.00
        assert lm.menton.y == pytest.approx(18.20, abs=1e-3)
        assert lm.menton.z == pytest.approx(-68.50, abs=1e-3)


# ── VECTOR_13_MORPHO_B — Bilateral Midline Symmetry Invariant ─────────────────

class TestVector13MorphoB:
    """Verifies strict bilateral midline symmetry invariant across dosage vectors."""

    def test_bilateral_symmetry_invariant(self):
        for d in [0, 1, 2]:
            dosages = {
                "rs974448": d,
                "rs12882923": d,
                "rs11130635": d,
                "rs13289": d,
                "rs7559252": d,
            }
            lm = engine.reconstruct_3d_landmarks(dosages)

            # Midline points must have exact X = 0.00
            assert lm.nasion.x == 0.00
            assert lm.pronasale.x == 0.00
            assert lm.subnasale.x == 0.00
            assert lm.labiale_superius.x == 0.00
            assert lm.menton.x == 0.00

            # Alare points must be exact mirrors across X axis
            assert lm.alare_left.x == pytest.approx(-lm.alare_right.x, abs=1e-6)
            assert lm.alare_left.y == pytest.approx(lm.alare_right.y, abs=1e-6)
            assert lm.alare_left.z == pytest.approx(lm.alare_right.z, abs=1e-6)


# ── VECTOR_13_MORPHO_C — Nasal Bridge Elevation & Projection ──────────────────

class TestVector13MorphoC:
    """Verifies PRDM16 and DCHS2 nasal tip deformation."""

    def test_prdm16_elevates_nasal_projection(self):
        # PRDM16 homozygous (X=2) + DCHS2 baseline (X=0)
        lm = engine.reconstruct_3d_landmarks({"rs11130635": 2, "rs13289": 0})
        # y = 48.5 + 2.10*2 = 52.70 mm
        # z = 12.1 + 1.15*2 = 14.40 mm
        assert lm.pronasale.y == pytest.approx(52.70, abs=1e-3)
        assert lm.pronasale.z == pytest.approx(14.40, abs=1e-3)

    def test_dchs2_modulates_subnasale_angle(self):
        # DCHS2 homozygous (X=2)
        lm = engine.reconstruct_3d_landmarks({"rs13289": 2})
        # Sn y = 38.2 - 1.10*2 = 36.00 mm
        # Sn z = -2.5 - 0.65*2 = -3.80 mm
        assert lm.subnasale.y == pytest.approx(36.00, abs=1e-3)
        assert lm.subnasale.z == pytest.approx(-3.80, abs=1e-3)


# ── VECTOR_13_MORPHO_D — Bizygomatic / Alar Breadth Expansion ─────────────────

class TestVector13MorphoD:
    """Verifies PAX9 alar breadth modulation."""

    def test_pax9_expands_alar_width(self):
        lm_base = engine.reconstruct_3d_landmarks({"rs12882923": 0})
        lm_expanded = engine.reconstruct_3d_landmarks({"rs12882923": 2})

        base_width = lm_base.alare_left.distance_to(lm_base.alare_right)
        exp_width = lm_expanded.alare_left.distance_to(lm_expanded.alare_right)

        # Baseline: 2 * 18.5 = 37.00 mm
        assert base_width == pytest.approx(37.00, abs=1e-2)
        # Expanded: 2 * (18.5 + 0.95*2) = 2 * 20.40 = 40.80 mm
        assert exp_width == pytest.approx(40.80, abs=1e-2)
        assert exp_width > base_width


# ── VECTOR_13_MORPHO_E — Mandibular & Chin Prominence ─────────────────────────

class TestVector13MorphoE:
    """Verifies PCDH15 chin prominence and mandibular convexity."""

    def test_pcdh15_modulates_menton_and_labiale(self):
        lm = engine.reconstruct_3d_landmarks({"rs7559252": 2})
        # Me: y = 18.2 + 1.85*2 = 21.90 mm, z = -68.5 - 1.20*2 = -70.90 mm
        assert lm.menton.y == pytest.approx(21.90, abs=1e-3)
        assert lm.menton.z == pytest.approx(-70.90, abs=1e-3)

        # Ls: y = 34.5 + 0.60*2 = 35.70 mm, z = -12.4 - 0.40*2 = -13.20 mm
        assert lm.labiale_superius.y == pytest.approx(35.70, abs=1e-3)
        assert lm.labiale_superius.z == pytest.approx(-13.20, abs=1e-3)


# ── VECTOR_13_MORPHO_F — Clinical Facial Indices & Typology ───────────────────

class TestVector13MorphoF:
    """Verifies facial dimensions, nasal projection, and facial index typology."""

    def test_facial_indices_calculation(self):
        res = engine.analyze_craniofacial_morphology({
            "rs974448": 2, "rs12882923": 1, "rs11130635": 2, "rs13289": 0, "rs7559252": 2
        })

        idx = res.indices
        assert idx.morphological_facial_height_mm > 100.0
        assert idx.alar_breadth_mm > 35.0
        assert idx.nasal_height_mm > 40.0
        assert idx.nasal_projection_mm > 10.0
        assert idx.facial_index_ratio > 200.0
        assert idx.facial_typology in [
            "EURYPROSOPIC (Broad Face)",
            "MESOPROSOPIC (Average Face)",
            "LEPTOPROSOPIC (Narrow/Long Face)",
        ]


# ── VECTOR_13_MORPHO_G — Vertical Z-Monotonicity Invariant ────────────────────

class TestVector13MorphoG:
    """Verifies anatomical vertical order z_N > z_Prn > z_Sn > z_Ls > z_Me."""

    def test_z_monotonicity_preserved_across_all_extremes(self):
        for p3 in [0, 2]:
            for p9 in [0, 2]:
                for pr in [0, 2]:
                    for dc in [0, 2]:
                        for pc in [0, 2]:
                            dosages = {
                                "rs974448": p3,
                                "rs12882923": p9,
                                "rs11130635": pr,
                                "rs13289": dc,
                                "rs7559252": pc,
                            }
                            lm = engine.reconstruct_3d_landmarks(dosages)
                            assert lm.nasion.z > lm.pronasale.z
                            assert lm.pronasale.z > lm.subnasale.z
                            assert lm.subnasale.z > lm.labiale_superius.z
                            assert lm.labiale_superius.z > lm.menton.z


# ── VECTOR_13_MORPHO_H — API Integration Tests ─────────────────────────────────

class TestVector13MorphoH:
    """Verifies FastAPI endpoints for 3D craniofacial reconstruction."""

    def test_api_reconstruct_3d_endpoint(self):
        payload = {
            "snp_dosages": {"rs974448": 2, "rs12882923": 1, "rs11130635": 2}
        }
        resp = client.post("/api/v1/forensic/morphometrics/craniofacial/reconstruct-3d", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "landmarks" in data
        assert "indices" in data
        assert data["landmarks"]["nasion"]["z"] > 45.0
        assert data["assayed_loci_count"] == 3

    def test_api_landmarks_endpoint(self):
        payload = {
            "snp_dosages": {"rs11130635": 2, "rs13289": 0}
        }
        resp = client.post("/api/v1/forensic/morphometrics/craniofacial/landmarks", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["pronasale"]["y"] == pytest.approx(52.70, abs=1e-2)
