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
