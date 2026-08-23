"""
FORENZA Ancient DNA & Degraded Forensic SNP Damage / Human ID (HID) API Router (Module 10).

Exposes endpoints for Ancient DNA & Degraded Skeletal Remains (Pillar 2 §5):
  POST /forensic/hid/damage-kinetics          — MapDamage post-mortem C->T deamination curve
  POST /forensic/hid/fragmentation-distribution — Exponential DNA length distribution & dropout
  POST /forensic/hid/snp-genotype-likelihood  — Low-coverage SNP GL with deamination compensation
  POST /forensic/hid/multi-snp-lr             — Multi-locus micro-multiplex SNP Likelihood Ratio
  POST /forensic/hid/skeletal-audit           — Skeletal degradation index (DI) & LCN audit
  POST /forensic/hid/evaluate-remains         — Multi-modal remains identification synthesis
"""

from fastapi import APIRouter, HTTPException, status

from node.services.forensic.hid.adna_engine import AncientDNAEngine
from node.services.forensic.hid.remains import HumanIdentificationEngine, MultiModalRemainsProfile
from node.services.forensic.models import STRGenotype, STRProfile
from .hid_schemas import (
    MapDamageRequest, MapDamageResponse,
    FragmentationDistributionRequest, FragmentationDistributionResponse,
    SNPLowCoverageGLRequest, SNPLowCoverageGLResponse,
    MultiSNPLRRequest, MultiSNPLRResponse,
    SkeletalDegradationAuditRequest, SkeletalDegradationAuditResponse,
    MultiModalRemainsRequest, MultiModalRemainsResponse,
    HumanIdentificationCandidateHitSchema,
    LegacyIdentifyRequest,
    LegacyDegradationAuditRequest, LegacyDegradationAuditResponse,
)


router = APIRouter(
    prefix="/forensic/hid",
    tags=["Ancient DNA & Degraded Forensic SNP Damage / HID (Module 10)"],
)

_adna_engine = AncientDNAEngine()
_hid_engine = HumanIdentificationEngine()


# ── MapDamage Kinetics ───────────────────────────────────────────────────────

@router.post(
    "/damage-kinetics",
    response_model=MapDamageResponse,
    summary="MapDamage Post-Mortem Deamination Kinetics",
    description="Computes position-dependent C->T deamination damage curve from 5' termini. (Research §5.1)",
    status_code=status.HTTP_200_OK,
)
async def compute_damage_kinetics(body: MapDamageRequest) -> MapDamageResponse:
    try:
        profile = _adna_engine.generate_mapdamage_profile(
            delta_0=body.delta_0,
            decay_alpha=body.decay_alpha,
            max_position=body.max_position,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"MapDamage kinetics calculation failed: {str(exc)}",
        )

    desc = (
        f"MapDamage / Briggs Model: Terminal 5' deamination delta_0={profile.delta_0}, "
        f"exponential decay alpha={profile.decay_alpha} per nucleotide distance."
    )

    return MapDamageResponse(
        delta_0=profile.delta_0,
        decay_alpha=profile.decay_alpha,
        max_position=profile.max_position,
        damage_curve=profile.damage_curve,
        model_description=desc,
    )


# ── Fragmentation Distribution ────────────────────────────────────────────────

@router.post(
    "/fragmentation-distribution",
    response_model=FragmentationDistributionResponse,
    summary="Ancient/Degraded DNA Fragmentation Length Distribution",
    description="Evaluates exponential fragment length distribution and STR dropout risk (<100 bp). (Research §5.1)",
    status_code=status.HTTP_200_OK,
)
async def compute_fragmentation(body: FragmentationDistributionRequest) -> FragmentationDistributionResponse:
    try:
        prof = _adna_engine.compute_fragmentation_distribution(
            lambda_param=body.lambda_param,
            l_min=body.l_min,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Fragmentation calculation failed: {str(exc)}",
        )

    risk_assessment = (
        f"{prof.cdf_at_100bp * 100.0:.1f}% of DNA fragments are shorter than 100 bp. "
        f"Standard multiplex STR (>150 bp) typing will experience extensive amplicon dropout. "
        f"Micro-multiplex SNP panels (40–70 bp) strongly recommended."
    )

    return FragmentationDistributionResponse(
        lambda_param=prof.lambda_param,
        l_min=prof.l_min,
        mean_length=prof.mean_length,
        median_length=prof.median_length,
        cdf_at_100bp=prof.cdf_at_100bp,
        dropout_risk_assessment=risk_assessment,
    )


# ── Low-Coverage SNP Genotype Likelihood ──────────────────────────────────────

@router.post(
    "/snp-genotype-likelihood",
    response_model=SNPLowCoverageGLResponse,
    summary="Low-Coverage SNP Genotype Likelihood (GL)",
    description="Computes damage-compensated genotype likelihoods and posteriors for a single SNP marker. (Research §5.2)",
    status_code=status.HTTP_200_OK,
)
async def compute_snp_genotype_likelihood(body: SNPLowCoverageGLRequest) -> SNPLowCoverageGLResponse:
    try:
        res = _adna_engine.compute_low_coverage_snp_likelihood(
            locus_id=body.locus_id,
            read_bases=body.read_bases,
            read_positions=body.read_positions,
            ref_allele=body.ref_allele,
            alt_allele=body.alt_allele,
            delta_0=body.delta_0,
            decay_alpha=body.decay_alpha,
            sequencing_error_rate=body.sequencing_error_rate,
            prior_genotypes=body.prior_genotypes,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"SNP Genotype Likelihood calculation failed: {str(exc)}",
        )

    return SNPLowCoverageGLResponse(
        locus_id=res.locus_id,
        ref_allele=res.ref_allele,
        alt_allele=res.alt_allele,
        read_count=res.read_count,
        raw_likelihoods=res.raw_likelihoods,
        log10_likelihoods=res.log10_likelihoods,
        posterior_probabilities=res.posterior_probabilities,
        called_genotype=res.called_genotype,
        is_damage_compensated=res.is_damage_compensated,
        deamination_risk_flag=res.deamination_risk_flag,
    )


# ── Multi-SNP Likelihood Ratio ───────────────────────────────────────────────

@router.post(
    "/multi-snp-lr",
    response_model=MultiSNPLRResponse,
    summary="Multi-Locus Micro-Multiplex SNP Likelihood Ratio",
    description="Synthesizes cumulative LR across low-coverage SNP loci under product rule. (Research §5.2)",
    status_code=status.HTTP_200_OK,
)
async def compute_multi_snp_lr(body: MultiSNPLRRequest) -> MultiSNPLRResponse:
    try:
        snp_results = []
        for snp in body.snp_observations:
            gl = _adna_engine.compute_low_coverage_snp_likelihood(
                locus_id=snp.locus_id,
                read_bases=snp.read_bases,
                read_positions=snp.read_positions,
                ref_allele=snp.ref_allele,
                alt_allele=snp.alt_allele,
                delta_0=body.delta_0,
                sequencing_error_rate=body.sequencing_error_rate,
            )
            snp_results.append(gl)

        res = _adna_engine.compute_multi_snp_lr(
            snp_results=snp_results,
            suspect_genotypes=body.suspect_genotypes,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Multi-SNP LR calculation failed: {str(exc)}",
        )

    return MultiSNPLRResponse(
        total_snps=res.total_snps,
        cumulative_lr=res.cumulative_lr,
        log10_cumulative_lr=res.log10_cumulative_lr,
        per_locus_lr=res.per_locus_lr,
        prosecutors_fallacy_shield=res.prosecutors_fallacy_shield,
    )


# ── Skeletal Degradation Audit ────────────────────────────────────────────────

@router.post(
    "/skeletal-audit",
    response_model=SkeletalDegradationAuditResponse,
    summary="Skeletal Remains PCR Degradation & LCN Audit",
    description="Audits Degradation Index (DI = RFU_small / RFU_large) and LCN stochastic risks. (Research §5.1)",
    status_code=status.HTTP_200_OK,
)
async def audit_skeletal_remains(body: SkeletalDegradationAuditRequest) -> SkeletalDegradationAuditResponse:
    try:
        res = _adna_engine.audit_skeletal_degradation(
            profile_id=body.profile_id,
            small_loci_rfu=body.small_loci_rfu,
            large_loci_rfu=body.large_loci_rfu,
            dna_input_pg=body.dna_input_pg,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Skeletal audit failed: {str(exc)}",
        )

    return SkeletalDegradationAuditResponse(
        profile_id=res.profile_id,
        degradation_index=res.degradation_index,
        small_loci_rfu=res.small_loci_rfu,
        large_loci_rfu=res.large_loci_rfu,
        dna_input_pg=res.dna_input_pg,
        is_lcn_sample=res.is_lcn_sample,
        long_amplicon_dropout_risk=res.long_amplicon_dropout_risk,
        recommended_technology=res.recommended_technology,
        stochastic_warning=res.stochastic_warning,
    )


# ── Multi-Modal Remains Evaluation (Legacy Compatible) ───────────────────────

@router.post(
    "/evaluate-remains",
    response_model=MultiModalRemainsResponse,
    summary="Multi-Modal Unidentified Remains Evaluation",
    description="Synthesizes STR, Y-STR, mtDNA, and SNP evidence for unknown human remains.",
    status_code=status.HTTP_200_OK,
)
async def evaluate_multimodal_remains(body: MultiModalRemainsRequest) -> MultiModalRemainsResponse:
    try:
        str_prof = None
        if body.str_profile:
            loci_dict = {
                k: STRGenotype(locus_name=v.locus_name, allele1=v.allele1, allele2=v.allele2)
                for k, v in body.str_profile.loci.items()
            }
            str_prof = STRProfile(profile_id=body.str_profile.profile_id, loci=loci_dict, population_group=body.str_profile.population_group or "Caucasian")

        remains = MultiModalRemainsProfile(
            remains_id=body.remains_id,
            sample_type=body.sample_type,
            str_profile=str_prof,
            ystr_markers=body.ystr_markers,
            mtdna_variants=body.mtdna_variants,
            snp_profile=body.snp_profile,
        )

        cand_db = []
        for c in body.candidate_db:
            c_loci = {
                k: STRGenotype(locus_name=v.locus_name or v.locus or k, allele1=v.allele1, allele2=v.allele2)
                for k, v in c.loci.items()
            }
            cand_db.append(STRProfile(profile_id=c.profile_id, loci=c_loci, population_group=c.population_group or "Caucasian"))

        res = _hid_engine.identify_unknown_remains(
            remains=remains,
            candidate_db=cand_db,
            prior_probability=body.prior_probability,
            top_k=body.top_k,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Remains evaluation failed: {str(exc)}",
        )

    hits = [
        HumanIdentificationCandidateHitSchema(
            candidate_id=h.candidate_id,
            lr_str=h.lr_str,
            lr_ystr=h.lr_ystr,
            lr_mtdna=h.lr_mtdna,
            lr_snp=h.lr_snp,
            joint_lr=h.joint_lr,
            log10_joint_lr=h.log10_joint_lr,
            posterior_probability=h.posterior_probability,
            identification_verdict=h.identification_verdict,
        )
        for h in res.top_candidate_hits
    ]

    return MultiModalRemainsResponse(
        remains_id=res.remains_id,
        sample_type=res.sample_type,
        evaluated_candidates_count=res.evaluated_candidates_count,
        top_candidate_hits=hits,
        hid_summary=res.hid_summary,
    )


@router.post(
    "/identify",
    response_model=MultiModalRemainsResponse,
    summary="Multi-Modal Unidentified Remains Identification (Legacy Compatible)",
    status_code=status.HTTP_200_OK,
)
async def identify_legacy_remains(body: LegacyIdentifyRequest) -> MultiModalRemainsResponse:
    try:
        str_prof = None
        if body.remains.str_profile:
            loci_dict = {
                k: STRGenotype(locus_name=v.locus_name or v.locus or k, allele1=v.allele1, allele2=v.allele2)
                for k, v in body.remains.str_profile.loci.items()
            }
            str_prof = STRProfile(profile_id=body.remains.str_profile.profile_id, loci=loci_dict, population_group=body.remains.str_profile.population_group or "Caucasian")

        remains = MultiModalRemainsProfile(
            remains_id=body.remains.remains_id,
            sample_type=body.remains.sample_type,
            str_profile=str_prof,
            ystr_markers=body.remains.ystr_markers,
            mtdna_variants=body.remains.mtdna_variants,
            snp_profile=body.remains.snp_profile,
        )

        cand_db = []
        for c in body.candidate_db:
            c_loci = {
                k: STRGenotype(locus_name=v.locus_name or v.locus or k, allele1=v.allele1, allele2=v.allele2)
                for k, v in c.loci.items()
            }
            cand_db.append(STRProfile(profile_id=c.profile_id, loci=c_loci, population_group=c.population_group or "Caucasian"))

        res = _hid_engine.identify_unknown_remains(
            remains=remains,
            candidate_db=cand_db,
            prior_probability=body.prior_probability,
            top_k=body.top_k,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Remains identification failed: {str(exc)}",
        )

    hits = [
        HumanIdentificationCandidateHitSchema(
            candidate_id=h.candidate_id,
            lr_str=h.lr_str,
            lr_ystr=h.lr_ystr,
            lr_mtdna=h.lr_mtdna,
            lr_snp=h.lr_snp,
            joint_lr=h.joint_lr,
            log10_joint_lr=h.log10_joint_lr,
            posterior_probability=h.posterior_probability,
            identification_verdict=h.identification_verdict,
        )
        for h in res.top_candidate_hits
    ]

    return MultiModalRemainsResponse(
        remains_id=res.remains_id,
        sample_type=res.sample_type,
        evaluated_candidates_count=res.evaluated_candidates_count,
        top_candidate_hits=hits,
        hid_summary=res.hid_summary,
    )


@router.post(
    "/degradation-audit",
    response_model=LegacyDegradationAuditResponse,
    summary="Skeletal Degradation Audit (Legacy Compatible)",
    status_code=status.HTTP_200_OK,
)
async def audit_legacy_degradation(body: LegacyDegradationAuditRequest) -> LegacyDegradationAuditResponse:
    try:
        from node.services.forensic.hid.degradation import SkeletalDegradationEvaluator
        evaluator = SkeletalDegradationEvaluator()

        loci_dict = {
            k: STRGenotype(locus_name=v.locus_name or v.locus or k, allele1=v.allele1, allele2=v.allele2)
            for k, v in body.profile.loci.items()
        }
        str_prof = STRProfile(profile_id=body.profile.profile_id, loci=loci_dict, population_group=body.profile.population_group or "Caucasian")

        res = evaluator.audit_skeletal_profile(str_prof, mean_rfu=body.mean_rfu)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Degradation audit failed: {str(exc)}",
        )

    return LegacyDegradationAuditResponse(
        profile_id=res.profile_id,
        degradation_index=res.degradation_index,
        long_loci_dropout_risk=res.long_loci_dropout_risk,
        is_lcn_sample=res.is_lcn_sample,
        stochastic_warning=res.stochastic_warning,
        recommended_amplification_strategy=res.recommended_amplification_strategy,
    )

