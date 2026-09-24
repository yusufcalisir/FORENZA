"""
FORENZA Massively Parallel Sequencing (MPS/NGS) STR API Router.
Exposes endpoints for sequence parsing, SE33 analysis, genotype evaluation,
mixture deconvolution, population biostatistics, flanking rescue, and syntenic linkage audits under /forensic/mps-str.
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
    SyntenicPairKinshipAudit,
    FlankingRescueReport
)
from node.services.forensic.genomics.mps_str.signal_filter import (
    MPSSignalFilter,
    MPSSignalFilterResult
)
from node.services.forensic.genomics.mps_str.frequency_matrices import (
    AUTOSOMAL_25_LOCI_REGISTRY,
    SequenceFrequencyMatrixEngine
)
from node.services.forensic.genomics.mps_str.golden_vectors import GOLDEN_VECTORS_MPS

from .mps_str_schemas import (
    ParseSequenceRequest,
    AnalyzeSE33Request,
    AnalyzeGenotypeRequest,
    AnalyzeGenotypeReport,
    MixtureDeconvolutionRequest,
    BiostatisticsRequest,
    SyntenicLinkageRequest,
    FlankingRescueRequest,
    FilterStutterRequest,
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
    "/analyze-genotype",
    response_model=AnalyzeGenotypeReport,
    summary="Universal 25-Locus MPS Genotype Analysis",
    description="Evaluates single-locus MPS vs CE Likelihood Ratios, information gain boost, and concordance.",
    status_code=status.HTTP_200_OK,
)
async def analyze_mps_genotype(body: AnalyzeGenotypeRequest) -> AnalyzeGenotypeReport:
    try:
        locus = body.locus_name.upper().strip()
        if locus == "SE33":
            se33_rep = SE33HyperPolymorphicEngine.analyze_se33_genotype(body.sequence_alleles, body.population)
            return AnalyzeGenotypeReport(
                locus_name="SE33",
                ce_genotype=se33_rep.ce_genotype,
                mps_genotype=se33_rep.mps_genotype,
                ce_single_locus_lr=se33_rep.ce_single_locus_lr,
                mps_single_locus_lr=se33_rep.mps_single_locus_lr,
                information_gain_ratio=se33_rep.information_gain_ratio,
                is_fully_concordant=se33_rep.is_fully_concordant,
                quality_assurance_notes=se33_rep.quality_assurance_notes
            )

        genotype = STRSequenceConverter.build_single_locus_genotype(locus, body.sequence_alleles)
        ce_calls = [p.ce_length_call for p in genotype.alleles]

        # Calculate sequence frequencies and marginalize to CE length allele frequencies
        p_seqs = [
            SequenceFrequencyMatrixEngine.get_sequence_frequency(locus, a.raw_sequence_string, body.population)
            for a in genotype.alleles
        ]
        all_locus_freqs = SequenceFrequencyMatrixEngine.get_all_frequencies_for_locus(locus, body.population)
        ce_marginal_map: Dict[str, float] = {}
        for seq_str, freq in all_locus_freqs.items():
            ce_val, _ = STRSequenceConverter.mps_to_ce_allele(locus, seq_str)
            ce_str_key = f"{ce_val:g}"
            ce_marginal_map[ce_str_key] = ce_marginal_map.get(ce_str_key, 0.0) + freq

        p_ces = [
            max(ce_marginal_map.get(f"{a.ce_length_call:g}", 0.0), p_seq)
            for a, p_seq in zip(genotype.alleles, p_seqs)
        ]

        if len(p_seqs) == 2:
            is_het = genotype.is_heterozygous
            lr_seq = 1.0 / (2.0 * p_seqs[0] * p_seqs[1]) if is_het else 1.0 / (p_seqs[0] ** 2)
            lr_ce = 1.0 / (2.0 * p_ces[0] * p_ces[1]) if is_het else 1.0 / (p_ces[0] ** 2)
        elif len(p_seqs) == 1:
            lr_seq = 1.0 / (p_seqs[0] ** 2)
            lr_ce = 1.0 / (p_ces[0] ** 2)
        else:
            # Multi-allele mixture fallback
            prod_seq = 1.0
            prod_ce = 1.0
            for ps in p_seqs:
                prod_seq *= max(1e-6, ps)
            for pc in p_ces:
                prod_ce *= max(1e-6, pc)
            lr_seq = 1.0 / max(1e-15, prod_seq)
            lr_ce = 1.0 / max(1e-15, prod_ce)

        gain = lr_seq / lr_ce if lr_ce > 0 else 1.0

        qa_notes = list(genotype.quality_flags)
        if not qa_notes:
            qa_notes.append(f"Standard {locus} genotype evaluated against {body.population} sequence matrix.")

        return AnalyzeGenotypeReport(
            locus_name=locus,
            ce_genotype=genotype.ce_genotype_string,
            mps_genotype=genotype.mps_genotype_string,
            ce_single_locus_lr=round(lr_ce, 2),
            mps_single_locus_lr=round(lr_seq, 2),
            information_gain_ratio=round(gain, 2),
            is_fully_concordant=True,
            quality_assurance_notes=qa_notes
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Genotype analysis failed: {str(exc)}"
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
@router.post(
    "/syntenic-linkage",
    response_model=SyntenicPairKinshipAudit,
    include_in_schema=False,
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


@router.post(
    "/flanking-rescue",
    response_model=FlankingRescueReport,
    summary="vWA Flanking Primer Mutation Rescue",
    description="Detects rs771794429 [G>A] in vWA 5' primer binding footprint and restores heterozygous genotype.",
    status_code=status.HTTP_200_OK,
)
@router.post(
    "/rescue-vwa",
    response_model=FlankingRescueReport,
    include_in_schema=False,
    status_code=status.HTTP_200_OK,
)
async def rescue_flanking_primer_mutation(body: FlankingRescueRequest) -> FlankingRescueReport:
    try:
        return SyntenicLinkageGuard.rescue_vwa_african_primer_mutation(
            body.sample_id,
            body.observed_sequences,
            body.apparent_ce_call
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Flanking rescue failed: {str(exc)}"
        )


@router.post(
    "/filter-stutter",
    response_model=MPSSignalFilterResult,
    summary="Analytical Threshold & PCR Stutter Filter",
    description="Filters sub-threshold reads (AT = 5.0% total coverage) and discriminates reverse isometric stutters.",
    status_code=status.HTTP_200_OK,
)
async def filter_stutter_artifacts(body: FilterStutterRequest) -> MPSSignalFilterResult:
    try:
        return MPSSignalFilter.filter_stutter_and_at(
            body.reads,
            body.analytical_threshold_ratio,
            body.stutter_threshold_ratio
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Signal filter failed: {str(exc)}"
        )


@router.get(
    "/locus-registry",
    summary="25-Autosomal STR Locus Registry",
    description="Returns the full 25-autosomal STR multiplex specification and expected diversity parameters.",
    status_code=status.HTTP_200_OK,
)
async def get_locus_registry() -> List[Dict[str, Any]]:
    return [item.model_dump() for item in AUTOSOMAL_25_LOCI_REGISTRY.values()]


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
