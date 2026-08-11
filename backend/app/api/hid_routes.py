"""
FORENZA Human Identification (HID) API Router.
Exposes endpoints for Unknown Remains Identification and Skeletal Degradation Auditing
under the /forensic/hid prefix.
"""

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.models import STRGenotype, STRProfile
from node.services.forensic.hid.remains import HumanIdentificationEngine, MultiModalRemainsProfile
from node.services.forensic.hid.degradation import SkeletalDegradationEvaluator
from .dvi_routes import _convert_schema_to_domain
from .hid_schemas import (
    HumanIdentifyRequest, HumanIdentifyResponse,
    DegradationAuditRequest, DegradationAuditResponse,
    HumanCandidateHitSchema
)

router = APIRouter(prefix="/forensic/hid", tags=["Human Identification (HID) & Skeletal Remains"])

_hid_engine = HumanIdentificationEngine()
_degradation_evaluator = SkeletalDegradationEvaluator()


@router.post(
    "/identify",
    response_model=HumanIdentifyResponse,
    summary="Multi-Modal Unknown Remains Identification",
    description="Synthesizes Autosomal STR, Y-STR, mtDNA, and SNP evidence to rank candidate database matches using joint product LR.",
    status_code=status.HTTP_200_OK,
)
async def identify_unknown_remains(body: HumanIdentifyRequest) -> HumanIdentifyResponse:
    try:
        str_prof = _convert_schema_to_domain(body.remains.str_profile) if body.remains.str_profile else None

        remains_dom = MultiModalRemainsProfile(
            remains_id=body.remains.remains_id,
            sample_type=body.remains.sample_type,
            str_profile=str_prof,
            ystr_markers=body.remains.ystr_markers,
            mtdna_variants=body.remains.mtdna_variants,
            snp_profile=body.remains.snp_profile
        )

        cand_dom = [_convert_schema_to_domain(c) for c in body.candidate_db]

        res = _hid_engine.identify_unknown_remains(
            remains=remains_dom,
            candidate_db=cand_dom,
            prior_probability=body.prior_probability,
            top_k=body.top_k
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Human identification calculation failed: {str(exc)}"
        )

    return HumanIdentifyResponse(
        remains_id=res.remains_id,
        sample_type=res.sample_type,
        evaluated_candidates_count=res.evaluated_candidates_count,
        top_candidate_hits=[
            HumanCandidateHitSchema(
                candidate_id=h.candidate_id,
                lr_str=h.lr_str,
                lr_ystr=h.lr_ystr,
                lr_mtdna=h.lr_mtdna,
                lr_snp=h.lr_snp,
                joint_lr=h.joint_lr,
                log10_joint_lr=h.log10_joint_lr,
                posterior_probability=h.posterior_probability,
                identification_verdict=h.identification_verdict
            )
            for h in res.top_candidate_hits
        ],
        hid_summary=res.hid_summary
    )


@router.post(
    "/degradation-audit",
    response_model=DegradationAuditResponse,
    summary="Skeletal Sample Degradation & LCN Audit",
    description="Audits amplicon length degradation index and LCN PCR stochastic threshold risks for bone fragments.",
    status_code=status.HTTP_200_OK,
)
async def audit_skeletal_degradation(body: DegradationAuditRequest) -> DegradationAuditResponse:
    try:
        prof_dom = _convert_schema_to_domain(body.profile)
        res = _degradation_evaluator.audit_skeletal_profile(prof_dom, mean_rfu=body.mean_rfu)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Skeletal degradation audit failed: {str(exc)}"
        )

    return DegradationAuditResponse(
        profile_id=res.profile_id,
        degradation_index=res.degradation_index,
        long_loci_dropout_risk=res.long_loci_dropout_risk,
        is_lcn_sample=res.is_lcn_sample,
        stochastic_warning=res.stochastic_warning,
        recommended_amplification_strategy=res.recommended_amplification_strategy
    )
