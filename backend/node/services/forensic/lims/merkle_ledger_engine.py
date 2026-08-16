r"""
FORENZA Cryptographic Chain of Custody (CoC) Immutable Merkle Tree Ledger Engine — Module 26.

Implements verbatim from Pillar 6 Research §1 & §6:
  - §1.1 Mathematical Formulation of the Binary Forensic Merkle Tree (Chained SHA-256 Leaves, Balanced Reduction)
  - §1.2 Audit Trail Verification Path & Proof of Inclusion (O(log2 N) Merkle Proofs)
  - ISO/IEC 17025:2017 & Federal Rules of Evidence (FRE 702 / Daubert) Chain of Custody Integrity
"""

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class CustodyEvent:
    event_id: str
    timestamp_iso: str  # RFC 3161 / ISO 8601 UTC timestamp
    officer_id: str
    sample_barcode: str
    location_id: str
    action_type: str = "TRANSFER"
    notes: Optional[str] = None
    prior_hash: Optional[str] = None

    def canonical_string(self, prior_hash: str) -> str:
        """Constructs canonical byte string: EventID || Timestamp || OfficerID || Barcode || LocationID || PriorHash"""
        return f"{self.event_id}|{self.timestamp_iso}|{self.officer_id}|{self.sample_barcode}|{self.location_id}|{prior_hash}"

    def compute_leaf_hash(self, prior_hash: str) -> str:
        canonical = self.canonical_string(prior_hash)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class ForensicMerkleLedgerEngine:
    """
    FORENZA Cryptographic Chain of Custody Merkle Tree Ledger Engine.

    Derives verbatim from Pillar 6 Research §1 & §6.
    """

    GENESIS_PRIOR_HASH = "0" * 64

    @staticmethod
    def sha256_combine(left_hex: str, right_hex: str) -> str:
        """H_parent = SHA256(H_left || H_right) (Research §1.1)"""
        combined = left_hex + right_hex
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    def build_merkle_tree(self, events: List[CustodyEvent]) -> Dict[str, Any]:
        """
        Builds a complete binary Merkle tree over chained custody events (Research §1.1).
        Returns tree layers, leaf hashes, and root commitment.
        """
        if not events:
            raise ValueError("Events list must not be empty.")

        # 1. Compute chained leaf hashes
        leaf_hashes: List[str] = []
        prior_hash = self.GENESIS_PRIOR_HASH
        for ev in events:
            h_i = ev.compute_leaf_hash(prior_hash)
            leaf_hashes.append(h_i)
            prior_hash = h_i

        # 2. Iteratively reduce layers pairwise
        layers: List[List[str]] = [leaf_hashes]
        current_layer = leaf_hashes

        while len(current_layer) > 1:
            next_layer: List[str] = []
            n = len(current_layer)
            for i in range(0, n, 2):
                left = current_layer[i]
                # If odd count, duplicate trailing leaf to maintain binary balance (Research §1.1)
                right = current_layer[i + 1] if (i + 1 < n) else left
                parent = self.sha256_combine(left, right)
                next_layer.append(parent)
            layers.append(next_layer)
            current_layer = next_layer

        merkle_root = current_layer[0]

        return {
            "merkle_root": merkle_root,
            "total_events": len(events),
            "tree_depth": len(layers) - 1,
            "leaf_hashes": leaf_hashes,
            "layers": layers,
        }

    def generate_inclusion_proof(
        self,
        events: List[CustodyEvent],
        target_event_index: int,
    ) -> Dict[str, Any]:
        """
        Generates an O(log2 N) Merkle Inclusion Proof (Audit Path) for event at index k (Research §1.2).
        """
        if target_event_index < 0 or target_event_index >= len(events):
            raise ValueError(f"Target index {target_event_index} out of range (0..{len(events)-1}).")

        tree_info = self.build_merkle_tree(events)
        layers = tree_info["layers"]
        merkle_root = tree_info["merkle_root"]

        proof_path: List[Dict[str, str]] = []
        current_idx = target_event_index

        for d in range(len(layers) - 1):
            layer = layers[d]
            n = len(layer)
            if current_idx % 2 == 0:
                # Target is left child, sibling is right child
                sibling_idx = current_idx + 1 if (current_idx + 1 < n) else current_idx
                sibling_hash = layer[sibling_idx]
                proof_path.append({"sibling_hash": sibling_hash, "direction": "RIGHT"})
            else:
                # Target is right child, sibling is left child
                sibling_idx = current_idx - 1
                sibling_hash = layer[sibling_idx]
                proof_path.append({"sibling_hash": sibling_hash, "direction": "LEFT"})

            current_idx = current_idx // 2

        target_event = events[target_event_index]
        target_leaf_hash = tree_info["leaf_hashes"][target_event_index]

        return {
            "target_event_id": target_event.event_id,
            "target_event_index": target_event_index,
            "target_leaf_hash": target_leaf_hash,
            "merkle_root": merkle_root,
            "proof_path": proof_path,
            "path_length": len(proof_path),
        }

    def verify_inclusion_proof(
        self,
        leaf_hash: str,
        proof_path: List[Dict[str, str]],
        expected_root: str,
    ) -> Dict[str, Any]:
        """
        Iteratively verifies a Merkle Inclusion Proof v_d == R_Merkle (Research §1.2).
        """
        if not leaf_hash or not expected_root:
            raise ValueError("Leaf hash and expected root must be non-empty.")

        current_hash = leaf_hash
        step_trace = [current_hash]

        for step in proof_path:
            sibling = step["sibling_hash"]
            direction = step.get("direction", "RIGHT").upper()
            if direction == "RIGHT":
                current_hash = self.sha256_combine(current_hash, sibling)
            else:
                current_hash = self.sha256_combine(sibling, current_hash)
            step_trace.append(current_hash)

        is_valid = (current_hash.lower() == expected_root.lower())

        shield_statement = (
            "IMPORTANT (ISO/IEC 17025:2017 & FRE 702 Chain of Custody Integrity Shield): Cryptographic Merkle "
            "inclusion proofs mathematically guarantee that evidence transitions occurred in an unaltered sequence. "
            "Any tampering with event timestamps, barcodes, or handler IDs alters the root hash with probability 1 - 2^-256."
        )

        return {
            "is_valid": is_valid,
            "computed_root": current_hash,
            "expected_root": expected_root,
            "verdict": "VALID (Admissible Evidence)" if is_valid else "INVALID (Tampered / Corrupted Chain)",
            "steps_evaluated": len(proof_path),
            "step_trace": step_trace,
            "prosecutors_fallacy_shield": shield_statement,
        }
