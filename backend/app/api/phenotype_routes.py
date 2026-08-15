"""
FORENZA Forensic DNA Phenotyping API Router.
Exposes POST /forensic/phenotype for HIrisPlex-S trait + BGA prediction.
"""

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.phenotyping.hirisplex import HiriPlexSEngine
from node.services.forensic.phenotyping.ancestry import AncestryEngine
from node.services.forensic.phenotyping.models import SNPInput, PhenotypeReport
from .phenotype_schemas import PhenotypeRequest, PhenotypeResponse, TraitPrediction

router = APIRouter(prefix="/forensic", tags=["Forensic Phenotyping"])

_hirisplex = HiriPlexSEngine()
_ancestry = AncestryEngine()


@router.post(
    "/phenotype",
    response_model=PhenotypeResponse,
    summary="Forensic DNA Phenotype Prediction",
    description=(
        "Predicts eye colour (IrisPlex 6-SNP), hair colour (HIrisPlex 22-SNP), "
        "skin tone (Fitzpatrick I–VI), and biogeographic ancestry from SNP dosage inputs. "
        "Based on Walsh et al. (2018) HIrisPlex-S validated coefficients."
    ),
    status_code=status.HTTP_200_OK,
)
async def predict_phenotype(body: PhenotypeRequest) -> PhenotypeResponse:
    try:
        snp_map = {s.rsid: SNPInput(rsid=s.rsid, dosage=s.dosage) for s in body.snps}

        eye = _hirisplex.predict_eye_colour(snp_map)
        hair = _hirisplex.predict_hair_colour(snp_map)
        skin = _hirisplex.predict_skin_tone(snp_map)
        anc = _ancestry.predict_ancestry(snp_map)

        report = PhenotypeReport(
            eye_colour=eye,
            hair_colour=hair,
            skin_tone=skin,
            ancestry=anc,
            snp_count_evaluated=len(snp_map),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Phenotype prediction failed: {str(exc)}"
        )

    return PhenotypeResponse(
        eye_colour=TraitPrediction(**eye.to_dict()["probabilities"] and {
            "most_likely": eye.most_likely,
            "confidence": round(eye.confidence, 4),
            "probabilities": {k: round(v, 4) for k, v in eye.probabilities.items()},
        }),
        hair_colour=TraitPrediction(
            most_likely=hair.most_likely,
            confidence=round(hair.confidence, 4),
            probabilities={k: round(v, 4) for k, v in hair.probabilities.items()},
        ),
        skin_tone=TraitPrediction(
            most_likely=skin.most_likely,
            confidence=round(skin.confidence, 4),
            probabilities={k: round(v, 4) for k, v in skin.probabilities.items()},
        ),
        ancestry=TraitPrediction(
            most_likely=anc.most_likely,
            confidence=round(anc.confidence, 4),
            probabilities={k: round(v, 4) for k, v in anc.probabilities.items()},
        ),
        snp_count_evaluated=report.snp_count_evaluated,
        model_version=report.model_version,
        limitations=report.limitations,
    )


# --- Extended HIrisPlex-S Router ---
from node.services.forensic.phenotyping.phenotype_engine import AdvancedPhenotypeEngine
from .phenotype_extended_schemas import PredictExtendedPhenotypeRequest, PredictExtendedPhenotypeResponse, UncertaintyIntervalSchema

_adv_pheno_engine = AdvancedPhenotypeEngine()


@router.post(
    "/phenotype/predict-extended",
    response_model=PredictExtendedPhenotypeResponse,
    summary="Extended HIrisPlex-S Phenotype & Population-Calibrated Uncertainty",
    description="Predicts Eye/Hair/Skin/Freckles/Morphology with population structure calibration and ISO 17025 U_95% uncertainty bounds.",
    status_code=status.HTTP_200_OK,
)
async def predict_extended_phenotype(body: PredictExtendedPhenotypeRequest) -> PredictExtendedPhenotypeResponse:
    try:
        res = _adv_pheno_engine.predict_extended_phenotype(
            sample_id=body.sample_id,
            snp_dosages=body.snp_dosages,
            ancestry_prior=body.ancestry_prior
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Extended phenotype prediction failed: {str(exc)}"
        )

    def convert_ui(ui_dict):
        return {
            k: UncertaintyIntervalSchema(
                probability=v.probability,
                u95_uncertainty=v.u95_uncertainty,
                ci_lower=v.ci_lower,
                ci_upper=v.ci_upper
            )
            for k, v in ui_dict.items()
        }

    fr = res.freckling_risk
    fr_schema = UncertaintyIntervalSchema(
        probability=fr.probability,
        u95_uncertainty=fr.u95_uncertainty,
        ci_lower=fr.ci_lower,
        ci_upper=fr.ci_upper
    )

    return PredictExtendedPhenotypeResponse(
        sample_id=res.sample_id,
        eye_color_probs=convert_ui(res.eye_color_probs),
        hair_color_probs=convert_ui(res.hair_color_probs),
        hair_morphology_probs=convert_ui(res.hair_morphology_probs),
        skin_tone_probs=convert_ui(res.skin_tone_probs),
        freckling_risk=fr_schema,
        top_eye_color=res.top_eye_color,
        top_hair_color=res.top_hair_color,
        top_hair_morphology=res.top_hair_morphology,
        top_skin_tone=res.top_skin_tone,
        biogeographic_ancestry_prior=res.biogeographic_ancestry_prior,
        phenotype_summary=res.phenotype_summary
    )


# ── Module 11 HIrisPlex-S Dedicated API Endpoints ────────────────────────────
from node.services.forensic.phenotyping.hirisplex_engine import HIrisPlexEngine
from .phenotype_schemas import (
    HIrisPlexSPredictionRequest, HIrisPlexSPredictionResponse,
    EyeColorResultSchema, HairColorResultSchema, SkinPhototypeResultSchema,
)

_hirisplex_m11 = HIrisPlexEngine()


@router.post(
    "/hirisplex-s/predict",
    response_model=HIrisPlexSPredictionResponse,
    summary="HIrisPlex-S Tri-Trait Pigmentation Prediction Suite (Module 11)",
    description="Simultaneously predicts Eye Color, Hair Color & Shade, and Fitzpatrick Skin Phototype via MLR Softmax. (Research §1)",
    status_code=status.HTTP_200_OK,
)
async def predict_hirisplex_s_full(body: HIrisPlexSPredictionRequest) -> HIrisPlexSPredictionResponse:
    try:
        res = _hirisplex_m11.predict_full_hirisplex_s(
            snp_dosages=body.snp_dosages,
            enable_imputation=body.enable_imputation,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"HIrisPlex-S prediction failed: {str(exc)}"
        )

    return HIrisPlexSPredictionResponse(
        eye_color=EyeColorResultSchema(
            probabilities=res.eye_color.probabilities,
            predicted_class=res.eye_color.predicted_class,
            confidence=res.eye_color.confidence,
            missing_loci_count=res.eye_color.missing_loci_count,
            imputed_loci_count=res.eye_color.imputed_loci_count,
        ),
        hair_color=HairColorResultSchema(
            probabilities=res.hair_color.probabilities,
            predicted_class=res.hair_color.predicted_class,
            confidence=res.hair_color.confidence,
            shade_probabilities=res.hair_color.shade_probabilities,
            predicted_shade=res.hair_color.predicted_shade,
            missing_loci_count=res.hair_color.missing_loci_count,
        ),
        skin_phototype=SkinPhototypeResultSchema(
            probabilities=res.skin_phototype.probabilities,
            fitzpatrick_type=res.skin_phototype.fitzpatrick_type,
            predicted_class=res.skin_phototype.predicted_class,
            confidence=res.skin_phototype.confidence,
            missing_loci_count=res.skin_phototype.missing_loci_count,
        ),
        total_snps_assayed=res.total_snps_assayed,
        missingness_ratio=res.missingness_ratio,
        prosecutors_fallacy_shield=res.prosecutors_fallacy_shield,
    )


@router.post(
    "/hirisplex-s/eye-color",
    response_model=EyeColorResultSchema,
    summary="IrisPlex 6-Loci Eye Color Prediction (Module 11)",
    status_code=status.HTTP_200_OK,
)
async def predict_irisplex_eye_color(body: HIrisPlexSPredictionRequest) -> EyeColorResultSchema:
    try:
        eye = _hirisplex_m11.predict_eye_color(
            snp_dosages=body.snp_dosages,
            enable_imputation=body.enable_imputation,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Eye color prediction failed: {str(exc)}"
        )

    return EyeColorResultSchema(
        probabilities=eye.probabilities,
        predicted_class=eye.predicted_class,
        confidence=eye.confidence,
        missing_loci_count=eye.missing_loci_count,
        imputed_loci_count=eye.imputed_loci_count,
    )


@router.post(
    "/hirisplex-s/hair-color",
    response_model=HairColorResultSchema,
    summary="HIrisPlex 22-Loci Hair Color & Shade Prediction (Module 11)",
    status_code=status.HTTP_200_OK,
)
async def predict_hirisplex_hair_color(body: HIrisPlexSPredictionRequest) -> HairColorResultSchema:
    try:
        hair = _hirisplex_m11.predict_hair_color(
            snp_dosages=body.snp_dosages,
            enable_imputation=body.enable_imputation,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Hair color prediction failed: {str(exc)}"
        )

    return HairColorResultSchema(
        probabilities=hair.probabilities,
        predicted_class=hair.predicted_class,
        confidence=hair.confidence,
        shade_probabilities=hair.shade_probabilities,
        predicted_shade=hair.predicted_shade,
        missing_loci_count=hair.missing_loci_count,
    )


@router.post(
    "/hirisplex-s/skin-phototype",
    response_model=SkinPhototypeResultSchema,
    summary="HIrisPlex-S 36-Loci Skin Phototype Prediction (Module 11)",
    status_code=status.HTTP_200_OK,
)
async def predict_hirisplex_skin_phototype(body: HIrisPlexSPredictionRequest) -> SkinPhototypeResultSchema:
    try:
        skin = _hirisplex_m11.predict_skin_phototype(
            snp_dosages=body.snp_dosages,
            enable_imputation=body.enable_imputation,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Skin phototype prediction failed: {str(exc)}"
        )

    return SkinPhototypeResultSchema(
        probabilities=skin.probabilities,
        fitzpatrick_type=skin.fitzpatrick_type,
        predicted_class=skin.predicted_class,
        confidence=skin.confidence,
        missing_loci_count=skin.missing_loci_count,
    )


# ── Module 12 55-AIM BGA & Live GIS Endpoints ─────────────────────────────────
from node.services.forensic.phenotyping.aim_bga_engine import AIMBGAEngine
from .phenotype_schemas import (
    AIMPredictionRequest, AIMPredictionResponse,
    GISCoordinatesSchema, ConfidenceEllipseSchema,
)

_aim_bga_engine = AIMBGAEngine()


@router.post(
    "/ancestry/55-aim/predict",
    response_model=AIMPredictionResponse,
    summary="55-AIM Continental Biogeographic Ancestry & GIS Geolocation (Module 12)",
    description="Calculates 5-continental Bayesian Dirichlet admixture (EUR, AFR, EAS, SAS, AMR) and 3D spherical GIS coordinates with 95% confidence ellipse. (Research §2)",
    status_code=status.HTTP_200_OK,
)
async def predict_55_aim_ancestry(body: AIMPredictionRequest) -> AIMPredictionResponse:
    try:
        res = _aim_bga_engine.analyze_bga_profile(body.snp_dosages)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"55-AIM ancestry analysis failed: {str(exc)}"
        )

    ellipse_schema = ConfidenceEllipseSchema(
        semi_major_deg=res.gis_projection.confidence_ellipse.semi_major_deg,
        semi_minor_deg=res.gis_projection.confidence_ellipse.semi_minor_deg,
        semi_major_km=res.gis_projection.confidence_ellipse.semi_major_km,
        semi_minor_km=res.gis_projection.confidence_ellipse.semi_minor_km,
        tilt_angle_deg=res.gis_projection.confidence_ellipse.tilt_angle_deg,
    )

    gis_schema = GISCoordinatesSchema(
        latitude=res.gis_projection.latitude,
        longitude=res.gis_projection.longitude,
        formatted_coords=res.gis_projection.formatted_coords,
        nearest_centroid=res.gis_projection.nearest_centroid,
        confidence_ellipse=ellipse_schema,
    )

    return AIMPredictionResponse(
        proportions=res.proportions,
        dominant_population=res.dominant_population,
        dominant_proportion=res.dominant_proportion,
        admixture_classification=res.admixture_classification,
        shannon_entropy=res.shannon_entropy,
        simpson_diversity=res.simpson_diversity,
        assayed_snps_count=res.assayed_snps_count,
        gis_projection=gis_schema,
        prosecutors_fallacy_shield=res.prosecutors_fallacy_shield,
    )


@router.post(
    "/ancestry/55-aim/gis-coordinates",
    response_model=GISCoordinatesSchema,
    summary="3D Spherical GIS Coordinate Projection (Module 12)",
    status_code=status.HTTP_200_OK,
)
async def project_55_aim_gis_coordinates(body: AIMPredictionRequest) -> GISCoordinatesSchema:
    try:
        res = _aim_bga_engine.analyze_bga_profile(body.snp_dosages)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"GIS coordinate projection failed: {str(exc)}"
        )

    ellipse_schema = ConfidenceEllipseSchema(
        semi_major_deg=res.gis_projection.confidence_ellipse.semi_major_deg,
        semi_minor_deg=res.gis_projection.confidence_ellipse.semi_minor_deg,
        semi_major_km=res.gis_projection.confidence_ellipse.semi_major_km,
        semi_minor_km=res.gis_projection.confidence_ellipse.semi_minor_km,
        tilt_angle_deg=res.gis_projection.confidence_ellipse.tilt_angle_deg,
    )

    return GISCoordinatesSchema(
        latitude=res.gis_projection.latitude,
        longitude=res.gis_projection.longitude,
        formatted_coords=res.gis_projection.formatted_coords,
        nearest_centroid=res.gis_projection.nearest_centroid,
        confidence_ellipse=ellipse_schema,
    )


# ── Module 13 Craniofacial Morphometrics & 3D Landmark Endpoints ─────────────
from node.services.forensic.phenotyping.morphometrics_engine import MorphometricsEngine
from .phenotype_schemas import (
    CraniofacialReconstructionRequest, CraniofacialReconstructionResponse,
    CephalometricLandmarksSchema, FacialIndicesSchema, Point3DSchema,
)

_morpho_engine = MorphometricsEngine()


@router.post(
    "/morphometrics/craniofacial/reconstruct-3d",
    response_model=CraniofacialReconstructionResponse,
    summary="3D Craniofacial Cephalometric Landmark Reconstruction (Module 13)",
    description="Reconstructs 7 primary 3D facial landmarks (N, Prn, Sn, Al_L, Al_R, Ls, Me) and morphological facial indices from PAX3, PAX9, PRDM16, DCHS2, PCDH15. (Research §3)",
    status_code=status.HTTP_200_OK,
)
async def reconstruct_craniofacial_3d(body: CraniofacialReconstructionRequest) -> CraniofacialReconstructionResponse:
    try:
        res = _morpho_engine.analyze_craniofacial_morphology(body.snp_dosages)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"3D Craniofacial reconstruction failed: {str(exc)}"
        )

    lm = res.landmarks
    landmarks_schema = CephalometricLandmarksSchema(
        nasion=Point3DSchema(x=lm.nasion.x, y=lm.nasion.y, z=lm.nasion.z),
        pronasale=Point3DSchema(x=lm.pronasale.x, y=lm.pronasale.y, z=lm.pronasale.z),
        subnasale=Point3DSchema(x=lm.subnasale.x, y=lm.subnasale.y, z=lm.subnasale.z),
        alare_left=Point3DSchema(x=lm.alare_left.x, y=lm.alare_left.y, z=lm.alare_left.z),
        alare_right=Point3DSchema(x=lm.alare_right.x, y=lm.alare_right.y, z=lm.alare_right.z),
        labiale_superius=Point3DSchema(x=lm.labiale_superius.x, y=lm.labiale_superius.y, z=lm.labiale_superius.z),
        menton=Point3DSchema(x=lm.menton.x, y=lm.menton.y, z=lm.menton.z),
    )

    idx = res.indices
    indices_schema = FacialIndicesSchema(
        morphological_facial_height_mm=idx.morphological_facial_height_mm,
        alar_breadth_mm=idx.alar_breadth_mm,
        nasal_height_mm=idx.nasal_height_mm,
        nasal_projection_mm=idx.nasal_projection_mm,
        facial_index_ratio=idx.facial_index_ratio,
        facial_typology=idx.facial_typology,
    )

    return CraniofacialReconstructionResponse(
        landmarks=landmarks_schema,
        indices=indices_schema,
        assayed_loci_count=res.assayed_loci_count,
        prosecutors_fallacy_shield=res.prosecutors_fallacy_shield,
    )


@router.post(
    "/morphometrics/craniofacial/landmarks",
    response_model=CephalometricLandmarksSchema,
    summary="Extract 3D Cephalometric Coordinates Only (Module 13)",
    status_code=status.HTTP_200_OK,
)
async def get_cephalometric_landmarks_only(body: CraniofacialReconstructionRequest) -> CephalometricLandmarksSchema:
    try:
        lm = _morpho_engine.reconstruct_3d_landmarks(body.snp_dosages)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Landmark extraction failed: {str(exc)}"
        )

    return CephalometricLandmarksSchema(
        nasion=Point3DSchema(x=lm.nasion.x, y=lm.nasion.y, z=lm.nasion.z),
        pronasale=Point3DSchema(x=lm.pronasale.x, y=lm.pronasale.y, z=lm.pronasale.z),
        subnasale=Point3DSchema(x=lm.subnasale.x, y=lm.subnasale.y, z=lm.subnasale.z),
        alare_left=Point3DSchema(x=lm.alare_left.x, y=lm.alare_left.y, z=lm.alare_left.z),
        alare_right=Point3DSchema(x=lm.alare_right.x, y=lm.alare_right.y, z=lm.alare_right.z),
        labiale_superius=Point3DSchema(x=lm.labiale_superius.x, y=lm.labiale_superius.y, z=lm.labiale_superius.z),
        menton=Point3DSchema(x=lm.menton.x, y=lm.menton.y, z=lm.menton.z),
    )



