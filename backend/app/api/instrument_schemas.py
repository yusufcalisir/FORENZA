from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class IngestInstrumentOutputRequest(BaseModel):
    instrument_type: str = Field(
        default="CE",
        description="Instrument category: CE, QPCR, NGS, LCMS, MICROSCOPY"
    )
    raw_content: Optional[str] = Field(
        default="Sample Name,Locus,Allele 1,Allele 2,Height 1,Height 2\nSAMPLE-01,D3S1358,15,16,1200,1150\nSAMPLE-01,vWA,16,17,950,980",
        description="Raw text output content (CSV, VCF, etc.)"
    )
    small_autosomal_conc_ng_ul: Optional[float] = Field(default=0.85)
    large_autosomal_conc_ng_ul: Optional[float] = Field(default=0.80)
    male_y_conc_ng_ul: Optional[float] = Field(default=0.82)


class IngestInstrumentOutputResponse(BaseModel):
    status: str
    instrument_type: str
    parsed_data: Dict[str, Any]
    ingestion_provenance: str
