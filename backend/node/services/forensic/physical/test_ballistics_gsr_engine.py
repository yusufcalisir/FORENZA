"""
Unit & Integration Tests for FORENZA Ballistics & SEM-EDX GSR Engine — Module 22.

Tests verbatim from Pillar 5 Research §2 & §6:
  - §2.1 Quantitative SEM-EDX GSR Particle Classification (ASTM E1588-20)
  - §2.2 Congruent Matching Cells (CMC) Algorithm for 3D Toolmarks & Striations

Golden Benchmarks:
  - VECTOR_22_GSR_A through H
"""

import pytest
from typing import List, Dict, Any
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.physical.ballistics_gsr_engine import (
    BallisticsGsrEngine,
)
from app.api.physical_routes import router as physical_router

_app = FastAPI()
_app.include_router(physical_router, prefix="/api/v1")
client = TestClient(_app)

engine = BallisticsGsrEngine()


# ── VECTOR_22_GSR_A — Characteristic Pb-Ba-Sb Triad (LR = 10,000) ─────────────

class TestVector22GsrA:
    """Verifies that 3 or more characteristic Pb-Ba-Sb particles yield LR = 10,000."""

    def test_characteristic_gsr_particles(self):
        particles = [
            {"particle_id": "p1", "pb": 35.0, "ba": 25.0, "sb": 15.0, "aspect_ratio": 1.1},
            {"particle_id": "p2", "pb": 40.0, "ba": 30.0, "sb": 12.0, "aspect_ratio": 1.2},
            {"particle_id": "p3", "pb": 28.0, "ba": 22.0, "sb": 18.0, "aspect_ratio": 1.0},
        ]
        res = engine.evaluate_sem_edx_gsr(particles)

        assert res["characteristic_particles"] == 3
        assert res["likelihood_ratio"] == 10000.0
        assert "Extremely Strong Support" in res["evidence_strength"]
        assert "ASTM E1588-20" in res["prosecutors_fallacy_shield"]


# ── VECTOR_22_GSR_B — 2-Component Consistent Particles (LR = 500) ─────────────

class TestVector22GsrB:
    """Verifies that 5 consistent particles (e.g. Pb-Ba) yield LR = 500."""

    def test_consistent_gsr_particles(self):
        particles = [
            {"particle_id": f"p{i}", "pb": 45.0, "ba": 35.0, "sb": 0.0, "aspect_ratio": 1.2}
            for i in range(5)
        ]
        res = engine.evaluate_sem_edx_gsr(particles)

        assert res["characteristic_particles"] == 0
        assert res["consistent_particles"] == 5
        assert res["likelihood_ratio"] == 500.0
        assert "Strong Support" in res["evidence_strength"]


# ── VECTOR_22_GSR_C — Irregular Morphology Aspect Ratio Downgrade ─────────────

class TestVector22GsrC:
    """Verifies that non-spherical aspect ratio > 1.3 disqualifies characteristic classification."""

    def test_morphology_aspect_ratio_downgrade(self):
        # High Pb-Ba-Sb elemental content, but irregular elongated shape (aspect_ratio = 1.8)
        particles = [
            {"particle_id": "p1", "pb": 35.0, "ba": 25.0, "sb": 15.0, "aspect_ratio": 1.8},
        ]
        res = engine.evaluate_sem_edx_gsr(particles)

        # Disqualified from Characteristic (<= 1.3) and Consistent (<= 1.5), classified as Commonly Associated
        assert res["characteristic_particles"] == 0
        assert res["consistent_particles"] == 0
        assert res["commonly_associated_particles"] == 1
        assert res["likelihood_ratio"] == 1.0


# ── VECTOR_22_GSR_D — Environmental Background Particles (LR = 1.0) ───────────

class TestVector22GsrD:
    """Verifies environmental particles without significant heavy metals yield LR = 1.0."""

    def test_environmental_background_particles(self):
        particles = [
            {"particle_id": "p1", "pb": 1.0, "ba": 2.0, "sb": 0.5, "aspect_ratio": 1.1},
            {"particle_id": "p2", "pb": 0.0, "ba": 0.0, "sb": 0.0, "aspect_ratio": 2.0},
        ]
        res = engine.evaluate_sem_edx_gsr(particles)

        assert res["characteristic_particles"] == 0
        assert res["consistent_particles"] == 0
        assert res["likelihood_ratio"] == 1.0
        assert "Inconclusive / Neutral" in res["evidence_strength"]


# ── VECTOR_22_GSR_E — Positive 3D CMC Striation Identification (K >= 6) ───────

class TestVector22GsrE:
    """Verifies K >= 6 congruent matching cells establish positive firearm identification."""

    def test_positive_cmc_identification(self):
        cells = [
            {"cell_id": f"c{i}", "ccf_max": 0.85, "delta_x_um": 2.0, "delta_y_um": -1.5, "delta_theta_deg": 0.3}
            for i in range(8)
        ]
        res = engine.evaluate_3d_cmc_striations(
            cells=cells,
            mean_delta_x_um=0.0,
            mean_delta_y_um=0.0,
            mean_delta_theta_deg=0.0
        )

        assert res["cmc_count"] == 8
        assert res["identification_verdict"] == "POSITIVE_IDENTIFICATION"
        assert res["false_match_probability"] == "< 1e-6"
        assert "Definitive ballistic match" in res["ballistic_conclusion"]


# ── VECTOR_22_GSR_F — Spatial Translation Threshold Rejection (|dx| > 15um) ──

class TestVector22GsrF:
    """Verifies cells with spatial offset > 15 um are rejected from CMC."""

    def test_spatial_translation_rejection(self):
        cells = [
            # 5 matching cells
            {"cell_id": f"c_good_{i}", "ccf_max": 0.80, "delta_x_um": 5.0, "delta_y_um": 5.0, "delta_theta_deg": 0.2}
            for i in range(5)
        ] + [
            # 3 cells with excessive translation (|dx| = 25 um > 15 um)
            {"cell_id": f"c_bad_{i}", "ccf_max": 0.80, "delta_x_um": 25.0, "delta_y_um": 5.0, "delta_theta_deg": 0.2}
            for i in range(3)
        ]

        res = engine.evaluate_3d_cmc_striations(cells=cells, mean_delta_x_um=0.0, mean_delta_y_um=0.0, mean_delta_theta_deg=0.0)

        assert res["total_cells_evaluated"] == 8
        assert res["cmc_count"] == 5
        assert res["identification_verdict"] == "INCONCLUSIVE_BORDERLINE"


# ── VECTOR_22_GSR_G — Angular Rotation Threshold Rejection (|dtheta| > 1.0 deg) 

class TestVector22GsrG:
    """Verifies cells with angular rotation > 1.0 deg are rejected from CMC."""

    def test_angular_rotation_rejection(self):
        cells = [
            # Low correlation or high rotation
            {"cell_id": "c1", "ccf_max": 0.70, "delta_x_um": 0.0, "delta_y_um": 0.0, "delta_theta_deg": 2.5},
            {"cell_id": "c2", "ccf_max": 0.40, "delta_x_um": 0.0, "delta_y_um": 0.0, "delta_theta_deg": 0.1},  # CCF fail
        ]
        res = engine.evaluate_3d_cmc_striations(cells=cells)

        assert res["cmc_count"] == 0
        assert res["identification_verdict"] == "ELIMINATION_NO_MATCH"


# ── VECTOR_22_GSR_H — FastAPI Endpoint Integration Tests ─────────────────────

class TestVector22GsrH:
    """Verifies FastAPI /forensic/physical GSR and CMC endpoints."""

    def test_api_gsr_endpoint(self):
        payload = {
            "particles": [
                {"particle_id": "p1", "pb_percent": 30.0, "ba_percent": 20.0, "sb_percent": 15.0, "aspect_ratio": 1.1},
                {"particle_id": "p2", "pb_percent": 25.0, "ba_percent": 25.0, "sb_percent": 10.0, "aspect_ratio": 1.2},
                {"particle_id": "p3", "pb_percent": 28.0, "ba_percent": 22.0, "sb_percent": 18.0, "aspect_ratio": 1.0},
            ]
        }
        resp = client.post("/api/v1/forensic/physical/gsr-sem-edx-analysis", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["characteristic_particles"] == 3
        assert data["likelihood_ratio"] == 10000.0

    def test_api_cmc_endpoint(self):
        payload = {
            "cells": [
                {"cell_id": f"c{i}", "ccf_max": 0.85, "delta_x_um": 1.0, "delta_y_um": 1.0, "delta_theta_deg": 0.2}
                for i in range(6)
            ],
            "mean_delta_x_um": 0.0,
            "mean_delta_y_um": 0.0,
            "mean_delta_theta_deg": 0.0,
        }
        resp = client.post("/api/v1/forensic/physical/cmc-striation-matching", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["cmc_count"] == 6
        assert data["identification_verdict"] == "POSITIVE_IDENTIFICATION"
