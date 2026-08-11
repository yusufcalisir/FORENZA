"""
FORENZA Forensic Reports API Router.
Exposes endpoints for generating SWGDAM/ENFSI compliant report certificates
and running ISO/IEC 17025 compliance audits under the /reports prefix.
"""

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.models import STRGenotype, STRProfile
from node.services.forensic.reports.generator import ForensicReportGenerator
from node.services.forensic.reports.compliance import ComplianceAuditor
from .report_schemas import (
    AuditRequest, AuditResponse,
    ReportGenerateRequest, ReportGenerateResponse
)

router = APIRouter(prefix="/forensic/reports", tags=["Forensic Reporting & Compliance"])

_generator = ForensicReportGenerator()
_auditor = ComplianceAuditor()


@router.post(
    "/generate",
    response_model=ReportGenerateResponse,
    summary="Generate SWGDAM Forensic Certificate",
    description="Compiles structured SWGDAM/ENFSI evaluative report with 95% HPD bounds and ENFSI 7-tier verbal scale.",
    status_code=status.HTTP_200_OK,
)
async def generate_report(body: ReportGenerateRequest) -> ReportGenerateResponse:
    try:
        cert = _generator.compile_certificate(
            evidence_id=body.evidence_id,
            suspect_id=body.suspect_id,
            lr_value=body.lr_value,
            log10_lr=body.log10_lr,
            population=body.population,
            phenotype_summary=body.phenotype_summary,
            zkp_verified=body.zkp_verified,
            zkp_tx_hash=body.zkp_tx_hash
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Report generation failed: {str(exc)}"
        )

    return ReportGenerateResponse(**cert.to_dict())


@router.post(
    "/audit",
    response_model=AuditResponse,
    summary="ISO/IEC 17025 Compliance Audit",
    description="Runs automated compliance checklist for CODIS loci completeness, theta application, and ZKP proof.",
    status_code=status.HTTP_200_OK,
)
async def audit_compliance(body: AuditRequest) -> AuditResponse:
    try:
        loci = {}
        for l_in in body.profile.loci:
            lname = l_in.locus.upper()
            loci[lname] = STRGenotype(locus_name=lname, allele1=l_in.allele1, allele2=l_in.allele2)

        profile_domain = STRProfile(
            profile_id=body.profile.profile_id,
            loci=loci,
            population_group=body.profile.population_group
        )

        audit_res = _auditor.audit_profile_compliance(
            profile=profile_domain,
            theta_applied=body.theta_applied,
            has_zkp_proof=body.has_zkp_proof
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Compliance audit failed: {str(exc)}"
        )

    return AuditResponse(**audit_res.to_dict())
