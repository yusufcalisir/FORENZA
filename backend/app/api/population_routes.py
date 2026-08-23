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
    ProfileRMPRequest, ProfileRMPResponse,
    KinshipDuoRequest, KinshipDuoResponse,
    KinshipLocusSchema,
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


# ── 24-Locus STR & Kinship Endpoints ────────────────────────────────────────

@router.post(
    "/profile-rmp",
    response_model=ProfileRMPResponse,
    summary="24-Locus Autosomal STR Multi-Population Match Probability",
    description=(
        "Computes full 24-locus Random Match Probability (RMP), combined LR, and "
        "ISO/IEC 17025:2017 GUM expanded measurement uncertainty (U_95% = 2.00 * u_c)."
    ),
    status_code=status.HTTP_200_OK,
)
async def compute_profile_rmp(body: ProfileRMPRequest) -> ProfileRMPResponse:
    try:
        from node.services.forensic.terminal.nist_1036_popgen_engine import Nist1036PopGenEngine
        res = Nist1036PopGenEngine.calculate_multilocus_profile_probability(
            profile=body.profile,
            population=body.population,
            theta=body.theta,
            dropout_map=body.dropout_map,
            dropout_q=body.dropout_q,
            use_exact_balding_nichols=body.use_exact_balding_nichols,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Profile RMP computation failed: {str(exc)}"
        )

    return ProfileRMPResponse(
        population=res["population"],
        theta=res["theta"],
        evaluated_loci_count=res["evaluated_loci_count"],
        combined_rmp=res["combined_rmp"],
        combined_lr=res["combined_lr"],
        combined_log10_lr=res["combined_log10_lr"],
        enfsi_verbal_scale=res["enfsi_verbal_scale"],
        measurement_uncertainty=res["measurement_uncertainty"],
        invariants=res["invariants"],
        locus_results=res["locus_results"],
    )


@router.post(
    "/kinship-duo",
    response_model=KinshipDuoResponse,
    summary="Pedigree Kinship Evaluation (IBD & SMM)",
    description=(
        "Calculates pairwise Kinship Index (KI), Combined Paternity Index (CPI), and "
        "Probability of Paternity W(%) under Balding-Nichols theta and Stepwise Mutation Model."
    ),
    status_code=status.HTTP_200_OK,
)
async def compute_kinship_duo(body: KinshipDuoRequest) -> KinshipDuoResponse:
    try:
        from node.services.forensic.kinship.str_engine import KinshipSTREngine, KinshipRelationship
        # Resolve relationship enum
        rel_enum = KinshipRelationship.PARENT_CHILD
        for r in KinshipRelationship:
            if r.value.lower() == body.relationship.lower() or r.name.lower() == body.relationship.lower().replace("-", "_").replace(" ", "_"):
                rel_enum = r
                break

        res = KinshipSTREngine.compute_kinship_profile_analysis(
            profile1=body.profile1,
            profile2=body.profile2,
            relationship=rel_enum,
            population=body.population,
            theta=body.theta,
            apply_smm=body.apply_smm,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Kinship duo calculation failed: {str(exc)}"
        )

    locus_schemas = [
        KinshipLocusSchema(
            locus_name=loc.locus_name,
            genotype1=loc.genotype1,
            genotype2=loc.genotype2,
            shared_alleles=loc.shared_alleles,
            kinship_index=loc.kinship_index,
            log10_ki=loc.log10_ki,
            mutation_occurred=loc.mutation_occurred,
            formula=loc.formula,
        )
        for loc in res.locus_results
    ]

    return KinshipDuoResponse(
        relationship=res.relationship.value,
        population=res.population,
        theta=res.theta,
        evaluated_loci_count=res.evaluated_loci_count,
        combined_kinship_index=res.combined_kinship_index,
        combined_log10_ki=res.combined_log10_ki,
        probability_of_paternity_w=res.probability_of_paternity_w,
        enfsi_verbal_scale=res.enfsi_verbal_scale,
        locus_results=locus_schemas,
        invariants=res.invariants,
    )


# ── Module 1.3: NRC-II & Balding-Nichols Endpoints ───────────────────────────

from node.services.forensic.kinship.nrc_engine import NRCPopulationEngine
from .population_schemas import (
    NRCProfileLRRequest,
    NRCProfileLRResponse,
    NRCLocusResultSchema,
    NRCDemographicReportResponse,
    WeirCockerhamAPIRequest,
    WeirCockerhamAPIResponse,
    DCMAPIRequest,
    DCMAPIResponse,
    SimplexValidateRequest,
    SimplexValidateResponse,
    GoldenProfilesListResponse,
)

_nrc_engine = NRCPopulationEngine()


@router.post(
    "/nrc/profile-lr",
    response_model=NRCProfileLRResponse,
    summary="NRC II 24-Locus Profile Likelihood Ratio",
    description="Computes composite 24-locus Likelihood Ratio under Balding-Nichols coancestry theta correction with reciprocal hypothesis balance verification.",
    status_code=status.HTTP_200_OK,
)
async def compute_nrc_profile_lr(body: NRCProfileLRRequest) -> NRCProfileLRResponse:
    try:
        res = _nrc_engine.compute_profile_lr(
            suspect_profile=body.suspect_profile,
            evidence_profile=body.evidence_profile,
            population=body.population,
            theta=body.theta,
            p_min=body.p_min or 0.0024131
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"NRC Profile LR computation failed: {str(exc)}"
        )

    locus_schemas = [
        NRCLocusResultSchema(
            locus=l.locus,
            suspect_genotype=l.suspect_genotype,
            evidence_genotype=l.evidence_genotype,
            match_state=l.match_state,
            theta=l.theta,
            p_conditional=l.p_conditional,
            lr_locus=l.lr_locus,
            log10_lr_locus=l.log10_lr_locus,
        )
        for l in res.locus_results
    ]

    return NRCProfileLRResponse(
        locus_results=locus_schemas,
        total_lr=res.total_lr,
        log10_total_lr=res.log10_total_lr,
        reciprocal_lr=res.reciprocal_lr,
        is_reciprocal_balanced=res.is_reciprocal_balanced,
        reciprocal_product_delta=res.reciprocal_product_delta,
        theta_used=res.theta_used,
        population_used=res.population_used,
        verbal_scale_en=res.verbal_scale_en,
        verbal_scale_tr=res.verbal_scale_tr,
    )


@router.post(
    "/nrc/demographic-report",
    response_model=NRCDemographicReportResponse,
    summary="NRC II Multi-Population Demographic Stratification Report",
    description="Cross-evaluates a suspect DNA profile across all 4 NIST 1036 demographic populations (Caucasian, African American, Hispanic, Asian).",
    status_code=status.HTTP_200_OK,
)
async def compute_nrc_demographic_report(body: NRCProfileLRRequest) -> NRCDemographicReportResponse:
    try:
        res = _nrc_engine.evaluate_demographic_stratification(
            suspect_profile=body.suspect_profile,
            theta=body.theta
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Demographic stratification evaluation failed: {str(exc)}"
        )

    return NRCDemographicReportResponse(
        profile_id=res.profile_id,
        theta_used=res.theta_used,
        population_lrs=res.population_lrs,
        population_log10_lrs=res.population_log10_lrs,
        verbal_scales_en=res.verbal_scales_en,
        verbal_scales_tr=res.verbal_scales_tr,
        min_lr=res.min_lr,
        max_lr=res.max_lr,
        stratification_ratio=res.stratification_ratio,
    )


@router.post(
    "/nrc/weir-cockerham",
    response_model=WeirCockerhamAPIResponse,
    summary="Weir & Cockerham (1984) ANOVA Fst Estimation",
    description="Estimates unbiased theta_hat across multiple sub-populations from discrete sample count matrices.",
    status_code=status.HTTP_200_OK,
)
async def compute_weir_cockerham_api(body: WeirCockerhamAPIRequest) -> WeirCockerhamAPIResponse:
    try:
        # Convert string allele keys to float
        parsed_counts: Dict[str, Dict[float, int]] = {}
        for pop, counts in body.subpop_allele_counts.items():
            parsed_counts[pop] = {float(a): c for a, c in counts.items()}

        res = _nrc_engine.estimate_weir_cockerham_fst(
            subpop_allele_counts=parsed_counts,
            locus=body.locus
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Weir-Cockerham estimation failed: {str(exc)}"
        )

    return WeirCockerhamAPIResponse(
        theta_hat=res.theta_hat,
        msp=res.msp,
        msg=res.msg,
        n_c=res.n_c,
        num_populations=res.num_populations,
        num_alleles=res.num_alleles,
        locus=res.locus,
    )


@router.post(
    "/nrc/dcm",
    response_model=DCMAPIResponse,
    summary="Dirichlet Compound Multinomial Sampling Likelihood",
    description="Evaluates Dirichlet Compound Multinomial (Polya-Eggenberger) log-likelihood in log-gamma space.",
    status_code=status.HTTP_200_OK,
)
async def compute_dcm_api(body: DCMAPIRequest) -> DCMAPIResponse:
    try:
        parsed_counts = {float(a): c for a, c in body.allele_counts.items()}
        res = _nrc_engine.evaluate_dcm_likelihood(
            allele_counts=parsed_counts,
            population=body.population,
            locus=body.locus,
            theta=body.theta
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"DCM evaluation failed: {str(exc)}"
        )

    return DCMAPIResponse(
        log_likelihood=res.log_likelihood,
        probability=res.probability,
        kappa=res.kappa,
        total_alleles_sampled=res.total_alleles_sampled,
        num_distinct_alleles=res.num_distinct_alleles,
    )


@router.post(
    "/nrc/simplex-validate",
    response_model=SimplexValidateResponse,
    summary="Probability Simplex Normalization Invariant Validator",
    description="Validates that the sum of all diploid genotype probabilities on a locus equals 1.00000000 ± tolerance.",
    status_code=status.HTTP_200_OK,
)
async def validate_simplex_api(body: SimplexValidateRequest) -> SimplexValidateResponse:
    try:
        res = _nrc_engine.validate_locus_simplex(
            locus=body.locus,
            population=body.population,
            theta=body.theta,
            tolerance=body.tolerance
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Simplex validation failed: {str(exc)}"
        )

    return SimplexValidateResponse(
        locus=res.locus,
        theta=res.theta,
        sum_probability=res.sum_probability,
        delta_from_unity=res.delta_from_unity,
        num_genotypes_evaluated=res.num_genotypes_evaluated,
        is_valid=res.is_valid,
    )


@router.get(
    "/nrc/golden-profiles",
    response_model=GoldenProfilesListResponse,
    summary="List Certified Reference Individual Profiles",
    description="Returns metadata for globally standardized golden reference profiles (NIST SRM 2391d Components A, B, C and GIAB NA12878).",
    status_code=status.HTTP_200_OK,
)
async def list_golden_profiles_api() -> GoldenProfilesListResponse:
    profiles = _nrc_engine.list_golden_reference_profiles()
    return GoldenProfilesListResponse(
        total_profiles=len(profiles),
        profiles=profiles
    )


