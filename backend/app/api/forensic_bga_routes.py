"""
FastAPI REST API Router for Expanded Biogeographical Ancestry (AIMs) & HIrisPlex-S.

Provides endpoints for:
- Multi-vendor raw genotype ingestion (Microarray, VCF, SNaPshot)
- Dual-mode discrete and continuous admixture deconvolution (ADMIXTURE / SLSQP)
- PCA / SVD Procrustes 3D WGS84 Geodesic Projection
- HIrisPlex-S 41-SNP Phenotypic Pigmentation Prediction (Eye, Hair, Skin)
- German § 81e StPO statutory compliance and ethical governance gates
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field, ConfigDict

from backend.node.services.forensic.genomics.bga.schemas import (
    AIMPanelTypeEnum,
    PlatformFormatEnum,
    GenomicAssemblyEnum,
    ReferenceSystemEnum,
    JurisdictionCodeEnum,
    IngestedBGASample,
    AdmixtureProportionResult,
    PhenotypePredictionResult,
    LocusInformativenessReport,
    GovernanceComplianceResult
)
from backend.node.services.forensic.genomics.bga.parser import BGAGenotypeParser
from backend.node.services.forensic.genomics.bga.qc_engine import BGAQualityControlEngine
from backend.node.services.forensic.genomics.bga.panel_registry import AIMPanelRegistry
from backend.node.services.forensic.genomics.bga.reference_matrices import BGAReferenceMatrices
from backend.node.services.forensic.genomics.bga.informativeness_engine import BGAInformativenessEngine
from backend.node.services.forensic.genomics.bga.admixture_engine import BGAAdmixtureEngine
from backend.node.services.forensic.genomics.bga.hirisplex_model import HIrisPlexModelEngine
from backend.node.services.forensic.genomics.bga.governance_engine import BGAGovernanceEngine
from backend.node.services.forensic.genomics.bga.golden_vectors import BGAGoldenVectors

router = APIRouter(prefix="/api/forensic/bga", tags=["Forensic BGA & HIrisPlex-S"])


class IngestBGARequest(BaseModel):
    """Request payload for raw genotype ingestion."""
    model_config = ConfigDict(protected_namespaces=())

    raw_text: str = Field(..., description="Raw text content of 23andMe, AncestryDNA, VCF, or SNaPshot TSV")
    sample_id: str = Field(default="SAMPLE_BGA", description="Unique sample identifier")
    force_panel: Optional[AIMPanelTypeEnum] = None


class AnalyzeBGARequest(BaseModel):
    """Full BGA and Phenotyping analysis request payload."""
    model_config = ConfigDict(protected_namespaces=())

    raw_text: str = Field(..., description="Raw genotype file content")
    sample_id: str = Field(default="SAMPLE_BGA", description="Sample identifier")
    reference_system: ReferenceSystemEnum = Field(
        default=ReferenceSystemEnum.ONE_THOUSAND_GENOMES_26,
        description="Population reference genomics panel"
    )
    jurisdiction: JurisdictionCodeEnum = Field(
        default=JurisdictionCodeEnum.ISFG_INTERNATIONAL,
        description="Statutory legal jurisdiction"
    )
    magistrate_authorized: bool = Field(
        default=True,
        description="Examining magistrate authorization flag for Dutch Art. 151a Sv"
    )


class InformativenessRequest(BaseModel):
    """Informativeness calculation request for a specific locus."""
    model_config = ConfigDict(protected_namespaces=())

    rs_id: str
    reference_system: ReferenceSystemEnum = ReferenceSystemEnum.ONE_THOUSAND_GENOMES_26


@router.post("/ingest", response_model=IngestedBGASample)
async def ingest_genotypes(request: IngestBGARequest):
    """
    Ingests and normalizes raw multi-vendor genotype text into a standardized IngestedBGASample.
    """
    if not request.raw_text.strip():
        raise HTTPException(status_code=400, detail="Empty genotype payload received.")

    sample = BGAGenotypeParser.parse_raw_text(
        raw_text=request.raw_text,
        sample_id=request.sample_id,
        force_panel=request.force_panel
    )
    qc_sample = BGAQualityControlEngine.evaluate_sample(sample)
    return qc_sample


@router.post("/analyze")
async def analyze_bga_and_phenotype(request: AnalyzeBGARequest):
    """
    Executes full multi-omic pipeline: Ingestion -> QC -> Admixture SLSQP Deconvolution ->
    PCA / Procrustes WGS84 GIS -> HIrisPlex-S 41-SNP Phenotype -> Statutory Legal Governance.
    """
    if not request.raw_text.strip():
        raise HTTPException(status_code=400, detail="Empty genotype payload received.")

    sample = BGAGenotypeParser.parse_raw_text(raw_text=request.raw_text, sample_id=request.sample_id)
    qc_sample = BGAQualityControlEngine.evaluate_sample(sample)

    # 1. Admixture and GIS Projection
    ancestry_report = BGAAdmixtureEngine.generate_full_ancestry_report(qc_sample, request.reference_system)

    # 2. HIrisPlex-S Phenotypic Prediction
    phenotype_report = HIrisPlexModelEngine.predict_full_phenotype(qc_sample)

    # 3. Statutory Legal Governance and Redactions
    governance_result = BGAGovernanceEngine.apply_governance_to_reports(
        ancestry_report=ancestry_report,
        phenotype_report=phenotype_report,
        jurisdiction=request.jurisdiction,
        magistrate_authorized=request.magistrate_authorized
    )

    return {
        "sample_metadata": {
            "sample_id": qc_sample.sample_id,
            "detected_platform": qc_sample.detected_platform,
            "primary_panel": qc_sample.primary_panel,
            "call_rate": qc_sample.call_rate,
            "heterozygosity_rate": qc_sample.heterozygosity_rate,
            "qc_status": qc_sample.qc_status,
            "qc_flags": qc_sample.qc_flags
        },
        "governance": governance_result["compliance"],
        "ancestry_analysis": governance_result["ancestry_report"],
        "phenotype_prediction": governance_result["phenotype_report"]
    }


@router.get("/panels")
async def list_panels():
    """Returns list of registered AIM panels and catalogued loci counts."""
    return {
        "panels": [
            {
                "panel_code": AIMPanelTypeEnum.KIDD_55,
                "name": "Kidd 55-AIM Continental Reference Panel",
                "locus_count": len(AIMPanelRegistry.get_panel_loci(AIMPanelTypeEnum.KIDD_55))
            },
            {
                "panel_code": AIMPanelTypeEnum.PRECISION_ID_165,
                "name": "Precision ID 165-SNP Ancestry Panel",
                "locus_count": len(AIMPanelRegistry.get_panel_loci(AIMPanelTypeEnum.PRECISION_ID_165))
            },
            {
                "panel_code": AIMPanelTypeEnum.VISAGE_BASIC_153,
                "name": "VISAGE Basic Tool (Appearance + Ancestry)",
                "locus_count": len(AIMPanelRegistry.get_panel_loci(AIMPanelTypeEnum.VISAGE_BASIC_153))
            },
            {
                "panel_code": AIMPanelTypeEnum.MICROHAPLOTYPE_74,
                "name": "Forensic Multiallelic Microhaplotype Panel",
                "locus_count": len(AIMPanelRegistry.get_all_microhaplotypes())
            }
        ]
    }


@router.get("/reference-systems")
async def list_reference_systems():
    """Returns available high-diversity population genomics reference databases."""
    return {
        "reference_systems": [
            {
                "code": ReferenceSystemEnum.ONE_THOUSAND_GENOMES_26,
                "name": "1000 Genomes Project (NYGC 30x, 26 Populations)",
                "sample_size": 2504
            },
            {
                "code": ReferenceSystemEnum.GNOMAD_V4_9POP,
                "name": "gnomAD v4.1 (807k Exomes/Genomes, 9 Ancestry Groups)",
                "sample_size": 807162
            },
            {
                "code": ReferenceSystemEnum.HGDP_CEPH_54,
                "name": "HGDP-CEPH (54 Global Indigenous Populations)",
                "sample_size": 929
            }
        ]
    }


@router.get("/golden-vectors")
async def list_golden_vectors():
    """Returns certified standard multi-omic reference individuals."""
    return {
        "vectors": [
            {"id": "VECTOR_BGA_01", "name": "NA12878 / HG001 (CEU European Reference)"},
            {"id": "VECTOR_BGA_02", "name": "NA19240 (YRI Sub-Saharan African Reference)"},
            {"id": "VECTOR_BGA_03", "name": "NA18507 / HG005 (CHB East Asian Reference)"},
            {"id": "VECTOR_BGA_04", "name": "HG002 / NA24385 (Ashkenazi Jewish Reference)"},
            {"id": "VECTOR_BGA_05", "name": "Admixed Tri-Racial Standard Reference (EUR/AFR/AMR)"}
        ]
    }


@router.post("/informativeness", response_model=LocusInformativenessReport)
async def get_locus_informativeness(request: InformativenessRequest):
    """Calculates Rosenberg In and Wright's Fst metrics for an individual AIM locus."""
    rep = BGAInformativenessEngine.compute_rosenberg_in(request.rs_id, request.reference_system)
    return rep
