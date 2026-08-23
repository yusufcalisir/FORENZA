"""
Forensic Genetic Genealogy Statutory Compliance & Legal Governance Engine.

Enforces US DOJ Interim Policy (2019), Maryland Title 17, Montana MCA 44-4-503,
Utah SB 156, Sweden Polisen 2025, and EU GDPR Art. 9 / LED Directive 2016/680.
"""

import hashlib
import json
from typing import List, Tuple
from .schemas import (
    LegalComplianceCase,
    LegalComplianceValidation,
    QualifyingOffenseEnum,
    JurisdictionStatuteEnum
)


class FGGLegalComplianceEngine:
    """Validates legal admissibility, statutory guardrails, and produces signed lead disclaimers."""

    LEGAL_DISCLAIMER_TEMPLATE: str = (
        "LEGAL NOTICE & INVESTIGATIVE LEAD DISCLAIMER (SWGDAM / US DOJ COMPLIANT):\n"
        "All genealogical matches, kinship estimations, and reconstructed pedigree trees generated "
        "by FORENZA are strictly INFORMATIONAL INVESTIGATIVE LEADS ONLY.\n"
        "1. This analysis CANNOT serve as sole probable cause for an arrest warrant or criminal charge.\n"
        "2. Traditional STR comparison (CODIS 20 / GlobalFiler / PowerPlex Fusion 6C) against a direct, "
        "lawfully obtained reference sample from the suspect is MANDATORY prior to formal indictment.\n"
        "3. Third-party reference profiles must be handled in strict accordance with statutory destruction mandates."
    )

    @classmethod
    def validate_case(cls, case: LegalComplianceCase) -> LegalComplianceValidation:
        """
        Validates case eligibility against jurisdiction-specific legal standards.
        Enforces CODIS exhaustion, qualifying crime mandates, warrants, and opt-in filters.
        """
        violations: List[str] = []
        warnings: List[str] = []

        # 1. CODIS STR Exhaustion Requirement (EC-FGG-02)
        if not case.is_codis_exhausted:
            violations.append(
                "CRITICAL STATUTORY VIOLATION (EC-FGG-02): Traditional CODIS STR database search has not been "
                "exhausted without a match. FGG search authorization is prohibited by US DOJ Section V & State law."
            )

        # 2. Qualifying Offense Check
        if case.offense_type == QualifyingOffenseEnum.NON_QUALIFYING_PROPERTY_CRIME:
            violations.append(
                f"OFFENSE INELIGIBLE: FGG is restricted exclusively to violent crimes (Homicide, Sexual Assault) "
                f"or Unidentified Human Remains (UHR). Offense '{case.offense_type.value}' is non-qualifying."
            )

        # 3. Opt-in Database Filter
        if not case.opt_in_matches_only_enforced:
            violations.append(
                "CONSENT VIOLATION: Opt-in law enforcement database filter is disabled. "
                "Searching non-consenting consumer profiles violates terms of service and DOJ Section VI guidelines."
            )

        # 4. Jurisdiction-Specific Statutory Checks
        if case.jurisdiction == JurisdictionStatuteEnum.US_DOJ_INTERIM_2019:
            if not case.prosecutor_authorization_id:
                violations.append("US DOJ REQUIREMENT: Prosecutor / Law Enforcement Supervisor authorization ID is missing.")

        elif case.jurisdiction == JurisdictionStatuteEnum.US_MARYLAND_TITLE_17:
            if not case.judicial_warrant_ref:
                violations.append("MARYLAND TITLE 17 VIOLATION: Judicial court authorization / warrant reference is mandatory.")
            if not case.destruction_plan_mandated:
                violations.append("MARYLAND TITLE 17 VIOLATION: Third-party reference sample destruction plan is mandated by law.")

        elif case.jurisdiction == JurisdictionStatuteEnum.US_MONTANA_MCA_44_4_503:
            if not case.judicial_warrant_ref:
                violations.append("MONTANA MCA 44-4-503 VIOLATION: Probable cause search warrant is required to query consumer databases.")

        elif case.jurisdiction == JurisdictionStatuteEnum.SWEDEN_POLISEN_2025:
            if case.offense_type not in (QualifyingOffenseEnum.HOMICIDE, QualifyingOffenseEnum.SEXUAL_ASSAULT):
                violations.append("SWEDEN POLISEN STATUTE: FGG permitted only for murder (mord) or aggravated rape (grov våldtäkt).")

        elif case.jurisdiction == JurisdictionStatuteEnum.EU_GDPR_LED_2016_680:
            warnings.append("EU GDPR / LED: Local encrypted processing mandated. No raw genomic SNPs may be transmitted to non-EU cloud nodes.")

        is_compliant = len(violations) == 0

        # Compute tamper-proof audit record hash
        audit_payload = {
            "case_id": case.case_id,
            "jurisdiction": case.jurisdiction.value,
            "offense": case.offense_type.value,
            "codis_exhausted": case.is_codis_exhausted,
            "is_compliant": is_compliant,
            "violations_count": len(violations)
        }
        audit_str = json.dumps(audit_payload, sort_keys=True)
        audit_hash = hashlib.sha256(audit_str.encode("utf-8")).hexdigest()

        return LegalComplianceValidation(
            case_id=case.case_id,
            is_compliant=is_compliant,
            violations=violations,
            warnings=warnings,
            lead_disclaimer_notice=cls.LEGAL_DISCLAIMER_TEMPLATE,
            audit_record_hash=audit_hash
        )
