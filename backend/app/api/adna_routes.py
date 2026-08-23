"""
FORENZA Ancient DNA & Degraded Forensic SNP API Router (Module 2.5).
Standards Compliance: ISFG Recommendations (2021), mapDamage 2.0 (2013), Briggs et al. (2007).

Exposes endpoints for Paleogenomics & Skeletal DNA Damage Modeling:
  POST /forensic/adna/mapdamage-profile        — Briggs 5' C->T and 3' G->A deamination curves
  POST /forensic/adna/fragmentation           — Exponential & log-normal fragment length distributions
  POST /forensic/adna/snp-likelihood          — Low-coverage damage-compensated SNP genotype calling
  POST /forensic/adna/contamination-subtraction— Culling of modern un-deaminated DNA contamination
  POST /forensic/adna/purine-excess           — Depurination pre-break site purine excess test
  GET  /forensic/adna/casework-cohorts        — Certified casework benchmark cohorts (Columbus, Briggs, etc.)
  GET  /forensic/adna/reporting-disclaimer    — ISFG Paleogenomics & aDNA Reporting Disclaimer
"""

from typing import Dict, List, Any
from fastapi import APIRouter, HTTPException, status

from node.services.forensic.adna.adna_mathematical_formulation import (
    AdnaMathematicalFormulation,
    DegradationRiskTier,
)
from node.services.forensic.adna.adna_reference_datasets import (
    AdnaReferenceDatasets,
    ADNA_CASEWORK_COHORTS,
)
from node.services.forensic.adna.adna_cross_validation import (
    AdnaCrossValidationEngine,
)
from .adna_schemas import (
    MapDamageProfileRequest, MapDamageProfileResponse,
    FragmentationRequest, FragmentationResponse,
    SNPLikelihoodRequest, SNPLikelihoodResponse,
    ContaminationRequest, ContaminationResponse,
    PurineExcessRequest, PurineExcessResponse,
    AdnaCaseworkCohortSchema,
)

router = APIRouter(
    prefix="/forensic/adna",
    tags=["Ancient & Degraded DNA Damage Kinetics (Module 2.5)"],
)


@router.post(
    "/mapdamage-profile",
    response_model=MapDamageProfileResponse,
    summary="Compute Briggs 5' C->T and 3' G->A Deamination Curves",
    status_code=status.HTTP_200_OK,
)
async def compute_mapdamage_profile(body: MapDamageProfileRequest) -> MapDamageProfileResponse:
    try:
        res = AdnaMathematicalFormulation.generate_mapdamage_curves(
            delta_0=body.delta_0,
            decay_alpha=body.decay_alpha,
            baseline=body.baseline_error,
            max_position=body.max_position,
            g_to_a_ratio=body.g_to_a_ratio,
        )

        summary = (
            f"Briggs aDNA Damage Profile: Terminal deamination delta_0={body.delta_0:.3f}, "
            f"decay rate alpha={body.decay_alpha:.3f}/bp, baseline error={body.baseline_error:.4f}."
        )

        return MapDamageProfileResponse(
            delta_0=res.delta_0,
            decay_alpha=res.decay_alpha,
            baseline_error=res.baseline_error,
            max_position=res.max_position,
            curve_5p_c_to_t=res.curve_5p_c_to_t,
            curve_3p_g_to_a=res.curve_3p_g_to_a,
            deamination_summary=summary,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"MapDamage profile computation failed: {str(exc)}",
        )


@router.post(
    "/fragmentation",
    response_model=FragmentationResponse,
    summary="Compute Fragment Length Distribution & Degradation Risk",
    status_code=status.HTTP_200_OK,
)
async def compute_fragmentation(body: FragmentationRequest) -> FragmentationResponse:
    try:
        stats = AdnaMathematicalFormulation.compute_exponential_fragmentation(
            lambda_param=body.lambda_param,
            l_min=body.l_min,
        )

        return FragmentationResponse(
            lambda_param=stats.lambda_param,
            l_min=stats.l_min,
            mean_length=stats.mean_length,
            median_length=stats.median_length,
            fraction_below_100bp=stats.fraction_below_100bp,
            degradation_tier=stats.degradation_tier.value,
            recommended_technology=stats.recommended_technology,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Fragmentation computation failed: {str(exc)}",
        )


@router.post(
    "/snp-likelihood",
    response_model=SNPLikelihoodResponse,
    summary="Damage-Aware Low-Coverage SNP Genotype Likelihood & Posteriors",
    status_code=status.HTTP_200_OK,
)
async def compute_snp_likelihood(body: SNPLikelihoodRequest) -> SNPLikelihoodResponse:
    try:
        res = AdnaMathematicalFormulation.compute_damage_aware_snp_likelihood(
            locus_id=body.locus_id,
            ref_allele=body.ref_allele,
            alt_allele=body.alt_allele,
            read_bases=body.read_bases,
            read_positions=body.read_positions,
            delta_0=body.delta_0,
            decay_alpha=body.decay_alpha,
            sequencing_error_rate=body.sequencing_error_rate,
            prior_p_ref=body.prior_p_ref,
        )

        return SNPLikelihoodResponse(
            locus_id=res.locus_id,
            ref_allele=res.ref_allele,
            alt_allele=res.alt_allele,
            read_count=res.read_count,
            raw_likelihoods=res.raw_likelihoods,
            log10_likelihoods=res.log10_likelihoods,
            posterior_probabilities=res.posterior_probabilities,
            called_genotype=res.called_genotype,
            is_damage_compensated=res.is_damage_compensated,
            deamination_risk_flag=res.deamination_risk_flag,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"SNP likelihood computation failed: {str(exc)}",
        )


@router.post(
    "/contamination-subtraction",
    response_model=ContaminationResponse,
    summary="Subtract Modern Un-Deaminated DNA Contamination",
    status_code=status.HTTP_200_OK,
)
async def subtract_contamination(body: ContaminationRequest) -> ContaminationResponse:
    try:
        res = AdnaMathematicalFormulation.subtract_modern_contamination(
            observed_curve=body.observed_curve,
            contamination_fraction=body.contamination_fraction,
            modern_terminal_rate=body.modern_terminal_rate,
        )

        return ContaminationResponse(
            contamination_fraction=res.contamination_fraction,
            observed_terminal_damage=res.observed_terminal_damage,
            modern_terminal_damage=res.modern_terminal_damage,
            true_ancient_terminal_damage=res.true_ancient_terminal_damage,
            corrected_curve=res.corrected_curve,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Contamination subtraction failed: {str(exc)}",
        )


@router.post(
    "/purine-excess",
    response_model=PurineExcessResponse,
    summary="Depurination Pre-Break Purine Excess Test",
    status_code=status.HTTP_200_OK,
)
async def evaluate_purine_excess(body: PurineExcessRequest) -> PurineExcessResponse:
    try:
        frac, is_anc = AdnaMathematicalFormulation.compute_pre_break_purine_excess(
            purine_minus1_count=body.purine_minus1_count,
            total_reads=body.total_reads,
        )

        return PurineExcessResponse(
            purine_fraction=frac,
            is_ancient_depurination_signature=is_anc,
            threshold_fraction=0.65,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Purine excess evaluation failed: {str(exc)}",
        )


@router.get(
    "/casework-cohorts",
    response_model=List[AdnaCaseworkCohortSchema],
    summary="List Certified aDNA Benchmark Cohorts",
    status_code=status.HTTP_200_OK,
)
async def list_casework_cohorts() -> List[AdnaCaseworkCohortSchema]:
    return [
        AdnaCaseworkCohortSchema(
            cohort_id=c.cohort_id,
            name=c.name,
            sample_type=c.sample_type,
            description=c.description,
            delta_0=c.delta_0,
            decay_alpha=c.decay_alpha,
            baseline_error=c.baseline_error,
            mean_fragment_length=c.mean_fragment_length,
            lambda_fragmentation=c.lambda_fragmentation,
            contamination_fraction=c.contamination_fraction,
            pre_break_purine_fraction=c.pre_break_purine_fraction,
            expected_degradation_tier=c.expected_degradation_tier.value,
            expected_tech_recommendation=c.expected_tech_recommendation,
        )
        for c in AdnaReferenceDatasets.list_casework_cohorts()
    ]


@router.get(
    "/reporting-disclaimer",
    summary="ISFG Paleogenomics & aDNA Reporting Disclaimer",
    status_code=status.HTTP_200_OK,
)
async def get_reporting_disclaimer() -> Dict[str, Any]:
    return AdnaCrossValidationEngine.get_isfg_paleogenomics_reporting_shield()
