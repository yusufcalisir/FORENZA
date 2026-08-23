"""
FORENZA Epigenetic Clocks & Multimodal PMI FastAPI REST API Routes (Pillar 4 & Pillar 5).

Endpoints:
  - GET  /api/v1/forensic/epigenetics/clocks/catalog
  - GET  /api/v1/forensic/epigenetics/clocks/tissue-offsets
  - GET  /api/v1/forensic/epigenetics/clocks/golden-vectors
  - POST /api/v1/forensic/epigenetics/clocks/estimate-age
  - POST /api/v1/forensic/epigenetics/clocks/biological-aging
  - POST /api/v1/forensic/epigenetics/clocks/multimodal-pmi
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict

from backend.node.services.forensic.epigenetics.clocks.schemas import (
    MethylationSample,
    ClockEstimationRequest,
    EpigeneticAgeResult,
    BiologicalAgingResult,
    TaphonomicPMIResult,
    MultimodalPMIRequest,
    ClockGeneration,
    EpigeneticTissueType,
)
from backend.node.services.forensic.epigenetics.clocks.clock_registry import (
    EpigeneticClockRegistry,
)
from backend.node.services.forensic.epigenetics.clocks.horvath_engine import (
    HorvathEpigeneticEngine,
)
from backend.node.services.forensic.epigenetics.clocks.hannum_engine import (
    HannumEpigeneticEngine,
)
from backend.node.services.forensic.epigenetics.clocks.acceleration_engine import (
    EpigeneticAccelerationEngine,
    LeukocyteProportions,
)
from backend.node.services.forensic.epigenetics.clocks.phenoage_engine import (
    PhenoAgeEngine,
)
from backend.node.services.forensic.epigenetics.clocks.grimage_engine import (
    GrimAgeEngine,
)
from backend.node.services.forensic.epigenetics.clocks.dunedin_pace_engine import (
    DunedinPACEEngine,
)
from backend.node.services.forensic.epigenetics.clocks.anti_averaging_guard import (
    AntiAveragingGuard,
)
from backend.node.services.forensic.epigenetics.clocks.visage_multiplex_engine import (
    VISAGEMultiplexEngine,
)
from backend.node.services.forensic.epigenetics.clocks.tissue_calibration_engine import (
    TissueCalibrationEngine,
    TISSUE_CALIBRATION_REGISTRY,
)
from backend.node.services.forensic.epigenetics.clocks.uncertainty_budget import (
    UncertaintyBudgetEngine,
)
from backend.node.services.forensic.epigenetics.clocks.taphonomy_engine import (
    TaphonomyEngine,
)
from backend.node.services.forensic.epigenetics.clocks.multimodal_pmi_engine import (
    MultimodalPMIEngine,
)
from backend.node.services.forensic.epigenetics.clocks.golden_vectors import (
    GOLDEN_VECTORS_CATALOG,
)
from backend.node.services.forensic.epigenetics.clocks.governance_engine import (
    EpigeneticGovernanceEngine,
)

router = APIRouter(prefix="/forensic/epigenetics/clocks", tags=["Forensic Epigenetic Clocks & PMI"])
_REGISTRY = EpigeneticClockRegistry()


# ── GET /catalog ─────────────────────────────────────────────────────────────
@router.get(
    "/catalog",
    status_code=status.HTTP_200_OK,
    summary="Retrieve master catalog of all 1st, 2nd, 3rd generation & forensic epigenetic clocks",
)
async def get_clock_catalog() -> Dict[str, Any]:
    clocks = _REGISTRY.get_all_clocks()
    return {
        "clock_count": len(clocks),
        "clocks": {
            cid: {
                "name": c.name,
                "generation": c.generation.value,
                "primary_tissues": [t.value for t in c.primary_tissues],
                "reported_mae": c.reported_mae,
                "has_piecewise_transform": c.has_piecewise_transform,
                "cpg_count": len(c.cpg_weights),
                "citations": c.citations,
            }
            for cid, c in clocks.items()
        },
    }


# ── GET /tissue-offsets ──────────────────────────────────────────────────────
@router.get(
    "/tissue-offsets",
    status_code=status.HTTP_200_OK,
    summary="Retrieve tissue-specific calibration offsets and standard uncertainties",
)
async def get_tissue_offsets() -> Dict[str, Any]:
    return {
        "offsets": {
            t.value: {
                "baseline_offset_years": p.baseline_offset_years,
                "reference_mae_years": p.reference_mae_years,
                "description_en": p.description,
                "description_tr": p.description_tr,
                "biological_rationale": p.biological_rationale,
            }
            for t, p in TISSUE_CALIBRATION_REGISTRY.items()
        }
    }


# ── GET /golden-vectors ──────────────────────────────────────────────────────
@router.get(
    "/golden-vectors",
    status_code=status.HTTP_200_OK,
    summary="Retrieve certified reference standards and golden benchmark vectors",
)
async def get_golden_vectors() -> Dict[str, Any]:
    return {
        "vectors": {
            vid: {
                "donor_name": v.donor_name,
                "true_chronological_age": v.true_chronological_age,
                "tissue_type": v.tissue_type.value,
                "smoking_pack_years": v.smoking_pack_years,
                "biological_sex": v.biological_sex,
                "expected_horvath_range": v.expected_horvath_range,
                "expected_visage_range": v.expected_visage_range,
                "sample": v.sample.model_dump(),
                "notes": v.notes,
            }
            for vid, v in GOLDEN_VECTORS_CATALOG.items()
        }
    }


# ── POST /estimate-age ───────────────────────────────────────────────────────
@router.post(
    "/estimate-age",
    status_code=status.HTTP_200_OK,
    summary="Estimate chronological age-at-death using 1st generation & forensic reduced multiplex clocks",
)
async def estimate_chronological_age(req: ClockEstimationRequest) -> Dict[str, Any]:
    try:
        tissue = req.sample.tissue_type
        tissue_offset = TissueCalibrationEngine.get_offset_for_tissue(tissue)
        selected_clocks = req.selected_clocks or req.target_clocks or ["horvath_2013", "visage_enhanced", "hannum_2013", "visage_basic"]
        known_age = req.chronological_age_known if req.chronological_age_known is not None else req.chronological_age

        results: List[EpigeneticAgeResult] = []

        for cid in selected_clocks:
            if cid in ("horvath_2013", "pedbe_2019"):
                r = HorvathEpigeneticEngine.predict_age(
                    sample=req.sample,
                    clock_id=cid,
                    chronological_age=known_age,
                    tissue_offset=tissue_offset,
                )
                results.append(r)
            elif cid == "hannum_2013":
                r = HannumEpigeneticEngine.predict_age(
                    sample=req.sample,
                    chronological_age=known_age,
                    tissue_offset=tissue_offset,
                )
                results.append(r)
            elif cid == "visage_basic":
                r = VISAGEMultiplexEngine.predict_visage_basic_mlr(
                    sample=req.sample,
                    chronological_age=known_age,
                    tissue_offset=tissue_offset,
                )
                results.append(r)
            elif cid == "visage_enhanced":
                r = VISAGEMultiplexEngine.predict_visage_enhanced(
                    sample=req.sample,
                    chronological_age=known_age,
                    tissue_offset=tissue_offset,
                )
                results.append(r)
            elif cid == "weidner_3cpg":
                r = VISAGEMultiplexEngine.predict_weidner_3cpg(
                    sample=req.sample,
                    chronological_age=known_age,
                    tissue_offset=tissue_offset,
                )
                results.append(r)
                results.append(r)

        if not results:
            raise ValueError("No valid chronological clocks were evaluated.")

        # Evaluative judicial reporting with ENFSI statements & Prosecutor's Fallacy shield
        judicial_report = EpigeneticGovernanceEngine.evaluate_judicial_admissibility(
            sample_id=req.sample.sample_id,
            clock_results=results,
            jurisdiction=req.jurisdiction,
        )

        return {
            "sample_id": req.sample.sample_id,
            "tissue_type": req.sample.tissue_type.value,
            "tissue_offset_applied": tissue_offset,
            "clock_results": [r.model_dump() for r in results],
            "judicial_report": {
                "admissible_chronological_age": judicial_report.admissible_chronological_age,
                "uncertainty_interval_95": judicial_report.uncertainty_interval_95,
                "enfsi_tier_level": judicial_report.enfsi_tier_level,
                "enfsi_statement_en": judicial_report.enfsi_statement_en,
                "enfsi_statement_tr": judicial_report.enfsi_statement_tr,
                "prosecutors_fallacy_shield": judicial_report.prosecutors_fallacy_shield,
                "statutory_compliance_status": judicial_report.statutory_compliance_status,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Epigenetic age estimation error: {str(e)}",
        )


# ── POST /biological-aging ───────────────────────────────────────────────────
@router.post(
    "/biological-aging",
    status_code=status.HTTP_200_OK,
    summary="Compute 2nd/3rd generation biological aging, mortality hazard risk & pace of aging",
)
async def compute_biological_aging(
    sample: MethylationSample,
    chronological_age: Optional[float] = None,
    smoking_pack_years: float = 0.0,
    biological_sex: str = "MALE",
) -> Dict[str, Any]:
    try:
        pheno_res = PhenoAgeEngine.predict_dnam_phenoage(
            sample=sample,
            chronological_age=chronological_age,
        )

        grim_res = GrimAgeEngine.predict_grimage(
            sample=sample,
            chronological_age=chronological_age,
            smoking_pack_years=smoking_pack_years,
            biological_sex=biological_sex,
        )

        pace_res = DunedinPACEEngine.calculate_pace_of_aging(
            sample=sample,
            smoking_pack_years=smoking_pack_years,
        )

        return {
            "sample_id": sample.sample_id,
            "phenoage": pheno_res,
            "grimage": grim_res,
            "dunedin_pace": pace_res,
            "anti_averaging_advisory": (
                "Biological clocks (PhenoAge, GrimAge, DunedinPACE) evaluate physiological decline "
                "and all-cause mortality hazard. They are legally inadmissible for suspect individualization."
            ),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Biological aging computation error: {str(e)}",
        )


# ── POST /multimodal-pmi ─────────────────────────────────────────────────────
@router.post(
    "/multimodal-pmi",
    response_model=TaphonomicPMIResult,
    status_code=status.HTTP_200_OK,
    summary="Compute multimodal Post-Mortem Interval (PMI) Bayesian evidence fusion",
)
async def compute_multimodal_pmi(req: MultimodalPMIRequest) -> TaphonomicPMIResult:
    try:
        return MultimodalPMIEngine.fuse_multimodal_pmi(req)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Multimodal PMI fusion error: {str(e)}",
        )
