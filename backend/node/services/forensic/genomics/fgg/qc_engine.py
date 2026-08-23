"""
Quality Control (QC) & Sample Degradation Evaluation Engine.

Evaluates sample call rates (>= 95.0% threshold), heterozygosity fractions,
and flags degraded/compromised forensic evidence.
"""

from typing import List, Dict
from .schemas import ProfileQCReport, GenotypeStateEnum, PlatformFormatEnum


class FGGQCEngine:
    """Evaluates sample-wide quality metrics for FGG profiles."""

    CALL_RATE_VALID_THRESHOLD: float = 95.00       # ISO/IEC 17025 Standard
    DEGRADATION_WARNING_THRESHOLD: float = 90.00   # Severe touch/aDNA degradation
    CONTAMINATION_MAX_HET: float = 35.00          # Excess heterozygosity indicating mixture
    INBREEDING_MIN_HET: float = 10.00             # Low heterozygosity indicating severe endogamy/ROH

    @classmethod
    def evaluate_profile_qc(
        cls,
        all_states: List[GenotypeStateEnum],
        detected_platform: PlatformFormatEnum,
        assembly_version: str = "GRCh38"
    ) -> ProfileQCReport:
        """Computes comprehensive sample-wide QC metrics."""
        total = len(all_states)
        if total == 0:
            return ProfileQCReport(
                total_snps_evaluated=0,
                called_snps=0,
                missing_snps=0,
                call_rate_percentage=0.0,
                heterozygosity_rate_percentage=0.0,
                is_call_rate_valid=False,
                degradation_warning=True,
                contamination_warning=False,
                detected_platform=detected_platform,
                assembly_version=assembly_version
            )

        called = 0
        missing = 0
        het = 0

        for s in all_states:
            if s == GenotypeStateEnum.NO_CALL:
                missing += 1
            else:
                called += 1
                if s == GenotypeStateEnum.HET:
                    het += 1

        call_rate = (called / total) * 100.0
        het_rate = (het / called * 100.0) if called > 0 else 0.0

        is_valid = call_rate >= cls.CALL_RATE_VALID_THRESHOLD
        deg_warn = call_rate < cls.DEGRADATION_WARNING_THRESHOLD
        contam_warn = het_rate > cls.CONTAMINATION_MAX_HET

        return ProfileQCReport(
            total_snps_evaluated=total,
            called_snps=called,
            missing_snps=missing,
            call_rate_percentage=round(call_rate, 4),
            heterozygosity_rate_percentage=round(het_rate, 4),
            is_call_rate_valid=is_valid,
            degradation_warning=deg_warn,
            contamination_warning=contam_warn,
            detected_platform=detected_platform,
            assembly_version=assembly_version
        )
