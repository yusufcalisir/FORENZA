"""
Unit & Integration Tests for FORENZA Forensic Report Generator & ISO 17025 Compliance Auditor (Phase 8).
Tests ENFSI verbal scale mapping, SWGDAM report compilation, compliance rules, and API endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.node.services.forensic.models import STRGenotype, STRProfile
from backend.node.services.forensic.reports.generator import ForensicReportGenerator
from backend.node.services.forensic.reports.compliance import ComplianceAuditor
from backend.app.api.report_routes import router as report_router

_app = FastAPI()
_app.include_router(report_router, prefix="/api/v1")
client = TestClient(_app)

generator = ForensicReportGenerator()
auditor = ComplianceAuditor()


# ── 8.1 ENFSI Verbal Scale & Report Generator Tests ──────────────────────────

def test_enfsi_verbal_scale_mapping():
    assert "Extremely Strong" in generator.map_to_enfsi_verbal_scale(6.5)
    assert "Very Strong" in generator.map_to_enfsi_verbal_scale(4.5)
    assert "Strong Support for Prosecution" in generator.map_to_enfsi_verbal_scale(3.0)
    assert "Inconclusive" in generator.map_to_enfsi_verbal_scale(0.0)
    assert "Defense Hypothesis" in generator.map_to_enfsi_verbal_scale(-3.0)


def test_compile_certificate_inclusion():
    cert = generator.compile_certificate(
        evidence_id="EVID-101",
        suspect_id="SUSPECT-202",
        lr_value=482109.34,
        log10_lr=5.6831,
        population="Caucasian"
    )
    assert cert.match_status == "INCLUSION"
    assert cert.hpd_interval_low < cert.lr_value
    assert cert.hpd_interval_high > cert.lr_value
    assert cert.swgdam_compliance_passed is True
    assert cert.report_id.startswith("FORENZA-CERT-")


# ── 8.2 Compliance Auditor Tests ─────────────────────────────────────────────

def _sample_full_profile() -> STRProfile:
    loci = {}
    names = ["TH01", "FGA", "VWA", "TPOX", "CSF1PO", "D3S1358", "D5S818",
             "D7S820", "D8S1179", "D13S317", "D16S539", "D18S51", "D21S11", "AMEL"]
    for n in names:
        loci[n] = STRGenotype(n, 10.0, 11.0)
    return STRProfile(profile_id="FULL_PROFILE_01", loci=loci)


def test_compliance_auditor_full_profile():
    report = auditor.audit_profile_compliance(_sample_full_profile(), theta_applied=0.01, has_zkp_proof=True)
    assert report.total_checks == 5
    assert report.passed_checks == 5
    assert report.compliance_score == 1.0
    assert report.iso17025_status == "ACCREDITED_COMPLIANT"


def test_compliance_auditor_partial_profile_warning():
    # Only 5 loci -> fails RULE-101
    loci = {"TH01": STRGenotype("TH01", 6.0, 9.3)}
    prof = STRProfile(profile_id="PARTIAL_01", loci=loci)
    report = auditor.audit_profile_compliance(prof, theta_applied=0.005, has_zkp_proof=False)

    assert report.passed_checks < 5
    assert len(report.warnings) >= 2


# ── 8.3 API Endpoint Integration Tests ───────────────────────────────────────

def test_api_generate_report():
    payload = {
        "evidence_id": "EVID-99",
        "suspect_id": "SUS-99",
        "lr_value": 15000.0,
        "log10_lr": 4.176,
        "population": "Caucasian"
    }
    resp = client.post("/api/v1/forensic/reports/generate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "report_id" in data
    assert data["match_status"] == "INCLUSION"
    assert "Very Strong" in data["enfsi_verbal_scale"]


def test_api_audit_compliance():
    payload = {
        "profile": {
            "profile_id": "AUDIT_PROV_01",
            "population_group": "Caucasian",
            "loci": [
                {"locus": "TH01", "allele1": 6.0, "allele2": 9.3},
                {"locus": "FGA", "allele1": 20.0, "allele2": 22.0},
                {"locus": "VWA", "allele1": 16.0, "allele2": 18.0},
                {"locus": "TPOX", "allele1": 8.0, "allele2": 11.0},
                {"locus": "CSF1PO", "allele1": 10.0, "allele2": 12.0},
                {"locus": "D3S1358", "allele1": 14.0, "allele2": 15.0},
                {"locus": "D5S818", "allele1": 11.0, "allele2": 12.0},
                {"locus": "D7S820", "allele1": 10.0, "allele2": 11.0},
                {"locus": "D8S1179", "allele1": 13.0, "allele2": 14.0},
                {"locus": "D13S317", "allele1": 11.0, "allele2": 12.0},
                {"locus": "D16S539", "allele1": 11.0, "allele2": 12.0},
                {"locus": "D18S51", "allele1": 14.0, "allele2": 15.0},
                {"locus": "D21S11", "allele1": 28.0, "allele2": 30.0},
                {"locus": "AMEL", "allele1": 1.0, "allele2": 2.0}
            ]
        },
        "theta_applied": 0.01,
        "has_zkp_proof": True
    }
    resp = client.post("/api/v1/forensic/reports/audit", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["compliance_score"] == 1.0
    assert data["iso17025_status"] == "ACCREDITED_COMPLIANT"
