r"""
Unit & Integration Tests for FORENZA Cryptographic Merkle Tree Ledger Engine — Module 26.

Tests verbatim from Pillar 6 Research §1 & §6:
  - §1.1 Mathematical Formulation of the Binary Forensic Merkle Tree
  - §1.2 Audit Trail Verification Path and Proof of Inclusion

Golden Benchmarks:
  - VECTOR_P6_01 (Tamper Detection Ground Truth)
  - VECTOR_26_MERKLE_A through G
"""

import pytest
import hashlib
from typing import List
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.lims.merkle_ledger_engine import (
    ForensicMerkleLedgerEngine,
    CustodyEvent,
)
from app.api.lims_routes import router as lims_router

_app = FastAPI()
_app.include_router(lims_router, prefix="/api/v1")
client = TestClient(_app)

engine = ForensicMerkleLedgerEngine()


def _create_sample_custody_events(n: int) -> List[CustodyEvent]:
    """Helper to generate sequential synthetic custody events."""
    events = []
    for i in range(1, n + 1):
        events.append(
            CustodyEvent(
                event_id=f"EVT-{i:03d}",
                timestamp_iso=f"2026-08-16T0{i:02d}:00:00Z",
                officer_id=f"OFFICER-{i:02d}",
                sample_barcode=f"BARCODE-DNA-CASE-99{i}",
                location_id=f"LAB_ZONE_{i}",
                action_type="TRANSFER" if i > 1 else "COLLECTION",
                notes=f"Custodial transition {i}",
            )
        )
    return events


# ── VECTOR_P6_01 — Tamper Detection Ground Truth ──────────────────────────────

class TestVectorP601:
    """Verifies that altering a 1-second timestamp causes 100% root divergence and invalidates proof."""

    def test_single_second_tamper_detection(self):
        events = _create_sample_custody_events(4)
        original_tree = engine.build_merkle_tree(events)
        original_root = original_tree["merkle_root"]

        # Generate valid proof for event 2
        proof = engine.generate_inclusion_proof(events, 2)
        valid_res = engine.verify_inclusion_proof(
            leaf_hash=proof["target_leaf_hash"],
            proof_path=proof["proof_path"],
            expected_root=original_root,
        )
        assert valid_res["is_valid"] is True
        assert "VALID" in valid_res["verdict"]

        # Tamper event 2 by 1 second
        tampered_events = _create_sample_custody_events(4)
        tampered_events[2].timestamp_iso = "2026-08-16T00:03:01Z"  # 1-second shift

        tampered_tree = engine.build_merkle_tree(tampered_events)
        tampered_root = tampered_tree["merkle_root"]

        # Assert 100% root divergence
        assert tampered_root != original_root

        # Assert proof with tampered leaf against original root fails
        tampered_leaf = tampered_tree["leaf_hashes"][2]
        invalid_res = engine.verify_inclusion_proof(
            leaf_hash=tampered_leaf,
            proof_path=proof["proof_path"],
            expected_root=original_root,
        )
        assert invalid_res["is_valid"] is False
        assert "INVALID" in invalid_res["verdict"]


# ── VECTOR_26_MERKLE_A — Single Event Tree Edge Case ─────────────────────────

class TestVector26MerkleA:
    """Verifies single-event tree produces root equal to leaf hash."""

    def test_single_event_tree(self):
        events = _create_sample_custody_events(1)
        tree = engine.build_merkle_tree(events)
        assert tree["total_events"] == 1
        assert tree["tree_depth"] == 0
        assert tree["merkle_root"] == tree["leaf_hashes"][0]

        proof = engine.generate_inclusion_proof(events, 0)
        assert proof["path_length"] == 0
        ver_res = engine.verify_inclusion_proof(proof["target_leaf_hash"], proof["proof_path"], tree["merkle_root"])
        assert ver_res["is_valid"] is True


# ── VECTOR_26_MERKLE_B — Power of Two Balanced Tree (N=4, 8) ──────────────────

class TestVector26MerkleB:
    """Verifies balanced reduction for N=4 and N=8."""

    def test_power_of_two_trees(self):
        for n in [4, 8]:
            events = _create_sample_custody_events(n)
            tree = engine.build_merkle_tree(events)
            assert tree["total_events"] == n
            assert len(tree["leaf_hashes"]) == n
            # Depth should be log2(n)
            import math
            assert tree["tree_depth"] == int(math.log2(n))


# ── VECTOR_26_MERKLE_C — Odd Leaf Count Balancing Invariance ──────────────────

class TestVector26MerkleC:
    """Verifies odd leaf counts (N=3, 5, 7) handle trailing leaf duplication correctly."""

    def test_odd_leaf_counts(self):
        for n in [3, 5, 7]:
            events = _create_sample_custody_events(n)
            tree = engine.build_merkle_tree(events)
            assert tree["merkle_root"] is not None
            assert len(tree["merkle_root"]) == 64  # Hex SHA-256

            # Verify every leaf in odd tree has a valid verifiable proof
            for idx in range(n):
                proof = engine.generate_inclusion_proof(events, idx)
                ver = engine.verify_inclusion_proof(
                    leaf_hash=proof["target_leaf_hash"],
                    proof_path=proof["proof_path"],
                    expected_root=tree["merkle_root"],
                )
                assert ver["is_valid"] is True, f"Failed for n={n}, idx={idx}"


# ── VECTOR_26_MERKLE_D — O(log2 N) Proof Path Length ─────────────────────────

class TestVector26MerkleD:
    """Verifies proof path length matches ceil(log2 N)."""

    def test_proof_path_complexity(self):
        import math
        for n in [2, 4, 8, 16]:
            events = _create_sample_custody_events(n)
            proof = engine.generate_inclusion_proof(events, n - 1)
            expected_length = math.ceil(math.log2(n))
            assert proof["path_length"] == expected_length


# ── VECTOR_26_MERKLE_E — Event Order Sensitivity ──────────────────────────────

class TestVector26MerkleE:
    """Verifies swapping two events alters the Merkle root."""

    def test_event_order_permutation_alters_root(self):
        events = _create_sample_custody_events(4)
        tree_orig = engine.build_merkle_tree(events)

        swapped_events = [events[1], events[0], events[2], events[3]]
        tree_swapped = engine.build_merkle_tree(swapped_events)

        assert tree_orig["merkle_root"] != tree_swapped["merkle_root"]


# ── VECTOR_26_MERKLE_F — Domain Validation for Empty Events ───────────────────

class TestVector26MerkleF:
    """Verifies empty events list raises ValueError."""

    def test_empty_events_raise(self):
        with pytest.raises(ValueError, match="must not be empty"):
            engine.build_merkle_tree([])

        with pytest.raises(ValueError, match="out of range"):
            engine.generate_inclusion_proof(_create_sample_custody_events(2), 5)


# ── VECTOR_26_MERKLE_G — FastAPI Endpoints Integration ────────────────────────

class TestVector26MerkleG:
    """Verifies FastAPI /forensic/lims/merkle endpoints."""

    def test_api_build_tree_and_verify_proof(self):
        events_payload = [
            {
                "event_id": f"EVT-00{i}",
                "timestamp_iso": f"2026-08-16T12:0{i}:00Z",
                "officer_id": f"OFFICER-0{i}",
                "sample_barcode": "BC-12345",
                "location_id": f"ZONE-{i}",
                "action_type": "TRANSFER",
            }
            for i in range(1, 4)
        ]

        # 1. Build tree
        res_tree = client.post("/api/v1/forensic/lims/merkle/build-tree", json={"events": events_payload})
        assert res_tree.status_code == 200
        tree_data = res_tree.json()
        root = tree_data["merkle_root"]
        assert len(root) == 64

        # 2. Generate proof for index 1
        res_proof = client.post(
            "/api/v1/forensic/lims/merkle/generate-proof",
            json={"events": events_payload, "target_event_index": 1}
        )
        assert res_proof.status_code == 200
        proof_data = res_proof.json()

        # 3. Verify proof
        res_ver = client.post(
            "/api/v1/forensic/lims/merkle/verify-proof",
            json={
                "leaf_hash": proof_data["target_leaf_hash"],
                "proof_path": proof_data["proof_path"],
                "expected_root": root,
            }
        )
        assert res_ver.status_code == 200
        ver_data = res_ver.json()
        assert ver_data["is_valid"] is True
        assert "VALID" in ver_data["verdict"]
