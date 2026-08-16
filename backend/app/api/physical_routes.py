from fastapi import APIRouter, HTTPException, status
from backend.app.api.physical_schemas import (
    BpaAreaOfOriginRequest,
    BpaAreaOfOriginResponse,
    GsrAnalysisRequest,
    GsrAnalysisResponse,
    CmcMatchingRequest,
    CmcMatchingResponse,
    EntomologyPmiRequest,
    EntomologyPmiResponse,
)
from backend.node.services.forensic.physical import (
    BpaAreaOfOriginEngine,
    BallisticsGsrEngine,
    ForensicEntomologyEngine,
)

router = APIRouter(prefix="/forensic/physical", tags=["Forensic Physical Evidence & Ballistics"])
_BPA_ENGINE = BpaAreaOfOriginEngine()
_BALLISTICS_ENGINE = BallisticsGsrEngine()
_ENTO_ENGINE = ForensicEntomologyEngine()



@router.post(
    "/bpa-area-of-origin",
    response_model=BpaAreaOfOriginResponse,
    status_code=status.HTTP_200_OK,
    summary="3D Bloodstain Pattern Analysis (BPA) Area of Origin Least-Squares Optimization",
    description="Calculates the closed-form 3D point of convergence (x0, y0, z0) and spatial error radius from bloodstain coordinates and elliptical impact parameters."
)
async def solve_bpa_area_of_origin(req: BpaAreaOfOriginRequest) -> BpaAreaOfOriginResponse:
    try:
        stains_dict = [stain.model_dump() for stain in req.stains]
        result = _BPA_ENGINE.solve_3d_area_of_origin(
            stains=stains_dict,
            apply_drag_gravity_correction=req.apply_drag_gravity_correction,
        )
        return BpaAreaOfOriginResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"BPA Area of Origin calculation error: {str(e)}"
        )


@router.post(
    "/gsr-sem-edx-analysis",
    response_model=GsrAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="ASTM E1588-20 SEM-EDX Gunshot Residue (GSR) Particle Evaluation",
    description="Classifies microscopic elemental particles into Characteristic (Pb-Ba-Sb), Consistent, or Environmental tiers and calculates evidentiary Likelihood Ratio."
)
async def evaluate_gsr_sem_edx(req: GsrAnalysisRequest) -> GsrAnalysisResponse:
    try:
        particles_dict = [p.model_dump() for p in req.particles]
        result = _BALLISTICS_ENGINE.evaluate_sem_edx_gsr(particles_dict)
        return GsrAnalysisResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SEM-EDX GSR analysis error: {str(e)}"
        )


@router.post(
    "/cmc-striation-matching",
    response_model=CmcMatchingResponse,
    status_code=status.HTTP_200_OK,
    summary="3D Congruent Matching Cells (CMC) Firearm Striation Toolmark Comparison",
    description="Applies tri-threshold cross-correlation, spatial translation, and angular rotation convergence to establish firearm identification (K >= 6 CMC, P_false < 1e-6)."
)
async def evaluate_cmc_striations(req: CmcMatchingRequest) -> CmcMatchingResponse:
    try:
        cells_dict = [c.model_dump() for c in req.cells]
        result = _BALLISTICS_ENGINE.evaluate_3d_cmc_striations(
            cells=cells_dict,
            mean_delta_x_um=req.mean_delta_x_um,
            mean_delta_y_um=req.mean_delta_y_um,
            mean_delta_theta_deg=req.mean_delta_theta_deg,
        )
        return CmcMatchingResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"3D CMC striation analysis error: {str(e)}"
        )


@router.post(
    "/entomology-pmi-estimation",
    response_model=EntomologyPmiResponse,
    status_code=status.HTTP_200_OK,
    summary="Forensic Entomology Minimum Post-Mortem Interval (PMI_min) Thermal Summation",
    description="Integrates backward through hourly ambient temperatures to determine exact Minimum Insect Colonisation Interval (MICI) and colonisation timestamp."
)
async def estimate_entomology_pmi(req: EntomologyPmiRequest) -> EntomologyPmiResponse:
    try:
        temps_dict = [t.model_dump() for t in req.hourly_temperatures]
        result = _ENTO_ENGINE.estimate_pmi_min(
            species_name=req.species_name,
            development_stage=req.development_stage,
            hourly_temperatures=temps_dict,
            delta_t_mass=req.delta_t_mass,
            sampling_time_iso=req.sampling_time_iso,
        )
        return EntomologyPmiResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Forensic Entomology PMI estimation error: {str(e)}"
        )


