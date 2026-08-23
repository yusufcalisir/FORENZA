"""
Unit tests for Levine DNAm PhenoAge Engine (Clinical Gompertz and 513-CpG Models).
"""

import pytest
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    MethylationSample,
    EpigeneticTissueType,
)
from backend.node.services.forensic.epigenetics.clocks.phenoage_engine import (
    PhenoAgeEngine,
)


def test_clinical_phenotypic_age_calculation():
    """Verify 10-biomarker Gompertz model calculations for healthy and elevated risk profiles."""
    # 1. Healthy adult aged 50
    healthy_bio = {
        "Albumin": 4.6,
        "Creatinine": 0.9,
        "Glucose": 90.0,
        "hsCRP": 0.8,
        "Lymphocyte_pct": 32.0,
        "MCV": 88.0,
        "RDW": 12.5,
        "Alkaline_Phosphatase": 65.0,
        "WBC_count": 5.8,
    }
    pheno_healthy, risk_healthy = PhenoAgeEngine.calculate_clinical_phenotypic_age(
        chronological_age=50.0,
        biomarkers=healthy_bio,
    )
    assert 40.0 <= pheno_healthy <= 55.0
    assert 0.0 < risk_healthy < 0.20

    # 2. High metabolic / inflammatory risk individual aged 50
    high_risk_bio = {
        "Albumin": 3.4,         # Low albumin
        "Creatinine": 1.8,      # High creatinine
        "Glucose": 160.0,       # High glucose
        "hsCRP": 8.5,           # High CRP
        "Lymphocyte_pct": 18.0, # Low lymphocytes
        "MCV": 98.0,
        "RDW": 16.2,            # High RDW
        "Alkaline_Phosphatase": 130.0,
        "WBC_count": 11.5,
    }
    pheno_high_risk, risk_high = PhenoAgeEngine.calculate_clinical_phenotypic_age(
        chronological_age=50.0,
        biomarkers=high_risk_bio,
    )
    assert pheno_high_risk > pheno_healthy
    assert risk_high > risk_healthy


def test_dnam_phenoage_prediction():
    """Verify DNAm PhenoAge prediction from CpG beta-values."""
    sample = MethylationSample(
        sample_id="SAMPLE_PHENO_01",
        tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
        beta_values={
            "cg16867657": 0.45,  # ELOVL2
            "cg21572722": 0.40,  # ELOVL2 CpG3
            "cg06639320": 0.35,  # FHL2
            "cg04523812": 0.30,  # TRIM59
            "cg07955995": 0.25,  # KLF14
        },
    )

    res = PhenoAgeEngine.predict_dnam_phenoage(
        sample=sample,
        chronological_age=45.0,
    )

    assert res["clock_id"] == "phenoage"
    assert res["dnam_phenoage"] > 30.0
    assert res["pheno_acceleration"] is not None
    assert res["forensic_admissibility_flag"] is False
    assert "2nd-generation" in res["advisory_note"]
