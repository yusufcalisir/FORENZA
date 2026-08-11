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
