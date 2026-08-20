"""
Backend Integration & Unit Test Suite for Module 1.3: NRC-II Population Genetics.
Sub-Item 1.3.5: Backend Implementation & Tests.

10 comprehensive tests validating:
  - NRCPopulationEngine service layer methods
  - 24-Locus Profile LR computation & demographic cross-comparison
  - Weir-Cockerham ANOVA & Dirichlet Compound Multinomial engines
  - FastAPI REST API endpoints (/forensic/population/nrc/...)

Run with:
    pytest backend/node/services/forensic/kinship/test_nrc.py -v
"""

import math
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from node.services.forensic.kinship.nrc_engine import NRCPopulationEngine
from node.services.forensic.population.nrc_reference_datasets import GOLDEN_REFERENCE_PROFILES


# ─────────────────────────────────────────────────────────────────────────────
# SERVICE LAYER TESTS (NRCPopulationEngine)
# ─────────────────────────────────────────────────────────────────────────────

def test_nrc_engine_profile_lr_caucasian():
    """
    Evaluates NIST SRM 2391d Component A (24 loci) using NRCPopulationEngine.
    Must compute a finite LR with log10(LR) > 20.0, reciprocal balance, and ENFSI tier.
    """
    engine = NRCPopulationEngine(default_theta=0.03)
    profile_a = GOLDEN_REFERENCE_PROFILES["SRM_2391D_COMP_A"].loci_genotypes

    res = engine.compute_profile_lr(
        suspect_profile=profile_a,
        population="Caucasian",
        theta=0.03
    )

    assert len(res.locus_results) == 24
    assert res.log10_total_lr > 20.0
    assert res.is_reciprocal_balanced is True
    assert res.reciprocal_product_delta < 1e-6
    assert res.verbal_scale_en == "Extremely strong support for inclusion (Hp)"
    assert res.verbal_scale_tr == "Dahil olma lehine son derece güçlü delil (Hp)"


def test_nrc_engine_demographic_stratification_comparison():
    """
    Evaluates multi-population demographic report across all 4 NIST 1036 demographies.
    """
    engine = NRCPopulationEngine(default_theta=0.03)
    profile_b = GOLDEN_REFERENCE_PROFILES["SRM_2391D_COMP_B"].loci_genotypes

    report = engine.evaluate_demographic_stratification(
        suspect_profile=profile_b,
        profile_id="SRM_2391D_COMP_B"
    )

    assert set(report.population_lrs.keys()) == {"Caucasian", "AfricanAmerican", "Hispanic", "Asian"}
    assert report.stratification_ratio > 1.0
    assert all(math.isfinite(lr) for lr in report.population_lrs.values())
    assert all(log_lr > 15.0 for log_lr in report.population_log10_lrs.values())


def test_nrc_engine_weir_cockerham_fst():
    """
    Evaluates Weir & Cockerham ANOVA theta_hat estimation via service engine.
    """
    engine = NRCPopulationEngine()
    counts = {
        "PopNorth": {14.0: 80, 15.0: 20},
        "PopSouth": {14.0: 20, 15.0: 80},
    }

    res = engine.estimate_weir_cockerham_fst(counts, locus="D3S1358")
    assert res.theta_hat == pytest.approx(0.5247, abs=1e-3)
    assert res.num_populations == 2
    assert res.num_alleles == 2


def test_nrc_engine_dcm_evaluation():
    """
    Evaluates Dirichlet Compound Multinomial log-likelihood via service engine.
    """
    engine = NRCPopulationEngine()
    counts = {6.0: 30, 9.3: 70}

    res = engine.evaluate_dcm_likelihood(
        allele_counts=counts,
        population="Caucasian",
        locus="TH01",
        theta=0.03
    )

    assert math.isfinite(res.log_likelihood)
    assert res.total_alleles_sampled == 100
    assert res.log_likelihood < 0.0


def test_nrc_engine_golden_profiles_lookup():
    """
    Verifies golden standard profiles listing and retrieval.
    """
    engine = NRCPopulationEngine()
    profiles_list = engine.list_golden_reference_profiles()

    assert len(profiles_list) >= 4
    profile_ids = [p["profile_id"] for p in profiles_list]
    assert "SRM_2391D_COMP_A" in profile_ids
    assert "SRM_2391D_COMP_B" in profile_ids
    assert "NA12878_CEU" in profile_ids

    profile_obj = engine.get_golden_reference_profile("SRM_2391D_COMP_A")
    assert profile_obj.sample_name.startswith("NIST SRM 2391d")


# ─────────────────────────────────────────────────────────────────────────────
# REST API ENDPOINT TESTS (FastAPI via AsyncClient)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_api_nrc_profile_lr_endpoint():
    """
    Tests POST /api/v1/forensic/population/nrc/profile-lr REST endpoint.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "suspect_profile": {
                "TH01": [6.0, 9.3],
                "D3S1358": [15.0, 16.0],
                "VWA": [16.0, 17.0],
            },
            "population": "Caucasian",
            "theta": 0.03
        }
        response = await ac.post("/api/v1/forensic/population/nrc/profile-lr", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert len(data["locus_results"]) == 3
        assert data["log10_total_lr"] > 2.0
        assert data["is_reciprocal_balanced"] is True
        assert "inclusion (Hp)" in data["verbal_scale_en"]


@pytest.mark.asyncio
async def test_api_nrc_demographic_report_endpoint():
    """
    Tests POST /api/v1/forensic/population/nrc/demographic-report REST endpoint.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "suspect_profile": {
                "TH01": [6.0, 9.3],
                "D3S1358": [15.0, 16.0],
            },
            "theta": 0.03
        }
        response = await ac.post("/api/v1/forensic/population/nrc/demographic-report", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "Caucasian" in data["population_lrs"]
        assert "AfricanAmerican" in data["population_lrs"]
        assert data["stratification_ratio"] >= 1.0


@pytest.mark.asyncio
async def test_api_nrc_weir_cockerham_endpoint():
    """
    Tests POST /api/v1/forensic/population/nrc/weir-cockerham REST endpoint.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "subpop_allele_counts": {
                "Pop1": {"14.0": 80, "15.0": 20},
                "Pop2": {"14.0": 20, "15.0": 80},
            },
            "locus": "D3S1358"
        }
        response = await ac.post("/api/v1/forensic/population/nrc/weir-cockerham", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["theta_hat"] == pytest.approx(0.5247, abs=1e-3)
        assert data["num_populations"] == 2


@pytest.mark.asyncio
async def test_api_nrc_dcm_endpoint():
    """
    Tests POST /api/v1/forensic/population/nrc/dcm REST endpoint.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "allele_counts": {"6.0": 30, "9.3": 70},
            "population": "Caucasian",
            "locus": "TH01",
            "theta": 0.03
        }
        response = await ac.post("/api/v1/forensic/population/nrc/dcm", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["total_alleles_sampled"] == 100
        assert math.isfinite(data["log_likelihood"])


@pytest.mark.asyncio
async def test_api_nrc_golden_profiles_endpoint():
    """
    Tests GET /api/v1/forensic/population/nrc/golden-profiles REST endpoint.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/forensic/population/nrc/golden-profiles")
        assert response.status_code == 200

        data = response.json()
        assert data["total_profiles"] >= 4
        profile_names = [p["profile_id"] for p in data["profiles"]]
        assert "SRM_2391D_COMP_A" in profile_names
