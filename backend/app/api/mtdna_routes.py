"""
FORENZA Mitochondrial DNA (mtDNA) Forensics API Router (Module 2.3).
Standards Compliance: ISO/IEC 17025:2017, ISFG Recommendations on Forensic mtDNA Testing (2014, 2020),
SWGDAM Interpretation Guidelines for Mitochondrial DNA Analysis.

Research Source: research/ystr_27_mtdna_empop_lineage_research.md §3 & §4.

Endpoints:
  POST /forensic/lineage/mtdna/evaluate-maternal-match — Pairwise maternal lineage match evaluation
  POST /forensic/lineage/mtdna/evaluate-kinship        — Alias for maternal match evaluation
  POST /forensic/lineage/mtdna/empop-upper-bound       — Clopper-Pearson 95% upper bound for EMPOP
  POST /forensic/lineage/mtdna/database-frequency      — Alias for EMPOP frequency bounds
  POST /forensic/lineage/mtdna/predict-haplogroup      — PhyloTree 17 haplogroup classification
  GET  /forensic/lineage/mtdna/panel-metadata         — rCRS Control Region (HV1/HV2/HV3) and ISFG rules
  GET  /forensic/lineage/mtdna/reference-metadata     — Alias for reference metadata
  GET  /forensic/lineage/mtdna/control-region-domains — 7 D-Loop functional domains
  GET  /forensic/lineage/mtdna/gold-standards         — Certified multi-omic reference standards
  GET  /forensic/lineage/mtdna/casework-cohorts        — Certified casework benchmark cohorts
  GET  /forensic/lineage/mtdna/reporting-disclaimer   — ISFG (2020) mtDNA evaluative reporting disclaimer
"""

import math
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status

from node.services.forensic.mtdna.mtdna_mathematical_formulation import (
    MtDnaMathematicalFormulation,
    MtDnaVariant,
    MTDNA_CONTROL_REGION_DOMAINS,
    MTDNA_IUPAC_CODES,
    PhyloTreeHaplogroupPredictor,
)
from node.services.forensic.mtdna.mtdna_reference_datasets import (
    MtDnaReferenceDatasets,
    MtDnaPopulationGroup,
    MTDNA_EMPOP_METADATA,
    MTDNA_GOLD_STANDARDS,
    MTDNA_CASEWORK_COHORTS,
)
from node.services.forensic.mtdna.mtdna_cross_validation import (
    MtDnaCrossValidationEngine,
)
from .mtdna_schemas import (
    MtDNAMatchRequest,
    MtDNAMatchResponse,
    EMPOPProbabilityRequest,
    EMPOPProbabilityResponse,
    MtDNAPanelMetadataResponse,
    HypervariableRegionSchema,
    MtDnaGoldStandardSchema,
    MtDnaCaseworkCohortSchema,
)

router = APIRouter(
    prefix="/forensic/lineage/mtdna",
    tags=["mtDNA Control Region Forensics & EMPOP (Module 2.3)"],
)


# ── 1. Maternal Match Evaluation ─────────────────────────────────────────────

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
        p1_id = "SAMPLE_1"
        p2_id = "SAMPLE_2"
        vars_a: List[MtDnaVariant] = []
        vars_b: List[MtDnaVariant] = []

        if body.evidence is not None and body.suspect is not None:
            p1_id = body.evidence.profile_id
            p2_id = body.suspect.profile_id
            for v in body.evidence.variants:
                if isinstance(v, str):
                    vars_a.append(MtDnaMathematicalFormulation.parse_variant_string(v))
                else:
                    vars_a.append(
                        MtDnaVariant(
                            position=v.position,
                            ref_base=v.ref_base,
                            variant_base=v.alt_base,
                            variant_type=v.variant_type,
                            insertion_index=v.insertion_index,
                            raw_notation=v.notation or "",
                        )
                    )
            for v in body.suspect.variants:
                if isinstance(v, str):
                    vars_b.append(MtDnaMathematicalFormulation.parse_variant_string(v))
                else:
                    vars_b.append(
                        MtDnaVariant(
                            position=v.position,
                            ref_base=v.ref_base,
                            variant_base=v.alt_base,
                            variant_type=v.variant_type,
                            insertion_index=v.insertion_index,
                            raw_notation=v.notation or "",
                        )
                    )
        elif body.variants_a is not None and body.variants_b is not None:
            vars_a = [MtDnaMathematicalFormulation.parse_variant_string(s) for s in body.variants_a]
            vars_b = [MtDnaMathematicalFormulation.parse_variant_string(s) for s in body.variants_b]
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Either (evidence, suspect) or (variants_a, variants_b) must be provided.",
            )

        res = MtDnaMathematicalFormulation.evaluate_pairwise_lineage(
            variants_a=vars_a,
            variants_b=vars_b,
            profile_a_id=p1_id,
            profile_b_id=p2_id,
            database_size_n=body.n_empop,
            observed_database_matches_k=body.empop_observed_k,
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"mtDNA variant parsing error: {str(exc)}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"mtDNA evaluation failed: {str(exc)}",
        )

    # Legacy match_status string compatibility
    if res.verdict == "MATCH":
        m_status = "CANNOT_BE_EXCLUDED"
    elif res.verdict == "INCONCLUSIVE":
        m_status = "INCONCLUSIVE"
    else:
        m_status = "EXCLUDED"

    empop_str1 = " ".join([v.formatted_call for v in vars_a])
    empop_str2 = " ".join([v.formatted_call for v in vars_b])

    # Extract point heteroplasmies detected
    php_list = [v.formatted_call for v in vars_a + vars_b if v.variant_type == "PHP"]

    return MtDNAMatchResponse(
        sample1_id=res.profile_a_id,
        sample2_id=res.profile_b_id,
        sample1_empop_string=empop_str1,
        sample2_empop_string=empop_str2,
        shared_variants=res.shared_variants,
        sample1_unique_variants=res.differences_a_only,
        sample2_unique_variants=res.differences_b_only,
        point_heteroplasmies_detected=php_list,
        differing_positions_count=res.homoplasmic_differences_count,
        match_status=m_status,
        empop_frequency_bound=res.database_upper_bound_p,
        maternal_lr=res.maternal_lr,
        log10_maternal_lr=res.log10_maternal_lr,
        maternal_lineage_verdict=res.verbal_predicate_en,
        predicted_haplogroup_a=res.predicted_haplogroup_a,
        predicted_haplogroup_b=res.predicted_haplogroup_b,
        verbal_predicate_en=res.verbal_predicate_en,
        verbal_predicate_tr=res.verbal_predicate_tr,
        prosecutors_fallacy_shield=res.prosecutors_fallacy_shield,
    )


@router.post(
    "/evaluate-kinship",
    response_model=MtDNAMatchResponse,
    summary="Evaluate Maternal Kinship",
    status_code=status.HTTP_200_OK,
)
async def evaluate_kinship(body: MtDNAMatchRequest) -> MtDNAMatchResponse:
    return await evaluate_maternal_match(body)


# ── 2. EMPOP Database Frequency Upper Bounds ─────────────────────────────────

@router.post(
    "/empop-upper-bound",
    response_model=EMPOPProbabilityResponse,
    summary="Exact Clopper-Pearson 95% Binomial Upper Bound",
    description="Calculates p_upper = 1 - (alpha)^(1/(N+1)) for unobserved haplotypes and maternal LR.",
    status_code=status.HTTP_200_OK,
)
async def compute_empop_upper_bound(body: EMPOPProbabilityRequest) -> EMPOPProbabilityResponse:
    try:
        p_up = MtDnaMathematicalFormulation.compute_clopper_pearson_bound(
            k=body.k,
            n=body.n_empop,
            alpha=body.alpha,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"EMPOP calculation error: {str(exc)}",
        )
    lr = 1.0 / p_up if p_up > 0.0 else 1e9
    log_lr = math.log10(lr) if lr > 0.0 else 0.0

    return EMPOPProbabilityResponse(
        observed_count_k=body.k,
        database_size_n=body.n_empop,
        alpha=body.alpha,
        p_upper_bound=round(p_up, 7),
        maternal_lr=round(lr, 4),
        log10_maternal_lr=round(log_lr, 4),
        is_unobserved=(body.k == 0),
        formula="p_upper = 1 - (alpha)^(1 / (N + 1))" if body.k == 0 else "Snedecor F / Beta Binomial Upper Bound",
    )


@router.post(
    "/database-frequency",
    response_model=EMPOPProbabilityResponse,
    summary="Compute EMPOP Database Frequency",
    status_code=status.HTTP_200_OK,
)
async def compute_database_frequency(body: EMPOPProbabilityRequest) -> EMPOPProbabilityResponse:
    return await compute_empop_upper_bound(body)


# ── 3. Panel Metadata & Reference Catalogs ───────────────────────────────────

@router.get(
    "/panel-metadata",
    response_model=MtDNAPanelMetadataResponse,
    summary="rCRS Control Region (HV1/HV2/HV3) and ISFG Rules Metadata",
    status_code=status.HTTP_200_OK,
)
async def get_panel_metadata() -> MtDNAPanelMetadataResponse:
    regions = [
        HypervariableRegionSchema(
            name="HV1",
            start_pos=16024,
            end_pos=16365,
            total_bases=342,
            key_homopolymeric_tracts=["HV1 Poly-C (16184-16193)"],
        ),
        HypervariableRegionSchema(
            name="HV2",
            start_pos=73,
            end_pos=340,
            total_bases=268,
            key_homopolymeric_tracts=["HV2 Poly-C (303-315)"],
        ),
        HypervariableRegionSchema(
            name="HV3",
            start_pos=438,
            end_pos=574,
            total_bases=137,
            key_homopolymeric_tracts=["HV3 Dinucleotide AC (522-524)"],
        ),
    ]

    return MtDNAPanelMetadataResponse(
        reference_genome="Revised Cambridge Reference Sequence (rCRS)",
        genbank_accession="NC_012920.1",
        hypervariable_regions=regions,
        supported_iupac_codes={
            "R": "A or G (Purine)",
            "Y": "C or T (Pyrimidine)",
            "M": "A or C (Amino)",
            "K": "G or T (Keto)",
            "S": "G or C (Strong)",
            "W": "A or T (Weak)",
        },
        isfg_rules_active=True,
    )


@router.get(
    "/reference-metadata",
    response_model=MtDNAPanelMetadataResponse,
    summary="Alias for Panel Reference Metadata",
    status_code=status.HTTP_200_OK,
)
async def get_reference_metadata() -> MtDNAPanelMetadataResponse:
    return await get_panel_metadata()


@router.get(
    "/control-region-domains",
    summary="List 7 D-Loop Control Region Functional Domains",
    status_code=status.HTTP_200_OK,
)
async def list_control_region_domains() -> Dict[str, Any]:
    return {
        "reference_sequence": "rCRS (NC_012920.1)",
        "domains": [
            {
                "domain_id": d.domain_id,
                "name": d.name,
                "start_pos": d.start_pos,
                "end_pos": d.end_pos,
                "length_bp": d.end_pos - d.start_pos + 1 if d.end_pos >= d.start_pos else (16569 - d.start_pos + d.end_pos + 1),
                "description": d.description,
            }
            for d in MTDNA_CONTROL_REGION_DOMAINS.values()
        ],
    }


@router.get(
    "/gold-standards",
    response_model=List[MtDnaGoldStandardSchema],
    summary="Certified Multi-Omic Reference Standards",
    status_code=status.HTTP_200_OK,
)
async def list_gold_standards() -> List[MtDnaGoldStandardSchema]:
    return [
        MtDnaGoldStandardSchema(
            sample_id=g.sample_id,
            coriell_id=g.coriell_id,
            nist_designation=g.nist_designation,
            haplogroup=g.haplogroup,
            population=g.population,
            description=g.description,
            variants=g.variants,
        )
        for g in MtDnaReferenceDatasets.list_gold_standards()
    ]


@router.get(
    "/casework-cohorts",
    response_model=List[MtDnaCaseworkCohortSchema],
    summary="Certified Casework Benchmark Cohorts",
    status_code=status.HTTP_200_OK,
)
async def list_casework_cohorts() -> List[MtDnaCaseworkCohortSchema]:
    return [
        MtDnaCaseworkCohortSchema(
            cohort_id=c.cohort_id,
            name=c.name,
            relationship=c.relationship,
            description=c.description,
            expected_verdict=c.expected_verdict,
            expected_matches_k=c.expected_matches_k,
            database_size_n=c.database_size_n,
            expected_min_lr=c.expected_min_lr,
            profile_a_variants=c.profile_a_variants,
            profile_b_variants=c.profile_b_variants,
        )
        for c in MtDnaReferenceDatasets.list_casework_cohorts()
    ]


@router.get(
    "/reporting-disclaimer",
    summary="ISFG (2020) mtDNA Evaluative Reporting Disclaimer",
    status_code=status.HTTP_200_OK,
)
async def get_reporting_disclaimer() -> Dict[str, Any]:
    return MtDnaCrossValidationEngine.get_isfg_mtdna_reporting_shield()
