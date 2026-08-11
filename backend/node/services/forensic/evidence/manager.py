"""
FORENZA Crime Scene Biological Evidence Management Engine.
Registers biological evidence items (Bloodstain, Hair, Saliva, Touch DNA, Tissue, Bone, Insect, Plant Material),
records 3D/GPS spatial coordinates, container seals, and enforces cryptographic SHA-256 Chain of Custody logging:
  H_k = SHA256(H_{k-1} || Sender || Receiver || Timestamp)

References:
  ISO 21043-2 (2018) Forensic Sciences — Part 2: Recognition, recording, collecting, transport and storage of items.
  NIST Special Publication 800-86 (2006) Guide to Integrating Forensic Techniques into Incident Response.
"""

import hashlib
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class CustodyTransferRecord:
    transfer_id: str
    sender_id: str
    receiver_id: str
    timestamp_utc: float
    transfer_reason: str
    previous_hash: str
    current_hash: str


@dataclass
class BiologicalEvidenceItem:
    evidence_id: str
    crime_scene_id: str
    evidence_type: str                  # 'Bloodstain', 'Hair', 'Saliva', 'TouchDNA', 'Tissue', 'Bone', 'Insect', 'PlantMaterial'
    collection_method: str               # 'Swab', 'Tape Lift', 'Excision', 'Forceps'
    collector_id: str
    timestamp_utc: float
    preservation_condition: str        # 'Dry Ambient', 'Frozen -20C', 'Refrigerated 4C'
    container_seal_code: str
    spatial_coordinates: Dict[str, float] # {'x': 2.4, 'y': 1.8, 'z': 0.5} or {'lat': 52.3, 'lon': 4.8}
    chain_of_custody_history: List[CustodyTransferRecord] = field(default_factory=list)


@dataclass
class ChainOfCustodyAudit:
    evidence_id: str
    chain_intact: bool
    total_transfers: int
    latest_custodian: str
    audit_summary: str


class BiologicalEvidenceManager:
    """
    Manages biological evidence items with cryptographic SHA-256 Chain of Custody verification.
    """

    def __init__(self):
        self.registry: Dict[str, BiologicalEvidenceItem] = {}

    def register_evidence(
        self,
        evidence_id: str,
        crime_scene_id: str,
        evidence_type: str,
        collection_method: str,
        collector_id: str,
        preservation_condition: str,
        container_seal_code: str,
        spatial_coordinates: Dict[str, float]
    ) -> BiologicalEvidenceItem:
        now = time.time()
        initial_hash = hashlib.sha256(
            f"{evidence_id}:{crime_scene_id}:{collector_id}:{container_seal_code}:{now}".encode('utf-8')
        ).hexdigest()

        initial_transfer = CustodyTransferRecord(
            transfer_id="TR-INIT",
            sender_id="CRIME_SCENE",
            receiver_id=collector_id,
            timestamp_utc=now,
            transfer_reason="Initial Evidence Collection & Sealing",
            previous_hash="GENESIS_BLOCK",
            current_hash=initial_hash
        )

        item = BiologicalEvidenceItem(
            evidence_id=evidence_id,
            crime_scene_id=crime_scene_id,
            evidence_type=evidence_type,
            collection_method=collection_method,
            collector_id=collector_id,
            timestamp_utc=now,
            preservation_condition=preservation_condition,
            container_seal_code=container_seal_code,
            spatial_coordinates=spatial_coordinates,
            chain_of_custody_history=[initial_transfer]
        )

        self.registry[evidence_id] = item
        return item

    def transfer_custody(
        self,
        evidence_id: str,
        sender_id: str,
        receiver_id: str,
        transfer_reason: str
    ) -> CustodyTransferRecord:
        if evidence_id not in self.registry:
            raise KeyError(f"Evidence ID {evidence_id} not registered in system.")

        item = self.registry[evidence_id]
        prev_hash = item.chain_of_custody_history[-1].current_hash
        now = time.time()

        raw_payload = f"{prev_hash}:{sender_id}:{receiver_id}:{transfer_reason}:{now}"
        curr_hash = hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()

        rec = CustodyTransferRecord(
            transfer_id=f"TR-{len(item.chain_of_custody_history)+1}",
            sender_id=sender_id,
            receiver_id=receiver_id,
            timestamp_utc=now,
            transfer_reason=transfer_reason,
            previous_hash=prev_hash,
            current_hash=curr_hash
        )

        item.chain_of_custody_history.append(rec)
        return rec

    def audit_chain_of_custody(self, evidence_id: str) -> ChainOfCustodyAudit:
        if evidence_id not in self.registry:
            return ChainOfCustodyAudit(evidence_id, False, 0, "UNKNOWN", "Evidence ID not registered.")

        item = self.registry[evidence_id]
        history = item.chain_of_custody_history
        intact = True

        for i in range(1, len(history)):
            if history[i].previous_hash != history[i-1].current_hash:
                intact = False
                break

        latest_custodian = history[-1].receiver_id if history else "NONE"
        summary = (
            f"Chain of Custody Audit for {evidence_id}: "
            f"Chain Intact = {intact}, Total Transfers = {len(history)}, Current Custodian = {latest_custodian}."
        )

        return ChainOfCustodyAudit(
            evidence_id=evidence_id,
            chain_intact=intact,
            total_transfers=len(history),
            latest_custodian=latest_custodian,
            audit_summary=summary
        )
