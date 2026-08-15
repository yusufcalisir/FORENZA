"""
FORENZA X-STR Linkage & Familial Kinship API Router (Module 07).

Exposes endpoints for Investigator Argus X-12 X-chromosomal forensics (Pillar 2 §2):
  POST /forensic/lineage/xstr/evaluate-kinship — Complex female kinship evaluation (PHS, Duo, PGM-GD, MS)
  POST /forensic/lineage/xstr/kosambi-map       — Kosambi map function (cM -> r)
  GET  /forensic/lineage/xstr/panel-metadata   — Argus X-12 12-locus & 4 linkage groups metadata
"""

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.dna.xstr_engine import (
    XSTREngine,
    XSTRGenotype,
    XSTRProfile,
    ARGUS_X12_LINKAGE_GROUPS,
    ARGUS_X12_LOCI,
)
from .xstr_schemas import (
    XSTRKinshipRequest, XSTRKinshipResponse,
    LinkageGroupResultSchema,
    KosambiRequest, KosambiResponse,
    ArgusX12PanelMetadataResponse,
    LinkageGroupMetadataSchema,
    XSTRLocusMetadataSchema,
)

router = APIRouter(
    prefix="/forensic/lineage/xstr",
    tags=["X-STR Linkage & Female Kinship Forensics (Module 07)"],
)

_xstr_engine = XSTREngine()


# ── Kinship Evaluation ───────────────────────────────────────────────────────

@router.post(
    "/evaluate-kinship",
    response_model=XSTRKinshipResponse,
    summary="Argus X-12 Complex Female Kinship Evaluation",
    description=(
        "Evaluates X-chromosomal Likelihood Ratios (KI_X) across 4 linkage groups "
        "for PHS, Father-Daughter, PGM-GD, Mother-Son, or Full Sisters. (Research §2.2)"
    ),
    status_code=status.HTTP_200_OK,
)
async def evaluate_xstr_kinship(body: XSTRKinshipRequest) -> XSTRKinshipResponse:
    try:
        p1_loci = {
            k: XSTRGenotype(locus=v.locus, allele1=v.allele1, allele2=v.allele2)
            for k, v in body.profile1.loci.items()
        }
        p2_loci = {
            k: XSTRGenotype(locus=v.locus, allele1=v.allele1, allele2=v.allele2)
            for k, v in body.profile2.loci.items()
        }

        p1 = XSTRProfile(profile_id=body.profile1.profile_id, is_male=body.profile1.is_male, loci=p1_loci)
        p2 = XSTRProfile(profile_id=body.profile2.profile_id, is_male=body.profile2.is_male, loci=p2_loci)

        res = _xstr_engine.evaluate_xstr_kinship(
            profile1=p1,
            profile2=p2,
            relationship=body.relationship,
            population_frequencies=body.population_frequencies,
            custom_intra_r=body.custom_intra_r,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"X-STR kinship evaluation failed: {str(exc)}",
        )

    return XSTRKinshipResponse(
        profile1_id=res.profile1_id,
        profile2_id=res.profile2_id,
        profile1_male=res.profile1_male,
        profile2_male=res.profile2_male,
        relationship_tested=res.relationship_tested,
        combined_ki_x=res.combined_ki_x,
        log10_combined_ki_x=res.log10_combined_ki_x,
        evaluated_loci_count=res.evaluated_loci_count,
        evaluated_clusters_count=res.evaluated_clusters_count,
        linkage_group_results=[
            LinkageGroupResultSchema(
                group_id=lg.group_id,
                chromosomal_band=lg.chromosomal_band,
                evaluated_loci=lg.evaluated_loci,
                locus_ki_values=lg.locus_ki_values,
                recombination_rates=lg.recombination_rates,
                group_ki=lg.group_ki,
                log10_group_ki=lg.log10_group_ki,
            )
            for lg in res.linkage_group_results
        ],
        is_excluded=res.is_excluded,
        kinship_verdict=res.kinship_verdict,
        prosecutors_fallacy_shield=res.prosecutors_fallacy_shield,
    )


# ── Kosambi Mapping Function ─────────────────────────────────────────────────

@router.post(
    "/kosambi-map",
    response_model=KosambiResponse,
    summary="Kosambi Mapping Function (cM to r)",
    description="Transforms genetic distance d (cM) into recombination fraction r using r = 0.5 * tanh(2d/100). (Research §2.1)",
    status_code=status.HTTP_200_OK,
)
async def compute_kosambi(body: KosambiRequest) -> KosambiResponse:
    try:
        r = _xstr_engine.kosambi_map_function(body.genetic_distance_cm)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Kosambi calculation failed: {str(exc)}",
        )
    return KosambiResponse(
        genetic_distance_cm=body.genetic_distance_cm,
        recombination_fraction_r=round(r, 6),
        formula="r = 0.5 * tanh(2d / 100)",
    )


# ── Panel Metadata ───────────────────────────────────────────────────────────

@router.get(
    "/panel-metadata",
    response_model=ArgusX12PanelMetadataResponse,
    summary="Argus X-12 12-Locus Panel & Linkage Groups Metadata",
    description="Returns all 12 loci, chromosomal bands, physical positions, map distances, and linkage groups. (Research §2.1)",
    status_code=status.HTTP_200_OK,
)
async def get_panel_metadata() -> ArgusX12PanelMetadataResponse:
    lg_list = [
        LinkageGroupMetadataSchema(
            group_id=meta.group_id,
            chromosomal_band=meta.chromosomal_band,
            loci=meta.loci,
            recombination_rates=meta.recombination_rates,
            genetic_distances_cm=meta.genetic_distances_cm,
        )
        for meta in ARGUS_X12_LINKAGE_GROUPS.values()
    ]
    loci_list = [
        XSTRLocusMetadataSchema(
            locus_name=meta.locus_name,
            linkage_group=meta.linkage_group,
            chromosomal_band=meta.chromosomal_band,
            physical_position_mb=meta.physical_position_mb,
            genetic_map_cm=meta.genetic_map_cm,
            intra_cluster_r=meta.intra_cluster_r,
        )
        for meta in ARGUS_X12_LOCI.values()
    ]
    return ArgusX12PanelMetadataResponse(
        panel_name="Investigator Argus X-12 Linkage Multiplex",
        total_loci=len(loci_list),
        total_linkage_groups=len(lg_list),
        linkage_groups=lg_list,
        loci=loci_list,
    )
