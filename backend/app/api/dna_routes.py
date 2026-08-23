"""
FORENZA Lineage DNA API Router.
Exposes endpoints for Y-STR paternal haplotype matching and mtDNA maternal sequence alignment
under the /forensic/dna prefix.
"""

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.dna.ystr import YSTREngine, YSTRHaplotype
from node.services.forensic.dna.mtdna import MtDnaEngine, MtDnaProfile, MtDnaVariant
from .dna_schemas import (
    YSTRMatchRequest, YSTRMatchResponse,
    MtDnaMatchRequest, MtDnaMatchResponse
)

router = APIRouter(prefix="/forensic/dna", tags=["Expanded Lineage DNA Forensics"])

_ystr_engine = YSTREngine()
_mtdna_engine = MtDnaEngine()


@router.post(
    "/ystr",
    response_model=YSTRMatchResponse,
    summary="Y-STR Paternal Haplotype Match",
    description="Evaluates 23-locus Y-STR haplotype matching and computes SWGDAM 95% Clopper-Pearson upper bound frequency.",
    status_code=status.HTTP_200_OK,
)
async def evaluate_ystr_match(body: YSTRMatchRequest) -> YSTRMatchResponse:
    try:
        ev_hap = YSTRHaplotype(haplotype_id=body.evidence_id, markers=body.evidence_markers)
        sus_hap = YSTRHaplotype(haplotype_id=body.suspect_id, markers=body.suspect_markers)

        res = _ystr_engine.evaluate_ystr_match(
            evidence=ev_hap,
            suspect=sus_hap,
            database_count=body.database_count,
            database_size_n=body.database_size_n
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Y-STR match evaluation failed: {str(exc)}"
        )

    return YSTRMatchResponse(
        evidence_id=res.evidence_id,
        suspect_id=res.suspect_id,
        matching_loci_count=res.matching_loci_count,
        evaluated_loci_count=res.evaluated_loci_count,
        haplotype_match_status=res.haplotype_match_status,
        database_count=res.database_count,
        database_size_n=res.database_size_n,
        haplotype_frequency_estimate=res.haplotype_frequency_estimate,
        upper_bound_95_ci=res.upper_bound_95_ci,
        paternal_lineage_verdict=res.paternal_lineage_verdict
    )


@router.post(
    "/mtdna",
    response_model=MtDnaMatchResponse,
    summary="mtDNA Maternal Lineage Sequence Alignment",
    description="Aligns HV1/HV2/HV3 sequence variants against rCRS reference and evaluates maternal origin.",
    status_code=status.HTTP_200_OK,
)
async def evaluate_mtdna_match(body: MtDnaMatchRequest) -> MtDnaMatchResponse:
    try:
        ev_vars = [MtDnaVariant(v.position, v.ref_allele, v.alt_allele, v.region) for v in body.evidence_variants]
        sus_vars = [MtDnaVariant(v.position, v.ref_allele, v.alt_allele, v.region) for v in body.suspect_variants]

        ev_prof = MtDnaProfile(profile_id=body.evidence_id, haplogroup=None, variants=ev_vars)
        sus_prof = MtDnaProfile(profile_id=body.suspect_id, haplogroup=None, variants=sus_vars)

        res = _mtdna_engine.evaluate_mtdna_match(ev_prof, sus_prof)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"mtDNA match evaluation failed: {str(exc)}"
        )

    return MtDnaMatchResponse(
        evidence_id=res.evidence_id,
        suspect_id=res.suspect_id,
        evidence_rcrs=res.evidence_rcrs,
        suspect_rcrs=res.suspect_rcrs,
        differing_positions_count=res.differing_positions_count,
        match_status=res.match_status,
        maternal_lineage_verdict=res.maternal_lineage_verdict
    )
