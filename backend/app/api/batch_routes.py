"""
FORENZA Batch Processing API Router.
Exposes endpoints for submitting asynchronous batch STR matching jobs,
polling progress status, and retrieving aggregated batch results under the /batch prefix.
"""

import uuid
from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from node.services.forensic.models import STRGenotype, STRProfile
from node.services.forensic.batch.processor import BatchProcessor, BatchItemRequest
from node.services.forensic.batch.aggregator import BatchAggregator
from .batch_schemas import (
    BatchSubmitRequest, BatchSubmitResponse,
    BatchJobResponse
)

router = APIRouter(prefix="/forensic/batch", tags=["Batch Processing Engine"])

_processor = BatchProcessor(concurrency=4)
_aggregator = BatchAggregator()


def _convert_profile_input(p_in) -> STRProfile:
    loci = {}
    for l in p_in.loci:
        lname = l.locus.upper()
        loci[lname] = STRGenotype(lname, l.allele1, l.allele2)
    return STRProfile(profile_id=p_in.profile_id, loci=loci, population_group=p_in.population_group)


async def _run_batch_job_task(job_id: str, requests: list):
    """Background execution task for batch processing."""
    results = await _processor.process_batch(requests)
    _aggregator.complete_job(job_id, results)


@router.post(
    "/submit",
    response_model=BatchSubmitResponse,
    summary="Submit Batch STR Analysis Job",
    description="Submits multiple profile pairs for concurrent high-throughput LR evaluation.",
    status_code=status.HTTP_202_ACCEPTED,
)
async def submit_batch_job(
    body: BatchSubmitRequest,
    background_tasks: BackgroundTasks
) -> BatchSubmitResponse:
    job_id = f"BATCH-JOB-{uuid.uuid4().hex[:8].upper()}"
    _aggregator.create_job(job_id, len(body.items))

    batch_requests = []
    for item in body.items:
        ev_prof = _convert_profile_input(item.evidence)
        sus_prof = _convert_profile_input(item.suspect)
        batch_requests.append(BatchItemRequest(
            item_id=item.item_id,
            evidence_profile=ev_prof,
            suspect_profile=sus_prof,
            population=item.population
        ))

    # Schedule background execution
    background_tasks.add_task(_run_batch_job_task, job_id, batch_requests)

    return BatchSubmitResponse(
        job_id=job_id,
        status="PROCESSING",
        total_items=len(body.items),
        submitted_timestamp=_aggregator.get_job(job_id).submitted_timestamp,
        message="Batch job accepted for background execution."
    )


@router.get(
    "/status/{job_id}",
    response_model=BatchJobResponse,
    summary="Get Batch Job Status & Results",
    description="Polls completion status, progress percentage, and aggregated results for a submitted batch job.",
    status_code=status.HTTP_200_OK,
)
async def get_batch_status(job_id: str) -> BatchJobResponse:
    job = _aggregator.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch job ID '{job_id}' not found."
        )

    return BatchJobResponse(**job.to_dict())
