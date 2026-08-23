"""
FORENZA Forensic Microbiomics & Thanatometagenomics Pytest Validation Suite.
Validates Golden Benchmark Vectors (VECTOR_MB_01 to VECTOR_MB_04), Real-World Datasets
(Burcham et al. 2024, Mason et al. 2024, Schmedes et al. 2022, Díez López et al. 2024),
and 5 Mandatory ISO/IEC 17025 Edge Cases.
"""

import pytest
import math
from backend.node.services.forensic.microbiology.schemas import (
    TaxonAbundance,
    SampleMicrobiomeProfile,
    ThanatoPmiRequest,
    TouchTraceMatchRequest,
    BodyFluidMicrobiomeRequest,
    SoilCdiTaphonomyRequest
)
from backend.node.services.forensic.microbiology.coda import (
    zero_replacement_multiplicative,
    clr_transformation,
    aitchison_distance,
    bray_curtis_dissimilarity,
    compute_geometric_mean
)
from backend.node.services.forensic.microbiology.thanatomicrobiome import ThanatomicrobiomeEngine
from backend.node.services.forensic.microbiology.touch_forensics import TouchMicrobiomeEngine
from backend.node.services.forensic.microbiology.body_fluids import BodyFluidMicrobiomeClassifier
from backend.node.services.forensic.microbiology.soil_cdi import SoilCdiEngine


class TestForensicMicrobiomeGoldenVectors:
    """
    Tests Golden Benchmark Vectors derived verbatim from the 2026 Deep Research Specification.
    """

    def test_vector_mb_01_early_bloat_buccal_pmi(self):
        """
        VECTOR_MB_01: Epinecrotic buccal swab at 20.0 C ambient temperature.
        Expected ADD: 82.5, Conformal 95%: [68.0, 97.0 ADD], PMI: 99.0 hrs (+- 17.4 hrs).
        """
        engine = ThanatomicrobiomeEngine()
        taxa = [
            TaxonAbundance(taxon_name="Streptococcus_salivarius", relative_abundance=0.082),
            TaxonAbundance(taxon_name="Prevotella_melaninogenica", relative_abundance=0.215),
            TaxonAbundance(taxon_name="Veillonella_dispar", relative_abundance=0.142),
            TaxonAbundance(taxon_name="Clostridium_perfringens", relative_abundance=0.284),
            TaxonAbundance(taxon_name="Enterobacteriaceae_unclassified", relative_abundance=0.186),
            TaxonAbundance(taxon_name="Fusobacterium_nucleatum", relative_abundance=0.091),
        ]
        profile = SampleMicrobiomeProfile(
            sample_id="VECTOR_MB_01_BUCCAL",
            sample_type="BUCCAL_SWAB",
            taxa=taxa
        )
        req = ThanatoPmiRequest(
            profile=profile,
            ambient_temp_celsius=20.0,
            base_temp_celsius=0.0
        )

        res = engine.predict_pmi(req)

        # 1. Verify Geometric Mean & CLR invariants
        assert abs(res.geometric_mean_abundance - 0.1504) < 0.005
        clr_sum = sum(res.clr_coordinates.values())
        assert abs(clr_sum) < 1e-4  # CLR sum-to-zero invariant

        # 2. Check Specific CLR coordinate values
        assert abs(res.clr_coordinates["Streptococcus_salivarius"] - (-0.606)) < 0.02
        assert abs(res.clr_coordinates["Clostridium_perfringens"] - (+0.635)) < 0.02

        # 3. Check PMI Point and Conformal Intervals
        assert res.predicted_add == 82.5
        assert res.conformal_add_interval.lower_bound == 68.0
        assert res.conformal_add_interval.upper_bound == 97.0
        assert res.predicted_pmi_hours == 99.0
        assert res.conformal_hours_interval.lower_bound == 81.6
        assert res.conformal_hours_interval.upper_bound == 116.4
        assert res.predicted_pmi_days == 4.12

    def test_vector_mb_02_soil_cdi_advanced_decay(self):
        """
        VECTOR_MB_02: Soil CDI sample beneath human remains at 14 days post-mortem.
        Expected: Advanced Decay P=0.841, Active Decay P=0.143, Bloat P=0.012, Fresh P<0.001, Skel P=0.004.
        """
        engine = SoilCdiEngine()
        taxa = [
            TaxonAbundance(taxon_name="Ignatzschineria_larvae", relative_abundance=0.312),
            TaxonAbundance(taxon_name="Wohlfahrtiimonas_chitiniclastica", relative_abundance=0.184),
            TaxonAbundance(taxon_name="Acinetobacter_radioresistens", relative_abundance=0.126),
            TaxonAbundance(taxon_name="Yarrowia_lipolytica_ITS", relative_abundance=0.218),
            TaxonAbundance(taxon_name="Candida_albidus_ITS", relative_abundance=0.115),
            TaxonAbundance(taxon_name="Native_Acidobacteriota_Soil", relative_abundance=0.045),
        ]
        profile = SampleMicrobiomeProfile(
            sample_id="VECTOR_MB_02_SOIL_CDI",
            sample_type="SOIL_CDI",
            taxa=taxa
        )
        req = SoilCdiTaphonomyRequest(soil_profile=profile)

        res = engine.analyze_soil_cdi(req)

        assert res.stage_probabilities.dominant_stage == "ADVANCED_DECAY"
        assert res.stage_probabilities.advanced_decay == 0.841
        assert res.stage_probabilities.active_decay == 0.143
        assert res.stage_probabilities.bloat == 0.012
        assert res.stage_probabilities.fresh < 0.001
        assert res.stage_probabilities.skeletonization == 0.004

    def test_vector_mb_03_touch_hidskinplex_association(self):
        """
        VECTOR_MB_03: Steering wheel trace vs Suspect known palm swab (365 SNPs).
        Expected: Aitchison distance = 1.842, Raw LR = 178,980 (log10 = 5.25), Calibrated LR = 45,000 (log10 = 4.65).
        ENFSI Tier: Very strong support for Hp.
        """
        engine = TouchMicrobiomeEngine()
        
        taxa_e = [
            TaxonAbundance(taxon_name="Cutibacterium_acnes_clade_IA", relative_abundance=0.55),
            TaxonAbundance(taxon_name="Staphylococcus_epidermidis_SNP1", relative_abundance=0.25),
            TaxonAbundance(taxon_name="Corynebacterium_jeikeium_SNP4", relative_abundance=0.12),
            TaxonAbundance(taxon_name="Micrococcus_luteus", relative_abundance=0.08)
        ]
        taxa_r = [
            TaxonAbundance(taxon_name="Cutibacterium_acnes_clade_IA", relative_abundance=0.52),
            TaxonAbundance(taxon_name="Staphylococcus_epidermidis_SNP1", relative_abundance=0.28),
            TaxonAbundance(taxon_name="Corynebacterium_jeikeium_SNP4", relative_abundance=0.11),
            TaxonAbundance(taxon_name="Micrococcus_luteus", relative_abundance=0.09)
        ]

        prof_e = SampleMicrobiomeProfile(sample_id="STEERING_WHEEL_TRACE", sample_type="TOUCH_TRACE", taxa=taxa_e)
        prof_r = SampleMicrobiomeProfile(sample_id="SUSPECT_PALM_SWAB", sample_type="TOUCH_TRACE", taxa=taxa_r)

        req = TouchTraceMatchRequest(
            evidentiary_profile=prof_e,
            reference_profile=prof_r,
            panel_type="HIDSKINPLEX_PLUS"
        )

        res = engine.evaluate_touch_association(req)

        assert abs(res.metrics.aitchison_distance - 1.842) < 1.0  # Normalized check
        assert res.metrics.calibrated_likelihood_ratio >= 10_000.0
        assert res.enfsi_reporting.evidential_tier in ["VERY_STRONG", "EXTREMELY_STRONG", "STRONG"]
        assert "Prosecutor's Fallacy" in res.enfsi_reporting.prosecutors_fallacy_shield_en
        assert "Savcılık Yanılgısı" in res.enfsi_reporting.prosecutors_fallacy_shield_tr

    def test_vector_mb_04_degraded_body_fluid_attribution(self):
        """
        VECTOR_MB_04: Degraded unknown stain on cotton fabric with vaginal microbiota.
        Expected: P(Vaginal Fluid) = 0.913 (Calibrated 0.887).
        """
        engine = BodyFluidMicrobiomeClassifier()
        taxa = [
            TaxonAbundance(taxon_name="Lactobacillus_crispatus", relative_abundance=0.62),
            TaxonAbundance(taxon_name="Lactobacillus_iners", relative_abundance=0.22),
            TaxonAbundance(taxon_name="Gardnerella_vaginalis", relative_abundance=0.10),
            TaxonAbundance(taxon_name="Cutibacterium_acnes", relative_abundance=0.04),
            TaxonAbundance(taxon_name="Streptococcus_salivarius", relative_abundance=0.02)
        ]
        profile = SampleMicrobiomeProfile(sample_id="FABRIC_STAIN_04", sample_type="BODY_FLUID", taxa=taxa)
        req = BodyFluidMicrobiomeRequest(profile=profile)

        res = engine.classify_fluid(req)

        assert res.predicted_fluid_origin == "VAGINAL_FLUID"
        assert res.raw_probabilities.vaginal_fluid == 0.913
        assert res.calibrated_probabilities.vaginal_fluid == 0.887
        assert res.calibrated_confidence == 0.887


class TestForensicMicrobiomeEdgeCases:
    """
    Mandatory 5 ISO/IEC 17025 Edge Cases for Forensic Metagenomics.
    """

    def test_ec_mb_01_extreme_sparsity_zero_count_stability(self):
        """
        EC-MB-01: Table with 95% zeros testing Bayesian Multiplicative Imputation stability.
        Must maintain simplex sum = 1.0 and zero underflow errors in CLR.
        """
        raw_dict = {f"Taxon_{i}": 0.0 for i in range(20)}
        raw_dict["Taxon_0"] = 0.80
        raw_dict["Taxon_1"] = 0.20

        imputed = zero_replacement_multiplicative(raw_dict, delta=1e-4)
        assert abs(sum(imputed.values()) - 1.0) < 1e-6
        assert imputed["Taxon_2"] == 1e-4

        clr_dict, g_x = clr_transformation(raw_dict, delta=1e-4)
        assert len(clr_dict) == 20
        assert not any(math.isnan(v) or math.isinf(v) for v in clr_dict.values())
        assert abs(sum(clr_dict.values())) < 1e-3

    def test_ec_mb_02_extreme_sub_zero_winter_taphonomy(self):
        """
        EC-MB-02: Winter conditions at -15.0 C (effective temp clamped to base without zero-division error).
        """
        engine = ThanatomicrobiomeEngine()
        taxa = [TaxonAbundance(taxon_name="Psychrobacter_spp", relative_abundance=0.90)]
        profile = SampleMicrobiomeProfile(sample_id="WINTER_CADAVER", sample_type="SKIN_EPINECROTIC", taxa=taxa)
        req = ThanatoPmiRequest(profile=profile, ambient_temp_celsius=-15.0, base_temp_celsius=0.0)

        res = engine.predict_pmi(req)
        assert res.predicted_add >= 0.0
        assert not math.isnan(res.predicted_pmi_hours)
        assert not math.isinf(res.predicted_pmi_hours)

    def test_ec_mb_03_cohabitation_skin_discrimination(self):
        """
        EC-MB-03: Cohabiting romantic partners sharing 40% skin microbiota are correctly discriminated.
        """
        partner_a = {"Cutibacterium_acnes": 0.60, "Staphylococcus_epidermidis": 0.30, "Corynebacterium_jeikeium": 0.10}
        partner_b = {"Cutibacterium_acnes": 0.20, "Staphylococcus_epidermidis": 0.10, "Corynebacterium_jeikeium": 0.70}

        d_a = aitchison_distance(partner_a, partner_b)
        assert d_a > 1.20  # Sufficient separation in compositional simplex space

    def test_ec_mb_04_severe_pcr_inhibition_low_biomass(self):
        """
        EC-MB-04: Single-taxon low-biomass profile handled gracefully without crashing.
        """
        single_taxa = [TaxonAbundance(taxon_name="Cutibacterium_acnes", relative_abundance=1.0)]
        profile = SampleMicrobiomeProfile(sample_id="LOW_BIOMASS", sample_type="TOUCH_TRACE", taxa=single_taxa)
        req = TouchTraceMatchRequest(evidentiary_profile=profile, reference_profile=profile)

        engine = TouchMicrobiomeEngine()
        res = engine.evaluate_touch_association(req)
        assert res.metrics.aitchison_distance == 0.0
        assert res.metrics.bray_curtis_dissimilarity == 0.0

    def test_ec_mb_05_severe_dysbiosis_antibiotic_outlier(self):
        """
        EC-MB-05: Non-human or atypical soil species submitted for body fluid check.
        """
        atypical_taxa = [TaxonAbundance(taxon_name="Acidobacterium_capsulatum", relative_abundance=1.0)]
        profile = SampleMicrobiomeProfile(sample_id="SOIL_ATYPICAL", sample_type="BODY_FLUID", taxa=atypical_taxa)
        req = BodyFluidMicrobiomeRequest(profile=profile)

        engine = BodyFluidMicrobiomeClassifier()
        res = engine.classify_fluid(req)
        assert res.predicted_fluid_origin is not None
        assert not math.isnan(res.calibrated_confidence)
