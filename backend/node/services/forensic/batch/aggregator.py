"""
FORENZA Batch Job State Tracker & Aggregator Engine.
Manages batch job states, calculates execution metrics (hit rates, mean LR, error counts),
and compiles aggregated forensic summary reports.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from .processor import BatchItemResult


@dataclass
class BatchJobSummary:
    job_id: str
    status: str                        # 'SUBMITTED', 'PROCESSING', 'COMPLETED', 'FAILED'
    total_items: int
    processed_items: int
    progress_percentage: float
    submitted_timestamp: float
    completed_timestamp: Optional[float]
    total_inclusions: int
    total_exclusions: int
    total_errors: int
    hit_rate_percentage: float
    mean_log10_lr: float
    results: List[BatchItemResult] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "job_id": self.job_id,
            "status": self.status,
            "total_items": self.total_items,
            "processed_items": self.processed_items,
            "progress_percentage": round(self.progress_percentage, 2),
            "submitted_timestamp": self.submitted_timestamp,
            "completed_timestamp": self.completed_timestamp,
            "metrics": {
                "total_inclusions": self.total_inclusions,
                "total_exclusions": self.total_exclusions,
                "total_errors": self.total_errors,
                "hit_rate_percentage": round(self.hit_rate_percentage, 2),
                "mean_log10_lr": round(self.mean_log10_lr, 4),
            },
            "results": [
                {
                    "item_id": r.item_id,
                    "processed_timestamp": r.processed_timestamp,
                    "match_status": r.match_status,
                    "lr_value": r.lr_value,
                    "log10_lr": r.log10_lr,
                    "error_message": r.error_message,
                }
                for r in self.results
            ]
        }


class BatchAggregator:
    """
    In-memory state tracker and statistical summary aggregator for batch jobs.
    """

    def __init__(self):
        self.jobs: Dict[str, BatchJobSummary] = {}

    def create_job(self, job_id: str, total_items: int) -> BatchJobSummary:
        job = BatchJobSummary(
            job_id=job_id,
            status="PROCESSING",
            total_items=total_items,
            processed_items=0,
            progress_percentage=0.0,
            submitted_timestamp=time.time(),
            completed_timestamp=None,
            total_inclusions=0,
            total_exclusions=0,
            total_errors=0,
            hit_rate_percentage=0.0,
            mean_log10_lr=0.0,
            results=[]
        )
        self.jobs[job_id] = job
        return job

    def complete_job(self, job_id: str, results: List[BatchItemResult]) -> BatchJobSummary:
        if job_id not in self.jobs:
            self.create_job(job_id, len(results))

        job = self.jobs[job_id]
        job.results = results
        job.processed_items = len(results)
        job.progress_percentage = 100.0 if job.total_items > 0 else 0.0
        job.status = "COMPLETED"
        job.completed_timestamp = time.time()

        # Compute summary metrics
        inclusions = sum(1 for r in results if r.match_status == "INCLUSION")
        exclusions = sum(1 for r in results if r.match_status == "EXCLUSION")
        errors = sum(1 for r in results if r.match_status == "ERROR")

        valid_lrs = [r.log10_lr for r in results if r.match_status != "ERROR"]
        mean_log_lr = (sum(valid_lrs) / len(valid_lrs)) if valid_lrs else 0.0
        hit_rate = (inclusions / len(results) * 100.0) if len(results) > 0 else 0.0

        job.total_inclusions = inclusions
        job.total_exclusions = exclusions
        job.total_errors = errors
        job.hit_rate_percentage = hit_rate
        job.mean_log10_lr = mean_log_lr

        return job

    def get_job(self, job_id: str) -> Optional[BatchJobSummary]:
        return self.jobs.get(job_id)
