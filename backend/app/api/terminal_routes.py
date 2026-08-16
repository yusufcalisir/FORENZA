"""
FastAPI Router for Forensic DNA & SNP Terminal Ingestion & Quality Engine
Routes: /api/v1/forensic/terminal/*
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List

try:
    from backend.app.api.terminal_schemas import (
        IngestTerminalFileRequest,
        IngestTerminalFileResponse,
        LocusSTRCallSchema,
        SnpGenotypeCallSchema,
        TerminalPopGenRequest,
        TerminalPopGenResponse,
        TerminalSexDeterminationRequest,
        TerminalSexDeterminationResponse,
        TerminalQualityAssessmentRequest,
        TerminalQualityAssessmentResponse,
        TerminalBgaRequest,
        ContinentalPosteriorDetail,
        TerminalBgaResponse,
        TerminalHIrisPlexRequest,
        TerminalHIrisPlexResponse,
        TerminalComprehensiveRequest,
        TerminalComprehensiveResponse,
    )
    from backend.node.services.forensic.terminal.dna_terminal_parser import (
        DnaTerminalParser,
        ParsedForensicProfile,
        LocusSTRCall,
        SnpGenotypeCall,
    )
    from backend.node.services.forensic.terminal.snp_phenotype_bga_engine import (
        SnpPhenotypeBgaEngine,
        ContinentalCluster,
        CONTINENTAL_COORDINATES,
    )
except ImportError:
    from app.api.terminal_schemas import (
        IngestTerminalFileRequest,
        IngestTerminalFileResponse,
        LocusSTRCallSchema,
        SnpGenotypeCallSchema,
        TerminalPopGenRequest,
        TerminalPopGenResponse,
        TerminalSexDeterminationRequest,
        TerminalSexDeterminationResponse,
        TerminalQualityAssessmentRequest,
        TerminalQualityAssessmentResponse,
        TerminalBgaRequest,
        ContinentalPosteriorDetail,
        TerminalBgaResponse,
        TerminalHIrisPlexRequest,
        TerminalHIrisPlexResponse,
        TerminalComprehensiveRequest,
        TerminalComprehensiveResponse,
    )
    from node.services.forensic.terminal.dna_terminal_parser import (
        DnaTerminalParser,
        ParsedForensicProfile,
        LocusSTRCall,
        SnpGenotypeCall,
    )
    from node.services.forensic.terminal.snp_phenotype_bga_engine import (
        SnpPhenotypeBgaEngine,
        ContinentalCluster,
        CONTINENTAL_COORDINATES,
    )

router = APIRouter(prefix="/forensic/terminal", tags=["Forensic DNA & SNP Terminal"])


@router.post("/parse", response_model=IngestTerminalFileResponse, summary="Parse Multi-Format Forensic Profile File")
def parse_forensic_file(req: IngestTerminalFileRequest) -> IngestTerminalFileResponse:
    """
    Parses GeneMapper ID-X CSV/TSV, CODIS CMF 3.2 XML, Forensic NGS VCF 4.2, or ISO 17025 LIMS JSON.
    """
    content = req.file_content.strip()
    fmt = req.file_format.lower() if req.file_format else "auto"

    try:
        if fmt in ("codis_xml", "xml") or content.startswith("<?xml") or "<CODIS" in content:
            profile = DnaTerminalParser.parse_codis_xml(content)
        elif fmt in ("ngs_vcf", "vcf") or content.startswith("##fileformat=VCF"):
            profile = DnaTerminalParser.parse_ngs_vcf(content)
        elif fmt in ("lims_json", "json") or content.startswith("{"):
            profile = DnaTerminalParser.parse_lims_json(content)
        else:
            # Default to GeneMapper CSV/TSV
            profile = DnaTerminalParser.parse_genemapper(content)

        if req.sample_id_override:
            profile.sample_id = req.sample_id_override

        str_dict = {
            k: LocusSTRCallSchema(
                locus_name=v.locus_name,
                allele1=v.allele1,
                allele2=v.allele2,
                rfu1=v.rfu1,
                rfu2=v.rfu2,
                size1=v.size1,
                size2=v.size2,
                is_homozygous=v.is_homozygous,
                is_dropout=v.is_dropout,
                is_imbalanced=v.is_imbalanced,
                heterozygote_balance=v.heterozygote_balance,
            )
            for k, v in profile.str_profile.items()
        }

        snp_dict = {
            k: SnpGenotypeCallSchema(
                rsid=v.rsid,
                genotype=v.genotype,
                gene=v.gene,
                dosage_value=v.dosage_value,
                trait=v.trait,
                read_depth=v.read_depth,
            )
            for k, v in profile.snp_profile.items()
        }

        return IngestTerminalFileResponse(
            sample_id=profile.sample_id,
            detected_format=profile.raw_source_format,
            chain_of_custody_hash=profile.chain_of_custody_hash or "",
            str_marker_count=len(str_dict),
            snp_marker_count=len(snp_dict),
            str_profile=str_dict,
            snp_profile=snp_dict,
            supplementary_markers=profile.supplementary_markers,
            laboratory_ori=profile.laboratory_ori,
            operator_id=profile.operator_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse forensic file: {str(e)}"
        )


@router.post("/popgen-probability", response_model=TerminalPopGenResponse, summary="Compute NRC II Bounded Match Probability")
def calculate_popgen_probability(req: TerminalPopGenRequest) -> TerminalPopGenResponse:
    """
    Computes subpopulation match probabilities with NRC II Rule 4.1 lower bound (p_min = 5 / 2072 ≈ 0.00241313)
    and Balding-Nichols coancestry correction.
    """
    try:
        str_profile: Dict[str, LocusSTRCall] = {}
        for locus_name, call_dict in req.str_profile.items():
            a1 = str(call_dict.get("allele1", ""))
            a2 = str(call_dict.get("allele2", a1)) if call_dict.get("allele2") is not None else a1
            rfu1 = float(call_dict.get("rfu1", 1000.0))
            rfu2 = float(call_dict.get("rfu2", rfu1)) if call_dict.get("rfu2") is not None else rfu1
            is_homo = (a1 == a2)
            is_drop = bool(call_dict.get("is_dropout", False)) or a1 in ("[0]", "0") or a2 in ("[0]", "0")

            str_profile[locus_name] = LocusSTRCall(
                locus_name=locus_name,
                allele1=a1,
                allele2=a2,
                rfu1=rfu1,
                rfu2=rfu2,
                is_homozygous=is_homo,
                is_dropout=is_drop,
            )

        parsed = ParsedForensicProfile(
            sample_id="API_PROFILE",
            raw_source_format="API_JSON",
            str_profile=str_profile,
        )

        res = DnaTerminalParser.calculate_popgen_match_probability(parsed, population=req.population, theta=req.theta)
        return TerminalPopGenResponse(
            population=res.population,
            coancestry_theta=res.coancestry_theta,
            minimum_allele_freq_pmin=res.minimum_allele_freq_pmin,
            locus_match_probabilities=res.locus_match_probabilities,
            combined_match_probability=res.combined_match_probability,
            random_match_probability_reciprocal=res.random_match_probability_reciprocal,
            log10_lr=res.log10_lr,
            enfsi_verbal_scale=res.enfsi_verbal_scale,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"PopGen calculation error: {str(e)}"
        )


@router.post("/sex-determination", response_model=TerminalSexDeterminationResponse, summary="Amelogenin Y-Null & Aneuploidy Detection")
def determine_sex_configuration(req: TerminalSexDeterminationRequest) -> TerminalSexDeterminationResponse:
    """
    Evaluates Amelogenin, DYS391, and SRY signals to determine chromosomal sex and detect Y-null deletions.
    """
    str_profile = {
        "Amelogenin": LocusSTRCall(
            locus_name="Amelogenin",
            allele1=req.amelogenin_allele1,
            allele2=req.amelogenin_allele2,
            rfu1=req.amelogenin_rfu1,
            rfu2=req.amelogenin_rfu2,
        )
    }
    supplementary = {}
    if req.dys391_signal:
        supplementary["DYS391"] = req.dys391_signal
    if req.sry_status:
        supplementary["SRY"] = req.sry_status

    profile = ParsedForensicProfile(
        sample_id="API_PROFILE",
        raw_source_format="API_JSON",
        str_profile=str_profile,
        supplementary_markers=supplementary,
    )

    res = DnaTerminalParser.validate_sex_and_aneuploidy(profile)
    return TerminalSexDeterminationResponse(
        amelogenin_call=res.amelogenin_call,
        dys391_signal=res.dys391_signal,
        sry_status=res.sry_status,
        ystr_signal_present=res.ystr_signal_present,
        sex_classification=res.sex_classification.value,
        prior_y_null_prob_sas=res.prior_y_null_prob_sas,
        prior_y_null_prob_eur=res.prior_y_null_prob_eur,
        operational_action=res.operational_action,
    )


@router.post("/quality-assessment", response_model=TerminalQualityAssessmentResponse, summary="Assess EPG Quality & Stochastic Thresholds")
def assess_profile_quality(req: TerminalQualityAssessmentRequest) -> TerminalQualityAssessmentResponse:
    """
    Assesses AT (50 RFU), ST (200 RFU), Hb (>= 0.60), and Degradation Index (DI).
    """
    str_profile: Dict[str, LocusSTRCall] = {}
    for locus_name, call_dict in req.str_profile.items():
        a1 = str(call_dict.get("allele1", ""))
        a2 = str(call_dict.get("allele2", a1)) if call_dict.get("allele2") is not None else a1
        rfu1 = float(call_dict.get("rfu1", 0.0))
        rfu2 = float(call_dict.get("rfu2", rfu1)) if call_dict.get("rfu2") is not None else rfu1
        is_homo = (a1 == a2)
        is_drop = bool(call_dict.get("is_dropout", False)) or a1 in ("[0]", "0") or a2 in ("[0]", "0")
        hb = min(rfu1, rfu2) / max(rfu1, rfu2) if max(rfu1, rfu2) > 0 and not is_homo else None

        str_profile[locus_name] = LocusSTRCall(
            locus_name=locus_name,
            allele1=a1,
            allele2=a2,
            rfu1=rfu1,
            rfu2=rfu2,
            is_homozygous=is_homo,
            is_dropout=is_drop,
            heterozygote_balance=hb,
        )

    profile = ParsedForensicProfile(
        sample_id="API_PROFILE",
        raw_source_format="API_JSON",
        str_profile=str_profile,
    )

    qc = DnaTerminalParser.assess_quality_and_stochastic_gates(profile)
    return TerminalQualityAssessmentResponse(
        passed_qc=qc.passed_qc,
        analytical_threshold_rfu=qc.analytical_threshold_rfu,
        stochastic_threshold_rfu=qc.stochastic_threshold_rfu,
        heterozygote_balance_threshold=qc.heterozygote_balance_threshold,
        total_loci_count=qc.total_loci_count,
        dropout_loci_count=qc.dropout_loci_count,
        imbalanced_loci_count=qc.imbalanced_loci_count,
        degradation_index=qc.degradation_index,
        degradation_severity=qc.degradation_severity,
        stochastic_mixture_flag=qc.stochastic_mixture_flag,
        recommendations=qc.recommendations,
    )


@router.post("/bga", response_model=TerminalBgaResponse, summary="55-SNP AIM Biogeographic Ancestry & Centroid")
def calculate_bga_ancestry(req: TerminalBgaRequest) -> TerminalBgaResponse:
    """
    Computes 7-continental posterior probabilities, WGS84 geographic centroid, and R_95% dispersion ellipse.
    """
    res = SnpPhenotypeBgaEngine.calculate_bga_posteriors(req.sample_id, req.genotype_dosages)
    breakdown = [
        ContinentalPosteriorDetail(
            cluster_code=cluster.value,
            cluster_name=CONTINENTAL_COORDINATES[cluster].name,
            posterior_probability=prob,
            reference_latitude=CONTINENTAL_COORDINATES[cluster].latitude,
            reference_longitude=CONTINENTAL_COORDINATES[cluster].longitude,
        )
        for cluster, prob in res.continental_posteriors.items()
    ]

    return TerminalBgaResponse(
        sample_id=res.sample_id,
        dominant_ancestry=res.dominant_ancestry.value,
        dominant_ancestry_label=res.dominant_ancestry_label,
        dominant_probability=res.dominant_probability,
        centroid_latitude=res.centroid_latitude,
        centroid_longitude=res.centroid_longitude,
        spatial_variance_lat=res.spatial_variance_lat,
        spatial_variance_lon=res.spatial_variance_lon,
        spatial_covariance=res.spatial_covariance,
        lambda_max=res.lambda_max,
        r95_confidence_radius_km=res.r95_confidence_radius_km,
        num_snps_utilized=res.num_snps_utilized,
        continental_breakdown=breakdown,
    )


@router.post("/hirisplex", response_model=TerminalHIrisPlexResponse, summary="41-SNP HIrisPlex-S Softmax MLR Pigmentation")
def calculate_hirisplex_pigmentation(req: TerminalHIrisPlexRequest) -> TerminalHIrisPlexResponse:
    """
    Executes HIrisPlex-S Softmax MLR for Eye (3-class), Hair (4-class + MC1R epistasis), and Skin (5-class).
    """
    res = SnpPhenotypeBgaEngine.calculate_hirisplex_phenotypes(req.sample_id, req.genotype_dosages)
    return TerminalHIrisPlexResponse(
        sample_id=res.sample_id,
        predicted_eye_color=res.predicted_eye_color,
        eye_color_probabilities=res.eye_color_probabilities,
        predicted_hair_color=res.predicted_hair_color,
        hair_color_probabilities=res.hair_color_probabilities,
        mc1r_red_hair_epistasis_flag=res.mc1r_red_hair_epistasis_flag,
        predicted_skin_phototype=res.predicted_skin_phototype,
        skin_phototype_probabilities=res.skin_phototype_probabilities,
        num_hirisplex_snps_evaluated=res.num_hirisplex_snps_evaluated,
    )


@router.post("/comprehensive", response_model=TerminalComprehensiveResponse, summary="Unified Comprehensive Forensic Profile Analysis")
def run_comprehensive_terminal_analysis(req: TerminalComprehensiveRequest) -> TerminalComprehensiveResponse:
    """
    Performs unified analysis: STR Ingestion + PopGen + Sex Determination + EPG QC + 55-SNP AIM BGA + 41-SNP HIrisPlex-S.
    """
    profile_obj = None
    if req.file_content:
        content = req.file_content.strip()
        if content.startswith("<?xml") or "<CODIS" in content:
            profile_obj = DnaTerminalParser.parse_codis_xml(content)
        elif content.startswith("##fileformat=VCF"):
            profile_obj = DnaTerminalParser.parse_ngs_vcf(content)
        elif content.startswith("{"):
            profile_obj = DnaTerminalParser.parse_lims_json(content)
        else:
            profile_obj = DnaTerminalParser.parse_genemapper(content)

    sample_id = profile_obj.sample_id if profile_obj else "COMPREHENSIVE_SAMPLE"
    coc_hash = profile_obj.chain_of_custody_hash if profile_obj else ""

    # Build STR dict
    str_dict: Dict[str, Dict[str, Any]] = {}
    if profile_obj:
        for k, v in profile_obj.str_profile.items():
            str_dict[k] = {
                "allele1": v.allele1,
                "allele2": v.allele2,
                "rfu1": v.rfu1,
                "rfu2": v.rfu2,
                "is_dropout": v.is_dropout,
            }
    elif req.str_profile:
        str_dict = req.str_profile

    # PopGen
    popgen_res = calculate_popgen_probability(TerminalPopGenRequest(
        str_profile=str_dict,
        population=req.population,
        theta=req.theta,
    ))

    # Sex Determination
    amel = str_dict.get("Amelogenin", {})
    dys391 = profile_obj.supplementary_markers.get("DYS391") if profile_obj else None
    sry = profile_obj.supplementary_markers.get("SRY") if profile_obj else None

    sex_res = determine_sex_configuration(TerminalSexDeterminationRequest(
        amelogenin_allele1=str(amel.get("allele1", "X")),
        amelogenin_allele2=str(amel.get("allele2", "Y")) if amel.get("allele2") is not None else None,
        amelogenin_rfu1=float(amel.get("rfu1", 1500.0)),
        amelogenin_rfu2=float(amel.get("rfu2", 1450.0)),
        dys391_signal=dys391,
        sry_status=sry,
    ))

    # QC
    qc_res = assess_profile_quality(TerminalQualityAssessmentRequest(str_profile=str_dict))

    # Build SNP dosages
    snp_dosages: Dict[str, int] = {}
    if profile_obj:
        for rsid, call in profile_obj.snp_profile.items():
            snp_dosages[rsid] = call.dosage_value
    if req.snp_dosages:
        snp_dosages.update(req.snp_dosages)

    # BGA
    bga_res = calculate_bga_ancestry(TerminalBgaRequest(
        sample_id=sample_id,
        genotype_dosages=snp_dosages,
    ))

    # HIrisPlex
    hiris_res = calculate_hirisplex_pigmentation(TerminalHIrisPlexRequest(
        sample_id=sample_id,
        genotype_dosages=snp_dosages,
    ))

    return TerminalComprehensiveResponse(
        sample_id=sample_id,
        chain_of_custody_hash=coc_hash or "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        popgen=popgen_res,
        sex=sex_res,
        qc=qc_res,
        bga=bga_res,
        hirisplex=hiris_res,
    )


