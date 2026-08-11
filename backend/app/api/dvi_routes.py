"""
FORENZA DVI & Missing Persons API Router.
Exposes endpoints for Missing Person Candidate Ranking and Interpol AM/PM Disaster Victim Identification
under the /forensic/dvi prefix.
"""

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.models import STRGenotype, STRProfile
from node.services.forensic.dvi.missing_persons import MissingPersonsEngine
from node.services.forensic.dvi.reconciliation import DviReconciliationEngine
from .dvi_schemas import (
    MissingPersonSearchRequest, MissingPersonSearchResponse,
    DviReconcileRequest, DviReconcileResponse,
    CandidateHitSchema, DviPairwiseSchema, STRProfileSchema
)

router = APIRouter(prefix="/forensic/dvi", tags=["Missing Persons & Disaster Victim Identification (DVI)"])

_missing_persons_engine = MissingPersonsEngine()
_dvi_engine = DviReconciliationEngine()


def _convert_schema_to_domain(schema: STRProfileSchema) -> STRProfile:
    loci = {}
    for l_name, g in schema.loci.items():
        loci[l_name] = STRGenotype(g.locus, g.allele1, g.allele2)
    return STRProfile(profile_id=schema.profile_id, loci=loci, population_group=schema.population_group)


@router.post(
    "/missing-person/search",
    response_model=MissingPersonSearchResponse,
    summary="Missing Persons Candidate Ranking",
    description="Ranks database candidate profiles against a missing person target query across kinship hypotheses.",
    status_code=status.HTTP_200_OK,
)
async def search_missing_person(body: MissingPersonSearchRequest) -> MissingPersonSearchResponse:
    try:
        query_dom = _convert_schema_to_domain(body.query_profile)
        db_dom = [_convert_schema_to_domain(c) for c in body.candidate_db]

        res = _missing_persons_engine.search_and_rank_candidates(
            query_profile=query_dom,
            candidate_db=db_dom,
            prior_probability=body.prior_probability,
            top_k=body.top_k
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Missing person candidate search failed: {str(exc)}"
        )

    return MissingPersonSearchResponse(
        query_id=res.query_id,
        total_candidates_searched=res.total_candidates_searched,
        top_candidate_hits=[
            CandidateHitSchema(
                candidate_id=h.candidate_id,
                relationship_type=h.relationship_type,
                combined_lr=h.combined_lr,
                log10_lr=h.log10_lr,
                posterior_probability=h.posterior_probability,
                matching_loci_count=h.matching_loci_count,
                evaluated_loci_count=h.evaluated_loci_count,
                confidence_tier=h.confidence_tier
            )
            for h in res.top_candidate_hits
        ],
        search_summary=res.search_summary
    )


@router.post(
    "/reconcile",
    response_model=DviReconcileResponse,
    summary="Interpol AM/PM DVI Mass Casualty Reconciliation",
    description="Executes N x M cross-comparison matrix matching Ante-Mortem family references vs Post-Mortem human remains.",
    status_code=status.HTTP_200_OK,
)
async def reconcile_dvi(body: DviReconcileRequest) -> DviReconcileResponse:
    try:
        am_dom = [_convert_schema_to_domain(a) for a in body.am_profiles]
        pm_dom = [_convert_schema_to_domain(p) for p in body.pm_profiles]

        res = _dvi_engine.reconcile_am_pm_profiles(
            disaster_event_id=body.disaster_event_id,
            am_profiles=am_dom,
            pm_profiles=pm_dom
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"DVI AM/PM reconciliation failed: {str(exc)}"
        )

    return DviReconcileResponse(
        disaster_event_id=res.disaster_event_id,
        total_am_profiles=res.total_am_profiles,
        total_pm_profiles=res.total_pm_profiles,
        confirmed_identifications_count=res.confirmed_identifications_count,
        reconciliation_matrix=[
            DviPairwiseSchema(
                am_profile_id=m.am_profile_id,
                pm_profile_id=m.pm_profile_id,
                relationship_hypothesis=m.relationship_hypothesis,
                lr=m.lr,
                log10_lr=m.log10_lr,
                identification_status=m.identification_status
            )
            for m in res.reconciliation_matrix
        ],
        dvi_summary=res.dvi_summary
    )
