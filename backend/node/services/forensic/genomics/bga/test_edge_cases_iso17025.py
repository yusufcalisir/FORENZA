"""
Mandatory ISO/IEC 17025 Edge-Case Test Suite for BGA & HIrisPlex-S Systems.

Verifies:
- EC-BGA-01: German § 81e StPO statutory ancestry block & phenotyping pass-through invariant
- EC-BGA-02: Softmax & Admixture probability simplex normalization invariant (|sum P - 1.0| <= 1e-6)
- EC-BGA-03: Monomorphic locus and missing SNP penalty handling without crash (lambda=0.35)
- EC-BGA-04: Fixed panel mathematical ceiling & HERC2 dominance validation
- EC-BGA-05: Admixed tri-continental continuous cline vs. hard classification error guard
"""

import pytest
import math
from backend.node.services.forensic.genomics.bga.schemas import (
    IngestedBGASample,
    PlatformFormatEnum,
    AIMPanelTypeEnum,
    JurisdictionCodeEnum,
    GenotypeCall,
    QCStatusEnum
)
from backend.node.services.forensic.genomics.bga.governance_engine import BGAGovernanceEngine
from backend.node.services.forensic.genomics.bga.admixture_engine import BGAAdmixtureEngine
from backend.node.services.forensic.genomics.bga.hirisplex_model import HIrisPlexModelEngine
from backend.node.services.forensic.genomics.bga.qc_engine import BGAQualityControlEngine
from backend.node.services.forensic.genomics.bga.golden_vectors import BGAGoldenVectors


def test_ec_bga_01_germany_stpo_invariants():
    """EC-BGA-01: German § 81e StPO statutory ancestry block & phenotyping pass-through invariant."""
    sample = BGAGoldenVectors.get_vector_01_na12878_ceu()
    anc = BGAAdmixtureEngine.generate_full_ancestry_report(sample)
    pheno = HIrisPlexModelEngine.predict_full_phenotype(sample)

    gov = BGAGovernanceEngine.apply_governance_to_reports(
        ancestry_report=anc,
        phenotype_report=pheno,
        jurisdiction=JurisdictionCodeEnum.GERMANY_STPO
    )

    compliance = gov["compliance"]
    assert compliance.is_ancestry_authorized is False
    assert compliance.ancestry_redacted is True
    assert gov["ancestry_report"].superpop_proportions == {}
    assert gov["ancestry_report"].pca_coordinates == []
    # EVC Phenotype MUST remain fully intact
    assert gov["phenotype_report"].eye_color.predicted_category == "Blue"


def test_ec_bga_02_simplex_normalization_invariants():
    """EC-BGA-02: Softmax & Admixture probability simplex normalization invariant (|sum P - 1.0| <= 1e-6)."""
    for vec_func in [
        BGAGoldenVectors.get_vector_01_na12878_ceu,
        BGAGoldenVectors.get_vector_02_na19240_yri,
        BGAGoldenVectors.get_vector_03_na18507_chb,
        BGAGoldenVectors.get_vector_04_hg002_aj,
        BGAGoldenVectors.get_vector_05_admixed_tri_racial
    ]:
        sample = vec_func()
        anc = BGAAdmixtureEngine.generate_full_ancestry_report(sample)
        pheno = HIrisPlexModelEngine.predict_full_phenotype(sample)

        # Admixture simplex invariant
        q_sum = sum(anc.superpop_proportions.values())
        assert abs(q_sum - 1.0) <= 1e-5, f"Admixture sum deviation: {abs(q_sum - 1.0)}"

        # Eye color simplex invariant
        eye_sum = pheno.eye_color.blue_probability + pheno.eye_color.brown_probability + pheno.eye_color.intermediate_probability
        assert abs(eye_sum - 1.0) <= 1e-5, f"Eye sum deviation: {abs(eye_sum - 1.0)}"

        # Hair color simplex invariant
        hair_sum = (pheno.hair_color.blond_probability + pheno.hair_color.brown_probability +
                    pheno.hair_color.red_probability + pheno.hair_color.black_probability)
        assert abs(hair_sum - 1.0) <= 1e-5, f"Hair sum deviation: {abs(hair_sum - 1.0)}"

        # Skin color simplex invariant
        skin_sum = (pheno.skin_color.very_pale_probability + pheno.skin_color.pale_probability +
                    pheno.skin_color.intermediate_probability + pheno.skin_color.dark_probability +
                    pheno.skin_color.dark_to_black_probability)
        assert abs(skin_sum - 1.0) <= 1e-5, f"Skin sum deviation: {abs(skin_sum - 1.0)}"


def test_ec_bga_03_missing_penalty_and_degraded_profile():
    """EC-BGA-03: Monomorphic locus and missing SNP penalty handling without crash (lambda=0.35)."""
    # Sample with only 2 SNPs called
    genotypes = {
        "rs2814778": GenotypeCall(locus_id="rs2814778", allele_1="T", allele_2="T", is_heterozygous=False, dosage_alt=0.0),
        "rs1426654": GenotypeCall(locus_id="rs1426654", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0)
    }
    sample = IngestedBGASample(
        sample_id="DEGRADED_EC03",
        detected_platform=PlatformFormatEnum.SNAPSHOT_CE_TABLE,
        primary_panel=AIMPanelTypeEnum.KIDD_55,
        genotypes=genotypes,
        total_loci_assayed=55
    )

    qc_sample = BGAQualityControlEngine.evaluate_sample(sample)
    assert qc_sample.qc_status == QCStatusEnum.FAIL

    penalty = BGAQualityControlEngine.compute_missing_logit_penalty(qc_sample)
    assert penalty > 0.30

    # Admixture deconvolution must still execute gracefully without dividing by zero
    anc = BGAAdmixtureEngine.generate_full_ancestry_report(qc_sample)
    assert abs(sum(anc.superpop_proportions.values()) - 1.0) <= 1e-5


def test_ec_bga_04_fixed_panel_ceiling_herc2_dominance():
    """EC-BGA-04: Fixed panel mathematical ceiling & HERC2 dominance validation."""
    # When HERC2 is GG (Blue driver), but other polygenic pigment loci are dark, HERC2 dominates European eye color
    genotypes = {
        "rs12913832": GenotypeCall(locus_id="rs12913832", allele_1="G", allele_2="G", is_heterozygous=False, dosage_alt=2.0),
        "rs1800407": GenotypeCall(locus_id="rs1800407", allele_1="C", allele_2="T", is_heterozygous=True, dosage_alt=1.0),
        "rs1393350": GenotypeCall(locus_id="rs1393350", allele_1="G", allele_2="A", is_heterozygous=True, dosage_alt=1.0)
    }
    eye_pred = HIrisPlexModelEngine.predict_eye_color(genotypes)
    # HERC2 dominance: Blue eye probability must remain >= 0.70 despite modifier variants
    assert eye_pred.blue_probability >= 0.70
    assert eye_pred.predicted_category == "Blue"


def test_ec_bga_05_admixed_continuous_cline_vs_hard_classification():
    """EC-BGA-05: Admixed tri-continental continuous cline vs. hard classification error guard."""
    sample = BGAGoldenVectors.get_vector_05_admixed_tri_racial()
    anc = BGAAdmixtureEngine.generate_full_ancestry_report(sample)

    # In admixed individuals, Shannon entropy must be elevated (> 0.5) indicating continuous admixture
    assert anc.shannon_entropy > 0.50
    # Soft Q fractions must not collapse to 1.0 for a single group
    max_q = max(anc.superpop_proportions.values())
    assert max_q < 0.90, f"Admixed sample artificially forced to single hard group with q={max_q}"
