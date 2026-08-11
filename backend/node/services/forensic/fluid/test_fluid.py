"""
Unit & Integration Tests for FORENZA Body Fluid Identification Package.
Tests mRNA gene expression profiling, multinomial fluid probability distribution,
RNA/DNA co-extraction auditing, and API endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.fluid.profiler import BodyFluidProfiler, StainSampleData, MrnaMarkerExpression
from node.services.forensic.fluid.compatibility import RnaDnaCoExtractor
from app.api.fluid_routes import router as fluid_router

_app = FastAPI()
_app.include_router(fluid_router, prefix="/api/v1")
client = TestClient(_app)

fluid_profiler = BodyFluidProfiler()
coextractor = RnaDnaCoExtractor()


# ── mRNA Profiling & Probability Tests ───────────────────────────────────────

def test_saliva_mrna_identification():
    sample = StainSampleData(
        sample_id="FLUID-101",
        mrna_expressions=[
            MrnaMarkerExpression("HTN3", 8500.0),
            MrnaMarkerExpression("STATH", 7200.0),
            MrnaMarkerExpression("HBA1", 120.0),
        ]
    )

    res = fluid_profiler.identify_body_fluid(sample)
    assert res.top_predicted_fluid == "SALIVA"
    saliva_prob = next(p for p in res.fluid_probabilities if p.fluid_type == "SALIVA")
    assert saliva_prob.probability >= 0.80


def test_semen_mrna_identification():
    sample = StainSampleData(
        sample_id="FLUID-102",
        mrna_expressions=[
            MrnaMarkerExpression("PRM1", 12000.0),
            MrnaMarkerExpression("PRM2", 9500.0),
            MrnaMarkerExpression("KLK3", 6400.0),
        ]
    )

    res = fluid_profiler.identify_body_fluid(sample)
    assert res.top_predicted_fluid == "SEMEN"
    semen_prob = next(p for p in res.fluid_probabilities if p.fluid_type == "SEMEN")
    assert semen_prob.probability >= 0.90


def test_co_extraction_audit_high_quality():
    res = coextractor.audit_co_extraction("COEXT-201", rna_yield=3.5, rin=8.5)
    assert res.str_co_extraction_compatible is True
    assert "OPTIMAL_CO_EXTRACTION" in res.recommended_strategy


# ── API Endpoint Integration Tests ───────────────────────────────────────────

def test_api_fluid_identify_endpoint():
    payload = {
        "sample": {
            "sample_id": "FLUID-SAMPLE-401",
            "mrna_expressions": [
                {"gene_symbol": "HBA1", "expression_rfu": 9400.0},
                {"gene_symbol": "HBB", "expression_rfu": 8800.0}
            ]
        }
    }

    resp = client.post("/api/v1/forensic/fluid/identify", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["sample_id"] == "FLUID-SAMPLE-401"
    assert data["top_predicted_fluid"] == "VENOUS_BLOOD"


def test_api_fluid_co_extraction_audit_endpoint():
    payload = {
        "sample_id": "COEXT-SAMPLE-801",
        "rna_yield_ng_per_ul": 2.5,
        "rin_integrity_score": 7.8
    }

    resp = client.post("/api/v1/forensic/fluid/co-extraction-audit", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["str_co_extraction_compatible"] is True
    assert data["rin_integrity_score"] == 7.8
