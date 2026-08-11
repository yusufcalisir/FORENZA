"""
FORENZA Population Genetics API Router.
Exposes endpoints for NRC II frequency bounding, Wright's FST distance calculation,
and population database specifications under the /population prefix.
"""

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.frequency_db import FrequencyDatabase
from node.services.forensic.population.substructure import SubstructureEngine
from node.services.forensic.population.rare_allele import RareAlleleEngine
from .population_schemas import (
    FrequencyBoundRequest, FrequencyBoundResponse,
    FstDistanceRequest, FstDistanceResponse,
    PopulationListResponse
)

router = APIRouter(prefix="/forensic/population", tags=["Population Genetics"])

_freq_db = FrequencyDatabase()
_rare_engine = RareAlleleEngine(default_database_n=500)
_substructure_engine = SubstructureEngine()


@router.get(
    "/populations",
    response_model=PopulationListResponse,
    summary="List Supported Populations",
    description="Returns supported reference populations and NRC II 5/2N minimum bound defaults.",
    status_code=status.HTTP_200_OK,
)
async def list_populations() -> PopulationListResponse:
    return PopulationListResponse(
        supported_populations=_freq_db.supported_populations,
        default_database_n=500,
        nrc2_recommendation="Recommendation 4.1: Minimum allele frequency bound = 5 / (2N)"
    )


@router.post(
    "/frequency",
    response_model=FrequencyBoundResponse,
    summary="NRC II Rare Allele Bounding",
    description="Applies NRC II Recommendation 4.1 5/2N minimum frequency bound to rare or unobserved alleles.",
    status_code=status.HTTP_200_OK,
)
async def bound_frequency(body: FrequencyBoundRequest) -> FrequencyBoundResponse:
    try:
        res = _rare_engine.bound_allele_frequency(
            locus=body.locus,
            allele=body.allele,
            raw_freq=body.raw_frequency,
            observed_count=body.observed_count,
            n_individuals=body.database_n
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Frequency bounding failed: {str(exc)}"
        )

    return FrequencyBoundResponse(
        locus=res.locus,
        allele=res.allele,
        observed_count=res.observed_count,
        raw_frequency=res.raw_frequency,
        bounded_frequency=res.bounded_frequency,
        was_bounded=res.was_bounded,
        rarity_index=res.rarity_index,
        explanation=res.explanation
    )


@router.post(
    "/fst",
    response_model=FstDistanceResponse,
    summary="Wright's FST & Nei Genetic Distance",
    description="Computes Wright's FST pairwise fixation index and Nei standard genetic distance between two populations.",
    status_code=status.HTTP_200_OK,
)
async def compute_fst_distance(body: FstDistanceRequest) -> FstDistanceResponse:
    try:
        res = _substructure_engine.compute_pairwise_fst(
            pop1=body.population1,
            pop2=body.population2
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"FST distance calculation failed: {str(exc)}"
        )

    return FstDistanceResponse(
        population_pair=list(res.population_pair),
        fst_value=res.fst_value,
        genetic_distance_neis=res.genetic_distance_neis,
        locus_fst_breakdown=res.locus_fst_breakdown,
        recommendation=res.recommendation
    )
