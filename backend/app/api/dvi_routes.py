"""
FORENZA Interpol Disaster Victim Identification (DVI) API Router (Module 09).

Exposes endpoints for Mass Disaster Matching & Interpol Reconciliation (Pillar 2 §4):
  POST /forensic/dvi/joint-lr           — Multi-omic joint LR computation & tier classification
  POST /forensic/dvi/reconcile-matrix   — N x M AM vs PM cross-reconciliation matrix
  GET  /forensic/dvi/decision-tiers     — Interpol DVI 4-tier standards & judicial action criteria
"""

import math
from typing import Optional
from fastapi import APIRouter, HTTPException, status

from node.services.forensic.dvi.dvi_engine import (
    DviEngine,
    INTERPOL_TIER_RULES,
    InterpolDecisionTier,
)
from node.services.forensic.models import STRGenotype, STRProfile
from node.services.forensic.dvi.missing_persons import MissingPersonsEngine
from node.services.forensic.dvi.reconciliation import DviReconciliationEngine
from .dvi_schemas import (
    DviJointLRRequest, DviJointLRResponse,
    DviMultiOmicComponentsSchema,
    DviReconciliationMatrixRequest, DviReconciliationMatrixResponse,
    DviPairwiseResultSchema,
    InterpolTiersResponse, InterpolDecisionTierMetadataSchema,
    MissingPersonsSearchRequest, MissingPersonsSearchResponse, MissingPersonCandidateHit,
    DviLegacyReconcileRequest, DviLegacyReconcileResponse, DviLegacyPairwiseComparison,
)

router = APIRouter(
    prefix="/forensic/dvi",
    tags=["Interpol DVI Mass Disaster Multi-Omic Reconciliation (Module 09)"],
)

_dvi_engine = DviEngine()
_legacy_missing_engine = MissingPersonsEngine()
_legacy_reconcile_engine = DviReconciliationEngine()



# ── Joint LR Computation ─────────────────────────────────────────────────────

@router.post(
    "/joint-lr",
    response_model=DviJointLRResponse,
    summary="Multi-Omic Joint Likelihood Ratio Computation",
    description=(
        "Computes cumulative Joint LR combining Autosomal STR, Y-STR, mtDNA, and SNP data "
        "under Interpol DVI Standing Committee guidelines. (Research §4.1, §4.2)"
    ),
    status_code=status.HTTP_200_OK,
)
async def compute_joint_lr(body: DviJointLRRequest) -> DviJointLRResponse:
    try:
        joint_lr, log10_joint, comp = _dvi_engine.compute_multi_omic_joint_lr(
            autosomal_lr=body.autosomal_lr,
            ystr_p_upper=body.ystr_p_upper,
            mtdna_p_upper=body.mtdna_p_upper,
            snp_lr=body.snp_lr,
            has_ystr=body.has_ystr,
            has_mtdna=body.has_mtdna,
            has_snp=body.has_snp,
        )
        tier, action = _dvi_engine.classify_interpol_decision_tier(joint_lr)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Joint LR calculation failed: {str(exc)}",
        )

    shield = (
        "IMPORTANT (Interpol DVI Multi-Omic Legal Shield): Standalone judicial identification "
        "requires LR_Joint >= 10^6 (log10 >= 6.0). Lower LRs (10^4 <= LR < 10^6) mandate secondary "
        "corroboration by forensic odontology, surgical serial numbers, or physical marks."
    )

    return DviJointLRResponse(
        joint_lr=round(joint_lr, 4),
        log10_joint_lr=round(log10_joint, 5),
        decision_tier=tier.value,
        components=DviMultiOmicComponentsSchema(
            autosomal_str_lr=comp.autosomal_str_lr,
            ystr_lr=comp.ystr_lr,
            ystr_p_upper=comp.ystr_p_upper,
            has_ystr=comp.has_ystr,
            mtdna_lr=comp.mtdna_lr,
            mtdna_p_upper=comp.mtdna_p_upper,
            has_mtdna=comp.has_mtdna,
            snp_lr=comp.snp_lr,
            has_snp=comp.has_snp,
        ),
        judicial_action=action,
        is_definitive_identification=(tier == InterpolDecisionTier.DEFINITIVE_IDENTIFICATION),
        prosecutors_fallacy_shield=shield,
    )


# ── N x M Matrix Reconciliation ──────────────────────────────────────────────

@router.post(
    "/reconcile-matrix",
    response_model=DviReconciliationMatrixResponse,
    summary="N x M Disaster Victim Cross-Reconciliation Matrix",
    description="Cross-compares N PM victim remains vs M AM family pedigrees with Interpol decision classifications. (Research §4.1)",
    status_code=status.HTTP_200_OK,
)
async def reconcile_matrix(body: DviReconciliationMatrixRequest) -> DviReconciliationMatrixResponse:
    try:
        pm_list = [pm.model_dump() for pm in body.pm_remains]
        am_list = [am.model_dump() for am in body.am_families]

        res = _dvi_engine.reconcile_dvi_matrix(
            disaster_event_id=body.disaster_event_id,
            pm_remains=pm_list,
            am_families=am_list,
            threshold_lr=body.threshold_lr,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"DVI matrix reconciliation failed: {str(exc)}",
        )

    matrix_schemas = [
        DviPairwiseResultSchema(
            pm_profile_id=r.pm_profile_id,
            am_family_id=r.am_family_id,
            joint_lr=r.joint_lr,
            log10_joint_lr=r.log10_joint_lr,
            decision_tier=r.decision_tier.value,
            components=DviMultiOmicComponentsSchema(
                autosomal_str_lr=r.components.autosomal_str_lr,
                ystr_lr=r.components.ystr_lr,
                ystr_p_upper=r.components.ystr_p_upper,
                has_ystr=r.components.has_ystr,
                mtdna_lr=r.components.mtdna_lr,
                mtdna_p_upper=r.components.mtdna_p_upper,
                has_mtdna=r.components.has_mtdna,
                snp_lr=r.components.snp_lr,
                has_snp=r.components.has_snp,
            ),
            judicial_action=r.judicial_action,
            is_positive_identification=r.is_positive_identification,
        )
        for r in res.reconciliation_matrix
    ]

    return DviReconciliationMatrixResponse(
        disaster_event_id=res.disaster_event_id,
        total_pm_remains=res.total_pm_remains,
        total_am_families=res.total_am_families,
        definitive_identifications_count=res.definitive_identifications_count,
        probable_matches_count=res.probable_matches_count,
        inconclusive_count=res.inconclusive_count,
        exclusions_count=res.exclusions_count,
        reconciliation_matrix=matrix_schemas,
        interpol_summary=res.interpol_summary,
        prosecutors_fallacy_shield=res.prosecutors_fallacy_shield,
    )


# ── Decision Tiers ────────────────────────────────────────────────────────────

@router.get(
    "/decision-tiers",
    response_model=InterpolTiersResponse,
    summary="Interpol DVI Decision Tiers & Thresholds",
    description="Returns statutory decision thresholds and criteria for mass disaster identification. (Research §4.2)",
    status_code=status.HTTP_200_OK,
)
async def get_interpol_decision_tiers() -> InterpolTiersResponse:
    def _clean_float(val: float) -> Optional[float]:
        if val is None or math.isinf(val) or math.isnan(val):
            return None
        return val

    tiers_list = [
        InterpolDecisionTierMetadataSchema(
            tier_name=meta.tier.value,
            min_lr=_clean_float(meta.min_lr),
            max_lr=_clean_float(meta.max_lr),
            min_log10=_clean_float(meta.min_log10),
            max_log10=_clean_float(meta.max_log10),
            judicial_action_criterion=meta.judicial_action_criterion,
            requires_secondary_corroboration=meta.requires_secondary_corroboration,
            is_court_admissible_standalone=meta.is_court_admissible_standalone,
        )
        for meta in INTERPOL_TIER_RULES.values()
    ]
    return InterpolTiersResponse(
        standard="Interpol Disaster Victim Identification (DVI) Guide Section 4 (2018/2023)",
        tiers=tiers_list,
    )


# ── Legacy Compatibility Endpoints ────────────────────────────────────────────

@router.post(
    "/missing-person/search",
    response_model=MissingPersonsSearchResponse,
    summary="Missing Persons Candidate Search (Legacy Compatible)",
    status_code=status.HTTP_200_OK,
)
async def search_missing_person_candidates(body: MissingPersonsSearchRequest) -> MissingPersonsSearchResponse:
    try:
        q_loci = {
            k: STRGenotype(locus_name=v.locus, allele1=v.allele1, allele2=v.allele2)
            for k, v in body.query_profile.loci.items()
        }
        q_prof = STRProfile(profile_id=body.query_profile.profile_id, loci=q_loci, population_group=body.query_profile.population_group or "Caucasian")

        cand_db = []
        for c in body.candidate_db:
            c_loci = {
                k: STRGenotype(locus_name=v.locus, allele1=v.allele1, allele2=v.allele2)
                for k, v in c.loci.items()
            }
            cand_db.append(STRProfile(profile_id=c.profile_id, loci=c_loci, population_group=c.population_group or "Caucasian"))

        res = _legacy_missing_engine.search_and_rank_candidates(
            query_profile=q_prof,
            candidate_db=cand_db,
            prior_probability=body.prior_probability,
            top_k=body.top_k,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Missing person search failed: {str(exc)}",
        )

    hits = [
        MissingPersonCandidateHit(
            candidate_id=h.candidate_id,
            relationship_type=h.relationship_type,
            combined_lr=h.combined_lr,
            log10_lr=h.log10_lr,
            posterior_probability=h.posterior_probability,
            matching_loci_count=h.matching_loci_count,
            evaluated_loci_count=h.evaluated_loci_count,
            confidence_tier=h.confidence_tier,
        )
        for h in res.top_candidate_hits
    ]

    return MissingPersonsSearchResponse(
        query_id=res.query_id,
        total_candidates_searched=res.total_candidates_searched,
        top_candidate_hits=hits,
        search_summary=res.search_summary,
    )


@router.post(
    "/reconcile",
    response_model=DviLegacyReconcileResponse,
    summary="DVI AM/PM Reconciliation (Legacy Compatible)",
    status_code=status.HTTP_200_OK,
)
async def reconcile_legacy_am_pm(body: DviLegacyReconcileRequest) -> DviLegacyReconcileResponse:
    try:
        am_profs = []
        for a in body.am_profiles:
            a_loci = {
                k: STRGenotype(locus_name=v.locus, allele1=v.allele1, allele2=v.allele2)
                for k, v in a.loci.items()
            }
            am_profs.append(STRProfile(profile_id=a.profile_id, loci=a_loci, population_group=a.population_group or "Caucasian"))

        pm_profs = []
        for p in body.pm_profiles:
            p_loci = {
                k: STRGenotype(locus_name=v.locus, allele1=v.allele1, allele2=v.allele2)
                for k, v in p.loci.items()
            }
            pm_profs.append(STRProfile(profile_id=p.profile_id, loci=p_loci, population_group=p.population_group or "Caucasian"))


        res = _legacy_reconcile_engine.reconcile_am_pm_profiles(
            disaster_event_id=body.disaster_event_id,
            am_profiles=am_profs,
            pm_profiles=pm_profs,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"DVI reconciliation failed: {str(exc)}",
        )

    matrix_res = [
        DviLegacyPairwiseComparison(
            am_profile_id=m.am_profile_id,
            pm_profile_id=m.pm_profile_id,
            relationship_hypothesis=m.relationship_hypothesis,
            lr=m.lr,
            log10_lr=m.log10_lr,
            identification_status=m.identification_status,
        )
        for m in res.reconciliation_matrix
    ]

    return DviLegacyReconcileResponse(
        disaster_event_id=res.disaster_event_id,
        total_am_profiles=res.total_am_profiles,
        total_pm_profiles=res.total_pm_profiles,
        confirmed_identifications_count=res.confirmed_identifications_count,
        reconciliation_matrix=matrix_res,
        dvi_summary=res.dvi_summary,
    )

