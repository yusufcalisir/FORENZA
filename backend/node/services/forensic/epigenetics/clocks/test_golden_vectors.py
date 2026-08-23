"""
Unit tests executing golden benchmark test vectors and cross-tool validation.
"""

import pytest
from backend.node.services.forensic.epigenetics.clocks.golden_vectors import (
    GOLDEN_VECTORS_CATALOG,
    VECTOR_NIST_2391D_A,
    VECTOR_NA12878_CEU,
    VECTOR_NA19240_YRI,
    VECTOR_HG002_AJ,
    VECTOR_SMOKER_MORBID,
)
from backend.node.services.forensic.epigenetics.clocks.horvath_engine import (
    HorvathEpigeneticEngine,
)
from backend.node.services.forensic.epigenetics.clocks.visage_multiplex_engine import (
    VISAGEMultiplexEngine,
)
from backend.node.services.forensic.epigenetics.clocks.grimage_engine import (
    GrimAgeEngine,
)


def test_nist_srm_2391d_comp_a_golden_vector():
    """Verify NIST SRM 2391d Component A (32.5y true chronological age)."""
    vec = VECTOR_NIST_2391D_A

    # 1. Horvath 2013 prediction
    res_horvath = HorvathEpigeneticEngine.predict_age(
        sample=vec.sample,
        clock_id="horvath_2013",
        chronological_age=vec.true_chronological_age,
    )
    assert vec.expected_horvath_range[0] <= res_horvath.predicted_age <= vec.expected_horvath_range[1]
    assert abs(res_horvath.predicted_age - vec.true_chronological_age) <= 3.8

    # 2. VISAGE Enhanced MPS prediction
    res_visage = VISAGEMultiplexEngine.predict_visage_enhanced(
        sample=vec.sample,
        chronological_age=vec.true_chronological_age,
    )
    assert vec.expected_visage_range[0] <= res_visage.predicted_age <= vec.expected_visage_range[1]


def test_na12878_ceu_golden_vector():
    """Verify NA12878 / HG001 CEU reference individual (45.0y true age)."""
    vec = VECTOR_NA12878_CEU

    res_horvath = HorvathEpigeneticEngine.predict_age(
        sample=vec.sample,
        clock_id="horvath_2013",
        chronological_age=vec.true_chronological_age,
    )
    assert vec.expected_horvath_range[0] <= res_horvath.predicted_age <= vec.expected_horvath_range[1]

    res_visage = VISAGEMultiplexEngine.predict_visage_enhanced(
        sample=vec.sample,
        chronological_age=vec.true_chronological_age,
    )
    assert vec.expected_visage_range[0] <= res_visage.predicted_age <= vec.expected_visage_range[1]


def test_na19240_yri_african_golden_vector():
    """Verify NA19240 African reference individual (28.0y true age)."""
    vec = VECTOR_NA19240_YRI

    res_horvath = HorvathEpigeneticEngine.predict_age(
        sample=vec.sample,
        clock_id="horvath_2013",
        chronological_age=vec.true_chronological_age,
    )
    assert vec.expected_horvath_range[0] <= res_horvath.predicted_age <= vec.expected_horvath_range[1]


def test_hg002_aj_boundary_pivot_vector():
    """Verify HG002 Ashkenazi Jewish individual at the pediatric/adult 20.0y boundary (19.5y true age)."""
    vec = VECTOR_HG002_AJ

    res_horvath = HorvathEpigeneticEngine.predict_age(
        sample=vec.sample,
        clock_id="horvath_2013",
        chronological_age=vec.true_chronological_age,
    )
    assert vec.expected_horvath_range[0] <= res_horvath.predicted_age <= vec.expected_horvath_range[1]


def test_smoker_morbid_divergence_vector():
    """Verify chronic smoker (52.0y): Chronological clocks accurate, GrimAge significantly accelerated."""
    vec = VECTOR_SMOKER_MORBID

    # 1. Horvath remains concordant with chronological age (~52)
    res_horvath = HorvathEpigeneticEngine.predict_age(
        sample=vec.sample,
        clock_id="horvath_2013",
        chronological_age=vec.true_chronological_age,
    )
    assert vec.expected_horvath_range[0] <= res_horvath.predicted_age <= vec.expected_horvath_range[1]

    # 2. GrimAge reveals massive smoking-induced age acceleration (> +6 years)
    res_grim = GrimAgeEngine.predict_grimage(
        sample=vec.sample,
        chronological_age=vec.true_chronological_age,
        smoking_pack_years=vec.smoking_pack_years,
        biological_sex=vec.biological_sex,
    )
    assert res_grim["grimage_acceleration"] >= 6.0
    assert res_grim["surrogate_biomarkers"]["DNAm_PACKYRS"] > 25.0
    assert res_grim["mortality_hazard_ratio"] > 1.50
