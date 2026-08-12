"""
FORENZA LIMS-Lite Sample Accessioning & Workflow Tracking Subsystem.

Tracks 9-step forensic laboratory workflow:
1. Case Registration
2. Evidence Ingestion
3. Sample Accessioning
4. DNA Extraction
5. qPCR Quantification
6. PCR Amplification
7. Capillary Electrophoresis / NGS Sequencing
8. Biocomputational Analysis
9. ISO 17025 Analyst Review & Certification

Maintains audit metadata (operator, instrument serial, reagent lot, ISO timestamp, protocol version, QC result)
and generates HMAC-SHA256 chained audit verification logs.
"""

import hashlib
import hmac
import time
from typing import Dict, Any, List, Optional


class LimsWorkflowTracker:
    """
    Forensic Laboratory Information Management System (LIMS-Lite) Workflow Tracker.
    """

    WORKFLOW_STEPS: List[str] = [
        "CASE_REGISTRATION",
        "EVIDENCE_INGESTION",
        "SAMPLE_ACCESSIONING",
        "DNA_EXTRACTION",
        "QPCR_QUANTIFICATION",
        "PCR_AMPLIFICATION",
        "SEQUENCING_CE",
        "BIOCOMPUTATIONAL_ANALYSIS",
        "ANALYST_REVIEW_REPORT",
    ]

    HMAC_SECRET: bytes = b"FORENZA_ISO17025_LIMS_CHAIN_KEY"

    def __init__(self):
        self._cases: Dict[str, Dict[str, Any]] = {}
        self._samples: Dict[str, Dict[str, Any]] = {}
        self._audit_trails: Dict[str, List[Dict[str, Any]]] = {}

    def create_case(
        self,
        case_id: str,
        investigator_name: str,
        jurisdiction: str = "INTERPOL_MEMBER_STATE",
    ) -> Dict[str, Any]:
        """Registers a new forensic case in the LIMS system."""
        clean_id = case_id.strip().upper()
        if clean_id in self._cases:
            raise ValueError(f"Case ID '{clean_id}' already registered in LIMS.")

        case_record = {
            "case_id": clean_id,
            "investigator_name": investigator_name,
            "jurisdiction": jurisdiction,
            "created_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": "OPEN",
            "associated_sample_ids": [],
        }
        self._cases[clean_id] = case_record
        return case_record

    def accession_sample(
        self,
        case_id: str,
        sample_id: str,
        evidence_type: str,
        collector_name: str,
    ) -> Dict[str, Any]:
        """Accessions a biological sample under a registered case."""
        case_clean = case_id.strip().upper()
        sample_clean = sample_id.strip().upper()

        if case_clean not in self._cases:
            raise ValueError(f"Case ID '{case_clean}' not found.")
        if sample_clean in self._samples:
            raise ValueError(f"Sample ID '{sample_clean}' already accessionalized.")

        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        sample_record = {
            "sample_id": sample_clean,
            "case_id": case_clean,
            "evidence_type": evidence_type,
            "collector_name": collector_name,
            "accession_timestamp": timestamp,
            "current_step": "SAMPLE_ACCESSIONING",
            "current_step_index": 2,
            "qc_status": "PASS",
        }
        self._samples[sample_clean] = sample_record
        self._cases[case_clean]["associated_sample_ids"].append(sample_clean)

        # Initialize audit log with genesis HMAC signature
        genesis_payload = f"{sample_clean}|SAMPLE_ACCESSIONING|{collector_name}|{timestamp}"
        genesis_hash = hmac.new(self.HMAC_SECRET, genesis_payload.encode(), hashlib.sha256).hexdigest()

        self._audit_trails[sample_clean] = [{
            "step_name": "SAMPLE_ACCESSIONING",
            "step_index": 2,
            "operator": collector_name,
            "instrument_id": "ACCESSIONING_BENCH_01",
            "reagent_lot": "LOT-ACC-2026-01",
            "protocol_version": "ISO-SOP-ACC-v1.0",
            "timestamp": timestamp,
            "step_result": "Accessioned successfully",
            "hmac_signature": genesis_hash,
        }]

        return sample_record

    def record_workflow_step(
        self,
        sample_id: str,
        step_name: str,
        operator_id: str,
        instrument_id: str,
        reagent_lot: str,
        protocol_version: str,
        step_result: str,
        pass_qc: bool = True,
    ) -> Dict[str, Any]:
        """Records an analytical workflow step with reagent lot & HMAC audit chaining."""
        sample_clean = sample_id.strip().upper()
        step_clean = step_name.strip().upper()

        if sample_clean not in self._samples:
            raise ValueError(f"Sample ID '{sample_clean}' not found.")
        if step_clean not in self.WORKFLOW_STEPS:
            raise ValueError(f"Invalid workflow step '{step_clean}'. Allowed: {self.WORKFLOW_STEPS}")

        step_idx = self.WORKFLOW_STEPS.index(step_clean)
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        prev_hash = self._audit_trails[sample_clean][-1]["hmac_signature"]

        # Compute chained HMAC-SHA256 signature
        payload = f"{prev_hash}|{sample_clean}|{step_clean}|{operator_id}|{instrument_id}|{reagent_lot}|{timestamp}|{step_result}"
        current_hash = hmac.new(self.HMAC_SECRET, payload.encode(), hashlib.sha256).hexdigest()

        step_entry = {
            "step_name": step_clean,
            "step_index": step_idx,
            "operator": operator_id,
            "instrument_id": instrument_id,
            "reagent_lot": reagent_lot,
            "protocol_version": protocol_version,
            "timestamp": timestamp,
            "step_result": step_result,
            "pass_qc": pass_qc,
            "hmac_signature": current_hash,
        }

        self._audit_trails[sample_clean].append(step_entry)
        self._samples[sample_clean]["current_step"] = step_clean
        self._samples[sample_clean]["current_step_index"] = step_idx
        self._samples[sample_clean]["qc_status"] = "PASS" if pass_qc else "FAILED_QC"

        return step_entry

    def get_chain_of_custody(self, sample_id: str) -> Dict[str, Any]:
        """Retrieves chain of custody history and verifies HMAC hash chain integrity."""
        sample_clean = sample_id.strip().upper()
        if sample_clean not in self._samples:
            raise ValueError(f"Sample ID '{sample_clean}' not found.")

        trail = self._audit_trails.get(sample_clean, [])
        is_valid = True

        for i in range(1, len(trail)):
            prev_hash = trail[i-1]["hmac_signature"]
            curr = trail[i]
            payload = f"{prev_hash}|{sample_clean}|{curr['step_name']}|{curr['operator']}|{curr['instrument_id']}|{curr['reagent_lot']}|{curr['timestamp']}|{curr['step_result']}"
            expected_hash = hmac.new(self.HMAC_SECRET, payload.encode(), hashlib.sha256).hexdigest()
            if curr["hmac_signature"] != expected_hash:
                is_valid = False
                break

        return {
            "sample_id": sample_clean,
            "case_id": self._samples[sample_clean]["case_id"],
            "current_step": self._samples[sample_clean]["current_step"],
            "total_steps_completed": len(trail),
            "chain_intact": is_valid,
            "audit_trail": trail,
        }
