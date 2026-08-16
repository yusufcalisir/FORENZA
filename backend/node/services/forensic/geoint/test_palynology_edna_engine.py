"""
Unit and Biome Classification Verification Suite for Pillar 7 Phase 2.1:
Forensic Palynology, Botanical Trace & Environmental Metagenomics Engine (palynology_edna_engine.py).

Verifies verbatim against:
  - Pillar 7 §3.1: Relative Pollen Frequency (RPF), Bray-Curtis, Cosine, Canberra, 6 Biomes
  - Pillar 7 §3.2: Soil eDNA Metagenomics (16S rRNA V4 & ITS ASVs) & Spatial Regression
  - Pillar 7 §8: ISO/IEC 17025:2017 & ENFSI 7-Tier Reporting Standards
"""

import pytest
import math
from backend.node.services.forensic.geoint.palynology_edna_engine import (
    PalynologyEdnaEngine,
    BiomeCategory,
    BiomeClassificationResult,
    EdnaSpatialPredictionResult,
    PalynologyComparisonResult,
)


@pytest.fixture
def engine():
    return PalynologyEdnaEngine()


class TestPalynologyEdnaEngine:

    def test_rpf_normalization_and_grain_count_validation(self, engine: PalynologyEdnaEngine):
        """
        Validates Relative Pollen Frequency (RPF) normalization to 100% and total count (§3.1).
        """
        raw_counts = {
            "Quercus": 150,
            "Fagus": 90,
            "Pinus": 30,
            "Poaceae": 30,
        }
        rpf, total = engine.normalize_rpf(raw_counts)

        assert total == 300
        assert pytest.approx(sum(rpf.values()), 1e-2) == 100.0
        assert rpf["Quercus"] == 50.0
        assert rpf["Fagus"] == 30.0
        assert rpf["Pinus"] == 10.0
        assert rpf["Poaceae"] == 10.0

    def test_bray_curtis_cosine_canberra_metrics(self, engine: PalynologyEdnaEngine):
        """
        Validates mathematical properties of Bray-Curtis, Cosine, and Canberra distance metrics (§3.1).
        """
        u = {"Quercus": 60.0, "Fagus": 30.0, "Pinus": 10.0}
        v = {"Quercus": 60.0, "Fagus": 30.0, "Pinus": 10.0}
        w = {"Salsola": 70.0, "Salicornia": 30.0}

        # Identical profiles
        d_bc_ident = engine.compute_bray_curtis_dissimilarity(u, v)
        s_cos_ident = engine.compute_cosine_similarity(u, v)
        d_can_ident = engine.compute_canberra_distance(u, v)

        assert d_bc_ident == 0.0
        assert s_cos_ident == 1.0
        assert d_can_ident == 0.0

        # Completely disjoint / orthogonal profiles
        d_bc_disjoint = engine.compute_bray_curtis_dissimilarity(u, w)
        s_cos_disjoint = engine.compute_cosine_similarity(u, w)

        assert d_bc_disjoint == 1.0
        assert s_cos_disjoint == 0.0

    def test_6_biome_classification_accuracy(self, engine: PalynologyEdnaEngine):
        """
        Validates ecological classification across all 6 canonical terrestrial biomes (§3.1).
        """
        # 1. Deciduous Forest (Oak, Beech, Hornbeam)
        deciduous_rpf = {"Quercus": 55.0, "Fagus": 25.0, "Carpinus": 15.0, "Poaceae": 5.0}
        res_dec = engine.classify_biome(deciduous_rpf)
        assert res_dec.primary_biome == BiomeCategory.DECIDUOUS_FOREST
        assert res_dec.confidence_score >= 0.85
        assert res_dec.ecological_canopy_coverage_pct >= 80.0

        # 2. Coniferous Forest (Pine, Spruce, Fir)
        coniferous_rpf = {"Pinus": 65.0, "Picea": 20.0, "Abies": 10.0, "Betula": 5.0}
        res_con = engine.classify_biome(coniferous_rpf)
        assert res_con.primary_biome == BiomeCategory.CONIFEROUS_FOREST
        assert res_con.confidence_score >= 0.85

        # 3. Grassland / Steppe (Grasses, Asteraceae, Artemisia)
        steppe_rpf = {"Poaceae": 50.0, "Asteraceae": 30.0, "Artemisia": 15.0, "Quercus": 5.0}
        res_stp = engine.classify_biome(steppe_rpf)
        assert res_stp.primary_biome == BiomeCategory.GRASSLAND_STEPPE

        # 4. Urban / Ruderal (Plantain, Nettle, Ambrosia)
        urban_rpf = {"Plantago": 40.0, "Urtica": 30.0, "Ambrosia": 20.0, "Poaceae": 10.0}
        res_urb = engine.classify_biome(urban_rpf)
        assert res_urb.primary_biome == BiomeCategory.URBAN_RUDERAL

        # 5. Agricultural / Cereal (Cerealia, Centaurea)
        agri_rpf = {"Cerealia": 50.0, "Secale": 25.0, "Centaurea": 15.0, "Poaceae": 10.0}
        res_agr = engine.classify_biome(agri_rpf)
        assert res_agr.primary_biome == BiomeCategory.AGRICULTURAL_CEREAL

        # 6. Coastal / Halophyte (Salsola, Salicornia, Rhizophora)
        coastal_rpf = {"Salicornia": 45.0, "Salsola": 35.0, "Rhizophora": 15.0, "Poaceae": 5.0}
        res_cst = engine.classify_biome(coastal_rpf)
        assert res_cst.primary_biome == BiomeCategory.COASTAL_HALOPHYTE

    def test_edna_microbial_spatial_regression(self, engine: PalynologyEdnaEngine):
        """
        Validates Random Forest eDNA spatial regression over 16S and ITS ASVs (§3.2).
        """
        asv_sample = {
            "Acidobacteriota_ASV01": 24.5,
            "Actinomycetota_ASV04": 18.2,
            "Pseudomonadota_ASV09": 15.1,
            "Planctomycetota_ASV12": 8.4,
            "Ascomycota_ITS_02": 22.0,
            "Basidiomycota_ITS_07": 11.8,
        }
        res = engine.predict_edna_spatial_centroid(asv_sample)

        assert 45.0 <= res.predicted_latitude <= 55.0
        assert 5.0 <= res.predicted_longitude <= 15.0
        assert res.out_of_bag_variance_sigma_sq > 0.0
        assert res.confidence_radius_km > 0.0
        assert len(res.dominant_bacterial_phyla) >= 1

    def test_palynology_prosecutors_fallacy_shield(self, engine: PalynologyEdnaEngine):
        """
        Validates ISO 17025 evaluative comparison and Prosecutor's Fallacy Shield (§8.2).
        """
        q_counts = {"Quercus": 160, "Fagus": 90, "Pinus": 30, "Poaceae": 20}
        c_counts = {"Quercus": 155, "Fagus": 95, "Pinus": 28, "Poaceae": 22}

        res = engine.compare_palynology_samples(
            questioned_counts=q_counts,
            control_counts=c_counts,
            questioned_id="SAMPLE_BOOT_01",
            control_id="SCENE_HABITAT_01",
        )

        assert res.bray_curtis_dissimilarity <= 0.05
        assert res.cosine_spectral_similarity >= 0.98
        assert res.likelihood_ratio >= 1500.0
        assert res.enfsi_verbal_tier == "TIER_4_STRONG"
        assert "PROSECUTOR'S FALLACY SHIELD" in res.prosecutors_fallacy_shield
        assert "ISO 17025" in res.prosecutors_fallacy_shield

    def test_fastapi_palynology_edna_endpoint(self):
        """
        Validates FastAPI endpoint POST /api/v1/forensic/geoint/palynology-edna-analysis.
        """
        from fastapi.testclient import TestClient
        from backend.app.main import app

        client = TestClient(app)
        payload = {
            "case_id": "CASE-GEO-2026-PALYNO",
            "questioned_sample": {
                "sample_id": "GEO_03_JACKET",
                "raw_taxon_counts": {
                    "Quercus": 160,
                    "Fagus": 90,
                    "Carpinus": 30,
                    "Poaceae": 20,
                },
            },
            "known_control_sample": {
                "sample_id": "GEO_03_FOREST_SCENE",
                "raw_taxon_counts": {
                    "Quercus": 155,
                    "Fagus": 95,
                    "Carpinus": 28,
                    "Poaceae": 22,
                },
            },
            "edna_asv_profile": {
                "target_locus": "16S_V4_ITS",
                "asv_relative_abundances": {
                    "Acidobacteriota_ASV01": 25.0,
                    "Actinomycetota_ASV04": 20.0,
                    "Pseudomonadota_ASV09": 15.0,
                    "Ascomycota_ITS_02": 25.0,
                    "Basidiomycota_ITS_07": 15.0,
                },
            },
        }

        response = client.post("/api/v1/forensic/geoint/palynology-edna-analysis", json=payload)
        assert response.status_code == 200
        data = response.json()

        assert data["case_id"] == "CASE-GEO-2026-PALYNO"
        assert data["questioned_sample_id"] == "GEO_03_JACKET"
        assert data["control_sample_id"] == "GEO_03_FOREST_SCENE"
        assert data["bray_curtis_dissimilarity"] <= 0.10
        assert data["cosine_spectral_similarity"] >= 0.98
        assert data["questioned_primary_biome"] == "DECIDUOUS_FOREST"
        assert data["control_primary_biome"] == "DECIDUOUS_FOREST"
        assert data["likelihood_ratio"] >= 1500.0
        assert data["edna_predicted_latitude"] is not None
        assert data["edna_predicted_longitude"] is not None
        assert "PROSECUTOR'S FALLACY SHIELD" in data["prosecutors_fallacy_shield"]
