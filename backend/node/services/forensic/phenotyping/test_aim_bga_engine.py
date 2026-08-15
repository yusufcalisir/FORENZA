"""
Unit & Integration Tests for FORENZA 55-SNP AIM Biogeographic Ancestry & Live GIS Geolocation Engine — Module 12.

Tests verbatim from Pillar 3 Research §2 & §6:
  - §2.1 55-SNP Reference Allele Frequency Matrix
  - §2.2 Bayesian Posterior Admixture Estimation (Sum-to-Unity Invariant |sum q_j - 1.0| <= 1e-6)
  - §2.3 3D Spherical Geographic Coordinate Projection & 95% Confidence Ellipse Geometry
  - Shannon Entropy, Simpson Diversity Index, and Admixture Complexity

Golden Benchmarks:
  - VECTOR_P3_01: Northern European Fair Phototype (q_EUR >= 0.95, GIS: European Centroid)
  - VECTOR_P3_02: Sub-Saharan African Dark Phototype (q_AFR >= 0.98, DARC Duffy null C/C, GIS: African Centroid)
  - VECTOR_P3_03: East Asian Coarse Hair Phenotype (q_EAS >= 0.95, EDAR C/C, OCA2 His615Arg C/C, GIS: East Asian Centroid)
  - VECTOR_12_AIM_A through H
"""

import math
from typing import Any, Dict, List
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.phenotyping.aim_bga_engine import (
    AIMBGAEngine,
    CONTINENTAL_CENTROIDS,
    POPULATIONS,
)
from app.api.phenotype_routes import router as phenotype_router

_app = FastAPI()
_app.include_router(phenotype_router, prefix="/api/v1")
client = TestClient(_app)

engine = AIMBGAEngine()


# ── Golden Benchmark VECTOR_P3_01 (Northern European Fair Phototype) ──────────

class TestVectorP301:
    """Verifies Golden Benchmark VECTOR_P3_01: Northern European Ancestry & GIS."""

    def test_vector_p3_01_ancestry_and_gis(self):
        # Genotype profile: rs1426654: 2 (A/A), rs16891982: 2 (G/G), rs28777: 2 (A/A), rs12913832: 2 (C/C)
        dosages = {
            "rs1426654": 2,   # SLC24A5 European derived (p_EUR=0.998)
            "rs16891982": 2,  # SLC45A2 European derived (p_EUR=0.984)
            "rs28777": 2,     # SLC45A2 (p_EUR=0.950)
            "rs12913832": 2,  # HERC2 (p_EUR=0.720)
            "rs2814778": 0,   # DARC ancestral (p_AFR=0.992) -> non-African
        }

        res = engine.analyze_bga_profile(dosages)

        # 1. European Posterior Admixture >= 0.95
        assert res.proportions["EUR"] >= 0.95
        assert res.dominant_population == "EUR"
        assert res.admixture_classification == "HOMOGENEOUS"
        assert abs(sum(res.proportions.values()) - 1.0) <= 1e-6

        # 2. GIS Coordinate Projection in Europe
        assert 40.0 <= res.gis_projection.latitude <= 55.0
        assert 5.0 <= res.gis_projection.longitude <= 25.0
        assert res.gis_projection.nearest_centroid == "European"


# ── Golden Benchmark VECTOR_P3_02 (Sub-Saharan African Dark Phototype) ─────────

class TestVectorP302:
    """Verifies Golden Benchmark VECTOR_P3_02: Sub-Saharan African Ancestry & GIS."""

    def test_vector_p3_02_ancestry_and_gis(self):
        # Genotype profile: rs2814778: 2 (C/C Duffy Null), rs1426654: 0 (G/G), rs10424031: 2 (A/A)
        dosages = {
            "rs2814778": 2,   # DARC Duffy Null (p_AFR=0.992)
            "rs1426654": 0,   # SLC24A5 ancestral (p_AFR=0.021)
            "rs10424031": 2,  # MFSD12 African dark skin (p_AFR=0.850)
            "rs6119471": 2,   # COL11A1 (p_AFR=0.780)
            "rs1834619": 2,   # SLC24A5 African (p_AFR=0.820)
        }

        res = engine.analyze_bga_profile(dosages)

        # 1. African Posterior Admixture >= 0.98
        assert res.proportions["AFR"] >= 0.98
        assert res.dominant_population == "AFR"
        assert res.admixture_classification == "HOMOGENEOUS"
        assert abs(sum(res.proportions.values()) - 1.0) <= 1e-6

        # 2. GIS Coordinate Projection in Africa
        assert -5.0 <= res.gis_projection.latitude <= 15.0
        assert 10.0 <= res.gis_projection.longitude <= 35.0
        assert res.gis_projection.nearest_centroid == "African"


# ── Golden Benchmark VECTOR_P3_03 (East Asian Coarse Hair Phenotype) ──────────

class TestVectorP303:
    """Verifies Golden Benchmark VECTOR_P3_03: East Asian Ancestry & GIS."""

    def test_vector_p3_03_ancestry_and_gis(self):
        # Genotype profile: rs3827072: 2 (C/C EDAR 370Ala), rs1800414: 2 (C/C OCA2), rs885479: 2 (G/G MC1R)
        dosages = {
            "rs3827072": 2,   # EDAR 370Ala (p_EAS=0.945)
            "rs1800414": 2,   # OCA2 His615Arg (p_EAS=0.725)
            "rs885479": 2,    # MC1R R163Q (p_EAS=0.680)
            "rs2065160": 2,   # OCA2 (p_EAS=0.850)
            "rs1799971": 2,   # OPRM1 (p_EAS=0.650)
        }

        res = engine.analyze_bga_profile(dosages)

        # 1. East Asian Posterior Admixture >= 0.95
        assert res.proportions["EAS"] >= 0.95
        assert res.dominant_population == "EAS"
        assert res.admixture_classification == "HOMOGENEOUS"
        assert abs(sum(res.proportions.values()) - 1.0) <= 1e-6

        # 2. GIS Coordinate Projection in East Asia
        assert 25.0 <= res.gis_projection.latitude <= 45.0
        assert 90.0 <= res.gis_projection.longitude <= 125.0
        assert res.gis_projection.nearest_centroid == "East Asian"


# ── VECTOR_12_AIM_A — Admixture Sum-to-Unity Invariant ────────────────────────

class TestVector12AIMA:
    """Verifies mathematical sum-to-one invariant |sum q_j - 1.0| <= 1e-6."""

    def test_sum_to_one_across_various_dosage_combinations(self):
        test_profiles = [
            {},  # Empty profile (uniform prior)
            {"rs2814778": 2},
            {"rs1426654": 2, "rs3827072": 1, "rs2814778": 1},
            {"rs3827072": 2, "rs1800414": 2, "rs16891982": 0},
            {k: 1 for k in ["rs2814778", "rs1426654", "rs3827072", "rs1800414", "rs16891982"]},
        ]

        for prof in test_profiles:
            props, _ = engine.estimate_admixture(prof)
            assert abs(sum(props.values()) - 1.0) <= 1e-6
            for p in props.values():
                assert 0.0 <= p <= 1.0


# ── VECTOR_12_AIM_B — DARC Duffy Null Informative Marker ──────────────────────

class TestVector12AIMB:
    """Verifies DARC rs2814778 fixation in African populations."""

    def test_duffy_null_homozygous_calls_african(self):
        props, _ = engine.estimate_admixture({"rs2814778": 2})
        assert props["AFR"] > 0.85

    def test_duffy_null_absent_excludes_african_dominance(self):
        props, _ = engine.estimate_admixture({"rs2814778": 0, "rs1426654": 2, "rs16891982": 2})
        assert props["AFR"] < 0.01
        assert props["EUR"] > 0.80


# ── VECTOR_12_AIM_C — SLC24A5 European vs South Asian Differentiation ────────

class TestVector12AIMC:
    """Verifies SLC24A5 and SLC45A2 European/South Asian differentiation."""

    def test_slc24a5_with_slc45a2_favors_european_over_south_asian(self):
        # SLC45A2 is high in EUR (0.984) and low in SAS (0.124)
        props, _ = engine.estimate_admixture({"rs1426654": 2, "rs16891982": 2})
        assert props["EUR"] > props["SAS"]
        assert props["EUR"] > 0.85

    def test_slc24a5_without_slc45a2_preserves_south_asian_possibility(self):
        props, _ = engine.estimate_admixture({"rs1426654": 2, "rs16891982": 0})
        assert props["SAS"] > props["EUR"]


# ── VECTOR_12_AIM_D — EDAR 370Ala & OCA2 East Asian Specificity ───────────────

class TestVector12AIMD:
    """Verifies EDAR and OCA2 East Asian specific markers."""

    def test_edar_and_oca2_produce_strong_east_asian_call(self):
        props, _ = engine.estimate_admixture({"rs3827072": 2, "rs1800414": 2})
        assert props["EAS"] > 0.90


# ── VECTOR_12_AIM_E — 3D Spherical GIS Coordinate Projection ──────────────────

class TestVector12AIME:
    """Verifies spherical coordinate transformation & centroid wrapping."""

    def test_pure_european_centroid_projection(self):
        props = {"EUR": 1.0, "AFR": 0.0, "EAS": 0.0, "SAS": 0.0, "AMR": 0.0}
        gis = engine.project_gis_coordinates(props)
        assert abs(gis.latitude - 48.50) < 0.1
        assert abs(gis.longitude - 15.20) < 0.1
        assert gis.nearest_centroid == "European"

    def test_pure_african_centroid_projection(self):
        props = {"EUR": 0.0, "AFR": 1.0, "EAS": 0.0, "SAS": 0.0, "AMR": 0.0}
        gis = engine.project_gis_coordinates(props)
        assert abs(gis.latitude - 2.50) < 0.1
        assert abs(gis.longitude - 22.80) < 0.1
        assert gis.nearest_centroid == "African"

    def test_bivariate_admixture_midpoint(self):
        # 50% EUR + 50% AFR
        props = {"EUR": 0.5, "AFR": 0.5, "EAS": 0.0, "SAS": 0.0, "AMR": 0.0}
        gis = engine.project_gis_coordinates(props)
        # Lat should be intermediate (~25-26 deg N)
        assert 20.0 < gis.latitude < 30.0
        assert 15.0 < gis.longitude < 25.0


# ── VECTOR_12_AIM_F — 95% Confidence Ellipse Geometry ─────────────────────────

class TestVector12AIMF:
    """Verifies 95% confidence ellipse semi-axes and orientation."""

    def test_ellipse_parameters_positive_and_ordered(self):
        # Mixed ancestry creates spatial dispersion
        props = {"EUR": 0.6, "AFR": 0.3, "EAS": 0.1, "SAS": 0.0, "AMR": 0.0}
        gis = engine.project_gis_coordinates(props)
        el = gis.confidence_ellipse

        assert el.semi_major_deg >= el.semi_minor_deg > 0.0
        assert el.semi_major_km >= el.semi_minor_km > 0.0
        assert -180.0 <= el.tilt_angle_deg <= 180.0


# ── VECTOR_12_AIM_G — Admixture Complexity & Entropy ──────────────────────────

class TestVector12AIMG:
    """Verifies Shannon entropy and admixture complexity classification."""

    def test_homogeneous_profile_has_low_entropy(self):
        res = engine.analyze_bga_profile({"rs1426654": 2, "rs16891982": 2, "rs28777": 2})
        assert res.admixture_classification == "HOMOGENEOUS"
        assert res.shannon_entropy < 0.50

    def test_admixed_profile_classification(self):
        # Balanced mixture with moderate frequencies across multiple continental clusters
        dosages = {"rs3340": 1, "rs174537": 1, "rs10007810": 1, "rs7561684": 1, "rs6152": 1, "rs756853": 1}
        res = engine.analyze_bga_profile(dosages)
        assert res.admixture_classification in ["BI_ADMIXED", "MULTI_ADMIXED"]
        assert res.shannon_entropy > 0.50




# ── VECTOR_12_AIM_H — API Integration Tests ───────────────────────────────────

class TestVector12AIMH:
    """Verifies FastAPI endpoints for 55-AIM BGA."""

    def test_api_predict_55_aim(self):
        payload = {
            "snp_dosages": {"rs1426654": 2, "rs16891982": 2, "rs28777": 2}
        }
        resp = client.post("/api/v1/forensic/ancestry/55-aim/predict", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["dominant_population"] == "EUR"
        assert data["proportions"]["EUR"] > 0.85
        assert "confidence_ellipse" in data["gis_projection"]

    def test_api_gis_coordinates(self):
        payload = {
            "snp_dosages": {"rs2814778": 2, "rs1426654": 0}
        }
        resp = client.post("/api/v1/forensic/ancestry/55-aim/gis-coordinates", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["nearest_centroid"] == "African"
        assert "formatted_coords" in data
