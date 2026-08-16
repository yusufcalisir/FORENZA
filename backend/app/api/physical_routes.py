from fastapi import APIRouter, HTTPException, status
from backend.app.api.physical_schemas import (
    BpaAreaOfOriginRequest,
    BpaAreaOfOriginResponse,
)
from backend.node.services.forensic.physical import BpaAreaOfOriginEngine

router = APIRouter(prefix="/forensic/physical", tags=["Forensic Physical Evidence & Ballistics"])
_BPA_ENGINE = BpaAreaOfOriginEngine()


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
