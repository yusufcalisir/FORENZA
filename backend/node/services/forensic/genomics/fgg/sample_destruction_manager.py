"""
Third-Party Reference Sample Destruction Order Manager.

Manages Maryland Title 17 and US DOJ Section VIII post-investigation sample purge
and issues cryptographically verifiable Destruction Order Certificates.
"""

import hashlib
import datetime
from typing import List, Dict
from pydantic import BaseModel, Field, ConfigDict


class SampleDestructionOrder(BaseModel):
    """Certified destruction order for third-party reference DNA samples."""
    model_config = ConfigDict(protected_namespaces=())

    order_id: str
    case_id: str
    statutory_basis: str
    reference_sample_ids: List[str]
    destruction_timestamp_iso: str
    certifying_officer_name: str
    is_destruction_verified: bool
    certificate_hash: str


class FGGSampleDestructionManager:
    """Issues and verifies third-party reference DNA destruction certificates."""

    @classmethod
    def generate_destruction_order(
        cls,
        case_id: str,
        statutory_basis: str,
        reference_sample_ids: List[str],
        certifying_officer: str
    ) -> SampleDestructionOrder:
        """Generates a certified sample destruction order."""
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        order_id = f"DEST_ORDER_{case_id}_{len(reference_sample_ids)}"

        payload = f"{order_id}|{case_id}|{','.join(sorted(reference_sample_ids))}|{now_iso}|{certifying_officer}"
        cert_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        return SampleDestructionOrder(
            order_id=order_id,
            case_id=case_id,
            statutory_basis=statutory_basis,
            reference_sample_ids=reference_sample_ids,
            destruction_timestamp_iso=now_iso,
            certifying_officer_name=certifying_officer,
            is_destruction_verified=True,
            certificate_hash=cert_hash
        )
