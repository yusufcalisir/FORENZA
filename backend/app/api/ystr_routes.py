"""
FORENZA Y-STR Haplotype Forensics API Router (Module 06).

Exposes endpoints for 27-locus Y-FILER Plus lineage forensics (Pillar 2 §1):
  POST /forensic/lineage/ystr/evaluate-match        — 27-Locus Paternal Match Evaluation
  POST /forensic/lineage/ystr/clopper-pearson-bound — Exact Binomial CI Upper Bound
  POST /forensic/lineage/ystr/brenner-frequency     — Brenner theta subpopulation correction
  POST /forensic/lineage/ystr/discrete-laplace      — Discrete Laplace clonal clustering model
  POST /forensic/lineage/ystr/mixture-contributors  — Minimum Male Contributor Count (N_male)
  POST /forensic/lineage/ystr/smm-transition        — Stepwise Mutation Model (SMM)
  GET  /forensic/lineage/ystr/panel-metadata        — Y-FILER Plus 27-Locus Panel Details
"""

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.dna.ystr_engine import (
    YSTREngine,
    LaplaceCluster,
    Y_FILER_PLUS_27_LOCI,
)
from .ystr_schemas import (
    YSTRMatchRequest, YSTRMatchResponse,
    ClopperPearsonRequest, ClopperPearsonSchema,
    BrennerFrequencyRequest, BrennerSchema,
    DiscreteLaplaceRequest, DiscreteLaplaceResponse,
    YSTRMixtureDeconvRequest, YSTRMixtureDeconvResponse,
    SMMTransitionRequest, SMMTransitionSchema,
    YSTRPanelMetadataResponse, YSTRLocusMetadataSchema,
)

router = APIRouter(
    prefix="/forensic/lineage/ystr",
    tags=["Y-STR Haplotype Forensics & Lineage Genetics (Module 06)"],
)

_ystr_engine = YSTREngine()


# ── §1.1 / §1.2 Full Match Evaluation ────────────────────────────────────────

@router.post(
    "/evaluate-match",
    response_model=YSTRMatchResponse,
    summary="27-Locus Y-FILER Plus Paternal Match Evaluation",
    description=(
        "Evaluates 27-locus Y-STR haplotype matching, Clopper-Pearson 95% upper bound, "
        "Brenner subpopulation correction, and SMM single-locus germline mutations. (Research §1.1, §1.2)"
    ),
    status_code=status.HTTP_200_OK,
)
async def evaluate_ystr_match(body: YSTRMatchRequest) -> YSTRMatchResponse:
    try:
        res = _ystr_engine.evaluate_ystr_paternal_match(
            evidence_markers=body.evidence_markers,
            suspect_markers=body.suspect_markers,
            evidence_id=body.evidence_id,
            suspect_id=body.suspect_id,
            database_count_k=body.database_count_k,
            database_size_n=body.database_size_n,
            theta=body.theta,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Y-STR match evaluation failed: {str(exc)}",
        )

    return YSTRMatchResponse(
        evidence_id=res.evidence_id,
        suspect_id=res.suspect_id,
        matching_loci_count=res.matching_loci_count,
        total_evaluated_loci=res.total_evaluated_loci,
        mismatch_loci_count=res.mismatch_loci_count,
        match_status=res.match_status,
        database_count_k=res.database_count_k,
        database_size_n=res.database_size_n,
        theta=res.theta,
        clopper_pearson=ClopperPearsonSchema(
            observed_count_k=res.clopper_pearson.observed_count_k,
            database_size_n=res.clopper_pearson.database_size_n,
            alpha=res.clopper_pearson.alpha,
            p_upper=res.clopper_pearson.p_upper,
            p_lower=res.clopper_pearson.p_lower,
            point_estimate=res.clopper_pearson.point_estimate,
            lr_upper_bound=res.clopper_pearson.lr_upper_bound,
            log10_lr_upper_bound=res.clopper_pearson.log10_lr_upper_bound,
            method_formula=res.clopper_pearson.method_formula,
        ),
        brenner=BrennerSchema(
            observed_count_k=res.brenner.observed_count_k,
            database_size_n=res.brenner.database_size_n,
            theta=res.brenner.theta,
            p_brenner=res.brenner.p_brenner,
            lr_brenner=res.brenner.lr_brenner,
            log10_lr_brenner=res.brenner.log10_lr_brenner,
        ),
        smm_mutations=[
            SMMTransitionSchema(
                locus_name=s.locus_name,
                father_allele=s.father_allele,
                son_allele=s.son_allele,
                step_distance_m=s.step_distance_m,
                is_mutation=s.is_mutation,
                mutation_rate=s.mutation_rate,
                transition_probability=s.transition_probability,
                log10_transition_probability=s.log10_transition_probability,
                mutation_classification=s.mutation_classification,
            )
            for s in res.smm_mutations
        ],
        paternal_lineage_verdict=res.paternal_lineage_verdict,
        prosecutors_fallacy_shield=res.prosecutors_fallacy_shield,
    )


# ── §1.1 Clopper-Pearson Exact Bound ──────────────────────────────────────────

@router.post(
    "/clopper-pearson-bound",
    response_model=ClopperPearsonSchema,
    summary="Clopper-Pearson 95% Exact Binomial Confidence Interval",
    description=(
        "Computes exact upper bound frequency p_upper: "
        "k=0: 1 - 0.05^(1/(N+1)); k>0: exact Snedecor F / Beta quantile. (Research §1.1)"
    ),
    status_code=status.HTTP_200_OK,
)
async def compute_clopper_pearson(body: ClopperPearsonRequest) -> ClopperPearsonSchema:
    try:
        res = _ystr_engine.compute_clopper_pearson_bound(
            k=body.observed_count_k,
            n=body.database_size_n,
            alpha=body.alpha,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Clopper-Pearson calculation failed: {str(exc)}",
        )
    return ClopperPearsonSchema(
        observed_count_k=res.observed_count_k,
        database_size_n=res.database_size_n,
        alpha=res.alpha,
        p_upper=res.p_upper,
        p_lower=res.p_lower,
        point_estimate=res.point_estimate,
        lr_upper_bound=res.lr_upper_bound,
        log10_lr_upper_bound=res.log10_lr_upper_bound,
        method_formula=res.method_formula,
    )


# ── §1.1 Brenner Subpopulation Correction ─────────────────────────────────────

@router.post(
    "/brenner-frequency",
    response_model=BrennerSchema,
    summary="Brenner / Surveyor Subpopulation Correction",
    description="Computes p_Brenner = (k + theta) / (N + theta). (Brenner 2010; Research §1.1)",
    status_code=status.HTTP_200_OK,
)
async def compute_brenner_frequency(body: BrennerFrequencyRequest) -> BrennerSchema:
    try:
        res = _ystr_engine.compute_brenner_frequency(
            k=body.observed_count_k,
            n=body.database_size_n,
            theta=body.theta,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Brenner frequency calculation failed: {str(exc)}",
        )
    return BrennerSchema(
        observed_count_k=res.observed_count_k,
        database_size_n=res.database_size_n,
        theta=res.theta,
        p_brenner=res.p_brenner,
        lr_brenner=res.lr_brenner,
        log10_lr_brenner=res.log10_lr_brenner,
    )


# ── §1.1 Discrete Laplace Model ───────────────────────────────────────────────

@router.post(
    "/discrete-laplace",
    response_model=DiscreteLaplaceResponse,
    summary="Discrete Laplace Clonal Clustering Frequency Smoothing",
    description=(
        "Smoothes haplotype frequency across C clonal clusters using the Discrete Laplace model: "
        "P(H) = SUM_c w_c PROD_l f_l(y_l | mu_cl, lambda_cl). (Andersen et al. 2013; Research §1.1)"
    ),
    status_code=status.HTTP_200_OK,
)
async def compute_discrete_laplace(body: DiscreteLaplaceRequest) -> DiscreteLaplaceResponse:
    try:
        clusters = [
            LaplaceCluster(
                weight=c.weight,
                center_haplotype=c.center_haplotype,
                scale_parameters=c.scale_parameters,
            )
            for c in body.clusters
        ]
        res = _ystr_engine.compute_discrete_laplace_probability(
            haplotype=body.haplotype,
            clusters=clusters,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Discrete Laplace calculation failed: {str(exc)}",
        )
    return DiscreteLaplaceResponse(
        haplotype=res.haplotype,
        num_clusters=res.num_clusters,
        haplotype_probability=res.haplotype_probability,
        log10_probability=res.log10_probability,
        lr=res.lr,
        log10_lr=res.log10_lr,
    )


# ── §1.3 Mixture Contributor Deconvolution ───────────────────────────────────

@router.post(
    "/mixture-contributors",
    response_model=YSTRMixtureDeconvResponse,
    summary="Minimum Male Contributor Estimation (N_male)",
    description=(
        "Infers N_male = max_l ceil(n_alleles / 2) with multi-copy locus rules "
        "(DYS385a/b, DYF387S1a/b > 4 alleles => >= 3 males). (Research §1.3)"
    ),
    status_code=status.HTTP_200_OK,
)
async def estimate_mixture_contributors(body: YSTRMixtureDeconvRequest) -> YSTRMixtureDeconvResponse:
    try:
        res = _ystr_engine.estimate_minimum_male_contributors(locus_alleles=body.locus_alleles)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Mixture contributor estimation failed: {str(exc)}",
        )
    return YSTRMixtureDeconvResponse(
        minimum_male_contributors=res.minimum_male_contributors,
        locus_with_max_alleles=res.locus_with_max_alleles,
        max_allele_count=res.max_allele_count,
        multi_copy_locus_flag=res.multi_copy_locus_flag,
        locus_allele_counts=res.locus_allele_counts,
        interpretation=res.interpretation,
    )


# ── §1.3 Stepwise Mutation Model (SMM) ───────────────────────────────────────

@router.post(
    "/smm-transition",
    response_model=SMMTransitionSchema,
    summary="Stepwise Mutation Model (SMM) Father-Son Transition",
    description=(
        "Computes germline transmission probability: "
        "P(a_s | a_f, mu_l) = (mu_l / 2) * p^(m-1) * (1-p) for m >= 1 step difference. (Research §1.3)"
    ),
    status_code=status.HTTP_200_OK,
)
async def compute_smm_transition(body: SMMTransitionRequest) -> SMMTransitionSchema:
    try:
        res = _ystr_engine.compute_smm_paternity_transition(
            father_allele=body.father_allele,
            son_allele=body.son_allele,
            locus_name=body.locus_name,
            p_step=body.p_step,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"SMM transition calculation failed: {str(exc)}",
        )
    return SMMTransitionSchema(
        locus_name=res.locus_name,
        father_allele=res.father_allele,
        son_allele=res.son_allele,
        step_distance_m=res.step_distance_m,
        is_mutation=res.is_mutation,
        mutation_rate=res.mutation_rate,
        transition_probability=res.transition_probability,
        log10_transition_probability=res.log10_transition_probability,
        mutation_classification=res.mutation_classification,
    )


# ── §1.2 Panel Metadata ───────────────────────────────────────────────────────

@router.get(
    "/panel-metadata",
    response_model=YSTRPanelMetadataResponse,
    summary="Y-FILER Plus 27-Locus Panel Metadata",
    description="Returns all 27 loci, mutation rates, sequence types, repeat motifs, and RM classifications.",
    status_code=status.HTTP_200_OK,
)
async def get_panel_metadata() -> YSTRPanelMetadataResponse:
    loci_list = [
        YSTRLocusMetadataSchema(
            locus_name=meta.locus_name,
            sequence_type=meta.sequence_type,
            mutation_class=meta.mutation_class,
            mutation_rate=meta.mutation_rate,
            repeat_motif=meta.repeat_motif,
            is_multicopy=meta.is_multicopy,
            is_rapidly_mutating=meta.is_rapidly_mutating,
        )
        for meta in Y_FILER_PLUS_27_LOCI.values()
    ]
    rm_count = sum(1 for l in loci_list if l.is_rapidly_mutating)
    std_count = len(loci_list) - rm_count
    return YSTRPanelMetadataResponse(
        panel_name="Y-FILER Plus 27-Locus Multiplex",
        total_loci=len(loci_list),
        standard_loci_count=std_count,
        rapidly_mutating_loci_count=rm_count,
        loci=loci_list,
    )
