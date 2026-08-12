from fastapi import APIRouter, HTTPException, status
from backend.app.api.genomics_schemas import MultiLayerGenomicsRequest, MultiLayerGenomicsResponse
from backend.node.services.forensic.genomics.multi_layer_engine import MultiLayerGenomicsEngine

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
