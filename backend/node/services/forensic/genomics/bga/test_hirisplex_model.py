"""
Unit Tests for HIrisPlex-S (41-SNP) Phenotypic Pigmentation Prediction Models.
"""

import pytest
from backend.node.services.forensic.genomics.bga.schemas import (
    IngestedBGASample,
    PlatformFormatEnum,
    AIMPanelTypeEnum,
    GenotypeCall
)
from backend.node.services.forensic.genomics.bga.hirisplex_model import HIrisPlexModelEngine


def test_blue_eye_prediction():
    """Verify HERC2 rs12913832 G/G homozygous yields high Blue eye probability."""
    genotypes = {
        "rs12913832": GenotypeCall(locus_id="rs12913832", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0),
        "rs1800407": GenotypeCall(locus_id="rs1800407", allele_1="C", allele_2="C", is_heterozygous=False, dosage_alt=0.0),
        "rs16891982": GenotypeCall(locus_id="rs16891982", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0)
    }
    pred = HIrisPlexModelEngine.predict_eye_color(genotypes)
    assert pred.predicted_category == "Blue"
    assert pred.blue_probability > 0.85
    assert abs((pred.blue_probability + pred.brown_probability + pred.intermediate_probability) - 1.0) < 1e-5


def test_brown_eye_prediction():
    """Verify HERC2 rs12913832 A/A homozygous yields high Brown eye probability."""
    genotypes = {
        "rs12913832": GenotypeCall(locus_id="rs12913832", allele_1="A", allele_2="A", is_heterozygous=False, dosage_alt=0.0),
        "rs1800407": GenotypeCall(locus_id="rs1800407", allele_1="C", allele_2="C", is_heterozygous=False, dosage_alt=0.0)
    }
    pred = HIrisPlexModelEngine.predict_eye_color(genotypes)
    assert pred.predicted_category == "Brown"
    assert pred.brown_probability > 0.80


def test_missing_herc2_gate():
    """Verify missing HERC2 rs12913832 halts deterministic eye call."""
    genotypes = {
        "rs1800407": GenotypeCall(locus_id="rs1800407", allele_1="C", allele_2="C", is_heterozygous=False, dosage_alt=0.0)
    }
    pred = HIrisPlexModelEngine.predict_eye_color(genotypes)
    assert pred.herc2_gate_status == "MISSING_CRITICAL_LOCUS"
    assert pred.predicted_category == "INDETERMINATE"


def test_red_hair_mc1r_epistasis():
    """Verify homozygous MC1R mutations yield high Red hair probability."""
    genotypes = {
        "rs1805007": GenotypeCall(locus_id="rs1805007", allele_1="T", allele_2="T", is_heterozygous=False, dosage_alt=2.0),
        "rs1805008": GenotypeCall(locus_id="rs1805008", allele_1="T", allele_2="T", is_heterozygous=False, dosage_alt=2.0),
        "rs12913832": GenotypeCall(locus_id="rs12913832", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0)
    }
    hair_pred = HIrisPlexModelEngine.predict_hair_color(genotypes)
    assert hair_pred.predicted_color == "Red"
    assert hair_pred.red_probability > 0.80
    assert hair_pred.mc1r_loss_of_function_count >= 2


def test_skin_pigmentation_polar_classes():
    """Verify Pale vs Dark-to-Black skin predictions driven by SLC24A5 and SLC45A2."""
    # Pale / Very Pale profile
    pale_genotypes = {
        "rs1426654": GenotypeCall(locus_id="rs1426654", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0),
        "rs16891982": GenotypeCall(locus_id="rs16891982", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0),
        "rs12913832": GenotypeCall(locus_id="rs12913832", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0)
    }
    skin_pale = HIrisPlexModelEngine.predict_skin_color(pale_genotypes)
    assert skin_pale.predicted_category in ("Pale", "Very Pale")
    assert (skin_pale.pale_probability + skin_pale.very_pale_probability) > 0.75

    # Dark / Dark-to-Black profile
    dark_genotypes = {
        "rs1426654": GenotypeCall(locus_id="rs1426654", allele_1="A", allele_2="A", is_heterozygous=False, dosage_alt=0.0),
        "rs16891982": GenotypeCall(locus_id="rs16891982", allele_1="C", allele_2="C", is_heterozygous=False, dosage_alt=0.0),
        "rs12913832": GenotypeCall(locus_id="rs12913832", allele_1="A", allele_2="A", is_heterozygous=False, dosage_alt=0.0)
    }
    skin_dark = HIrisPlexModelEngine.predict_skin_color(dark_genotypes)
    assert skin_dark.predicted_category in ("Dark", "Dark-to-Black")
    assert (skin_dark.dark_probability + skin_dark.dark_to_black_probability) > 0.85


def test_full_phenotype_assessment_synthesis():
    """Verify unified PhenotypePredictionResult synthesis."""
    genotypes = {
        "rs12913832": GenotypeCall(locus_id="rs12913832", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0),
        "rs1426654": GenotypeCall(locus_id="rs1426654", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0),
        "rs16891982": GenotypeCall(locus_id="rs16891982", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0)
    }
    sample = IngestedBGASample(
        sample_id="PHENOTYPE_TEST",
        detected_platform=PlatformFormatEnum.AMPLISEQ_TSV,
        primary_panel=AIMPanelTypeEnum.VISAGE_BASIC_153,
        genotypes=genotypes
    )
    result = HIrisPlexModelEngine.predict_full_phenotype(sample)
    assert "Blue Eyes" in result.phenotype_summary
    assert result.eye_color.predicted_category == "Blue"
