"""
Unit Tests for FGG Legal Compliance, Statutory Guardrails, and Sample Destruction.
"""

import pytest
from backend.node.services.forensic.genomics.fgg.schemas import (
    LegalComplianceCase,
    QualifyingOffenseEnum,
    JurisdictionStatuteEnum
)
from backend.node.services.forensic.genomics.fgg.legal_compliance import FGGLegalComplianceEngine
from backend.node.services.forensic.genomics.fgg.sample_destruction_manager import FGGSampleDestructionManager


class TestFGGLegalCompliance:
    """Tests statutory compliance under US DOJ (2019), Maryland Title 17, and Montana MCA."""

    def test_codis_exhaustion_mandatory_ec_fgg_02(self):
        # CODIS search NOT exhausted -> Must be rejected with critical violation
        case = LegalComplianceCase(
            case_id="CASE_2026_01",
            jurisdiction=JurisdictionStatuteEnum.US_DOJ_INTERIM_2019,
            offense_type=QualifyingOffenseEnum.HOMICIDE,
            is_codis_exhausted=False,  # Violation!
            prosecutor_authorization_id="AUTH_DA_991",
            opt_in_matches_only_enforced=True
        )
        val = FGGLegalComplianceEngine.validate_case(case)
        assert val.is_compliant is False
        assert any("EC-FGG-02" in v for v in val.violations)

    def test_non_qualifying_crime_rejection(self):
        # Property crime -> Ineligible
        case = LegalComplianceCase(
            case_id="CASE_2026_02",
            jurisdiction=JurisdictionStatuteEnum.US_DOJ_INTERIM_2019,
            offense_type=QualifyingOffenseEnum.NON_QUALIFYING_PROPERTY_CRIME,
            is_codis_exhausted=True,
            prosecutor_authorization_id="AUTH_DA_992",
            opt_in_matches_only_enforced=True
        )
        val = FGGLegalComplianceEngine.validate_case(case)
        assert val.is_compliant is False
        assert any("OFFENSE INELIGIBLE" in v for v in val.violations)

    def test_us_doj_valid_case(self):
        # Valid Homicide case under US DOJ 2019
        case = LegalComplianceCase(
            case_id="CASE_2026_03",
            jurisdiction=JurisdictionStatuteEnum.US_DOJ_INTERIM_2019,
            offense_type=QualifyingOffenseEnum.HOMICIDE,
            is_codis_exhausted=True,
            prosecutor_authorization_id="AUTH_DOJ_12345",
            opt_in_matches_only_enforced=True
        )
        val = FGGLegalComplianceEngine.validate_case(case)
        assert val.is_compliant is True
        assert len(val.violations) == 0
        assert "INVESTIGATIVE LEADS ONLY" in val.lead_disclaimer_notice
        assert len(val.audit_record_hash) == 64

    def test_maryland_title_17_destruction_plan_mandate(self):
        # Maryland requires both court warrant and destruction plan
        case_md_invalid = LegalComplianceCase(
            case_id="CASE_MD_01",
            jurisdiction=JurisdictionStatuteEnum.US_MARYLAND_TITLE_17,
            offense_type=QualifyingOffenseEnum.SEXUAL_ASSAULT,
            is_codis_exhausted=True,
            judicial_warrant_ref=None, # Missing warrant!
            destruction_plan_mandated=False # Missing destruction plan!
        )
        val_inv = FGGLegalComplianceEngine.validate_case(case_md_invalid)
        assert val_inv.is_compliant is False
        assert len(val_inv.violations) == 2

        case_md_valid = LegalComplianceCase(
            case_id="CASE_MD_02",
            jurisdiction=JurisdictionStatuteEnum.US_MARYLAND_TITLE_17,
            offense_type=QualifyingOffenseEnum.SEXUAL_ASSAULT,
            is_codis_exhausted=True,
            judicial_warrant_ref="MD_COURT_ORD_2026_88",
            destruction_plan_mandated=True
        )
        val_v = FGGLegalComplianceEngine.validate_case(case_md_valid)
        assert val_v.is_compliant is True

    def test_sample_destruction_manager_certificate(self):
        order = FGGSampleDestructionManager.generate_destruction_order(
            case_id="CASE_MD_02",
            statutory_basis="Maryland Title 17 Criminal Procedure Section 17-104",
            reference_sample_ids=["REF_COUSIN_01", "REF_COUSIN_02"],
            certifying_officer="Commander Jane Doe"
        )
        assert order.is_destruction_verified is True
        assert len(order.reference_sample_ids) == 2
        assert len(order.certificate_hash) == 64
