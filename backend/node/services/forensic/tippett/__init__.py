"""
FORENZA Forensic Evidence Operating System
Pillar 1 — Module 1.5: Tippett Plot ROC Calibration & Misleading Evidence Lab
"""

from .tippett_mathematical_formulation import (
    TippettPoint,
    TippettCurveResult,
    ROCAnalysisResult,
    CllrCostResult,
    HPDLowerBoundResult,
    TippettMathematicalFormulation,
    LOG10_LR_MIN,
    LOG10_LR_MAX,
    CLLR_TARGET_EXCELLENT,
    CLLR_TARGET_ACCEPTABLE,
    MIN_ECCDF_SAMPLES,
    ROYALL_MISLEADING_BOUND_EXPONENT,
)

from .tippett_reference_datasets import (
    TippettBenchmarkCohort,
    TippettReferenceDatasetRegistry,
    NIST_1036_FREQUENCIES,
    NIST_SRM2391D_COMP_A_GENOTYPES,
)

from .tippett_cross_validation import (
    ENFSIReportResult,
    ToolCrossValidationResult,
    TippettCrossValidationEngine,
    ENFSI_TIERS,
)

__all__ = [
    "TippettPoint",
    "TippettCurveResult",
    "ROCAnalysisResult",
    "CllrCostResult",
    "HPDLowerBoundResult",
    "TippettMathematicalFormulation",
    "TippettBenchmarkCohort",
    "TippettReferenceDatasetRegistry",
    "NIST_1036_FREQUENCIES",
    "NIST_SRM2391D_COMP_A_GENOTYPES",
    "ENFSIReportResult",
    "ToolCrossValidationResult",
    "TippettCrossValidationEngine",
    "ENFSI_TIERS",
    "LOG10_LR_MIN",
    "LOG10_LR_MAX",
    "CLLR_TARGET_EXCELLENT",
    "CLLR_TARGET_ACCEPTABLE",
    "MIN_ECCDF_SAMPLES",
    "ROYALL_MISLEADING_BOUND_EXPONENT",
]
