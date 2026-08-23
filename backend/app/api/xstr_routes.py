"""
FORENZA X-STR Linkage & Familial Kinship API Router (Module 2.2).
Standards Compliance: ISO/IEC 17025:2017, ISFG Recommendations on X-STR Testing (2012),
ENFSI Evaluative Reporting (2017).

Research Source: research/pillar_2_lineage_kinship_research.md §2.1 & §2.2.

Endpoints:
  POST /forensic/lineage/xstr/evaluate-kinship     — Complex female kinship evaluation (PHS, Duo, PGM-GD, MS)
  POST /forensic/lineage/xstr/kosambi-map          — Kosambi mapping function (cM -> r)
  POST /forensic/lineage/xstr/kosambi-recombination— Kosambi mapping alias
  GET  /forensic/lineage/xstr/panel-metadata       — Argus X-12 12-locus & 4 linkage groups metadata
  GET  /forensic/lineage/xstr/linkage-groups       — 4 Linkage Groups (LG1–LG4) details
  GET  /forensic/lineage/xstr/population-frequencies— Tillmar et al. (2017) population frequencies
  GET  /forensic/lineage/xstr/gold-standards       — Certified multi-omic reference standards
  GET  /forensic/lineage/xstr/casework-cohorts     — Certified casework benchmark cohorts
  GET  /forensic/lineage/xstr/reporting-disclaimer — ISFG (2012) evaluative reporting disclaimer
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status

from node.services.forensic.xstr.xstr_mathematical_formulation import (
    XStrMathematicalFormulation,
    ARGUS_X12_MASTER_REGISTRY,
    ARGUS_X12_LINKAGE_GROUPS,
    KinshipRelationshipType,
)
from node.services.forensic.xstr.xstr_reference_datasets import (
    XStrReferenceDatasets,
    XStrPopulationGroup,
    XSTR_POPULATION_METADATA,
    XSTR_POPULATION_FREQUENCIES,
    XSTR_GOLD_STANDARDS,
    XSTR_CASEWORK_COHORTS,
)
from node.services.forensic.xstr.xstr_cross_validation import (
    XStrCrossValidationEngine,
)
from .xstr_schemas import (
    XSTRKinshipRequest,
    XSTRKinshipResponse,
    LinkageGroupResultSchema,
    KosambiRequest,
    KosambiResponse,
    ArgusX12PanelMetadataResponse,
    LinkageGroupMetadataSchema,
    XSTRLocusMetadataSchema,
    XStrPopulationMetadataSchema,
    XStrGoldStandardSchema,
    XStrCaseworkCohortSchema,
)

router = APIRouter(
    prefix="/forensic/lineage/xstr",
    tags=["X-STR Linkage & Female Kinship Forensics (Module 2.2)"],
)


# ── 1. Kinship Evaluation ───────────────────────────────────────────────────

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
        # Extract profiles from either schema format
        p1_id = "PERSON_A"
        p2_id = "PERSON_B"
        p1_is_male = body.sex_a.upper() in ["MALE", "M", "XY"]
        p2_is_male = body.sex_b.upper() in ["MALE", "M", "XY"]
        raw_a: Dict[str, Any] = {}
        raw_b: Dict[str, Any] = {}

        if body.profile1 is not None and body.profile2 is not None:
            p1_id = body.profile1.profile_id
            p2_id = body.profile2.profile_id
            p1_is_male = body.profile1.is_male
            p2_is_male = body.profile2.is_male
            for k, v in body.profile1.loci.items():
                if hasattr(v, "allele1"):
                    raw_a[k] = [v.allele1] if v.allele2 is None else [v.allele1, v.allele2]
                else:
                    raw_a[k] = v
            for k, v in body.profile2.loci.items():
                if hasattr(v, "allele1"):
                    raw_b[k] = [v.allele1] if v.allele2 is None else [v.allele1, v.allele2]
                else:
                    raw_b[k] = v
        elif body.profile_a is not None and body.profile_b is not None:
            raw_a = body.profile_a
            raw_b = body.profile_b
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Either (profile1, profile2) or (profile_a, profile_b) must be supplied.",
            )

        # Normalize relationship type
        rel_str = body.relationship.upper().replace("-", "_").replace(" ", "_")
        rel_type = KinshipRelationshipType.PATERNAL_HALF_SISTERS
        for rel in KinshipRelationshipType:
            if rel.value == rel_str or rel.name == rel_str:
                rel_type = rel
                break
        if rel_str == "PGM_GD":
            rel_type = KinshipRelationshipType.PATERNAL_GRANDMOTHER_GRANDDAUGHTER

        # Population frequency formatting
        freq_map: Optional[Dict[str, Dict[float, float]]] = None
        if body.population_frequencies:
            freq_map = {}
            for loc, val in body.population_frequencies.items():
                if isinstance(val, (int, float)):
                    # Uniform single frequency override
                    freq_map[loc] = {float(a): float(val) for a in [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0, 33.0, 34.0]}
                elif isinstance(val, dict):
                    freq_map[loc] = {float(k): float(v) for k, v in val.items()}
        else:
            freq_map = XSTR_POPULATION_FREQUENCIES

        custom_r_dict: Optional[Dict[str, float]] = None
        if body.custom_intra_r is not None:
            custom_r_dict = {loc: body.custom_intra_r for loc in ARGUS_X12_MASTER_REGISTRY}

        res = XStrMathematicalFormulation.evaluate_xstr_kinship(
            profile_a=raw_a,
            profile_b=raw_b,
            sex_a="MALE" if p1_is_male else "FEMALE",
            sex_b="MALE" if p2_is_male else "FEMALE",
            relationship=rel_type,
            person_a_id=p1_id,
            person_b_id=p2_id,
            custom_recombination_rates=custom_r_dict,
            population_frequencies=freq_map,
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"X-STR input validation error: {str(exc)}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal X-STR computation error: {str(exc)}",
        )

    lg_schema_list = [
        LinkageGroupResultSchema(
            group_id=g.group_id,
            chromosomal_band=g.chromosomal_band,
            evaluated_loci=g.loci_evaluated,
            locus_ki_values={l.locus_name: l.ki_locus for l in g.locus_results},
            recombination_rates=[l.recombination_fraction_r for l in g.locus_results],
            group_ki=g.ki_group,
            log10_group_ki=g.log10_ki_group,
        )
        for g in res.linkage_group_results.values()
    ]

    return XSTRKinshipResponse(
        profile1_id=res.person_a_id,
        profile2_id=res.person_b_id,
        profile1_male=p1_is_male,
        profile2_male=p2_is_male,
        relationship_tested=res.relationship_type.value,
        combined_ki_x=res.combined_ki,
        log10_combined_ki_x=res.log10_combined_ki,
        evaluated_loci_count=res.total_loci_evaluated,
        evaluated_clusters_count=len(res.linkage_group_results),
        linkage_group_results=lg_schema_list,
        is_excluded=not res.is_kinship_supported,
        kinship_verdict=res.verbal_predicate_en,
        verbal_predicate_en=res.verbal_predicate_en,
        verbal_predicate_tr=res.verbal_predicate_tr,
        prosecutors_fallacy_shield=res.prosecutors_fallacy_shield,
    )


# ── 2. Kosambi Mapping Functions ─────────────────────────────────────────────

@router.post(
    "/kosambi-map",
    response_model=KosambiResponse,
    summary="Kosambi Mapping Function (cM to r)",
    description="Transforms genetic distance d (cM) into recombination fraction r using r = 0.5 * tanh(2d/100). (Research §2.1)",
    status_code=status.HTTP_200_OK,
)
async def compute_kosambi(body: KosambiRequest) -> KosambiResponse:
    try:
        r = XStrMathematicalFormulation.kosambi_map(body.genetic_distance_cm)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Kosambi validation error: {str(exc)}",
        )
    return KosambiResponse(
        genetic_distance_cm=body.genetic_distance_cm,
        recombination_fraction_r=round(r, 6),
        formula="r = 0.5 * tanh(2d / 100)",
    )


@router.post(
    "/kosambi-recombination",
    response_model=KosambiResponse,
    summary="Kosambi Recombination Fraction Calculation",
    status_code=status.HTTP_200_OK,
)
async def compute_kosambi_recombination(body: KosambiRequest) -> KosambiResponse:
    return await compute_kosambi(body)


# ── 3. Panel Metadata & Linkage Groups ───────────────────────────────────────

@router.get(
    "/panel-metadata",
    response_model=ArgusX12PanelMetadataResponse,
    summary="Argus X-12 12-Locus Panel & Linkage Groups Metadata",
    status_code=status.HTTP_200_OK,
)
async def get_panel_metadata() -> ArgusX12PanelMetadataResponse:
    lg_list = [
        LinkageGroupMetadataSchema(
            group_id=meta.group_id,
            chromosomal_band=meta.chromosomal_band,
            loci=list(meta.loci),
            recombination_rates=[meta.r_1_2, meta.r_2_3],
            genetic_distances_cm=[meta.genetic_start_cm, meta.genetic_end_cm],
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
            intra_cluster_r=meta.intra_cluster_r_to_next,
        )
        for meta in ARGUS_X12_MASTER_REGISTRY.values()
    ]

    return ArgusX12PanelMetadataResponse(
        panel_name="Investigator Argus X-12 (Qiagen)",
        total_loci=12,
        total_linkage_groups=4,
        linkage_groups=lg_list,
        loci=loci_list,
    )


@router.get(
    "/linkage-groups",
    response_model=List[LinkageGroupMetadataSchema],
    summary="List Argus X-12 4 Linkage Groups (LG1–LG4)",
    status_code=status.HTTP_200_OK,
)
async def list_linkage_groups() -> List[LinkageGroupMetadataSchema]:
    return [
        LinkageGroupMetadataSchema(
            group_id=meta.group_id,
            chromosomal_band=meta.chromosomal_band,
            loci=list(meta.loci),
            recombination_rates=[meta.r_1_2, meta.r_2_3],
            genetic_distances_cm=[meta.genetic_start_cm, meta.genetic_end_cm],
        )
        for meta in ARGUS_X12_LINKAGE_GROUPS.values()
    ]


@router.get(
    "/population-frequencies",
    summary="Tillmar et al. (2017) Population Allele Frequencies",
    status_code=status.HTTP_200_OK,
)
async def get_population_frequencies() -> Dict[str, Any]:
    return {
        "dataset": "Tillmar et al. (2017) Argus X-12 European Frequencies",
        "frequencies": XSTR_POPULATION_FREQUENCIES,
    }


@router.get(
    "/gold-standards",
    response_model=List[XStrGoldStandardSchema],
    summary="Certified Multi-Omic Reference Standards",
    status_code=status.HTTP_200_OK,
)
async def list_gold_standards() -> List[XStrGoldStandardSchema]:
    return [
        XStrGoldStandardSchema(
            sample_id=g.sample_id,
            coriell_id=g.coriell_id,
            nist_designation=g.nist_designation,
            sex=g.sex,
            population=g.population,
            description=g.description,
            x_str_genotypes=g.x_str_genotypes,
        )
        for g in XStrReferenceDatasets.list_gold_standards()
    ]


@router.get(
    "/casework-cohorts",
    response_model=List[XStrCaseworkCohortSchema],
    summary="Certified Casework Benchmark Cohorts",
    status_code=status.HTTP_200_OK,
)
async def list_casework_cohorts() -> List[XStrCaseworkCohortSchema]:
    return [
        XStrCaseworkCohortSchema(
            cohort_id=c.cohort_id,
            name=c.name,
            relationship=c.relationship,
            sex_a=c.sex_a,
            sex_b=c.sex_b,
            description=c.description,
            expected_matching_loci=c.expected_matching_loci,
            expected_min_ki=c.expected_min_ki,
            profile_a=c.profile_a,
            profile_b=c.profile_b,
        )
        for c in XStrReferenceDatasets.list_casework_cohorts()
    ]


@router.get(
    "/reporting-disclaimer",
    summary="ISFG (2012) X-STR Evaluative Reporting Disclaimer",
    status_code=status.HTTP_200_OK,
)
async def get_reporting_disclaimer() -> Dict[str, Any]:
    return XStrCrossValidationEngine.get_isfg_xstr_reporting_shield()
