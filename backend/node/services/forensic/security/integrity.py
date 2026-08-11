"""
FORENZA System-Wide Cryptographic Audit & Provenance Integrity Engine.
Implements HMAC-SHA256 profile signature verification and tamper-evident SHA-256
hash chaining across forensic audit logs for chain-of-custody compliance.
"""

import hashlib
import hmac
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AuditLogBlock:
    index: int
    timestamp: float
    event_type: str
    payload_hash: str
    previous_hash: str
    block_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "payload_hash": self.payload_hash,
            "previous_hash": self.previous_hash,
            "block_hash": self.block_hash,
        }


class IntegrityEngine:
    """
    Cryptographic integrity verifier for forensic evidence payloads and audit log chains.
    """

    def __init__(self, secret_key: str = "FORENZA_FORENSIC_SECRET_2026"):
        self.secret_key = secret_key.encode("utf-8")
        self.chain: List[AuditLogBlock] = []

        # Initialize Genesis Block
        self._append_block("GENESIS_EVENT", {"genesis": "FORENZA Audit Genesis Block"})

    def compute_hmac_signature(self, payload: Dict[str, Any]) -> str:
        """Computes HMAC-SHA256 signature for a JSON-serializable payload."""
        canonical_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hmac.new(self.secret_key, canonical_bytes, hashlib.sha256).hexdigest()

    def verify_hmac_signature(self, payload: Dict[str, Any], expected_signature: str) -> bool:
        """Verifies HMAC-SHA256 signature against an expected hash."""
        computed = self.compute_hmac_signature(payload)
        return hmac.compare_digest(computed, expected_signature)

    def compute_payload_hash(self, payload: Dict[str, Any]) -> str:
        """Computes SHA-256 digest of a payload."""
        canonical_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(canonical_bytes).hexdigest()

    def _append_block(self, event_type: str, payload: Dict[str, Any]) -> AuditLogBlock:
        """Creates and appends a tamper-evident block to the audit hash chain."""
        index = len(self.chain)
        timestamp = time.time()
        prev_hash = self.chain[-1].block_hash if self.chain else "0" * 64
        payload_hash = self.compute_payload_hash(payload)

        block_contents = f"{index}:{timestamp}:{event_type}:{payload_hash}:{prev_hash}".encode("utf-8")
        block_hash = hashlib.sha256(block_contents).hexdigest()

        block = AuditLogBlock(
            index=index,
            timestamp=timestamp,
            event_type=event_type,
            payload_hash=payload_hash,
            previous_hash=prev_hash,
            block_hash=block_hash
        )
        self.chain.append(block)
        return block

    def log_event(self, event_type: str, payload: Dict[str, Any]) -> AuditLogBlock:
        return self._append_block(event_type, payload)

    def verify_chain_integrity(self) -> bool:
        """
        Verifies the cryptographic integrity of the entire audit chain.
        Returns True if hash chain is untampered, False otherwise.
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]

            if current.previous_hash != prev.block_hash:
                return False

            block_contents = f"{current.index}:{current.timestamp}:{current.event_type}:{current.payload_hash}:{current.previous_hash}".encode("utf-8")
            recomputed = hashlib.sha256(block_contents).hexdigest()
            if recomputed != current.block_hash:
                return False

        return True
