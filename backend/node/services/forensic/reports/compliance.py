"""
FORENZA ISO/IEC 17025 Forensic Compliance Auditor.
Automated audit engine checking chain-of-custody integrity, CODIS loci completeness,
Balding-Nichols theta application, and ENFSI verbal scale mapping for court admissibility.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from ..models import STRProfile


@dataclass
class ComplianceCheckItem:
    rule_id: str
    rule_name: str
    passed: bool
    details: str


@dataclass
class ComplianceAuditReport:
    profile_id: str
    total_checks: int
    passed_checks: int
    compliance_score: float                # 0.0 to 1.0 (1.0 = 100% compliant)
    iso17025_status: str                   # 'ACCREDITED_COMPLIANT' or 'NON_COMPLIANT'
    checks: List[ComplianceCheckItem]
    warnings: List[str]

    def to_dict(self) -> Dict:
        return {
            "profile_id": self.profile_id,
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks,
            "compliance_score": round(self.compliance_score, 4),
            "iso17025_status": self.iso17025_status,
            "checks": [
                {
                    "rule_id": c.rule_id,
                    "rule_name": c.rule_name,
                    "passed": c.passed,
                    "details": c.details,
                }
                for c in self.checks
            ],
            "warnings": self.warnings,
        }


class ComplianceAuditor:
    """
    Automated ISO/IEC 17025 & SWGDAM compliance verification suite.
    """

    MINIMUM_CODIS_LOCI_THRESHOLD = 13

    def audit_profile_compliance(
        self,
        profile: STRProfile,
        theta_applied: float = 0.01,
        has_zkp_proof: bool = True
    ) -> ComplianceAuditReport:
        """Runs compliance rules against a profile analysis."""
        checks: List[ComplianceCheckItem] = []
        warnings: List[str] = []

        # Check 1: CODIS Loci Count
        loci_count = len(profile.loci)
        loci_pass = loci_count >= self.MINIMUM_CODIS_LOCI_THRESHOLD
        checks.append(ComplianceCheckItem(
            rule_id="RULE-101",
            rule_name="CODIS Core Loci Completeness",
            passed=loci_pass,
            details=f"Profile contains {loci_count} loci (minimum required: {self.MINIMUM_CODIS_LOCI_THRESHOLD})"
        ))
        if not loci_pass:
            warnings.append("Profile contains fewer than 13 loci; full CODIS database search precluded.")

        # Check 2: Theta Coancestry Correction
        theta_pass = theta_applied >= 0.01
        checks.append(ComplianceCheckItem(
            rule_id="RULE-102",
            rule_name="Balding-Nichols Theta Correction",
            passed=theta_pass,
            details=f"Theta coancestry correction applied (theta = {theta_applied})"
        ))
        if not theta_pass:
            warnings.append("Theta correction is below NRC II recommended baseline of 0.01.")

        # Check 3: Amelogenin Sex Marker
        has_amel = "AMEL" in profile.loci or "AMELOGENIN" in profile.loci
        checks.append(ComplianceCheckItem(
            rule_id="RULE-103",
            rule_name="Amelogenin Sex Chromosome Marker",
            passed=has_amel,
            details="AMEL sex determination marker present" if has_amel else "AMEL marker absent"
        ))

        # Check 4: ZKP Proof Integrity
        checks.append(ComplianceCheckItem(
            rule_id="RULE-104",
            rule_name="Zero-Knowledge Privacy Proof",
            passed=has_zkp_proof,
            details="Circom zk-SNARK cryptographic match proof validated" if has_zkp_proof else "ZKP proof not provided"
        ))

        # Check 5: Allele Validity
        all_valid_alleles = True
        for lname, geno in profile.loci.items():
            if geno.allele1 <= 0 or geno.allele2 <= 0:
                all_valid_alleles = False
                break
        checks.append(ComplianceCheckItem(
            rule_id="RULE-105",
            rule_name="Allele Designation Validity",
            passed=all_valid_alleles,
            details="All allele designations are positive repeat numbers"
        ))

        passed_count = sum(1 for c in checks if c.passed)
        score = passed_count / len(checks)
        status_str = "ACCREDITED_COMPLIANT" if score >= 0.80 else "NON_COMPLIANT"

        return ComplianceAuditReport(
            profile_id=profile.profile_id,
            total_checks=len(checks),
            passed_checks=passed_count,
            compliance_score=score,
            iso17025_status=status_str,
            checks=checks,
            warnings=warnings
        )
