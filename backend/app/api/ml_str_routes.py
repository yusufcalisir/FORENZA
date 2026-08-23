"""
FastAPI Router for Machine Learning STR Calling & Fragsifier Pre-Filtering.
Base Route: /api/v1/forensic/ml-str
"""

from typing import Dict, List, Any
from fastapi import APIRouter, HTTPException, status

from node.services.forensic.genomics.ml_str.feature_extractor import MLSTRFeatureExtractor
from node.services.forensic.genomics.ml_str.classifier import FragsifierRandomForestClassifier
from node.services.forensic.genomics.ml_str.isfg_hierarchy import ISFGHierarchyEngine
from node.services.forensic.genomics.ml_str.mcmc_prefilter import MLMCMCPreFilterOptimizer
from node.services.forensic.genomics.ml_str.golden_vectors import GOLDEN_VECTORS_MLSTR
from .ml_str_schemas import (
    ExtractFeaturesRequest,
    ClassifyPeakRequest,
    FilterLocusPeaksRequest,
    ISFGHierarchyRequest,
    MultiLocusPreFilterRequest,
    FeatureVector24D,
    PeakClassificationResult,
    LocusMLPreFilterReport,
    ISFGHierarchicalRepresentation,
    MultiLocusPreFilterSummary,
)

router = APIRouter(prefix="/forensic/ml-str", tags=["Forensic ML STR Calling & Fragsifier"])


@router.post("/extract-features", response_model=FeatureVector24D)
async def extract_features_endpoint(req: ExtractFeaturesRequest) -> FeatureVector24D:
    """
    Extracts 24-dimensional feature representations for forensic peak classification.
    """
    try:
        return MLSTRFeatureExtractor.extract_features(
            locus_name=req.locus_name,
            peak_id=req.peak_id,
            peak_height=req.peak_height,
            peak_area=req.peak_area,
            fwhm=req.fwhm,
            bp_position=req.bp_position,
            major_allele_bp=req.major_allele_bp,
            major_allele_height=req.major_allele_height,
            repeat_unit_len=req.repeat_unit_len,
            sequence_string=req.sequence_string,
            co_eluting_secondary_rfu=req.co_eluting_secondary_rfu,
            analytical_threshold=req.analytical_threshold
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Feature extraction failed: {str(e)}"
        )


@router.post("/classify-peak", response_model=PeakClassificationResult)
async def classify_peak_endpoint(req: ClassifyPeakRequest) -> PeakClassificationResult:
    """
    Classifies a candidate peak into one of 7 biophysical classes via Fragsifier ensemble.
    """
    try:
        if req.feature_vector is not None:
            fv = req.feature_vector
        else:
            if req.locus_name is None or req.peak_id is None or req.peak_height is None:
                raise ValueError("Either feature_vector or (locus_name, peak_id, peak_height) must be provided.")
            fv = MLSTRFeatureExtractor.extract_features(
                locus_name=req.locus_name,
                peak_id=req.peak_id,
                peak_height=req.peak_height,
                peak_area=req.peak_area,
                fwhm=req.fwhm if req.fwhm is not None else 1.0,
                bp_position=req.bp_position if req.bp_position is not None else 150.0,
                major_allele_bp=req.major_allele_bp if req.major_allele_bp is not None else 150.0,
                major_allele_height=req.major_allele_height,
                repeat_unit_len=req.repeat_unit_len if req.repeat_unit_len is not None else 4,
                sequence_string=req.sequence_string or "",
                co_eluting_secondary_rfu=req.co_eluting_secondary_rfu or 0.0,
                analytical_threshold=req.analytical_threshold if req.analytical_threshold is not None else 50.0,
            )
        return FragsifierRandomForestClassifier.classify_peak(fv)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Peak classification failed: {str(e)}"
        )



@router.post("/filter-locus", response_model=LocusMLPreFilterReport)
async def filter_locus_endpoint(req: FilterLocusPeaksRequest) -> LocusMLPreFilterReport:
    """
    Filters all peaks at a locus, generating a candidate cleaning and search space reduction report.
    """
    try:
        return FragsifierRandomForestClassifier.filter_locus_peaks(req.locus_name, req.feature_vectors)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Locus filtering failed: {str(e)}"
        )


@router.post("/translate-isfg", response_model=ISFGHierarchicalRepresentation)
async def translate_isfg_endpoint(req: ISFGHierarchyRequest) -> ISFGHierarchicalRepresentation:
    """
    Translates forensic STR sequences across ISFG 3-tier hierarchical levels (Text -> Alignment -> Nomenclature).
    """
    try:
        return ISFGHierarchyEngine.build_hierarchical_representation(
            req.locus_name, req.sequence_or_bracketed_string
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ISFG hierarchy translation failed: {str(e)}"
        )


@router.post("/prefilter-mixture", response_model=MultiLocusPreFilterSummary)
async def prefilter_mixture_endpoint(req: MultiLocusPreFilterRequest) -> MultiLocusPreFilterSummary:
    """
    Optimizes multi-locus mixture profiles before MCMC Markov chain initialization.
    """
    try:
        return MLMCMCPreFilterOptimizer.optimize_mixture_profile(
            req.case_id, req.locus_peaks_map
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mixture pre-filtering failed: {str(e)}"
        )


@router.get("/golden-vectors", response_model=List[Dict[str, Any]])
async def get_golden_vectors_endpoint() -> List[Dict[str, Any]]:
    """
    Returns all 4 certified golden benchmark test vectors for ML STR calling.
    """
    return [
        {
            "vector_id": v.vector_id,
            "name": v.name,
            "locus": v.locus,
            "challenge_type": v.challenge_type,
            "raw_peak_descriptions": v.raw_peak_descriptions,
            "expected_classification_labels": v.expected_classification_labels,
            "expected_action_taken": v.expected_action_taken,
            "mcmc_speedup_factor": v.mcmc_speedup_factor,
            "description": v.description,
            "iso17025_conformance_note": v.iso17025_conformance_note,
        }
        for v in GOLDEN_VECTORS_MLSTR.values()
    ]
