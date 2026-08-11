"""
FORENZA High-Throughput Batch Processing Engine.
Executes concurrent multi-profile forensic DNA analysis (LR calculations, mixture deconvolutions,
and kinship queries) across asynchronous worker task pools.
"""

import asyncio
import math
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from ..lr_engine import LREngine
from ..models import STRProfile


@dataclass
class BatchItemRequest:
    item_id: str
    evidence_profile: STRProfile
    suspect_profile: STRProfile
    population: str = "Caucasian"


@dataclass
class BatchItemResult:
    item_id: str
    processed_timestamp: float
    match_status: str
    lr_value: float
    log10_lr: float
    error_message: Optional[str] = None


class BatchProcessor:
    """
    Concurrent asynchronous batch processor for high-throughput STR profile matching.
    """

    def __init__(self, concurrency: int = 4):
        self.concurrency = concurrency
        self.lr_engine = LREngine()

    async def _process_single_item(self, item: BatchItemRequest) -> BatchItemResult:
        """Processes a single STR pair analysis item asynchronously."""
        try:
            res = self.lr_engine.compute_single_source_lr(
                evidence_profile=item.evidence_profile,
                suspect_profile=item.suspect_profile,
                population=item.population
            )
            lr_val = res.value
            match_status = res.metadata.get("match_status", "INCLUSION") if res.metadata else ("INCLUSION" if lr_val > 1.0 else "EXCLUSION")
            log10_lr = res.metadata.get("log10_lr", math.log10(max(1e-12, lr_val))) if res.metadata else math.log10(max(1e-12, lr_val))

            return BatchItemResult(
                item_id=item.item_id,
                processed_timestamp=time.time(),
                match_status=match_status,
                lr_value=round(lr_val, 2),
                log10_lr=round(log10_lr, 4),
                error_message=None
            )
        except Exception as exc:
            return BatchItemResult(
                item_id=item.item_id,
                processed_timestamp=time.time(),
                match_status="ERROR",
                lr_value=0.0,
                log10_lr=-99.0,
                error_message=str(exc)
            )

    async def process_batch(self, items: List[BatchItemRequest]) -> List[BatchItemResult]:
        """
        Executes batch processing over item list with bounded concurrency via asyncio Semaphore.
        """
        semaphore = asyncio.Semaphore(self.concurrency)

        async def worker(item: BatchItemRequest) -> BatchItemResult:
            async with semaphore:
                return await self._process_single_item(item)

        tasks = [worker(item) for item in items]
        results = await asyncio.gather(*tasks)
        return list(results)
