"""
FastAPI REST API Router for Forensic Genetic Genealogy (FGG / IGG).

SWGDAM (2023), US DOJ Interim Policy (2019), and Maryland Title 17 Compliant Endpoints.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Body
from pydantic import BaseModel, Field, ConfigDict

from backend.node.services.forensic.genomics.fgg.schemas import (
    PlatformFormatEnum,
    GenotypeStateEnum,
    IBDSegment,
    PairwiseIBDResult,
    KinshipClassificationResult,
    PedigreeReconstructionResult,
    LegalComplianceCase,
    LegalComplianceValidation,
    QualifyingOffenseEnum,
    JurisdictionStatuteEnum,
    SexEnum
)
from backend.node.services.forensic.genomics.fgg.parser import FGGGenotypeParser
from backend.node.services.forensic.genomics.fgg.ibd_detector import FGGIBDDetector
from backend.node.services.forensic.genomics.fgg.kinship_classifier import FGGKinshipClassifier
from backend.node.services.forensic.genomics.fgg.bonsai_solver import FGGBonsaiSolver
from backend.node.services.forensic.genomics.fgg.mrca_triangulator import FGGMRCATriangulator
from backend.node.services.forensic.genomics.fgg.legal_compliance import FGGLegalComplianceEngine
from backend.node.services.forensic.genomics.fgg.sample_destruction_manager import FGGSampleDestructionManager, SampleDestructionOrder
from backend.node.services.forensic.genomics.fgg.golden_vectors import FGGGoldenVectors

router = APIRouter()


class IngestRawTextRequest(BaseModel):
    """Request payload for raw genotype string ingestion."""
    model_config = ConfigDict(protected_namespaces=())

    raw_text: str = Field(..., description="Raw text content of SNP microarray or VCF")
    profile_id: str = Field(default="SAMPLE_PROFILE", description="Unique sample identifier")
    force_platform: Optional[PlatformFormatEnum] = None


class PairwiseIBDRequest(BaseModel):
    """Pairwise IBD detection request between two raw profile strings."""
    model_config = ConfigDict(protected_namespaces=())

    raw_text_a: str
    profile_id_a: str = "SAMPLE_A"
    raw_text_b: str
    profile_id_b: str = "SAMPLE_B"
    min_segment_cm: Optional[float] = 7.0
    min_snps: Optional[int] = 500


class PedigreeReconstructionRequest(BaseModel):
    """Pedigree DAG assembly request."""
    model_config = ConfigDict(protected_namespaces=())

    target_profile_raw: str
    target_id: str = "TARGET_SAMPLE"
    target_birth_year: Optional[int] = None
    target_sex: SexEnum = SexEnum.UNKNOWN
    target_y_haplogroup: Optional[str] = None
    target_mtdna_haplogroup: Optional[str] = None
    match_profiles: List[Dict[str, str]] = Field(
        ..., description="List of dicts with keys 'profile_id' and 'raw_text'"
    )


class SampleDestructionRequest(BaseModel):
    """Destruction order generation request."""
    model_config = ConfigDict(protected_namespaces=())

    case_id: str
    statutory_basis: str
    reference_sample_ids: List[str]
    certifying_officer: str


@router.post("/ingest", summary="Ingest raw SNP array or VCF file")
async def ingest_genotype_file(req: IngestRawTextRequest) -> Dict[str, Any]:
    """Ingests raw text and produces 2-bit packed blocks and QC metrics."""
    try:
        profile = FGGGenotypeParser.parse_profile(
            content=req.raw_text,
            profile_id=req.profile_id,
            force_platform=req.force_platform
        )
        return {
            "status": "SUCCESS",
            "profile_id": profile.profile_id,
            "platform": profile.platform.value,
            "assembly": profile.assembly_version,
            "qc_report": profile.qc_report.model_dump(),
            "chromosomes_loaded": list(profile.chromosome_blocks.keys()),
            "total_snps_evaluated": profile.qc_report.total_snps_evaluated
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ibd-pairwise", response_model=PairwiseIBDResult, summary="Detect pairwise IBD segments")
async def detect_pairwise_ibd(req: PairwiseIBDRequest) -> PairwiseIBDResult:
    """Detects multi-megabase IBD1/IBD2 segments between two profiles."""
    try:
        p_a = FGGGenotypeParser.parse_profile(req.raw_text_a, profile_id=req.profile_id_a)
        p_b = FGGGenotypeParser.parse_profile(req.raw_text_b, profile_id=req.profile_id_b)
        result = FGGIBDDetector.detect_pairwise_ibd(p_a, p_b, min_cm=req.min_segment_cm, min_snps=req.min_snps)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/classify-kinship", response_model=KinshipClassificationResult, summary="Classify kinship degree")
async def classify_kinship_pairwise(req: PairwiseIBDRequest) -> KinshipClassificationResult:
    """Classifies genealogical degree with Shared cM Project models and endogamy filtering."""
    try:
        p_a = FGGGenotypeParser.parse_profile(req.raw_text_a, profile_id=req.profile_id_a)
        p_b = FGGGenotypeParser.parse_profile(req.raw_text_b, profile_id=req.profile_id_b)
        ibd_res = FGGIBDDetector.detect_pairwise_ibd(p_a, p_b, min_cm=req.min_segment_cm, min_snps=req.min_snps)
        class_res = FGGKinshipClassifier.classify_kinship(ibd_res, p_a, p_b)
        return class_res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reconstruct-pedigree", response_model=PedigreeReconstructionResult, summary="Reconstruct pedigree DAG")
async def reconstruct_pedigree_tree(req: PedigreeReconstructionRequest) -> PedigreeReconstructionResult:
    """Builds multi-generational pedigree DAG with MRCA triangulation."""
    try:
        target_profile = FGGGenotypeParser.parse_profile(req.target_profile_raw, profile_id=req.target_id)
        
        match_class_results = []
        match_segments_map = {}

        for m in req.match_profiles:
            mp_id = m.get("profile_id", "UNKNOWN_MATCH")
            mp_raw = m.get("raw_text", "")
            match_p = FGGGenotypeParser.parse_profile(mp_raw, profile_id=mp_id)
            
            ibd_res = FGGIBDDetector.detect_pairwise_ibd(target_profile, match_p)
            class_res = FGGKinshipClassifier.classify_kinship(ibd_res, target_profile, match_p)
            match_class_results.append(class_res)
            match_segments_map[mp_id] = ibd_res.segments

        # Triangulate MRCAs
        mrca_clusters = FGGMRCATriangulator.triangulate_clusters(
            match_segments_map,
            target_y_haplogroup=req.target_y_haplogroup,
            target_mtdna_haplogroup=req.target_mtdna_haplogroup
        )

        # Assemble tree via Bonsai
        tree = FGGBonsaiSolver.reconstruct_pedigree(
            target_id=req.target_id,
            target_birth_year=req.target_birth_year,
            target_sex=req.target_sex,
            target_y_hap=req.target_y_haplogroup,
            target_mt_hap=req.target_mtdna_haplogroup,
            match_results=match_class_results,
            mrca_clusters=mrca_clusters
        )
        return tree
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/validate-legal", response_model=LegalComplianceValidation, summary="Validate statutory compliance")
async def validate_legal_compliance(case: LegalComplianceCase) -> LegalComplianceValidation:
    """Enforces US DOJ (2019), Maryland Title 17, and Montana MCA statutory rules."""
    return FGGLegalComplianceEngine.validate_case(case)


@router.post("/sample-destruction-order", response_model=SampleDestructionOrder, summary="Generate sample destruction certificate")
async def generate_sample_destruction_order(req: SampleDestructionRequest) -> SampleDestructionOrder:
    """Generates certified destruction order for reference DNA samples."""
    return FGGSampleDestructionManager.generate_destruction_order(
        case_id=req.case_id,
        statutory_basis=req.statutory_basis,
        reference_sample_ids=req.reference_sample_ids,
        certifying_officer=req.certifying_officer
    )


@router.get("/benchmarks", summary="List available FGG golden standard benchmarks")
async def get_fgg_benchmarks() -> Dict[str, Any]:
    """Returns catalog of standard golden benchmark vectors."""
    return {
        "benchmarks": [
            {
                "id": "VECTOR_FGG_01",
                "title": "CEPH / GIAB NA12878 Multi-Generational Trio Benchmark",
                "description": "Standard European benchmark with 100% IBD1 parent-child transmission"
            },
            {
                "id": "VECTOR_FGG_02",
                "title": "GIAB Ashkenazi Trio (HG002, HG003, HG004) Endogamy Benchmark",
                "description": "Evaluates F_ROH > 4% resistance to false close-cousin calling"
            },
            {
                "id": "VECTOR_FGG_03",
                "title": "Golden State Killer (GSK) Investigative Case Benchmark",
                "description": "Simulates 3rd cousin matching (~80 cM) and 1840s MRCA couple triangulation"
            }
        ]
    }
