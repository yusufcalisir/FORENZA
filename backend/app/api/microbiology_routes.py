"""
FORENZA Forensic Microbiology API Router.
Exposes endpoints for 16S rRNA Taxonomic Profiling and Human Body Site Origin Prediction
under the /forensic/microbiology prefix.
"""

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.microbiology.classifier import ForensicMicrobiologyEngine, MicrobialProfileData, TaxonAbundance
from node.services.forensic.microbiology.origin import MicrobialOriginAuditor
from .microbiology_schemas import (
    MicrobiologyClassifyRequest, MicrobiologyClassifyResponse,
    BodySiteOriginRequest, BodySiteOriginResponse
)

router = APIRouter(prefix="/forensic/microbiology", tags=["Forensic Microbiology & 16S rRNA"])

_microbiology_engine = ForensicMicrobiologyEngine()
_origin_auditor = MicrobialOriginAuditor()


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
                TaxonAbundance(t.genus_name, t.phylum_name, t.relative_abundance)
                for t in body.profile.taxa
            ]
        )
        res = _microbiology_engine.classify_microbial_profile(prof_dom)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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
                TaxonAbundance(t.genus_name, t.phylum_name, t.relative_abundance)
                for t in body.profile.taxa
            ]
        )
        res = _origin_auditor.predict_body_site_origin(prof_dom)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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
