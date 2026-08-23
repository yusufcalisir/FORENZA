"""
Forensic Statutory Governance & Admissibility Compliance Engine.

Enforces:
- German Code of Criminal Procedure (§ 81e StPO) ancestry redaction gate
- Dutch Code of Criminal Procedure (Art. 151a Sv) examining magistrate authorization check
- ISFG / ENFSI (2017) Evaluative Intelligence Reporting & Prosecutor's Fallacy Shield
"""

from typing import Optional, Dict, Any
from backend.node.services.forensic.genomics.bga.schemas import (
    JurisdictionCodeEnum,
    GovernanceComplianceResult,
    AdmixtureProportionResult,
    PhenotypePredictionResult,
    ContinentalSuperPopEnum
)


class BGAGovernanceEngine:
    """Automates statutory legal governance and ethical shields for FDP and BGA reporting."""

    PROSECUTORS_FALLACY_SHIELD_TEXT = (
        "PROSECUTOR'S FALLACY SHIELD: The calculated likelihood ratios and posterior probabilities "
        "quantify the likelihood of the multi-locus genotypic evidence under competing ancestral "
        "and phenotypic hypotheses, NOT the posterior probability of guilt or individual identity. "
        "Biogeographical ancestry reflects continuous evolutionary genomic variation and must never "
        "be conflated with sociological concepts of race or demographic profiling."
    )

    @classmethod
    def evaluate_compliance(
        cls,
        jurisdiction: JurisdictionCodeEnum = JurisdictionCodeEnum.ISFG_INTERNATIONAL,
        magistrate_authorized: bool = True
    ) -> GovernanceComplianceResult:
        """
        Evaluates legal admissibility and statutory restrictions for the active jurisdiction.
        """
        is_phenotyping_auth = True
        is_ancestry_auth = True
        ancestry_redacted = False
        notice = None
        mag_status = "AUTHORIZED" if magistrate_authorized else "UNAUTHORIZED_PENDING"

        if jurisdiction == JurisdictionCodeEnum.GERMANY_STPO:
            # German § 81e (2) StPO: Phenotyping allowed; Ancestry STRICTLY PROHIBITED
            is_ancestry_auth = False
            ancestry_redacted = True
            notice = (
                "§ 81e (2) StPO STATUTORY COMPLIANCE GATE: Biogeographical Ancestry (BGA) inference "
                "is strictly prohibited and redacted under German criminal procedure law (Strafprozessordnung). "
                "Externally Visible Characteristics (Eye/Hair/Skin Pigmentation) and Epigenetic Age remain authorized."
            )
        elif jurisdiction == JurisdictionCodeEnum.NETHERLANDS_SV:
            if not magistrate_authorized:
                mag_status = "WARNING: Examining magistrate (rechter-commissaris) authorization is pending under Art. 151a Sv."
        elif jurisdiction == JurisdictionCodeEnum.UK_PACE:
            notice = "UK PACE (1984) / BFEG GUIDANCE: Profile output is classified strictly as investigative intelligence."

        return GovernanceComplianceResult(
            jurisdiction=jurisdiction,
            is_phenotyping_authorized=is_phenotyping_auth,
            is_ancestry_authorized=is_ancestry_auth,
            ancestry_redacted=ancestry_redacted,
            redaction_statutory_notice=notice,
            magistrate_authorization_status=mag_status,
            prosecutors_fallacy_shield=cls.PROSECUTORS_FALLACY_SHIELD_TEXT,
            reporting_classification="INVESTIGATIVE_LEAD_ONLY"
        )

    @classmethod
    def apply_governance_to_reports(
        cls,
        ancestry_report: Optional[AdmixtureProportionResult],
        phenotype_report: Optional[PhenotypePredictionResult],
        jurisdiction: JurisdictionCodeEnum = JurisdictionCodeEnum.ISFG_INTERNATIONAL,
        magistrate_authorized: bool = True
    ) -> Dict[str, Any]:
        """
        Applies jurisdiction filtering and statutory redactions to BGA and FDP reports.
        """
        compliance = cls.evaluate_compliance(jurisdiction, magistrate_authorized)

        final_ancestry = ancestry_report
        final_phenotype = phenotype_report

        if compliance.ancestry_redacted and final_ancestry:
            # Redact ancestry coordinates and verbal statement per German § 81e StPO
            final_ancestry = AdmixtureProportionResult(
                sample_id=ancestry_report.sample_id,
                panel_type=ancestry_report.panel_type,
                superpop_proportions={},
                top_assigned_population=ContinentalSuperPopEnum.OTH,
                bayes_factor_vs_second=0.0,
                shannon_entropy=0.0,
                simpson_diversity=0.0,
                pca_coordinates=[],
                wgs84_centroid_lat=0.0,
                wgs84_centroid_lng=0.0,
                spatial_covariance_semi_major_km=0.0,
                spatial_covariance_semi_minor_km=0.0,
                spatial_ellipse_tilt_deg=0.0,
                enfsi_verbal_statement=(
                    "[REDACTED - § 81e (2) StPO] Biogeographical ancestry inference is prohibited "
                    "under German criminal procedure law."
                )
            )

        return {
            "compliance": compliance,
            "ancestry_report": final_ancestry,
            "phenotype_report": final_phenotype
        }
