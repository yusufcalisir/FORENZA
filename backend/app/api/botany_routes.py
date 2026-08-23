"""
FORENZA Forensic Botany API Router.
Exposes endpoints for Plant Species Identification (rbcL/matK DNA barcoding, pollen morphology)
and Geographic Habitat Origin Inference under the /forensic/botany prefix.
"""

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.botany.species import ForensicBotanyEngine, BotanicalSpecimenData
from node.services.forensic.botany.habitat import PlantHabitatAuditor, PlantAssemblageEntry
from .botany_schemas import (
    BotanyIdentifyRequest, BotanyIdentifyResponse,
    HabitatInferenceRequest, HabitatInferenceResponse,
    BotanicalHitSchema
)

router = APIRouter(prefix="/forensic/botany", tags=["Forensic Botany & Palynology"])

_botany_engine = ForensicBotanyEngine()
_habitat_auditor = PlantHabitatAuditor()


@router.post(
    "/identify",
    response_model=BotanyIdentifyResponse,
    summary="Plant Species Identification",
    description="Identifies plant species and computes barcode sequence similarity (rbcL, matK) and pollen exine morphology match.",
    status_code=status.HTTP_200_OK,
)
async def identify_botanical_species(body: BotanyIdentifyRequest) -> BotanyIdentifyResponse:
    try:
        spec_dom = BotanicalSpecimenData(
            specimen_id=body.specimen.specimen_id,
            sample_type=body.specimen.sample_type,
            rbcl_sequence=body.specimen.rbcl_sequence,
            matk_sequence=body.specimen.matk_sequence,
            pollen_aperture_type=body.specimen.pollen_aperture_type,
            exine_ornamentation=body.specimen.exine_ornamentation
        )
        res = _botany_engine.identify_species(spec_dom)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Botanical species identification failed: {str(exc)}"
        )

    return BotanyIdentifyResponse(
        specimen_id=res.specimen_id,
        sample_type=res.sample_type,
        top_species_hits=[
            BotanicalHitSchema(
                species_name=h.species_name,
                family_name=h.family_name,
                dna_similarity_score=h.dna_similarity_score,
                pollen_morphology_match=h.pollen_morphology_match,
                confidence_verdict=h.confidence_verdict
            )
            for h in res.top_species_hits
        ],
        botany_summary=res.botany_summary
    )


@router.post(
    "/habitat-inference",
    response_model=HabitatInferenceResponse,
    summary="Geographic Habitat Origin Inference",
    description="Infers outdoor crime scene ecological habitat type, geographic association, and seasonal bloom window.",
    status_code=status.HTTP_200_OK,
)
async def infer_botanical_habitat(body: HabitatInferenceRequest) -> HabitatInferenceResponse:
    try:
        assemblage = [
            PlantAssemblageEntry(p.species_name, p.abundance_percentage)
            for p in body.assemblage
        ]
        res = _habitat_auditor.infer_habitat(body.sample_id, assemblage)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Habitat inference failed: {str(exc)}"
        )

    return HabitatInferenceResponse(
        sample_id=res.sample_id,
        inferred_habitat_type=res.inferred_habitat_type,
        geographic_association=res.geographic_association,
        seasonal_bloom_window=res.seasonal_bloom_window,
        habitat_match_lr=res.habitat_match_lr,
        habitat_summary=res.habitat_summary
    )
