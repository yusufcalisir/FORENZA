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
from backend.node.services.forensic.genomics.fgg.endogamy_filter import FGGEndogamyFilter
from backend.node.services.forensic.genomics.fgg.parser import FGGGenotypeParser
from backend.node.services.forensic.genomics.fgg.ibd_detector import FGGIBDDetector
from backend.node.services.forensic.genomics.fgg.kinship_classifier import FGGKinshipClassifier
from backend.node.services.forensic.genomics.fgg.bonsai_solver import FGGBonsaiSolver
from backend.node.services.forensic.genomics.fgg.mrca_triangulator import FGGMRCATriangulator
from backend.node.services.forensic.genomics.fgg.legal_compliance import FGGLegalComplianceEngine
from backend.node.services.forensic.genomics.fgg.sample_destruction_manager import FGGSampleDestructionManager, SampleDestructionOrder
from backend.node.services.forensic.genomics.fgg.golden_vectors import FGGGoldenVectors

router = APIRouter(
    prefix="/forensic/fgg",
    tags=["Forensic Genetic Genealogy (FGG / IGG)"],
)


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


class EvaluateBenchmarkRequest(BaseModel):
    """Full FGG workflow benchmark execution request."""
    model_config = ConfigDict(protected_namespaces=())

    benchmark_id: str = Field("VECTOR_FGG_01", description="Benchmark vector ID (VECTOR_FGG_01, VECTOR_FGG_02, VECTOR_FGG_03)")
    min_segment_cm: float = Field(7.0, ge=3.0, le=50.0)
    min_snps: int = Field(500, ge=100)
    jurisdiction: JurisdictionStatuteEnum = JurisdictionStatuteEnum.US_DOJ_INTERIM_2019
    offense_type: QualifyingOffenseEnum = QualifyingOffenseEnum.HOMICIDE
    is_codis_exhausted: bool = True
    prosecutor_authorization_id: str = "DA_AUTH_2026_01"
    opt_in_matches_only_enforced: bool = True


@router.post("/evaluate-benchmark", summary="Evaluate full FGG biocomputational benchmark pipeline")
async def evaluate_fgg_benchmark(req: EvaluateBenchmarkRequest) -> Dict[str, Any]:
    """
    Executes the full Forensic Genetic Genealogy (FGG) pipeline on certified golden vectors:
    - Phase-free windowed IBS0/IBD scanning
    - Cotterman (k0, k1, k2), Kinship Phi, Wright's r, and KING-robust estimation
    - Endogamy ROH filtering (F_ROH)
    - MRCA Triangulation & Bonsai Composite Pedigree DAG assembly
    - Statutory Legal Compliance Gatekeeping (US DOJ / Maryland Title 17 / Montana MCA)
    """
    bench_id = req.benchmark_id.upper()
    if "02" in bench_id:
        vec = FGGGoldenVectors.get_vector_02_ashkenazi_endogamy_trio()
        target = vec["son"]
        match = vec["father"]
        target_id = "HG002_ASHKENAZI_SON"
        match_id = "HG003_ASHKENAZI_FATHER"
        platform_name = "Illumina Global Diversity Array GDA (~1.8M SNPs)"
        mrca_label = "Ashkenazi Lineage Paternal Anchor"
        uniparental = "CONCORDANT"
    elif "03" in bench_id:
        vec = FGGGoldenVectors.get_vector_03_gsk_investigative_case()
        target = vec["crime_scene"]
        match = vec["cousin1"]
        target_id = "CRIME_SCENE_GSK_EVID_01"
        match_id = "GEDMATCH_COUSIN_1"
        platform_name = "Illumina Omni2.5 / WGS Phased (~2.4M SNPs)"
        mrca_label = "1840s Great-Great-Grandparents (John & Rebecca)"
        uniparental = "Y-STR R1b Concordant"
    else:
        vec = FGGGoldenVectors.get_vector_01_ceph_trio()
        target = vec["target"]
        match = vec["father"]
        target_id = "NA12878_DAUGHTER"
        match_id = "NA12877_FATHER"
        platform_name = "Illumina Infinium GSA (~654k SNPs)"
        mrca_label = "Direct Generation"
        uniparental = "CONCORDANT"

    # Step 1: IBD Detection
    ibd_res = FGGIBDDetector.detect_pairwise_ibd(
        target, match, min_cm=req.min_segment_cm, min_snps=req.min_snps
    )

    # Step 2: Kinship Classification
    kinship_res = FGGKinshipClassifier.classify_kinship(ibd_res, target, match)

    # Step 3: Endogamy ROH evaluation
    f_roh_target = FGGEndogamyFilter.compute_individual_f_roh(target)
    f_roh_match = FGGEndogamyFilter.compute_individual_f_roh(match)

    # Step 4: Bonsai Pedigree Assembly
    if "03" in bench_id:
        c2 = vec["cousin2"]
        ibd_c2 = FGGIBDDetector.detect_pairwise_ibd(target, c2, min_cm=req.min_segment_cm, min_snps=req.min_snps)
        kin_c2 = FGGKinshipClassifier.classify_kinship(ibd_c2, target, c2)
        match_seg_map = {match_id: ibd_res.segments, "GEDMATCH_COUSIN_2": ibd_c2.segments}
        mrca_clusters = FGGMRCATriangulator.triangulate_clusters(match_seg_map, target_y_haplogroup="R1b")
        pedigree_tree = FGGBonsaiSolver.reconstruct_pedigree(
            target_id=target_id,
            target_birth_year=1945,
            target_sex=SexEnum.MALE,
            target_y_hap="R1b",
            target_mt_hap="U5b",
            match_results=[kinship_res, kin_c2],
            mrca_clusters=mrca_clusters
        )
    else:
        match_seg_map = {match_id: ibd_res.segments}
        mrca_clusters = FGGMRCATriangulator.triangulate_clusters(match_seg_map)
        pedigree_tree = FGGBonsaiSolver.reconstruct_pedigree(
            target_id=target_id,
            target_birth_year=1980,
            target_sex=SexEnum.FEMALE if "01" in bench_id else SexEnum.MALE,
            target_y_hap=None if "01" in bench_id else "J2a",
            target_mt_hap="H1" if "01" in bench_id else "K1a",
            match_results=[kinship_res],
            mrca_clusters=mrca_clusters
        )

    # Step 5: Statutory Legal Compliance Validation
    case = LegalComplianceCase(
        case_id="CASE_FGG_2026",
        jurisdiction=req.jurisdiction,
        offense_type=req.offense_type,
        is_codis_exhausted=req.is_codis_exhausted,
        prosecutor_authorization_id=req.prosecutor_authorization_id,
        opt_in_matches_only_enforced=req.opt_in_matches_only_enforced
    )
    legal_val = FGGLegalComplianceEngine.validate_case(case)

    # Convert segments to UI-friendly format
    segments_ui = [
        {
            "chr": s.chromosome,
            "startBp": s.start_bp,
            "endBp": s.end_bp,
            "startCm": s.start_cm,
            "endCm": s.end_cm,
            "lengthCm": s.length_cm,
            "snpCount": s.snp_count,
            "type": "IBD2" if s.ibd_state.value == 2 else "IBD1"
        }
        for s in ibd_res.segments
    ]

    top_cand = kinship_res.top_candidate
    candidates_list = [
        {
            "degree": c.degree.value,
            "label": c.relationship_label or c.degree.name.replace("_", " "),
            "probability": c.probability,
            "expectedMeanCm": c.expected_mean_cm,
            "range": f"{c.typical_cm_range_min:.1f} - {c.typical_cm_range_max:.1f} cM"
        }
        for c in kinship_res.all_candidates
    ]

    return {
        "benchmark_id": req.benchmark_id,
        "target_id": target_id,
        "match_id": match_id,
        "platform": platform_name,
        "total_shared_cm": ibd_res.total_shared_cm,
        "longest_shared_cm": ibd_res.longest_segment_cm,
        "segment_count": ibd_res.segment_count,
        "segments": segments_ui,
        "cotterman_k0": ibd_res.cotterman_k0,
        "cotterman_k1": ibd_res.cotterman_k1,
        "cotterman_k2": ibd_res.cotterman_k2,
        "kinship_phi": ibd_res.kinship_phi,
        "wright_r": ibd_res.wright_r,
        "king_phi": ibd_res.king_phi,
        "top_candidate": {
            "degree": top_cand.degree.value,
            "label": top_cand.relationship_label or top_cand.degree.name.replace("_", " "),
            "probability": top_cand.probability,
            "expectedMeanCm": top_cand.expected_mean_cm,
            "range": f"{top_cand.typical_cm_range_min:.1f} - {top_cand.typical_cm_range_max:.1f} cM"
        } if top_cand else None,
        "candidates": candidates_list,
        "is_endogamy_suspected": kinship_res.is_endogamy_suspected,
        "f_roh_target": f_roh_target,
        "f_roh_match": f_roh_match,
        "adjusted_shared_cm": kinship_res.adjusted_shared_cm,
        "mrca_label": mrca_label,
        "uniparental_status": uniparental,
        "pedigree_tree": pedigree_tree.model_dump() if pedigree_tree else None,
        "legal_compliance": legal_val.model_dump()
    }


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
