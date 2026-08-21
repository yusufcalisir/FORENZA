"""
FastAPI REST API Routes for FORENZA Biogeographic Ancestry (BGA-55) & GIS Engine (Module 3.2).
"""

from typing import Dict, List
from fastapi import APIRouter, HTTPException, Query, status

from node.services.forensic.phenotyping.bga_mathematical_formulation import (
    BGAMathematicalFormulation,
)
from node.services.forensic.phenotyping.bga_reference_datasets import (
    BGAReferenceDatasets,
)
from node.services.forensic.phenotyping.bga_cross_validation import (
    BGACrossValidationEngine,
)
from app.api.bga_schemas import (
    BGAPredictionRequest,
    BGAFullAnalysisResponse,
    BGAGoldenStandardSchema,
    BGACrossValidationSchema,
    BGAReportingShieldSchema,
)

router = APIRouter(
    prefix="/forensic/phenotyping/bga",
    tags=["Biogeographic Ancestry (BGA-55) & GIS Projection"],
)


@router.post(
    "/predict-full",
    response_model=BGAFullAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Estimate 55-SNP AIM continental admixture and project 3D WGS84 geodesic coordinates",
)
async def predict_bga_full(request: BGAPredictionRequest) -> BGAFullAnalysisResponse:
    try:
        res = BGAMathematicalFormulation.analyze_full_bga_profile(
            snp_dosages=request.snp_dosages,
            populations=request.populations,
        )
        return BGAFullAnalysisResponse(
            admixture={
                "proportions": res.admixture.proportions,
                "log_likelihoods": res.admixture.log_likelihoods,
                "dominant_population": res.admixture.dominant_population,
                "dominant_proportion": res.admixture.dominant_proportion,
                "admixture_classification": res.admixture.admixture_classification,
                "shannon_entropy": res.admixture.shannon_entropy,
                "simpson_diversity": res.admixture.simpson_diversity,
                "assayed_snps_count": res.admixture.assayed_snps_count,
                "is_simplex_valid": res.admixture.is_simplex_valid,
            },
            gis={
                "latitude": res.gis.latitude,
                "longitude": res.gis.longitude,
                "formatted_coords": res.gis.formatted_coords,
                "nearest_centroid": res.gis.nearest_centroid,
                "confidence_ellipse": {
                    "semi_major_deg": res.gis.confidence_ellipse.semi_major_deg,
                    "semi_minor_deg": res.gis.confidence_ellipse.semi_minor_deg,
                    "semi_major_km": res.gis.confidence_ellipse.semi_major_km,
                    "semi_minor_km": res.gis.confidence_ellipse.semi_minor_km,
                    "tilt_angle_deg": res.gis.confidence_ellipse.tilt_angle_deg,
                },
            },
            prosecutors_fallacy_shield=res.prosecutors_fallacy_shield,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"BGA estimation error: {str(e)}",
        )


@router.get(
    "/standards",
    response_model=List[BGAGoldenStandardSchema],
    status_code=status.HTTP_200_OK,
    summary="List all certified reference standards for 55-SNP AIM BGA",
)
async def get_bga_standards() -> List[BGAGoldenStandardSchema]:
    standards = BGAReferenceDatasets.list_standards()
    return [
        BGAGoldenStandardSchema(
            standard_id=s.standard_id,
            name=s.name,
            population=s.population,
            description=s.description,
            genotype_dosages=s.genotype_dosages,
            expected_dominant_pop=s.expected_dominant_pop,
            min_dominant_proportion=s.min_dominant_proportion,
            expected_lat_bounds=list(s.expected_lat_bounds),
            expected_lng_bounds=list(s.expected_lng_bounds),
            expected_classification=s.expected_classification,
        )
        for s in standards
    ]


@router.get(
    "/cross-validation",
    response_model=List[BGACrossValidationSchema],
    status_code=status.HTTP_200_OK,
    summary="Run independent tool cross-validation against FROG-kb and STRUCTURE 2.3.4",
)
async def get_bga_cross_validation() -> List[BGACrossValidationSchema]:
    res_frog = BGACrossValidationEngine.cross_validate_frog_kb_na12878_eur()
    res_str_afr = BGACrossValidationEngine.cross_validate_structure_na19240_afr()
    res_str_eas = BGACrossValidationEngine.cross_validate_structure_na18507_eas()

    return [
        BGACrossValidationSchema(
            tool_name=r.tool_name,
            benchmark_name=r.benchmark_name,
            computed_proportion=r.computed_proportion,
            expected_proportion=r.expected_proportion,
            absolute_residual=r.absolute_residual,
            is_concordant=r.is_concordant,
            description=r.description,
        )
        for r in [res_frog, res_str_afr, res_str_eas]
    ]


@router.get(
    "/reporting-shield",
    response_model=BGAReportingShieldSchema,
    status_code=status.HTTP_200_OK,
    summary="Retrieve ENFSI/ISFG evaluative reporting shields for BGA evidence",
)
async def get_bga_reporting_shield() -> BGAReportingShieldSchema:
    shield = BGACrossValidationEngine.get_bga_reporting_shield()
    return BGAReportingShieldSchema(**shield)
