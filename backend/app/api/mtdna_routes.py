"""
FORENZA Mitochondrial DNA (mtDNA) Forensics API Router (Module 08).

Exposes endpoints for mtDNA Control Region Forensics (Pillar 2 §3):
  POST /forensic/lineage/mtdna/evaluate-maternal-match — Pairwise maternal lineage match evaluation
  POST /forensic/lineage/mtdna/empop-upper-bound        — Clopper-Pearson 95% upper bound for EMPOP
  GET  /forensic/lineage/mtdna/panel-metadata          — rCRS Control Region (HV1/HV2/HV3) and ISFG rules
"""

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.dna.mtdna_engine import (
    MtDNAEngine,
    MtDNAVariant,
    MtDNAProfile,
    HV1_RANGE,
    HV2_RANGE,
    HV3_RANGE,
    IUPAC_HETEROPLASMY_MAP,
)
from .mtdna_schemas import (
    MtDNAMatchRequest, MtDNAMatchResponse,
    EMPOPProbabilityRequest, EMPOPProbabilityResponse,
    MtDNAPanelMetadataResponse, HypervariableRegionSchema,
)

router = APIRouter(
    prefix="/forensic/lineage/mtdna",
    tags=["mtDNA Control Region Forensics & EMPOP (Module 08)"],
)

_mtdna_engine = MtDNAEngine()


# ── Maternal Match Evaluation ────────────────────────────────────────────────

@router.post(
    "/evaluate-maternal-match",
    response_model=MtDNAMatchResponse,
    summary="mtDNA Pairwise Maternal Match Evaluation",
    description=(
        "Evaluates pairwise mtDNA sequence concordance between questioned and reference samples "
        "across HV1, HV2, and HV3 with ISFG right-alignment, IUPAC heteroplasmy, and EMPOP bounds. (Research §3.2)"
    ),
    status_code=status.HTTP_200_OK,
)
async def evaluate_maternal_match(body: MtDNAMatchRequest) -> MtDNAMatchResponse:
    try:
        ev_variants = [
            MtDNAVariant(
                position=v.position,
                ref_base=v.ref_base,
                alt_base=v.alt_base,
                region=v.region or "",
                variant_type=v.variant_type,
                insertion_index=v.insertion_index,
                notation=v.notation or "",
            )
            for v in body.evidence.variants
        ]
        sus_variants = [
            MtDNAVariant(
                position=v.position,
                ref_base=v.ref_base,
                alt_base=v.alt_base,
                region=v.region or "",
                variant_type=v.variant_type,
                insertion_index=v.insertion_index,
                notation=v.notation or "",
            )
            for v in body.suspect.variants
        ]

        p_ev = MtDNAProfile(profile_id=body.evidence.profile_id, haplogroup=body.evidence.haplogroup, variants=ev_variants)
        p_sus = MtDNAProfile(profile_id=body.suspect.profile_id, haplogroup=body.suspect.haplogroup, variants=sus_variants)

        res = _mtdna_engine.evaluate_mtdna_maternal_match(
            evidence=p_ev,
            suspect=p_sus,
            n_empop=body.n_empop,
            empop_observed_k=body.empop_observed_k,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"mtDNA maternal match evaluation failed: {str(exc)}",
        )

    return MtDNAMatchResponse(
        sample1_id=res.sample1_id,
        sample2_id=res.sample2_id,
        sample1_empop_string=res.sample1_empop_string,
        sample2_empop_string=res.sample2_empop_string,
        shared_variants=res.shared_variants,
        sample1_unique_variants=res.sample1_unique_variants,
        sample2_unique_variants=res.sample2_unique_variants,
        point_heteroplasmies_detected=res.point_heteroplasmies_detected,
        differing_positions_count=res.differing_positions_count,
        match_status=res.match_status,
        empop_frequency_bound=res.empop_frequency_bound,
        maternal_lr=res.maternal_lr,
        log10_maternal_lr=res.log10_maternal_lr,
        maternal_lineage_verdict=res.maternal_lineage_verdict,
        prosecutors_fallacy_shield=res.prosecutors_fallacy_shield,
    )


# ── EMPOP Upper Bound ─────────────────────────────────────────────────────────

@router.post(
    "/empop-upper-bound",
    response_model=EMPOPProbabilityResponse,
    summary="EMPOP Clopper-Pearson 95% Frequency Upper Bound",
    description="Calculates exact binomial upper bound for EMPOP haplotype observation count k in database of size N. (Research §3.2)",
    status_code=status.HTTP_200_OK,
)
async def compute_empop_upper_bound(body: EMPOPProbabilityRequest) -> EMPOPProbabilityResponse:
    try:
        res = _mtdna_engine.calculate_empop_match_probability(k=body.k, n_empop=body.n_empop, alpha=body.alpha)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"EMPOP upper bound calculation failed: {str(exc)}",
        )

    formula = (
        "p_upper = 1 - alpha^(1 / (N + 1))" if body.k == 0
        else "p_upper = BetaQuantile(1 - alpha/2; k + 1, N - k)"
    )

    return EMPOPProbabilityResponse(
        observed_count_k=res.observed_count_k,
        database_size_n=res.database_size_n,
        alpha=res.alpha,
        p_upper_bound=res.p_upper_bound,
        maternal_lr=res.maternal_lr,
        log10_maternal_lr=res.log10_maternal_lr,
        is_unobserved=res.is_unobserved,
        formula=formula,
    )


# ── Panel Metadata ───────────────────────────────────────────────────────────

@router.get(
    "/panel-metadata",
    response_model=MtDNAPanelMetadataResponse,
    summary="mtDNA Control Region & ISFG Metadata",
    description="Returns hypervariable regions (HV1/HV2/HV3), rCRS reference info, and IUPAC heteroplasmy codes. (Research §3.1)",
    status_code=status.HTTP_200_OK,
)
async def get_mtdna_panel_metadata() -> MtDNAPanelMetadataResponse:
    regions = [
        HypervariableRegionSchema(
            name="HV1",
            start_pos=HV1_RANGE[0],
            end_pos=HV1_RANGE[1],
            total_bases=HV1_RANGE[1] - HV1_RANGE[0] + 1,
            key_homopolymeric_tracts=["16184-16193 Poly-C (16189 T->C)"],
        ),
        HypervariableRegionSchema(
            name="HV2",
            start_pos=HV2_RANGE[0],
            end_pos=HV2_RANGE[1],
            total_bases=HV2_RANGE[1] - HV2_RANGE[0] + 1,
            key_homopolymeric_tracts=["303-315 Poly-C (309.1C / 315.1C)"],
        ),
        HypervariableRegionSchema(
            name="HV3",
            start_pos=HV3_RANGE[0],
            end_pos=HV3_RANGE[1],
            total_bases=HV3_RANGE[1] - HV3_RANGE[0] + 1,
            key_homopolymeric_tracts=["522-523 CA Dinucleotide Repeats (522del)"],
        ),
    ]

    iupac_desc = {
        k: "/".join(sorted(v))
        for k, v in IUPAC_HETEROPLASMY_MAP.items()
        if len(v) > 1
    }

    return MtDNAPanelMetadataResponse(
        reference_genome="Revised Cambridge Reference Sequence (rCRS)",
        genbank_accession="NC_012920.1 (AC_000021.2)",
        hypervariable_regions=regions,
        supported_iupac_codes=iupac_desc,
        isfg_rules_active=True,
    )
