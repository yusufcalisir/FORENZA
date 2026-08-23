"""
Unit Tests for Certified Golden Standard Reference Vectors (VECTOR_BGA_01 to 05).
"""

import pytest
from backend.node.services.forensic.genomics.bga.schemas import ContinentalSuperPopEnum
from backend.node.services.forensic.genomics.bga.golden_vectors import BGAGoldenVectors
from backend.node.services.forensic.genomics.bga.admixture_engine import BGAAdmixtureEngine
from backend.node.services.forensic.genomics.bga.hirisplex_model import HIrisPlexModelEngine


def test_vector_01_na12878_ceu():
    """Verify NA12878 CEU European Reference Vector."""
    vec = BGAGoldenVectors.get_vector_01_na12878_ceu()
    anc = BGAAdmixtureEngine.generate_full_ancestry_report(vec)
    pheno = HIrisPlexModelEngine.predict_full_phenotype(vec)

    assert anc.top_assigned_population == ContinentalSuperPopEnum.EUR
    assert pheno.eye_color.predicted_category == "Blue"
    assert pheno.skin_color.predicted_category in ("Pale", "Very Pale")


def test_vector_02_na19240_yri():
    """Verify NA19240 YRI African Reference Vector."""
    vec = BGAGoldenVectors.get_vector_02_na19240_yri()
    anc = BGAAdmixtureEngine.generate_full_ancestry_report(vec)
    pheno = HIrisPlexModelEngine.predict_full_phenotype(vec)

    assert anc.top_assigned_population == ContinentalSuperPopEnum.AFR
    assert pheno.eye_color.predicted_category == "Brown"
    assert pheno.skin_color.predicted_category in ("Dark", "Dark-to-Black")


def test_vector_03_na18507_chb():
    """Verify NA18507 CHB East Asian Reference Vector."""
    vec = BGAGoldenVectors.get_vector_03_na18507_chb()
    anc = BGAAdmixtureEngine.generate_full_ancestry_report(vec)
    pheno = HIrisPlexModelEngine.predict_full_phenotype(vec)

    assert anc.top_assigned_population == ContinentalSuperPopEnum.EAS
    assert pheno.eye_color.predicted_category == "Brown"


def test_vector_04_hg002_aj():
    """Verify HG002 Ashkenazi Jewish Reference Vector."""
    vec = BGAGoldenVectors.get_vector_04_hg002_aj()
    anc = BGAAdmixtureEngine.generate_full_ancestry_report(vec)
    assert anc.top_assigned_population in (ContinentalSuperPopEnum.EUR, ContinentalSuperPopEnum.MID)


def test_vector_05_admixed_tri_racial():
    """Verify Tri-Racial Admixed Reference Vector exhibits multi-continental admixture."""
    vec = BGAGoldenVectors.get_vector_05_admixed_tri_racial()
    anc = BGAAdmixtureEngine.generate_full_ancestry_report(vec)
    assert anc.shannon_entropy > 0.50
    assert anc.simpson_diversity > 0.30
