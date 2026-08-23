"""
FORENZA Microscopy Intelligence API Router.
Exposes endpoints for Microscopic Cell Classification and Hair Medullary Index & DNA Strategy Routing
under the /forensic/microscopy prefix.
"""

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.microscopy.classifier import MicroscopyIntelligenceEngine
from .microscopy_schemas import (
    ClassifyCellRequest, ClassifyCellResponse,
    HairMorphologyRequest, HairMorphologyResponse
)

router = APIRouter(prefix="/forensic/microscopy", tags=["Microscopy Intelligence & Hair Analysis"])

_microscopy_engine = MicroscopyIntelligenceEngine()


@router.post(
    "/classify-cell",
    response_model=ClassifyCellResponse,
    summary="Microscopic Cell Morphometry Classification",
    description="Classifies sperm head morphometry, length/width ratio, and acrosome coverage percentage.",
    status_code=status.HTTP_200_OK,
)
async def classify_cell(body: ClassifyCellRequest) -> ClassifyCellResponse:
    try:
        res = _microscopy_engine.classify_sperm_cell(
            cell_id=body.cell_id,
            head_length_um=body.head_length_um,
            head_width_um=body.head_width_um,
            acrosome_coverage_pct=body.acrosome_coverage_pct
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Cell morphometry classification failed: {str(exc)}"
        )

    return ClassifyCellResponse(
        cell_id=res.cell_id,
        cell_type=res.cell_type,
        head_length_um=res.head_length_um,
        head_width_um=res.head_width_um,
        acrosome_coverage_pct=res.acrosome_coverage_pct,
        normal_morphology=res.normal_morphology
    )


@router.post(
    "/hair-morphology",
    response_model=HairMorphologyResponse,
    summary="Hair Medullary Index & DNA Strategy Routing",
    description="Calculates medullary index (I_medulla), discriminates human vs. animal origin, and routes for nDNA STR vs. mtDNA HV1/HV2.",
    status_code=status.HTTP_200_OK,
)
async def analyze_hair_morphology(body: HairMorphologyRequest) -> HairMorphologyResponse:
    try:
        res = _microscopy_engine.analyze_hair_morphology(
            hair_id=body.hair_id,
            hair_diameter_um=body.hair_diameter_um,
            medulla_diameter_um=body.medulla_diameter_um,
            root_status=body.root_status
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Hair morphology analysis failed: {str(exc)}"
        )

    return HairMorphologyResponse(
        hair_id=res.hair_id,
        hair_diameter_um=res.hair_diameter_um,
        medulla_diameter_um=res.medulla_diameter_um,
        medullary_index=res.medullary_index,
        species_origin=res.species_origin,
        root_status=res.root_status,
        dna_routing=res.dna_routing,
        microscopy_summary=res.microscopy_summary
    )
