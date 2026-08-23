"""
FORENZA Forensic Microbiology API Router.
Exposes endpoints for 16S rRNA Taxonomic Profiling, Thanatomicrobiome PMI Estimation,
hidSkinPlex+ Touch Trace Association, Body Fluid Niche Attribution, and Soil CDI Taphonomy.
"""

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.microbiology.classifier import (
    ForensicMicrobiologyEngine,
    MicrobialProfileData,
    TaxonAbundance as LegacyTaxonAbundance
)
from node.services.forensic.microbiology.origin import MicrobialOriginAuditor
from node.services.forensic.microbiology.thanatomicrobiome import ThanatomicrobiomeEngine
from node.services.forensic.microbiology.touch_forensics import TouchMicrobiomeEngine
from node.services.forensic.microbiology.body_fluids import BodyFluidMicrobiomeClassifier
from node.services.forensic.microbiology.soil_cdi import SoilCdiEngine

from .microbiology_schemas import (
    MicrobiologyClassifyRequest, MicrobiologyClassifyResponse,
    BodySiteOriginRequest, BodySiteOriginResponse,
    ThanatoPmiRequest, ThanatoPmiResponse,
    TouchTraceMatchRequest, TouchTraceMatchResponse,
    BodyFluidMicrobiomeRequest, BodyFluidMicrobiomeResponse,
    SoilCdiTaphonomyRequest, SoilCdiTaphonomyResponse
)

router = APIRouter(prefix="/forensic/microbiology", tags=["Forensic Microbiology & Thanatometagenomics"])

_microbiology_engine = ForensicMicrobiologyEngine()
_origin_auditor = MicrobialOriginAuditor()
_thanato_engine = ThanatomicrobiomeEngine()
_touch_engine = TouchMicrobiomeEngine()
_fluid_classifier = BodyFluidMicrobiomeClassifier()
_soil_engine = SoilCdiEngine()


@router.post(
    "/classify",
    response_model=MicrobiologyClassifyResponse,
    summary="16S rRNA Taxonomic Profiling",
    description="Calculates Shannon diversity index H' and dominant bacterial phyla/genera from 16S rRNA relative abundance data.",
    status_code=status.HTTP_200_OK,
)
async def classify_microbial_taxa(body: MicrobiologyClassifyRequest) -> MicrobiologyClassifyResponse:
    try:
        prof_dom = MicrobialProfileData(
            sample_id=body.profile.sample_id,
            sample_type=body.profile.sample_type,
            taxa=[
                LegacyTaxonAbundance(t.genus_name, t.phylum_name, t.relative_abundance)
                for t in body.profile.taxa
            ]
        )
        res = _microbiology_engine.classify_microbial_profile(prof_dom)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Microbial classification failed: {str(exc)}"
        )

    return MicrobiologyClassifyResponse(
        sample_id=res.sample_id,
        shannon_diversity_index=res.shannon_diversity_index,
        dominant_genus=res.dominant_genus,
        dominant_phylum=res.dominant_phylum,
        taxa_count=res.taxa_count,
        microbiology_summary=res.microbiology_summary
    )


@router.post(
    "/body-site-origin",
    response_model=BodySiteOriginResponse,
    summary="Human Body Site Origin Prediction",
    description="Predicts human body fluid site origin (Sebaceous Skin, Oral, Vaginal, Gut) and calculates LR_microbiome.",
    status_code=status.HTTP_200_OK,
)
async def predict_microbial_body_site(body: BodySiteOriginRequest) -> BodySiteOriginResponse:
    try:
        prof_dom = MicrobialProfileData(
            sample_id=body.profile.sample_id,
            sample_type=body.profile.sample_type,
            taxa=[
                LegacyTaxonAbundance(t.genus_name, t.phylum_name, t.relative_abundance)
                for t in body.profile.taxa
            ]
        )
        res = _origin_auditor.predict_body_site_origin(prof_dom)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Body site origin prediction failed: {str(exc)}"
        )

    return BodySiteOriginResponse(
        sample_id=res.sample_id,
        predicted_body_site=res.predicted_body_site,
        site_confidence_score=res.site_confidence_score,
        indicator_species=res.indicator_species,
        origin_likelihood_ratio=res.origin_likelihood_ratio,
        origin_summary=res.origin_summary
    )


@router.post(
    "/thanato-pmi",
    response_model=ThanatoPmiResponse,
    summary="Thanatomicrobiome Post-Mortem Interval (PMI) Estimation",
    description="Calculates Accumulated Degree Days (ADD/ADH) and post-mortem interval with 95% conformal bounds.",
    status_code=status.HTTP_200_OK,
)
async def estimate_thanatomicrobiome_pmi(body: ThanatoPmiRequest) -> ThanatoPmiResponse:
    try:
        return _thanato_engine.predict_pmi(body)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Thanatomicrobiome PMI estimation failed: {str(exc)}"
        )


@router.post(
    "/touch-trace-match",
    response_model=TouchTraceMatchResponse,
    summary="Touch Trace Individualization (hidSkinPlex+)",
    description="Evaluates Score-Based Likelihood Ratios (SLR) between questioned touch trace and reference palm swabs.",
    status_code=status.HTTP_200_OK,
)
async def evaluate_touch_trace_association(body: TouchTraceMatchRequest) -> TouchTraceMatchResponse:
    try:
        return _touch_engine.evaluate_touch_association(body)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Touch trace association evaluation failed: {str(exc)}"
        )


@router.post(
    "/body-fluid",
    response_model=BodyFluidMicrobiomeResponse,
    summary="Microbial Body Fluid Niche Attribution",
    description="Performs 6-class forensic body fluid deconvolution with Softmax calibrated posterior probabilities.",
    status_code=status.HTTP_200_OK,
)
async def classify_microbial_body_fluid(body: BodyFluidMicrobiomeRequest) -> BodyFluidMicrobiomeResponse:
    try:
        return _fluid_classifier.classify_fluid(body)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Microbial body fluid classification failed: {str(exc)}"
        )


@router.post(
    "/soil-cdi",
    response_model=SoilCdiTaphonomyResponse,
    summary="Cadaver Decomposition Island (CDI) & Soil Taphonomy",
    description="Evaluates 5-stage decomposition progression and perturbation indices from soil metagenomic profiles.",
    status_code=status.HTTP_200_OK,
)
async def analyze_soil_cdi_taphonomy(body: SoilCdiTaphonomyRequest) -> SoilCdiTaphonomyResponse:
    try:
        return _soil_engine.analyze_soil_cdi(body)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Soil CDI taphonomy analysis failed: {str(exc)}"
        )
