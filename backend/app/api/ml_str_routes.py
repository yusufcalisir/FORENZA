"""
FastAPI Router for Machine Learning STR Calling & Fragsifier Pre-Filtering.
Base Route: /api/v1/forensic/ml-str

Phase 69 Fixes:
  D-MLSTR-02: Dynamic repeat unit length via LOCUS_REPEAT_UNIT_REGISTRY (k=3,4,5).
  D-MLSTR-06: Analytical Gaussian area formula replaces arbitrary 8.5x multiplier.
              Area = h * fwhm * sqrt(pi / (4 * ln2))  [FWHM default = 1.25 bp]
"""

import math
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

# ---------------------------------------------------------------------------
# D-MLSTR-02: Locus Repeat Unit Length Registry
# Source: str_24_locus_microvariants_research.md & mps_ngs_str_sequence_analysis_research.md
# k=3: trinucleotide (D22S1045); k=4: tetranucleotide (majority); k=5: pentanucleotide (Penta D/E)
# ---------------------------------------------------------------------------
LOCUS_REPEAT_UNIT_REGISTRY: Dict[str, int] = {
    "TH01":      4,
    "D3S1358":   4,
    "D21S11":    4,
    "SE33":      4,
    "VWA":       4,
    "D16S539":   4,
    "D18S51":    4,
    "FGA":       4,
    "CSF1PO":    4,
    "D1S1656":   4,
    "D2S441":    4,
    "D2S1338":   4,
    "D5S818":    4,
    "D7S820":    4,
    "D8S1179":   4,
    "D10S1248":  4,
    "D12S391":   4,
    "D19S433":   4,
    "D22S1045":  3,   # trinucleotide – critical for correct back-stutter position
    "TPOX":      4,
    "PENTA_D":   5,   # pentanucleotide
    "PENTA_E":   5,   # pentanucleotide
    "D6S1043":   4,
    "D13S317":   4,
    "AMEL":      0,   # amelogenin – no repeat unit
}

_DEFAULT_REPEAT_UNIT_LEN: int = 4

# Gaussian area coefficient: sqrt(pi / (4 * ln(2)))
_GAUSSIAN_COEFF: float = math.sqrt(math.pi / (4.0 * math.log(2.0)))
# Default FWHM for CE peaks when not provided (1.25 bp per research spec)
_DEFAULT_CE_FWHM: float = 1.25


def _locus_repeat_unit(locus_name: str) -> int:
    """Lookup repeat unit length k from the canonical registry."""
    key = locus_name.upper().replace(" ", "_").replace("-", "_")
    return LOCUS_REPEAT_UNIT_REGISTRY.get(key, _DEFAULT_REPEAT_UNIT_LEN)


def _gaussian_area(height: float, fwhm: float) -> float:
    """Compute analytical Gaussian peak area.
    
    Area = h * FWHM * sqrt(pi / (4 * ln(2)))
    
    For FWHM = 1.25 bp: Area ≈ 1.330 * h  (not 8.5 * h)
    """
    return height * fwhm * _GAUSSIAN_COEFF


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
            fwhm_val = req.fwhm if req.fwhm is not None else _DEFAULT_CE_FWHM
            # D-MLSTR-02: dynamic k from registry
            k = req.repeat_unit_len if req.repeat_unit_len is not None else _locus_repeat_unit(req.locus_name)
            # D-MLSTR-06: Gaussian area instead of 8.5x
            area_val = (
                req.peak_area if req.peak_area is not None
                else _gaussian_area(req.peak_height, fwhm_val)
            )
            fv = MLSTRFeatureExtractor.extract_features(
                locus_name=req.locus_name,
                peak_id=req.peak_id,
                peak_height=req.peak_height,
                peak_area=area_val,
                fwhm=fwhm_val,
                bp_position=req.bp_position if req.bp_position is not None else 150.0,
                major_allele_bp=req.major_allele_bp if req.major_allele_bp is not None else 150.0,
                major_allele_height=req.major_allele_height,
                repeat_unit_len=k,
                sequence_string=req.sequence_string or "",
                co_eluting_secondary_rfu=req.co_eluting_secondary_rfu or 0.0,
                analytical_threshold=req.analytical_threshold if req.analytical_threshold is not None else 50.0,
            )
        return FragsifierRandomForestClassifier.classify_peak(fv)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Peak classification failed: {str(e)}"
        )


@router.post("/filter-locus", response_model=LocusMLPreFilterReport)
async def filter_locus_endpoint(req: FilterLocusPeaksRequest) -> LocusMLPreFilterReport:
    """
    Filters all peaks at a locus, generating a candidate cleaning and search space reduction report.
    """
    try:
        if req.feature_vectors is not None and len(req.feature_vectors) > 0:
            fvs = req.feature_vectors
        elif req.raw_peaks is not None and len(req.raw_peaks) > 0:
            major_peak = max(req.raw_peaks, key=lambda p: p.height)
            # D-MLSTR-02: locus-specific k; D-MLSTR-06: Gaussian area
            k = _locus_repeat_unit(req.locus_name)
            fvs = [
                MLSTRFeatureExtractor.extract_features(
                    locus_name=req.locus_name,
                    peak_id=p.peak_id,
                    peak_height=p.height,
                    peak_area=(
                        p.peak_area if p.peak_area is not None
                        else _gaussian_area(p.height, p.fwhm if p.fwhm else _DEFAULT_CE_FWHM)
                    ),
                    fwhm=p.fwhm if p.fwhm else _DEFAULT_CE_FWHM,
                    bp_position=p.bp_position,
                    major_allele_bp=major_peak.bp_position,
                    major_allele_height=major_peak.height,
                    repeat_unit_len=k,
                    sequence_string=p.sequence_string,
                    co_eluting_secondary_rfu=p.co_eluting_secondary_rfu,
                )
                for p in req.raw_peaks
            ]
        else:
            raise ValueError("Either feature_vectors or raw_peaks must be provided.")

        return FragsifierRandomForestClassifier.filter_locus_peaks(req.locus_name, fvs)
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
        if req.locus_peaks_map is not None:
            lmap = req.locus_peaks_map
        elif req.raw_locus_peaks_map is not None:
            lmap = {}
            for loc, pks in req.raw_locus_peaks_map.items():
                if not pks:
                    continue
                major_pk = max(pks, key=lambda p: p.height)
                # D-MLSTR-02 + D-MLSTR-06 applied per locus
                k = _locus_repeat_unit(loc)
                lmap[loc] = [
                    MLSTRFeatureExtractor.extract_features(
                        locus_name=loc,
                        peak_id=p.peak_id,
                        peak_height=p.height,
                        peak_area=(
                            p.peak_area if p.peak_area is not None
                            else _gaussian_area(p.height, p.fwhm if p.fwhm else _DEFAULT_CE_FWHM)
                        ),
                        fwhm=p.fwhm if p.fwhm else _DEFAULT_CE_FWHM,
                        bp_position=p.bp_position,
                        major_allele_bp=major_pk.bp_position,
                        major_allele_height=major_pk.height,
                        repeat_unit_len=k,
                        sequence_string=p.sequence_string,
                        co_eluting_secondary_rfu=p.co_eluting_secondary_rfu,
                    )
                    for p in pks
                ]
        else:
            raise ValueError("Either locus_peaks_map or raw_locus_peaks_map must be provided.")

        return MLMCMCPreFilterOptimizer.optimize_mixture_profile(
            req.case_id, lmap
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