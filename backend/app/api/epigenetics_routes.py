from fastapi import APIRouter, HTTPException, status
from backend.app.api.epigenetics_schemas import (
    PredictAgeRequest,
    PredictAgeResponse,
    DeconvolveTissueRequest,
    DeconvolveTissueResponse,
    LifestyleProfileRequest,
    LifestyleProfileResponse,
)
from backend.node.services.forensic.epigenetics import (
    EpigeneticClockEngine,
    TissueDeconvolutionEngine,
    LifestyleEpigeneticEngine,
)

router = APIRouter(prefix="/forensic/epigenetics", tags=["Forensic Epigenetics & Research"])
_AGE_ENGINE = EpigeneticClockEngine()
_TISSUE_ENGINE = TissueDeconvolutionEngine()
_LIFESTYLE_ENGINE = LifestyleEpigeneticEngine()


@router.post(
    "/predict-age",
    response_model=PredictAgeResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict chronological age from CpG methylation ratios with 95% prediction interval",
    description="Applies ElasticNet multivariate regression over CpG site methylation ratios (ELOVL2, FHL2, TRIM59, KLF14, MIR29B2CHG), applies tissue intercept calibration, and computes ISO 17025 95% prediction intervals."
)
async def predict_age(req: PredictAgeRequest) -> PredictAgeResponse:
    try:
        result = _AGE_ENGINE.predict_age(
            cpg_methylation=req.cpg_methylation,
            tissue_type=req.tissue_type,
            chronological_age_known=req.chronological_age_known
        )
        return PredictAgeResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Epigenetic age prediction error: {str(e)}"
        )


@router.post(
    "/deconvolve-tissue",
    response_model=DeconvolveTissueResponse,
    status_code=status.HTTP_200_OK,
    summary="Deconvolve biological tissue origin from tDMR methylation ratios",
    description="Applies Dirichlet-multinomial Gaussian mixture optimization over tDMR methylation profiles to determine top predicted tissue type and LR_tissue."
)
async def deconvolve_tissue(req: DeconvolveTissueRequest) -> DeconvolveTissueResponse:
    try:
        result = _TISSUE_ENGINE.deconvolve_sample(tdmr_methylation=req.tdmr_methylation)
        return DeconvolveTissueResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tissue deconvolution error: {str(e)}"
        )


@router.post(
    "/lifestyle-profile",
    response_model=LifestyleProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict lifestyle biomarkers (smoking, alcohol, circadian phase)",
    description="Evaluates AHRR cg05575921 methylation for smoking status, SLC6A3 for alcohol exposure, and PER2/BMAL1 for circadian diurnal phase shift."
)
async def lifestyle_profile(req: LifestyleProfileRequest) -> LifestyleProfileResponse:
    try:
        result = _LIFESTYLE_ENGINE.analyze_lifestyle_profile(
            ahrr_cg05575921_beta=req.ahrr_cg05575921_beta,
            slc6a3_beta=req.slc6a3_beta,
            per2_beta=req.per2_beta,
            bmal1_beta=req.bmal1_beta
        )
        return LifestyleProfileResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lifestyle epigenetics error: {str(e)}"
        )
