"""
Unit and Integration Tests for Forensic Metagenomics API Routes & ISO 17025 Certification.
Covers:
- /api/v1/forensic/metagenomics/catalog
- /api/v1/forensic/metagenomics/classify-reads
- /api/v1/forensic/metagenomics/coda-provenance
- /api/v1/forensic/metagenomics/calibrated-lr
- /api/v1/forensic/metagenomics/golden-vectors
- /api/v1/forensic/metagenomics/generate-meta-iso-report (Full 8-Section ISO 17025 Certificate Compiler)
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_metagenomics_catalog_api():
    """Test /api/v1/forensic/metagenomics/catalog endpoint."""
    response = client.get("/api/v1/forensic/metagenomics/catalog")
    assert response.status_code == 200
    data = response.json()
    assert "classifiers" in data
    assert "amplicon_loci" in data
    assert "coda_methods" in data
    assert len(data["classifiers"]) >= 6

def test_classify_reads_api():
    """Test /api/v1/forensic/metagenomics/classify-reads endpoint."""
    payload = {
        "sample_id": "TEST_TRACE_01",
        "engine": "KRAKEN2",
        "reads": [
            {"sequence": "ACGTACGTACGTACGTACGTACGTACGTACGT", "read_id": "R001"},
            {"sequence": "TGCATGCATGCATGCATGCATGCATGCATGCA", "read_id": "R002"}
        ],
        "confidence_threshold": 0.0,
        "reference_db": "STANDARD",
        "min_k_uniq": 2000,
        "apply_dark_matter_filter": True
    }
    response = client.post("/api/v1/forensic/metagenomics/classify-reads", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "abundance_vector" in data
    assert "f_unclass" in data
    assert data["sample_id"] == "TEST_TRACE_01"

def test_coda_provenance_api():
    """Test /api/v1/forensic/metagenomics/coda-provenance endpoint."""
    payload = {
        "sample_abundance_vectors": {
            "Q_SOIL": {
                "1224": 0.28,
                "201174": 0.20,
                "976": 0.16,
                "1239": 0.12,
                "200795": 0.10,
                "544448": 0.08,
                "74152": 0.06
            },
            "REF_SOIL": {
                "1224": 0.27,
                "201174": 0.21,
                "976": 0.15,
                "1239": 0.13,
                "200795": 0.09,
                "544448": 0.09,
                "74152": 0.06
            }
        },
        "compute_bray_curtis": True
    }
    response = client.post("/api/v1/forensic/metagenomics/coda-provenance", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "aitchison_distance_matrix" in data
    assert "clr_vectors" in data
    dist = data["aitchison_distance_matrix"][0][1]
    assert dist < 0.5  # Very similar compositions

def test_calibrated_lr_api():
    """Test /api/v1/forensic/metagenomics/calibrated-lr endpoint."""
    payload = {
        "sample_id": "Q_BOOT_TRACE",
        "reference_site_id": "CRIME_SCENE_REF",
        "questioned_abundance": {
            "1224": 0.28,
            "201174": 0.20,
            "976": 0.16,
            "1239": 0.12,
            "200795": 0.10,
            "544448": 0.08,
            "74152": 0.06
        },
        "reference_abundance": {
            "1224": 0.27,
            "201174": 0.21,
            "976": 0.15,
            "1239": 0.13,
            "200795": 0.09,
            "544448": 0.09,
            "74152": 0.06
        },
        "total_reads": 50000,
        "u_c": 0.5
    }
    response = client.post("/api/v1/forensic/metagenomics/calibrated-lr", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "log10_lr_fused" in data
    assert "enfsi_tier" in data
    assert "prosecutors_fallacy_shield_en" in data
    assert "prosecutors_fallacy_shield_tr" in data

def test_golden_vectors_api():
    """Test /api/v1/forensic/metagenomics/golden-vectors endpoint."""
    response = client.get("/api/v1/forensic/metagenomics/golden-vectors")
    assert response.status_code == 200
    data = response.json()
    assert "vectors" in data
    assert len(data["vectors"]) >= 5

def test_generate_meta_iso_report_api():
    """Test /api/v1/forensic/metagenomics/generate-meta-iso-report endpoint."""
    payload = {
        "case_id": "CASE-2026-META-001",
        "sample_id": "Q-EVID-SOIL-77",
        "reference_site_id": "REF-CRIME-SCENE-01",
        "investigator_name": "Dr. E. Vance, Forensic Biologist",
        "primary_analyst_id": "ANALYST-01 (Dr. Jane Doe)",
        "technical_reviewer_id": "REVIEWER-02 (Dr. John Smith)",
        "aitchison_distance": 0.245,
        "log10_lr_metagenomics": 2.70,
        "log10_lr_fused": 2.70,
        "enfsi_tier": "TIER_4_MODERATELY_STRONG_SUPPORT",
        "enfsi_verbal_en": "The metagenomic evidence provides moderately strong support for Hp over Hd.",
        "enfsi_verbal_tr": "Metagenomik deliller, Hp hipotezini Hd hipotezine karsi orta-guclu derecede desteklemektedir.",
        "prosecutors_fallacy_shield_en": "LR evaluates P(E|Hp)/P(E|Hd), not posterior probability of guilt.",
        "prosecutors_fallacy_shield_tr": "LR delillerin olabilirligini degerlendirir, dogrudan sucluluk olasiligini ifade etmez.",
        "iso_17025_u_expanded_95pct": 1.0,
        "reference_db": "GTDB_220 / SILVA_138.2",
        "top_phyla": [
            {"name": "Pseudomonadota", "abundance": 0.28},
            {"name": "Actinomycetota", "abundance": 0.20}
        ],
        "hp_description": "Questioned soil trace originated from the crime scene location.",
        "hd_description": "Questioned soil trace originated from an unrelated alternative location.",
        "qc_verdict": "QC_PASSED"
    }
    response = client.post("/api/v1/forensic/metagenomics/generate-meta-iso-report", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["certificate_title"] == "ISO 17025 OFFICIAL FORENSIC METAGENOMIC SOIL EXAMINATION REPORT"
    assert data["case_summary"]["iso_standard"] == "ISO/IEC 17025:2017"
    assert "case_summary" in data
    assert "evidence_chain" in data
    assert "methods" in data
    assert "empirical_results" in data
    assert "statistical_interpretation" in data
    assert "limitations_and_uncertainty" in data
    assert "dual_sign_off_governance" in data
    assert "audit_trail_and_cryptography" in data
    assert data["statistical_interpretation"]["log10_lr_fused"] == 2.70
    assert len(data["audit_trail_and_cryptography"]["certificate_hash"]) == 64
