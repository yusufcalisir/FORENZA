"""
Unit Tests for Statutory Legal Governance and German § 81e StPO Masking Gate.
"""

import pytest
from backend.node.services.forensic.genomics.bga.schemas import (
    JurisdictionCodeEnum,
    ContinentalSuperPopEnum
)
from backend.node.services.forensic.genomics.bga.governance_engine import BGAGovernanceEngine
from backend.node.services.forensic.genomics.bga.admixture_engine import BGAAdmixtureEngine
from backend.node.services.forensic.genomics.bga.hirisplex_model import HIrisPlexModelEngine
from backend.node.services.forensic.genomics.bga.golden_vectors import BGAGoldenVectors


def test_germany_stpo_statutory_ancestry_redaction():
    """Verify German § 81e (2) StPO automatically redacts BGA while preserving EVC phenotyping."""
    sample = BGAGoldenVectors.get_vector_01_na12878_ceu()
    ancestry_rep = BGAAdmixtureEngine.generate_full_ancestry_report(sample)
    phenotype_rep = HIrisPlexModelEngine.predict_full_phenotype(sample)

    gov_res = BGAGovernanceEngine.apply_governance_to_reports(
        ancestry_report=ancestry_rep,
        phenotype_report=phenotype_rep,
        jurisdiction=JurisdictionCodeEnum.GERMANY_STPO
    )

    compliance = gov_res["compliance"]
    assert compliance.is_ancestry_authorized is False
    assert compliance.ancestry_redacted is True
    assert "§ 81e (2) StPO" in compliance.redaction_statutory_notice

    # Redacted ancestry report
    redacted_anc = gov_res["ancestry_report"]
    assert redacted_anc.superpop_proportions == {}
    assert redacted_anc.pca_coordinates == []
    assert "[REDACTED - § 81e (2) StPO]" in redacted_anc.enfsi_verbal_statement

    # Phenotyping must NOT be redacted
    final_pheno = gov_res["phenotype_report"]
    assert final_pheno is not None
    assert final_pheno.eye_color.predicted_category == "Blue"


def test_netherlands_magistrate_authorization():
    """Verify Dutch Art. 151a Sv flags pending authorization when magistrate flag is False."""
    comp_unauth = BGAGovernanceEngine.evaluate_compliance(JurisdictionCodeEnum.NETHERLANDS_SV, magistrate_authorized=False)
    assert "WARNING" in comp_unauth.magistrate_authorization_status

    comp_auth = BGAGovernanceEngine.evaluate_compliance(JurisdictionCodeEnum.NETHERLANDS_SV, magistrate_authorized=True)
    assert comp_auth.magistrate_authorization_status == "AUTHORIZED"


def test_prosecutors_fallacy_shield_present():
    """Verify Prosecutor's Fallacy Shield is always attached to compliance certificates."""
    comp = BGAGovernanceEngine.evaluate_compliance(JurisdictionCodeEnum.ISFG_INTERNATIONAL)
    assert "PROSECUTOR'S FALLACY SHIELD" in comp.prosecutors_fallacy_shield
    assert "never be conflated with sociological concepts of race" in comp.prosecutors_fallacy_shield
