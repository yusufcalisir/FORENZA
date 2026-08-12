import pytest
from backend.node.services.forensic.lims.workflow_tracker import LimsWorkflowTracker


def test_create_case_and_accession_sample():
    tracker = LimsWorkflowTracker()
    case = tracker.create_case("CASE-2026-LIMS-01", "Dr. Sarah Connor")
    assert case["case_id"] == "CASE-2026-LIMS-01"
    assert case["status"] == "OPEN"

    sample = tracker.accession_sample("CASE-2026-LIMS-01", "SAMPLE-DNA-101", "Blood Stain", "Tech John")
    assert sample["sample_id"] == "SAMPLE-DNA-101"
    assert sample["current_step"] == "SAMPLE_ACCESSIONING"


def test_record_workflow_step_and_audit_chain():
    tracker = LimsWorkflowTracker()
    tracker.create_case("CASE-2026-02", "Investigator Miller")
    tracker.accession_sample("CASE-2026-02", "SAMPLE-DNA-102", "Saliva", "Tech Alice")

    step = tracker.record_workflow_step(
        sample_id="SAMPLE-DNA-102",
        step_name="DNA_EXTRACTION",
        operator_id="OP-042",
        instrument_id="QIAGEN_EZ1_01",
        reagent_lot="LOT-EXT-994",
        protocol_version="ISO-SOP-EXT-v2.1",
        step_result="Extracted 150 uL DNA solution",
        pass_qc=True
    )

    assert step["step_name"] == "DNA_EXTRACTION"
    assert step["hmac_signature"] is not None

    custody = tracker.get_chain_of_custody("SAMPLE-DNA-102")
    assert custody["chain_intact"] is True
    assert custody["total_steps_completed"] == 2


def test_duplicate_case_id_raises_error():
    tracker = LimsWorkflowTracker()
    tracker.create_case("CASE-DUP", "Investigator A")
    with pytest.raises(ValueError, match="already registered"):
        tracker.create_case("CASE-DUP", "Investigator B")


def test_accession_non_existent_case_raises_error():
    tracker = LimsWorkflowTracker()
    with pytest.raises(ValueError, match="not found"):
        tracker.accession_sample("NON-EXISTENT", "SAMPLE-1", "Hair", "Tech")


def test_invalid_workflow_step_raises_error():
    tracker = LimsWorkflowTracker()
    tracker.create_case("CASE-STEP-ERR", "Investigator A")
    tracker.accession_sample("CASE-STEP-ERR", "SAMPLE-ERR", "Touch DNA", "Tech")
    with pytest.raises(ValueError, match="Invalid workflow step"):
        tracker.record_workflow_step("SAMPLE-ERR", "INVALID_STEP_NAME", "OP", "INST", "LOT", "SOP", "RES")


def test_hmac_chain_integrity_tampering_detected():
    tracker = LimsWorkflowTracker()
    tracker.create_case("CASE-TAMPER", "Investigator A")
    tracker.accession_sample("CASE-TAMPER", "SAMPLE-TAMPER", "Bone", "Tech")
    tracker.record_workflow_step("SAMPLE-TAMPER", "DNA_EXTRACTION", "OP-1", "INST-1", "LOT-1", "SOP-1", "OK")

    # Manually tamper with audit trail
    tracker._audit_trails["SAMPLE-TAMPER"][1]["step_result"] = "TAMPERED_RESULT"

    custody = tracker.get_chain_of_custody("SAMPLE-TAMPER")
    assert custody["chain_intact"] is False
