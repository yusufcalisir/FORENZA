"""
FORENZA Population Genetics API Router.
Exposes endpoints for NRC II frequency bounding, Wright's FST distance calculation,
Dirichlet Bayesian smoothing, HWE exact testing, theta-corrected LR, and
full FST population matrix under the /population prefix.
"""

import math
from fastapi import APIRouter, HTTPException, status

from node.services.forensic.frequency_db import FrequencyDatabase
from node.services.forensic.population.substructure import SubstructureEngine
from node.services.forensic.population.rare_allele import RareAlleleEngine
from node.services.forensic.population.dirichlet_smoothing import DirichletSmoothingEngine
from node.services.forensic.population.hwe_engine import HWEEngine
from .population_schemas import (
    FrequencyBoundRequest, FrequencyBoundResponse,
    FstDistanceRequest, FstDistanceResponse,
    PopulationListResponse,
    DirichletSmoothRequest, DirichletSmoothResponse, DirichletAlleleResult,
    HWETestRequest, HWETestResponse,
    ThetaCorrectedLRRequest, ThetaCorrectedLRResponse,
    FstMatrixRequest, FstMatrixResponse,
)

router = APIRouter(prefix="/forensic/population", tags=["Population Genetics"])

_freq_db = FrequencyDatabase()
_rare_engine = RareAlleleEngine(default_database_n=500)
_substructure_engine = SubstructureEngine()
_dirichlet_engine = DirichletSmoothingEngine()
_hwe_engine = HWEEngine()



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


@router.post(
    "/dirichlet",
    response_model=DirichletSmoothResponse,
    summary="Module 03: Dirichlet Bayesian Allele Frequency Smoothing",
    description=(
        "Applies Dirichlet conjugate prior Bayesian smoothing to STR allele frequencies. "
        "Formula: p_tilde_i = (n_i + alpha_i) / (N + kappa), "
        "kappa = (1-theta)/theta. NRC II Rec 4.1 p_min floor always applied."
    ),
    status_code=status.HTTP_200_OK,
)
async def dirichlet_smooth(body: DirichletSmoothRequest) -> DirichletSmoothResponse:
    try:
        observed_counts = {float(k): v for k, v in body.observed_counts.items()}
        prior_freqs = {float(k): v for k, v in body.prior_frequencies.items()} if body.prior_frequencies else {}
        result = _dirichlet_engine.compute_locus_posteriors(
            locus=body.locus,
            observed_counts=observed_counts,
            prior_frequencies=prior_freqs,
            theta=body.theta,
            n_individuals=body.n_individuals,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Dirichlet smoothing failed: {str(exc)}"
        )

    allele_list = [
        DirichletAlleleResult(
            allele=ar.allele,
            observed_count=ar.observed_count,
            raw_frequency=ar.raw_frequency,
            prior_frequency=ar.prior_frequency,
            posterior_frequency=ar.posterior_frequency,
            dirichlet_alpha=ar.dirichlet_alpha,
            was_p_min_applied=ar.was_p_min_applied,
            p_min_used=ar.p_min_used,
        )
        for ar in result.allele_posteriors.values()
    ]
    return DirichletSmoothResponse(
        locus=result.locus,
        allele_posteriors=allele_list,
        n_individuals=result.n_individuals,
        theta=result.theta,
        concentration_parameter=result.concentration_parameter,
        sum_posterior=result.sum_posterior,
    )


@router.post(
    "/hwe",
    response_model=HWETestResponse,
    summary="Module 03: Hardy-Weinberg Equilibrium Exact Test",
    description=(
        "Guo & Thompson (1992) HWE exact test via Monte Carlo permutation. "
        "Reports H_obs, H_exp, F_IS (inbreeding coefficient), p-value and "
        "Bonferroni-corrected decision (alpha = 0.05/24 = 0.002083)."
    ),
    status_code=status.HTTP_200_OK,
)
async def test_hwe(body: HWETestRequest) -> HWETestResponse:
    try:
        # Parse "a1,a2" keys into (float, float) tuples
        genotype_counts = {}
        for key, count in body.genotype_counts.items():
            parts = key.split(",")
            if len(parts) != 2:
                raise ValueError(f"Invalid genotype key '{key}', expected 'a1,a2' format")
            a1, a2 = sorted([float(parts[0]), float(parts[1])])
            genotype_counts[(a1, a2)] = count

        result = _hwe_engine.test_locus_hwe(
            locus=body.locus,
            genotype_counts=genotype_counts,
            n_permutations=body.n_permutations,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"HWE test failed: {str(exc)}"
        )

    return HWETestResponse(
        locus=result.locus,
        n_alleles=result.n_alleles,
        n_genotypes=result.n_genotypes,
        h_obs=result.h_obs,
        h_exp=result.h_exp,
        f_is=result.f_is,
        p_value=result.p_value,
        alpha_bonferroni=result.alpha_bonferroni,
        hwe_rejected=result.hwe_rejected,
        decision=result.decision,
        n_permutations=result.n_permutations,
    )


@router.post(
    "/theta-lr",
    response_model=ThetaCorrectedLRResponse,
    summary="Module 03: NRC II Theta-Corrected Match Probability",
    description=(
        "Applies NRC II Recommendation 4.10b theta-corrected match probability formula. "
        "Homozygote: pi = [theta+(1-theta)*p_a]*[2*theta+(1-theta)*p_a]/[(1+theta)*(1+2*theta)]. "
        "Heterozygote: pi = 2*[theta+(1-theta)*p_a]*[theta+(1-theta)*p_b]/[(1+theta)*(1+2*theta)]."
    ),
    status_code=status.HTTP_200_OK,
)
async def theta_corrected_lr(body: ThetaCorrectedLRRequest) -> ThetaCorrectedLRResponse:
    try:
        if body.p_b is not None:
            match_prob = _substructure_engine.theta_corrected_lr_het(
                p_a=body.p_a, p_b=body.p_b, theta=body.theta
            )
            gtype = 'HETEROZYGOTE'
        else:
            match_prob = _substructure_engine.theta_corrected_lr(
                p_a=body.p_a, theta=body.theta
            )
            gtype = 'HOMOZYGOTE'

        log10_lr = -math.log10(max(match_prob, 1e-300))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Theta-corrected LR failed: {str(exc)}"
        )

    return ThetaCorrectedLRResponse(
        p_a=body.p_a,
        p_b=body.p_b,
        theta=body.theta,
        match_probability=round(match_prob, 8),
        log10_lr=round(log10_lr, 4),
        genotype_type=gtype,
    )


@router.post(
    "/fst-matrix",
    response_model=FstMatrixResponse,
    summary="Module 03: Pairwise FST Population Matrix",
    description=(
        "Computes full K*(K-1)/2 pairwise FST and Nei's D matrix for K populations. "
        "Recommends NRC II theta correction level (0.01/0.03/0.05) based on max FST."
    ),
    status_code=status.HTTP_200_OK,
)
async def fst_matrix(body: FstMatrixRequest) -> FstMatrixResponse:
    try:
        result = _substructure_engine.compute_fst_matrix(populations=body.populations)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"FST matrix computation failed: {str(exc)}"
        )

    # Serialize tuple keys as "pop1|pop2" strings for JSON
    matrix_json = {f"{p1}|{p2}": v for (p1, p2), v in result.matrix.items()}
    nei_json = {f"{p1}|{p2}": v for (p1, p2), v in result.nei_matrix.items()}

    return FstMatrixResponse(
        populations=result.populations,
        n_pairs=len(result.matrix),
        matrix=matrix_json,
        nei_matrix=nei_json,
        theta_recommendation=result.theta_recommendation,
        verdict=result.verdict,
    )

