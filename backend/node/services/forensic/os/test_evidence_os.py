import pytest
from backend.node.services.forensic.os.evidence_os_orchestrator import ForensicEvidenceOS


def test_system_architecture_topology_retrieval():
    os_engine = ForensicEvidenceOS()
    arch = os_engine.get_system_architecture()
    assert arch["platform_name"] == "FORENZA Forensic Evidence OS"
    assert arch["total_subsystems"] == 30
    assert len(arch["layers"]) == 6
    assert arch["system_status"] == "OPERATIONAL_HEALTHY"


def test_unified_pipeline_end_to_end_execution():
    os_engine = ForensicEvidenceOS()
    pipe = os_engine.run_unified_pipeline(
        case_id="CASE-2026-OS-101",
        sample_id="SAMPLE-DNA-202"
    )
    assert pipe["unified_pipeline_status"] == "PIPELINE_SUCCESSFULLY_EXECUTED"
    assert "layer_1_ingestion" in pipe["execution_layers"]
    assert "layer_6_reporting" in pipe["execution_layers"]
    assert pipe["master_os_hmac_hash"] is not None


def test_pipeline_layer_4_qc_passed():
    os_engine = ForensicEvidenceOS()
    pipe = os_engine.run_unified_pipeline()
    qc = pipe["execution_layers"]["layer_4_qc"]
    assert qc["overall_qc_verdict"] == "QC_PASSED"
    assert qc["positive_control_match"] is True


def test_pipeline_layer_5_dual_sign_off():
    os_engine = ForensicEvidenceOS()
    pipe = os_engine.run_unified_pipeline(
        primary_analyst="ANALYST-01",
        technical_reviewer="PEER-02"
    )
    rev = pipe["execution_layers"]["layer_5_review"]
    assert rev["primary_analyst"] == "ANALYST-01"
    assert rev["technical_reviewer"] == "PEER-02"
    assert rev["dual_sign_off_verified"] is True


def test_pipeline_layer_6_court_admissible():
    os_engine = ForensicEvidenceOS()
    pipe = os_engine.run_unified_pipeline()
    rep = pipe["execution_layers"]["layer_6_reporting"]
    assert rep["court_admissibility_certified"] is True
    assert rep["certificate_hash"] is not None


def test_master_os_hmac_reproducibility():
    os_engine = ForensicEvidenceOS()
    p1 = os_engine.run_unified_pipeline(case_id="CASE-X")
    p2 = os_engine.run_unified_pipeline(case_id="CASE-Y")
    assert p1["master_os_hmac_hash"] != p2["master_os_hmac_hash"]
