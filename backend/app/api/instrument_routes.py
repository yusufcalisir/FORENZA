from fastapi import APIRouter, HTTPException, status
from backend.app.api.instrument_schemas import IngestInstrumentOutputRequest, IngestInstrumentOutputResponse
from backend.node.services.forensic.instruments.parser_gateway import InstrumentParserGateway

router = APIRouter(prefix="/forensic/instruments", tags=["Automated Analytical Instrument Gateway"])
_PARSER = InstrumentParserGateway()


@router.post(
    "/ingest-output",
    response_model=IngestInstrumentOutputResponse,
    status_code=status.HTTP_200_OK,
    summary="Ingest raw output from analytical instruments (CE, qPCR, NGS, LC-MS/MS, Microscopy)",
)
async def ingest_instrument_output(req: IngestInstrumentOutputRequest) -> IngestInstrumentOutputResponse:
    try:
        inst_type = req.instrument_type.strip().upper()
        if inst_type == "CE":
            parsed = _PARSER.parse_ce_genemapper(req.raw_content or "")
        elif inst_type == "QPCR":
            parsed = _PARSER.parse_qpcr_quantifiler(
                req.small_autosomal_conc_ng_ul or 0.0,
                req.large_autosomal_conc_ng_ul or 0.0,
                req.male_y_conc_ng_ul or 0.0,
            )
        elif inst_type == "NGS":
            parsed = _PARSER.parse_ngs_vcf(req.raw_content or "")
        else:
            parsed = {"instrument_type": inst_type, "status": "INGESTED_GENERIC", "raw_length": len(req.raw_content or "")}

        return IngestInstrumentOutputResponse(
            status="SUCCESS",
            instrument_type=inst_type,
            parsed_data=parsed,
            ingestion_provenance="FORENZA Automated Analytical Instrument Gateway v1.0"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Instrument parsing failed: {str(e)}")
