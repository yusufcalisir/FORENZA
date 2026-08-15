from fastapi import APIRouter, HTTPException, status
from typing import Dict, List, Tuple
from backend.app.api.genomics_schemas import (
    MultiLayerGenomicsRequest,
    MultiLayerGenomicsResponse,
    DeconvolveMixtureRequest,
    DeconvolveMixtureResponse,
    LocusDeconvolutionDetail,
)
from backend.node.services.forensic.genomics.multi_layer_engine import MultiLayerGenomicsEngine
from backend.node.services.forensic.probabilistic.mixture import MixtureDeconvolutionEngine

router = APIRouter(prefix="/forensic/genomics", tags=["Multi-Layered Forensic Genomics"])
_ENGINE = MultiLayerGenomicsEngine()


@router.post(
    "/synthesize-layers",
    response_model=MultiLayerGenomicsResponse,
    status_code=status.HTTP_200_OK,
    summary="Synthesize multi-layer genetic evidence (STR, SNP, mtDNA, Y-STR, WGS)",
    description="Calculates synthesized joint likelihood ratio (LR_joint), log10 LR_joint, composite exclusion probability (PE_joint), and maps to ENFSI verbal predicate."
)
async def synthesize_genomic_layers(req: MultiLayerGenomicsRequest) -> MultiLayerGenomicsResponse:
    try:
        result = _ENGINE.synthesize_genomic_layers(
            lr_str=req.lr_str,
            lr_snp=req.lr_snp,
            lr_mtdna=req.lr_mtdna,
            lr_y_str=req.lr_y_str,
            lr_wgs=req.lr_wgs,
            pe_str=req.pe_str,
            pe_snp=req.pe_snp,
            pe_mtdna=req.pe_mtdna,
            pe_y_str=req.pe_y_str,
            pe_wgs=req.pe_wgs
        )
        return MultiLayerGenomicsResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multi-layer genomic synthesis error: {str(e)}"
        )


@router.post(
    "/deconvolve",
    response_model=DeconvolveMixtureResponse,
    status_code=status.HTTP_200_OK,
    summary="Continuous MCMC Mixture Deconvolution",
    description="Runs 3-chain Metropolis-Hastings MCMC mixture deconvolution (EuroForMix / STRmix) for 2 to 4 contributors with Gelman-Rubin convergence and 95% HPD LR bounds."
)
async def deconvolve_mixture(req: DeconvolveMixtureRequest) -> DeconvolveMixtureResponse:
    try:
        engine = MixtureDeconvolutionEngine(
            model=req.model_engine,
            n_burn=req.n_burn,
            n_sample=req.n_sample,
            n_chains=req.n_chains,
            seed=42,
        )

        # Convert observed peaks from Dict[str, Dict[str, float]] to Dict[str, Dict[float, float]]
        parsed_observed: Dict[str, Dict[float, float]] = {}
        for locus, alleles_map in req.observed_peaks.items():
            parsed_observed[locus] = {float(a): float(h) for a, h in alleles_map.items()}

        suspect_geno: Optional[List[Tuple[float, float]]] = None
        if req.suspect_profile:
            suspect_geno = [(float(pair[0]), float(pair[1])) for pair in req.suspect_profile]

        result = engine.deconvolute(
            observed=parsed_observed,
            K=req.num_contributors,
            suspect_genotype=suspect_geno,
        )

        locus_details = []
        for lr in result.locus_results:
            if lr.top_candidates:
                top = lr.top_candidates[0]
                locus_details.append(LocusDeconvolutionDetail(
                    locus=lr.locus,
                    major_genotype=list(top.major_genotype),
                    minor_genotype=list(top.minor_genotype),
                    posterior_probability=top.posterior_probability,
                    log_likelihood=top.log_likelihood,
                ))

        lr = result.lr_result
        return DeconvolveMixtureResponse(
            num_contributors=result.n_contributors,
            model_engine=result.model_engine,
            log10_lr=lr.log10_lr_point,
            lr_value=lr.lr_point,
            hpd95_lower=lr.log10_lr_hpd95_lo,
            hpd95_upper=lr.log10_lr_hpd95_hi,
            posterior_mixture_weights=lr.posterior_mixture_weights,
            posterior_degradation_slopes=lr.posterior_degradation,
            r_hat_max=lr.convergence.r_hat_max if lr.convergence else 1.0,
            ess_min=lr.convergence.ess_min if lr.convergence else 1000.0,
            mcmc_converged=lr.convergence.converged if lr.convergence else True,
            major_contributor_identified=result.major_contributor_identified,
            locus_deconvolutions=locus_details,
            verbal_scale_en=lr.verbal_scale_en,
            verbal_scale_tr=lr.verbal_scale_tr,
            assumptions=result.assumptions,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Mixture deconvolution failed: {str(exc)}"
        )

