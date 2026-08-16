"""
Unit and Integration Verification Suite for Pillar 7 Phase 3:
Multi-Criteria Bayesian Evidence Fusion Engine (geo_fusion_engine.py).

Verifies verbatim against:
  - Pillar 7 §5.1: Multi-Source Bayesian Grid Integration
  - Pillar 7 §5.2: 2D Adaptive Gaussian Kernel Density Estimation (KDE) with Silverman Rule
  - Pillar 7 §5.3: Prioritized Search Area & Search Efficiency Index (SEI >= 90%)
  - Pillar 7 §8: ENFSI 7-Tier Standardized Verbal Reporting Scale & ISO 17025 Prosecutor's Fallacy Shields
"""

import pytest
import math
from backend.node.services.forensic.geoint.geo_fusion_engine import (
    GeoFusionEngine,
    EvidenceLayerInput,
    SpatialHotspot,
    EvidenceFusionResult,
)


@pytest.fixture
def engine():
    return GeoFusionEngine()


class TestGeoFusionEngine:

    def test_2d_adaptive_gaussian_kde_smoothing(self, engine: GeoFusionEngine):
        """
        Validates 2D bivariate Gaussian kernel density estimation and Silverman bandwidth estimation (§5.2).
        """
        # Cluster of 5 crime/trace points around (10.0, 10.0)
        points = [
            (9.5, 9.8),
            (10.2, 10.1),
            (9.8, 10.3),
            (10.5, 9.7),
            (10.0, 10.0),
        ]

        kde_surface, (hx, hy) = engine.compute_2d_gaussian_kde(
            points=points,
            grid_bounds=(0.0, 20.0, 0.0, 20.0),
            grid_resolution_km=1.0,
        )

        assert hx > 0.0
        assert hy > 0.0
        assert len(kde_surface) == 21
        assert len(kde_surface[0]) == 21

        # Probability surface sum should normalize to 1.0
        total_mass = sum(sum(row) for row in kde_surface)
        assert pytest.approx(total_mass, 1e-5) == 1.0

        # Peak of KDE should be near center (10, 10) -> index (10, 10)
        peak_val = kde_surface[10][10]
        corner_val = kde_surface[0][0]
        assert peak_val > corner_val * 100.0

    def test_multi_layer_bayesian_grid_fusion(self, engine: GeoFusionEngine):
        """
        Validates multi-layer Bayesian product rule fusion and composite likelihood ratios (§5.1).
        """
        # Create 4 synthetic 10x10 likelihood layers
        nx, ny = 10, 10

        # Layer 1: Isotope likelihood peaking at (3, 3)
        l1 = [[math.exp(-0.5 * (((i - 3) ** 2 + (j - 3) ** 2) / 2.0)) for j in range(ny)] for i in range(nx)]
        # Layer 2: Soil QXRD likelihood peaking at (4, 3)
        l2 = [[math.exp(-0.5 * (((i - 4) ** 2 + (j - 3) ** 2) / 2.0)) for j in range(ny)] for i in range(nx)]
        # Layer 3: Palynology eDNA likelihood peaking at (3, 4)
        l3 = [[math.exp(-0.5 * (((i - 3) ** 2 + (j - 4) ** 2) / 2.0)) for j in range(ny)] for i in range(nx)]
        # Layer 4: Rossmo geographic profiling peaking at (4, 4)
        l4 = [[math.exp(-0.5 * (((i - 4) ** 2 + (j - 4) ** 2) / 2.0)) for j in range(ny)] for i in range(nx)]

        layers = [
            EvidenceLayerInput("L1", "ISOTOPE_ISOSCAPE", l1, weight=1.0, modality_likelihood_ratio=50.0),
            EvidenceLayerInput("L2", "SOIL_CODA", l2, weight=1.0, modality_likelihood_ratio=100.0),
            EvidenceLayerInput("L3", "PALYNOLOGY_EDNA", l3, weight=1.0, modality_likelihood_ratio=20.0),
            EvidenceLayerInput("L4", "ROSSMO_GEO_PROFILE", l4, weight=1.0, modality_likelihood_ratio=10.0),
        ]

        res = engine.fuse_evidence_layers(
            layers=layers,
            case_id="CASE_MULTI_FUSION_01",
            grid_bounds=(0.0, 10.0, 0.0, 10.0),
            grid_resolution_km=1.0,
        )

        assert res.case_id == "CASE_MULTI_FUSION_01"
        assert res.fused_likelihood_ratio >= 10000.0
        assert res.enfsi_verbal_tier in ["TIER_5_VERY_STRONG", "TIER_6_EXTREMELY_STRONG"]
        assert len(res.top_spatial_hotspots) >= 1
        assert "PROSECUTOR'S FALLACY SHIELD" in res.prosecutors_fallacy_shield

    def test_search_efficiency_index_calculation(self, engine: GeoFusionEngine):
        """
        Validates prioritized search area reduction and SEI >= 90% invariant (§5.3).
        """
        nx, ny = 20, 20
        # Highly concentrated evidence peaking at (10, 10)
        l1 = [[math.exp(-0.5 * (((i - 10) ** 2 + (j - 10) ** 2) / 0.5)) for j in range(ny)] for i in range(nx)]

        layer = EvidenceLayerInput("L1", "FOCUSED_EVIDENCE", l1, weight=1.0, modality_likelihood_ratio=500.0)

        res = engine.fuse_evidence_layers(
            layers=[layer],
            grid_bounds=(0.0, 20.0, 0.0, 20.0),
            grid_resolution_km=1.0,
        )

        # Concentrated signal yields small search area and high SEI
        assert res.search_area_50pct_sq_km <= 15.0
        assert res.search_efficiency_index_pct >= 90.0

    def test_composite_lr_and_enfsi_verbal_scale(self, engine: GeoFusionEngine):
        """
        Validates ENFSI 7-tier scale verbal formulations in EN & TR (§8.1 & §8.2).
        """
        l1 = [[1.0, 0.5], [0.5, 0.2]]
        layer = EvidenceLayerInput("L1", "MODERATE_EVIDENCE", l1, weight=1.0, modality_likelihood_ratio=150.0)

        res = engine.fuse_evidence_layers(layers=[layer], grid_bounds=(0.0, 2.0, 0.0, 2.0), grid_resolution_km=1.0)

        assert "kaynak dahil oluş" in res.enfsi_verbal_statement_tr
        assert "source inclusion" in res.enfsi_verbal_statement_en
        assert res.enfsi_verbal_tier == "TIER_3_MODERATELY_STRONG"

    def test_fastapi_fuse_evidence_layers_endpoint(self):
        """
        Validates FastAPI endpoint POST /api/v1/forensic/geoint/fuse-evidence-layers.
        """
        from fastapi.testclient import TestClient
        from backend.app.main import app

        client = TestClient(app)
        payload = {
            "case_id": "CASE-GEO-2026-FUSION",
            "layers": [
                {
                    "layer_id": "ISO_LAYER",
                    "modality_name": "ISOTOPE_ISOSCAPE",
                    "likelihood_matrix": [[1.0, 0.2], [0.1, 0.05]],
                    "weight": 1.0,
                    "modality_likelihood_ratio": 120.0,
                },
                {
                    "layer_id": "SOIL_LAYER",
                    "modality_name": "SOIL_CODA",
                    "likelihood_matrix": [[0.9, 0.3], [0.2, 0.01]],
                    "weight": 1.0,
                    "modality_likelihood_ratio": 80.0,
                }
            ],
            "grid_bounds_km": [0.0, 10.0, 0.0, 10.0],
            "grid_resolution_km": 5.0,
        }

        response = client.post("/api/v1/forensic/geoint/fuse-evidence-layers", json=payload)
        assert response.status_code == 200
        data = response.json()

        assert data["case_id"] == "CASE-GEO-2026-FUSION"
        assert data["fused_likelihood_ratio"] >= 9000.0
        assert len(data["top_spatial_hotspots"]) >= 1
        assert "PROSECUTOR'S FALLACY SHIELD" in data["prosecutors_fallacy_shield"]
