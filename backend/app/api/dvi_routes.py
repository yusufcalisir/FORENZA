"""
FORENZA Interpol Disaster Victim Identification (DVI) API Router (Module 2.4).
Standards Compliance: ISO/IEC 17025:2017, Interpol DVI Guide Section 4 (2018, 2023),
ENFSI Guidelines for Evaluative Reporting in Forensic Science (2017).

Research Source: research/pillar_2_lineage_kinship_research.md §4.

Exposes endpoints for Mass Disaster Matching & Interpol Reconciliation:
  POST /forensic/dvi/joint-lr            — Multi-omic joint LR computation & tier classification
  POST /forensic/dvi/reconcile-matrix    — N x M AM vs PM cross-reconciliation matrix & Hungarian assignment
  GET  /forensic/dvi/decision-tiers      — Interpol DVI 4-tier standards & judicial action criteria
  GET  /forensic/dvi/pedigree-templates  — 4 Standard Interpol Pedigree Templates
  GET  /forensic/dvi/casework-cohorts    — Certified Casework Benchmark Cohorts
  GET  /forensic/dvi/reporting-disclaimer— Interpol & ENFSI Evaluative Reporting Disclaimer
  POST /forensic/dvi/missing-person/search — Search missing persons database
  POST /forensic/dvi/reconcile           — Standard AM/PM profile batch reconciliation
"""

import math
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, status

from node.services.forensic.dvi.dvi_mathematical_formulation import (
    DviMathematicalFormulation,
    InterpolDecisionTier,
    INTERPOL_TIER_RULES,
)
from node.services.forensic.dvi.dvi_reference_datasets import (
    DviReferenceDatasets,
    DviPedigreeTemplateType,
    DVI_PEDIGREE_TEMPLATES,
    DVI_CASEWORK_COHORTS,
)
from node.services.forensic.dvi.dvi_cross_validation import (
    DviCrossValidationEngine,
)
from node.services.forensic.models import STRGenotype, STRProfile
from node.services.forensic.dvi.missing_persons import MissingPersonsEngine
from node.services.forensic.dvi.reconciliation import DviReconciliationEngine
from .dvi_schemas import (
    DviJointLRRequest, DviJointLRResponse,
    DviMultiOmicComponentsSchema,
    DviReconciliationMatrixRequest, DviReconciliationMatrixResponse,
    DviPairwiseResultSchema, DviOptimalAssignmentSchema,
    InterpolTiersResponse, InterpolDecisionTierMetadataSchema,
    DviPedigreeTemplateSchema, DviCaseworkCohortSchema,
)

router = APIRouter(
    prefix="/forensic/dvi",
    tags=["Interpol DVI Mass Disaster Multi-Omic Reconciliation (Module 2.4)"],
)

_legacy_missing_engine = MissingPersonsEngine()
_legacy_reconcile_engine = DviReconciliationEngine()


def _parse_str_profile_dict(prof_dict: Dict[str, Any]) -> STRProfile:
    pid = prof_dict.get("profile_id", prof_dict.get("sample_id", "SAMPLE"))
    pop = prof_dict.get("population_group", "Caucasian")
    loci_raw = prof_dict.get("loci", prof_dict.get("profile", {}))
    genotypes: Dict[str, STRGenotype] = {}
    for locus, val in loci_raw.items():
        if isinstance(val, (list, tuple)) and len(val) >= 2:
            genotypes[locus] = STRGenotype(locus_name=locus, allele1=float(val[0]), allele2=float(val[1]))
        elif isinstance(val, dict):
            a1 = float(val.get("allele1", val.get("allele_1", 0.0)))
            a2 = float(val.get("allele2", val.get("allele_2", 0.0)))
            genotypes[locus] = STRGenotype(locus_name=locus, allele1=a1, allele2=a2)
    return STRProfile(profile_id=pid, loci=genotypes, population_group=pop)


# ── 1. Joint LR Computation ──────────────────────────────────────────────────

@router.post(
    "/joint-lr",
    response_model=DviJointLRResponse,
    summary="Multi-Omic Joint Likelihood Ratio Computation",
    description=(
        "Computes cumulative Joint LR combining Autosomal STR, Y-STR, mtDNA, and SNP data "
        "under Interpol DVI Standing Committee guidelines and calculates Bayesian posterior probability W. (Research §4.1, §4.2)"
    ),
    status_code=status.HTTP_200_OK,
)
async def compute_joint_lr(body: DviJointLRRequest) -> DviJointLRResponse:
    try:
        joint_lr, log10_joint = DviMathematicalFormulation.compute_multi_omic_joint_lr(
            autosomal_lr=body.autosomal_lr,
            ystr_p_upper=body.ystr_p_upper or 1.0,
            mtdna_p_upper=body.mtdna_p_upper or 1.0,
            snp_lr=body.snp_lr,
            has_ystr=body.has_ystr,
            has_mtdna=body.has_mtdna,
            has_snp=body.has_snp,
        )
        tier, action = DviMathematicalFormulation.classify_interpol_tier(joint_lr)
        w = DviMathematicalFormulation.compute_posterior_probability(joint_lr=joint_lr, prior=body.prior_probability)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"DVI Joint LR calculation error: {str(exc)}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DVI Joint LR calculation failed: {str(exc)}",
        )

    # Calculate individual components
    ystr_lr = (1.0 / body.ystr_p_upper) if (body.has_ystr and body.ystr_p_upper and body.ystr_p_upper > 0) else 1.0
    mtdna_lr = (1.0 / body.mtdna_p_upper) if (body.has_mtdna and body.mtdna_p_upper and body.mtdna_p_upper > 0) else 1.0

    comp = DviMultiOmicComponentsSchema(
        autosomal_str_lr=body.autosomal_lr,
        ystr_lr=ystr_lr,
        ystr_p_upper=body.ystr_p_upper,
        has_ystr=body.has_ystr,
        mtdna_lr=mtdna_lr,
        mtdna_p_upper=body.mtdna_p_upper,
        has_mtdna=body.has_mtdna,
        snp_lr=body.snp_lr,
        has_snp=body.has_snp,
    )

    if tier == InterpolDecisionTier.DEFINITIVE_IDENTIFICATION:
        v_en = "Definitive Forensic Identification (LR >= 1,000,000, W >= 0.999999)"
        v_tr = "Kesin Adli Kimliklendirme (LR >= 1.000.000, W >= 0.999999)"
    elif tier == InterpolDecisionTier.PROBABLE_MATCH:
        v_en = "Probable Identification Requiring Secondary Corroboration (10,000 <= LR < 1,000,000)"
        v_tr = "İkincil Doğrulama Gerektiren Olası Kimliklendirme (10.000 <= LR < 1.000.000)"
    elif tier == InterpolDecisionTier.INCONCLUSIVE:
        v_en = "Inconclusive Identification (0.01 < LR < 10,000)"
        v_tr = "Yetersiz / Sonuçsuz Eşleşme (0.01 < LR < 10.000)"
    else:
        v_en = "Definitive Exclusion from Missing Person Pedigree (LR <= 0.01)"
        v_tr = "Kayıp Şahıs Soyağacından Kesin Olarak Dışlanma (LR <= 0.01)"

    shield = (
        "IMPORTANT (Interpol DVI Multi-Omic Legal Shield): Standalone judicial identification "
        "requires LR_Joint >= 10^6 (log10 >= 6.0, W >= 0.999999). Lower LRs (10^4 <= LR < 10^6) mandate secondary "
        "corroboration by forensic odontology, surgical serial numbers, or physical marks."
    )

    return DviJointLRResponse(
        joint_lr=round(joint_lr, 4),
        log10_joint_lr=round(log10_joint, 4),
        decision_tier=tier.value,
        components=comp,
        posterior_probability_w=round(w, 8),
        prior_probability=body.prior_probability,
        judicial_action=action,
        is_definitive_identification=(tier == InterpolDecisionTier.DEFINITIVE_IDENTIFICATION),
        verbal_predicate_en=v_en,
        verbal_predicate_tr=v_tr,
        prosecutors_fallacy_shield=shield,
    )


# ── 2. N x M Cross-Reconciliation Matrix ─────────────────────────────────────

@router.post(
    "/reconcile-matrix",
    response_model=DviReconciliationMatrixResponse,
    summary="N x M Disaster Victim vs Missing Person Cross-Reconciliation Matrix",
    description="Cross-evaluates all PM remains against AM family reference pedigrees and solves Hungarian 1-to-1 matching.",
    status_code=status.HTTP_200_OK,
)
async def reconcile_matrix(body: DviReconciliationMatrixRequest) -> DviReconciliationMatrixResponse:
    try:
        results: List[DviPairwiseResultSchema] = []
        n_def = 0
        n_prob = 0
        n_inconc = 0
        n_excl = 0

        cost_matrix: List[List[float]] = []
        pm_ids: List[str] = [pm.pm_id for pm in body.pm_remains]
        am_ids: List[str] = [am.am_id for am in body.am_families]

        for pm in body.pm_remains:
            row_costs: List[float] = []
            for am in body.am_families:
                auto_lr = pm.autosomal_lr_map.get(am.am_id, pm.default_autosomal_lr)
                snp_lr = pm.snp_lr_map.get(am.am_id, 1.0)
                joint_lr, log10_joint = DviMathematicalFormulation.compute_multi_omic_joint_lr(
                    autosomal_lr=auto_lr,
                    ystr_p_upper=pm.ystr_p_upper or 1.0,
                    mtdna_p_upper=pm.mtdna_p_upper or 1.0,
                    snp_lr=snp_lr,
                    has_ystr=am.has_male_reference and (pm.ystr_p_upper is not None),
                    has_mtdna=am.has_maternal_reference and (pm.mtdna_p_upper is not None),
                    has_snp=am.has_snp_data,
                )
                tier, action = DviMathematicalFormulation.classify_interpol_tier(joint_lr)

                if tier == InterpolDecisionTier.DEFINITIVE_IDENTIFICATION:
                    n_def += 1
                elif tier == InterpolDecisionTier.PROBABLE_MATCH:
                    n_prob += 1
                elif tier == InterpolDecisionTier.INCONCLUSIVE:
                    n_inconc += 1
                else:
                    n_excl += 1

                ystr_lr = (1.0 / pm.ystr_p_upper) if (pm.ystr_p_upper and pm.ystr_p_upper > 0 and am.has_male_reference) else 1.0
                mtdna_lr = (1.0 / pm.mtdna_p_upper) if (pm.mtdna_p_upper and pm.mtdna_p_upper > 0 and am.has_maternal_reference) else 1.0

                comp = DviMultiOmicComponentsSchema(
                    autosomal_str_lr=auto_lr,
                    ystr_lr=ystr_lr,
                    ystr_p_upper=pm.ystr_p_upper,
                    has_ystr=am.has_male_reference and (pm.ystr_p_upper is not None),
                    mtdna_lr=mtdna_lr,
                    mtdna_p_upper=pm.mtdna_p_upper,
                    has_mtdna=am.has_maternal_reference and (pm.mtdna_p_upper is not None),
                    snp_lr=snp_lr,
                    has_snp=am.has_snp_data,
                )

                results.append(
                    DviPairwiseResultSchema(
                        pm_profile_id=pm.pm_id,
                        am_family_id=am.am_id,
                        joint_lr=round(joint_lr, 4),
                        log10_joint_lr=round(log10_joint, 4),
                        decision_tier=tier.value,
                        components=comp,
                        judicial_action=action,
                        is_positive_identification=(tier == InterpolDecisionTier.DEFINITIVE_IDENTIFICATION),
                    )
                )
                row_costs.append(joint_lr)
            cost_matrix.append(row_costs)

        assignments_raw = DviMathematicalFormulation.solve_bipartite_assignment(cost_matrix, pm_ids, am_ids)
        optimal_assignments = [
            DviOptimalAssignmentSchema(
                pm_id=p,
                am_id=a,
                joint_lr=round(score, 4),
                log10_joint_lr=round(math.log10(score) if score > 0 else -300.0, 4),
                decision_tier=DviMathematicalFormulation.classify_interpol_tier(score)[0].value,
            )
            for p, a, score in assignments_raw
        ]

        summary = (
            f"Interpol DVI Reconciliation Matrix: {len(body.pm_remains)} PM remains evaluated against "
            f"{len(body.am_families)} AM families ({len(results)} total pairwise comparisons). "
            f"Definitive Identifications: {n_def}, Probable Matches: {n_prob}, Inconclusive: {n_inconc}, Exclusions: {n_excl}."
        )

        shield = (
            "IMPORTANT (Interpol DVI Multi-Omic Legal Shield): Standalone judicial identification "
            "requires LR_Joint >= 10^6 (log10 >= 6.0). Lower LRs (10^4 <= LR < 10^6) mandate secondary "
            "corroboration by forensic odontology, surgical serial numbers, or physical marks."
        )

        return DviReconciliationMatrixResponse(
            disaster_event_id=body.disaster_event_id,
            total_pm_remains=len(body.pm_remains),
            total_am_families=len(body.am_families),
            definitive_identifications_count=n_def,
            probable_matches_count=n_prob,
            inconclusive_count=n_inconc,
            exclusions_count=n_excl,
            reconciliation_matrix=results,
            optimal_assignments=optimal_assignments,
            interpol_summary=summary,
            prosecutors_fallacy_shield=shield,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"DVI Matrix Reconciliation failed: {str(exc)}",
        )


# ── 3. Decision Tiers & Metadata ─────────────────────────────────────────────

@router.get(
    "/decision-tiers",
    response_model=InterpolTiersResponse,
    summary="Interpol DVI 4-Tier Decision Rules & Judicial Criteria",
    status_code=status.HTTP_200_OK,
)
async def get_decision_tiers() -> InterpolTiersResponse:
    tiers = [
        InterpolDecisionTierMetadataSchema(
            tier=m.tier.value,
            tier_name=m.tier.value,
            min_lr=m.min_lr,
            max_lr=m.max_lr if not math.isinf(m.max_lr) else 1.0e18,
            min_log10=m.min_log10 if not math.isinf(m.min_log10) else -300.0,
            max_log10=m.max_log10 if not math.isinf(m.max_log10) else 300.0,
            judicial_action_criterion=m.judicial_action_criterion,
            requires_secondary_corroboration=m.requires_secondary_corroboration,
            is_court_admissible_standalone=m.is_court_admissible_standalone,
        )
        for m in INTERPOL_TIER_RULES.values()
    ]
    return InterpolTiersResponse(
        standard="Interpol Disaster Victim Identification Guide Section 4",
        version="2018 / 2023 Standing Committee Edition",
        tiers=tiers,
    )


@router.get(
    "/pedigree-templates",
    response_model=List[DviPedigreeTemplateSchema],
    summary="List 4 Standard Interpol Pedigree Templates",
    status_code=status.HTTP_200_OK,
)
async def list_pedigree_templates() -> List[DviPedigreeTemplateSchema]:
    return [
        DviPedigreeTemplateSchema(
            template_id=t.template_id.value,
            name=t.name,
            description=t.description,
            required_am_members=t.required_am_members,
            expected_min_autosomal_lr=t.expected_min_autosomal_lr,
        )
        for t in DviReferenceDatasets.list_pedigree_templates()
    ]


@router.get(
    "/casework-cohorts",
    response_model=List[DviCaseworkCohortSchema],
    summary="List Certified Casework Benchmark Cohorts",
    status_code=status.HTTP_200_OK,
)
async def list_casework_cohorts() -> List[DviCaseworkCohortSchema]:
    return [
        DviCaseworkCohortSchema(
            cohort_id=c.cohort_id,
            name=c.name,
            pedigree_type=c.pedigree_type.value,
            description=c.description,
            autosomal_lr=c.autosomal_lr,
            ystr_p_upper=c.ystr_p_upper,
            mtdna_p_upper=c.mtdna_p_upper,
            snp_lr=c.snp_lr,
            has_ystr=c.has_ystr,
            has_mtdna=c.has_mtdna,
            has_snp=c.has_snp,
            expected_joint_lr=c.expected_joint_lr,
            expected_log10_lr=c.expected_log10_lr,
            expected_tier=c.expected_tier,
            prior_probability=c.prior_probability,
            expected_min_w=c.expected_min_w,
        )
        for c in DviReferenceDatasets.list_casework_cohorts()
    ]


@router.get(
    "/reporting-disclaimer",
    summary="Interpol & ENFSI Evaluative Reporting Legal Disclaimer",
    status_code=status.HTTP_200_OK,
)
async def get_reporting_disclaimer() -> Dict[str, Any]:
    return DviCrossValidationEngine.get_interpol_dvi_reporting_shield()


# ── 4. Missing Person Search & Batch Reconciliation Endpoints ────────────────

@router.post(
    "/missing-person/search",
    summary="Missing Persons Candidate Search",
    status_code=status.HTTP_200_OK,
)
async def search_missing_person_endpoint(body: Dict[str, Any]) -> Dict[str, Any]:
    try:
        query_dict = body.get("query_profile", {})
        cand_dicts = body.get("candidate_db", [])
        prior = float(body.get("prior_probability", 0.50))
        top_k = int(body.get("top_k", 5))

        query_prof = _parse_str_profile_dict(query_dict)
        candidate_profs = [_parse_str_profile_dict(cd) for cd in cand_dicts]

        res = _legacy_missing_engine.search_and_rank_candidates(
            query_profile=query_prof,
            candidate_db=candidate_profs,
            prior_probability=prior,
            top_k=top_k,
        )

        hits = [
            {
                "candidate_id": h.candidate_id,
                "relationship_type": h.relationship_type,
                "combined_lr": h.combined_lr,
                "log10_lr": h.log10_lr,
                "posterior_probability": h.posterior_probability,
                "matching_loci_count": h.matching_loci_count,
                "evaluated_loci_count": h.evaluated_loci_count,
                "confidence_tier": h.confidence_tier,
            }
            for h in res.top_candidate_hits
        ]

        return {
            "query_id": res.query_id,
            "total_candidates_searched": res.total_candidates_searched,
            "top_candidate_hits": hits,
            "search_summary": res.search_summary,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Missing person search failed: {str(exc)}",
        )


@router.post(
    "/reconcile",
    summary="Direct AM/PM Profile Batch Reconciliation",
    status_code=status.HTTP_200_OK,
)
async def reconcile_profiles_endpoint(body: Dict[str, Any]) -> Dict[str, Any]:
    try:
        disaster_id = body.get("disaster_event_id", body.get("disaster_id", "DVI-EVENT"))
        am_dicts = body.get("am_profiles", [])
        pm_dicts = body.get("pm_profiles", [])

        am_profs = [_parse_str_profile_dict(ad) for ad in am_dicts]
        pm_profs = [_parse_str_profile_dict(pd) for pd in pm_dicts]

        report = _legacy_reconcile_engine.reconcile_am_pm_profiles(
            disaster_event_id=disaster_id,
            am_profiles=am_profs,
            pm_profiles=pm_profs,
        )

        matrix = [
            {
                "am_profile_id": c.am_profile_id,
                "pm_profile_id": c.pm_profile_id,
                "relationship_hypothesis": c.relationship_hypothesis,
                "lr": c.lr,
                "log10_lr": c.log10_lr,
                "identification_status": c.identification_status,
            }
            for c in report.reconciliation_matrix
        ]

        return {
            "disaster_event_id": report.disaster_event_id,
            "total_am_profiles": report.total_am_profiles,
            "total_pm_profiles": report.total_pm_profiles,
            "confirmed_identifications_count": report.confirmed_identifications_count,
            "reconciliation_matrix": matrix,
            "dvi_summary": report.dvi_summary,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"DVI Reconciliation failed: {str(exc)}",
        )
