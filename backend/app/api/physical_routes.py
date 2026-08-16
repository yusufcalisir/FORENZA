from fastapi import APIRouter, HTTPException, status
try:
    from app.api.physical_schemas import (
        BpaAreaOfOriginRequest,
        BpaAreaOfOriginResponse,
        GsrAnalysisRequest,
        GsrAnalysisResponse,
        CmcMatchingRequest,
        CmcMatchingResponse,
        EntomologyPmiRequest,
        EntomologyPmiResponse,
        MsiAnalysisRequest,
        MsiAnalysisResponse,
        TraceSpectroscopyRequest,
        TraceSpectroscopyResponse,
        PmrEvaluationRequest,
        PmrEvaluationResponse,
        AntemortemExtrapolationRequest,
        AntemortemExtrapolationResponse,
    )
    from node.services.forensic.physical import (
        BpaAreaOfOriginEngine,
        BallisticsGsrEngine,
        ForensicEntomologyEngine,
        TraceSpectroscopyMsiEngine,
        ForensicToxicologyPmrEngine,
    )
except ImportError:
    from backend.app.api.physical_schemas import (
        BpaAreaOfOriginRequest,
        BpaAreaOfOriginResponse,
        GsrAnalysisRequest,
        GsrAnalysisResponse,
        CmcMatchingRequest,
        CmcMatchingResponse,
        EntomologyPmiRequest,
        EntomologyPmiResponse,
        MsiAnalysisRequest,
        MsiAnalysisResponse,
        TraceSpectroscopyRequest,
        TraceSpectroscopyResponse,
        PmrEvaluationRequest,
        PmrEvaluationResponse,
        AntemortemExtrapolationRequest,
        AntemortemExtrapolationResponse,
    )
    from backend.node.services.forensic.physical import (
        BpaAreaOfOriginEngine,
        BallisticsGsrEngine,
        ForensicEntomologyEngine,
        TraceSpectroscopyMsiEngine,
        ForensicToxicologyPmrEngine,
    )

router = APIRouter(prefix="/forensic/physical", tags=["Forensic Physical Evidence & Ballistics"])
_BPA_ENGINE = BpaAreaOfOriginEngine()
_BALLISTICS_ENGINE = BallisticsGsrEngine()
_ENTO_ENGINE = ForensicEntomologyEngine()
_SPEC_ENGINE = TraceSpectroscopyMsiEngine()
_TOX_ENGINE = ForensicToxicologyPmrEngine()





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


@router.post(
    "/msi-optical-analysis",
    response_model=MsiAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Multispectral Optical Wavelength Response & Contrast Simulation",
    description="Evaluates 365nm UV-A, 415nm Soret, 450nm Blue, or 850nm NIR contrast mechanisms for questioned physical evidence."
)
async def analyze_msi_optical(req: MsiAnalysisRequest) -> MsiAnalysisResponse:
    try:
        result = _SPEC_ENGINE.simulate_msi_optical_response(
            evidence_type=req.evidence_type,
            active_wavelength_nm=req.active_wavelength_nm,
        )
        return MsiAnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MSI optical analysis error: {str(e)}"
        )


@router.post(
    "/ftir-raman-hqi-match",
    response_model=TraceSpectroscopyResponse,
    status_code=status.HTTP_200_OK,
    summary="ATR-FTIR & Raman Trace Spectral Matching (Hit Quality Index — HQI)",
    description="Compares unknown sample intensity spectrum against the forensic fiber & polymer library using normalized squared dot product (HQI >= 90.0% match)."
)
async def match_trace_spectroscopy(req: TraceSpectroscopyRequest) -> TraceSpectroscopyResponse:
    try:
        result = _SPEC_ENGINE.match_trace_spectrum(
            sample_spectrum=req.sample_spectrum,
            wavenumbers_cm_1=req.wavenumbers_cm_1,
        )
        return TraceSpectroscopyResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Trace micro-spectroscopy matching error: {str(e)}"
        )


@router.post(
    "/toxicology-pmr-evaluation",
    response_model=PmrEvaluationResponse,
    status_code=status.HTTP_200_OK,
    summary="Post-Mortem Drug Redistribution (PMR) C_heart / C_femoral Evaluation",
    description="Evaluates central-to-peripheral ratio against empirical Vd and literature benchmarks to detect systemic toxicity overestimation."
)
async def evaluate_pmr(req: PmrEvaluationRequest) -> PmrEvaluationResponse:
    try:
        result = _TOX_ENGINE.evaluate_pmr_ratio(
            compound_name=req.compound_name,
            c_heart=req.c_heart,
            c_femoral=req.c_femoral,
            unit=req.unit,
        )
        return PmrEvaluationResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PMR evaluation error: {str(e)}"
        )


@router.post(
    "/toxicology-antemortem-extrapolation",
    response_model=AntemortemExtrapolationResponse,
    status_code=status.HTTP_200_OK,
    summary="Antemortem Toxicokinetic Back-Extrapolation",
    description="Back-extrapolates antemortem concentration using zero-order (Ethanol Widmark) or first-order elimination kinetics."
)
async def extrapolate_antemortem_toxicology(req: AntemortemExtrapolationRequest) -> AntemortemExtrapolationResponse:
    try:
        result = _TOX_ENGINE.extrapolate_antemortem_concentration(
            compound_name=req.compound_name,
            c_femoral=req.c_femoral,
            elapsed_hours=req.elapsed_hours,
            unit=req.unit,
            custom_half_life_hours=req.custom_half_life_hours,
            custom_beta_60=req.custom_beta_60,
        )
        return AntemortemExtrapolationResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Antemortem toxicokinetic extrapolation error: {str(e)}"
        )




