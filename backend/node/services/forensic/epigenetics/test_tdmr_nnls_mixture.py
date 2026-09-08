"""
Unit and Integration Tests for tDMR NNLS Mixture Deconvolution Engine.
Tests verbatim from Pillar 4 Research Section 2 & Section 6:
  - Section 2.1 Diagnostic 12-tDMR Loci Matrix
  - Section 2.2 Quadratic Discriminant Analysis
  - Section 2.3 Non-Negative Least Squares (NNLS) with Sum-to-One Simplex Invariant
  - Golden Reference Standards & Casework Mixtures
"""

import math
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.epigenetics.tissue_deconv import (
    TissueDeconvolutionEngine,
    CERTIFIED_TISSUE_GOLDEN_VECTORS,
    project_to_simplex,
)
from app.api.epigenetics_routes import router as epigenetics_router

_app = FastAPI()
_app.include_router(epigenetics_router, prefix="/api/v1")
client = TestClient(_app)

engine = TissueDeconvolutionEngine()


class TestTdmrReferenceAndStandards:
    """Verifies reference distribution matrix and golden vector catalogs."""

    def test_reference_matrix_structure(self):
        mat = engine.get_reference_matrix()
        assert mat["loci_count"] == 12
        assert len(mat["tissues"]) == 6
        assert len(mat["reference_loci"]) == 12
        first = mat["reference_loci"][0]
        assert "blood_mean" in first
        assert "semen_mean" in first
        assert "saliva_mean" in first

    def test_golden_vectors_catalog(self):
        gv = engine.get_golden_vectors()
        assert gv["total_vectors"] == 8
        assert "VECTOR_TISSUE_BLOOD_PURE" in gv["vectors"]
        assert "VECTOR_TISSUE_MIX_SEXUAL_ASSAULT" in gv["vectors"]


class TestSimplexProjection:
    """Verifies mathematical invariant of simplex projection."""

    def test_simplex_sum_to_one(self):
        raw_vectors = [
            [0.5, 0.5, 0.0, 0.0, 0.0, 0.0],
            [1.2, -0.3, 0.4, 0.1, -0.2, 0.0],
            [0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
            [5.0, 2.0, 1.0, 0.0, 0.0, 0.0],
        ]
        for v in raw_vectors:
            proj = project_to_simplex(v)
            assert len(proj) == len(v)
            assert all(x >= 0.0 for x in proj)
            assert abs(sum(proj) - 1.0) < 1e-6


class TestNnlsMixtureDeconvolution:
    """Verifies constrained least-squares mixture decomposition."""

    def test_nnls_pure_venous_blood(self):
        vec = CERTIFIED_TISSUE_GOLDEN_VECTORS["VECTOR_TISSUE_BLOOD_PURE"]
        res = engine.deconvolve_mixture_nnls(vec["betas"])

        assert res["major_contributor"] == "BLOOD"
        assert res["major_fraction"] >= 0.90
        assert res["is_mixture"] is False
        assert abs(res["sum_proportions"] - 1.0) <= 1e-3
        assert res["tdmr_loci_evaluated"] == 12

    def test_nnls_pure_semen(self):
        vec = CERTIFIED_TISSUE_GOLDEN_VECTORS["VECTOR_TISSUE_SEMEN_PURE"]
        res = engine.deconvolve_mixture_nnls(vec["betas"])

        assert res["major_contributor"] == "SEMEN"
        assert res["major_fraction"] >= 0.90
        assert res["is_mixture"] is False
        assert abs(res["sum_proportions"] - 1.0) <= 1e-3

    def test_nnls_mixture_sexual_assault_70_30(self):
        vec = CERTIFIED_TISSUE_GOLDEN_VECTORS["VECTOR_TISSUE_MIX_SEXUAL_ASSAULT"]
        res = engine.deconvolve_mixture_nnls(vec["betas"])

        assert res["is_mixture"] is True
        assert res["major_contributor"] == "SEMEN"
        assert res["tissue_proportions"]["SEMEN"] >= 0.60
        assert res["tissue_proportions"]["VAGINAL"] >= 0.20
        assert abs(res["sum_proportions"] - 1.0) <= 1e-3
        assert res["residual_sum_of_squares"] < 0.05

    def test_nnls_mixture_violent_scene_60_40(self):
        vec = CERTIFIED_TISSUE_GOLDEN_VECTORS["VECTOR_TISSUE_MIX_VIOLENT_SCENE"]
        res = engine.deconvolve_mixture_nnls(vec["betas"])

        assert res["is_mixture"] is True
        assert res["major_contributor"] == "BLOOD"
        assert res["tissue_proportions"]["BLOOD"] >= 0.50
        assert res["tissue_proportions"]["SALIVA"] >= 0.30
        assert abs(res["sum_proportions"] - 1.0) <= 1e-3


class TestApiEndpoints:
    """Verifies FastAPI route dispatching and response validation."""

    def test_api_deconvolve_mixture_nnls(self):
        vec = CERTIFIED_TISSUE_GOLDEN_VECTORS["VECTOR_TISSUE_MIX_SEXUAL_ASSAULT"]
        resp = client.post(
            "/api/v1/forensic/epigenetics/deconvolve-mixture-nnls",
            json={"tdmr_methylation": vec["betas"]}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_mixture"] is True
        assert data["major_contributor"] == "SEMEN"
        assert "VAGINAL" in data["tissue_proportions"]
        assert abs(data["sum_proportions"] - 1.0) <= 1e-3

    def test_api_tdmr_reference_matrix(self):
        resp = client.get("/api/v1/forensic/epigenetics/tdmr/reference-matrix")
        assert resp.status_code == 200
        data = resp.json()
        assert data["loci_count"] == 12
        assert len(data["tissues"]) == 6

    def test_api_tdmr_golden_vectors(self):
        resp = client.get("/api/v1/forensic/epigenetics/tdmr/golden-vectors")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_vectors"] == 8
