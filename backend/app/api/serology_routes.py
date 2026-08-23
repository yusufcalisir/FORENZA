"""
FORENZA Forensic Serology API Router.
Exposes endpoints for ABO/Rh Blood Group Antigen Evaluation and Dual Serology + DNA Evidence Fusion
under the /forensic/serology prefix.
"""

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.serology.serology import ForensicSerologyEngine, SerologicalPhenotypeData
from node.services.forensic.serology.integration import SerologyDnaIntegrator
from .serology_schemas import (
    SerologyPhenotypeRequest, SerologyPhenotypeResponse,
    SerologyDnaIntegrateRequest, SerologyDnaIntegrateResponse
)

router = APIRouter(prefix="/forensic/serology", tags=["Forensic Serology & Blood Groups"])

_serology_engine = ForensicSerologyEngine()
_integrator = SerologyDnaIntegrator()


@router.post(
    "/phenotype",
    response_model=SerologyPhenotypeResponse,
    summary="ABO/Rh Blood Group Phenotype Evaluation",
    description="Evaluates ABO, Rh, Kell antigen phenotypes, secretor status, and calculates serological match frequency.",
    status_code=status.HTTP_200_OK,
)
async def evaluate_serology_phenotype(body: SerologyPhenotypeRequest) -> SerologyPhenotypeResponse:
    try:
        sample_dom = SerologicalPhenotypeData(
            sample_id=body.sample.sample_id,
            abo_group=body.sample.abo_group,
            rh_factor=body.sample.rh_factor,
            kell_status=body.sample.kell_status,
            lewis_phenotype=body.sample.lewis_phenotype
        )
        res = _serology_engine.evaluate_phenotype(sample_dom)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Serology phenotype evaluation failed: {str(exc)}"
        )

    return SerologyPhenotypeResponse(
        sample_id=res.sample_id,
        abo_group=res.abo_group,
        rh_factor=res.rh_factor,
        secretor_status=res.secretor_status,
        combined_serology_frequency=res.combined_serology_frequency,
        serology_likelihood_ratio=res.serology_likelihood_ratio,
        serology_summary=res.serology_summary
    )


@router.post(
    "/integrate-dna",
    response_model=SerologyDnaIntegrateResponse,
    summary="Dual Serology + DNA Evidence Integration",
    description="Combines classical serology LR with 24-locus autosomal STR LR (LR_combined = LR_serology * LR_STR).",
    status_code=status.HTTP_200_OK,
)
async def integrate_serology_and_dna(body: SerologyDnaIntegrateRequest) -> SerologyDnaIntegrateResponse:
    try:
        sample_dom = SerologicalPhenotypeData(
            sample_id=body.sample.sample_id,
            abo_group=body.sample.abo_group,
            rh_factor=body.sample.rh_factor,
            kell_status=body.sample.kell_status,
            lewis_phenotype=body.sample.lewis_phenotype
        )
        ser_res = _serology_engine.evaluate_phenotype(sample_dom)
        res = _integrator.integrate_serology_and_dna(body.sample.sample_id, ser_res, body.lr_str)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Dual Serology + DNA integration failed: {str(exc)}"
        )

    return SerologyDnaIntegrateResponse(
        sample_id=res.sample_id,
        lr_serology=res.lr_serology,
        lr_str=res.lr_str,
        lr_combined=res.lr_combined,
        log10_lr_combined=res.log10_lr_combined,
        verbal_statement=res.verbal_statement,
        integration_summary=res.integration_summary
    )
