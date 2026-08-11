"""
Unit & Integration Tests for FORENZA Batch Processing Engine (Phase 9).
Tests async batch concurrency, job state aggregation, progress tracking, and API endpoints.
"""

import asyncio
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.node.services.forensic.models import STRGenotype, STRProfile
from backend.node.services.forensic.batch.processor import BatchProcessor, BatchItemRequest
from backend.node.services.forensic.batch.aggregator import BatchAggregator
from backend.app.api.batch_routes import router as batch_router

_app = FastAPI()
_app.include_router(batch_router, prefix="/api/v1")
client = TestClient(_app)

processor = BatchProcessor(concurrency=4)
aggregator = BatchAggregator()


def _sample_profile(pid: str) -> STRProfile:
    loci = {
        "TH01": STRGenotype("TH01", 6.0, 9.3),
        "FGA": STRGenotype("FGA", 20.0, 22.0),
        "VWA": STRGenotype("VWA", 16.0, 18.0),
        "TPOX": STRGenotype("TPOX", 8.0, 11.0),
        "CSF1PO": STRGenotype("CSF1PO", 10.0, 12.0),
        "D3S1358": STRGenotype("D3S1358", 14.0, 15.0),
        "D5S818": STRGenotype("D5S818", 11.0, 12.0),
        "D7S820": STRGenotype("D7S820", 10.0, 11.0),
        "D8S1179": STRGenotype("D8S1179", 13.0, 14.0),
        "D13S317": STRGenotype("D13S317", 11.0, 12.0),
        "D16S539": STRGenotype("D16S539", 11.0, 12.0),
        "D18S51": STRGenotype("D18S51", 14.0, 15.0),
        "D21S11": STRGenotype("D21S11", 28.0, 30.0),
    }
    return STRProfile(profile_id=pid, loci=loci)


# ── 9.1 Batch Concurrency Tests ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_batch_processor_concurrent_execution():
    p1 = _sample_profile("PROFA")
    p2 = _sample_profile("PROFB")

    items = [
        BatchItemRequest(item_id=f"ITEM-{i}", evidence_profile=p1, suspect_profile=p2, population="Caucasian")
        for i in range(10)
    ]

    results = await processor.process_batch(items)
    assert len(results) == 10
    assert all(r.match_status == "INCLUSION" for r in results)
    assert all(r.lr_value > 1.0 for r in results)


# ── 9.2 Batch Aggregator Tests ───────────────────────────────────────────────

def test_batch_aggregator_metrics():
    job = aggregator.create_job("TEST-JOB-01", 5)
    assert job.status == "PROCESSING"

    from backend.node.services.forensic.batch.processor import BatchItemResult
    res_list = [
        BatchItemResult("I1", 1.0, "INCLUSION", 100.0, 2.0),
        BatchItemResult("I2", 1.0, "INCLUSION", 200.0, 2.3),
        BatchItemResult("I3", 1.0, "EXCLUSION", 0.0, -5.0),
        BatchItemResult("I4", 1.0, "ERROR", 0.0, -99.0, "Malformed data"),
    ]

    completed = aggregator.complete_job("TEST-JOB-01", res_list)
    assert completed.status == "COMPLETED"
    assert completed.total_inclusions == 2
    assert completed.total_exclusions == 1
    assert completed.total_errors == 1
    assert completed.hit_rate_percentage == 50.0


# ── 9.3 API Endpoint Integration Tests ───────────────────────────────────────

def test_api_submit_and_poll_batch():
    profile_payload = {
        "profile_id": "P1",
        "population_group": "Caucasian",
        "loci": [
            {"locus": "TH01", "allele1": 6.0, "allele2": 9.3},
            {"locus": "FGA", "allele1": 20.0, "allele2": 22.0},
            {"locus": "VWA", "allele1": 16.0, "allele2": 18.0},
            {"locus": "TPOX", "allele1": 8.0, "allele2": 11.0},
            {"locus": "CSF1PO", "allele1": 10.0, "allele2": 12.0},
            {"locus": "D3S1358", "allele1": 14.0, "allele2": 15.0},
            {"locus": "D5S818", "allele1": 11.0, "allele2": 12.0},
            {"locus": "D7S820", "allele1": 10.0, "allele2": 11.0},
            {"locus": "D8S1179", "allele1": 13.0, "allele2": 14.0},
            {"locus": "D13S317", "allele1": 11.0, "allele2": 12.0},
            {"locus": "D16S539", "allele1": 11.0, "allele2": 12.0},
            {"locus": "D18S51", "allele1": 14.0, "allele2": 15.0},
            {"locus": "D21S11", "allele1": 28.0, "allele2": 30.0}
        ]
    }

    payload = {
        "items": [
            {
                "item_id": "PAIR-1001",
                "evidence": profile_payload,
                "suspect": profile_payload,
                "population": "Caucasian"
            }
        ],
        "concurrency": 2
    }

    # 1. Submit batch job
    resp = client.post("/api/v1/forensic/batch/submit", json=payload)
    assert resp.status_code == 202
    data = resp.json()
    job_id = data["job_id"]
    assert job_id.startswith("BATCH-JOB-")

    # 2. Poll job status
    status_resp = client.get(f"/api/v1/forensic/batch/status/{job_id}")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["job_id"] == job_id
