"""
Integration tests for FastAPI Metagenomic Taxonomic Classifiers & Soil Palynology API.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_api_get_metagenomics_catalog(client):
    response = client.get("/api/v1/forensic/metagenomics/catalog")
    assert response.status_code == 200
    data = response.json()
    assert "classifiers" in data
    engines = [c["engine"] for c in data["classifiers"]]
    assert "KRAKEN2" in engines
    assert "KRAKENUNIQ" in engines
    assert "BRACKEN" in engines
    assert "METAPHLAN4" in engines
    assert "amplicon_loci" in data
    assert "coda_methods" in data


def test_api_get_golden_vectors(client):
    response = client.get("/api/v1/forensic/metagenomics/golden-vectors")
    assert response.status_code == 200
    data = response.json()
    assert data["total_vectors"] == 5
    assert "VECTOR_GEO_SOIL_WGS_01" in data["vector_ids"]
    assert "VECTOR_GEO_EXCLUSION_05" in data["vector_ids"]


def test_api_get_single_golden_vector(client):
    response = client.get("/api/v1/forensic/metagenomics/golden-vectors/VECTOR_GEO_SOIL_WGS_01")
    assert response.status_code == 200
    data = response.json()
    assert data["vector_id"] == "VECTOR_GEO_SOIL_WGS_01"
    assert data["expected_top_phylum_taxid"] == 1224
    assert data["profile"]["sample_id"] == "VECTOR_GEO_SOIL_WGS_01"


def test_api_classify_reads(client):
    payload = {
        "sample_id": "TEST_SAMPLE_01",
        "engine": "KRAKEN2",
        "reads": [
            {"read_id": "READ_01", "sequence": "ATCGATCGATCGATCGATCGATCGATCGATCGATCG"},
            {"read_id": "READ_02", "sequence": "CGATCGATCGATCGATCGATCGATCGATCGATCGAT"},
        ],
        "confidence_threshold": 0.0,
        "reference_db": "STANDARD",
        "apply_dark_matter_filter": True,
    }
    response = client.post("/api/v1/forensic/metagenomics/classify-reads", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sample_id"] == "TEST_SAMPLE_01"
    assert data["engine"] == "KRAKEN2"
    assert data["total_reads"] == 2
    assert "abundance_vector" in data


def test_api_coda_provenance(client):
    payload = {
        "sample_abundance_vectors": {
            "S1": {"1224": 0.35, "201174": 0.25, "976": 0.20, "1239": 0.20},
            "S2": {"1224": 0.34, "201174": 0.26, "976": 0.19, "1239": 0.21},
            "S3": {"1224": 0.05, "201174": 0.05, "976": 0.10, "1239": 0.80},
        },
        "compute_bray_curtis": True,
    }
    response = client.post("/api/v1/forensic/metagenomics/coda-provenance", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["sample_ids"]) == 3
    assert "clr_vectors" in data
    assert "aitchison_distance_matrix" in data
    # S1 vs S2 distance should be smaller than S1 vs S3 distance
    s1_s2 = data["aitchison_distance_matrix"][0][1]
    s1_s3 = data["aitchison_distance_matrix"][0][2]
    assert s1_s2 < s1_s3


def test_api_palynology_edna(client):
    payload = {
        "sample_id": "POLLEN_TEST_01",
        "locus": "rbcL",
        "asv_sequences": [
            "ATGTCACCACAAACAGAGACTAAAGCAAGTGTTGGATTCAAAGCTGGTGTTAAAGAGTAC",
            "ATGTCACCACAAACAGAGACTAAAGCAAGTGTTGGATTCAAAGCTGGTGTTAAAGACTAC",
        ],
    }
    response = client.post("/api/v1/forensic/metagenomics/palynology-edna", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sample_id"] == "POLLEN_TEST_01"
    assert data["total_asvs"] == 2
    assert "assignments" in data


def test_api_calibrated_lr(client):
    payload = {
        "sample_id": "QUESTIONED_SOIL_01",
        "reference_site_id": "CRIME_SCENE_ALPHA",
        "questioned_abundance": {
            "1224": 0.28, "201174": 0.195, "976": 0.155, "1239": 0.12, "200795": 0.105, "29053": 0.045
        },
        "reference_abundance": {
            "1224": 0.28, "201174": 0.195, "976": 0.155, "1239": 0.12, "200795": 0.105, "29053": 0.045
        },
        "total_reads": 10000,
        "u_c": 0.5,
    }
    response = client.post("/api/v1/forensic/metagenomics/calibrated-lr", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sample_id"] == "QUESTIONED_SOIL_01"
    assert "log10_lr_fused" in data
    assert "enfsi_tier" in data
    assert "prosecutors_fallacy_shield_en" in data
    assert "prosecutors_fallacy_shield_tr" in data


def test_api_feast_source_tracking(client):
    payload = {
        "sink_id": "SHOE_SOIL_SINK",
        "sink_abundance": {"1224": 0.50, "201174": 0.30, "976": 0.20},
        "sources": [
            {"source_id": "CRIME_SCENE", "description": "Scene soil", "relative_abundance": {"1224": 0.55, "201174": 0.28, "976": 0.17}},
            {"source_id": "SUSPECT_GARDEN", "description": "Garden soil", "relative_abundance": {"1224": 0.10, "201174": 0.10, "976": 0.80}},
        ],
        "hp_source_id": "CRIME_SCENE",
    }
    response = client.post("/api/v1/forensic/metagenomics/feast-source-tracking", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sink_id"] == "SHOE_SOIL_SINK"
    assert "source_proportions" in data
    assert data["source_proportions"]["CRIME_SCENE"] > data["source_proportions"]["SUSPECT_GARDEN"]


def test_api_generate_meta_iso_report(client):
    payload = {
        "case_id": "CASE-2026-GEO-001",
        "sample_id": "SOIL-TRACE-42",
        "reference_site_id": "WOODLAND_SCENE",
        "investigator_name": "Dr. Sarah Connor",
        "primary_analyst_id": "ANALYST-01",
        "technical_reviewer_id": "PEER-REVIEWER-02",
        "aitchison_distance": 0.1245,
        "log10_lr_metagenomics": 3.85,
        "log10_lr_fused": 4.12,
        "enfsi_tier": "TIER_4_VERY_STRONG_SUPPORT",
        "enfsi_verbal_en": "The findings provide very strong support for Hp.",
        "enfsi_verbal_tr": "Bulgular, Hp lehine cok guclu destek saglamaktadir.",
        "prosecutors_fallacy_shield_en": "LR evaluates P(E|Hp)/P(E|Hd), not P(Hp|E).",
        "prosecutors_fallacy_shield_tr": "LR olabilirlik oranidir, sucluluk olasiligi degildir.",
        "iso_17025_u_expanded_95pct": 1.0,
        "reference_db": "GTDB_220 / SILVA_138.2",
    }
    response = client.post("/api/v1/forensic/metagenomics/generate-meta-iso-report", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["court_admissibility_certified"] is True
    assert data["case_summary"]["case_id"] == "CASE-2026-GEO-001"
    assert data["empirical_results"]["aitchison_distance"] == 0.1245
    assert data["statistical_interpretation"]["log10_lr_fused"] == 4.12
    assert "certificate_hash" in data["audit_trail_and_cryptography"]
