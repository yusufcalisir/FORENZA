"""
FORENZA HIrisPlex-S DNA Pigmentation Forensics REST API Router (Module 3.1).
Exposes endpoints for full trait prediction, certified reference standards,
cross-validation, and VISAGE/ENFSI evaluative reporting shields.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status

from node.services.forensic.phenotyping.hirisplex_mathematical_formulation import (
    HIrisPlexMathematicalFormulation,
    EYE_COLOR_MODEL,
    HAIR_COLOR_MODEL,
    SKIN_PHOTOTYPE_MODEL,
)
from node.services.forensic.phenotyping.hirisplex_reference_datasets import (
    HIrisPlexReferenceDatasets,
)
from node.services.forensic.phenotyping.hirisplex_cross_validation import (
    HIrisPlexCrossValidationEngine,
)
from .hirisplex_schemas import (
    HIrisPlexPredictRequest,
    HIrisPlexFullResponse,
    PhenotypeTraitResponse,
    HIrisPlexStandardResponse,
    HIrisPlexCrossValResponse,
    HIrisPlexShieldResponse,
)

router = APIRouter(prefix="/forensic/phenotyping/hirisplex", tags=["Pillar 3: HIrisPlex-S Phenotyping"])


@router.post(
    "/predict-full",
    response_model=HIrisPlexFullResponse,
    summary="Simultaneous 41-SNP HIrisPlex-S Prediction (Eye, Hair, Skin, Morphology)",
    description="Predicts categorical probabilities across eye color, hair color & shade, skin phototype (Fitzpatrick I-VI), and hair morphology.",
    status_code=status.HTTP_200_OK,
)
async def predict_full_hirisplex(body: HIrisPlexPredictRequest) -> HIrisPlexFullResponse:
    try:
        res = HIrisPlexMathematicalFormulation.predict_full_hirisplex_s(
            genotype_dosages=body.genotype_dosages,
            enable_imputation=body.enable_imputation,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"HIrisPlex-S prediction failed: {str(exc)}",
        )

    return HIrisPlexFullResponse(
        eye_color=PhenotypeTraitResponse(
            domain=res.eye_color.domain,
            probabilities=res.eye_color.probabilities,
            predicted_class=res.eye_color.predicted_class,
            confidence=res.eye_color.confidence,
            is_simplex_valid=res.eye_color.is_simplex_valid,
            missing_loci_count=res.eye_color.missing_loci_count,
            imputed_loci_count=res.eye_color.imputed_loci_count,
            uncertainty_penalty_applied=res.eye_color.uncertainty_penalty_applied,
        ),
        hair_color=PhenotypeTraitResponse(
            domain=res.hair_color.domain,
            probabilities=res.hair_color.probabilities,
            predicted_class=res.hair_color.predicted_class,
            confidence=res.hair_color.confidence,
            is_simplex_valid=res.hair_color.is_simplex_valid,
            missing_loci_count=res.hair_color.missing_loci_count,
            imputed_loci_count=res.hair_color.imputed_loci_count,
            uncertainty_penalty_applied=res.hair_color.uncertainty_penalty_applied,
        ),
        hair_shade=res.hair_shade,
        skin_phototype=PhenotypeTraitResponse(
            domain=res.skin_phototype.domain,
            probabilities=res.skin_phototype.probabilities,
            predicted_class=res.skin_phototype.predicted_class,
            confidence=res.skin_phototype.confidence,
            is_simplex_valid=res.skin_phototype.is_simplex_valid,
            missing_loci_count=res.skin_phototype.missing_loci_count,
            imputed_loci_count=res.skin_phototype.imputed_loci_count,
            uncertainty_penalty_applied=res.skin_phototype.uncertainty_penalty_applied,
        ),
        hair_morphology=PhenotypeTraitResponse(
            domain=res.hair_morphology.domain,
            probabilities=res.hair_morphology.probabilities,
            predicted_class=res.hair_morphology.predicted_class,
            confidence=res.hair_morphology.confidence,
            is_simplex_valid=res.hair_morphology.is_simplex_valid,
            missing_loci_count=res.hair_morphology.missing_loci_count,
            imputed_loci_count=res.hair_morphology.imputed_loci_count,
            uncertainty_penalty_applied=res.hair_morphology.uncertainty_penalty_applied,
        ),
        total_snps_assayed=res.total_snps_assayed,
        total_snps_missing=res.total_snps_missing,
        global_confidence_score=res.global_confidence_score,
        prosecutors_fallacy_shield=res.prosecutors_fallacy_shield,
    )


@router.get(
    "/standards",
    response_model=List[HIrisPlexStandardResponse],
    summary="List Certified Reference Standards (NA12878, NA19240, Celtic, NA18507, HG002)",
    status_code=status.HTTP_200_OK,
)
async def list_standards() -> List[HIrisPlexStandardResponse]:
    stds = HIrisPlexReferenceDatasets.list_standards()
    return [
        HIrisPlexStandardResponse(
            standard_id=s.standard_id,
            name=s.name,
            population=s.population,
            description=s.description,
            genotype_dosages=s.genotype_dosages,
            expected_eye_class=s.expected_eye_class,
            min_eye_confidence=s.min_eye_confidence,
            expected_hair_class=s.expected_hair_class,
            min_hair_confidence=s.min_hair_confidence,
            expected_skin_class=s.expected_skin_class,
            min_skin_confidence=s.min_skin_confidence,
            expected_morphology=s.expected_morphology,
        )
        for s in stds
    ]


@router.get(
    "/cross-validation",
    response_model=List[HIrisPlexCrossValResponse],
    summary="Run Independent Tool Cross-Validation (Erasmus MC & VISAGE)",
    status_code=status.HTTP_200_OK,
)
async def run_cross_validation() -> List[HIrisPlexCrossValResponse]:
    r1 = HIrisPlexCrossValidationEngine.cross_validate_erasmus_mc_irisplex()
    r2 = HIrisPlexCrossValidationEngine.cross_validate_red_hair_mc1r()
    r3 = HIrisPlexCrossValidationEngine.cross_validate_visage_skin_phototype()

    return [
        HIrisPlexCrossValResponse(
            tool_name=r.tool_name,
            benchmark_name=r.benchmark_name,
            computed_probability=r.computed_probability,
            expected_probability=r.expected_probability,
            absolute_residual=r.absolute_residual,
            is_concordant=r.is_concordant,
            description=r.description,
        )
        for r in [r1, r2, r3]
    ]


@router.get(
    "/reporting-shield",
    response_model=HIrisPlexShieldResponse,
    summary="Retrieve VISAGE & ENFSI Evaluative Phenotyping Reporting Shield",
    status_code=status.HTTP_200_OK,
)
async def get_reporting_shield() -> HIrisPlexShieldResponse:
    shield = HIrisPlexCrossValidationEngine.get_visage_enfsi_reporting_shield()
    return HIrisPlexShieldResponse(
        has_phenotype_disclaimer=shield["has_phenotype_disclaimer"],
        prosecutors_fallacy_shield_active=shield["prosecutors_fallacy_shield_active"],
        disclaimer_text_en=shield["disclaimer_text_en"],
        disclaimer_text_tr=shield["disclaimer_text_tr"],
    )
