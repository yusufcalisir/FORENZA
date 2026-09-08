"""
FORENZA Crime Scene Biological Evidence Management API Router.
Exposes endpoints for Evidence Registration, Custody Transfer, and SHA-256 Chain of Custody Auditing
under the /forensic/evidence prefix.
"""

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.evidence.manager import BiologicalEvidenceManager
from .evidence_schemas import (
    RegisterEvidenceRequest, RegisterEvidenceResponse,
    TransferCustodyRequest, TransferCustodyResponse,
    AuditChainResponse, ListEvidenceResponse,
    BiologicalEvidenceItemDetail, CustodyTransferRecordSchema,
)

router = APIRouter(prefix="/forensic/evidence", tags=["Crime Scene Biological Evidence Management"])

_evidence_manager = BiologicalEvidenceManager()


@router.get(
    "/items",
    response_model=ListEvidenceResponse,
    summary="List All Registered Evidence Items",
    description="Retrieves all registered biological and physical crime scene evidence items.",
    status_code=status.HTTP_200_OK,
)
async def list_evidence_items() -> ListEvidenceResponse:
    raw_items = _evidence_manager.get_all_evidence()
    items = []
    for item in raw_items:
        history = [
            CustodyTransferRecordSchema(
                transfer_id=h.transfer_id,
                sender_id=h.sender_id,
                receiver_id=h.receiver_id,
                timestamp_utc=h.timestamp_utc,
                transfer_reason=h.transfer_reason,
                previous_hash=h.previous_hash,
                current_hash=h.current_hash,
            )
            for h in item.chain_of_custody_history
        ]
        items.append(
            BiologicalEvidenceItemDetail(
                evidence_id=item.evidence_id,
                crime_scene_id=item.crime_scene_id,
                evidence_type=item.evidence_type,
                collection_method=item.collection_method,
                collector_id=item.collector_id,
                timestamp_utc=item.timestamp_utc,
                preservation_condition=item.preservation_condition,
                container_seal_code=item.container_seal_code,
                spatial_coordinates=item.spatial_coordinates,
                chain_of_custody_history=history,
            )
        )
    return ListEvidenceResponse(total_count=len(items), items=items)



@router.post(
    "/register",
    response_model=RegisterEvidenceResponse,
    summary="Register Biological Evidence Item",
    description="Registers evidence (Bloodstain, Hair, Saliva, Touch DNA, Bone, Plant, Insect), spatial coordinates, container seal, and genesis hash.",
    status_code=status.HTTP_200_OK,
)
async def register_evidence(body: RegisterEvidenceRequest) -> RegisterEvidenceResponse:
    try:
        item = _evidence_manager.register_evidence(
            evidence_id=body.evidence_id,
            crime_scene_id=body.crime_scene_id,
            evidence_type=body.evidence_type,
            collection_method=body.collection_method,
            collector_id=body.collector_id,
            preservation_condition=body.preservation_condition,
            container_seal_code=body.container_seal_code,
            spatial_coordinates=body.spatial_coordinates
        )
        genesis = item.chain_of_custody_history[0].current_hash
        summary = f"Evidence Registered: {body.evidence_id} ({body.evidence_type}) collected by {body.collector_id}."
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Evidence registration failed: {str(exc)}"
        )

    return RegisterEvidenceResponse(
        evidence_id=item.evidence_id,
        crime_scene_id=item.crime_scene_id,
        evidence_type=item.evidence_type,
        container_seal_code=item.container_seal_code,
        genesis_hash=genesis,
        registration_summary=summary
    )


@router.post(
    "/transfer-custody",
    response_model=TransferCustodyResponse,
    summary="Transfer Custody & Update Hash Ledger",
    description="Appends custody transfer record and updates SHA-256 chain of custody hash.",
    status_code=status.HTTP_200_OK,
)
async def transfer_custody(body: TransferCustodyRequest) -> TransferCustodyResponse:
    try:
        rec = _evidence_manager.transfer_custody(
            evidence_id=body.evidence_id,
            sender_id=body.sender_id,
            receiver_id=body.receiver_id,
            transfer_reason=body.transfer_reason
        )
        summary = f"Custody Transferred: {body.evidence_id} ({body.sender_id} -> {body.receiver_id})."
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidence ID {body.evidence_id} not registered."
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Custody transfer failed: {str(exc)}"
        )

    return TransferCustodyResponse(
        evidence_id=body.evidence_id,
        transfer_id=rec.transfer_id,
        sender_id=rec.sender_id,
        receiver_id=rec.receiver_id,
        current_hash=rec.current_hash,
        transfer_summary=summary
    )


@router.get(
    "/audit-chain/{evidence_id}",
    response_model=AuditChainResponse,
    summary="Audit Chain of Custody Integrity",
    description="Verifies complete SHA-256 hash chain continuity for specified evidence ID.",
    status_code=status.HTTP_200_OK,
)
async def audit_chain_of_custody(evidence_id: str) -> AuditChainResponse:
    audit = _evidence_manager.audit_chain_of_custody(evidence_id)
    return AuditChainResponse(
        evidence_id=audit.evidence_id,
        chain_intact=audit.chain_intact,
        total_transfers=audit.total_transfers,
        latest_custodian=audit.latest_custodian,
        audit_summary=audit.audit_summary
    )
