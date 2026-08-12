import pytest
from backend.node.services.forensic.reports.iso_report_compiler import IsoReportCompiler


def test_standard_iso_certificate_compilation():
    compiler = IsoReportCompiler()
    res = compiler.compile_iso_certificate(
        case_id="CASE-2026-LIMS-01",
        sample_id="SAMPLE-DNA-101",
        likelihood_ratio=1.0e26,
        log10_lr=26.0,
        enfsi_verbal_predicate="EXTREMELY_STRONG_SUPPORT_FOR_INCLUSION"
    )

    assert res["certificate_title"] == "ISO 17025 OFFICIAL FORENSIC GENETICS EXAMINATION REPORT"
    assert res["case_summary"]["case_id"] == "CASE-2026-LIMS-01"
    assert res["statistical_interpretation"]["log10_likelihood_ratio"] == 26.0
    assert res["statistical_interpretation"]["mathematical_immutability_flag"] == "IMMUTABLE_VERIFIED"
    assert res["audit_trail_and_cryptography"]["certificate_hash"] is not None


def test_mathematical_immutability_negative_lr_rejected():
    compiler = IsoReportCompiler()
    with pytest.raises(ValueError, match="must be strictly positive"):
        compiler.compile_iso_certificate(likelihood_ratio=-5.0)


def test_dual_sign_off_governance_included():
    compiler = IsoReportCompiler()
    res = compiler.compile_iso_certificate(
        primary_analyst_id="ANALYST-01",
        technical_reviewer_id="PEER-02",
        human_decision="APPROVE_AI_PREDICATE"
    )
    assert res["dual_sign_off_governance"]["primary_analyst_signature"] == "ANALYST-01"
    assert res["dual_sign_off_governance"]["technical_reviewer_signature"] == "PEER-02"
    assert res["dual_sign_off_governance"]["dual_sign_off_status"] == "DUAL_SIGN_OFF_VERIFIED"


def test_override_reason_captured_in_report():
    compiler = IsoReportCompiler()
    res = compiler.compile_iso_certificate(
        human_decision="OVERRIDE_MODIFIED_PREDICATE",
        override_reason="Allele dropout at locus D18S51 due to primer binding site mutation"
    )
    assert res["dual_sign_off_governance"]["override_reason"] is not None


def test_report_contains_all_8_standard_sections():
    compiler = IsoReportCompiler()
    res = compiler.compile_iso_certificate()
    sections = [
        "case_summary", "evidence_chain", "methods", "empirical_results",
        "statistical_interpretation", "limitations_and_uncertainty",
        "dual_sign_off_governance", "audit_trail_and_cryptography"
    ]
    for sec in sections:
        assert sec in res


def test_court_admissibility_certified_flag():
    compiler = IsoReportCompiler()
    res = compiler.compile_iso_certificate()
    assert res["court_admissibility_certified"] is True
