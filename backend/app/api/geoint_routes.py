"""
FastAPI Router for Geo-Forensic Intelligence (Pillar 7) — Modules 1.1, 1.2, 2.1, 2.2 & 3.1.
Includes dual import resilience for local dev and production Docker/Render environments.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Optional, List

try:
    from backend.app.api.geoint_schemas import (
        MultiIsotopeProvenanceRequest,
        MultiIsotopeProvenanceResponse,
        CandidateRegionDto,
        SoilComparisonRequest,
        SoilComparisonResponse,
        PalynologyEdnaAnalysisRequest,
        PalynologyEdnaAnalysisResponse,
        CrimeIncidentInput,
        GeographicProfileRequest,
        GeographicProfileResponse,
        EvidenceLayerWeightInput,
        GeoEvidenceFusionRequest,
        FusedSpatialHotspotDto,
        GeoEvidenceFusionResponse,
    )
    from backend.node.services.forensic.geoint.isoscape_provenance_engine import (
        IsoscapeProvenanceEngine,
        IsotopeObservation,
        TissueType,
    )
    from backend.node.services.forensic.geoint.soil_mineralogy_engine import (
        SoilMineralogyEngine,
        SoilMineralogyProfile,
    )
    from backend.node.services.forensic.geoint.palynology_edna_engine import (
        PalynologyEdnaEngine,
        PalynologyProfile,
        EdnaMicrobiomeProfile,
    )
    from backend.node.services.forensic.geoint.geographic_profiling_engine import (
        GeographicProfilingEngine,
        CrimeSitePoint,
        OffenderMobilityTypology,
    )
    from backend.node.services.forensic.geoint.geo_fusion_engine import (
        GeoFusionEngine,
        EvidenceLayerInput,
        SpatialHotspot,
        EvidenceFusionResult,
    )
except ImportError:
    try:
        from app.api.geoint_schemas import (
            MultiIsotopeProvenanceRequest,
            MultiIsotopeProvenanceResponse,
            CandidateRegionDto,
            SoilComparisonRequest,
            SoilComparisonResponse,
            PalynologyEdnaAnalysisRequest,
            PalynologyEdnaAnalysisResponse,
            CrimeIncidentInput,
            GeographicProfileRequest,
            GeographicProfileResponse,
            EvidenceLayerWeightInput,
            GeoEvidenceFusionRequest,
            FusedSpatialHotspotDto,
            GeoEvidenceFusionResponse,
        )
        from node.services.forensic.geoint.isoscape_provenance_engine import (
            IsoscapeProvenanceEngine,
            IsotopeObservation,
            TissueType,
        )
        from node.services.forensic.geoint.soil_mineralogy_engine import (
            SoilMineralogyEngine,
            SoilMineralogyProfile,
        )
        from node.services.forensic.geoint.palynology_edna_engine import (
            PalynologyEdnaEngine,
            PalynologyProfile,
            EdnaMicrobiomeProfile,
        )
        from node.services.forensic.geoint.geographic_profiling_engine import (
            GeographicProfilingEngine,
            CrimeSitePoint,
            OffenderMobilityTypology,
        )
        from node.services.forensic.geoint.geo_fusion_engine import (
            GeoFusionEngine,
            EvidenceLayerInput,
            SpatialHotspot,
            EvidenceFusionResult,
        )
    except ImportError:
        from .geoint_schemas import (
            MultiIsotopeProvenanceRequest,
            MultiIsotopeProvenanceResponse,
            CandidateRegionDto,
            SoilComparisonRequest,
            SoilComparisonResponse,
            PalynologyEdnaAnalysisRequest,
            PalynologyEdnaAnalysisResponse,
            CrimeIncidentInput,
            GeographicProfileRequest,
            GeographicProfileResponse,
            EvidenceLayerWeightInput,
            GeoEvidenceFusionRequest,
            FusedSpatialHotspotDto,
            GeoEvidenceFusionResponse,
        )
        from ...node.services.forensic.geoint.isoscape_provenance_engine import (
            IsoscapeProvenanceEngine,
            IsotopeObservation,
            TissueType,
        )
        from ...node.services.forensic.geoint.soil_mineralogy_engine import (
            SoilMineralogyEngine,
            SoilMineralogyProfile,
        )
        from ...node.services.forensic.geoint.palynology_edna_engine import (
            PalynologyEdnaEngine,
            PalynologyProfile,
            EdnaMicrobiomeProfile,
        )
        from ...node.services.forensic.geoint.geographic_profiling_engine import (
            GeographicProfilingEngine,
            CrimeSitePoint,
            OffenderMobilityTypology,
        )
        from ...node.services.forensic.geoint.geo_fusion_engine import (
            GeoFusionEngine,
            EvidenceLayerInput,
            SpatialHotspot,
            EvidenceFusionResult,
        )


router = APIRouter(
    prefix="/forensic/geoint",
    tags=["Geo-Forensic Intelligence"],
)

_ISOSCAPE_ENGINE = IsoscapeProvenanceEngine()
_SOIL_ENGINE = SoilMineralogyEngine()
_PALYNO_ENGINE = PalynologyEdnaEngine()
_GEOPROF_ENGINE = GeographicProfilingEngine()
_FUSION_ENGINE = GeoFusionEngine()


# ── Module 1.1: Multi-Isotope Provenance Endpoint ─────────────────────────────

@router.post(
    "/isoscape-provenance",
    response_model=MultiIsotopeProvenanceResponse,
    status_code=status.HTTP_200_OK,
    summary="Multi-Isotope Biogeochemical Spatial Provenancing (Pillar 7 §1)",
    description=(
        "Ingests multi-tissue stable (H, O, C, N) and radiogenic (Sr, Pb) isotope observations. "
        "Applies biological fractionation transformations (Daux/Chenery enamel, Ehleringer keratin) "
        "and evaluates continuous multivariate Gaussian likelihood across spatial isoscapes "
        "to resolve geographic origin centroids, 95% spatial confidence radius, and ISO/IEC 17025 ENFSI likelihood ratios."
    ),
)
async def evaluate_isoscape_provenance(
    request: MultiIsotopeProvenanceRequest,
) -> MultiIsotopeProvenanceResponse:
    try:
        primary_tissue = TissueType(request.primary_measurements.sample_tissue)
        primary_obs = IsotopeObservation(
            sample_id=request.sample_id,
            tissue_type=primary_tissue,
            delta_18o_permil=request.primary_measurements.delta_18o_permil,
            delta_2h_permil=request.primary_measurements.delta_2h_permil,
            sr_87_86_ratio=request.primary_measurements.sr_87_86_ratio,
            delta_13c_permil=request.primary_measurements.delta_13c_permil,
            delta_15n_permil=request.primary_measurements.delta_15n_permil,
            pb_206_207_ratio=request.primary_measurements.pb_206_207_ratio,
        )

        secondary_obs: Optional[IsotopeObservation] = None
        if request.secondary_measurements is not None:
            secondary_tissue = TissueType(request.secondary_measurements.sample_tissue)
            secondary_obs = IsotopeObservation(
                sample_id=f"{request.sample_id}_secondary",
                tissue_type=secondary_tissue,
                delta_18o_permil=request.secondary_measurements.delta_18o_permil,
                delta_2h_permil=request.secondary_measurements.delta_2h_permil,
                sr_87_86_ratio=request.secondary_measurements.sr_87_86_ratio,
                delta_13c_permil=request.secondary_measurements.delta_13c_permil,
                delta_15n_permil=request.secondary_measurements.delta_15n_permil,
                pb_206_207_ratio=request.secondary_measurements.pb_206_207_ratio,
            )

        result = _ISOSCAPE_ENGINE.solve_spatial_provenance(
            primary_obs=primary_obs,
            secondary_obs=secondary_obs,
        )

        top_candidates = [
            CandidateRegionDto(
                region_id=r["region_id"],
                name=r["name"],
                country=r["country"],
                latitude=r["latitude"],
                longitude=r["longitude"],
                posterior_probability=r["posterior_probability"],
                isoscape_d18o_mean=r["isoscape_d18o_mean"],
                isoscape_sr_87_86_mean=r["isoscape_sr_87_86_mean"],
            )
            for r in result.top_candidate_regions
        ]

        return MultiIsotopeProvenanceResponse(
            case_id=request.case_id,
            sample_id=request.sample_id,
            inferred_drinking_water_d18o=result.inferred_drinking_water_d18o,
            inferred_drinking_water_d18o_sigma=result.inferred_drinking_water_d18o_sigma,
            inferred_drinking_water_d2h=result.inferred_drinking_water_d2h,
            inferred_drinking_water_d2h_sigma=result.inferred_drinking_water_d2h_sigma,
            deuterium_excess_permil=result.deuterium_excess_permil,
            measured_sr_87_86=result.measured_sr_87_86,
            resolved_centroid_lat=result.resolved_centroid_lat,
            resolved_centroid_lon=result.resolved_centroid_lon,
            confidence_radius_95_km=result.confidence_radius_95_km,
            likelihood_ratio=result.likelihood_ratio,
            primary_candidate_region=result.primary_candidate_region,
            top_candidate_regions=top_candidates,
            enfsi_verbal_tier=result.enfsi_verbal_tier,
            enfsi_verbal_statement_en=result.enfsi_verbal_statement_en,
            enfsi_verbal_statement_tr=result.enfsi_verbal_statement_tr,
            prosecutors_fallacy_shield=result.prosecutors_fallacy_shield,
        )

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Mathematical or schema input error: {str(ve)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Spatial provenance calculation failed: {str(e)}",
        )


# ── Module 1.2: Soil Pedology & CoDa Comparison Endpoint ──────────────────────

@router.post(
    "/soil-comparison",
    response_model=SoilComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Forensic Soil Pedology, QXRD Mineralogy & CoDa Comparison (Pillar 7 §2)",
    description=(
        "Compares questioned and known control soil samples under ASTM E3272-21 standards. "
        "Applies Centered Log-Ratio (CLR) compositional transformations to eliminate closure bias, "
        "calculates Minimum Covariance Determinant (MCD) Robust Mahalanobis Distance, "
        "computes Hotelling F-test p-value, evaluates CIEDE2000 color difference, "
        "and renders ISO/IEC 17025 ENFSI evaluative likelihood ratios."
    ),
)
async def evaluate_soil_comparison(
    request: SoilComparisonRequest,
) -> SoilComparisonResponse:
    try:
        q_profile = SoilMineralogyProfile(
            sample_id=request.questioned_soil.sample_id,
            quartz_percent=request.questioned_soil.quartz_percent,
            feldspar_k_percent=request.questioned_soil.feldspar_k_percent,
            plagioclase_percent=request.questioned_soil.plagioclase_percent,
            calcite_percent=request.questioned_soil.calcite_percent,
            clay_kaolinite_percent=request.questioned_soil.clay_kaolinite_percent,
            clay_illite_percent=request.questioned_soil.clay_illite_percent,
            clay_smectite_percent=request.questioned_soil.clay_smectite_percent,
            dolomite_percent=request.questioned_soil.dolomite_percent,
            chlorite_percent=request.questioned_soil.chlorite_percent,
            zircon_percent=request.questioned_soil.zircon_percent,
            tourmaline_percent=request.questioned_soil.tourmaline_percent,
            rutile_percent=request.questioned_soil.rutile_percent,
            total_heavy_minerals_percent=request.questioned_soil.total_heavy_minerals_percent,
            munsell_color_dry=request.questioned_soil.munsell_color_dry,
            xrf_major_oxides_wt_pct=request.questioned_soil.xrf_major_oxides_wt_pct,
            xrf_trace_ppm=request.questioned_soil.xrf_trace_ppm,
        )

        c_profile = SoilMineralogyProfile(
            sample_id=request.known_control_soil.sample_id,
            quartz_percent=request.known_control_soil.quartz_percent,
            feldspar_k_percent=request.known_control_soil.feldspar_k_percent,
            plagioclase_percent=request.known_control_soil.plagioclase_percent,
            calcite_percent=request.known_control_soil.calcite_percent,
            clay_kaolinite_percent=request.known_control_soil.clay_kaolinite_percent,
            clay_illite_percent=request.known_control_soil.clay_illite_percent,
            clay_smectite_percent=request.known_control_soil.clay_smectite_percent,
            dolomite_percent=request.known_control_soil.dolomite_percent,
            chlorite_percent=request.known_control_soil.chlorite_percent,
            zircon_percent=request.known_control_soil.zircon_percent,
            tourmaline_percent=request.known_control_soil.tourmaline_percent,
            rutile_percent=request.known_control_soil.rutile_percent,
            total_heavy_minerals_percent=request.known_control_soil.total_heavy_minerals_percent,
            munsell_color_dry=request.known_control_soil.munsell_color_dry,
            xrf_major_oxides_wt_pct=request.known_control_soil.xrf_major_oxides_wt_pct,
            xrf_trace_ppm=request.known_control_soil.xrf_trace_ppm,
        )

        result = _SOIL_ENGINE.compare_soil_samples(
            questioned=q_profile,
            control=c_profile,
        )

        return SoilComparisonResponse(
            case_id=request.case_id,
            questioned_sample_id=result.questioned_sample_id,
            control_sample_id=result.control_sample_id,
            clr_questioned=result.clr_questioned,
            clr_control=result.clr_control,
            mahalanobis_distance_mcd=result.mahalanobis_distance_mcd,
            hotelling_f_statistic=result.hotelling_f_statistic,
            hotelling_p_value=result.hotelling_p_value,
            color_difference_delta_e00=result.color_difference_delta_e00,
            ztr_index_questioned=result.ztr_index_questioned,
            ztr_index_control=result.ztr_index_control,
            ztr_index_difference=result.ztr_index_difference,
            astm_e3272_verdict=result.astm_e3272_verdict.value,
            likelihood_ratio=result.likelihood_ratio,
            enfsi_verbal_tier=result.enfsi_verbal_tier,
            enfsi_verbal_statement_en=result.enfsi_verbal_statement_en,
            enfsi_verbal_statement_tr=result.enfsi_verbal_statement_tr,
            prosecutors_fallacy_shield=result.prosecutors_fallacy_shield,
        )

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Soil comparison mathematical error: {str(ve)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Soil comparison execution failed: {str(e)}",
        )


# ── Module 2.1: Forensic Palynology & Environmental eDNA Endpoint ─────────────

@router.post(
    "/palynology-edna-analysis",
    response_model=PalynologyEdnaAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Forensic Palynology, 6-Biome Ecological Classification & eDNA Metagenomics (Pillar 7 §3)",
    description=(
        "Quantifies Relative Pollen Frequencies (RPF), computes multivariate Bray-Curtis, "
        "Cosine and Canberra distance metrics, classifies terrestrial vegetation biomes, "
        "predicts geographic coordinates via microbial 16S/ITS eDNA spatial regression, "
        "and compiles ISO 17025 evaluative Likelihood Ratios."
    ),
)
async def evaluate_palynology_edna(
    request: PalynologyEdnaAnalysisRequest,
) -> PalynologyEdnaAnalysisResponse:
    try:
        q_counts = request.questioned_sample.raw_taxon_counts
        c_counts = request.known_control_sample.raw_taxon_counts

        edna_asvs = None
        if request.edna_asv_profile is not None:
            edna_asvs = request.edna_asv_profile.asv_relative_abundances

        result = _PALYNO_ENGINE.compare_palynology_samples(
            questioned_counts=q_counts,
            control_counts=c_counts,
            questioned_id=request.questioned_sample.sample_id,
            control_id=request.known_control_sample.sample_id,
            edna_asvs=edna_asvs,
        )

        lat = result.edna_spatial_prediction.predicted_latitude if result.edna_spatial_prediction else None
        lon = result.edna_spatial_prediction.predicted_longitude if result.edna_spatial_prediction else None
        radius = result.edna_spatial_prediction.confidence_radius_km if result.edna_spatial_prediction else None

        return PalynologyEdnaAnalysisResponse(
            case_id=request.case_id,
            questioned_sample_id=result.questioned_sample_id,
            control_sample_id=result.control_sample_id,
            bray_curtis_dissimilarity=result.bray_curtis_dissimilarity,
            cosine_spectral_similarity=result.cosine_spectral_similarity,
            canberra_distance=result.canberra_distance,
            questioned_primary_biome=result.questioned_biome.primary_biome.value,
            questioned_biome_confidence=result.questioned_biome.confidence_score,
            questioned_canopy_coverage_pct=result.questioned_biome.ecological_canopy_coverage_pct,
            control_primary_biome=result.control_biome.primary_biome.value,
            control_biome_confidence=result.control_biome.confidence_score,
            control_canopy_coverage_pct=result.control_biome.ecological_canopy_coverage_pct,
            diagnostic_indicator_taxa=result.questioned_biome.diagnostic_indicator_taxa,
            edna_predicted_latitude=lat,
            edna_predicted_longitude=lon,
            edna_confidence_radius_km=radius,
            likelihood_ratio=result.likelihood_ratio,
            enfsi_verbal_tier=result.enfsi_verbal_tier,
            enfsi_verbal_statement_en=result.enfsi_verbal_statement_en,
            enfsi_verbal_statement_tr=result.enfsi_verbal_statement_tr,
            prosecutors_fallacy_shield=result.prosecutors_fallacy_shield,
        )

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Palynology mathematical error: {str(ve)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Palynology analysis execution failed: {str(e)}",
        )


# ── Module 2.2: Bayesian Rossmo Geographic Profiling Endpoint ─────────────────

@router.post(
    "/geographic-profile",
    response_model=GeographicProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Bayesian Rossmo Geographic Profiling & Spatial Crime Analytics (Pillar 7 §4)",
    description=(
        "Computes Rossmo's targeted hunting probability surface across linked serial crime locations, "
        "applies buffer zone penalties, calculates Search Efficiency Index (SEI), "
        "classifies offender mobility (MARAUDER vs COMMUTER) via Canter's Circle Hypothesis, "
        "and computes Standard Deviational Ellipses (SDE)."
    ),
)
async def evaluate_geographic_profile(
    request: GeographicProfileRequest,
) -> GeographicProfileResponse:
    try:
        points = [
            CrimeSitePoint(
                site_id=p.site_id,
                x_coord_km=p.x_coord_km,
                y_coord_km=p.y_coord_km,
                latitude=p.latitude,
                longitude=p.longitude,
                weight=p.weight,
            )
            for p in request.crime_sites
        ]

        bounds = (
            request.grid_bounds_km[0],
            request.grid_bounds_km[1],
            request.grid_bounds_km[2],
            request.grid_bounds_km[3],
        )

        result = _GEOPROF_ENGINE.compute_geographic_profile(
            crimes=points,
            case_id=request.case_id,
            buffer_radius_km=request.buffer_radius_km,
            decay_exponent_f=request.decay_exponent_f,
            buffer_exponent_g=request.buffer_exponent_g,
            grid_bounds=bounds,
            grid_resolution_km=request.grid_resolution_km,
        )

        return GeographicProfileResponse(
            case_id=result.case_id,
            incident_count=result.incident_count,
            peak_anchor_x_km=result.peak_anchor_x_km,
            peak_anchor_y_km=result.peak_anchor_y_km,
            top_5_percent_search_area_sq_km=result.top_5_percent_search_area_sq_km,
            total_grid_area_sq_km=result.total_grid_area_sq_km,
            search_efficiency_index_pct=result.search_efficiency_index_pct,
            canter_typology=result.canter_circle.typology.value,
            canter_circle_diameter_km=result.canter_circle.diameter_km,
            sde_center_x_km=result.deviational_ellipse.center_x_km,
            sde_center_y_km=result.deviational_ellipse.center_y_km,
            sde_rotation_angle_deg=result.deviational_ellipse.rotation_angle_degrees,
            probability_density_surface=result.probability_density_surface,
            likelihood_ratio=result.likelihood_ratio,
            enfsi_verbal_tier=result.enfsi_verbal_tier,
            enfsi_verbal_statement_en=result.enfsi_verbal_statement_en,
            enfsi_verbal_statement_tr=result.enfsi_verbal_statement_tr,
            prosecutors_fallacy_shield=result.prosecutors_fallacy_shield,
        )

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Geographic profiling input error: {str(ve)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Geographic profiling calculation failed: {str(e)}",
        )


# ── Module 3.1: Multi-Criteria Bayesian Evidence Fusion Endpoint ───────────────

@router.post(
    "/fuse-evidence-layers",
    response_model=GeoEvidenceFusionResponse,
    status_code=status.HTTP_200_OK,
    summary="Multi-Criteria Bayesian Evidence Fusion & GIS Spatial Heatmap (Pillar 7 §5)",
    description=(
        "Fuses multi-modal spatial evidence layers (Isoscapes, Soil QXRD/CoDa, Palynology/eDNA, "
        "and Rossmo Geographic Profiling) into a unified posterior probability surface. "
        "Applies 2D adaptive Gaussian KDE smoothing, calculates Search Efficiency Index (SEI >= 90%), "
        "identifies primary/secondary spatial hotspots, and renders ISO/IEC 17025 evaluative reports."
    ),
)
async def evaluate_geo_evidence_fusion(
    request: GeoEvidenceFusionRequest,
) -> GeoEvidenceFusionResponse:
    try:
        layers = [
            EvidenceLayerInput(
                layer_id=l.layer_id,
                modality_name=l.modality_name,
                likelihood_matrix=l.likelihood_matrix,
                weight=l.weight,
                modality_likelihood_ratio=l.modality_likelihood_ratio,
            )
            for l in request.layers
        ]

        bounds = (
            request.grid_bounds_km[0],
            request.grid_bounds_km[1],
            request.grid_bounds_km[2],
            request.grid_bounds_km[3],
        )

        result = _FUSION_ENGINE.fuse_evidence_layers(
            layers=layers,
            case_id=request.case_id,
            prior_surface=request.prior_surface,
            grid_bounds=bounds,
            grid_resolution_km=request.grid_resolution_km,
        )

        hotspots = [
            FusedSpatialHotspotDto(
                hotspot_id=h.hotspot_id,
                centroid_x_km=h.centroid_x_km,
                centroid_y_km=h.centroid_y_km,
                centroid_lat=h.centroid_lat,
                centroid_lon=h.centroid_lon,
                bounding_radius_km=h.bounding_radius_km,
                posterior_density_mass_pct=h.posterior_density_mass_pct,
                primary_associated_modality=h.primary_associated_modality,
            )
            for h in result.top_spatial_hotspots
        ]

        return GeoEvidenceFusionResponse(
            case_id=result.case_id,
            grid_dimensions=result.grid_dimensions,
            fused_probability_surface=result.fused_probability_surface,
            peak_posterior_coord_km=result.peak_posterior_coord_km,
            search_area_50pct_sq_km=result.search_area_50pct_sq_km,
            search_area_5pct_sq_km=result.search_area_5pct_sq_km,
            total_grid_area_sq_km=result.total_grid_area_sq_km,
            search_efficiency_index_pct=result.search_efficiency_index_pct,
            top_spatial_hotspots=hotspots,
            fused_likelihood_ratio=result.fused_likelihood_ratio,
            enfsi_verbal_tier=result.enfsi_verbal_tier,
            enfsi_verbal_statement_en=result.enfsi_verbal_statement_en,
            enfsi_verbal_statement_tr=result.enfsi_verbal_statement_tr,
            prosecutors_fallacy_shield=result.prosecutors_fallacy_shield,
        )

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Evidence fusion input error: {str(ve)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evidence fusion calculation failed: {str(e)}",
        )
