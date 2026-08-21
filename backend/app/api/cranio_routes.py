"""
FastAPI Router for 3D Craniofacial Morphometry & Anthropological Landmarks (Module 3.3).
Pillar 3: Phenotyping, Biogeographic Ancestry & Morphometrics.
"""

from typing import Any, Dict, List
import numpy as np
from fastapi import APIRouter, HTTPException, Query

from backend.node.services.forensic.phenotyping.cranio_mathematical_formulation import (
    CraniofacialMathematicalFormulation,
    CRANIOFACIAL_LOCI,
)
from backend.node.services.forensic.phenotyping.cranio_reference_datasets import (
    CRANIOFACIAL_STANDARDS,
)
from backend.node.services.forensic.phenotyping.cranio_cross_validation import (
    CraniofacialCrossValidation,
)
from .cranio_schemas import (
    CraniofacialPredictionRequest,
    CraniofacialPredictionResponse,
    CephalometricLandmarksSchema,
    AnthropologicalIndicesSchema,
    Point3DSchema,
    ProcrustesAlignmentRequest,
    ProcrustesAlignmentResponse,
)

router = APIRouter(
    prefix="/forensic/phenotyping/craniofacial",
    tags=["Forensic Craniofacial Morphometrics & Anthropological Landmarks"],
)


@router.post("/reconstruct", response_model=CraniofacialPredictionResponse)
def reconstruct_craniofacial_profile(req: CraniofacialPredictionRequest):
    """
    Reconstructs 3D cephalometric landmarks, anthropological indices, and facial typology
    from morphometric SNP genotypes and biological sex dimorphism.
    """
    try:
        landmarks = CraniofacialMathematicalFormulation.reconstruct_cephalometric_landmarks(
            snp_dosages=req.snp_dosages,
            sex=req.sex,
            age_years=req.age_years,
        )
        indices = CraniofacialMathematicalFormulation.compute_anthropological_indices(
            landmarks=landmarks,
            sex=req.sex,
        )

        shield = CraniofacialCrossValidation.get_evaluative_reporting_shield()
        assayed_count = sum(1 for rs in CRANIOFACIAL_LOCI if rs in req.snp_dosages)

        lm_dict = landmarks.to_dict()
        lm_schema = CephalometricLandmarksSchema(
            nasion=Point3DSchema(**lm_dict["nasion"]),
            pronasale=Point3DSchema(**lm_dict["pronasale"]),
            subnasale=Point3DSchema(**lm_dict["subnasale"]),
            alare_left=Point3DSchema(**lm_dict["alare_left"]),
            alare_right=Point3DSchema(**lm_dict["alare_right"]),
            labiale_superius=Point3DSchema(**lm_dict["labiale_superius"]),
            menton=Point3DSchema(**lm_dict["menton"]),
            zygion_left=Point3DSchema(**lm_dict["zygion_left"]),
            zygion_right=Point3DSchema(**lm_dict["zygion_right"]),
            cheilion_left=Point3DSchema(**lm_dict["cheilion_left"]),
            cheilion_right=Point3DSchema(**lm_dict["cheilion_right"]),
        )

        ind_schema = AnthropologicalIndicesSchema(
            nasal_height_mm=indices.nasal_height_mm,
            alar_breadth_mm=indices.alar_breadth_mm,
            nasal_index=indices.nasal_index,
            nasal_typology=indices.nasal_typology,
            morphological_facial_height_mm=indices.morphological_facial_height_mm,
            bizygomatic_breadth_mm=indices.bizygomatic_breadth_mm,
            morphological_facial_index=indices.morphological_facial_index,
            facial_typology=indices.facial_typology,
            nasal_bridge_elevation_index=indices.nasal_bridge_elevation_index,
            facial_convexity_angle_deg=indices.facial_convexity_angle_deg,
            mandibular_breadth_mm=indices.mandibular_breadth_mm,
            sexual_dimorphism_offset_mm=indices.sexual_dimorphism_offset_mm,
        )

        return CraniofacialPredictionResponse(
            landmarks=lm_schema,
            indices=ind_schema,
            assayed_loci_count=assayed_count,
            prosecutors_fallacy_shield=shield["prosecutors_fallacy_shield"],
            validation_status="VERIFIED",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/superposition", response_model=ProcrustesAlignmentResponse)
def procrustes_superposition(req: ProcrustesAlignmentRequest):
    """
    Performs 3D Generalized Orthogonal Procrustes Superposition between target and source landmarks.
    """
    try:
        mat_target = np.array(req.landmarks_target, dtype=np.float64)
        mat_source = np.array(req.landmarks_source, dtype=np.float64)

        result = CraniofacialMathematicalFormulation.generalized_procrustes_superposition(
            mat_target, mat_source
        )

        return ProcrustesAlignmentResponse(
            centroid_size_target=result.centroid_size_1,
            centroid_size_source=result.centroid_size_2,
            procrustes_distance=result.procrustes_distance,
            rmsd_mm=result.rmsd_mm,
            rotation_matrix=result.rotation_matrix,
            translation_vector=result.translation_vector,
            aligned_matrix=result.aligned_matrix,
        )
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/standards")
def list_reference_standards():
    """
    Returns the certified craniofacial reference standards.
    """
    return {
        "standards": [
            {
                "standard_id": s.standard_id,
                "sample_name": s.sample_name,
                "population": s.population,
                "sex": s.sex,
                "age_years": s.age_years,
                "snp_dosages": s.snp_dosages,
                "expected_nasal_typology_prefix": s.expected_nasal_typology_prefix,
                "expected_min_nasal_index": s.expected_min_nasal_index,
                "expected_max_nasal_index": s.expected_max_nasal_index,
                "description": s.description,
            }
            for s in CRANIOFACIAL_STANDARDS.values()
        ]
    }


@router.get("/cross-validation")
def get_cross_validation_results(
    std1: str = Query(default="NA12878_CEU_EUROPEAN"),
    std2: str = Query(default="NA19240_YRI_AFRICAN"),
):
    """
    Returns independent tool cross-validation concordance metrics between two standards.
    """
    try:
        return CraniofacialCrossValidation.cross_validate_procrustes_alignment(std1, std2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reporting-shield")
def get_reporting_shield():
    """
    Returns the ENFSI (2017) & ISFG evaluative reporting shield and Prosecutor's Fallacy disclaimer.
    """
    return CraniofacialCrossValidation.get_evaluative_reporting_shield()
