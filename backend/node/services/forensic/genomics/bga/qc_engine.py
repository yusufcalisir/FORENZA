"""
Forensic Quality Control Engine for Biogeographical Ancestry (BGA) Ingestion.

Enforces SWGDAM / ISO/IEC 17025 QC gates:
- Call Rate Verification (>=95% Pass, 80-95% Warning, <80% Fail)
- Heterozygosity Anomaly & Multi-Contributor Contamination Guard
- Missing Marker Logit Penalization (lambda = 0.35)
"""

from typing import Dict, List, Tuple, Optional
from backend.node.services.forensic.genomics.bga.schemas import (
    IngestedBGASample,
    QCStatusEnum,
    AIMPanelTypeEnum
)
from backend.node.services.forensic.genomics.bga.panel_registry import AIMPanelRegistry


class BGAQualityControlEngine:
    """Evaluates biometric quality, completeness, and mixture integrity of AIM samples."""

    MIN_CALL_RATE_PASS: float = 95.0
    MIN_CALL_RATE_WARN: float = 80.0
    MAX_HETEROZYGOSITY_LIMIT: float = 45.0
    MIN_HETEROZYGOSITY_LIMIT: float = 10.0
    DEFAULT_MISSING_PENALTY_LAMBDA: float = 0.35

    @classmethod
    def evaluate_sample(
        cls,
        sample: IngestedBGASample,
        expected_panel: Optional[AIMPanelTypeEnum] = None
    ) -> IngestedBGASample:
        """
        Executes comprehensive QC gate checks and annotates sample with status and alerts.
        """
        panel = expected_panel or sample.primary_panel
        panel_loci = AIMPanelRegistry.get_panel_loci(panel)
        expected_locus_count = len(panel_loci) if panel_loci else sample.total_loci_assayed or 55

        flags: List[str] = []
        status = QCStatusEnum.PASS

        # 1. Call rate evaluation
        called_loci = [
            g for g in sample.genotypes.values()
            if g.allele_1 not in ("-", "0", ".", "N")
        ]
        called_count = len(called_loci)
        call_rate = (called_count / max(1, expected_locus_count)) * 100.0
        sample.called_loci_count = called_count
        sample.call_rate = round(min(100.0, call_rate), 2)

        if sample.call_rate < cls.MIN_CALL_RATE_WARN:
            status = QCStatusEnum.FAIL
            flags.append(f"CRITICAL: Severely depleted call rate ({sample.call_rate:.1f}% < {cls.MIN_CALL_RATE_WARN}%). High probability of allele dropout.")
        elif sample.call_rate < cls.MIN_CALL_RATE_PASS:
            if status != QCStatusEnum.FAIL:
                status = QCStatusEnum.WARNING
            flags.append(f"WARNING: Sub-optimal call rate ({sample.call_rate:.1f}%). Missing loci will incur logit penalty lambda={cls.DEFAULT_MISSING_PENALTY_LAMBDA}.")

        # 2. Heterozygosity and Mixture check
        if called_count >= 10:
            het_count = sum(1 for g in called_loci if g.is_heterozygous)
            het_rate = (het_count / called_count) * 100.0
            sample.heterozygosity_rate = round(het_rate, 2)

            if het_rate > cls.MAX_HETEROZYGOSITY_LIMIT:
                if status != QCStatusEnum.FAIL:
                    status = QCStatusEnum.WARNING
                flags.append(f"WARNING: Elevated heterozygosity rate ({het_rate:.1f}% > {cls.MAX_HETEROZYGOSITY_LIMIT}%). Potential multi-donor biological mixture detected.")
            elif het_rate < cls.MIN_HETEROZYGOSITY_LIMIT:
                flags.append(f"INFO: Low heterozygosity rate ({het_rate:.1f}%). Consistent with high homozygosity / isolated ancestral population.")

        # 3. Missing critical loci check
        critical_pigment_snps = {"rs12913832", "rs1426654", "rs16891982"}
        for crit in critical_pigment_snps:
            call = sample.genotypes.get(crit)
            if not call or call.allele_1 in ("-", "0", ".", "N"):
                flags.append(f"WARNING: Missing canonical driver locus '{crit}'. May affect phenotypic pleiotropic resolution.")

        sample.qc_status = status
        sample.qc_flags = flags
        return sample

    @classmethod
    def compute_missing_logit_penalty(
        cls,
        sample: IngestedBGASample,
        lambda_factor: float = DEFAULT_MISSING_PENALTY_LAMBDA
    ) -> float:
        """
        Computes the log-likelihood entropy penalty for missing loci in continuous deconvolution.
        Penalty = (1.0 - CallRate/100) * lambda_factor
        """
        missing_fraction = max(0.0, 1.0 - (sample.call_rate / 100.0))
        return round(missing_fraction * lambda_factor, 6)
