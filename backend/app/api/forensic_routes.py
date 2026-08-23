"""
FORENZA Forensic API Router.
Exposes three production endpoints under the /forensic prefix:
  POST /forensic/lr       — Single-source Likelihood Ratio evaluation
  POST /forensic/kinship  — Kinship Index calculation
  POST /forensic/validate — Internal validation simulation run
"""

import math
import uuid
from typing import Dict

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.frequency_db import FrequencyDatabase
from node.services.forensic.lr_engine import LREngine
from node.services.forensic.kinship_engine import KinshipEngine
from node.services.forensic.models import (
    KinshipRelationship, STRGenotype, STRProfile, SampleType
)
from node.services.forensic.validation.validator import ValidationRunner
from .forensic_schemas import (
    ConfidenceInterval,
    KinshipRequest, KinshipResponse,
    LRRequest, LRResponse,
    ValidationRequest, ValidationResponse,
)

router = APIRouter(prefix="/forensic", tags=["Forensic Engine"])


def _build_str_profile(profile_input, name_override: str = None) -> STRProfile:
    """Converts a ProfileInput Pydantic model into an STRProfile domain object."""
    loci: Dict[str, STRGenotype] = {}
    for locus_input in profile_input.loci:
        lname = locus_input.locus.upper()
        loci[lname] = STRGenotype(
            locus_name=lname,
            allele1=locus_input.allele1,
            allele2=locus_input.allele2
        )
    return STRProfile(
        profile_id=name_override or profile_input.profile_id,
        loci=loci,
        population_group=profile_input.population_group
    )


@router.post(
    "/lr",
    response_model=LRResponse,
    summary="Single-source Likelihood Ratio",
    description=(
        "Computes the Likelihood Ratio (LR) between evidence and suspect profiles "
        "under Balding-Nichols theta-corrected population frequency model. "
        "Returns INCLUSION or EXCLUSION with 95% HPD confidence interval."
    ),
    status_code=status.HTTP_200_OK,
)
async def compute_lr(body: LRRequest) -> LRResponse:
    try:
        population = body.population or body.suspect_profile.population_group
        freq_db = FrequencyDatabase(default_population=population)
        engine = LREngine(freq_db=freq_db)

        evidence = _build_str_profile(body.evidence_profile)
        suspect = _build_str_profile(body.suspect_profile)

        result = engine.compute_single_source_lr(
            evidence_profile=evidence,
            suspect_profile=suspect,
            theta=body.theta,
            population=population
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"LR computation failed: {str(exc)}"
        )

    lr_val = result.value
    log10_lr = math.log10(lr_val) if lr_val > 0 else -10.0

    return LRResponse(
        match_status=result.metadata.get("match_status", "UNKNOWN"),
        lr_value=lr_val,
        log10_lr=round(log10_lr, 4),
        confidence_interval=ConfidenceInterval(
            low=result.confidence_interval[0],
            high=result.confidence_interval[1]
        ),
        evaluated_loci=result.metadata.get("evaluated_loci_count", len(result.locus_scores)),
        locus_scores={k: round(v, 6) for k, v in result.locus_scores.items()},
        assumptions=result.assumptions,
        limitations=result.limitations,
        model=result.model,
        data_source=result.data_source,
    )


@router.post(
    "/kinship",
    response_model=KinshipResponse,
    summary="Kinship Index Calculator",
    description=(
        "Computes the Kinship Index (KI) for a given relationship hypothesis "
        "(parent_child | full_sibling | half_sibling | unrelated) and returns "
        "posterior relationship probability under equal prior odds."
    ),
    status_code=status.HTTP_200_OK,
)
async def compute_kinship(body: KinshipRequest) -> KinshipResponse:
    try:
        population = body.population or body.profile1.population_group
        freq_db = FrequencyDatabase(default_population=population)
        engine = KinshipEngine(freq_db=freq_db)

        p1 = _build_str_profile(body.profile1)
        p2 = _build_str_profile(body.profile2)

        relationship = KinshipRelationship(body.relationship)
        result = engine.compute_kinship_index(
            profile1=p1,
            profile2=p2,
            relationship=relationship,
            theta=body.theta,
            population=population
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Kinship computation failed: {str(exc)}"
        )

    ki_val = result.value
    log10_ki = math.log10(ki_val) if ki_val > 0 else -10.0

    return KinshipResponse(
        relationship=body.relationship,
        ki_value=ki_val,
        log10_ki=round(log10_ki, 4),
        confidence_interval=ConfidenceInterval(
            low=result.confidence_interval[0],
            high=result.confidence_interval[1]
        ),
        posterior_probability=round(result.metadata.get("posterior_probability", 0.0), 6),
        evaluated_loci=result.metadata.get("evaluated_loci_count", len(result.locus_scores)),
        locus_scores={k: round(v, 6) for k, v in result.locus_scores.items()},
        assumptions=result.assumptions,
        limitations=result.limitations,
        model=result.model,
        data_source=result.data_source,
    )


@router.post(
    "/validate",
    response_model=ValidationResponse,
    summary="Internal Validation Simulation",
    description=(
        "Runs a seeded synthetic validation simulation with n_per_type profile pairs "
        "per relationship category. Returns Accuracy, Sensitivity, Specificity, FIR, FER, "
        "RMSE(log10 LR), and Tippett curve sample data."
    ),
    status_code=status.HTTP_200_OK,
)
async def run_validation(body: ValidationRequest) -> ValidationResponse:
    try:
        run_id = f"API_{uuid.uuid4().hex[:8].upper()}"
        runner = ValidationRunner(
            population=body.population,
            theta=body.theta,
            seed=body.seed
        )
        report = runner.run(n_per_type=body.n_per_type, run_id=run_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation run failed: {str(exc)}"
        )

    mm = report.match_metrics
    return ValidationResponse(
        run_id=report.run_id,
        population=report.population,
        n_pairs_per_type=report.n_pairs_per_type,
        elapsed_seconds=report.elapsed_seconds,
        accuracy=mm["accuracy"],
        sensitivity_tpr=mm["sensitivity_tpr"],
        specificity_tnr=mm["specificity_tnr"],
        false_inclusion_rate=mm["false_inclusion_rate"],
        false_exclusion_rate=mm["false_exclusion_rate"],
        rmse_log10_lr=report.rmse_match_log10_lr,
        per_type_mean_log10_lr=report.per_type_mean_log10_lr,
        tippett_sample=report.tippett_data,
        model=report.metadata.get("model", "FORENZA Validation Runner v1.0"),
    )
