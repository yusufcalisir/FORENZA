"""
Forensic Genetic Genealogy (FGG / IGG) Package Facade.

SWGDAM (2023) & US DOJ Interim Policy (2019) Compliant Ingestion & Kinship Architecture.
"""

from .schemas import (
    PlatformFormatEnum,
    GenotypeStateEnum,
    IBDStateEnum,
    IBDSegment,
    PairwiseIBDResult,
    KinshipDegreeEnum,
    RelationshipCandidate,
    KinshipClassificationResult,
    SexEnum,
    PedigreeNode,
    PedigreeEdge,
    MRCACluster,
    PedigreeReconstructionResult,
    QualifyingOffenseEnum,
    JurisdictionStatuteEnum,
    LegalComplianceCase,
    LegalComplianceValidation,
    SNPRecord,
    BitwiseGenotypeBlock,
    ProfileQCReport,
    IngestedFGGProfile,
)
from .liftover_normalizer import LiftoverNormalizer
from .bitwise_packer import BitwiseGenotypePacker
from .qc_engine import FGGQCEngine
from .parser import FGGGenotypeParser
from .genetic_map import FGGGeneticMap
from .ibd_detector import FGGIBDDetector
from .kinship_estimator import FGGKinshipEstimator
from .endogamy_filter import FGGEndogamyFilter
from .kinship_classifier import FGGKinshipClassifier
from .pedigree_dag import FGGPedigreeDAG
from .druid_reconstructor import FGGDruidReconstructor
from .mrca_triangulator import FGGMRCATriangulator
from .bonsai_solver import FGGBonsaiSolver
from .legal_compliance import FGGLegalComplianceEngine
from .sample_destruction_manager import FGGSampleDestructionManager, SampleDestructionOrder

__all__ = [
    "PlatformFormatEnum",
    "GenotypeStateEnum",
    "IBDStateEnum",
    "IBDSegment",
    "PairwiseIBDResult",
    "KinshipDegreeEnum",
    "RelationshipCandidate",
    "KinshipClassificationResult",
    "SexEnum",
    "PedigreeNode",
    "PedigreeEdge",
    "MRCACluster",
    "PedigreeReconstructionResult",
    "QualifyingOffenseEnum",
    "JurisdictionStatuteEnum",
    "LegalComplianceCase",
    "LegalComplianceValidation",
    "SNPRecord",
    "BitwiseGenotypeBlock",
    "ProfileQCReport",
    "IngestedFGGProfile",
    "LiftoverNormalizer",
    "BitwiseGenotypePacker",
    "FGGQCEngine",
    "FGGGenotypeParser",
    "FGGGeneticMap",
    "FGGIBDDetector",
    "FGGKinshipEstimator",
    "FGGEndogamyFilter",
    "FGGKinshipClassifier",
    "FGGPedigreeDAG",
    "FGGDruidReconstructor",
    "FGGMRCATriangulator",
    "FGGBonsaiSolver",
    "FGGLegalComplianceEngine",
    "FGGSampleDestructionManager",
    "SampleDestructionOrder",
]
