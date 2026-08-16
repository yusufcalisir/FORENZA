"""
Unit & Integration Tests for FORENZA 3D BPA & Area of Origin Engine — Module 21.

Tests verbatim from Pillar 5 Research §1 & §6:
  - §1.1 Fluid Kinematics and Elliptical Projection Dynamics
  - §1.2 Least Squares Orthogonal Distance Minimization for 3D Area of Origin
  - §1.3 Aerodynamic Drag (Schiller-Naumann Cd) and Gravitational Trajectory Curvature Correction

Golden Benchmarks:
  - VECTOR_P5_01 (5-Stain 3D Area of Origin Ground Truth Convergence)
  - VECTOR_21_BPA_A through H
"""

import math
from typing import Tuple, Dict, Any, List
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


from node.services.forensic.physical.bpa_origin_engine import (
    BpaAreaOfOriginEngine,
)
from app.api.physical_routes import router as physical_router

_app = FastAPI()
_app.include_router(physical_router, prefix="/api/v1")
client = TestClient(_app)

engine = BpaAreaOfOriginEngine()


# ── Helper to generate stains pointing back to origin ─────────────────────────

def make_stain_pointing_to_origin(
    origin: Tuple[float, float, float],
    stain_pos: Tuple[float, float, float],
    stain_id: str = "stain"
) -> Dict[str, Any]:
    x0, y0, z0 = origin
    px, py, pz = stain_pos
    vx = x0 - px
    vy = y0 - py
    vz = z0 - pz
    dist = math.sqrt(vx * vx + vy * vy + vz * vz)
    if dist > 0:
        vx /= dist
        vy /= dist
        vz /= dist

    # If vz < 0, invert line direction so vz >= 0 (since sin(alpha) >= 0 in geometric projection)
    if vz < 0:
        vx = -vx
        vy = -vy
        vz = -vz

    alpha_rad = math.asin(max(0.0, min(1.0, vz)))
    gamma_rad = math.atan2(vy, vx)
    gamma_deg = math.degrees(gamma_rad)
    if gamma_deg < 0:
        gamma_deg += 360.0

    length = 10.0
    width = length * math.sin(alpha_rad)

    return {
        "stain_id": stain_id,
        "x_cm": px,
        "y_cm": py,
        "z_cm": pz,
        "width_mm": max(0.1, round(width, 4)),
        "length_mm": length,
        "gamma_degrees": round(gamma_deg, 4)
    }



# ── VECTOR_P5_01 — 3D BPA Impact Spatter Origin Golden Benchmark ──────────────

class TestVectorP501:
    """Verifies 5-stain vertical wall convergence to target origin (125.4, -45.2, 142.8) cm."""

    def test_vector_p5_01_area_of_origin_convergence(self):
        target_origin = (125.4, -45.2, 142.8)
        stain_coords = [
            (150.0, -20.0, 180.0),
            (100.0, -70.0, 110.0),
            (160.0, -60.0, 130.0),
            (90.0, -30.0, 160.0),
            (140.0, -80.0, 150.0),
        ]

        stains = [
            make_stain_pointing_to_origin(target_origin, pos, f"stain_{i+1}")
            for i, pos in enumerate(stain_coords)
        ]

        res = engine.solve_3d_area_of_origin(stains, apply_drag_gravity_correction=False)

        assert res["stains_analyzed"] == 5
        assert res["origin"]["x_cm"] == pytest.approx(125.4, abs=3.0)
        assert res["origin"]["y_cm"] == pytest.approx(-45.2, abs=3.0)
        assert res["origin"]["z_cm"] == pytest.approx(142.8, abs=3.0)
        assert res["spatial_error_radius_cm"] <= 3.0
        assert "SWGSTAIN / IABPA" in res["prosecutors_fallacy_shield"]


# ── VECTOR_21_BPA_A — Two-Stain Minimal Geometric Intersection ────────────────

class TestVector21BpaA:
    """Verifies 2-stain intersection solves cleanly."""

    def test_two_stain_intersection(self):
        target = (100.0, 100.0, 150.0)
        stains = [
            make_stain_pointing_to_origin(target, (50.0, 100.0, 100.0), "s1"),
            make_stain_pointing_to_origin(target, (150.0, 100.0, 100.0), "s2"),
        ]
        res = engine.solve_3d_area_of_origin(stains)

        assert res["stains_analyzed"] == 2
        assert res["origin"]["x_cm"] == pytest.approx(100.0, abs=1.0)
        assert res["origin"]["z_cm"] == pytest.approx(150.0, abs=1.0)


# ── VECTOR_21_BPA_B — Perpendicular Impact (W / L = 1.0) ──────────────────────

class TestVector21BpaB:
    """Verifies circular droplet normal impact (90 deg)."""

    def test_perpendicular_impact_angle(self):
        alpha = engine.compute_impact_angle(10.0, 10.0)
        assert alpha == pytest.approx(90.0, abs=1e-3)


# ── VECTOR_21_BPA_C — Glancing Impact Angle ────────────────────────────────────

class TestVector21BpaC:
    """Verifies acute impact angle calculation."""

    def test_glancing_impact_angle(self):
        # W = 2.0 mm, L = 10.0 mm -> sin(alpha) = 0.20 -> alpha approx 11.537 deg
        alpha = engine.compute_impact_angle(2.0, 10.0)
        assert alpha == pytest.approx(11.537, abs=0.01)


# ── VECTOR_21_BPA_D — Parallel Trajectories Singular Matrix Rejection ─────────

class TestVector21BpaD:
    """Verifies parallel trajectories raise a singular matrix error."""

    def test_parallel_trajectories_raise(self):
        stains = [
            {"stain_id": "s1", "x_cm": 0.0, "y_cm": 0.0, "z_cm": 0.0, "width_mm": 5.0, "length_mm": 10.0, "gamma_degrees": 45.0},
            {"stain_id": "s2", "x_cm": 10.0, "y_cm": 10.0, "z_cm": 10.0, "width_mm": 5.0, "length_mm": 10.0, "gamma_degrees": 45.0},
        ]
        with pytest.raises(ValueError, match="Singular matrix encountered"):
            engine.solve_3d_area_of_origin(stains)


# ── VECTOR_21_BPA_E — Insufficient Stains Rejection ───────────────────────────

class TestVector21BpaE:
    """Verifies single stain is rejected."""

    def test_single_stain_rejected(self):
        with pytest.raises(ValueError, match="At least 2 bloodstains"):
            engine.solve_3d_area_of_origin([
                {"stain_id": "s1", "x_cm": 0.0, "y_cm": 0.0, "z_cm": 0.0, "width_mm": 5.0, "length_mm": 10.0, "gamma_degrees": 45.0}
            ])


# ── VECTOR_21_BPA_F — Aerodynamic Gravity Upward Correction ───────────────────

class TestVector21BpaF:
    """Verifies aerodynamic drag and gravity upward correction increases z0."""

    def test_gravity_correction_elevates_z0(self):
        target_origin = (120.0, 50.0, 130.0)
        stain_coords = [
            (200.0, 100.0, 100.0),
            (50.0, 20.0, 90.0),
            (180.0, 10.0, 110.0),
        ]
        stains = [
            make_stain_pointing_to_origin(target_origin, pos, f"s_{i}")
            for i, pos in enumerate(stain_coords)
        ]

        res_linear = engine.solve_3d_area_of_origin(stains, apply_drag_gravity_correction=False)
        res_gravity = engine.solve_3d_area_of_origin(stains, apply_drag_gravity_correction=True)

        assert res_gravity["origin"]["z_cm"] > res_linear["origin"]["z_cm"]
        assert res_gravity["gravity_correction_applied"] is True


# ── VECTOR_21_BPA_G — Invalid Width/Length Rejection ─────────────────────────

class TestVector21BpaG:
    """Verifies non-positive dimensions raise ValueError."""

    def test_non_positive_dimensions_raise(self):
        with pytest.raises(ValueError, match="positive"):
            engine.compute_impact_angle(-1.0, 10.0)


# ── VECTOR_21_BPA_H — FastAPI Endpoint Integration Tests ─────────────────────

class TestVector21BpaH:
    """Verifies FastAPI /forensic/physical/bpa-area-of-origin endpoint integration."""

    def test_api_bpa_area_of_origin_endpoint(self):
        target_origin = (125.4, -45.2, 142.8)
        stain_coords = [
            (150.0, -20.0, 180.0),
            (100.0, -70.0, 110.0),
            (160.0, -60.0, 130.0),
        ]
        stains = [
            make_stain_pointing_to_origin(target_origin, pos, f"stain_{i+1}")
            for i, pos in enumerate(stain_coords)
        ]

        payload = {
            "stains": stains,
            "apply_drag_gravity_correction": True
        }
        resp = client.post("/api/v1/forensic/physical/bpa-area-of-origin", json=payload)
        assert resp.status_code == 200
        data = resp.json()

        assert "origin" in data
        assert data["origin"]["x_cm"] == pytest.approx(125.4, abs=3.0)
        assert data["stains_analyzed"] == 3
        assert data["gravity_correction_applied"] is True
        assert "SWGSTAIN / IABPA" in data["prosecutors_fallacy_shield"]
