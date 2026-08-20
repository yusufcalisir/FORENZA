"""
FORENZA Y-STR Haplotype Forensics API Router (Module 2.1).
Standards Compliance: ISO/IEC 17025:2017, SWGDAM Lineage Guidelines (2020), ENFSI Evaluative Reporting (2017).
Research Source: research/pillar_2_lineage_kinship_research.md & research/ystr_27_mtdna_empop_lineage_research.md

Endpoints:
  POST /forensic/lineage/ystr/evaluate-paternal-kinship — Full 27-Locus Paternal Lineage Kinship Evaluation
  POST /forensic/lineage/ystr/clopper-pearson-bound     — Exact Binomial CI Upper Bound
  POST /forensic/lineage/ystr/brenner-frequency         — Brenner theta subpopulation correction
  POST /forensic/lineage/ystr/predict-haplogroup        — Bayesian Y-DNA Haplogroup Prediction
  POST /forensic/lineage/ystr/decouple-dys389           — DYS389I / DYS389II nested repeat decoupling
  POST /forensic/lineage/ystr/mixture-contributors      — Minimum Male Contributor Count (N_male)
  GET  /forensic/lineage/ystr/panel-metadata            — Y-FILER Plus 27-Locus Panel Details
  GET  /forensic/lineage/ystr/metapopulations           — YHRD Release 68 Database Partitions
  GET  /forensic/lineage/ystr/gold-standards            — Certified Multi-Omic Gold Standards
  GET  /forensic/lineage/ystr/casework-cohorts          — Certified Casework Benchmark Cohorts
  GET  /forensic/lineage/ystr/patrilineal-disclaimer    — ISFG (2020) Patrilineal Evaluative Disclaimer
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status

from node.services.forensic.ystr.ystr_mathematical_formulation import (
    YSTR_27_MASTER_REGISTRY,
    YStrMathematicalFormulation,
)
from node.services.forensic.ystr.ystr_reference_datasets import (
    YhrdMetapopulation,
    YStrReferenceDatasets,
)
from node.services.forensic.ystr.ystr_cross_validation import (
    YStrCrossValidationEngine,
)
from .ystr_schemas import (
    PaternalKinshipRequest,
    PaternalKinshipResponse,
    LocusKinshipDetailSchema,
    ClopperPearsonRequest,
    ClopperPearsonResponse,
    BrennerFrequencyRequest,
    BrennerFrequencyResponse,
    HaplogroupPredictionRequest,
    HaplogroupPredictionResponse,
    DecoupleDys389Request,
    DecoupleDys389Response,
    MixtureContributorsRequest,
    MixtureContributorsResponse,
    YStrLocusMetadataSchema,
    YhrdMetapopulationSchema,
    GoldStandardIndividualSchema,
    CaseworkCohortSchema,
)

router = APIRouter(
    prefix="/forensic/lineage/ystr",
    tags=["Y-STR 27-Locus Lineage Forensics & Haplotype Genetics (Module 2.1)"],
)


# ── 1. Paternal Kinship Evaluation ───────────────────────────────────────────

@router.post(
    "/evaluate-paternal-kinship",
    response_model=PaternalKinshipResponse,
    summary="27-Locus Y-FILER Plus Paternal Kinship Evaluation",
    description="Evaluates full 27-locus paternal lineage kinship likelihood ratio, SMM mutations, and RM loci differentiation.",
    status_code=status.HTTP_200_OK,
)
async def evaluate_paternal_kinship(body: PaternalKinshipRequest) -> PaternalKinshipResponse:
    try:
        res = YStrMathematicalFormulation.evaluate_paternal_kinship_likelihood(
            profile_a=body.evidence_markers,
            profile_b=body.suspect_markers,
            meioses_m=body.meioses_m,
            database_size_n=body.database_size_n,
            theta=body.theta,
        )
        shield = YStrCrossValidationEngine.get_isfg_patrilineal_disclaimer()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Y-STR paternal kinship evaluation error: {str(exc)}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal computational error during kinship evaluation: {str(exc)}",
        )

    locus_dict: Dict[str, LocusKinshipDetailSchema] = {
        loc: LocusKinshipDetailSchema(
            allele_a=det["allele_a"],
            allele_b=det["allele_b"],
            is_match=det["is_match"],
            transition_probability=det["transition_probability"],
            is_rm=det["is_rm"],
            mutation_rate=det["mutation_rate"],
        )
        for loc, det in res.locus_evaluations.items()
    }

    return PaternalKinshipResponse(
        evidence_id=body.evidence_id,
        suspect_id=body.suspect_id,
        meioses_m=res.meioses_m,
        total_loci_evaluated=res.total_loci_evaluated,
        matching_loci_count=res.matching_loci_count,
        mutated_loci_count=res.mutated_loci_count,
        rm_mutations_count=res.rm_mutations_count,
        standard_mutations_count=res.standard_mutations_count,
        transition_probability_product=res.transition_probability_product,
        haplotype_p_upper=res.haplotype_p_upper,
        paternal_lr=res.paternal_lr,
        log10_paternal_lr=res.log10_paternal_lr,
        is_lineage_excluded=res.is_lineage_excluded,
        locus_evaluations=locus_dict,
        verbal_predicate_en=res.verbal_predicate_en,
        verbal_predicate_tr=res.verbal_predicate_tr,
        patrilineal_disclaimer_en=shield.disclaimer_text_en,
        patrilineal_disclaimer_tr=shield.disclaimer_text_tr,
    )


# ── 2. Population Frequency & Confidence Bounds ─────────────────────────────

@router.post(
    "/clopper-pearson-bound",
    response_model=ClopperPearsonResponse,
    summary="Exact Clopper-Pearson 95% Binomial Upper Bound",
    description="Calculates exact upper confidence limit for observed or unobserved Y-STR haplotypes using Snedecor F-distribution.",
    status_code=status.HTTP_200_OK,
)
async def get_clopper_pearson_bound(body: ClopperPearsonRequest) -> ClopperPearsonResponse:
    try:
        res = YStrMathematicalFormulation.compute_clopper_pearson_upper_bound(
            k=body.observed_count_k,
            n=body.database_size_n,
            alpha=body.alpha,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Clopper-Pearson parameter validation error: {str(exc)}",
        )

    return ClopperPearsonResponse(
        database_size_n=res.database_size_n,
        observed_matches_k=res.observed_matches_k,
        alpha=res.alpha,
        point_estimate=res.point_estimate,
        p_upper_bound=res.p_upper_bound,
        equivalent_match_ratio=res.equivalent_match_ratio,
        method=res.method,
    )


@router.post(
    "/brenner-frequency",
    response_model=BrennerFrequencyResponse,
    summary="Brenner / Surveyor Subpopulation Coancestry Correction",
    description="Computes theta-adjusted match probability p_Brenner = (k + theta) / (N + theta).",
    status_code=status.HTTP_200_OK,
)
async def get_brenner_frequency(body: BrennerFrequencyRequest) -> BrennerFrequencyResponse:
    try:
        p_b = YStrMathematicalFormulation.compute_brenner_frequency(
            k=body.observed_count_k,
            n=body.database_size_n,
            theta=body.theta,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Brenner parameter validation error: {str(exc)}",
        )

    return BrennerFrequencyResponse(
        observed_count_k=body.observed_count_k,
        database_size_n=body.database_size_n,
        theta=body.theta,
        p_brenner=p_b,
        equivalent_match_ratio=1.0 / p_b if p_b > 0 else float("inf"),
    )


# ── 3. Haplogroup Prediction ────────────────────────────────────────────────

@router.post(
    "/predict-haplogroup",
    response_model=HaplogroupPredictionResponse,
    summary="Bayesian Y-DNA Haplogroup Prediction",
    description="Predicts major Y-DNA haplogroup from 27-locus Y-STR vector across 16 major modal clades.",
    status_code=status.HTTP_200_OK,
)
async def predict_y_haplogroup(body: HaplogroupPredictionRequest) -> HaplogroupPredictionResponse:
    try:
        res = YStrMathematicalFormulation.predict_haplogroup(profile=body.y_str_markers)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Haplogroup prediction failed: {str(exc)}",
        )

    return HaplogroupPredictionResponse(
        predicted_haplogroup=res.predicted_haplogroup,
        confidence_score=res.confidence_score,
        primary_snp_marker=res.primary_snp_marker,
        distance_to_modal=res.distance_to_modal,
        description=res.description,
        bayesian_posteriors=res.bayesian_posteriors,
    )


# ── 4. Decoupling & Mixture Contributors ────────────────────────────────────

@router.post(
    "/decouple-dys389",
    response_model=DecoupleDys389Response,
    summary="Decouple Nested Repeat System DYS389I / DYS389II",
    description="Calculates pure variable repeat component: DYS389.2_pure = DYS389II_total - DYS389I.",
    status_code=status.HTTP_200_OK,
)
async def decouple_dys389_endpoint(body: DecoupleDys389Request) -> DecoupleDys389Response:
    try:
        pure = YStrMathematicalFormulation.decouple_dys389(body.dys389i, body.dys389ii_total)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"DYS389 decoupling error: {str(exc)}",
        )

    return DecoupleDys389Response(
        dys389i=body.dys389i,
        dys389ii_total=body.dys389ii_total,
        dys389_2_pure=pure,
        explanation=f"DYS389II total ({body.dys389ii_total}) decoupled by subtracting nested DYS389I ({body.dys389i}) yields variable repeat component {pure}.",
    )


@router.post(
    "/mixture-contributors",
    response_model=MixtureContributorsResponse,
    summary="Minimum Male Contributor Estimation (N_male)",
    description="Infers minimum male contributors from maximum observed alleles per locus.",
    status_code=status.HTTP_200_OK,
)
async def get_mixture_contributors(body: MixtureContributorsRequest) -> MixtureContributorsResponse:
    try:
        n_male = YStrMathematicalFormulation.estimate_minimum_male_contributors(body.locus_allele_counts)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Mixture contributor estimation error: {str(exc)}",
        )

    return MixtureContributorsResponse(
        minimum_male_contributors=n_male,
        locus_allele_counts=body.locus_allele_counts,
        methodology="N_male = max_l ceil(n_alleles / 2) with multi-copy locus discrimination",
    )


# ── 5. Catalogs, Metapopulations & Casework Cohorts ──────────────────────────

@router.get(
    "/panel-metadata",
    response_model=List[YStrLocusMetadataSchema],
    summary="Y-FILER Plus 27-Locus Panel Master Registry",
    status_code=status.HTTP_200_OK,
)
async def get_panel_metadata() -> List[YStrLocusMetadataSchema]:
    return [
        YStrLocusMetadataSchema(
            locus_name=m.locus_name,
            cytogenetic_band=m.cytogenetic_band,
            grch38_start=m.grch38_start,
            grch38_end=m.grch38_end,
            repeat_unit_bp=m.repeat_unit_bp,
            canonical_motif=m.canonical_motif,
            ce_dye=m.ce_dye.value,
            amplicon_min_bp=m.amplicon_min_bp,
            amplicon_max_bp=m.amplicon_max_bp,
            mutation_rate=m.mutation_rate,
            stepwise_param_r=m.stepwise_param_r,
            mutation_class=m.mutation_class.value,
            is_rapidly_mutating=m.is_rapidly_mutating,
            is_multi_copy=m.is_multi_copy,
        )
        for m in YSTR_27_MASTER_REGISTRY.values()
    ]


@router.get(
    "/metapopulations",
    response_model=List[YhrdMetapopulationSchema],
    summary="YHRD Release 68 Global Population Partitions",
    status_code=status.HTTP_200_OK,
)
async def list_metapopulations() -> List[YhrdMetapopulationSchema]:
    return [
        YhrdMetapopulationSchema(
            code=p.code.value,
            name=p.name,
            database_size_n=p.database_size_n,
            default_theta=p.default_theta,
            description=p.description,
            primary_modal_haplogroups=list(p.primary_modal_haplogroups),
        )
        for p in YStrReferenceDatasets.list_population_partitions()
    ]


@router.get(
    "/gold-standards",
    response_model=List[GoldStandardIndividualSchema],
    summary="Certified Multi-Omic Gold Standard Reference Individuals",
    status_code=status.HTTP_200_OK,
)
async def list_gold_standards() -> List[GoldStandardIndividualSchema]:
    return [
        GoldStandardIndividualSchema(
            sample_id=g.sample_id,
            coriell_id=g.coriell_id,
            nist_srm_designation=g.nist_srm_designation,
            sex=g.sex,
            population_group=g.population_group,
            certified_haplogroup=g.certified_haplogroup,
            primary_snp=g.primary_snp,
            description=g.description,
            y_str_haplotype=g.y_str_haplotype,
        )
        for g in YStrReferenceDatasets.list_gold_standards()
    ]


@router.get(
    "/casework-cohorts",
    response_model=List[CaseworkCohortSchema],
    summary="Certified Casework Benchmark Cohorts",
    status_code=status.HTTP_200_OK,
)
async def list_casework_cohorts() -> List[CaseworkCohortSchema]:
    return [
        CaseworkCohortSchema(
            cohort_id=c.cohort_id,
            name=c.name,
            description=c.description,
            meioses_m=c.meioses_m,
            expected_outcome=c.expected_outcome,
            expected_matching_loci=c.expected_matching_loci,
            expected_mutation_count=c.expected_mutation_count,
            expected_min_lr=c.expected_min_lr,
            profile_a=c.profile_a,
            profile_b=c.profile_b,
        )
        for c in YStrReferenceDatasets.list_casework_cohorts()
    ]


@router.get(
    "/patrilineal-disclaimer",
    summary="ISFG (2020) Patrilineal Lineage Reporting Disclaimer",
    status_code=status.HTTP_200_OK,
)
async def get_patrilineal_disclaimer() -> Dict[str, Any]:
    shield = YStrCrossValidationEngine.get_isfg_patrilineal_disclaimer()
    return {
        "has_patrilineal_disclaimer": shield.has_patrilineal_disclaimer,
        "prosecutors_fallacy_shield_active": shield.prosecutors_fallacy_shield_active,
        "disclaimer_text_en": shield.disclaimer_text_en,
        "disclaimer_text_tr": shield.disclaimer_text_tr,
    }
