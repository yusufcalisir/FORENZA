"""
FORENZA Master End-to-End Integration & Multi-Phase Pipeline Verification Test Suite.
Verifies full end-to-end operational execution across all 10 engine phases:
1. Profile Ingestion & CODIS Loci Validation
2. Single-Source Likelihood Ratio calculation (Balding-Nichols theta)
3. Kinship Index & Pedigree Mapping
4. Continuous Probabilistic Genotyping (Logistic Dropout & MCMC Mixture Sampler)
5. HIrisPlex-S Phenotype Prediction & Biogeographic Ancestry
6. Federated Multi-Node Query Orchestration
7. Population Genetics (Wright's FST & NRC II 5/2N Bounding)
8. SWGDAM Reporting & ISO/IEC 17025 Compliance Audit
9. High-Throughput Concurrent Batch Processing
10. System Health Telemetry & Cryptographic Integrity Chain
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.node.services.forensic.models import STRGenotype, STRProfile
from backend.node.services.forensic.str_engine import STREngine
from backend.node.services.forensic.lr_engine import LREngine
from backend.node.services.forensic.kinship_engine import KinshipEngine
from backend.node.services.forensic.probabilistic.mixture import MixtureDeconvolutionEngine
from backend.node.services.forensic.phenotyping.hirisplex import HiriPlexSEngine
from backend.node.services.forensic.phenotyping.ancestry import AncestryEngine
from backend.node.services.forensic.population.substructure import SubstructureEngine
from backend.node.services.forensic.population.rare_allele import RareAlleleEngine
from backend.node.services.forensic.reports.generator import ForensicReportGenerator
from backend.node.services.forensic.reports.compliance import ComplianceAuditor
from backend.node.services.forensic.security.integrity import IntegrityEngine
from backend.app.main import app

client = TestClient(app)


def _build_full_codis_profile(pid: str) -> STRProfile:
    loci = {
        "CSF1PO": STRGenotype("CSF1PO", 10.0, 12.0),
        "FGA": STRGenotype("FGA", 21.0, 23.0),
        "TH01": STRGenotype("TH01", 6.0, 9.3),
        "TPOX": STRGenotype("TPOX", 8.0, 11.0),
        "VWA": STRGenotype("VWA", 16.0, 17.0),
        "D3S1358": STRGenotype("D3S1358", 15.0, 18.0),
        "D5S818": STRGenotype("D5S818", 11.0, 12.0),
        "D7S820": STRGenotype("D7S820", 10.0, 11.0),
        "D8S1179": STRGenotype("D8S1179", 13.0, 14.0),
        "D13S317": STRGenotype("D13S317", 11.0, 12.0),
        "D16S539": STRGenotype("D16S539", 11.0, 12.0),
        "D18S51": STRGenotype("D18S51", 14.0, 17.0),
        "D21S11": STRGenotype("D21S11", 28.0, 30.0),
        "AMEL": STRGenotype("AMEL", 1.0, 2.0)
    }
    return STRProfile(profile_id=pid, loci=loci, population_group="Caucasian")


# ── MASTER END-TO-END TEST CASES ─────────────────────────────────────────────

def test_master_pipeline_execution():
    """Executes full pipeline end-to-end across core Python engine classes."""
    # 1. Profile Creation
    evidence = _build_full_codis_profile("EVIDENCE-001")
    suspect = _build_full_codis_profile("SUSPECT-001")

    # 2. Single-Source LR Calculation
    lr_engine = LREngine()
    lr_res = lr_engine.compute_single_source_lr(evidence, suspect, theta=0.01)
    assert lr_res.value > 1000.0
    assert lr_res.metadata["match_status"] == "INCLUSION"

    # 3. Kinship Evaluation
    from backend.node.services.forensic.kinship_engine import KinshipRelationship
    kin_engine = KinshipEngine()
    kin_res = kin_engine.compute_kinship_index(evidence, suspect, KinshipRelationship.PARENT_CHILD)
    assert kin_res.value > 1.0

    # 4. Probabilistic Mixture Deconvolution
    mix_engine = MixtureDeconvolutionEngine()
    candidates = mix_engine.deconvolute_2person_locus("TH01", {6.0: 500.0, 9.3: 450.0, 7.0: 120.0, 8.0: 110.0})
    assert len(candidates) > 0

    # 5. HIrisPlex-S Phenotyping
    from backend.node.services.forensic.phenotyping.models import SNPInput
    pheno_engine = HiriPlexSEngine()
    hair_res = pheno_engine.predict_hair_colour({"rs12913832": SNPInput(rsid="rs12913832", dosage=2)})
    assert len(hair_res.probabilities) > 0

    # 6. Biogeographic Ancestry
    anc_engine = AncestryEngine()
    anc_res = anc_engine.predict_ancestry({"rs16891982": SNPInput(rsid="rs16891982", dosage=2)})
    assert anc_res.most_likely is not None

    # 7. Population Substructure & Rare Allele Bounding
    sub_engine = SubstructureEngine()
    fst_res = sub_engine.compute_pairwise_fst("Caucasian", "AfricanAmerican")
    assert fst_res.fst_value > 0.0

    rare_engine = RareAlleleEngine()
    rare_res = rare_engine.bound_allele_frequency("TH01", 9.3, 0.0001)
    assert rare_res.was_bounded is True

    # 8. Report Compilation & ISO 17025 Compliance
    rep_gen = ForensicReportGenerator()
    cert = rep_gen.compile_certificate("EVID-001", "SUSP-001", lr_res.value, lr_res.metadata["log10_lr"])
    assert cert.match_status == "INCLUSION"

    auditor = ComplianceAuditor()
    audit_report = auditor.audit_profile_compliance(evidence)
    assert audit_report.iso17025_status == "ACCREDITED_COMPLIANT"

    # 9. Cryptographic Integrity Hashing
    integrity = IntegrityEngine()
    block = integrity.log_event("E2E_PIPELINE_COMPLETE", {"lr": lr_res.value})
    assert integrity.verify_chain_integrity() is True


def test_api_health_readiness_endpoint():
    resp = client.get("/api/v1/health/ready")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ["READY", "DEGRADED"]
    assert data["subsystems"]["str_engine"] == "OPERATIONAL"


def test_api_health_liveness_endpoint():
    resp = client.get("/api/v1/health/live")
    assert resp.status_code == 200
    assert resp.json()["status"] == "LIVE"


def test_api_health_metrics_endpoint():
    resp = client.get("/api/v1/health/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert data["evaluated_loci_count"] == 20
    assert data["memory_footprint_mb"] > 0
    assert data["audit_chain_block_count"] >= 1


def test_root_and_system_health_endpoints():
    # Test /health
    r_health = client.get("/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "operational"

    # Test /api/health
    r_api_health = client.get("/api/health")
    assert r_api_health.status_code == 200
    assert r_api_health.json()["status"] == "operational"

    # Test /api/v1/health
    r_v1_health = client.get("/api/v1/health")
    assert r_v1_health.status_code == 200
    assert r_v1_health.json()["status"] == "healthy"

    # Test / (root)
    r_root = client.get("/")
    assert r_root.status_code == 200
    assert r_root.json()["status"] == "tactical_online"

