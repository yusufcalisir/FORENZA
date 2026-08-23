"""
FORENZA Massively Parallel Sequencing (MPS/NGS) STR API Router.
Exposes endpoints for sequence parsing, SE33 analysis, mixture deconvolution,
population biostatistics, and syntenic linkage audits under /forensic/mps-str.
"""

from typing import Dict, List, Any
from fastapi import APIRouter, HTTPException, status

from node.services.forensic.genomics.mps_str.schemas import (
    ParsedSTRSequence,
    SingleLocusMPSGenotype,
)
from node.services.forensic.genomics.mps_str.grammar import ISFGSequenceParser
from node.services.forensic.genomics.mps_str.converter import STRSequenceConverter
from node.services.forensic.genomics.mps_str.se33_engine import (
    SE33HyperPolymorphicEngine,
    SE33GenotypeAnalysisReport
)
from node.services.forensic.genomics.mps_str.mixture_deconvolution import (
    MPSMixtureDeconvolutionEngine,
    MultiLocusMixtureReport
)
from node.services.forensic.genomics.mps_str.biostatistics import (
    ForensicBiostatisticsEngine,
    MultiLocusDiversitySummary
)
from node.services.forensic.genomics.mps_str.linkage_guard import (
    SyntenicLinkageGuard,
    SyntenicPairKinshipAudit
)
from node.services.forensic.genomics.mps_str.golden_vectors import GOLDEN_VECTORS_MPS

from .mps_str_schemas import (
    ParseSequenceRequest,
    AnalyzeSE33Request,
    MixtureDeconvolutionRequest,
    BiostatisticsRequest,
    SyntenicLinkageRequest,
)

router = APIRouter(prefix="/forensic/mps-str", tags=["MPS / NGS STR Sequence Lab"])


@router.post(
    "/parse-sequence",
    response_model=ParsedSTRSequence,
    summary="Parse ISFG Sequence String",
    description="Parses standard ISFG syntax into repeat motif blocks, 5'/3' flanking mutations, and CE length calls.",
    status_code=status.HTTP_200_OK,
)
async def parse_isfg_sequence(body: ParseSequenceRequest) -> ParsedSTRSequence:
    try:
        return ISFGSequenceParser.parse_sequence_string(body.locus_name, body.sequence_string)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"ISFG sequence parsing failed: {str(exc)}"
        )


@router.post(
    "/analyze-se33",
    response_model=SE33GenotypeAnalysisReport,
    summary="SE33 Hyper-Polymorphic Deep Analysis",
    description="Performs bimodal repeat classification, 7 flanking variant detection, and 4-bp deletion reconciliation.",
    status_code=status.HTTP_200_OK,
)
@router.post(
    "/se33/analyze",
    response_model=SE33GenotypeAnalysisReport,
    include_in_schema=False,
    status_code=status.HTTP_200_OK,
)
async def analyze_se33_genotype(body: AnalyzeSE33Request) -> SE33GenotypeAnalysisReport:
    try:
        alleles = body.sequence_alleles or [a for a in [body.sequence_1, body.sequence_2] if a]
        if not alleles:
            raise ValueError("No sequence alleles provided for SE33 analysis.")
        return SE33HyperPolymorphicEngine.analyze_se33_genotype(alleles, body.population)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"SE33 analysis failed: {str(exc)}"
        )



@router.post(
    "/deconvolve-mixture",
    response_model=MultiLocusMixtureReport,
    summary="Multi-Locus Mixture Deconvolution",
    description="Deconvolves multi-contributor DNA mixtures using sequence-based isoalleles, computing sequence LR boost.",
    status_code=status.HTTP_200_OK,
)
async def deconvolve_mps_mixture(body: MixtureDeconvolutionRequest) -> MultiLocusMixtureReport:
    try:
        return MPSMixtureDeconvolutionEngine.deconvolve_multi_locus_mixture(
            body.sample_id,
            body.locus_sequence_map,
            body.contributors,
            body.population
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Mixture deconvolution failed: {str(exc)}"
        )


@router.post(
    "/biostatistics",
    response_model=MultiLocusDiversitySummary,
    summary="4-Population Forensic Biostatistics",
    description="Computes Expected Heterozygosity (H_exp), Power of Discrimination (PD), and Match Probability (PM).",
    status_code=status.HTTP_200_OK,
)
async def compute_biostatistics(body: BiostatisticsRequest) -> MultiLocusDiversitySummary:
    try:
        return ForensicBiostatisticsEngine.calculate_multi_locus_summary(body.locus_names, body.population)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Biostatistics calculation failed: {str(exc)}"
        )


@router.post(
    "/audit-linkage",
    response_model=SyntenicPairKinshipAudit,
    summary="D6S1043 - SE33 Syntenic Linkage Audit",
    description="Audits syntenic linkage between D6S1043 and SE33 on chromosome 6q (theta=0.0440) for kinship evaluations.",
    status_code=status.HTTP_200_OK,
)
async def audit_syntenic_linkage(body: SyntenicLinkageRequest) -> SyntenicPairKinshipAudit:
    try:
        return SyntenicLinkageGuard.audit_d6s1043_se33_kinship(
            body.d6s1043_lr,
            body.se33_lr,
            body.apply_single_locus_fallback
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Linkage audit failed: {str(exc)}"
        )


@router.get(
    "/golden-vectors",
    summary="Certified MPS Golden Vectors",
    description="Returns all 4 standardized reference golden vectors (VECTOR_MPS_01 to VECTOR_MPS_04).",
    status_code=status.HTTP_200_OK,
)
async def get_golden_vectors() -> List[Dict[str, Any]]:
    return [
        {
            "vector_id": v.vector_id,
            "name": v.name,
            "locus": v.locus,
            "population": v.population,
            "ce_apparent_genotype": v.ce_apparent_genotype,
            "mps_sequence_alleles": v.mps_sequence_alleles,
            "flanking_variants_detected": v.flanking_variants_detected,
            "expected_lr_mps_gain": v.expected_lr_mps_gain,
            "description": v.description,
            "iso17025_conformance_note": v.iso17025_conformance_note
        }
        for v in GOLDEN_VECTORS_MPS.values()
    ]
